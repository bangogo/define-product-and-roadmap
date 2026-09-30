#!/usr/bin/env python3
"""Check durable output-spec fixtures without claiming visual or host execution."""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SKILL = ROOT / 'skills' / 'define-product-and-roadmap'
HERE = Path(__file__).resolve().parent
VALIDATOR = SKILL / 'scripts' / 'validate_product_docs.py'


def validate(path: Path) -> None:
    result = subprocess.run([sys.executable, str(VALIDATOR), '--prd-html', str(path)], capture_output=True, text=True)
    assert result.returncode == 0, f'{path.name}: {result.stdout}\n{result.stderr}'


def main() -> None:
    validate(SKILL / 'assets' / 'prd-template.html')
    versions = []
    for n in (1, 2, 3):
        path = HERE / f'existing-prd-draft.{n}.html'
        validate(path)
        versions.append(path.read_text(encoding='utf-8'))
    assert '工单关闭前需负责人确认。' in versions[0]
    assert '工单关闭前需附处理证据并由负责人确认。' in versions[1]
    assert versions[2].count('工单关闭前需附处理证据并由当班负责人确认。') == 1
    assert '<th scope="col">处理证据</th>' in versions[1]
    assert '<th scope="col">确认责任</th>' in versions[2]
    assert '当班负责人确认</text>' in versions[2]
    assert '当班负责人确认结案' in versions[2]
    assert not list(HERE.glob('*roadmap*')), 'standalone PRD regression must not generate a Roadmap'
    negative = HERE / 'visual-overflow-negative.html'
    result = subprocess.run([sys.executable, str(VALIDATOR), '--prd-html', str(negative)], capture_output=True, text=True)
    assert result.returncode == 0, f'{negative.name}: {result.stdout}\n{result.stderr}'  # Static geometry blind spot.
    print('scenario fixtures: new HTML, 3 B revisions, unique rule, table/SVG sync, static visual blind spot passed')


if __name__ == '__main__':
    main()
