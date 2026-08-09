#!/usr/bin/env python3
"""Validate product-shape-aware PRD and Roadmap Markdown contracts."""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from pathlib import Path


LINK_RE = re.compile(r"\[[^\]]+\]\(([^)]+)\)")
HEADING_RE = re.compile(r"^(#{2,3})\s+(.+?)\s*$", re.MULTILINE)
METADATA_RE = re.compile(r"^-\s*([^：:\n]+)[：:]\s*(.+?)\s*$", re.MULTILINE)
MODULE_RE = re.compile(r"(?<![A-Z0-9])([A-Z])「([^」]+)」")
CAPABILITY_RE = re.compile(r"(?<![A-Z0-9])([A-KM-QS-Z][0-9]+)(?![A-Z0-9])")
BOXED_CAPABILITY_RE = re.compile(r"(?<![A-Z0-9])([A-KM-QS-Z][0-9]+)「([^」]+)」")
VERSION_CODE_RE = re.compile(r"(?<![A-Z0-9])R(\d+)(?![A-Z0-9])")
BOXED_VERSION_RE = re.compile(r"R(\d+)（第\s*(\d+)\s*个体验版本）「([^」]+)」")
OPEN_MARKER_RE = re.compile(r"\[待确认\]|\b(?:TODO|TBD)\b", re.IGNORECASE)
PERCENT_TARGET_RE = re.compile(r"(?<![A-Za-z0-9])\d+(?:\.\d+)?%")
TARGET_EVIDENCE_RE = re.compile(
    r"依据|来源|基线|已批准|已确认|提案|候选|待批准|proposal|baseline|source",
    re.IGNORECASE,
)
PROCESS_HEADING_RE = re.compile(
    r"创建者诉求|决策摘要|内部简报|为什么选择\s*Pattern|自检|分析过程",
    re.IGNORECASE,
)

REQUIRED_METADATA = [
    "产品主形态",
    "次级形态",
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

EVIDENCE_STATUSES = {
    "真实",
    "测试接入",
    "模拟",
    "人工承接",
    "仅有文档",
    "已观察",
    "尚未验证",
    "历史证据",
    "已确认",
}

ASSUMPTION_TYPES = {"必须为真", "重要假设", "可逆默认", "高风险外部事实"}
ASSUMPTION_STATUSES = {"已确认", "建议假设，待确认", "待调研", "已否决"}


@dataclass
class Table:
    line: int
    headers: list[str]
    rows: list[list[str]]


def issue(area: str, expected: str, actual: str, fix: str) -> str:
    return f"[{area}] 期望结构：{expected}；实际发现：{actual}；修复位置：{fix}"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--prd", required=True, type=Path)
    parser.add_argument("--roadmap", required=True, type=Path)
    parser.add_argument("--allow-open-questions", action="store_true")
    return parser.parse_args()


def read_markdown(path: Path, errors: list[str]) -> str:
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
    if not any(line.startswith("# ") for line in text.splitlines()):
        errors.append(issue(str(path), "一个 H1 标题", "未找到 H1", "文件开头"))
    return text


def validate_markdown(path: Path, text: str, errors: list[str]) -> None:
    lines = text.splitlines()
    index = 0
    while index < len(lines):
        if not lines[index].startswith("|"):
            index += 1
            continue
        start = index
        block: list[str] = []
        while index < len(lines) and lines[index].startswith("|"):
            block.append(lines[index])
            index += 1
        counts = [line.count("|") for line in block]
        if len(set(counts)) != 1:
            errors.append(issue(str(path), "表格列数一致", f"第 {start + 1} 行附近列数不一致", f"{path}:{start + 1}"))
        if len(block) < 2 or not re.fullmatch(r"\|(?:\s*:?-+:?\s*\|)+\s*", block[1]):
            errors.append(issue(str(path), "Markdown 表格分隔行", "分隔行缺失", f"{path}:{start + 1}"))

    for raw_target in LINK_RE.findall(text):
        target = raw_target.strip("<>")
        if target.startswith(("http://", "https://", "mailto:", "#")):
            continue
        file_part = target.split("#", 1)[0]
        if file_part and not (path.parent / file_part).resolve().exists():
            errors.append(issue(str(path), "有效相对链接", raw_target, f"链接所在文件 {path}"))


def headings(text: str, level: int = 2) -> list[str]:
    prefix = "#" * level
    return [title.strip() for marks, title in HEADING_RE.findall(text) if marks == prefix]


def metadata(text: str) -> dict[str, str]:
    return {key.strip(): value.strip() for key, value in METADATA_RE.findall(text)}


def parse_tables(text: str) -> list[Table]:
    lines = text.splitlines()
    result: list[Table] = []
    index = 0
    while index < len(lines) - 1:
        if not lines[index].startswith("|") or not re.fullmatch(
            r"\|(?:\s*:?-+:?\s*\|)+\s*", lines[index + 1]
        ):
            index += 1
            continue
        start = index
        headers = [cell.strip() for cell in lines[index].strip().strip("|").split("|")]
        index += 2
        rows: list[list[str]] = []
        while index < len(lines) and lines[index].startswith("|"):
            rows.append([cell.strip() for cell in lines[index].strip().strip("|").split("|")])
            index += 1
        result.append(Table(start + 1, headers, rows))
    return result


def find_table(text: str, expected: list[str]) -> Table | None:
    for table in parse_tables(text):
        if all(header in table.headers for header in expected):
            return table
    return None


def expect_table(
    text: str, expected: list[str], label: str, location: str, errors: list[str]
) -> Table | None:
    table = find_table(text, expected)
    if table is None:
        found = [table.headers for table in parse_tables(text)]
        errors.append(issue(label, f"表头包含 {expected}", f"现有表头 {found}", location))
    return table


def validate_metadata(prd: str, roadmap: str, errors: list[str]) -> tuple[str, list[str]]:
    prd_meta = metadata(prd)
    roadmap_meta = metadata(roadmap)
    for label, data in [("PRD", prd_meta), ("Roadmap", roadmap_meta)]:
        for key in REQUIRED_METADATA:
            if key not in data:
                errors.append(issue(f"{label}:metadata", f"字段「{key}」", "缺失", "文档 H1 后的元数据"))

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

    primary = prd_meta.get("产品主形态", "")
    if primary not in PRIMARY_SHAPES:
        errors.append(
            issue(
                "PRD:product-shape",
                f"一个明确主形态 {sorted(PRIMARY_SHAPES)}",
                primary or "缺失",
                "产品主形态元数据",
            )
        )
    if "混合" in primary:
        errors.append(issue("PRD:product-shape", "一个主要价值载体", primary, "产品主形态元数据"))

    secondary_raw = prd_meta.get("次级形态", "无")
    secondaries = [] if secondary_raw in {"无", "不适用", "—"} else [
        item.strip() for item in re.split(r"[、,，]", secondary_raw) if item.strip()
    ]
    if len(secondaries) > 2:
        errors.append(issue("PRD:product-shape", "最多两个次级形态", secondary_raw, "次级形态元数据"))
    return primary, secondaries


def validate_outline(prd: str, roadmap: str, errors: list[str]) -> None:
    prd_h2 = headings(prd)
    roadmap_h2 = headings(roadmap)
    expected_prd = ["产品定位", "目标用户", "当前", "产品价值"]
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
    for keyword in ["能力层级", "体验版本", "当前版本", "依赖"]:
        if not any(keyword in heading for heading in roadmap_h2):
            errors.append(issue("Roadmap:outline", f"包含「{keyword}」的 H2", str(roadmap_h2), "Roadmap 目录"))

    ref_index = next((i for i, h in enumerate(prd_h2) if "参考" in h), None)
    for target in ["产品能力", "产品需求"]:
        target_index = next((i for i, h in enumerate(prd_h2) if target in h), None)
        if ref_index is not None and target_index is not None and ref_index > target_index:
            errors.append(issue("PRD:outline", f"参考与复用早于「{target}」", "参考章节位于其后", "PRD 章节顺序"))

    for label, text in [("PRD", prd), ("Roadmap", roadmap)]:
        for _, title in HEADING_RE.findall(text):
            if PROCESS_HEADING_RE.search(title):
                errors.append(issue(f"{label}:outline", "产品面向的正式章节", title, "将内部分析移出正式文档"))


def validate_universal_tables(prd: str, roadmap: str, errors: list[str]) -> None:
    current = expect_table(
        prd,
        ["观察对象", "当前效果", "证据状态", "证据来源", "当前缺口"],
        "PRD:current-effect",
        "当前产品形态与效果章节",
        errors,
    )
    if current:
        status_index = current.headers.index("证据状态")
        for row in current.rows:
            if status_index >= len(row) or row[status_index] not in EVIDENCE_STATUSES:
                actual = row[status_index] if status_index < len(row) else "缺失"
                errors.append(issue("PRD:current-effect", f"证据状态属于 {sorted(EVIDENCE_STATUSES)}", actual, f"PRD:{current.line}"))

    expect_table(
        prd,
        ["来源", "负责什么", "已证实能力", "产品映射", "复用决策", "项目补充", "用户价值", "证据边界"],
        "PRD:reference-reuse",
        "参考产品与复用章节",
        errors,
    )
    expect_table(
        prd,
        ["编号", "优先级", "模块", "产品要求", "用户可见结果", "业务规则", "技术验收边界", "证据状态"],
        "PRD:requirements",
        "产品需求章节",
        errors,
    )
    expect_table(
        prd,
        ["层面", "当前实现", "真实性", "用户可见标识", "后续替换"],
        "PRD:truth-boundary",
        "当前版本章节",
        errors,
    )
    expect_table(
        prd,
        ["类型", "假设或决策", "状态", "依据", "对产品影响", "确认人/下一步"],
        "PRD:assumptions",
        "成功、风险与假设章节",
        errors,
    )
    expect_table(
        roadmap,
        ["产品模块", "L0", "L1", "L2"],
        "Roadmap:capability-levels",
        "能力层级章节",
        errors,
    )
    expect_table(
        roadmap,
        ["体验版本", "用户任务", "核心能力", "用户可见结果", "本版主要增量", "主要验证问题", "进入条件", "退出条件", "状态"],
        "Roadmap:versions",
        "体验版本章节",
        errors,
    )


SHAPE_TABLES = {
    "C端交互产品": ["场景", "进入页面", "页面呈现", "用户动作", "状态变化", "可见结果", "失败与恢复"],
    "内容/产物生产": ["阶段", "输入", "处理责任", "中间/最终产物", "质量门", "失败与恢复", "证据"],
    "内部流程工具": ["角色", "触发", "处理步骤", "交接/审批", "可见结果", "异常恢复", "审计证据"],
    "API/平台": ["使用者", "接入入口", "首次成功任务", "接口/合同", "可见结果", "失败恢复", "采用证据"],
    "服务编排": ["服务场景", "用户触点", "承接方", "服务动作", "状态回流", "失败恢复", "责任边界"],
    "交易/市场": ["角色方", "发现/匹配", "信任保障", "交易动作", "履约结果", "争议恢复", "证据"],
}


def validate_shape_contracts(primary: str, secondaries: list[str], prd: str, errors: list[str]) -> None:
    selected = [primary] + secondaries
    for shape, headers in SHAPE_TABLES.items():
        if shape in selected:
            expect_table(prd, headers, f"PRD:shape:{shape}", f"{shape} 产品合同章节", errors)
    if any("AI" in item or "助手" in item or "Agent" in item for item in selected):
        expect_table(
            prd,
            ["场景", "触发入口", "携带上下文", "助手响应", "关键追问", "行动边界", "可见结果", "回退"],
            "PRD:risk:AI",
            "AI 助手或 Agent 合同章节",
            errors,
        )


def canonical_modules(text: str) -> tuple[dict[str, str], list[str]]:
    result: dict[str, str] = {}
    conflicts: list[str] = []
    for code, name in MODULE_RE.findall(text):
        if code in result and result[code] != name:
            conflicts.append(f"{code}: {result[code]} / {name}")
        result[code] = name
    return result, conflicts


def validate_alignment(prd: str, roadmap: str, errors: list[str]) -> None:
    prd_modules, prd_conflicts = canonical_modules(prd)
    roadmap_modules, roadmap_conflicts = canonical_modules(roadmap)
    if prd_conflicts:
        errors.append(issue("PRD:modules", "每个模块代码只有一个名称", str(prd_conflicts), "产品能力章节"))
    if roadmap_conflicts:
        errors.append(issue("Roadmap:modules", "每个模块代码只有一个名称", str(roadmap_conflicts), "能力层级章节"))
    if not prd_modules or not roadmap_modules:
        errors.append(issue("cross-doc:modules", "PRD/Roadmap 均定义 A「名称」类模块", f"PRD={prd_modules}，Roadmap={roadmap_modules}", "产品能力章节"))
    elif prd_modules != roadmap_modules:
        errors.append(issue("cross-doc:modules", "模块代码与名称一致", f"PRD={prd_modules}，Roadmap={roadmap_modules}", "两份文档产品能力章节"))

    roadmap_capabilities = {code: name for code, name in BOXED_CAPABILITY_RE.findall(roadmap)}
    for line_number, line in enumerate(roadmap.splitlines(), 1):
        for match in CAPABILITY_RE.finditer(line):
            if not line.startswith("「", match.end()):
                errors.append(issue("Roadmap:capability-code", f"{match.group(1)}「能力名称」", line.strip(), f"Roadmap:{line_number}"))

    version_table = find_table(
        roadmap,
        ["体验版本", "用户任务", "核心能力", "用户可见结果", "本版主要增量", "主要验证问题", "进入条件", "退出条件", "状态"],
    )
    defined_versions: set[int] = set()
    if version_table:
        version_index = version_table.headers.index("体验版本")
        for row in version_table.rows:
            if version_index >= len(row):
                continue
            cell = row[version_index]
            if cell.startswith("R0「"):
                defined_versions.add(0)
                continue
            match = BOXED_VERSION_RE.fullmatch(cell)
            if not match:
                errors.append(issue("Roadmap:version-code", "R1（第 1 个体验版本）「名称」", cell, f"Roadmap:{version_table.line}"))
                continue
            number, ordinal = int(match.group(1)), int(match.group(2))
            defined_versions.add(number)
            if number != ordinal:
                errors.append(issue("Roadmap:version-code", "版本号与中文序号一致", cell, f"Roadmap:{version_table.line}"))
    used_versions = {int(number) for number in VERSION_CODE_RE.findall(roadmap)}
    missing = sorted(used_versions - defined_versions)
    if missing:
        errors.append(issue("Roadmap:version-code", "所有版本代码在路线表中具名定义", str(missing), "体验版本路线图"))

    if not roadmap_capabilities:
        errors.append(issue("Roadmap:capability-code", "至少一个 A0「能力」", "未找到", "能力层级章节"))


def validate_assumptions(prd: str, errors: list[str], warnings: list[str]) -> None:
    table = find_table(prd, ["类型", "假设或决策", "状态", "依据", "对产品影响", "确认人/下一步"])
    if not table:
        return
    type_index = table.headers.index("类型")
    status_index = table.headers.index("状态")
    blocking: list[str] = []
    for row in table.rows:
        if type_index >= len(row) or status_index >= len(row):
            errors.append(issue("PRD:assumptions", "完整假设行", str(row), f"PRD:{table.line}"))
            continue
        kind, status = row[type_index], row[status_index]
        if kind not in ASSUMPTION_TYPES:
            errors.append(issue("PRD:assumptions", f"类型属于 {sorted(ASSUMPTION_TYPES)}", kind, f"PRD:{table.line}"))
        if status not in ASSUMPTION_STATUSES:
            errors.append(issue("PRD:assumptions", f"状态属于 {sorted(ASSUMPTION_STATUSES)}", status, f"PRD:{table.line}"))
        if kind == "必须为真" and status != "已确认":
            blocking.append(row[1] if len(row) > 1 else "未命名假设")

    readiness = metadata(prd).get("是否具备审批条件", "")
    if blocking and readiness.startswith("是"):
        errors.append(issue("PRD:approval-readiness", "未确认的必须为真假设使审批条件为否", f"阻断项={blocking}，审批条件={readiness}", "元数据和假设表"))
    elif blocking:
        warnings.append(f"PRD remains not approval-ready because must-be-true assumptions are unresolved: {blocking}")


def validate_numeric_targets(prd: str, errors: list[str]) -> None:
    for number, line in enumerate(prd.splitlines(), 1):
        if PERCENT_TARGET_RE.search(line) and not TARGET_EVIDENCE_RE.search(line):
            errors.append(issue("PRD:numeric-target", "数字目标带来源、提案状态或基线计划", line.strip(), f"PRD:{number}"))


def validate_open_markers(
    documents: list[tuple[Path, str]], allow: bool, errors: list[str], warnings: list[str]
) -> None:
    for path, text in documents:
        for number, line in enumerate(text.splitlines(), 1):
            if OPEN_MARKER_RE.search(line):
                message = issue(str(path), "开放项进入假设登记表", line.strip(), f"{path}:{number}")
                (warnings if allow else errors).append(message)


def main() -> int:
    args = parse_args()
    errors: list[str] = []
    warnings: list[str] = []
    prd = read_markdown(args.prd, errors)
    roadmap = read_markdown(args.roadmap, errors)
    documents = [(args.prd, prd), (args.roadmap, roadmap)]

    for path, text in documents:
        if text:
            validate_markdown(path, text, errors)
    if prd and roadmap:
        primary, secondaries = validate_metadata(prd, roadmap, errors)
        validate_outline(prd, roadmap, errors)
        validate_universal_tables(prd, roadmap, errors)
        validate_shape_contracts(primary, secondaries, prd, errors)
        validate_alignment(prd, roadmap, errors)
        validate_assumptions(prd, errors, warnings)
        validate_numeric_targets(prd, errors)
        validate_open_markers(documents, args.allow_open_questions, errors, warnings)

    for warning in warnings:
        print(f"WARNING: {warning}", file=sys.stderr)
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        print(f"validation failed: {len(errors)} error(s), {len(warnings)} warning(s)", file=sys.stderr)
        return 1
    print(f"validation passed: {args.prd} + {args.roadmap} ({len(warnings)} warning(s))")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
