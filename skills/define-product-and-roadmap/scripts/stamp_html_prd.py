#!/usr/bin/env python3
"""Stamp an HTML PRD with a checksum of its exact source, excluding the stamp itself."""
from __future__ import annotations

import argparse
from pathlib import Path
from html_prd_validator import FINGERPRINT_ATTR, content_fingerprint


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument('html', type=Path)
    args = parser.parse_args()
    source = args.html.read_text(encoding='utf-8-sig')
    fingerprint = content_fingerprint(source)
    stamped = FINGERPRINT_ATTR.sub(lambda m: m.group(1) + fingerprint + m.group(2), source)
    args.html.write_text(stamped, encoding='utf-8')
    print(fingerprint)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
