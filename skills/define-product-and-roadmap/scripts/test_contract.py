#!/usr/bin/env python3
"""产品 PRD/Roadmap 契约验证器的回归测试（契约 3.0.0:PRD 7 章/Roadmap 6 章、需求块、场景 A/B、各司其职）。

要求 Python >= 3.8,零第三方依赖。用当前解释器（sys.executable）调用验证器,兼容无 python3 命令的平台。
"""

from __future__ import annotations

import json
import subprocess
import sys
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

AI_EVALUATION_TABLE = """| 评估维度 | 评估载体 | 基线采集动作 | 裁决机制 | 解锁条件 |
|---|---|---|---|---|
| 结果质量 | 3 篇真实样本 | 评审者先打分建立基线 | 双人独立评分一致 | 基线记录归档后解锁生成 |"""

ASSUMPTIONS = """| 类型 | 假设或决策 | 状态 | 依据 | 对产品影响 | 确认人/下一步 |
|---|---|---|---|---|---|
| 必须为真 | 用户需要该结果 | 已确认 | 用户研究 | 决定方向 | 产品负责人 |
| 可逆默认 | 首版使用固定数据 | 已确认 | 当前阶段 | 只影响验证方式 | R1 后复核 |"""

SUCCESS_TABLE = """| 指标组 | 成功信号 | 对应用户价值 | 当前基线 | 本版判定 | 证据方法 | 结论状态 |
|---|---|---|---|---|---|---|
| 交互与流畅 | 完成主任务 | 获得可用结果 | 已有记录 | 完成并理解结果 | 任务观察 | 待验证 |"""

REQUIREMENT_BLOCKS = """#### 3.2.1 P0 需求:主任务闭环（1 条,最高优先级）

**P0-01「主任务」**（P0 · 模块 A）
- 做什么:完成主任务并闭合结果。
- 你会看到:看见结果与状态。
- 规则:保留返回。
- 验收:状态可复现。
- 证据:待版本验证。"""


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
    scenario: str = "B（存量迭代）",
) -> str:
    risks = normalized_risks(primary, risks)
    selected = [primary] + ([] if secondary == "无" else secondary.split("、"))
    shape_tables = "\n\n".join(SHAPE_TABLES[item] for item in selected if item in SHAPE_TABLES)
    if scenario.startswith("A"):
        reuse_section = """| 依赖 | 用途 | 可用性 | 许可状态 | 失败影响 |
|---|---|---|---|---|
| 外部服务 | 数据来源 | 未接入 | 未声明 | 降级人工 |"""
        current_effect = ""
        evidence_stage = "交互原型"
    else:
        reuse_section = """| 来源 | 版本/日期 | 复用决策 | 负责什么 | 已证实能力 | 产品映射 | 证据边界 |
|---|---|---|---|---|---|---|
| Reference | 2026-08-01 | 「方法借鉴」 | 参考方法 | 已有样例 | A「核心能力」 | 不证明运行效果 |"""
        current_effect = """
### 2.4 当前效果与缺口

| 观察对象 | 当前效果 | 证据状态 | 证据来源 | 当前缺口 |
|---|---|---|---|---|
| 当前原型 | 能完成一半任务 | 已观察 | 原型记录 | 结果未闭合 |
"""
        evidence_stage = "有限真实使用"
    return f"""# Example Product Requirements

- 文档版本：2.0.0
- 证据截止日期：2026-08-09
- 产品主形态：{primary}
- 次级形态：{secondary}
- 风险修饰项：{risks}
- 当前证据阶段：{evidence_stage}
- 当前交付目的：用户价值验证
- 适用场景：{scenario}
- 适用产品合同：{contracts(primary, secondary, risks)}
- 文档状态：Proposed
- 是否具备审批条件：{readiness}

## 1. 产品定位与承诺

**本章讲什么**:定位、目标与关键决定。

帮助用户完成一项有价值的任务;本版不包含真实外部写入。

## 2. 现状与问题

**本章讲什么**:谁在用、问题多严重、瓶颈在哪。

目标用户需要一个清楚的结果,当前只能完成一半任务。
{current_effect}
### 2.5 第一个价值瓶颈与最短价值路径

**最短价值路径**:输入 → 处理（当前人工）→ 结果。瓶颈=结果未闭合。

## 3. 产品方案:能力、需求与运转

**本章讲什么**:能力地图、需求清单与运转方式。

### 3.1 能力地图

| 模块 | 责任 | 输入 | 用户可见输出 | 当前状态 | 失败与恢复 | 优先级 |
|---|---|---|---|---|---|---|
| A「核心能力」 | 完成主任务 | 用户输入 | 用户结果 | 输入、处理中、完成 | 保存输入后重试 | P0 |
| B「可信保障」 | 保护真实性 | 状态 | 边界标识 | 已知、未知 | 转人工 | P1 |

### 3.2 需求清单

**需求落到哪个版本由路线图统一编排（见 ROADMAP 需求落位映射）,本文只定优先级与验收,不标版本**。

{REQUIREMENT_BLOCKS}

### 3.3 系统如何运转

{shape_tables}{risk_tables(risks)}

#### 3.3.5 AI 参与的边界

{AI_EVALUATION_TABLE}

## 4. 规则与红线

状态来源和恢复方式可追溯;未知外部结果不得显示为成功。

## 5. 价值与成功指标

用户获得结果并形成继续使用理由。

{SUCCESS_TABLE}

## 6. 复用与依赖

{reuse_section}

## 7. 风险与假设

{ASSUMPTIONS}

通过评审只授权进入下一闸门,不授权真实外部写入。
"""


def make_roadmap(
    primary: str,
    secondary: str = "无",
    risks: str = "无",
    readiness: str = "是（等待批准）",
    scenario: str = "B（存量迭代）",
) -> str:
    risks = normalized_risks(primary, risks)
    if scenario.startswith("A"):
        baseline = "起点声明:从零开始,无存量资产。"
        r0_row = ""
        r0_detail = ""
    else:
        baseline = "R0 只完成一半任务,结果闭合是瓶颈。"
        r0_row = "| R0「当前基线」 | 记录现状 | 能完成一半任务 | 已有 |\n"
        r0_detail = """**R0「当前基线」**（已有）
- 任务:记录当前现状。
- 核心能力:A0「固定结果」、B0「状态标识」。

"""
    return f"""# Example Product Roadmap

- 文档版本：2.0.0
- 证据截止日期：2026-08-09
- 产品主形态：{primary}
- 次级形态：{secondary}
- 风险修饰项：{risks}
- 当前证据阶段：{"交互原型" if scenario.startswith("A") else "有限真实使用"}
- 当前交付目的：用户价值验证
- 适用场景：{scenario}
- 适用产品合同：{contracts(primary, secondary, risks)}
- 文档状态：Proposed
- 是否具备审批条件：{readiness}

## 1. 用户与终局

用户完成主任务并看见结果。

## 2. 现状与总路线

{baseline}

## 3. 本版详单:主任务闭环（R1，第 1 个体验版本）

### 3.1 本版范围与不包含

交付 P0-01;不包含真实外部写入。

### 3.2 交付清单与验收

| 交付项 | 用户可见结果 | 当前实现 | 真实性 | 验收证据 |
|---|---|---|---|---|
| 主任务闭环 | 看见结果和状态 | 固定数据原型 | 模拟 | 可复现路径记录 |

### 3.3 真值边界表

| 层面 | 当前实现 | 真实性 | 用户可见标识 | 后续替换 |
|---|---|---|---|---|
| 产品表面 | 可操作原型 | 模拟 | 演示 | R1 完成后评估 |
| 数据 | Fixture | 模拟 | 演示数据 | R1 完成后评估 |

## 4. 体验版本路线图

### 4.1 一句话路线总述

R1 完成主任务闭环。

### 4.2 版本总表

| 版本 | 一句话任务 | 你会看到什么（对比上一版） | 状态 |
|---|---|---|---|
{r0_row}| R1「主任务闭环」 | 完成主任务 | 看见结果 | Proposed |

### 4.3 每版详述

{r0_detail}**R1（第 1 个体验版本）「主任务闭环」**（Proposed）
- 任务:完成主任务并看见结果。
- 核心能力:A0「固定结果」、B0「状态标识」。
- 你会看到:结果与状态同时呈现。
- 为什么有效:闭合当前断点。
- 本版增量（动作→感知）:补齐闭环。
- 主要验证问题:价值是否成立。
- 进入条件:基线完成。
- 退出条件:路径证据并进入评审。

### 4.4 需求落位映射

本表为需求落位到各体验版本的唯一权威:PRD 按优先级组织、不标版本。

- R1：P0-01

## 5. 能力层级（参考）

| 产品模块 | L0（第一级） | L1（第二级） | L2（第三级） |
|---|---|---|---|
| A「核心能力」 | A0「固定结果」 | A1「规则结果」 | A2「真实结果」 |
| B「可信保障」 | B0「状态标识」 | B1「权限恢复」 | B2「审计治理」 |

## 6. 闸门与假设

{ASSUMPTIONS}

| 闸门 | 这门管什么（白话） | 所需证据 | 决策人 | 通过后授权 | 卡住回到哪 |
|---|---|---|---|---|---|
| GT1（第 1 道闸门） | 值不值得开工 | 完整路径与恢复证据 | 产品负责人 | 仅进入下一轮验证 | 修复后重审 |
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
                [sys.executable, str(VALIDATOR), "--prd", str(prd_path), "--roadmap", str(roadmap_path), *extra],
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
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

    # --- 形态与风险（回归） ---

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

    # --- 元数据（回归） ---

    def test_future_target_is_not_current_evidence(self) -> None:
        prd = make_prd("内容/产物生产").replace("| 已观察 | 原型记录 |", "| 目标态 | 路线图 |")
        self.assert_fails_with(prd, make_roadmap("内容/产物生产"), "current-effect")

    def test_invalid_truth_status_fails(self) -> None:
        roadmap = make_roadmap("内容/产物生产").replace("| 模拟 | 演示 |", "| 目标态 | 演示 |", 1)
        self.assert_fails_with(make_prd("内容/产物生产"), roadmap, "truth-boundary")

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
        self.assertIn("警告", result.stderr)

    def test_assumption_mismatch_fails(self) -> None:
        roadmap = make_roadmap("内容/产物生产").replace("首版使用固定数据", "首版使用人工数据")
        self.assert_fails_with(make_prd("内容/产物生产"), roadmap, "cross-doc:assumptions")

    def test_metadata_mismatch_fails(self) -> None:
        roadmap = make_roadmap("内容/产物生产").replace("- 当前交付目的：用户价值验证", "- 当前交付目的：规模化")
        self.assert_fails_with(make_prd("内容/产物生产"), roadmap, "cross-doc:metadata")

    def test_scenario_metadata_mismatch_fails(self) -> None:
        roadmap = make_roadmap("内容/产物生产", scenario="A（0→1 新产品）")
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

    # --- 版本与能力（回归） ---

    def test_version_ordinal_mismatch_fails(self) -> None:
        roadmap = make_roadmap("内容/产物生产").replace("R1（第 1 个体验版本）「主任务闭环」**（Proposed）", "R1（第 2 个体验版本）「主任务闭环」**（Proposed）")
        self.assert_fails_with(make_prd("内容/产物生产"), roadmap, "version-code")

    def test_version_gap_fails(self) -> None:
        row = '| R3「规模」 | 扩展任务 | 更多结果 | Proposed |'
        roadmap = make_roadmap("内容/产物生产").replace("\n\n### 4.3", f"\n{row}\n\n### 4.3")
        self.assert_fails_with(make_prd("内容/产物生产"), roadmap, "连续编号")

    def test_invalid_version_status_fails(self) -> None:
        roadmap = make_roadmap("内容/产物生产").replace('| R1「主任务闭环」 | 完成主任务 | 看见结果 | Proposed |', '| R1「主任务闭环」 | 完成主任务 | 看见结果 | Done |')
        self.assert_fails_with(make_prd("内容/产物生产"), roadmap, "状态属于")

    def test_unnamed_capability_fails(self) -> None:
        roadmap = make_roadmap("内容/产物生产").replace("A0「固定结果」 | A1「规则结果」", "A0 | A1「规则结果」")
        self.assert_fails_with(make_prd("内容/产物生产"), roadmap, "capability-code")

    def test_numbered_gate_is_not_misread_as_capability(self) -> None:
        roadmap = make_roadmap("内容/产物生产").replace("| GT1（第 1 道闸门） |", "| G1「GT1（第 1 道闸门）」 |")
        result = self.run_validator(make_prd("内容/产物生产"), roadmap)
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_module_l_capability_is_supported(self) -> None:
        prd = make_prd("内容/产物生产").replace('B「可信保障」', 'L「可信保障」')
        roadmap = make_roadmap("内容/产物生产").replace('B「可信保障」', 'L「可信保障」').replace('B0「状态标识」', 'L0「状态标识」').replace('B1「权限恢复」', 'L1「权限恢复」').replace('B2「审计治理」', 'L2「审计治理」')
        result = self.run_validator(prd, roadmap)
        self.assertEqual(result.returncode, 0, result.stderr)

    # --- 需求块（新结构回归） ---

    def test_requirement_id_must_be_named(self) -> None:
        prd = make_prd("内容/产物生产").replace("**P0-01「主任务」**", "**P0-01**")
        self.assert_fails_with(prd, make_roadmap("内容/产物生产"), "落位映射只引用")

    def test_requirement_must_map_to_defined_module(self) -> None:
        prd = make_prd("内容/产物生产").replace("**P0-01「主任务」**（P0 · 模块 A）", "**P0-01「主任务」**（P0 · 模块 C）")
        self.assert_fails_with(prd, make_roadmap("内容/产物生产"), "需求块模块映射到能力地图已定义模块")

    def test_requirement_missing_element_fails(self) -> None:
        prd = make_prd("内容/产物生产").replace("- 验收:状态可复现。", "")
        self.assert_fails_with(prd, make_roadmap("内容/产物生产"), "五要素")

    def test_requirement_priority_mismatch_with_group_fails(self) -> None:
        prd = make_prd("内容/产物生产").replace(
            "#### 3.2.1 P0 需求:主任务闭环（1 条,最高优先级）",
            "#### 3.2.1 P1 需求:主任务闭环（1 条,次优先级）",
        )
        self.assert_fails_with(prd, make_roadmap("内容/产物生产"), "需求优先级与所在分组一致")

    def test_requirements_without_priority_groups_fail(self) -> None:
        prd = make_prd("内容/产物生产").replace("#### 3.2.1 P0 需求:主任务闭环（1 条,最高优先级）", "#### 3.2.1 需求:主任务闭环")
        self.assert_fails_with(prd, make_roadmap("内容/产物生产"), "按 P0/P1/P2 优先级分组")

    # --- 各司其职（新增） ---

    def test_prd_version_placement_statement_fails(self) -> None:
        prd = make_prd("内容/产物生产").replace("- 做什么:完成主任务并闭合结果。", "- 做什么:完成主任务并闭合结果（落位 R1）。")
        self.assert_fails_with(prd, make_roadmap("内容/产物生产"), "PRD 不标版本")

    def test_prd_requirement_section_version_code_fails(self) -> None:
        prd = make_prd("内容/产物生产").replace("本文只定优先级与验收,不标版本**。", "本文只定优先级与验收,不标版本**。R1 承载主任务。")
        self.assert_fails_with(prd, make_roadmap("内容/产物生产"), "需求清单区段不出现 R* 版本编码")

    def test_mapping_missing_requirement_fails(self) -> None:
        roadmap = make_roadmap("内容/产物生产").replace("- R1：P0-01", "- R1：P0-02")
        self.assert_fails_with(make_prd("内容/产物生产"), roadmap, "PRD 每条需求在落位映射中有落位版本")

    def test_mapping_undefined_requirement_fails(self) -> None:
        roadmap = make_roadmap("内容/产物生产").replace("- R1：P0-01", "- R1：P0-01/P0-02")
        self.assert_fails_with(make_prd("内容/产物生产"), roadmap, "落位映射只引用 PRD 已定义的需求编号")

    def test_mapping_section_missing_fails(self) -> None:
        roadmap = make_roadmap("内容/产物生产").replace("### 4.4 需求落位映射", "### 4.4 其他内容")
        self.assert_fails_with(make_prd("内容/产物生产"), roadmap, "「需求落位映射」小节")

    # --- 场景 A/B（新增） ---

    def test_scenario_a_passes_without_current_effect_and_r0(self) -> None:
        prd = make_prd("内容/产物生产", scenario="A（0→1 新产品）")
        roadmap = make_roadmap("内容/产物生产", scenario="A（0→1 新产品）")
        result = self.run_validator(prd, roadmap)
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_scenario_b_requires_current_effect_table(self) -> None:
        prd = make_prd("内容/产物生产").replace(
            """### 2.4 当前效果与缺口

| 观察对象 | 当前效果 | 证据状态 | 证据来源 | 当前缺口 |
|---|---|---|---|---|
| 当前原型 | 能完成一半任务 | 已观察 | 原型记录 | 结果未闭合 |
""",
            "",
        )
        self.assert_fails_with(prd, make_roadmap("内容/产物生产"), "current-effect")

    def test_scenario_b_requires_r0_row(self) -> None:
        roadmap = make_roadmap("内容/产物生产").replace('| R0「当前基线」 | 记录现状 | 能完成一半任务 | 已有 |\n', "")
        self.assert_fails_with(make_prd("内容/产物生产"), roadmap, "R0 当前基线行")

    def test_scenario_a_with_real_use_warns_transition(self) -> None:
        prd = make_prd("内容/产物生产", scenario="A（0→1 新产品）").replace(
            "- 当前证据阶段：交互原型", "- 当前证据阶段：有限真实使用"
        )
        roadmap = make_roadmap("内容/产物生产", scenario="A（0→1 新产品）").replace(
            "- 当前证据阶段：交互原型", "- 当前证据阶段：有限真实使用"
        )
        result = self.run_validator(prd, roadmap)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("A→B", result.stderr)

    def test_invalid_scenario_value_fails(self) -> None:
        prd = make_prd("内容/产物生产", scenario="C（未知）")
        roadmap = make_roadmap("内容/产物生产", scenario="C（未知）")
        self.assert_fails_with(prd, roadmap, "适用场景为")

    # --- 呈现与开放项（回归） ---

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
        self.assertIn("警告", result.stderr)

    def test_empty_required_table_fails(self) -> None:
        prd = make_prd("内容/产物生产").replace(
            "| 交互与流畅 | 完成主任务 | 获得可用结果 | 已有记录 | 完成并理解结果 | 任务观察 | 待验证 |", ""
        )
        self.assert_fails_with(prd, make_roadmap("内容/产物生产"), "至少一行数据")

    def test_broken_relative_link_fails(self) -> None:
        prd = make_prd("内容/产物生产").replace("帮助用户完成一项有价值的任务", "帮助用户完成一项有价值的任务，见 [证据](missing.md)")
        self.assert_fails_with(prd, make_roadmap("内容/产物生产"), "有效相对链接")

    def test_factory_documents_stay_warning_clean(self) -> None:
        for primary, secondary, risks, scenario in (
            ("内容/产物生产", "无", "无", "B（存量迭代）"),
            ("C端交互产品", "服务编排", "AI", "B（存量迭代）"),
            ("内容/产物生产", "无", "无", "A（0→1 新产品）"),
        ):
            with self.subTest(primary=primary, risks=risks, scenario=scenario):
                result = self.run_validator(
                    make_prd(primary, secondary, risks, scenario=scenario),
                    make_roadmap(primary, secondary, risks, scenario=scenario),
                )
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertNotIn("警告:", result.stderr)

    def test_repeated_sentence_warns(self) -> None:
        sentence = "产品哲学是以用户价值为唯一导向并持续压缩无效环节"
        prd = make_prd("内容/产物生产")
        prd = prd.replace("本版不包含真实外部写入。", f"本版不包含真实外部写入。\n\n{sentence}。")
        prd = prd.replace("当前只能完成一半任务。", f"当前只能完成一半任务。{sentence}。")
        prd = prd.replace("不得显示为成功。", f"不得显示为成功。{sentence}。")
        result = self.run_validator(prd, make_roadmap("内容/产物生产"))
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("presentation:duplication", result.stderr)

    def test_repeated_fragment_warns(self) -> None:
        fragment = "推进公式要求从证据出发经过假设分层再进入版本闸门形成完整闭环"
        prd = make_prd("内容/产物生产").replace(
            "不得显示为成功。",
            "不得显示为成功。第一，" + fragment + "。第二，" + fragment + "并被团队确认。第三，" + fragment + "以防止跳跃。",
        )
        result = self.run_validator(prd, make_roadmap("内容/产物生产"))
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("presentation:duplication", result.stderr)

    def test_table_content_repetition_is_exempt(self) -> None:
        row = "| 重要假设 | 用户能理解结果 | 已确认 | 说明 | 影响 | 产品负责人 |"
        prd = make_prd("内容/产物生产").replace(ASSUMPTIONS, ASSUMPTIONS + "\n" + row)
        roadmap = make_roadmap("内容/产物生产").replace(ASSUMPTIONS, ASSUMPTIONS + "\n" + row)
        result = self.run_validator(prd, roadmap)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertNotIn("presentation:duplication", result.stderr)

    def test_boxed_code_repetition_is_exempt(self) -> None:
        marker = "R1（第 1 个体验版本）「主任务闭环」按计划推进"
        roadmap = make_roadmap("内容/产物生产").replace(
            "R1 完成主任务闭环。",
            f"R1 完成主任务闭环。{marker}。{marker}。{marker}。",
        )
        result = self.run_validator(make_prd("内容/产物生产"), roadmap)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertNotIn("presentation:duplication", result.stderr)

    def test_header_revision_history_warns(self) -> None:
        prd = make_prd("内容/产物生产").replace(
            "- 文档状态：Proposed",
            "- 修订要点：0.6.0 新增成功表；0.6.1 合并基线\n- 文档状态：Proposed",
        )
        result = self.run_validator(prd, make_roadmap("内容/产物生产"))
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("presentation:header-archaeology", result.stderr)

    def test_body_version_archaeology_warns(self) -> None:
        prd = make_prd("内容/产物生产").replace(
            "帮助用户完成一项有价值的任务",
            "帮助用户完成一项有价值的任务（0.6.0 起）",
        )
        result = self.run_validator(prd, make_roadmap("内容/产物生产"))
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("presentation:version-archaeology", result.stderr)

    def test_self_version_mismatch_fails(self) -> None:
        prd = make_prd("内容/产物生产").replace("帮助用户完成", "本文档（0.6.1）帮助用户完成")
        roadmap = make_roadmap("内容/产物生产").replace("用户完成主任务并看见结果", "本路线图（0.6.1）描述用户完成主任务并看见结果")
        self.assert_fails_with(prd, roadmap, "self-version")

    def test_self_version_consistent_passes(self) -> None:
        prd = make_prd("内容/产物生产").replace("帮助用户完成", "本文档（2.0.0）帮助用户完成")
        result = self.run_validator(prd, make_roadmap("内容/产物生产"))
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertNotIn("self-version", result.stderr)

    def test_same_header_tables_warn_convergence(self) -> None:
        prd = make_prd("内容/产物生产").replace(ASSUMPTIONS, ASSUMPTIONS + "\n\n同轴补充：\n\n" + ASSUMPTIONS)
        result = self.run_validator(prd, make_roadmap("内容/产物生产"))
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("presentation:table-convergence", result.stderr)

    def test_prose_module_code_must_be_defined(self) -> None:
        prd = make_prd("内容/产物生产").replace(
            "帮助用户完成一项有价值的任务",
            "D「数据分析」帮助用户完成一项有价值的任务",
        )
        self.assert_fails_with(prd, make_roadmap("内容/产物生产"), "prose-codes")

    def test_prose_module_code_defined_passes(self) -> None:
        prd = make_prd("内容/产物生产").replace(
            "帮助用户完成一项有价值的任务",
            "A「核心能力」帮助用户完成一项有价值的任务",
        )
        result = self.run_validator(prd, make_roadmap("内容/产物生产"))
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_missing_ai_evaluation_table_warns(self) -> None:
        prd = make_prd("C端交互产品", risks="AI").replace("\n\n" + AI_EVALUATION_TABLE, "")
        result = self.run_validator(prd, make_roadmap("C端交互产品", risks="AI"))
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("risk:AI-evaluation", result.stderr)


if __name__ == "__main__":
    unittest.main()
