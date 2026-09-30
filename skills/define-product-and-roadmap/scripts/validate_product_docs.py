#!/usr/bin/env python3
"""验证 HTML PRD 或旧 Markdown PRD/Roadmap 对（契约 4.0.0）。

要求 Python >= 3.8,零第三方依赖。

结构契约:
- PRD 7 章 / Roadmap 6 章新目录
- 需求为优先级分组的需求块（非宽表格）,按 P0/P1/P2 组织、不标版本
- 各司其职硬校验:PRD 禁止版本落位表述;Roadmap 需求落位映射与 PRD 需求编号双向一一对应
- 真值边界表唯一权威在 Roadmap
- 场景维度:A（0→1 新产品）/B（存量迭代）分支校验
- 目录即地图:「## 目录」节与实际 H2/H3 标题双向一致（错误级）
- 分组计数:分组标题声明的「N 条」与实际需求块数一致（错误级）
- 跨文档去重:PRD 与 Roadmap ≥30 字相同正文行为警告（假设表逐字同源行白名单）
- 口径一致:「连续 N 天」类观察窗口数值两文档不一致为警告
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Sequence, Set, Tuple

from html_prd_validator import validate_html_prd


LINK_RE = re.compile(r"\[[^\]]+\]\(([^)]+)\)")
HEADING_RE = re.compile(r"^(#{1,3})\s+(.+?)\s*$", re.MULTILINE)
METADATA_RE = re.compile(r"^-\s*([^：:\n]+)[：:]\s*(.+?)\s*$")
MODULE_RE = re.compile(r"(?<![A-Z0-9])([A-Z])「([^」]+)」")
CAPABILITY_RE = re.compile(r"(?<![A-Z0-9])([A-Z][0-9]+)(?![A-Z0-9])")
BOXED_CAPABILITY_RE = re.compile(r"(?<![A-Z0-9])([A-Z][0-9]+)「([^」]+)」")
VERSION_CODE_RE = re.compile(r"(?<![A-Z0-9])R(\d+)(?![A-Z0-9])")
BOXED_VERSION_RE = re.compile(r"R(\d+)（第\s*(\d+)\s*个体验版本）「([^」]+)」")
REQUIREMENT_RE = re.compile(r"P([0-3])-(\d{2,})「([^」]+)」")
REQ_PLAIN_RE = re.compile(r"\bP([0-3])-(\d{2,})\b")
REQ_BLOCK_RE = re.compile(
    r"^\*\*(P[0-2]-(\d{2,}))「([^」]+)」\*\*（(?:优先级\s*)?(P[0-2])\s*·\s*模块\s*([A-Z](?:/[A-Z])*)）"
)
REQ_GROUP_RE = re.compile(r"^#{3,4}\s+\d+\.\d+\.\d+\s+P([0-2])\s*需求")
OPEN_MARKER_RE = re.compile(r"\[待确认\]|\b(?:TODO|TBD)\b", re.IGNORECASE)
PERCENT_TARGET_RE = re.compile(r"(?<![A-Za-z0-9])\d+(?:\.\d+)?%")
TARGET_EVIDENCE_RE = re.compile(
    r"依据|来源|基线|已批准|已确认|提案|候选|待批准|待验证|建议|proposal|baseline|source",
    re.IGNORECASE,
)
PROCESS_HEADING_RE = re.compile(
    r"创建者诉求|决策摘要|内部简报|为什么选择\s*Pattern|自检|分析过程",
    re.IGNORECASE,
)
SEMVER_RE = re.compile(r"^v?\d+\.\d+\.\d+(?:[-+][0-9A-Za-z.-]+)?$")
SELF_VERSION_RE = re.compile(
    r"(?:本文档|本需求文档|本产品需求文档|本\s*PRD|本路线图|本\s*Roadmap)"
    r"\s*(?:[（(]\s*v?(\d+(?:\.\d+){1,2})\s*[）)]|v?(\d+\.\d+\.\d+))"
)
HEADER_HISTORY_RE = re.compile(r"修订要点|修订记录|修订历史|变更记录|变更摘要|合并基线|历史版本")
HEADER_VERSION_SERIES_RE = re.compile(
    r"v?\d+\.\d+(?:\.\d+)?(?:\s*[→,，、/]\s*v?\d+\.\d+(?:\.\d+)?)+"
)
VERSION_SINCE_RE = re.compile(r"[（(]v?\d+\.\d+(?:\.\d+)?\s*起[）)]")

REQUIRED_METADATA = [
    "文档版本",
    "证据截止日期",
    "产品主形态",
    "次级形态",
    "风险修饰项",
    "当前证据阶段",
    "当前交付目的",
    "适用场景",
    "适用产品合同",
    "文档状态",
    "是否具备审批条件",
]

SCENARIO_A = "A（0→1 新产品）"
SCENARIO_B = "B（存量迭代）"
REAL_USE_STAGES = {"有限真实使用", "线上/规模化"}

PRD_OUTLINE_KEYWORDS = [
    "产品定位与承诺",
    "现状与问题",
    "产品方案",
    "规则与红线",
    "价值与成功指标",
    "复用与依赖",
    "风险与假设",
]
ROADMAP_OUTLINE_KEYWORDS = [
    "用户与终局",
    "现状与总路线",
    "本版详单",
    "体验版本路线图",
    "能力层级",
    "闸门与假设",
]

PRIMARY_SHAPES = {
    "C端交互产品",
    "内容/产物生产",
    "内部流程工具",
    "API/平台",
    "服务编排",
    "交易/市场",
}

RISK_MODIFIERS = {"AI", "敏感数据", "外部写入", "第三方复用", "发布", "交易", "高风险决策"}
EVIDENCE_STAGES = {"想法", "仅有文档", "静态设计", "交互原型", "测试接入", "有限真实使用", "线上/规模化"}
DELIVERY_PURPOSES = {"决策演示", "用户价值验证", "生产改进", "集成验证", "真实试点", "规模化"}
DOCUMENT_STATUSES = {"Draft", "Proposed", "Review Candidate", "Approved", "Superseded"}
VERSION_STATUSES = {"已有", "Proposed", "Ready", "In Progress", "Blocked", "Complete", "Superseded"}
TRUTH_STATUSES = {"真实", "测试接入", "模拟", "人工承接", "仅有文档", "已观察", "尚未验证", "历史证据"}
ASSUMPTION_TYPES = {"必须为真", "重要假设", "可逆默认", "高风险外部事实"}
ASSUMPTION_STATUSES = {"已确认", "建议假设，待确认", "待调研", "已否决"}

DUP_SENTENCE_MIN = 12
DUP_FRAGMENT_SIZE = 20
DUP_FRAGMENT_HITS = 3
DUP_MAX_REPORTS = 10
AI_EVALUATION_HEADERS = ["评估维度", "评估载体", "基线采集动作", "裁决机制", "解锁条件"]

TOC_TITLE = "目录"
CROSS_DOC_DUP_MIN = 30
TOC_ENTRY_LINK_RE = re.compile(r"^\[([^\]]+)\]\([^)]*\)$")
CONSECUTIVE_DAYS_RE = re.compile(r"连续\s*(\d+)\s*天")
REQ_GROUP_COUNT_RE = re.compile(r"（\s*(\d+)\s*条")

SHAPE_TABLES = {
    "C端交互产品": ["场景", "进入页面", "页面呈现", "用户动作", "状态变化", "可见结果", "失败与恢复"],
    "内容/产物生产": ["阶段", "输入", "处理责任", "中间/最终产物", "质量门", "失败与恢复", "证据"],
    "内部流程工具": ["角色", "触发", "处理步骤", "交接/审批", "可见结果", "异常恢复", "审计证据"],
    "API/平台": ["使用者", "接入入口", "首次成功任务", "接口/合同", "可见结果", "失败恢复", "采用证据"],
    "服务编排": ["服务场景", "用户触点", "承接方", "服务动作", "状态回流", "失败恢复", "责任边界"],
    "交易/市场": ["角色方", "发现/匹配", "信任保障", "交易动作", "履约结果", "争议恢复", "证据"],
}

REQ_FIVE_ELEMENTS = ["做什么", "你会看到", "规则", "验收", "证据"]


@dataclass
class Table:
    line: int
    end_line: int
    headers: List[str]
    rows: List[List[str]]


def issue(area: str, expected: str, actual: str, fix: str) -> str:
    return f"[{area}] 期望结构：{expected}；实际发现：{actual}；修复位置：{fix}"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    prd_input = parser.add_mutually_exclusive_group(required=True)
    prd_input.add_argument("--prd", type=Path, help="旧 Markdown PRD；需同时提供 --roadmap")
    prd_input.add_argument("--prd-html", type=Path, help="独立 HTML PRD")
    parser.add_argument("--roadmap", type=Path, help="Markdown Roadmap；HTML PRD 时可选")
    parser.add_argument("--decisions", type=Path, help="与 HTML 审阅稿绑定的决定记录 JSON")
    parser.add_argument(
        "--allow-open-questions",
        action="store_true",
        help="将假设登记表之外的 TODO/TBD/[待确认] 作为警告而非错误报告。",
    )
    parser.add_argument("--format", choices=("text", "json"), default="text")
    args = parser.parse_args()
    if args.prd and not args.roadmap:
        parser.error("--prd 旧 Markdown 模式需要 --roadmap")
    if args.prd and args.decisions:
        parser.error("--decisions 只适用于 --prd-html")
    return args


def read_markdown(path: Path, errors: List[str]) -> str:
    if not path.is_file():
        errors.append(issue(str(path), "UTF-8 Markdown 文件", "路径不存在", "文件路径"))
        return ""
    try:
        raw = path.read_bytes()
        # utf-8-sig:剥除 Windows 记事本保存的 UTF-8 BOM,否则 BOM 附着首行导致元数据全失配
        text = raw.decode("utf-8-sig")
    except UnicodeDecodeError as exc:
        errors.append(issue(str(path), "UTF-8", str(exc), "文件编码"))
        return ""
    if not text.endswith("\n"):
        errors.append(issue(str(path), "结尾换行", "文件末尾无换行", "文件末尾"))
    h1_count = sum(1 for marks, _ in HEADING_RE.findall(text) if marks == "#")
    if h1_count != 1:
        errors.append(issue(str(path), "恰好一个 H1 标题", f"找到 {h1_count} 个", "文档标题"))
    return text


def _is_separator(line: str) -> bool:
    return bool(re.fullmatch(r"\|(?:\s*:?-+:?\s*\|)+\s*", line.strip()))


def _cells(line: str) -> List[str]:
    # 按非转义管道切分:单元格内的 `\|` 是合法转义,不能计入列边界;切分后还原为字面管道
    body = line.strip()
    if body.startswith("|"):
        body = body[1:]
    if body.endswith("|") and not body.endswith("\\|"):
        body = body[:-1]
    return [cell.strip().replace("\\|", "|") for cell in re.split(r"(?<!\\)\|", body)]


def parse_tables(text: str) -> List[Table]:
    lines = text.splitlines()
    result: List[Table] = []
    index = 0
    in_fence = False
    while index < len(lines) - 1:
        stripped = lines[index].strip()
        if stripped.startswith("```"):
            in_fence = not in_fence
            index += 1
            continue
        if in_fence or not stripped.startswith("|") or not _is_separator(lines[index + 1]):
            index += 1
            continue
        start = index
        headers = _cells(lines[index])
        index += 2
        rows: List[List[str]] = []
        while index < len(lines) and lines[index].strip().startswith("|"):
            rows.append(_cells(lines[index]))
            index += 1
        result.append(Table(start + 1, index, headers, rows))
    return result


def validate_markdown(path: Path, text: str, errors: List[str]) -> None:
    for table in parse_tables(text):
        if not table.rows:
            errors.append(issue(str(path), "每个表格至少一行数据", "空表", f"{path}:{table.line}"))
        for offset, row in enumerate(table.rows, 2):
            if len(row) != len(table.headers):
                errors.append(
                    issue(
                        str(path),
                        f"{len(table.headers)} 列",
                        f"{len(row)} 列",
                        f"{path}:{table.line + offset}",
                    )
                )
            if any(not cell for cell in row):
                errors.append(issue(str(path), "数据行无空单元格", str(row), f"{path}:{table.line + offset}"))

    for raw_target in LINK_RE.findall(text):
        target = raw_target.strip("<>")
        if target.startswith(("http://", "https://", "mailto:", "#")):
            continue
        file_part = target.split("#", 1)[0]
        if file_part and not (path.parent / file_part).resolve().exists():
            errors.append(issue(str(path), "有效相对链接", raw_target, f"链接所在文件 {path}"))


def headings(text: str, level: int = 2) -> List[str]:
    prefix = "#" * level
    return [title.strip() for marks, title in HEADING_RE.findall(text) if marks == prefix]


def metadata_entries(text: str) -> Dict[str, List[Tuple[str, int]]]:
    result: Dict[str, List[Tuple[str, int]]] = {}
    first_h2 = next((index for index, line in enumerate(text.splitlines(), 1) if line.startswith("## ")), 10**9)
    for number, line in enumerate(text.splitlines(), 1):
        if number >= first_h2:
            break
        match = METADATA_RE.fullmatch(line)
        if match:
            result.setdefault(match.group(1).strip(), []).append((match.group(2).strip(), number))
    return result


def metadata(text: str) -> Dict[str, str]:
    return {key: values[0][0] for key, values in metadata_entries(text).items() if values}


def split_values(raw: str) -> List[str]:
    if raw in {"无", "不适用", "—", "-"}:
        return []
    return [item.strip() for item in re.split(r"[、,，]", raw) if item.strip()]


def find_table(text: str, expected: Sequence[str]) -> Optional[Table]:
    for table in parse_tables(text):
        if all(header in table.headers for header in expected):
            return table
    return None


def find_table_flex(
    text: str,
    exact: Sequence[str] = (),
    startswith: Sequence[str] = (),
) -> Optional[Table]:
    """表头包含全部 exact 列,且每个 startswith 前缀至少有一列命中（用于「L0（第一级）」类变体）。"""
    for table in parse_tables(text):
        if not all(header in table.headers for header in exact):
            continue
        if all(any(column.startswith(prefix) for column in table.headers) for prefix in startswith):
            return table
    return None


def expect_table(
    text: str,
    expected: Sequence[str],
    label: str,
    location: str,
    errors: List[str],
) -> Optional[Table]:
    table = find_table(text, expected)
    if table is None:
        found = [table.headers for table in parse_tables(text)]
        errors.append(issue(label, f"表头包含 {list(expected)}", f"现有表头 {found}", location))
    return table


def expect_table_flex(
    text: str,
    label: str,
    location: str,
    errors: List[str],
    exact: Sequence[str] = (),
    startswith: Sequence[str] = (),
) -> Optional[Table]:
    table = find_table_flex(text, exact, startswith)
    if table is None:
        found = [table.headers for table in parse_tables(text)]
        errors.append(issue(label, f"表头包含 {list(exact)} 且存在以 {list(startswith)} 开头的列", f"现有表头 {found}", location))
    return table


def scenario_of(meta: Dict[str, str]) -> str:
    value = meta.get("适用场景", "")
    if value.startswith("A"):
        return "A"
    if value.startswith("B"):
        return "B"
    return ""


def validate_metadata(
    prd: str,
    roadmap: str,
    errors: List[str],
    warnings: List[str],
) -> Tuple[str, List[str], List[str], str]:
    entries_by_label = {"PRD": metadata_entries(prd), "Roadmap": metadata_entries(roadmap)}
    data_by_label = {label: metadata(text) for label, text in (("PRD", prd), ("Roadmap", roadmap))}

    for label, entries in entries_by_label.items():
        for key in REQUIRED_METADATA:
            if key not in entries:
                errors.append(issue(f"{label}:metadata", f"字段「{key}」", "缺失", "H1 后、首个 H2 前的元数据"))
            elif len(entries[key]) > 1:
                errors.append(issue(f"{label}:metadata", f"字段「{key}」只出现一次", str(entries[key]), "元数据区"))

    prd_meta = data_by_label["PRD"]
    roadmap_meta = data_by_label["Roadmap"]
    for key in REQUIRED_METADATA:
        if key in prd_meta and key in roadmap_meta and prd_meta[key] != roadmap_meta[key]:
            errors.append(
                issue(
                    "cross-doc:metadata",
                    f"PRD/Roadmap 的「{key}」一致",
                    f"PRD={prd_meta[key]}，Roadmap={roadmap_meta[key]}",
                    "两份文档元数据",
                )
            )

    version = prd_meta.get("文档版本", "")
    if version and not SEMVER_RE.fullmatch(version):
        errors.append(issue("PRD:metadata", "语义版本，如 1.2.0", version, "文档版本"))
    date_value = prd_meta.get("证据截止日期", "")
    if date_value:
        try:
            dt.date.fromisoformat(date_value)
        except ValueError:
            errors.append(issue("PRD:metadata", "YYYY-MM-DD 日期", date_value, "证据截止日期"))

    scenario_raw = prd_meta.get("适用场景", "")
    scenario = scenario_of(prd_meta)
    if scenario_raw and not scenario:
        errors.append(issue("PRD:scenario", f"适用场景为「{SCENARIO_A}」或「{SCENARIO_B}」", scenario_raw, "适用场景"))

    evidence_stage = prd_meta.get("当前证据阶段", "")
    if evidence_stage and evidence_stage not in EVIDENCE_STAGES:
        errors.append(issue("PRD:metadata", f"证据阶段属于 {sorted(EVIDENCE_STAGES)}", evidence_stage, "当前证据阶段"))
    if scenario == "A" and evidence_stage in REAL_USE_STAGES:
        warnings.append(
            issue(
                "PRD:scenario",
                "证据阶段已进入真实使用,建议与用户确认切换为场景 B（回填 R0 基线、补 B 专属维度、升 minor 版）",
                f"适用场景=A,证据阶段={evidence_stage}",
                "A→B 演进承接",
            )
        )

    primary = prd_meta.get("产品主形态", "")
    if primary not in PRIMARY_SHAPES:
        errors.append(issue("PRD:product-shape", f"一个明确主形态 {sorted(PRIMARY_SHAPES)}", primary or "缺失", "产品主形态"))

    secondaries = split_values(prd_meta.get("次级形态", "无"))
    if len(secondaries) > 2:
        errors.append(issue("PRD:product-shape", "最多两个次级形态", str(secondaries), "次级形态"))
    if len(secondaries) != len(set(secondaries)):
        errors.append(issue("PRD:product-shape", "次级形态不重复", str(secondaries), "次级形态"))
    for secondary in secondaries:
        if secondary not in PRIMARY_SHAPES:
            errors.append(issue("PRD:product-shape", f"次级形态属于 {sorted(PRIMARY_SHAPES)}", secondary, "次级形态"))
        if secondary == primary:
            errors.append(issue("PRD:product-shape", "主形态不重复为次级形态", secondary, "次级形态"))

    risks = split_values(prd_meta.get("风险修饰项", "无"))
    if len(risks) != len(set(risks)):
        errors.append(issue("PRD:risk", "风险修饰项不重复", str(risks), "风险修饰项"))
    for risk in risks:
        if risk not in RISK_MODIFIERS:
            errors.append(issue("PRD:risk", f"风险修饰项属于 {sorted(RISK_MODIFIERS)}", risk, "风险修饰项"))
    if primary == "交易/市场" and "交易" not in risks:
        errors.append(issue("PRD:risk", "交易/市场主形态同时声明交易风险", str(risks) or "无", "风险修饰项"))

    purpose = prd_meta.get("当前交付目的", "")
    if purpose and purpose not in DELIVERY_PURPOSES:
        errors.append(issue("PRD:metadata", f"交付目的属于 {sorted(DELIVERY_PURPOSES)}", purpose, "当前交付目的"))
    doc_status = prd_meta.get("文档状态", "")
    if doc_status and doc_status not in DOCUMENT_STATUSES:
        errors.append(issue("PRD:metadata", f"文档状态属于 {sorted(DOCUMENT_STATUSES)}", doc_status, "文档状态"))
    readiness = prd_meta.get("是否具备审批条件", "")
    if readiness and not readiness.startswith(("是", "否")):
        errors.append(issue("PRD:metadata", "以「是」或「否」开头并说明边界", readiness, "是否具备审批条件"))
    if doc_status == "Approved" and not readiness.startswith("是（已批准"):
        errors.append(issue("PRD:approval-readiness", "Approved 对应「是（已批准…）」", readiness, "元数据"))

    contracts = prd_meta.get("适用产品合同", "")
    if contracts:
        if "通用" not in contracts:
            errors.append(issue("PRD:contracts", "包含通用合同", contracts, "适用产品合同"))
        if primary and primary not in contracts:
            errors.append(issue("PRD:contracts", f"包含主形态「{primary}」", contracts, "适用产品合同"))
        for risk in risks:
            if risk not in contracts:
                errors.append(issue("PRD:contracts", f"包含风险合同「{risk}」", contracts, "适用产品合同"))

    return primary, secondaries, risks, scenario


def validate_outline(prd: str, roadmap: str, errors: List[str]) -> None:
    # 「## 目录」是导航节,不计入正文章节序列
    prd_h2 = [title for title in headings(prd) if title != TOC_TITLE]
    roadmap_h2 = [title for title in headings(roadmap) if title != TOC_TITLE]
    for index, keyword in enumerate(PRD_OUTLINE_KEYWORDS):
        actual = prd_h2[index] if index < len(prd_h2) else "缺失"
        if keyword not in actual:
            errors.append(issue("PRD:outline", f"第 {index + 1} 个 H2 包含「{keyword}」", actual, "PRD 开篇结构"))
    for index, keyword in enumerate(ROADMAP_OUTLINE_KEYWORDS):
        actual = roadmap_h2[index] if index < len(roadmap_h2) else "缺失"
        if keyword not in actual:
            errors.append(issue("Roadmap:outline", f"第 {index + 1} 个 H2 包含「{keyword}」", actual, "Roadmap 开篇结构"))

    for label, text in (("PRD", prd), ("Roadmap", roadmap)):
        for _, title in HEADING_RE.findall(text):
            if PROCESS_HEADING_RE.search(title):
                errors.append(issue(f"{label}:outline", "产品面向的正式章节", title, "将内部分析移出正式文档"))


def validate_status_column(
    table: Optional[Table],
    header: str,
    allowed: Set[str],
    area: str,
    errors: List[str],
) -> None:
    if table is None:
        return
    index = table.headers.index(header)
    for offset, row in enumerate(table.rows, 2):
        if index >= len(row) or row[index] not in allowed:
            actual = row[index] if index < len(row) else "缺失"
            errors.append(issue(area, f"{header}属于 {sorted(allowed)}", actual, f"第 {table.line + offset} 行"))


def validate_universal_tables(
    prd: str,
    roadmap: str,
    scenario: str,
    errors: List[str],
) -> Dict[str, Optional[Table]]:
    tables: Dict[str, Optional[Table]] = {}

    # B 场景必选当前效果表;A 场景允许缺失（章变形为问题假设与冷启动）
    if scenario == "B":
        tables["current"] = expect_table(
            prd, ["观察对象", "当前效果", "证据状态", "证据来源", "当前缺口"], "PRD:current-effect", "现状与问题章节", errors
        )
        validate_status_column(tables["current"], "证据状态", TRUTH_STATUSES, "PRD:current-effect", errors)

    # 复用注册:B 场景为复用决策注册;A 场景允许外部依赖表替代
    if scenario == "B":
        tables["reuse"] = expect_table(
            prd,
            ["来源", "版本/日期", "复用决策", "负责什么", "已证实能力", "产品映射", "证据边界"],
            "PRD:reference-reuse",
            "复用与依赖章节",
            errors,
        )
    else:
        tables["reuse"] = find_table(
            prd, ["来源", "版本/日期", "复用决策", "负责什么", "已证实能力", "产品映射", "证据边界"]
        ) or find_table(prd, ["依赖", "用途", "可用性"])

    tables["modules"] = expect_table(
        prd,
        ["模块", "责任", "输入", "用户可见输出", "当前状态", "失败与恢复", "优先级"],
        "PRD:modules",
        "产品方案·能力地图章节",
        errors,
    )

    tables["success"] = expect_table_flex(
        prd,
        "PRD:success",
        "价值与成功指标章节",
        errors,
        exact=["成功信号", "对应用户价值", "当前基线", "本版判定", "证据方法", "结论状态"],
        startswith=["指标组"],
    )

    tables["prd_assumptions"] = expect_table(
        prd, ["类型", "假设或决策", "状态", "依据", "对产品影响", "确认人/下一步"], "PRD:assumptions", "风险与假设章节", errors
    )

    tables["levels"] = expect_table_flex(
        roadmap,
        "Roadmap:capability-levels",
        "能力层级章节",
        errors,
        exact=["产品模块"],
        startswith=["L0", "L1", "L2"],
    )
    tables["versions"] = expect_table_flex(
        roadmap,
        "Roadmap:versions",
        "体验版本路线图·版本总表",
        errors,
        exact=["版本", "一句话任务", "状态"],
        startswith=["你会看到什么"],
    )
    validate_status_column(tables["versions"], "状态", VERSION_STATUSES, "Roadmap:versions", errors)
    if scenario == "B" and tables["versions"] is not None:
        version_header = next(name for name in ("体验版本", "版本") if name in tables["versions"].headers)
        version_index = tables["versions"].headers.index(version_header)
        has_r0 = any(
            version_index < len(row) and row[version_index].startswith("R0")
            for row in tables["versions"].rows
        )
        if not has_r0:
            errors.append(
                issue("Roadmap:scenario", "B（存量迭代）场景的版本总表包含 R0 当前基线行", "未找到 R0 行", "版本总表")
            )
    tables["deliverables"] = expect_table(
        roadmap,
        ["交付项", "用户可见结果", "当前实现", "真实性", "验收证据"],
        "Roadmap:deliverables",
        "本版详单章节",
        errors,
    )
    validate_status_column(tables["deliverables"], "真实性", TRUTH_STATUSES, "Roadmap:deliverables", errors)
    tables["truth"] = expect_table(
        roadmap, ["层面", "当前实现", "真实性", "用户可见标识", "后续替换"], "Roadmap:truth-boundary", "本版详单·真值边界表", errors
    )
    validate_status_column(tables["truth"], "真实性", TRUTH_STATUSES, "Roadmap:truth-boundary", errors)
    tables["gates"] = expect_table(
        roadmap,
        ["闸门", "所需证据", "决策人", "通过后授权", "卡住回到哪"],
        "Roadmap:gates",
        "闸门与假设章节",
        errors,
    )
    tables["roadmap_assumptions"] = expect_table(
        roadmap, ["类型", "假设或决策", "状态", "依据", "对产品影响", "确认人/下一步"], "Roadmap:assumptions", "闸门与假设章节", errors
    )
    return tables


def validate_shape_contracts(
    primary: str,
    secondaries: Sequence[str],
    risks: Sequence[str],
    prd: str,
    errors: List[str],
) -> None:
    for shape in [primary] + list(secondaries):
        headers = SHAPE_TABLES.get(shape)
        if headers:
            expect_table(prd, headers, f"PRD:shape:{shape}", f"{shape} 产品合同章节（产品方案·系统运转）", errors)

    if risks:
        risk_table = expect_table(
            prd,
            ["风险修饰项", "触发场景", "潜在损害", "预防控制", "用户控制", "失败/未知状态", "审计证据", "发布/审批门"],
            "PRD:risk",
            "风险与假设章节",
            errors,
        )
        if risk_table:
            index = risk_table.headers.index("风险修饰项")
            covered = {row[index] for row in risk_table.rows if index < len(row)}
            missing = sorted(set(risks) - covered)
            if missing:
                errors.append(issue("PRD:risk", "每个风险修饰项有一行控制合同", str(missing), f"PRD:{risk_table.line}"))
    if "AI" in risks:
        expect_table(
            prd,
            ["场景", "触发入口", "携带上下文", "助手响应", "关键追问", "行动边界", "可见结果", "回退"],
            "PRD:risk:AI",
            "AI 合同章节（产品方案·AI 参与边界）",
            errors,
        )


@dataclass
class RequirementBlock:
    line: int
    identifier: str
    priority: str
    name: str
    modules: List[str]


def extract_requirement_blocks(prd: str) -> List[RequirementBlock]:
    blocks: List[RequirementBlock] = []
    for number, line in enumerate(prd.splitlines(), 1):
        match = REQ_BLOCK_RE.match(line.strip())
        if match:
            blocks.append(
                RequirementBlock(
                    line=number,
                    identifier=match.group(1),
                    priority=match.group(4),
                    name=match.group(3),
                    modules=match.group(5).split("/"),
                )
            )
    return blocks


def requirement_section_lines(prd: str) -> List[Tuple[int, str]]:
    """需求清单区段:自「x.2 需求清单」节标题（含引言）起,到下一个同级或更高级标题为止。"""
    lines = prd.splitlines()
    start = next(
        (
            index
            for index, line in enumerate(lines)
            if re.match(r"^#{2,4}\s+\d+\.\d+\s*需求清单", line.strip())
        ),
        None,
    )
    if start is None:
        start = next((index for index, line in enumerate(lines) if REQ_GROUP_RE.match(line.strip())), None)
    if start is None:
        return []
    result: List[Tuple[int, str]] = []
    for index in range(start, len(lines)):
        stripped = lines[index].strip()
        # 终止条件与起始层级对称(起始容忍 H2-H4,则任何 H1-H4 标题都终止区段)
        if index > start and re.match(r"^#{1,4}\s", stripped):
            break
        result.append((index + 1, stripped))
    return result


def validate_requirement_blocks(
    prd: str,
    modules: Dict[str, str],
    errors: List[str],
) -> List[str]:
    """校验需求块格式、分组、五要素与模块映射;返回全部需求编号（供落位映射比对）。"""
    lines = prd.splitlines()
    blocks = extract_requirement_blocks(prd)

    group_headers: List[Tuple[int, str]] = []
    for number, line in enumerate(lines, 1):
        match = REQ_GROUP_RE.match(line.strip())
        if match:
            group_headers.append((number, match.group(1)))

    if not group_headers:
        errors.append(
            issue("PRD:requirements", "按 P0/P1/P2 优先级分组的需求小节（如「#### 3.2.1 P0 需求:…」）", "未找到分组标题", "产品方案·需求清单")
        )
    if blocks and not group_headers:
        errors.append(issue("PRD:requirements", "需求块置于优先级分组小节之下", "存在需求块但无分组", "产品方案·需求清单"))

    # 每个需求块的优先级须与其所在分组一致
    seen: Set[str] = set()
    for block in blocks:
        if not REQUIREMENT_RE.fullmatch(f"{block.identifier}「{block.name}」"):
            errors.append(
                issue("PRD:requirement-id", "P0-01「要求名称」", f"{block.identifier}「{block.name}」", f"PRD:{block.line}")
            )
        if block.identifier in seen:
            errors.append(issue("PRD:requirement-id", "唯一需求编号", block.identifier, f"PRD:{block.line}"))
        seen.add(block.identifier)
        for code in block.modules:
            if code not in modules:
                errors.append(
                    issue("PRD:requirements", "需求块模块映射到能力地图已定义模块", f"{block.identifier} 引用 {code}", f"PRD:{block.line}")
                )
        enclosing = [level for number, level in group_headers if number < block.line]
        if enclosing:
            group_level = enclosing[-1]
            if block.priority != f"P{group_level}":
                errors.append(
                    issue(
                        "PRD:requirements",
                        f"需求优先级与所在分组一致（P{group_level}）",
                        f"{block.identifier} 标注 {block.priority}",
                        f"PRD:{block.line}",
                    )
                )
        # 五要素完整性:块首行到下一个需求块/标题之间(不设行数窗口,长需求块不漏扫)
        following: List[str] = []
        for offset in range(block.line, len(lines)):
            text = lines[offset].strip()
            if offset + 1 > block.line and (REQ_BLOCK_RE.match(text) or text.startswith("#")):
                break
            following.append(text)
        body = "\n".join(following)
        for element in REQ_FIVE_ELEMENTS:
            if f"- {element}" not in body and f"- **{element}" not in body:
                errors.append(
                    issue("PRD:requirements", f"五要素行之一「- {element}：…」", f"{block.identifier} 缺该要素", f"PRD:{block.line}")
                )

    priorities = {block.priority for block in blocks}
    if blocks and "P0" not in priorities:
        errors.append(issue("PRD:requirements", "至少一组 P0（最高优先级）需求", str(sorted(priorities)), "产品方案·需求清单"))
    return sorted(seen)


def validate_separation_of_duties(
    prd: str,
    roadmap: str,
    prd_requirement_ids: Sequence[str],
    errors: List[str],
) -> None:
    """各司其职:PRD 不标版本;Roadmap 需求落位映射为唯一权威且与 PRD 编号双向一致。"""
    # 1. PRD 全文禁止「落位 R*」类版本编排表述
    for number, line in enumerate(prd.splitlines(), 1):
        if re.search(r"落位\s*R\d", line):
            errors.append(
                issue("PRD:separation", "PRD 不标版本（版本落位只由 Roadmap 需求落位映射编排）", line.strip()[:60], f"PRD:{number}")
            )

    # 2. PRD 需求清单区段内不得出现体验版本编码（需求按优先级组织）
    for number, line in requirement_section_lines(prd):
        if VERSION_CODE_RE.search(line):
            errors.append(
                issue(
                    "PRD:separation",
                    "需求清单区段不出现 R* 版本编码（落位由 Roadmap 统一编排）",
                    line[:60],
                    f"PRD:{number}",
                )
            )

    # 3. Roadmap 需求落位映射:存在性声明 + 双向一致
    lines = roadmap.splitlines()
    mapping_start = next(
        (index for index, line in enumerate(lines) if re.match(r"^#{2,4}\s+\d+\.\d+\s*需求落位映射", line.strip())),
        None,
    )
    if mapping_start is None:
        errors.append(issue("Roadmap:separation", "「需求落位映射」小节（每条需求落位版本的唯一权威）", "未找到该小节", "体验版本路线图"))
        return
    mapping_ids: Set[str] = set()
    uniqueness: Dict[str, int] = {}
    for index in range(mapping_start + 1, len(lines)):
        stripped = lines[index].strip()
        # 终止条件与起始层级对称(起始容忍 H2-H4,则任何 H1-H4 标题都终止区段)
        if re.match(r"^#{1,4}\s", stripped):
            break
        for level, number in REQ_PLAIN_RE.findall(stripped):
            identifier = f"P{level}-{number}"
            mapping_ids.add(identifier)
            uniqueness[identifier] = uniqueness.get(identifier, 0) + 1

    duplicated = sorted(identifier for identifier, count in uniqueness.items() if count > 1)
    if duplicated:
        errors.append(issue("Roadmap:separation", "同一需求只落位一个版本", f"重复出现 {duplicated}", "需求落位映射"))

    prd_set = set(prd_requirement_ids)
    unmapped = sorted(prd_set - mapping_ids)
    unknown = sorted(mapping_ids - prd_set)
    if unmapped:
        errors.append(
            issue("Roadmap:separation", "PRD 每条需求在落位映射中有落位版本", f"未落位 {unmapped}", "需求落位映射")
        )
    if unknown:
        errors.append(
            issue("Roadmap:separation", "落位映射只引用 PRD 已定义的需求编号", f"PRD 未定义 {unknown}", "需求落位映射")
        )


def canonical_modules_from_table(table: Optional[Table]) -> Tuple[Dict[str, str], List[str]]:
    result: Dict[str, str] = {}
    conflicts: List[str] = []
    if table is None:
        return result, conflicts
    header = next((name for name in ("产品模块", "模块") if name in table.headers), None)
    if header is None:
        return result, conflicts
    module_index = table.headers.index(header)
    for row in table.rows:
        if module_index >= len(row):
            continue
        matches = MODULE_RE.findall(row[module_index])
        if len(matches) != 1:
            conflicts.append(f"invalid module cell: {row[module_index]}")
            continue
        code, name = matches[0]
        if code in result and result[code] != name:
            conflicts.append(f"{code}: {result[code]} / {name}")
        result[code] = name
    return result, conflicts


def validate_alignment(
    prd: str,
    roadmap: str,
    tables: Dict[str, Optional[Table]],
    errors: List[str],
) -> List[str]:
    prd_modules, prd_conflicts = canonical_modules_from_table(tables.get("modules"))
    roadmap_modules, roadmap_conflicts = canonical_modules_from_table(tables.get("levels"))
    if prd_conflicts:
        errors.append(issue("PRD:modules", "每个模块代码只有一个名称", str(prd_conflicts), "能力地图章节"))
    if roadmap_conflicts:
        errors.append(issue("Roadmap:modules", "每个模块代码只有一个名称", str(roadmap_conflicts), "能力层级章节"))
    if not prd_modules or not roadmap_modules:
        errors.append(issue("cross-doc:modules", "PRD/Roadmap 均定义 A「名称」类模块", f"PRD={prd_modules}，Roadmap={roadmap_modules}", "能力地图/能力层级章节"))
    elif prd_modules != roadmap_modules:
        errors.append(issue("cross-doc:modules", "模块代码与名称一致", f"PRD={prd_modules}，Roadmap={roadmap_modules}", "两份文档能力章节"))

    for label, text, module_map in (
        ("PRD", prd, prd_modules),
        ("Roadmap", roadmap, roadmap_modules),
    ):
        if not module_map:
            continue
        for number, line in prose_lines(text):
            for code, name in MODULE_RE.findall(line):
                if code not in module_map:
                    errors.append(issue(f"{label}:prose-codes", "散文中的模块编码在权威表定义", f"{code}「{name}」", f"{label}:{number}"))
                elif module_map[code] != name:
                    errors.append(issue(f"{label}:prose-codes", "散文中的模块名称与权威表一致", f"{code}「{name}」≠「{module_map[code]}」", f"{label}:{number}"))
            for code, _ in BOXED_CAPABILITY_RE.findall(line):
                if code[0] == "R" and code[1:].isdigit():
                    continue
                if code[0] not in module_map:
                    errors.append(issue(f"{label}:prose-codes", "散文中的能力编码前缀映射到已定义模块", code, f"{label}:{number}"))

    requirement_ids = validate_requirement_blocks(prd, prd_modules, errors)

    capability_cells: List[Tuple[str, str]] = []
    levels_table = tables.get("levels")
    if levels_table:
        level_headers = [header for header in levels_table.headers if header.startswith(("L0", "L1", "L2"))]
        for offset, row in enumerate(levels_table.rows, 2):
            for header in level_headers:
                index = levels_table.headers.index(header)
                if index < len(row):
                    capability_cells.append((row[index], f"Roadmap:{levels_table.line + offset}"))
    # 每版详述的「核心能力」散文行同样纳入能力编码检查
    for number, line in prose_lines(roadmap):
        if line.startswith(("- 核心能力", "核心能力")):
            capability_cells.append((line, f"Roadmap:{number}"))

    roadmap_capabilities: Dict[str, str] = {}
    for cell, location in capability_cells:
        for code, name in BOXED_CAPABILITY_RE.findall(cell):
            if code in roadmap_capabilities and roadmap_capabilities[code] != name:
                errors.append(issue("Roadmap:capability-code", "每个能力代码名称唯一", f"{code}: {roadmap_capabilities[code]} / {name}", location))
            roadmap_capabilities[code] = name
            if code[0] not in roadmap_modules:
                errors.append(issue("Roadmap:capability-code", "能力前缀映射到已定义模块", code, location))
        for match in CAPABILITY_RE.finditer(cell):
            if match.group(1)[0] == "L":
                continue  # L0/L1/L2 为成熟度等级刻度保留字，不是能力编码
            if not cell.startswith("「", match.end()):
                errors.append(issue("Roadmap:capability-code", f"{match.group(1)}「能力名称」", cell, location))
    if not roadmap_capabilities:
        errors.append(issue("Roadmap:capability-code", "至少一个 A0「能力」", "未找到", "能力层级章节"))

    defined_versions: Set[int] = set()
    planned_versions: List[int] = []
    version_table = tables.get("versions")
    if version_table:
        version_header = next(name for name in ("体验版本", "版本") if name in version_table.headers)
        version_index = version_table.headers.index(version_header)
        for offset, row in enumerate(version_table.rows, 2):
            if version_index >= len(row):
                continue
            cell = row[version_index]
            # 总表接受短格式 R1「名称」（全称在每版详述块给出）或全格式 R1（第 1 个体验版本）「名称」
            short = re.fullmatch(r"R(\d+)「([^」]+)」", cell)
            full = BOXED_VERSION_RE.fullmatch(cell)
            match = full or short
            if not match:
                errors.append(issue("Roadmap:version-code", "R1「名称」（总表短格式）或 R1（第 1 个体验版本）「名称」", cell, f"Roadmap:{version_table.line + offset}"))
                continue
            number = int(match.group(1))
            if number == 0:
                defined_versions.add(0)
                continue
            if full:
                ordinal = int(full.group(2))
                if number != ordinal:
                    errors.append(issue("Roadmap:version-code", "非零版本号与中文序号一致", cell, f"Roadmap:{version_table.line + offset}"))
            if number in defined_versions:
                errors.append(issue("Roadmap:version-code", "版本号唯一", cell, f"Roadmap:{version_table.line + offset}"))
            defined_versions.add(number)
            planned_versions.append(number)
    if planned_versions:
        expected = list(range(1, max(planned_versions) + 1))
        if sorted(planned_versions) != expected:
            errors.append(issue("Roadmap:version-code", f"从 R1 连续编号 {expected}", str(sorted(planned_versions)), "体验版本路线图"))
    used_versions = {int(number) for number in VERSION_CODE_RE.findall(roadmap)}
    missing = sorted(used_versions - defined_versions)
    if missing:
        errors.append(issue("Roadmap:version-code", "所有版本代码在版本总表中具名定义", str(missing), "体验版本路线图"))

    # 每版详述:总表中每个非 R0 版本应有对应详述块（**R{n}（第 {n} 个体验版本）「…」**）,且序号一致
    detail_versions: Set[int] = set()
    for number, line in enumerate(roadmap.splitlines(), 1):
        stripped = line.strip()
        if stripped.startswith("**"):
            for match in BOXED_VERSION_RE.finditer(stripped):
                version_number, ordinal = int(match.group(1)), int(match.group(2))
                if version_number != ordinal:
                    errors.append(
                        issue("Roadmap:version-code", "非零版本号与中文序号一致", match.group(0), f"Roadmap:{number}")
                    )
                detail_versions.add(version_number)
    lacking_detail = sorted(set(planned_versions) - detail_versions)
    if lacking_detail:
        errors.append(
            issue("Roadmap:version-detail", "版本总表每个非零版本有每版详述块", f"缺详述 R{lacking_detail}", "体验版本路线图·每版详述")
        )

    prd_assumptions = tables.get("prd_assumptions")
    roadmap_assumptions = tables.get("roadmap_assumptions")
    if prd_assumptions and roadmap_assumptions:
        if prd_assumptions.rows != roadmap_assumptions.rows:
            errors.append(issue("cross-doc:assumptions", "两份文档的物质性假设行完全一致", f"PRD={prd_assumptions.rows}；Roadmap={roadmap_assumptions.rows}", "两份假设表"))

    return requirement_ids


def validate_assumptions(
    prd: str,
    table: Optional[Table],
    errors: List[str],
    warnings: List[str],
) -> None:
    if table is None:
        return
    type_index = table.headers.index("类型")
    status_index = table.headers.index("状态")
    blocking: List[str] = []
    for offset, row in enumerate(table.rows, 2):
        if type_index >= len(row) or status_index >= len(row):
            continue
        kind, status = row[type_index], row[status_index]
        if kind not in ASSUMPTION_TYPES:
            errors.append(issue("PRD:assumptions", f"类型属于 {sorted(ASSUMPTION_TYPES)}", kind, f"PRD:{table.line + offset}"))
        if status not in ASSUMPTION_STATUSES:
            errors.append(issue("PRD:assumptions", f"状态属于 {sorted(ASSUMPTION_STATUSES)}", status, f"PRD:{table.line + offset}"))
        if kind == "必须为真" and status != "已确认":
            blocking.append(row[1] if len(row) > 1 else "未命名假设")

    readiness = metadata(prd).get("是否具备审批条件", "")
    if blocking and readiness.startswith("是"):
        errors.append(issue("PRD:approval-readiness", "未确认或否决的必须为真假设使审批条件为否", f"阻断项={blocking}，审批条件={readiness}", "元数据和假设表"))
    elif blocking:
        warnings.append(f"PRD remains not approval-ready because must-be-true assumptions are unresolved: {blocking}")


def assumption_line_numbers(text: str) -> Set[int]:
    table = find_table(text, ["类型", "假设或决策", "状态", "依据", "对产品影响", "确认人/下一步"])
    if table is None:
        return set()
    return set(range(table.line, table.end_line + 1))


def validate_open_markers(
    documents: Sequence[Tuple[Path, str]],
    allow: bool,
    errors: List[str],
    warnings: List[str],
) -> None:
    for path, text in documents:
        assumption_lines = assumption_line_numbers(text)
        for number, line in enumerate(text.splitlines(), 1):
            if OPEN_MARKER_RE.search(line) and number not in assumption_lines:
                message = issue(str(path), "开放项进入假设登记表", line.strip(), f"{path}:{number}")
                (warnings if allow else errors).append(message)


def validate_numeric_targets(documents: Sequence[Tuple[str, str]], errors: List[str]) -> None:
    for label, text in documents:
        for number, line in enumerate(text.splitlines(), 1):
            if PERCENT_TARGET_RE.search(line) and not TARGET_EVIDENCE_RE.search(line):
                errors.append(issue(f"{label}:numeric-target", "数字目标带来源、基线、提案或待验证状态", line.strip(), f"{label}:{number}"))


def prose_lines(text: str) -> List[Tuple[int, str]]:
    """返回正文行（跳过元数据区、标题、表格、代码围栏与目录锚点行），带行号。"""
    first_h2 = next((number for number, line in enumerate(text.splitlines(), 1) if line.startswith("## ")), 10**9)
    result: List[Tuple[int, str]] = []
    in_fence = False
    for number, line in enumerate(text.splitlines(), 1):
        stripped = line.strip()
        if stripped.startswith("```"):
            in_fence = not in_fence
            continue
        if in_fence or number <= first_h2 or stripped.startswith(("|", "#")) or not stripped:
            continue
        # 目录锚点行（- [标题](#锚点)）是导航,不是正文复述
        if stripped.startswith("- ") and TOC_ENTRY_LINK_RE.match(stripped[2:].strip()):
            continue
        result.append((number, stripped))
    return result


def _dup_normalize(text: str) -> str:
    text = BOXED_VERSION_RE.sub(r"R\1", text)
    text = BOXED_CAPABILITY_RE.sub(r"\1", text)
    text = REQUIREMENT_RE.sub(r"P\1-\2", text)
    text = MODULE_RE.sub(r"\1", text)
    return re.sub(r"[^0-9A-Za-z一-鿿]", "", text)


def validate_duplication(label: str, text: str, warnings: List[str]) -> None:
    lines = prose_lines(text)
    reported = 0

    sentences: Dict[str, List[int]] = {}
    for number, line in lines:
        for piece in re.split(r"[。！？；!?;]", line):
            normalized = _dup_normalize(piece)
            if len(normalized) >= DUP_SENTENCE_MIN:
                sentences.setdefault(normalized, []).append(number)
    duplicated = [sentence for sentence, numbers in sentences.items() if len(numbers) >= 2]
    duplicated.sort(key=lambda sentence: sentences[sentence][0])
    for sentence in duplicated:
        if reported >= DUP_MAX_REPORTS:
            break
        numbers = sentences[sentence]
        warnings.append(
            issue(
                f"{label}:presentation:duplication",
                "同一句子在一份文档正文只出现一次；复述处改为引用（如 见 §x）",
                f"「{sentence[:24]}…」出现 {len(numbers)} 次",
                f"{label}:{'、'.join(str(number) for number in numbers[:6])}",
            )
        )
        reported += 1

    stream_parts: List[str] = []
    stream_lines: List[int] = []
    for number, line in lines:
        normalized_line = _dup_normalize(line)
        if normalized_line:
            stream_parts.append(normalized_line)
            stream_lines.extend([number] * len(normalized_line))
    stream = "".join(stream_parts)
    counts: Dict[str, int] = {}
    first_position: Dict[str, int] = {}
    for start in range(max(0, len(stream) - DUP_FRAGMENT_SIZE + 1)):
        fragment = stream[start:start + DUP_FRAGMENT_SIZE]
        counts[fragment] = counts.get(fragment, 0) + 1
        first_position.setdefault(fragment, start)
    hot = sorted(
        (fragment for fragment, count in counts.items() if count >= DUP_FRAGMENT_HITS),
        key=lambda fragment: first_position[fragment],
    )
    cluster_end = -1
    for fragment in hot:
        if reported >= DUP_MAX_REPORTS:
            break
        position = first_position[fragment]
        if position <= cluster_end:
            continue
        cluster_end = position + DUP_FRAGMENT_SIZE
        if any(fragment in sentence for sentence in duplicated):
            continue
        warnings.append(
            issue(
                f"{label}:presentation:duplication",
                f"相同片段出现少于 {DUP_FRAGMENT_HITS} 次；规则单源化后用引用替代",
                f"「{fragment[:30]}…」出现 {counts[fragment]} 次",
                f"{label}:{stream_lines[position]}",
            )
        )
        reported += 1


def validate_header_archaeology(label: str, text: str, warnings: List[str]) -> None:
    first_h2 = next((number for number, line in enumerate(text.splitlines(), 1) if line.startswith("## ")), 10**9)
    for number, line in enumerate(text.splitlines(), 1):
        if number >= first_h2:
            break
        if line.startswith("- 文档版本："):
            continue
        if HEADER_HISTORY_RE.search(line) or HEADER_VERSION_SERIES_RE.search(line):
            warnings.append(
                issue(
                    f"{label}:presentation:header-archaeology",
                    "H1 与首个 H2 之间只保留 11 个元数据字段；修订史外置到 CHANGELOG 或独立修订文件",
                    line.strip()[:60],
                    f"{label}:{number}",
                )
            )
            break


def validate_version_archaeology(label: str, text: str, warnings: List[str]) -> None:
    for number, line in enumerate(text.splitlines(), 1):
        if line.startswith("- 文档版本："):
            continue
        match = VERSION_SINCE_RE.search(line)
        if match:
            warnings.append(
                issue(
                    f"{label}:presentation:version-archaeology",
                    "版本沿革写入 CHANGELOG，不用「（0.x.y 起）」考古括号",
                    match.group(0),
                    f"{label}:{number}",
                )
            )


def validate_self_version(label: str, text: str, errors: List[str]) -> None:
    declared = metadata(text).get("文档版本", "").lstrip("v")
    if not declared:
        return
    for number, line in enumerate(text.splitlines(), 1):
        for match in SELF_VERSION_RE.finditer(line):
            found = match.group(1) or match.group(2) or ""
            if found and found != declared:
                errors.append(
                    issue(
                        f"{label}:self-version",
                        f"正文自引用版本与元数据「文档版本」一致（{declared}）",
                        match.group(0),
                        f"{label}:{number}",
                    )
                )


def validate_table_convergence(label: str, text: str, warnings: List[str]) -> None:
    seen: Dict[Tuple[str, ...], Table] = {}
    for table in parse_tables(text):
        key = tuple(table.headers)
        if key in seen:
            warnings.append(
                issue(
                    f"{label}:presentation:table-convergence",
                    "表头完全相同的表格在一份文档内只出现一次；同轴信息合并为一张表",
                    f"表头 {table.headers}",
                    f"{label}:{seen[key].line} 与 {label}:{table.line}",
                )
            )
        else:
            seen[key] = table


def heading_records(text: str) -> List[Tuple[int, int, str]]:
    """带行号的 H1-H3 标题记录（跳过代码围栏）: (行号, 层级, 标题)。"""
    result: List[Tuple[int, int, str]] = []
    in_fence = False
    for number, line in enumerate(text.splitlines(), 1):
        stripped = line.strip()
        if stripped.startswith("```"):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        match = re.match(r"^(#{1,3})\s+(.+?)\s*$", stripped)
        if match:
            result.append((number, len(match.group(1)), match.group(2).strip()))
    return result


def toc_entries(text: str) -> Optional[Tuple[int, List[str]]]:
    """「## 目录」节:返回 (目录标题行号, [条目标题]);无目录节返回 None。

    条目兼容两种写法:「- [标题](#锚点)」链接式与「- 标题」纯文本式。
    """
    toc_line = next(
        (number for number, level, title in heading_records(text) if level == 2 and title == TOC_TITLE),
        None,
    )
    if toc_line is None:
        return None
    entries: List[str] = []
    for number, line in enumerate(text.splitlines(), 1):
        if number <= toc_line:
            continue
        stripped = line.strip()
        if stripped.startswith("#"):
            break
        if not stripped.startswith("-"):
            continue
        item = stripped[1:].strip()
        link = TOC_ENTRY_LINK_RE.match(item)
        entries.append((link.group(1) if link else item).strip())
    return toc_line, entries


def validate_toc_alignment(label: str, text: str, errors: List[str]) -> None:
    toc = toc_entries(text)
    if toc is None:
        errors.append(
            issue(
                f"{label}:toc",
                "元数据后存在「## 目录」节,目录行与实际 H2/H3 标题逐字一致",
                "未找到目录节",
                f"{label} 元数据之后",
            )
        )
        return
    _, entries = toc
    actual = [
        title
        for _, level, title in heading_records(text)
        if level in (2, 3) and title != TOC_TITLE
    ]
    entry_set, heading_set = set(entries), set(actual)
    missing = [title for title in actual if title not in entry_set]
    dangling = [title for title in entries if title not in heading_set]
    if missing:
        errors.append(
            issue(
                f"{label}:toc",
                "每个 H2/H3 标题都在目录中列出（目录即地图）",
                f"未列入目录 {missing[:6]}",
                f"{label} 目录节",
            )
        )
    if dangling:
        errors.append(
            issue(
                f"{label}:toc",
                "目录条目与实际标题一一对应（无失效条目）",
                f"目录中无对应标题 {dangling[:6]}",
                f"{label} 目录节",
            )
        )


def validate_group_counts(prd: str, errors: List[str]) -> None:
    lines = prd.splitlines()
    group_headers: List[Tuple[int, str]] = [
        (number, line.strip())
        for number, line in enumerate(lines, 1)
        if REQ_GROUP_RE.match(line.strip())
    ]
    for index, (number, header) in enumerate(group_headers):
        declared = REQ_GROUP_COUNT_RE.search(header)
        if declared is None:
            continue
        expected = int(declared.group(1))
        end = group_headers[index + 1][0] if index + 1 < len(group_headers) else len(lines) + 1
        actual = sum(
            1 for candidate in range(number, min(end, len(lines) + 1)) if REQ_BLOCK_RE.match(lines[candidate - 1].strip())
        )
        if actual != expected:
            errors.append(
                issue(
                    "PRD:requirements:group-count",
                    f"分组标题声明「{expected} 条」与该组实际需求块数一致",
                    f"实际 {actual} 条",
                    f"PRD:{number}",
                )
            )


def validate_cross_doc_duplication(prd: str, roadmap: str, warnings: List[str]) -> None:
    """跨文档 ≥30 字相同正文行为警告;假设表「逐字同源」要求行白名单。"""
    seen: Dict[str, List[str]] = {}
    for label, text in (("PRD", prd), ("Roadmap", roadmap)):
        whitelist = assumption_line_numbers(text)
        for number, line in prose_lines(text):
            if number in whitelist:
                continue
            normalized = _dup_normalize(line)
            if len(normalized) < CROSS_DOC_DUP_MIN:
                continue
            seen.setdefault(normalized, []).append(f"{label}:{number}")
    reported = 0
    for normalized, locations in seen.items():
        labels = {location.split(":", 1)[0] for location in locations}
        if len(labels) < 2 or reported >= DUP_MAX_REPORTS:
            continue
        warnings.append(
            issue(
                "cross-doc:presentation:duplication",
                "同一正文句行只在一份文档出现；跨文档复述收敛为单文档+引用（如「见 ROADMAP §n」）",
                f"「{normalized[:24]}…」同时出现在 {len(locations)} 处",
                "、".join(locations[:6]),
            )
        )
        reported += 1


def validate_window_consistency(prd: str, roadmap: str, warnings: List[str]) -> None:
    prd_windows = {int(value) for value in CONSECUTIVE_DAYS_RE.findall(prd)}
    roadmap_windows = {int(value) for value in CONSECUTIVE_DAYS_RE.findall(roadmap)}
    if not prd_windows or not roadmap_windows or prd_windows == roadmap_windows:
        return
    warnings.append(
        issue(
            "cross-doc:window-consistency",
            "「连续 N 天」类观察窗口口径在两文档一致（同一指标同一天数）",
            f"PRD={sorted(prd_windows)} 天，Roadmap={sorted(roadmap_windows)} 天",
            "两份文档的验收/退出条件",
        )
    )


def validate_ai_evaluation(prd: str, risks: Sequence[str], warnings: List[str]) -> None:
    if "AI" not in risks:
        return
    if find_table(prd, AI_EVALUATION_HEADERS) is None:
        warnings.append(
            issue(
                "PRD:risk:AI-evaluation",
                "AI 风险包含评估表（评估维度、评估载体、基线采集动作、裁决机制、解锁条件）",
                "未找到该表",
                "评估章节（先评价 → 再生成 → 后执行）",
            )
        )


def validate_presentation(documents: Sequence[Tuple[str, str]], errors: List[str], warnings: List[str]) -> None:
    for label, text in documents:
        validate_duplication(label, text, warnings)
        validate_header_archaeology(label, text, warnings)
        validate_version_archaeology(label, text, warnings)
        validate_table_convergence(label, text, warnings)
        validate_self_version(label, text, errors)
        validate_toc_alignment(label, text, errors)


def emit_result(
    fmt: str,
    prd_path: Path,
    roadmap_path: Path,
    errors: Sequence[str],
    warnings: Sequence[str],
) -> int:
    if fmt == "json":
        print(
            json.dumps(
                {
                    "status": "fail" if errors else "pass",
                    "prd": str(prd_path),
                    "roadmap": str(roadmap_path),
                    "errors": list(errors),
                    "warnings": list(warnings),
                    "proof_boundary": "structural_and_cross_document_consistency_only",
                },
                ensure_ascii=False,
                indent=2,
            )
        )
    else:
        for warning in warnings:
            print(f"警告:{warning}", file=sys.stderr)
        if errors:
            for error in errors:
                print(f"错误:{error}", file=sys.stderr)
            print(f"验证失败:{len(errors)} 个错误,{len(warnings)} 个警告", file=sys.stderr)
        else:
            print(f"验证通过:{prd_path} + {roadmap_path}({len(warnings)} 个警告)")
            print("证明边界(proof boundary):仅结构与跨文档一致性")
    return 1 if errors else 0


def main() -> int:
    # Windows 控制台默认 GBK:强制 UTF-8 输出,避免中文诊断乱码或 UnicodeEncodeError
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            try:
                stream.reconfigure(encoding="utf-8", errors="replace")
            except (OSError, ValueError):
                pass
    args = parse_args()
    if args.prd_html:
        errors, warnings, parsed = validate_html_prd(args.prd_html, args.decisions)
        if args.roadmap and parsed:
            roadmap_errors: List[str] = []
            roadmap = read_markdown(args.roadmap, roadmap_errors)
            errors.extend(roadmap_errors)
            if roadmap:
                validate_markdown(args.roadmap, roadmap, errors)
                rm_meta = metadata(roadmap)
                for field in ("产品主形态", "次级形态", "风险修饰项", "适用场景"):
                    if field in parsed.metadata and field in rm_meta and parsed.metadata[field] != rm_meta[field]:
                        errors.append(f"跨文档产品口径不一致：{field}")
                match = re.search(r"^#{2,4}[^\n]*需求落位映射[^\n]*\n([\s\S]*?)(?=^#{1,4} |\Z)", roadmap, re.MULTILINE)
                if match:
                    mapped = set(REQ_PLAIN_RE.findall(match.group(1)))
                    mapped_ids = {f"P{priority}-{number}" for priority, number in mapped}
                    if mapped_ids != set(parsed.requirements):
                        errors.append("Roadmap 需求落位映射与 HTML PRD 需求 ID 不一一对应")
                else:
                    errors.append("Roadmap 缺少需求落位映射章节")
        if args.format == "json":
            print(json.dumps({"status": "fail" if errors else "pass", "prd_html": str(args.prd_html),
                              "roadmap": str(args.roadmap) if args.roadmap else None,
                              "errors": errors, "warnings": warnings,
                              "proof_boundary": "html_structure_and_record_matching_only"}, ensure_ascii=False, indent=2))
        else:
            for warning in warnings:
                print(f"警告:{warning}", file=sys.stderr)
            for error in errors:
                print(f"错误:{error}", file=sys.stderr)
            print(f"HTML PRD {'验证失败' if errors else '验证通过'}：{len(errors)} 个错误，{len(warnings)} 个警告")
        return 1 if errors else 0
    errors: List[str] = []
    warnings: List[str] = []
    prd = read_markdown(args.prd, errors)
    roadmap = read_markdown(args.roadmap, errors)
    documents = [(args.prd, prd), (args.roadmap, roadmap)]

    for path, text in documents:
        if text:
            validate_markdown(path, text, errors)
    if prd and roadmap:
        primary, secondaries, risks, scenario = validate_metadata(prd, roadmap, errors, warnings)
        validate_outline(prd, roadmap, errors)
        tables = validate_universal_tables(prd, roadmap, scenario, errors)
        validate_shape_contracts(primary, secondaries, risks, prd, errors)
        requirement_ids = validate_alignment(prd, roadmap, tables, errors)
        validate_separation_of_duties(prd, roadmap, requirement_ids, errors)
        validate_assumptions(prd, tables.get("prd_assumptions"), errors, warnings)
        validate_numeric_targets((("PRD", prd), ("Roadmap", roadmap)), errors)
        validate_ai_evaluation(prd, risks, warnings)
        validate_presentation((("PRD", prd), ("Roadmap", roadmap)), errors, warnings)
        validate_group_counts(prd, errors)
        validate_cross_doc_duplication(prd, roadmap, warnings)
        validate_window_consistency(prd, roadmap, warnings)
        validate_open_markers(documents, args.allow_open_questions, errors, warnings)

    return emit_result(args.format, args.prd, args.roadmap, errors, warnings)


if __name__ == "__main__":
    raise SystemExit(main())
