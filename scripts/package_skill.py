#!/usr/bin/env python3
"""构建确定性的 Agent Skills ZIP 与 SHA-256 校验和。"""

from __future__ import annotations

import hashlib
import subprocess
import sys
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILL_NAME = "define-product-and-roadmap"
SKILL = ROOT / "skills" / SKILL_NAME
DIST = ROOT / "dist"
EXCLUDED_PARTS = {"__pycache__", ".DS_Store"}


def included_files():
    for path in sorted(SKILL.rglob("*")):
        if not path.is_file():
            continue
        if any(part in EXCLUDED_PARTS for part in path.parts) or path.suffix == ".pyc":
            continue
        yield path


def main() -> int:
    check = subprocess.run([sys.executable, str(ROOT / "scripts" / "check_project.py")], cwd=ROOT, check=False)
    if check.returncode:
        return check.returncode

    version = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
    DIST.mkdir(parents=True, exist_ok=True)
    archive = DIST / f"{SKILL_NAME}-{version}.zip"
    temporary = DIST / f".{archive.name}.tmp"

    with zipfile.ZipFile(temporary, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as package:
        for path in included_files():
            relative = path.relative_to(SKILL)
            info = zipfile.ZipInfo(f"{SKILL_NAME}/{relative.as_posix()}", date_time=(2020, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            mode = 0o755 if relative.parts[0] == "scripts" and path.suffix == ".py" else 0o644
            info.external_attr = mode << 16
            package.writestr(info, path.read_bytes())

    temporary.replace(archive)
    digest = hashlib.sha256(archive.read_bytes()).hexdigest()
    checksum = archive.with_suffix(".zip.sha256")
    checksum.write_text(f"{digest}  {archive.name}\n", encoding="utf-8")
    print(archive)
    print(checksum)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
