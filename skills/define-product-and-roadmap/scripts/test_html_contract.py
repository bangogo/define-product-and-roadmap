#!/usr/bin/env python3
"""HTML PRD and review-record regression tests (stdlib only)."""
from __future__ import annotations

import json
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SKILL = Path(__file__).resolve().parents[1]
TEMPLATE = SKILL / 'assets' / 'prd-template.html'
VALIDATOR = SKILL / 'scripts' / 'validate_product_docs.py'
STAMP = SKILL / 'scripts' / 'stamp_html_prd.py'


class HTMLContractTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.prd = self.root / 'product.html'
        self.prd.write_text(TEMPLATE.read_text(encoding='utf-8'), encoding='utf-8')
        self.record = self.root / 'record.json'

    def stamp(self) -> None:
        result = subprocess.run([sys.executable, str(STAMP), str(self.prd)], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)

    def validate(self, with_record: bool = False):
        command = [sys.executable, str(VALIDATOR), '--prd-html', str(self.prd), '--format', 'json']
        if with_record:
            command += ['--decisions', str(self.record)]
        result = subprocess.run(command, capture_output=True, text=True)
        return result.returncode, json.loads(result.stdout)

    def make_record(self, choice='确认', note='', source='web-export', content=False, visual=False):
        from html_prd_validator import PRDParser
        parser = PRDParser()
        parser.feed(self.prd.read_text(encoding='utf-8'))
        data = {
            'document_id': parser.main['data-document-id'],
            'version': parser.main['data-version'],
            'review_id': parser.main['data-review-id'],
            'content_fingerprint': parser.main['data-content-fingerprint'],
            'decisions': [{'decision_id': key, 'choice': choice, 'note': note, 'source': source}
                          for key in parser.decision_ids],
            'review_confirmation': {'content': content, 'visual': visual},
        }
        self.record.write_text(json.dumps(data, ensure_ascii=False), encoding='utf-8')
        return data

    def assert_fails(self, fragment, with_record=False):
        code, result = self.validate(with_record)
        self.assertEqual(code, 1, result)
        self.assertTrue(any(fragment in error for error in result['errors']), result)

    def test_standalone_draft_and_review_record(self):
        code, result = self.validate()
        self.assertEqual(code, 0, result)
        self.assertIsNone(result['roadmap'])
        self.make_record()
        self.assertEqual(self.validate(True)[0], 0)

    def test_source_edit_invalidates_stamp_and_old_record(self):
        self.make_record()
        self.prd.write_text(self.prd.read_text().replace('可审阅草稿', '有来源的审阅草稿', 1))
        self.assert_fails('内容指纹', True)
        self.stamp()
        self.assert_fails('content_fingerprint', True)

    def test_missing_duplicate_preselected_and_modified_without_note(self):
        data = self.make_record(choice='')
        self.assert_fails('未明确选择', True)
        data['decisions'][0]['choice'] = '修改'
        self.record.write_text(json.dumps(data, ensure_ascii=False))
        self.assert_fails('没有具体说明', True)
        data['decisions'] *= 2
        self.record.write_text(json.dumps(data, ensure_ascii=False))
        self.assert_fails('不一一对应', True)
        self.prd.write_text(self.prd.read_text().replace('value="确认">', 'value="确认" checked>'))
        self.stamp()
        self.assert_fails('不得预选')

    def test_stale_version_and_unknown_source(self):
        data = self.make_record()
        data['version'] = '0.0.0-draft.1'
        data['decisions'][0]['source'] = 'unknown'
        self.record.write_text(json.dumps(data, ensure_ascii=False))
        self.assert_fails('version', True)
        self.assert_fails('来源', True)

    def test_final_requires_explicit_review_and_no_deferred(self):
        self.prd.write_text(self.prd.read_text().replace('data-status="审阅稿"', 'data-status="最终版"', 1).replace('<dt>文档状态</dt><dd>审阅稿</dd>', '<dt>文档状态</dt><dd>最终版</dd>', 1))
        self.stamp()
        self.assert_fails('必须提供当前审阅稿')
        self.make_record(choice='暂缓', content=True, visual=True)
        self.assert_fails('暂缓', True)
        self.make_record(content=True, visual=False)
        self.assert_fails('内容和视觉', True)
        self.make_record(content=True, visual=True)
        self.assertEqual(self.validate(True)[0], 0)

    def test_approval_status_only_keeps_reviewed_content_fingerprint(self):
        data = self.make_record(content=True, visual=True)
        original = data['content_fingerprint']
        self.prd.write_text(self.prd.read_text().replace('data-status="审阅稿"', 'data-status="最终版"', 1)
                            .replace('<dt>文档状态</dt><dd>审阅稿</dd>', '<dt>文档状态</dt><dd>最终版</dd>', 1))
        self.stamp()
        self.assertIn(original, self.prd.read_text())
        self.assertEqual(self.validate(True)[0], 0)

    def test_no_pending_still_has_review_entry(self):
        text = self.prd.read_text()
        start = text.index('    <section class="decision"')
        end = text.index('    <section class="review-confirmation"', start)
        self.prd.write_text(text[:start] + text[end:])
        self.stamp()
        self.make_record(content=False, visual=False)
        self.assertEqual(self.validate(True)[0], 0)
        self.assertEqual(json.loads(self.record.read_text())['decisions'], [])

    def test_structure_failures(self):
        self.prd.write_text(self.prd.read_text().replace('id="evidence"', 'id="value"'))
        self.stamp()
        self.assert_fails('重复 HTML id')
        self.prd.write_text(re.sub(r'<desc id="flow-desc">.*?</desc>', '', TEMPLATE.read_text()))
        self.stamp()
        self.assert_fails('SVG 1')


if __name__ == '__main__':
    unittest.main()
