# Product Requirements Contract

## Contents

1. Universal PRD structure
2. Universal tables
3. Product-shape contracts
4. Risk contracts
5. Approval readiness

## Universal PRD structure

Use this complete product-facing order. Put executive conclusions inside the first four sections; do not add a preceding summary section.

1. `产品定位与目标`: metadata, product promise, goal, non-goal, and current decision.
2. `目标用户与核心问题`: product user, context, current workaround, unmet need, and priority.
3. `当前产品形态、效果与核心缺口`: present state, evidence, shortest value path, truth boundary, and first bottleneck.
4. `产品价值与价值循环`: user result, business result, repeated-use reason, evidence loop, and stop condition.
5. `参考、复用与项目责任`: references, existing assets, external services, license/provenance, and project-owned additions.
6. `主要体验或生产合同`: primary shape, material secondary shapes, states, and recovery.
7. `产品能力与优先级`: lasting modules, responsibility, ownership, state, recovery, and priority rationale.
8. `产品需求与验收`: stable requirements with product and technical acceptance boundaries.
9. `数据、服务、状态、权限、质量与恢复边界`: cross-cutting contracts that materially affect value.
10. `当前版本范围与真实性`: included/excluded scope and implementation truth.
11. `成功、风险、假设与下一闸门`: measurement, risk controls, assumption register, status, reviewer, and next gate.

A requested PRD means the full contract. Use a shorter brief only when the user explicitly asks for one. Keep discovery notes, route rationale, raw interviews, and rejected directions outside the formal PRD.

## Universal tables

### Current effect

| 观察对象 | 当前效果 | 证据状态 | 证据来源 | 当前缺口 |
|---|---|---|---|---|

Use only the canonical truth labels from the intent contract. State `尚未验证` rather than filling a gap with an inferred claim.

### Reference, reuse, and project responsibility

| 来源 | 版本/日期 | 许可状态 | 负责什么 | 已证实能力 | 产品映射 | 复用决策 | 项目补充 | 用户价值 | 证据边界 |
|---|---|---|---|---|---|---|---|---|---|

Use consistent decisions:

- `「方法借鉴」`: apply a method while the project owns the resulting rules;
- `「原样复用」`: retain a working project capability and build only the named connection;
- `「直接复用」`: call a pinned capability through a bounded adapter after source, version, license, interface, and exclusions are known;
- `「参考复用」`: use structure, constraints, or fixtures as design and test input;
- `「新建」`: own contract, implementation, tests, and maintenance.

Unknown license or source revision blocks `「直接复用」` but does not block `「方法借鉴」` when independently re-created and legally safe. Never infer a license from repository location, access, or project ownership; write `未声明` when evidence does not state it. Map each module responsibility to one reuse decision and one project-owned addition.

### Product capability

Define lasting modules as `A「名称」`:

| 产品模块 | 责任 | 输入 | 用户可见输出 | 负责人 | 主要状态 | 失败与恢复 | 当前优先级及依据 |
|---|---|---|---|---|---|---|---|

Do not present demo controllers, narration, reset tools, approval decks, database tables, or internal classes as product modules. Put them under current-version delivery support or the technical Spec.

### Requirements

| 编号 | 优先级 | 模块 | 产品要求 | 用户可见结果 | 业务规则 | 技术验收边界 | 证据状态 |
|---|---|---|---|---|---|---|---|

Use unique IDs such as `P0-01「要求名称」`. Every requirement must map to a defined product module. Acceptance must describe observable state, contract, or artifact evidence; “功能完成” and “测试通过” are insufficient alone.

### Current-version truth

| 层面 | 当前实现 | 真实性 | 用户可见标识 | 后续替换 |
|---|---|---|---|---|

Cover every applicable layer: frontend or task surface, backend/process, data/input, model, external service, manual support, output quality, and publication/transaction state.

### Success model

| 成功信号 | 对应用户价值 | 当前基线 | 本版判定 | 证据方法 | 结论状态 |
|---|---|---|---|---|---|

Use `未知，需建立基线` when evidence is absent. Label numeric targets as confirmed, evidence-supported, proposed, or pending validation. Do not invent thresholds.

### Assumptions

| 类型 | 假设或决策 | 状态 | 依据 | 对产品影响 | 确认人/下一步 |
|---|---|---|---|---|---|

Publish the same material rows in the Roadmap.

## Product-shape contracts

Load the primary shape and only the secondary shapes that materially affect value delivery.

### C-end interaction

Describe page inventory, information architecture, entry points, mobile/accessibility, and the core route:

| 场景 | 进入页面 | 页面呈现 | 用户动作 | 状态变化 | 可见结果 | 失败与恢复 |
|---|---|---|---|---|---|---|

Define loading, empty, error, permission, cancellation, return, repeated-use, and accessibility states where relevant. Use clickable route evidence for version exits; static screens alone prove only presentation.

### Content or artifact production

| 阶段 | 输入 | 处理责任 | 中间/最终产物 | 质量门 | 失败与恢复 | 证据 |
|---|---|---|---|---|---|---|

Include provenance, immutable revisions, human review, artifact usability, rework, and output separation. Measure quality, throughput, cycle time, and rework only after a baseline exists.

### Internal workflow

| 角色 | 触发 | 处理步骤 | 交接/审批 | 可见结果 | 异常恢复 | 审计证据 |
|---|---|---|---|---|---|---|

Define ownership, queue state, permissions, escalation, responsibility transfer, and unknown outcomes. Describe UI only where it changes the operator task.

### API or platform

| 使用者 | 接入入口 | 首次成功任务 | 接口/合同 | 可见结果 | 失败恢复 | 采用证据 |
|---|---|---|---|---|---|---|

Include examples, docs/SDK boundaries, credentials, compatibility, deprecation, self-service, reliability, and time to first value. An endpoint existing is not consumer first-success evidence.

### Service orchestration

| 服务场景 | 用户触点 | 承接方 | 服务动作 | 状态回流 | 失败恢复 | 责任边界 |
|---|---|---|---|---|---|---|

Cover online/offline handoffs, provider truth, support, cancellation, unknown external outcomes, reconciliation, and return to the originating task. A link without provider responsibility or return state is not a service outcome.

### Marketplace or transaction

| 角色方 | 发现/匹配 | 信任保障 | 交易动作 | 履约结果 | 争议恢复 | 证据 |
|---|---|---|---|---|---|---|

Define both sides' value, supply/demand constraints, identity and fraud controls, payment/settlement, fulfillment, cancellation, refund, and dispute ownership.

## Risk contracts

When `风险修饰项` is not `无`, include one row per modifier:

| 风险修饰项 | 触发场景 | 潜在损害 | 预防控制 | 用户控制 | 失败/未知状态 | 审计证据 | 发布/审批门 |
|---|---|---|---|---|---|---|---|

### AI

Also include:

| 场景 | 触发入口 | 携带上下文 | 助手响应 | 关键追问 | 行动边界 | 可见结果 | 回退 |
|---|---|---|---|---|---|---|---|

Define model role, human control, uncertainty, feedback, correction, permissions, evaluation, and non-AI fallback. A plausible answer, transcript, or successful invocation is not semantic or production proof.

### Sensitive data, external writes, publishing, transactions, and high-stakes decisions

Name data class, consent, authority, confirmation point, idempotency or deduplication where relevant, external responsibility, unknown-result state, reconciliation, support, audit, reversal, and escalation. A successful local request does not prove the external outcome.

### Third-party reuse

Record pinned source, revision, license status, callable boundary, exclusions, provenance, update policy, adapter ownership, security review, and current proof. Repository HEAD movement does not prove the reused subdirectory changed.

## Approval readiness

Use canonical document statuses: `Draft`, `Proposed`, `Review Candidate`, `Approved`, or `Superseded`.

Set `是否具备审批条件：否（原因）` when any `必须为真` item is unresolved or denied, a high-risk external fact lacks authority, the selected direction is still mixed, or material current-state evidence conflicts. `Approved` requires `是否具备审批条件：是（已批准）` and an explicit approval record. Approval activates only the named next gate.
