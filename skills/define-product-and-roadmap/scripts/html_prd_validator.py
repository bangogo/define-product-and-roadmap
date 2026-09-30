#!/usr/bin/env python3
"""Validate the deterministic parts of a single HTML PRD. Python >= 3.8, stdlib only."""

from __future__ import annotations

import hashlib
import json
import re
from collections import Counter
from html.parser import HTMLParser
from pathlib import Path
from typing import Dict, List, Optional, Tuple


REQUIRED_METADATA = (
    "文档版本", "证据截止日期", "产品主形态", "次级形态", "风险修饰项",
    "当前证据阶段", "当前交付目的", "适用场景", "适用产品合同",
    "文档状态", "是否具备审批条件",
)
CHOICES = {"确认", "修改", "暂缓"}
SEMVER = re.compile(r"^v?\d+\.\d+\.\d+(?:[-+][0-9A-Za-z.-]+)?$")
REQ_ID = re.compile(r"^P[0-2]-\d{2,}$")
DECISION_ID = re.compile(r"^D-\d{2,}$")
FINGERPRINT_ATTR = re.compile(r'(data-content-fingerprint=")[^"]*(")')
FINGERPRINT_PLACEHOLDER = 'sha256:UNSTAMPED'
STATUS_ATTR = re.compile(r'(data-status=")[^"]*(")')
STATUS_META = re.compile(r'(<dt>文档状态</dt>\s*<dd>)[^<]*(</dd>)')


def content_fingerprint(document: str) -> str:
    """Hash exact source text with only the embedded fingerprint normalized."""
    if len(FINGERPRINT_ATTR.findall(document)) != 1:
        raise ValueError('HTML 须有且仅有一个 data-content-fingerprint')
    canonical = FINGERPRINT_ATTR.sub(lambda m: m.group(1) + FINGERPRINT_PLACEHOLDER + m.group(2), document)
    # Approval status changes after review; it is not a change to reviewed content.
    canonical = STATUS_ATTR.sub(lambda m: m.group(1) + 'REVIEW_STATUS' + m.group(2), canonical, count=1)
    canonical = STATUS_META.sub(lambda m: m.group(1) + 'REVIEW_STATUS' + m.group(2), canonical)
    return 'sha256:' + hashlib.sha256(canonical.encode('utf-8')).hexdigest()



class PRDParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.stack: List[str] = []
        self.ids: List[str] = []
        self.main: Dict[str, str] = {}
        self.headings: List[Tuple[str, str, str]] = []
        self.nav_links: List[Tuple[str, str]] = []
        self.metadata: Dict[str, str] = {}
        self.current_dt = ""
        self.requirements: List[str] = []
        self.decision_ids: List[str] = []
        self.decisions: Dict[str, Dict[str, object]] = {}
        self.svgs: List[Dict[str, object]] = []
        self.tables: List[Dict[str, object]] = []
        self.links: List[str] = []
        self.inputs: List[Dict[str, str]] = []
        self.buttons: List[Dict[str, str]] = []
        self.scripts = 0
        self.noscripts = 0
        self._capture: Optional[Tuple[str, Dict[str, str], List[str]]] = None
        self._active_decision: Optional[str] = None
        self._active_svg: Optional[Dict[str, object]] = None
        self._active_table: Optional[Dict[str, object]] = None
        self._active_row: Optional[List[str]] = None
        self._in_nav = 0
        self._in_metadata = 0

    def handle_starttag(self, tag: str, attrs: List[Tuple[str, Optional[str]]]) -> None:
        a = {key: (value or "") for key, value in attrs}
        if a.get("id"):
            self.ids.append(a["id"])
        if tag == "main":
            self.main = a
        if tag == "input":
            self.inputs.append(a)
        if tag == "button":
            self.buttons.append(a)
        if tag == "script":
            self.scripts += 1
        if tag == "noscript":
            self.noscripts += 1
        if tag == "nav":
            self._in_nav += 1
        if tag == "dl" and "metadata" in a.get("class", "").split():
            self._in_metadata += 1
        if tag == "a" and a.get("href"):
            self.links.append(a["href"])
            if self._in_nav and a["href"].startswith("#"):
                self._capture = ("nav-a", a, [])
        if tag in ("h1", "h2", "h3"):
            self._capture = (tag, a, [])
        elif tag in ("dt", "dd") and self._in_metadata:
            self._capture = (tag, a, [])
        if a.get("data-requirement-id"):
            self.requirements.append(a["data-requirement-id"])
        if a.get("data-decision-id"):
            decision_id = a["data-decision-id"]
            self.decision_ids.append(decision_id)
            self._active_decision = decision_id
            self.decisions.setdefault(decision_id, {"options": set(), "preselected": False})
        if tag == "input" and self._active_decision and a.get("type") == "radio":
            if a.get("name") == self._active_decision:
                options = self.decisions[self._active_decision]["options"]
                assert isinstance(options, set)
                options.add(a.get("value", ""))
            if "checked" in a:
                self.decisions[self._active_decision]["preselected"] = True
        if tag == "svg":
            self._active_svg = {"attrs": a, "title": "", "desc": ""}
            self.svgs.append(self._active_svg)
        if tag in ("title", "desc") and self._active_svg is not None:
            self._capture = ("svg-" + tag, a, [])
        if tag == "table":
            self._active_table = {"caption": "", "headers": 0, "rows": []}
            self.tables.append(self._active_table)
        if tag == "caption" and self._active_table is not None:
            self._capture = ("caption", a, [])
        if tag == "tr" and self._active_table is not None:
            self._active_row = []
        if tag in ("th", "td") and self._active_row is not None:
            self._capture = (tag, a, [])
        if tag not in ("input", "meta", "link", "br", "hr", "img", "source", "path", "rect", "circle", "line", "polygon", "polyline"):
            self.stack.append(tag)

    def handle_data(self, data: str) -> None:
        if self._capture is not None:
            self._capture[2].append(data)

    def handle_endtag(self, tag: str) -> None:
        if self._capture is not None:
            kind, attrs, parts = self._capture
            if kind == tag or kind == "svg-" + tag or (kind == "nav-a" and tag == "a"):
                value = " ".join(" ".join(parts).split())
                if kind in ("h1", "h2", "h3"):
                    self.headings.append((kind, attrs.get("id", ""), value))
                elif kind == "nav-a":
                    self.nav_links.append((attrs["href"][1:], value))
                elif kind == "dt":
                    self.current_dt = value
                elif kind == "dd" and self.current_dt:
                    self.metadata[self.current_dt] = value
                    self.current_dt = ""
                elif kind.startswith("svg-") and self._active_svg is not None:
                    self._active_svg[tag] = value
                elif kind == "caption" and self._active_table is not None:
                    self._active_table["caption"] = value
                elif kind in ("th", "td") and self._active_row is not None:
                    self._active_row.append(kind)
                self._capture = None
        if tag == "tr" and self._active_table is not None and self._active_row is not None:
            rows = self._active_table["rows"]
            assert isinstance(rows, list)
            rows.append(self._active_row)
            if any(cell == "th" for cell in self._active_row):
                self._active_table["headers"] = max(int(self._active_table["headers"]), len(self._active_row))
            self._active_row = None
        if tag == "table":
            self._active_table = None
        if tag == "svg":
            self._active_svg = None
        if tag == "nav":
            self._in_nav = max(0, self._in_nav - 1)
        if tag == "dl" and self._in_metadata:
            self._in_metadata -= 1
        if self._active_decision and tag in ("section", "article", "div"):
            # A decision card should be the innermost structural section.
            if self.stack and self.stack[-1] == tag:
                self._active_decision = None
        if tag in self.stack:
            index = len(self.stack) - 1 - self.stack[::-1].index(tag)
            del self.stack[index:]


def validate_html_prd(path: Path, decisions_path: Optional[Path] = None) -> Tuple[List[str], List[str], Optional[PRDParser]]:
    errors: List[str] = []
    warnings: List[str] = []
    try:
        document = path.read_text(encoding="utf-8-sig")
    except OSError as exc:
        return [f"无法读取 HTML PRD：{exc}"], warnings, None
    try:
        expected_fingerprint = content_fingerprint(document)
    except ValueError as exc:
        errors.append(str(exc))
        expected_fingerprint = None
    parser = PRDParser()
    try:
        parser.feed(document)
    except (ValueError, AssertionError) as exc:
        errors.append(f"HTML 解析失败：{exc}")
        return errors, warnings, parser
    if "<!doctype html" not in document[:100].lower():
        warnings.append("缺少 HTML5 doctype")
    duplicates = sorted(key for key, count in Counter(parser.ids).items() if count > 1)
    if duplicates:
        errors.append(f"重复 HTML id：{duplicates}")
    h1 = [heading for heading in parser.headings if heading[0] == "h1"]
    if len(h1) != 1 or not h1[0][2]:
        errors.append("须有一个非空 h1")
    for field in ("data-document-id", "data-version", "data-review-id", "data-status", "data-content-fingerprint"):
        if not parser.main.get(field):
            errors.append(f"main 缺少 {field}")
    if expected_fingerprint and parser.main.get("data-content-fingerprint") != expected_fingerprint:
        errors.append("内容指纹与当前 HTML 源稿不匹配；修改后须重新盖章并确认")
    if parser.main.get("data-version") and not SEMVER.fullmatch(parser.main["data-version"]):
        errors.append("main data-version 不是完整语义版本")
    if parser.main.get("data-status") not in ("审阅稿", "最终版"):
        errors.append("main data-status 只能是审阅稿或最终版")
    for field in REQUIRED_METADATA:
        if not parser.metadata.get(field):
            errors.append(f"元数据缺少 {field}")
    if parser.metadata.get("文档状态") != parser.main.get("data-status"):
        errors.append("文档状态与 main data-status 不一致")
    if parser.metadata.get("文档版本") and parser.metadata["文档版本"] != parser.main.get("data-version"):
        errors.append("文档版本与 main data-version 不一致")
    h2 = [(id_, title) for level, id_, title in parser.headings if level == "h2" and title != "目录"]
    if not h2:
        errors.append("缺少正文 h2")
    if not any(title == "目录" for level, _, title in parser.headings if level == "h2"):
        errors.append("缺少目录标题")
    if Counter(h2) != Counter(parser.nav_links):
        errors.append("目录链接须与正文 h2 的锚点和标题逐一对应")
    known = set(parser.ids)
    for href in parser.links:
        if href.startswith(("http://", "https://", "mailto:", "data:", "javascript:")):
            if href.startswith("javascript:"):
                errors.append("链接不得使用 javascript: URL")
            continue
        target, _, fragment = href.partition("#")
        if target and not (path.parent / target).exists():
            errors.append(f"本地链接文件不存在：{href}")
        elif fragment and not target and fragment not in known:
            errors.append(f"锚点不存在：{href}")
    for name, values, pattern in (("需求", parser.requirements, REQ_ID), ("决定", parser.decision_ids, DECISION_ID)):
        duplicate = sorted(key for key, count in Counter(values).items() if count > 1)
        if duplicate:
            errors.append(f"重复{name} ID：{duplicate}")
        for value in values:
            if not pattern.fullmatch(value):
                errors.append(f"无效{name} ID：{value}")
    if not any(a.get("id") == "export-decisions" for a in parser.buttons):
        errors.append("缺少可视化确认导出入口")
    if not parser.scripts or not parser.noscripts:
        errors.append("确认页须有交互脚本和无脚本阅读替代")
    for name in ("review-content", "review-visual"):
        matches = [a for a in parser.inputs if a.get("id") == name and a.get("type") == "checkbox"]
        if len(matches) != 1 or "checked" in matches[0]:
            errors.append(f"版本级确认 {name} 缺失或被预选")
    for key, card in parser.decisions.items():
        if card["options"] != CHOICES:
            errors.append(f"决定 {key} 必须提供确认／修改／暂缓三个选项")
        if card["preselected"]:
            errors.append(f"决定 {key} 不得预选")
    for index, svg in enumerate(parser.svgs, 1):
        attrs = svg["attrs"]
        assert isinstance(attrs, dict)
        labels = attrs.get("aria-labelledby", "").split()
        if attrs.get("role") != "img" or not svg["title"] or not svg["desc"] or len(labels) < 2 or any(label not in known for label in labels):
            errors.append(f"SVG {index} 缺少可访问的 title／desc／aria-labelledby")
        if not attrs.get("viewbox"):
            errors.append(f"SVG {index} 缺少 viewBox")
    for index, table in enumerate(parser.tables, 1):
        rows = table["rows"]
        assert isinstance(rows, list)
        widths = [len(row) for row in rows]
        if not table["caption"] or not table["headers"] or len(rows) < 2 or not widths or len(set(widths)) != 1:
            errors.append(f"表格 {index} 须有 caption、表头、数据行及一致列数")
    if decisions_path is not None:
        errors.extend(validate_decisions(parser, decisions_path))
    if parser.main.get("data-status") == "最终版" and decisions_path is None:
        errors.append("最终版必须提供当前审阅稿的决定与版本级确认记录")
    warnings.append("静态校验不证明 SVG 几何、桌面／窄屏／打印渲染或用户最终确认")
    return errors, warnings, parser


def validate_decisions(parser: PRDParser, path: Path) -> List[str]:
    errors: List[str] = []
    try:
        record = json.loads(path.read_text(encoding="utf-8-sig"))
    except (OSError, ValueError) as exc:
        return [f"决定记录无法读取：{exc}"]
    if not isinstance(record, dict):
        return ["决定记录必须是 JSON 对象"]
    for key, attribute in (("document_id", "data-document-id"), ("version", "data-version"), ("review_id", "data-review-id"), ("content_fingerprint", "data-content-fingerprint")):
        if record.get(key) != parser.main.get(attribute):
            errors.append(f"决定记录 {key} 与当前审阅稿不匹配")
    decisions = record.get("decisions")
    if not isinstance(decisions, list):
        return errors + ["决定记录缺少 decisions 数组"]
    ids = [item.get("decision_id") for item in decisions if isinstance(item, dict)]
    if len(ids) != len(decisions) or Counter(ids) != Counter(parser.decision_ids):
        errors.append("决定记录 ID 与 HTML 决定卡不一一对应")
    for item in decisions:
        if not isinstance(item, dict):
            continue
        if item.get("source") not in ("web-export", "conversation"):
            errors.append(f"决定 {item.get('decision_id')} 缺少有效来源")
        choice = item.get("choice")
        if choice not in CHOICES:
            errors.append(f"决定 {item.get('decision_id')} 未明确选择")
        elif choice == "修改" and not str(item.get("note", "")).strip():
            errors.append(f"决定 {item.get('decision_id')} 选择修改但没有具体说明")
        elif choice == "暂缓" and parser.main.get("data-status") == "最终版":
            errors.append(f"决定 {item.get('decision_id')} 暂缓，不能标最终版")
    confirmation = record.get("review_confirmation")
    if not isinstance(confirmation, dict) or not isinstance(confirmation.get("content"), bool) or not isinstance(confirmation.get("visual"), bool):
        errors.append("决定记录缺少明确的内容与视觉版本级确认")
    elif parser.main.get("data-status") == "最终版" and not (confirmation["content"] and confirmation["visual"]):
        errors.append("最终版需要用户对确切修订的内容和视觉均明确确认")
    return errors
