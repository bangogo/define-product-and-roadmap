#!/usr/bin/env python3
"""Regression tests for the product PRD/Roadmap contract validator."""

from __future__ import annotations

import json
import subprocess
import tempfile
import unittest
from pathlib import Path


VALIDATOR = Path(__file__).with_name("validate_product_docs.py")

SHAPE_TABLES = {
    "C端交互产品": """| 场景 | 进入页面 | 页面呈现 | 用户动作 | 状态变化 | 可见结果 | 失败与恢复 |
|---|---|---|---|---|---|---|
| 主任务 | 首页 | 状态与行动 | 点击行动 | 处理中 | 看见结果 | 返回首页 |""",
    "内容/产物生产": """| 阶段 | 输入 | 处理责任 | 中间/最终产物 | 质量门 | 失败与恢复 | 证据 |
|---|---|---|---|---|---|---|
| 生产 | 素材 | 生成与审查 | 可用产物 | 人工审查 | checkpoint 恢复 | 来源记录 |""",
    "内部流程工具": """| 角色 | 触发 | 处理步骤 | 交接/审批 | 可见结果 | 异常恢复 | 审计证据 |
|---|---|---|---|---|---|---|
| 操作员 | 新任务 | 处理 | 主管批准 | 完成 | 退回队列 | 操作日志 |""",
    "API/平台": """| 使用者 | 接入入口 | 首次成功任务 | 接口/合同 | 可见结果 | 失败恢复 | 采用证据 |
|---|---|---|---|---|---|---|
| 开发者 | 快速开始 | 首次调用 | API 合同 | 成功响应 | 错误指南 | 调用记录 |""",
    "服务编排": """| 服务场景 | 用户触点 | 承接方 | 服务动作 | 状态回流 | 失败恢复 | 责任边界 |
|---|---|---|---|---|---|---|
| 办理 | 首页 | 服务方 | 提交 | 结果返回 | 人工渠道 | 产品解释、服务方处理 |""",
    "交易/市场": """| 角色方 | 发现/匹配 | 信任保障 | 交易动作 | 履约结果 | 争议恢复 | 证据 |
|---|---|---|---|---|---|---|
| 买卖双方 | 匹配 | 身份校验 | 下单 | 交付 | 申诉 | 交易记录 |""",
}

AI_TABLE = """| 场景 | 触发入口 | 携带上下文 | 助手响应 | 关键追问 | 行动边界 | 可见结果 | 回退 |
|---|---|---|---|---|---|---|---|
| 主任务 | 首页 | 用户状态 | 解释下一步 | 一个问题 | 用户确认后行动 | 看见结果 | 人工入口 |"""

ASSUMPTIONS = """| 类型 | 假设或决策 | 状态 | 依据 | 对产品影响 | 确认人/下一步 |
|---|---|---|---|---|---|
| 必须为真 | 用户需要该结果 | 已确认 | 用户研究 | 决定方向 | 产品负责人 |
| 可逆默认 | 首版使用固定数据 | 已确认 | 当前阶段 | 只影响验证方式 | R1 后复核 |"""


def normalized_risks(primary: str, risks: str) -> str:
    values = [] if risks == "无" else risks.split("、")
    if primary == "交易/市场" and "交易" not in values:
        values.append("交易")
    return "无" if not values else "、".join(values)


def contracts(primary: str, secondary: str, risks: str) -> str:
    parts = ["通用合同", f"{primary}合同"]
    if secondary != "无":
        parts.extend(f"{item}合同" for item in secondary.split("、"))
    if risks != "无":
        parts.extend(f"{item}风险合同" for item in risks.split("、"))
    return "、".join(parts)


def risk_tables(risks: str) -> str:
    if risks == "无":
        return ""
    rows = "\n".join(
        f"| {risk} | 主任务 | 错误结果 | 人工复核 | 用户确认 | 标记未知 | 审计记录 | 负责人批准 |"
        for risk in risks.split("、")
    )
    generic = f"""| 风险修饰项 | 触发场景 | 潜在损害 | 预防控制 | 用户控制 | 失败/未知状态 | 审计证据 | 发布/审批门 |
|---|---|---|---|---|---|---|---|
{rows}"""
    ai = f"\n\n{AI_TABLE}" if "AI" in risks.split("、") else ""
    return f"\n\n{generic}{ai}"


def make_prd(
    primary: str,
    secondary: str = "无",
    risks: str = "无",
    readiness: str = "是（等待批准）",
) -> str:
    risks = normalized_risks(primary, risks)
    selected = [primary] + ([] if secondary == "无" else secondary.split("、"))
    shape_tables = "\n\n".join(SHAPE_TABLES[item] for item in selected if item in SHAPE_TABLES)
    return f"""# Example Product Requirements

- 文档版本：2.0.0
- 证据截止日期：2026-08-09
- 产品主形态：{primary}
- 次级形态：{secondary}
- 风险修饰项：{risks}
- 当前证据阶段：交互原型
- 当前交付目的：用户价值验证
- 适用产品合同：{contracts(primary, secondary, risks)}
- 文档状态：Proposed
- 是否具备审批条件：{readiness}

## 1. 产品定位与目标

帮助用户完成一项有价值的任务；本版不包含真实外部写入。

## 2. 目标用户与核心问题

目标用户需要一个清楚的结果，当前只能完成一半任务。

## 3. 当前产品形态、效果与核心缺口

| 观察对象 | 当前效果 | 证据状态 | 证据来源 | 当前缺口 |
|---|---|---|---|---|
| 当前原型 | 能完成一半任务 | 已观察 | 原型记录 | 结果未闭合 |

## 4. 产品价值与价值循环

用户获得结果并形成继续使用理由。

| 成功信号 | 对应用户价值 | 当前基线 | 本版判定 | 证据方法 | 结论状态 |
|---|---|---|---|---|---|
| 完成主任务 | 获得可用结果 | 未知，需建立基线 | 完成并理解结果 | 任务观察 | 待验证 |

## 5. 参考、复用与项目责任

| 来源 | 版本/日期 | 许可状态 | 负责什么 | 已证实能力 | 产品映射 | 复用决策 | 项目补充 | 用户价值 | 证据边界 |
|---|---|---|---|---|---|---|---|---|---|
| Reference | 2026-08-01 | 方法参考，无代码复用 | 参考方法 | 已有样例 | A「核心能力」 | 「方法借鉴」 | 项目规则 | 更快完成 | 不证明运行效果 |

## 6. 主要体验或生产合同

{shape_tables}{risk_tables(risks)}

## 7. 产品能力与优先级

| 产品模块 | 责任 | 输入 | 用户可见输出 | 负责人 | 主要状态 | 失败与恢复 | 当前优先级及依据 |
|---|---|---|---|---|---|---|---|
| A「核心能力」 | 完成主任务 | 用户输入 | 用户结果 | 产品负责人 | 输入、处理中、完成 | 保存输入后重试 | P0，当前瓶颈 |
| B「可信保障」 | 保护真实性 | 状态 | 边界标识 | 技术负责人 | 已知、未知 | 转人工 | P1，支持可信使用 |

## 8. 产品需求与验收

| 编号 | 优先级 | 模块 | 产品要求 | 用户可见结果 | 业务规则 | 技术验收边界 | 证据状态 |
|---|---|---|---|---|---|---|---|
| P0-01「主任务」 | P0 | A「核心能力」 | 完成主任务 | 看见结果 | 保留返回 | 状态可复现 | 待版本验证 |

## 9. 数据、状态与恢复边界

状态来源和恢复方式可追溯；未知外部结果不得显示为成功。

## 10. 当前版本范围与真实性

| 层面 | 当前实现 | 真实性 | 用户可见标识 | 后续替换 |
|---|---|---|---|---|
| 产品表面 | 可操作原型 | 模拟 | 演示 | R1 完成后评估 |
| 数据 | Fixture | 模拟 | 演示数据 | R1 完成后评估 |

## 11. 成功、风险、假设与下一闸门

{ASSUMPTIONS}

通过评审只授权进入 R1 的体验验证，不授权真实外部写入。
"""


def make_roadmap(
    primary: str,
    secondary: str = "无",
    risks: str = "无",
    readiness: str = "是（等待批准）",
) -> str:
    risks = normalized_risks(primary, risks)
    return f"""# Example Product Roadmap

- 文档版本：2.0.0
- 证据截止日期：2026-08-09
- 产品主形态：{primary}
- 次级形态：{secondary}
- 风险修饰项：{risks}
- 当前证据阶段：交互原型
- 当前交付目的：用户价值验证
- 适用产品合同：{contracts(primary, secondary, risks)}
- 文档状态：Proposed
- 是否具备审批条件：{readiness}

## 1. 核心用户任务与演进目标

用户完成主任务并看见结果。

## 2. 当前基线、价值瓶颈与能力优先级

R0 只完成一半任务，结果闭合是瓶颈。

## 3. 产品能力层级

| 产品模块 | L0 | L1 | L2 |
|---|---|---|---|
| A「核心能力」 | A0「固定结果」 | A1「规则结果」 | A2「真实结果」 |
| B「可信保障」 | B0「状态标识」 | B1「权限恢复」 | B2「审计治理」 |

## 4. 体验版本路线图

| 体验版本 | 用户任务 | 核心能力 | 用户可见结果 | 本版主要增量 | 主要验证问题 | 进入条件 | 退出条件 | 状态 |
|---|---|---|---|---|---|---|---|---|
| R0「当前基线」 | 查看已有结果 | 历史能力 | 看见已有页面 | 冻结现状 | 当前证明什么 | 原型存在 | 基线记录 | 已有 |
| R1（第 1 个体验版本）「主任务闭环」 | 完成主任务 | A0「固定结果」 + B0「状态标识」 | 看见结果 | 补齐闭环 | 价值是否成立 | 基线完成 | 路径证据并进入评审 | Proposed |

## 5. 当前版本交付与真实性

| 交付项 | 用户可见结果 | 当前实现 | 真实性 | 验收证据 | 不包含 |
|---|---|---|---|---|---|
| 主任务闭环 | 看见结果和状态 | 固定数据原型 | 模拟 | 可复现路径记录 | 真实外部写入 |

## 6. 依赖、风险、假设与版本闸门

{ASSUMPTIONS}

| 闸门 | 所需证据 | 决策人 | 通过后授权 | 未通过处理 |
|---|---|---|---|---|
| R1 评审 | 完整路径与恢复证据 | 产品负责人 | 仅进入下一轮验证 | 修复后重审 |
"""


class ContractTests(unittest.TestCase):
    def run_validator(
        self,
        prd: str,
        roadmap: str,
        *extra: str,
    ) -> subprocess.CompletedProcess[str]:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            prd_path = root / "prd.md"
            roadmap_path = root / "roadmap.md"
            prd_path.write_text(prd, encoding="utf-8")
            roadmap_path.write_text(roadmap, encoding="utf-8")
            return subprocess.run(
                ["python3", str(VALIDATOR), "--prd", str(prd_path), "--roadmap", str(roadmap_path), *extra],
                capture_output=True,
                text=True,
                check=False,
            )

    def assert_passes(self, primary: str, secondary: str = "无", risks: str = "无") -> None:
        result = self.run_validator(make_prd(primary, secondary, risks), make_roadmap(primary, secondary, risks))
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("proof boundary", result.stdout)

    def assert_fails_with(self, prd: str, roadmap: str, marker: str) -> None:
        result = self.run_validator(prd, roadmap)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(marker, result.stderr)

    def test_all_primary_shapes_pass(self) -> None:
        for primary in SHAPE_TABLES:
            with self.subTest(primary=primary):
                self.assert_passes(primary)

    def test_secondary_shape_and_ai_risk_pass(self) -> None:
        self.assert_passes("C端交互产品", "服务编排", "AI")

    def test_json_report_passes_and_names_boundary(self) -> None:
        result = self.run_validator(make_prd("内容/产物生产"), make_roadmap("内容/产物生产"), "--format", "json")
        self.assertEqual(result.returncode, 0, result.stdout)
        report = json.loads(result.stdout)
        self.assertEqual(report["status"], "pass")
        self.assertEqual(report["proof_boundary"], "structural_and_cross_document_consistency_only")

    def test_invalid_primary_fails(self) -> None:
        self.assert_fails_with(make_prd("混合产品"), make_roadmap("混合产品"), "product-shape")

    def test_invalid_secondary_fails(self) -> None:
        self.assert_fails_with(make_prd("内容/产物生产", "AI助手"), make_roadmap("内容/产物生产", "AI助手"), "product-shape")

    def test_more_than_two_secondary_shapes_fail(self) -> None:
        value = "C端交互产品、内部流程工具、API/平台"
        self.assert_fails_with(make_prd("内容/产物生产", value), make_roadmap("内容/产物生产", value), "最多两个")

    def test_primary_cannot_repeat_as_secondary(self) -> None:
        self.assert_fails_with(make_prd("API/平台", "API/平台"), make_roadmap("API/平台", "API/平台"), "主形态不重复")

    def test_marketplace_requires_transaction_risk(self) -> None:
        prd = make_prd("交易/市场").replace("- 风险修饰项：交易", "- 风险修饰项：无").replace("、交易风险合同", "").replace(risk_tables("交易"), "")
        roadmap = make_roadmap("交易/市场").replace("- 风险修饰项：交易", "- 风险修饰项：无").replace("、交易风险合同", "")
        self.assert_fails_with(prd, roadmap, "交易风险")

    def test_missing_shape_contract_fails(self) -> None:
        prd = make_prd("内容/产物生产").replace(SHAPE_TABLES["内容/产物生产"], "缺少生产合同")
        self.assert_fails_with(prd, make_roadmap("内容/产物生产"), "shape:内容/产物生产")

    def test_missing_risk_control_row_fails(self) -> None:
        prd = make_prd("C端交互产品", risks="AI、发布").replace(
            "| 发布 | 主任务 | 错误结果 | 人工复核 | 用户确认 | 标记未知 | 审计记录 | 负责人批准 |\n",
            "",
        )
        self.assert_fails_with(prd, make_roadmap("C端交互产品", risks="AI、发布"), "每个风险修饰项")

    def test_missing_ai_contract_fails(self) -> None:
        prd = make_prd("C端交互产品", risks="AI").replace(AI_TABLE, "缺少 AI 合同")
        self.assert_fails_with(prd, make_roadmap("C端交互产品", risks="AI"), "risk:AI")

    def test_future_target_is_not_current_evidence(self) -> None:
        prd = make_prd("内容/产物生产").replace("| 已观察 | 原型记录 |", "| 目标态 | 路线图 |")
        self.assert_fails_with(prd, make_roadmap("内容/产物生产"), "current-effect")

    def test_invalid_truth_status_fails(self) -> None:
        prd = make_prd("内容/产物生产").replace("| 模拟 | 演示 |", "| 目标态 | 演示 |", 1)
        self.assert_fails_with(prd, make_roadmap("内容/产物生产"), "truth-boundary")

    def test_missing_assumption_register_fails(self) -> None:
        prd = make_prd("内容/产物生产").replace(ASSUMPTIONS, "| 备注 | 内容 |\n|---|---|\n| 一 | 二 |")
        self.assert_fails_with(prd, make_roadmap("内容/产物生产"), "assumptions")

    def test_unconfirmed_must_be_true_cannot_be_ready(self) -> None:
        changed = ASSUMPTIONS.replace("| 必须为真 | 用户需要该结果 | 已确认 |", "| 必须为真 | 用户需要该结果 | 建议假设，待确认 |")
        prd = make_prd("内容/产物生产").replace(ASSUMPTIONS, changed)
        roadmap = make_roadmap("内容/产物生产").replace(ASSUMPTIONS, changed)
        self.assert_fails_with(prd, roadmap, "approval-readiness")

    def test_unconfirmed_must_be_true_can_remain_not_ready(self) -> None:
        changed = ASSUMPTIONS.replace("| 必须为真 | 用户需要该结果 | 已确认 |", "| 必须为真 | 用户需要该结果 | 建议假设，待确认 |")
        readiness = "否（存在未确认关键假设）"
        result = self.run_validator(
            make_prd("内容/产物生产", readiness=readiness).replace(ASSUMPTIONS, changed),
            make_roadmap("内容/产物生产", readiness=readiness).replace(ASSUMPTIONS, changed),
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("WARNING", result.stderr)

    def test_assumption_mismatch_fails(self) -> None:
        roadmap = make_roadmap("内容/产物生产").replace("首版使用固定数据", "首版使用人工数据")
        self.assert_fails_with(make_prd("内容/产物生产"), roadmap, "cross-doc:assumptions")

    def test_metadata_mismatch_fails(self) -> None:
        roadmap = make_roadmap("内容/产物生产").replace("- 当前交付目的：用户价值验证", "- 当前交付目的：规模化")
        self.assert_fails_with(make_prd("内容/产物生产"), roadmap, "cross-doc:metadata")

    def test_duplicate_metadata_fails(self) -> None:
        prd = make_prd("内容/产物生产").replace("- 文档版本：2.0.0", "- 文档版本：2.0.0\n- 文档版本：2.0.0")
        self.assert_fails_with(prd, make_roadmap("内容/产物生产"), "只出现一次")

    def test_invalid_version_and_date_fail(self) -> None:
        prd = make_prd("内容/产物生产").replace("- 文档版本：2.0.0", "- 文档版本：draft").replace("- 证据截止日期：2026-08-09", "- 证据截止日期：2026-99-99")
        roadmap = make_roadmap("内容/产物生产").replace("- 文档版本：2.0.0", "- 文档版本：draft").replace("- 证据截止日期：2026-08-09", "- 证据截止日期：2026-99-99")
        result = self.run_validator(prd, roadmap)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("语义版本", result.stderr)
        self.assertIn("YYYY-MM-DD", result.stderr)

    def test_invalid_document_status_fails(self) -> None:
        prd = make_prd("内容/产物生产").replace("- 文档状态：Proposed", "- 文档状态：Done")
        roadmap = make_roadmap("内容/产物生产").replace("- 文档状态：Proposed", "- 文档状态：Done")
        self.assert_fails_with(prd, roadmap, "文档状态属于")

    def test_approved_requires_approved_readiness(self) -> None:
        prd = make_prd("内容/产物生产").replace("- 文档状态：Proposed", "- 文档状态：Approved")
        roadmap = make_roadmap("内容/产物生产").replace("- 文档状态：Proposed", "- 文档状态：Approved")
        self.assert_fails_with(prd, roadmap, "Approved 对应")

    def test_version_ordinal_mismatch_fails(self) -> None:
        roadmap = make_roadmap("内容/产物生产").replace("R1（第 1 个体验版本）", "R1（第 2 个体验版本）")
        self.assert_fails_with(make_prd("内容/产物生产"), roadmap, "version-code")

    def test_version_gap_fails(self) -> None:
        row = "| R3（第 3 个体验版本）「规模」 | 扩展任务 | A2「真实结果」 | 更多结果 | 扩展 | 是否可扩展 | R1 完成 | 采用证据 | Proposed |"
        roadmap = make_roadmap("内容/产物生产").replace("\n\n## 5.", f"\n{row}\n\n## 5.")
        self.assert_fails_with(make_prd("内容/产物生产"), roadmap, "连续编号")

    def test_invalid_version_status_fails(self) -> None:
        roadmap = make_roadmap("内容/产物生产").replace("| Proposed |\n\n## 5.", "| Done |\n\n## 5.")
        self.assert_fails_with(make_prd("内容/产物生产"), roadmap, "状态属于")

    def test_unnamed_capability_fails(self) -> None:
        roadmap = make_roadmap("内容/产物生产").replace("A0「固定结果」 + B0「状态标识」", "A0 + B0「状态标识」")
        self.assert_fails_with(make_prd("内容/产物生产"), roadmap, "capability-code")

    def test_numbered_gate_is_not_misread_as_capability(self) -> None:
        roadmap = make_roadmap("内容/产物生产").replace("| R1 评审 |", "| G1「R1 评审」 |")
        result = self.run_validator(make_prd("内容/产物生产"), roadmap)
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_module_l_capability_is_supported(self) -> None:
        prd = make_prd("内容/产物生产").replace('B「可信保障」', 'L「可信保障」').replace('B「状态标识」', 'L「状态标识」')
        roadmap = make_roadmap("内容/产物生产").replace('B「可信保障」', 'L「可信保障」').replace('B0「状态标识」', 'L0「状态标识」').replace('B1「权限恢复」', 'L1「权限恢复」').replace('B2「审计治理」', 'L2「审计治理」')
        result = self.run_validator(prd, roadmap)
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_requirement_id_must_be_named(self) -> None:
        prd = make_prd("内容/产物生产").replace("P0-01「主任务」", "P0-01")
        self.assert_fails_with(prd, make_roadmap("内容/产物生产"), "requirement-id")

    def test_requirement_must_map_to_defined_module(self) -> None:
        prd = make_prd("内容/产物生产").replace("| P0-01「主任务」 | P0 | A「核心能力」 |", "| P0-01「主任务」 | P0 | C「不存在」 |")
        self.assert_fails_with(prd, make_roadmap("内容/产物生产"), "需求映射到已定义模块")

    def test_unsourced_numeric_target_fails(self) -> None:
        prd = make_prd("内容/产物生产").replace("用户获得结果并形成继续使用理由。", "任务完成率达到 90%。")
        self.assert_fails_with(prd, make_roadmap("内容/产物生产"), "numeric-target")

    def test_open_marker_outside_assumptions_fails(self) -> None:
        prd = make_prd("内容/产物生产").replace("帮助用户完成一项有价值的任务", "帮助用户完成 [待确认] 任务")
        self.assert_fails_with(prd, make_roadmap("内容/产物生产"), "开放项进入假设登记表")

    def test_allow_open_marker_turns_error_into_warning(self) -> None:
        prd = make_prd("内容/产物生产").replace("帮助用户完成一项有价值的任务", "帮助用户完成 [待确认] 任务")
        result = self.run_validator(prd, make_roadmap("内容/产物生产"), "--allow-open-questions")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("WARNING", result.stderr)

    def test_empty_required_table_fails(self) -> None:
        prd = make_prd("内容/产物生产").replace("| 完成主任务 | 获得可用结果 | 未知，需建立基线 | 完成并理解结果 | 任务观察 | 待验证 |", "")
        self.assert_fails_with(prd, make_roadmap("内容/产物生产"), "至少一行数据")

    def test_broken_relative_link_fails(self) -> None:
        prd = make_prd("内容/产物生产").replace("帮助用户完成一项有价值的任务", "帮助用户完成一项有价值的任务，见 [证据](missing.md)")
        self.assert_fails_with(prd, make_roadmap("内容/产物生产"), "有效相对链接")


if __name__ == "__main__":
    unittest.main()
