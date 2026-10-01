#!/usr/bin/env python3
"""Regression tests for the standalone HTML PRD contract. Python >= 3.8."""

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


SKILL = Path(__file__).resolve().parents[1]
TEMPLATE = SKILL / "assets" / "prd-template.html"
VALIDATOR = SKILL / "scripts" / "validate_product_docs.py"


class HTMLPRDContractTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.folder = Path(self.temp.name)
        self.prd = self.folder / "product.html"
        self.prd.write_text(TEMPLATE.read_text(encoding="utf-8"), encoding="utf-8")

    def run_validator(self, *extra: str):
        result = subprocess.run(
            [sys.executable, str(VALIDATOR), "--prd-html", str(self.prd), "--format", "json", *extra],
            capture_output=True, text=True, check=False,
        )
        return result.returncode, json.loads(result.stdout)

    def test_single_html_prd_passes(self) -> None:
        code, result = self.run_validator()
        self.assertEqual(code, 0, result)
        self.assertEqual(result["proof_boundary"], "html_structure_and_record_matching_only")

    def test_svg_without_desc_fails(self) -> None:
        text = self.prd.read_text().replace('<desc id="flow-desc">用户提交材料，系统生成可审阅草稿，用户确认后进入下一步。</desc>', '')
        self.prd.write_text(text)
        code, result = self.run_validator()
        self.assertEqual(code, 1)
        self.assertTrue(any("SVG 1" in message for message in result["errors"]))

    def test_duplicate_id_and_broken_toc_fail(self) -> None:
        text = self.prd.read_text().replace('id="evidence"', 'id="value"')
        self.prd.write_text(text)
        code, result = self.run_validator()
        self.assertEqual(code, 1)
        self.assertTrue(any("重复 HTML id" in message for message in result["errors"]))
        self.assertTrue(any("目录链接" in message for message in result["errors"]))

    def test_unselected_card_and_stale_version_fail(self) -> None:
        record = self.folder / "decisions.json"
        record.write_text(json.dumps({"document_id": "example-prd", "version": "4.0.0-draft.0",
                                      "review_id": "review-001", "decisions": [{"id": "D-01", "choice": ""}]}))
        code, result = self.run_validator("--decisions", str(record))
        self.assertEqual(code, 1)
        self.assertTrue(any("version" in message for message in result["errors"]))
        self.assertTrue(any("未明确选择" in message for message in result["errors"]))

    def test_complete_record_passes_and_deferred_final_fails(self) -> None:
        record = self.folder / "decisions.json"
        data = {"document_id": "example-prd", "version": "4.0.0-draft.1", "review_id": "review-001",
                "decisions": [{"id": "D-01", "choice": "确认", "note": ""}]}
        record.write_text(json.dumps(data))
        code, result = self.run_validator("--decisions", str(record))
        self.assertEqual(code, 0, result)
        self.prd.write_text(self.prd.read_text().replace('data-status="审阅稿"', 'data-status="最终版"'))
        data["decisions"][0]["choice"] = "暂缓"
        record.write_text(json.dumps(data))
        code, result = self.run_validator("--decisions", str(record))
        self.assertEqual(code, 1)
        self.assertTrue(any("不能标最终版" in message for message in result["errors"]))

    def test_preselected_choice_fails(self) -> None:
        self.prd.write_text(self.prd.read_text().replace('value="确认">', 'value="确认" checked>'))
        code, result = self.run_validator()
        self.assertEqual(code, 1)
        self.assertTrue(any("不得预选" in message for message in result["errors"]))


if __name__ == "__main__":
    unittest.main()
