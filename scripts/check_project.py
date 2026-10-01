#!/usr/bin/env python3
"""运行结构、可移植性、版本、评估 schema 与单元测试检查。

要求 Python >= 3.8,零第三方依赖。
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
import zipfile
from pathlib import Path
from typing import Dict, List, Optional


ROOT = Path(__file__).resolve().parents[1]
SKILL_NAME = "define-product-and-roadmap"
SKILL = ROOT / "skills" / SKILL_NAME
SEMVER_RE = re.compile(r"^\d+\.\d+\.\d+(?:[-+][0-9A-Za-z.-]+)?$")
LINK_RE = re.compile(r"\[[^\]]+\]\(([^)]+)\)")


def fail(errors: List[str], message: str) -> None:
    errors.append(message)


def read_or_fail(path: Path, errors: List[str]) -> Optional[str]:
    """读取文本文件;缺失或不可读时记录错误并返回 None,避免检查门自身崩溃。"""
    if not path.is_file():
        fail(errors, f"缺失文件:{path.relative_to(ROOT)}")
        return None
    try:
        return path.read_text(encoding="utf-8-sig")
    except OSError as exc:
        fail(errors, f"文件不可读:{path.relative_to(ROOT)}:{exc}")
        return None


def frontmatter(path: Path, errors: List[str]) -> Dict[str, str]:
    text = path.read_text(encoding="utf-8-sig")
    lines = text.splitlines()
    if not lines or lines[0] != "---":
        fail(errors, f"{path}:缺少起始 frontmatter 标记")
        return {}
    try:
        end = lines.index("---", 1)
    except ValueError:
        fail(errors, f"{path}:缺少结束 frontmatter 标记")
        return {}
    result: Dict[str, str] = {}
    for line in lines[1:end]:
        if ":" not in line:
            fail(errors, f"{path}:frontmatter 行格式错误:{line}")
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
        "references/html-prd-workflow.md",
        "references/roadmap-contract.md",
        "references/revision-lessons.md",
        "references/quality-rubric.md",
        "assets/prd-template.md",
        "assets/prd-template.html",
        "assets/roadmap-template.md",
        "scripts/validate_product_docs.py",
        "scripts/test_contract.py",
        "scripts/html_prd_validator.py",
        "scripts/test_html_contract.py",
    ]
    for relative in required:
        if not (SKILL / relative).is_file():
            fail(errors, f"缺失技能文件:{relative}")

    skill_path = SKILL / "SKILL.md"
    if not skill_path.is_file():
        return  # 后续检查依赖 SKILL.md;缺失错误已记录
    metadata = frontmatter(skill_path, errors)
    if set(metadata) != {"name", "description"}:
        fail(errors, f"SKILL.md frontmatter 只能包含 name 和 description:{sorted(metadata)}")
    if metadata.get("name") != SKILL_NAME:
        fail(errors, f"技能名称不匹配:{metadata.get('name')}")
    description = metadata.get("description", "")
    if not 1 <= len(description) <= 1024:
        fail(errors, f"description 长度超出 1..1024:{len(description)}")
    if "Do not use" not in description:
        fail(errors, "description 缺少负向触发边界(Do not use)")

    skill_text = (SKILL / "SKILL.md").read_text(encoding="utf-8-sig")
    if len(skill_text.splitlines()) >= 500:
        fail(errors, "SKILL.md 必须少于 500 行")
    for target in LINK_RE.findall(skill_text):
        if target.startswith(("http://", "https://", "#")):
            continue
        if not (SKILL / target.split("#", 1)[0]).resolve().exists():
            fail(errors, f"SKILL.md 链接失效:{target}")

    forbidden = {"README.md", "CHANGELOG.md", "INSTALLATION_GUIDE.md", "QUICK_REFERENCE.md"}
    found = sorted(path.name for path in SKILL.iterdir() if path.name in forbidden)
    if found:
        fail(errors, f"辅助项目文档必须放在技能目录之外:{found}")

    openai_yaml_path = SKILL / "agents" / "openai.yaml"
    openai_yaml = read_or_fail(openai_yaml_path, errors)
    if openai_yaml is None:
        return
    if f"${SKILL_NAME}" not in openai_yaml:
        fail(errors, "agents/openai.yaml 的 default_prompt 必须显式提及技能名")


def check_versions(errors: List[str]) -> str:
    project_text = read_or_fail(ROOT / "VERSION", errors)
    skill_text = read_or_fail(SKILL / "VERSION", errors)
    changelog = read_or_fail(ROOT / "CHANGELOG.md", errors)
    if project_text is None or skill_text is None or changelog is None:
        return ""
    project_version = project_text.strip()
    skill_version = skill_text.strip()
    if project_version != skill_version:
        fail(errors, f"版本不匹配:project={project_version},skill={skill_version}")
    if not SEMVER_RE.fullmatch(project_version):
        fail(errors, f"无效语义版本:{project_version}")
    if f"## {project_version} " not in changelog:
        fail(errors, f"CHANGELOG.md 缺少版本 {project_version}")
    return project_version


def check_discovery_links(errors: List[str]) -> None:
    expected_target = f"skills/{SKILL_NAME}"
    for relative in (
        Path(".agents/skills") / SKILL_NAME,
        Path(".claude/skills") / SKILL_NAME,
        Path(".codebuddy/skills") / SKILL_NAME,
        Path(".workbuddy/skills") / SKILL_NAME,
    ):
        link = ROOT / relative
        if not link.is_symlink():
            # Windows:git 默认 core.symlinks=false,克隆后 symlink 变为内容等于目标相对路径的普通文件。
            if os.name == "nt" and link.is_file():
                content = link.read_text(encoding="utf-8-sig").strip()
                if content == expected_target:
                    continue
            fail(errors, f"项目发现路径不是符号链接:{relative}")
            continue
        if link.resolve() != SKILL.resolve():
            fail(errors, f"项目发现路径指向别处:{relative} -> {link.resolve()}")


def check_evals(errors: List[str]) -> None:
    path = ROOT / "evals" / "cases.jsonl"
    text = read_or_fail(path, errors)
    if text is None:
        return
    seen = set()
    counts = {"trigger": 0, "semantic": 0}
    for number, line in enumerate(text.splitlines(), 1):
        try:
            case = json.loads(line)
        except json.JSONDecodeError as exc:
            fail(errors, f"{path}:{number}:无效 JSON:{exc}")
            continue
        required = {"id", "category", "should_trigger", "prompt", "assertions"}
        missing = sorted(required - set(case))
        if missing:
            fail(errors, f"{path}:{number}:缺失字段 {missing}")
        if case.get("id") in seen:
            fail(errors, f"{path}:{number}:重复 id {case.get('id')}")
        seen.add(case.get("id"))
        category = case.get("category")
        if category not in counts:
            fail(errors, f"{path}:{number}:无效类别 {category}")
        else:
            counts[category] += 1
        fixture = case.get("fixture")
        if fixture and not (ROOT / fixture).exists():
            fail(errors, f"{path}:{number}:缺失 fixture {fixture}")
        assertions = case.get("assertions")
        if not isinstance(assertions, list) or not assertions:
            fail(errors, f"{path}:{number}:assertions 必须是非空列表")
    if counts["trigger"] < 8 or counts["semantic"] < 3:
        fail(errors, f"评估清单过小:{counts}")


def run_command(command: List[str], errors: List[str], label: str) -> None:
    result = subprocess.run(command, cwd=ROOT, capture_output=True, text=True, check=False)
    if result.returncode:
        fail(errors, f"{label} 失败\n{result.stdout}{result.stderr}")
    else:
        print(f"通过 {label}")


def verify_dist(version: str, errors: List[str]) -> None:
    archive = ROOT / "dist" / f"{SKILL_NAME}-{version}.zip"
    checksum = archive.with_suffix(".zip.sha256")
    if not archive.is_file() or not checksum.is_file():
        fail(errors, f"缺少 {version} 的发布归档或校验和")
        return
    expected_parts = checksum.read_text(encoding="utf-8-sig").split()
    if not expected_parts:
        fail(errors, f"校验和文件为空或格式错误:{checksum.relative_to(ROOT)}")
        return
    expected = expected_parts[0]
    actual = hashlib.sha256(archive.read_bytes()).hexdigest()
    if expected != actual:
        fail(errors, f"发布校验和不匹配:expected={expected},actual={actual}")
    with zipfile.ZipFile(archive) as package:
        names = package.namelist()
        required = f"{SKILL_NAME}/SKILL.md"
        if required not in names:
            fail(errors, f"发布归档缺少 {required}")
        if any("__pycache__" in name or name.endswith((".pyc", ".DS_Store")) for name in names):
            fail(errors, "发布归档包含被排除的构建文件")
        version_entry = f"{SKILL_NAME}/VERSION"
        if version_entry not in names:
            fail(errors, f"发布归档缺少 {version_entry}")
            return
        extracted_version = package.read(version_entry).decode("utf-8").strip()
        if extracted_version != version:
            fail(errors, f"归档版本不匹配:{extracted_version}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--verify-dist", action="store_true")
    args = parser.parse_args()
    errors: List[str] = []

    check_skill(errors)
    version = check_versions(errors)
    check_discovery_links(errors)
    check_evals(errors)

    run_command([sys.executable, str(SKILL / "scripts" / "test_contract.py"), "-q"], errors, "契约测试")
    run_command([sys.executable, str(SKILL / "scripts" / "test_html_contract.py"), "-q"], errors, "HTML PRD 契约测试")
    run_command(
        [sys.executable, "-m", "py_compile", str(SKILL / "scripts" / "validate_product_docs.py"), str(SKILL / "scripts" / "html_prd_validator.py"), str(SKILL / "scripts" / "test_contract.py"), str(SKILL / "scripts" / "test_html_contract.py")],
        errors,
        "Python 编译",
    )

    quick_validate = Path.home() / ".codex" / "skills" / ".system" / "skill-creator" / "scripts" / "quick_validate.py"
    if quick_validate.is_file():
        run_command([sys.executable, str(quick_validate), str(SKILL)], errors, "OpenAI quick_validate")
    else:
        print("跳过 OpenAI quick_validate(当前环境未安装)")

    if args.verify_dist:
        if version:
            verify_dist(version, errors)
        else:
            fail(errors, "版本未知,跳过 --verify-dist")

    if errors:
        for message in errors:
            print(f"失败 {message}", file=sys.stderr)
        print(f"项目验证失败:{len(errors)} 个错误", file=sys.stderr)
        return 1
    print(f"项目验证通过:{SKILL_NAME} {version}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
