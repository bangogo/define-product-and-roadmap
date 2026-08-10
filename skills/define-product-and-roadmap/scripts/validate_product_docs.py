#!/usr/bin/env python3
"""验证基于证据、感知产品形态的 PRD 与 Roadmap Markdown。"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Sequence, Set, Tuple


LINK_RE = re.compile(r"\[[^\]]+\]\(([^)]+)\)")
HEADING_RE = re.compile(r"^(#{1,3})\s+(.+?)\s*$", re.MULTILINE)
METADATA_RE = re.compile(r"^-\s*([^：:\n]+)[：:]\s*(.+?)\s*$")
MODULE_RE = re.compile(r"(?<![A-Z0-9])([A-Z])「([^」]+)」")
CAPABILITY_RE = re.compile(r"(?<![A-Z0-9])([A-Z][0-9]+)(?![A-Z0-9])")
BOXED_CAPABILITY_RE = re.compile(r"(?<![A-Z0-9])([A-Z][0-9]+)「([^」]+)」")
VERSION_CODE_RE = re.compile(r"(?<![A-Z0-9])R(\d+)(?![A-Z0-9])")
BOXED_VERSION_RE = re.compile(r"R(\d+)（第\s*(\d+)\s*个体验版本）「([^」]+)」")
REQUIREMENT_RE = re.compile(r"P([0-3])-(\d{2,})「([^」]+)」")
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

REQUIRED_METADATA = [
    "文档版本",
    "证据截止日期",
    "产品主形态",
    "次级形态",
    "风险修饰项",
    "当前证据阶段",
    "当前交付目的",
    "适用产品合同",
    "文档状态",
    "是否具备审批条件",
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

SHAPE_TABLES = {
    "C端交互产品": ["场景", "进入页面", "页面呈现", "用户动作", "状态变化", "可见结果", "失败与恢复"],
    "内容/产物生产": ["阶段", "输入", "处理责任", "中间/最终产物", "质量门", "失败与恢复", "证据"],
    "内部流程工具": ["角色", "触发", "处理步骤", "交接/审批", "可见结果", "异常恢复", "审计证据"],
    "API/平台": ["使用者", "接入入口", "首次成功任务", "接口/合同", "可见结果", "失败恢复", "采用证据"],
    "服务编排": ["服务场景", "用户触点", "承接方", "服务动作", "状态回流", "失败恢复", "责任边界"],
    "交易/市场": ["角色方", "发现/匹配", "信任保障", "交易动作", "履约结果", "争议恢复", "证据"],
}


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
    parser.add_argument("--prd", required=True, type=Path)
    parser.add_argument("--roadmap", required=True, type=Path)
    parser.add_argument(
        "--allow-open-questions",
        action="store_true",
        help="将假设登记表之外的 TODO/TBD/[待确认] 作为警告而非错误报告。",
    )
    parser.add_argument("--format", choices=("text", "json"), default="text")
    return parser.parse_args()


def read_markdown(path: Path, errors: List[str]) -> str:
    if not path.is_file():
        errors.append(issue(str(path), "UTF-8 Markdown 文件", "路径不存在", "文件路径"))
        return ""
    try:
        raw = path.read_bytes()
        text = raw.decode("utf-8")
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
    return [cell.strip() for cell in line.strip().strip("|").split("|")]


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


def validate_metadata(
    prd: str,
    roadmap: str,
    errors: List[str],
) -> Tuple[str, List[str], List[str]]:
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

    evidence_stage = prd_meta.get("当前证据阶段", "")
    if evidence_stage and evidence_stage not in EVIDENCE_STAGES:
        errors.append(issue("PRD:metadata", f"证据阶段属于 {sorted(EVIDENCE_STAGES)}", evidence_stage, "当前证据阶段"))
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

    return primary, secondaries, risks


def validate_outline(prd: str, roadmap: str, errors: List[str]) -> None:
    prd_h2 = headings(prd)
    roadmap_h2 = headings(roadmap)
    expected_prd = ["产品定位", "目标用户", "当前产品形态", "产品价值"]
    for index, keyword in enumerate(expected_prd):
        actual = prd_h2[index] if index < len(prd_h2) else "缺失"
        if keyword not in actual:
            errors.append(issue("PRD:outline", f"第 {index + 1} 个 H2 包含「{keyword}」", actual, "PRD 开篇结构"))
    expected_roadmap = ["核心用户任务", "当前基线"]
    for index, keyword in enumerate(expected_roadmap):
        actual = roadmap_h2[index] if index < len(roadmap_h2) else "缺失"
        if keyword not in actual:
            errors.append(issue("Roadmap:outline", f"第 {index + 1} 个 H2 包含「{keyword}」", actual, "Roadmap 开篇结构"))

    for keyword in ["参考", "产品能力", "产品需求", "当前版本", "成功"]:
        if not any(keyword in heading for heading in prd_h2):
            errors.append(issue("PRD:outline", f"包含「{keyword}」的 H2", str(prd_h2), "PRD 目录"))
    for keyword in ["产品能力层级", "体验版本", "当前版本", "依赖"]:
        if not any(keyword in heading for heading in roadmap_h2):
            errors.append(issue("Roadmap:outline", f"包含「{keyword}」的 H2", str(roadmap_h2), "Roadmap 目录"))

    ref_index = next((i for i, h in enumerate(prd_h2) if "参考" in h), None)
    for target in ["产品能力", "产品需求"]:
        target_index = next((i for i, h in enumerate(prd_h2) if target in h), None)
        if ref_index is not None and target_index is not None and ref_index > target_index:
            errors.append(issue("PRD:outline", f"参考与复用早于「{target}」", "参考章节位于其后", "PRD 章节顺序"))

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


def validate_universal_tables(prd: str, roadmap: str, errors: List[str]) -> Dict[str, Optional[Table]]:
    tables: Dict[str, Optional[Table]] = {}
    tables["current"] = expect_table(prd, ["观察对象", "当前效果", "证据状态", "证据来源", "当前缺口"], "PRD:current-effect", "当前产品形态章节", errors)
    validate_status_column(tables["current"], "证据状态", TRUTH_STATUSES, "PRD:current-effect", errors)

    tables["reuse"] = expect_table(
        prd,
        ["来源", "版本/日期", "许可状态", "负责什么", "已证实能力", "产品映射", "复用决策", "项目补充", "用户价值", "证据边界"],
        "PRD:reference-reuse",
        "参考、复用与项目责任章节",
        errors,
    )
    tables["modules"] = expect_table(
        prd,
        ["产品模块", "责任", "输入", "用户可见输出", "负责人", "主要状态", "失败与恢复", "当前优先级及依据"],
        "PRD:modules",
        "产品能力章节",
        errors,
    )
    tables["requirements"] = expect_table(
        prd,
        ["编号", "优先级", "模块", "产品要求", "用户可见结果", "业务规则", "技术验收边界", "证据状态"],
        "PRD:requirements",
        "产品需求章节",
        errors,
    )
    tables["truth"] = expect_table(prd, ["层面", "当前实现", "真实性", "用户可见标识", "后续替换"], "PRD:truth-boundary", "当前版本章节", errors)
    validate_status_column(tables["truth"], "真实性", TRUTH_STATUSES, "PRD:truth-boundary", errors)
    tables["success"] = expect_table(prd, ["成功信号", "对应用户价值", "当前基线", "本版判定", "证据方法", "结论状态"], "PRD:success", "产品价值或成功章节", errors)
    tables["prd_assumptions"] = expect_table(prd, ["类型", "假设或决策", "状态", "依据", "对产品影响", "确认人/下一步"], "PRD:assumptions", "成功、风险与假设章节", errors)

    tables["levels"] = expect_table(roadmap, ["产品模块", "L0", "L1", "L2"], "Roadmap:capability-levels", "产品能力层级章节", errors)
    tables["versions"] = expect_table(
        roadmap,
        ["体验版本", "用户任务", "核心能力", "用户可见结果", "本版主要增量", "主要验证问题", "进入条件", "退出条件", "状态"],
        "Roadmap:versions",
        "体验版本章节",
        errors,
    )
    validate_status_column(tables["versions"], "状态", VERSION_STATUSES, "Roadmap:versions", errors)
    tables["deliverables"] = expect_table(roadmap, ["交付项", "用户可见结果", "当前实现", "真实性", "验收证据", "不包含"], "Roadmap:truth-boundary", "当前版本章节", errors)
    validate_status_column(tables["deliverables"], "真实性", TRUTH_STATUSES, "Roadmap:truth-boundary", errors)
    tables["roadmap_assumptions"] = expect_table(roadmap, ["类型", "假设或决策", "状态", "依据", "对产品影响", "确认人/下一步"], "Roadmap:assumptions", "依赖、风险与假设章节", errors)
    tables["gates"] = expect_table(roadmap, ["闸门", "所需证据", "决策人", "通过后授权", "未通过处理"], "Roadmap:gates", "版本闸门章节", errors)
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
            expect_table(prd, headers, f"PRD:shape:{shape}", f"{shape} 产品合同章节", errors)

    if risks:
        risk_table = expect_table(
            prd,
            ["风险修饰项", "触发场景", "潜在损害", "预防控制", "用户控制", "失败/未知状态", "审计证据", "发布/审批门"],
            "PRD:risk",
            "风险合同章节",
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
            "AI 合同章节",
            errors,
        )


def canonical_modules_from_table(table: Optional[Table]) -> Tuple[Dict[str, str], List[str]]:
    result: Dict[str, str] = {}
    conflicts: List[str] = []
    if table is None:
        return result, conflicts
    module_index = table.headers.index("产品模块")
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


def validate_requirements(table: Optional[Table], modules: Dict[str, str], errors: List[str]) -> None:
    if table is None:
        return
    id_index = table.headers.index("编号")
    module_index = table.headers.index("模块")
    seen: Set[str] = set()
    for offset, row in enumerate(table.rows, 2):
        if id_index >= len(row) or module_index >= len(row):
            continue
        requirement_id = row[id_index]
        if not REQUIREMENT_RE.fullmatch(requirement_id):
            errors.append(issue("PRD:requirement-id", "P0-01「要求名称」", requirement_id, f"PRD:{table.line + offset}"))
        elif requirement_id in seen:
            errors.append(issue("PRD:requirement-id", "唯一需求编号", requirement_id, f"PRD:{table.line + offset}"))
        seen.add(requirement_id)
        mapped = MODULE_RE.findall(row[module_index])
        if not mapped:
            errors.append(issue("PRD:requirements", "模块列使用 A「模块名称」", row[module_index], f"PRD:{table.line + offset}"))
        for code, name in mapped:
            if modules.get(code) != name:
                errors.append(issue("PRD:requirements", "需求映射到已定义模块", f"{code}「{name}」", f"PRD:{table.line + offset}"))


def validate_alignment(
    prd: str,
    roadmap: str,
    tables: Dict[str, Optional[Table]],
    errors: List[str],
) -> None:
    prd_modules, prd_conflicts = canonical_modules_from_table(tables.get("modules"))
    roadmap_modules, roadmap_conflicts = canonical_modules_from_table(tables.get("levels"))
    if prd_conflicts:
        errors.append(issue("PRD:modules", "每个模块代码只有一个名称", str(prd_conflicts), "产品能力章节"))
    if roadmap_conflicts:
        errors.append(issue("Roadmap:modules", "每个模块代码只有一个名称", str(roadmap_conflicts), "能力层级章节"))
    if not prd_modules or not roadmap_modules:
        errors.append(issue("cross-doc:modules", "PRD/Roadmap 均定义 A「名称」类模块", f"PRD={prd_modules}，Roadmap={roadmap_modules}", "产品能力章节"))
    elif prd_modules != roadmap_modules:
        errors.append(issue("cross-doc:modules", "模块代码与名称一致", f"PRD={prd_modules}，Roadmap={roadmap_modules}", "两份文档产品能力章节"))

    validate_requirements(tables.get("requirements"), prd_modules, errors)

    capability_cells: List[Tuple[str, str]] = []
    levels_table = tables.get("levels")
    if levels_table:
        for offset, row in enumerate(levels_table.rows, 2):
            for header in ("L0", "L1", "L2"):
                index = levels_table.headers.index(header)
                if index < len(row):
                    capability_cells.append((row[index], f"Roadmap:{levels_table.line + offset}"))
    version_table = tables.get("versions")
    if version_table:
        capability_index = version_table.headers.index("核心能力")
        for offset, row in enumerate(version_table.rows, 2):
            if capability_index < len(row):
                capability_cells.append((row[capability_index], f"Roadmap:{version_table.line + offset}"))

    roadmap_capabilities: Dict[str, str] = {}
    for cell, location in capability_cells:
        for code, name in BOXED_CAPABILITY_RE.findall(cell):
            if code in roadmap_capabilities and roadmap_capabilities[code] != name:
                errors.append(issue("Roadmap:capability-code", "每个能力代码名称唯一", f"{code}: {roadmap_capabilities[code]} / {name}", location))
            roadmap_capabilities[code] = name
            if code[0] not in roadmap_modules:
                errors.append(issue("Roadmap:capability-code", "能力前缀映射到已定义模块", code, location))
        for match in CAPABILITY_RE.finditer(cell):
            if not cell.startswith("「", match.end()):
                errors.append(issue("Roadmap:capability-code", f"{match.group(1)}「能力名称」", cell, location))
    if not roadmap_capabilities:
        errors.append(issue("Roadmap:capability-code", "至少一个 A0「能力」", "未找到", "能力层级章节"))

    defined_versions: Set[int] = set()
    planned_versions: List[int] = []
    if version_table:
        version_index = version_table.headers.index("体验版本")
        for offset, row in enumerate(version_table.rows, 2):
            if version_index >= len(row):
                continue
            cell = row[version_index]
            if cell == "R0「当前基线」":
                defined_versions.add(0)
                continue
            match = BOXED_VERSION_RE.fullmatch(cell)
            if not match:
                errors.append(issue("Roadmap:version-code", "R1（第 1 个体验版本）「名称」", cell, f"Roadmap:{version_table.line + offset}"))
                continue
            number, ordinal = int(match.group(1)), int(match.group(2))
            if number == 0 or number != ordinal:
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
        errors.append(issue("Roadmap:version-code", "所有版本代码在路线表中具名定义", str(missing), "体验版本路线图"))

    prd_assumptions = tables.get("prd_assumptions")
    roadmap_assumptions = tables.get("roadmap_assumptions")
    if prd_assumptions and roadmap_assumptions:
        if prd_assumptions.rows != roadmap_assumptions.rows:
            errors.append(issue("cross-doc:assumptions", "两份文档的物质性假设行完全一致", f"PRD={prd_assumptions.rows}；Roadmap={roadmap_assumptions.rows}", "两份假设表"))


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
    args = parse_args()
    errors: List[str] = []
    warnings: List[str] = []
    prd = read_markdown(args.prd, errors)
    roadmap = read_markdown(args.roadmap, errors)
    documents = [(args.prd, prd), (args.roadmap, roadmap)]

    for path, text in documents:
        if text:
            validate_markdown(path, text, errors)
    if prd and roadmap:
        primary, secondaries, risks = validate_metadata(prd, roadmap, errors)
        validate_outline(prd, roadmap, errors)
        tables = validate_universal_tables(prd, roadmap, errors)
        validate_shape_contracts(primary, secondaries, risks, prd, errors)
        validate_alignment(prd, roadmap, tables, errors)
        validate_assumptions(prd, tables.get("prd_assumptions"), errors, warnings)
        validate_numeric_targets((("PRD", prd), ("Roadmap", roadmap)), errors)
        validate_open_markers(documents, args.allow_open_questions, errors, warnings)

    return emit_result(args.format, args.prd, args.roadmap, errors, warnings)


if __name__ == "__main__":
    raise SystemExit(main())
