#!/usr/bin/env python3
"""Regression tests for product-shape-aware PRD and Roadmap contracts."""

from __future__ import annotations

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
| 生产 | 素材 | 生成与审查 | 可用产物 | 人工审查 | checkpoint | 来源记录 |""",
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


def make_prd(primary: str, secondary: str = "无", readiness: str = "是（等待批准）") -> str:
    selected = [primary] + ([] if secondary == "无" else secondary.split("、"))
    shape_tables = "\n\n".join(SHAPE_TABLES[item] for item in selected if item in SHAPE_TABLES)
    ai_table = f"\n\n### AI 风险合同\n\n{AI_TABLE}" if "AI助手" in selected else ""
    return f"""# Example Product Requirements

- 产品主形态：{primary}
- 次级形态：{secondary}
- 当前证据阶段：交互原型
- 当前交付目的：用户验证
- 适用产品合同：通用合同、{primary}合同
- 文档状态：Proposed
- 是否具备审批条件：{readiness}

## 1. 产品定位与目标

帮助用户完成一项有价值的任务。

## 2. 目标用户与核心问题

目标用户需要一个清楚的结果。

## 3. 当前产品形态与效果

| 观察对象 | 当前效果 | 证据状态 | 证据来源 | 当前缺口 |
|---|---|---|---|---|
| 当前原型 | 能完成一半任务 | 已观察 | 原型记录 | 结果未闭合 |

## 4. 产品价值与价值循环

用户获得结果并形成继续使用理由。

## 5. 参考产品与复用策略

| 来源 | 负责什么 | 已证实能力 | 产品映射 | 复用决策 | 项目补充 | 用户价值 | 证据边界 |
|---|---|---|---|---|---|---|---|
| Reference | 参考方法 | 已有样例 | A「核心能力」 | 「方法借鉴」 | 项目规则 | 更快完成 | 仅作参考 |

## 6. 主要体验或生产合同

{shape_tables}{ai_table}

## 7. 产品能力与优先级

| 产品模块 | 责任 | 输入 | 用户可见输出 | 当前优先级 |
|---|---|---|---|---|
| A「核心能力」 | 完成主任务 | 用户输入 | 用户结果 | P0 |
| B「可信保障」 | 保护真实性 | 状态 | 边界标识 | P1 |

## 8. 产品需求与验收

| 编号 | 优先级 | 模块 | 产品要求 | 用户可见结果 | 业务规则 | 技术验收边界 | 证据状态 |
|---|---|---|---|---|---|---|---|
| P0-01「主任务」 | P0 | A「核心能力」 | 完成主任务 | 看见结果 | 保留返回 | 状态可复现 | 待版本验证 |

## 9. 数据、状态与恢复边界

状态来源和恢复方式可追溯。

## 10. 当前版本范围与真实性

| 层面 | 当前实现 | 真实性 | 用户可见标识 | 后续替换 |
|---|---|---|---|---|
| 产品表面 | 可操作原型 | 模拟 | 演示 | R2 |
| 数据 | Fixture | 模拟 | 演示数据 | R2 |

## 11. 成功、风险、假设与下一闸门

| 类型 | 假设或决策 | 状态 | 依据 | 对产品影响 | 确认人/下一步 |
|---|---|---|---|---|---|
| 必须为真 | 用户需要该结果 | 已确认 | 用户研究 | 决定方向 | 产品负责人 |
| 可逆默认 | 首版使用固定数据 | 已确认 | 当前阶段 | 只影响验证方式 | R2 替换 |
"""


def make_roadmap(primary: str, secondary: str = "无") -> str:
    return f"""# Example Product Roadmap

- 产品主形态：{primary}
- 次级形态：{secondary}
- 当前证据阶段：交互原型
- 当前交付目的：用户验证
- 适用产品合同：通用合同、{primary}合同
- 文档状态：Proposed
- 是否具备审批条件：是（等待批准）

## 1. 核心用户任务与演进目标

用户完成主任务并看见结果。

## 2. 当前基线、瓶颈与能力优先级

当前基线只完成一半任务，结果闭合是瓶颈。

## 3. 产品能力层级

| 产品模块 | L0 | L1 | L2 |
|---|---|---|---|
| A「核心能力」 | A0「固定结果」 | A1「规则结果」 | A2「真实结果」 |
| B「可信保障」 | B0「状态标识」 | B1「权限恢复」 | B2「审计治理」 |

## 4. 体验版本路线图

| 体验版本 | 用户任务 | 核心能力 | 用户可见结果 | 本版主要增量 | 主要验证问题 | 进入条件 | 退出条件 | 状态 |
|---|---|---|---|---|---|---|---|---|
| R0「当前基线」 | 查看已有结果 | 历史能力 | 看见已有页面 | 冻结现状 | 当前证明什么 | 原型存在 | 基线记录 | 已有 |
| R1（第 1 个体验版本）「主任务闭环」 | 完成主任务 | A0「固定结果」 + B0「状态标识」 | 看见结果 | 补齐闭环 | 价值是否成立 | 基线完成 | 路径证据 | Proposed |

## 5. 当前版本交付与真实性

当前版本使用固定数据验证完整体验。

## 6. 依赖、风险、假设与版本闸门

通过后进入下一阶段。
"""


class ContractTests(unittest.TestCase):
    def run_validator(self, prd: str, roadmap: str) -> subprocess.CompletedProcess[str]:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            prd_path = root / "prd.md"
            roadmap_path = root / "roadmap.md"
            prd_path.write_text(prd, encoding="utf-8")
            roadmap_path.write_text(roadmap, encoding="utf-8")
            return subprocess.run(
                ["python3", str(VALIDATOR), "--prd", str(prd_path), "--roadmap", str(roadmap_path)],
                capture_output=True,
                text=True,
                check=False,
            )

    def assert_passes(self, primary: str, secondary: str = "无") -> None:
        result = self.run_validator(make_prd(primary, secondary), make_roadmap(primary, secondary))
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_c_end_contract_passes(self) -> None:
        self.assert_passes("C端交互产品", "服务编排、AI助手")

    def test_content_contract_passes_without_homepage_or_ai(self) -> None:
        self.assert_passes("内容/产物生产", "内部流程工具")

    def test_internal_contract_passes(self) -> None:
        self.assert_passes("内部流程工具")

    def test_platform_contract_passes(self) -> None:
        self.assert_passes("API/平台")

    def test_service_contract_passes(self) -> None:
        self.assert_passes("服务编排")

    def test_marketplace_contract_passes(self) -> None:
        self.assert_passes("交易/市场")

    def test_hybrid_primary_fails(self) -> None:
        result = self.run_validator(make_prd("混合产品"), make_roadmap("混合产品"))
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("product-shape", result.stderr)

    def test_missing_c_end_route_fails(self) -> None:
        prd = make_prd("C端交互产品").replace(SHAPE_TABLES["C端交互产品"], "缺少用户路径")
        result = self.run_validator(prd, make_roadmap("C端交互产品"))
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("shape:C端交互产品", result.stderr)

    def test_missing_content_contract_fails(self) -> None:
        prd = make_prd("内容/产物生产").replace(SHAPE_TABLES["内容/产物生产"], "缺少生产合同")
        result = self.run_validator(prd, make_roadmap("内容/产物生产"))
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("shape:内容/产物生产", result.stderr)

    def test_missing_internal_contract_fails(self) -> None:
        prd = make_prd("内部流程工具").replace(SHAPE_TABLES["内部流程工具"], "缺少流程合同")
        result = self.run_validator(prd, make_roadmap("内部流程工具"))
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("shape:内部流程工具", result.stderr)

    def test_missing_platform_contract_fails(self) -> None:
        prd = make_prd("API/平台").replace(SHAPE_TABLES["API/平台"], "缺少接入合同")
        result = self.run_validator(prd, make_roadmap("API/平台"))
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("shape:API/平台", result.stderr)

    def test_missing_service_handoff_fails(self) -> None:
        prd = make_prd("服务编排").replace(SHAPE_TABLES["服务编排"], "缺少服务承接")
        result = self.run_validator(prd, make_roadmap("服务编排"))
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("shape:服务编排", result.stderr)

    def test_missing_ai_contract_fails(self) -> None:
        prd = make_prd("C端交互产品", "AI助手").replace(AI_TABLE, "缺少 AI 合同")
        result = self.run_validator(prd, make_roadmap("C端交互产品", "AI助手"))
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("risk:AI", result.stderr)

    def test_future_target_is_not_valid_current_evidence(self) -> None:
        prd = make_prd("内容/产物生产").replace("| 已观察 | 原型记录 |", "| 目标态 | 路线图 |")
        result = self.run_validator(prd, make_roadmap("内容/产物生产"))
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("current-effect", result.stderr)

    def test_missing_assumption_register_fails(self) -> None:
        prd = make_prd("内容/产物生产").replace("| 类型 | 假设或决策 | 状态 | 依据 | 对产品影响 | 确认人/下一步 |", "| 备注 | 内容 |")
        result = self.run_validator(prd, make_roadmap("内容/产物生产"))
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("assumptions", result.stderr)

    def test_unconfirmed_must_be_true_cannot_be_ready(self) -> None:
        prd = make_prd("内容/产物生产").replace("| 必须为真 | 用户需要该结果 | 已确认 |", "| 必须为真 | 用户需要该结果 | 建议假设，待确认 |")
        result = self.run_validator(prd, make_roadmap("内容/产物生产"))
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("approval-readiness", result.stderr)

    def test_unconfirmed_must_be_true_can_remain_not_ready(self) -> None:
        prd = make_prd("内容/产物生产", readiness="否（存在未确认关键假设）").replace("| 必须为真 | 用户需要该结果 | 已确认 |", "| 必须为真 | 用户需要该结果 | 建议假设，待确认 |")
        roadmap = make_roadmap("内容/产物生产").replace("- 是否具备审批条件：是（等待批准）", "- 是否具备审批条件：否（存在未确认关键假设）")
        result = self.run_validator(prd, roadmap)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("WARNING", result.stderr)

    def test_metadata_mismatch_fails(self) -> None:
        roadmap = make_roadmap("内容/产物生产").replace("- 当前交付目的：用户验证", "- 当前交付目的：规模化")
        result = self.run_validator(make_prd("内容/产物生产"), roadmap)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("cross-doc:metadata", result.stderr)

    def test_version_ordinal_mismatch_fails(self) -> None:
        roadmap = make_roadmap("内容/产物生产").replace("R1（第 1 个体验版本）", "R1（第 2 个体验版本）")
        result = self.run_validator(make_prd("内容/产物生产"), roadmap)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("version-code", result.stderr)

    def test_unsourced_numeric_target_fails(self) -> None:
        prd = make_prd("内容/产物生产").replace("用户获得结果并形成继续使用理由。", "任务完成率达到 90%。")
        result = self.run_validator(prd, make_roadmap("内容/产物生产"))
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("numeric-target", result.stderr)


if __name__ == "__main__":
    unittest.main()
