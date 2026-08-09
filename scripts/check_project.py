#!/usr/bin/env python3
"""Run structural, portability, version, eval-schema, and unit-test checks."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
import zipfile
from pathlib import Path
from typing import Dict, List


ROOT = Path(__file__).resolve().parents[1]
SKILL_NAME = "define-product-and-roadmap"
SKILL = ROOT / "skills" / SKILL_NAME
SEMVER_RE = re.compile(r"^\d+\.\d+\.\d+(?:[-+][0-9A-Za-z.-]+)?$")
LINK_RE = re.compile(r"\[[^\]]+\]\(([^)]+)\)")


def fail(errors: List[str], message: str) -> None:
    errors.append(message)


def frontmatter(path: Path, errors: List[str]) -> Dict[str, str]:
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()
    if not lines or lines[0] != "---":
        fail(errors, f"{path}: missing opening frontmatter marker")
        return {}
    try:
        end = lines.index("---", 1)
    except ValueError:
        fail(errors, f"{path}: missing closing frontmatter marker")
        return {}
    result: Dict[str, str] = {}
    for line in lines[1:end]:
        if ":" not in line:
            fail(errors, f"{path}: malformed frontmatter line: {line}")
            continue
        key, value = line.split(":", 1)
        result[key.strip()] = value.strip().strip('"')
    return result


def check_skill(errors: List[str]) -> None:
    required = [
        "SKILL.md",
        "VERSION",
        "agents/openai.yaml",
        "references/intent-and-scenario-contract.md",
        "references/prd-contract.md",
        "references/roadmap-contract.md",
        "references/revision-lessons.md",
        "references/quality-rubric.md",
        "assets/prd-template.md",
        "assets/roadmap-template.md",
        "scripts/validate_product_docs.py",
        "scripts/test_contract.py",
    ]
    for relative in required:
        if not (SKILL / relative).is_file():
            fail(errors, f"missing skill file: {relative}")

    metadata = frontmatter(SKILL / "SKILL.md", errors)
    if set(metadata) != {"name", "description"}:
        fail(errors, f"SKILL.md frontmatter must contain only name and description: {sorted(metadata)}")
    if metadata.get("name") != SKILL_NAME:
        fail(errors, f"skill name mismatch: {metadata.get('name')}")
    description = metadata.get("description", "")
    if not 1 <= len(description) <= 1024:
        fail(errors, f"description length outside 1..1024: {len(description)}")
    if "Do not use" not in description:
        fail(errors, "description lacks a negative trigger boundary")

    skill_text = (SKILL / "SKILL.md").read_text(encoding="utf-8")
    if len(skill_text.splitlines()) >= 500:
        fail(errors, "SKILL.md must stay below 500 lines")
    for target in LINK_RE.findall(skill_text):
        if target.startswith(("http://", "https://", "#")):
            continue
        if not (SKILL / target.split("#", 1)[0]).resolve().exists():
            fail(errors, f"broken SKILL.md link: {target}")

    forbidden = {"README.md", "CHANGELOG.md", "INSTALLATION_GUIDE.md", "QUICK_REFERENCE.md"}
    found = sorted(path.name for path in SKILL.iterdir() if path.name in forbidden)
    if found:
        fail(errors, f"auxiliary project docs must stay outside skill folder: {found}")

    openai_yaml = (SKILL / "agents" / "openai.yaml").read_text(encoding="utf-8")
    if f"${SKILL_NAME}" not in openai_yaml:
        fail(errors, "agents/openai.yaml default_prompt must mention the skill explicitly")


def check_versions(errors: List[str]) -> str:
    project_version = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
    skill_version = (SKILL / "VERSION").read_text(encoding="utf-8").strip()
    if project_version != skill_version:
        fail(errors, f"version mismatch: project={project_version}, skill={skill_version}")
    if not SEMVER_RE.fullmatch(project_version):
        fail(errors, f"invalid semantic version: {project_version}")
    changelog = (ROOT / "CHANGELOG.md").read_text(encoding="utf-8")
    if f"## {project_version} " not in changelog:
        fail(errors, f"CHANGELOG.md lacks version {project_version}")
    return project_version


def check_discovery_links(errors: List[str]) -> None:
    for relative in (
        Path(".agents/skills") / SKILL_NAME,
        Path(".claude/skills") / SKILL_NAME,
    ):
        link = ROOT / relative
        if not link.is_symlink():
            fail(errors, f"project discovery path is not a symlink: {relative}")
            continue
        if link.resolve() != SKILL.resolve():
            fail(errors, f"project discovery path points elsewhere: {relative} -> {link.resolve()}")


def check_evals(errors: List[str]) -> None:
    path = ROOT / "evals" / "cases.jsonl"
    seen = set()
    counts = {"trigger": 0, "semantic": 0}
    for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        try:
            case = json.loads(line)
        except json.JSONDecodeError as exc:
            fail(errors, f"{path}:{number}: invalid JSON: {exc}")
            continue
        required = {"id", "category", "should_trigger", "prompt", "assertions"}
        missing = sorted(required - set(case))
        if missing:
            fail(errors, f"{path}:{number}: missing fields {missing}")
        if case.get("id") in seen:
            fail(errors, f"{path}:{number}: duplicate id {case.get('id')}")
        seen.add(case.get("id"))
        category = case.get("category")
        if category not in counts:
            fail(errors, f"{path}:{number}: invalid category {category}")
        else:
            counts[category] += 1
        fixture = case.get("fixture")
        if fixture and not (ROOT / fixture).exists():
            fail(errors, f"{path}:{number}: missing fixture {fixture}")
        assertions = case.get("assertions")
        if not isinstance(assertions, list) or not assertions:
            fail(errors, f"{path}:{number}: assertions must be a non-empty list")
    if counts["trigger"] < 8 or counts["semantic"] < 3:
        fail(errors, f"eval inventory too small: {counts}")


def run_command(command: List[str], errors: List[str], label: str) -> None:
    result = subprocess.run(command, cwd=ROOT, capture_output=True, text=True, check=False)
    if result.returncode:
        fail(errors, f"{label} failed\n{result.stdout}{result.stderr}")
    else:
        print(f"PASS {label}")


def verify_dist(version: str, errors: List[str]) -> None:
    archive = ROOT / "dist" / f"{SKILL_NAME}-{version}.zip"
    checksum = archive.with_suffix(".zip.sha256")
    if not archive.is_file() or not checksum.is_file():
        fail(errors, f"missing release archive or checksum for {version}")
        return
    expected = checksum.read_text(encoding="utf-8").split()[0]
    actual = hashlib.sha256(archive.read_bytes()).hexdigest()
    if expected != actual:
        fail(errors, f"release checksum mismatch: expected={expected}, actual={actual}")
    with zipfile.ZipFile(archive) as package:
        names = package.namelist()
        required = f"{SKILL_NAME}/SKILL.md"
        if required not in names:
            fail(errors, f"release archive lacks {required}")
        if any("__pycache__" in name or name.endswith((".pyc", ".DS_Store")) for name in names):
            fail(errors, "release archive contains excluded build files")
        extracted_version = package.read(f"{SKILL_NAME}/VERSION").decode("utf-8").strip()
        if extracted_version != version:
            fail(errors, f"archive version mismatch: {extracted_version}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--verify-dist", action="store_true")
    args = parser.parse_args()
    errors: List[str] = []

    check_skill(errors)
    version = check_versions(errors)
    check_discovery_links(errors)
    check_evals(errors)

    run_command([sys.executable, str(SKILL / "scripts" / "test_contract.py"), "-q"], errors, "contract tests")
    run_command(
        [sys.executable, "-m", "py_compile", str(SKILL / "scripts" / "validate_product_docs.py"), str(SKILL / "scripts" / "test_contract.py")],
        errors,
        "Python compilation",
    )

    quick_validate = Path.home() / ".codex" / "skills" / ".system" / "skill-creator" / "scripts" / "quick_validate.py"
    if quick_validate.is_file():
        run_command([sys.executable, str(quick_validate), str(SKILL)], errors, "OpenAI quick_validate")
    else:
        print("SKIP OpenAI quick_validate (not installed in this environment)")

    if args.verify_dist:
        verify_dist(version, errors)

    if errors:
        for message in errors:
            print(f"FAIL {message}", file=sys.stderr)
        print(f"project validation failed: {len(errors)} error(s)", file=sys.stderr)
        return 1
    print(f"project validation passed for {SKILL_NAME} {version}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
