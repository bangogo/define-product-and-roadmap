# 技能架构诊断与重构提案（v4.1.0 → 候选版本）

状态：**待确认的诊断与方案，不是已实施的重构**。本轮未修改技能源码、未改版本、未安装、未发布。
分支：`codex/skill-architecture-review`，基线 `v4.1.0` / `29cf020`。本文件是本轮**唯一当前提案入口**。

## 0. 结论先行

v4.1.0 的真实问题不是“提示词变短了”，而是三件事同时发生：

1. **默认交付格式换成了 HTML，但产品语义校验没有跟过去。** HTML 分支只检查结构、指纹与决定记录；v3.2 已有的需求五要素、形态表、分工、假设同源、数值基线、呈现规则一整套检查，在默认路径下全部不执行。
2. **提示词、脚本、模板 JS 三条控制链各自演化，没有明确的职责边界。** 结果是真实浏览器里导出记录就写错了字段，而现有测试依然全绿。
3. **测试证明的是 mock 与已知负例，不是真实交互。** 现有 Node 冒烟用假 DOM 替身，恰好掩盖了真实 DOM 的取值顺序问题。

建议方向：**不回到 v3.x 的章法约束，也不做重型编排器**；把“格式无关的产品不变量”抽成确定性的内核层，HTML 与 Markdown 都只做适配，恢复 v3.x 值得保留的语义检查，并把真实交互与人工闸门显式化。

## 1. 已执行的证据

| 项 | 结果 | 证据 |
|---|---|---|
| 基线静态检查 | 全通过 | `check_project.py --verify-dist`（72 旧契约 + 11 HTML 契约）、`check_scenarios.py`、Node `interaction_smoke.mjs` |
| 验证器探针 | 14 条观察，其中 8 条“坏样本被接受”、1 条崩溃、1 条误拒 | [validator-results.json](evidence/validator-results.json)、[validator_probe.py](probes/validator_probe.py) |
| 真实浏览器探针 | 桌面 1440 与移动端 390 均复现导出记录字段错位 | [browser-results.json](evidence/browser/browser-results.json)、[browser_probe.mjs](probes/browser_probe.mjs) |
| 该错误记录再校验 | 被验证器拒绝（`决定 D-01 未明确选择`） | 本轮执行 `validate_product_docs.py --prd-html ... --decisions evidence/browser/download-1440.json` |

证据边界：探针使用临时合成副本与合成点击，不编辑技能与 fixture；截图已生成但本轮未做视觉评审；合成操作不等于用户批准。

## 2. 问题清单（按严重度）

### P0-1 默认路径丢失产品语义校验
[validate_product_docs.py:1408-1439](../../skills/define-product-and-roadmap/scripts/validate_product_docs.py) 的 HTML 分支只调用 `validate_html_prd`，并在有 Roadmap 时做 4 个元数据字段与需求 ID 集合比对。以下 v3.2 能力在默认路径完全不执行：`validate_metadata`、`validate_outline`、`validate_universal_tables`、`validate_shape_contracts`、`validate_requirement_blocks`、`validate_separation_of_duties`、`validate_assumptions`、`validate_numeric_targets`、`validate_presentation`、`validate_group_counts`、`validate_window_consistency`、`validate_ai_evaluation`。
影响：单份 HTML PRD 可以没有需求、需求为空、主形态取值非法，仍“验证通过”。

### P0-2 真实导出记录字段错位
[prd-template.html:119](../../skills/define-product-and-roadmap/assets/prd-template.html) 用 `card.querySelector('input[type="radio"]:checked')` 取 choice，会先命中方向组，于是 choice 被写成方向值。
真实浏览器复现：`chosenChoice=确认` → `downloadedChoice=user-review`（1440 与 390 均复现）。该记录随后被验证器拒绝，形成“页面能导出、采纳不了”的闭环。
掩盖原因：[interaction_smoke.mjs:35-40](../../evals/prd-output-spec/interaction_smoke.mjs) 的假卡片对任何 `input` 选择器都按状态返回，不反映真实 DOM 顺序。

### P1-3 检查可被最小改动绕过
流程语义只校验已声明的边：删掉所有 `data-flow-*` 即通过；规则短语检查在整份源码里找，命中自身属性也算通过；迁移表只校验新文档内的旧 ID 与当前需求覆盖，没有基线输入，无法证明旧对象被逐项盘点、删除已获授权、有效内容被保留。

### P1-4 终稿闸门可被自证
visible 字段写“已批准”、“是否具备审批条件”写“否”、决定仍为“修改且未落地”的稿子，都能标“最终版”并通过。哈希只绑定内容，不能证明真人身份或批准；脚本也无法约束其调用路径之外的 Agent 行为。

### P1-5 健壮性与入口缺口
数组型字段导致 `TypeError` 而非结构化拒绝；无害的嵌套 `div` 会让解析器误判决定卡结束（`html_prd_validator.py:195-198`）产生误拒；没有独立的单份 Markdown PRD 校验入口（`--prd` 强制要求 `--roadmap`）。

### P2-6 契约拖拽与漂移
`roadmap-contract.md:30,50,207,237` 仍引用已从 `prd-contract.md` 删除的“12 条呈现规则／场景矩阵／第 7 章”；`intent-and-scenario-contract.md:207` 使用 `Proposed`，而 HTML 状态枚举是中文；`quality-rubric.md:117-119` 的专项审查依赖仓库 `spec.md` 与案例草稿史，不在打包技能内。

### P2-7 效率证据不足
v3.1/v3.2 的 `SKILL.md` 为 179/195 行，v4.1 为 40 行；references 字符数 20692/26348/26386。这是字符数不是 token，入口变短本身不构成“更高效”的证据，需要用同一输入的真实轨迹比较。

## 3. v3.x 能力留存矩阵

| v3.x 能力 | 判定 | 理由 |
|---|---|---|
| 证据分层（已确认决定／已观察／文档记载／历史／候选／待调研） | 保留 | v4.1 仍在，是证据边界的核心 |
| 形态／风险区分、价值瓶颈驱动优先级、可观察验收 | 保留 | 仍在契约与评分表 |
| 复用边界、PRD 与 Roadmap 分工、四视角评审 | 保留 | 仍在，且已区分自审与独立评审 |
| 需求五要素、形态表、假设同源、数值基线、呈现规则等确定性检查 | 恢复 | v3.2 有实现，v4.1 默认路径没有 |
| 固定 7 章目录 | 不恢复 | 与“章节随读者问题与既有结构确定”冲突，v4.1 决策合理 |
| 强制临时 Roadmap | 不恢复 | spec.md 明确不为单份 PRD 造临时 Roadmap |
| 每个 B 场景必问扩展意图、施工期 ≥1 天观察等通用化约束 | 不恢复 | 只在案例成立，不应推广为通用默认值 |
| 文档状态英文枚举 | 不恢复 | HTML 已定中文枚举，改为统一 intent 契约的残留英文 |

## 4. 架构选项

| 选项 | 做法 | 优点 | 代价 |
|---|---|---|---|
| A 局部加固 | 在现有 `html_prd_validator.py` 加语义检查，修模板与拖拽 | 改动小、风险低 | 语义规则仍按格式各写一遍，Markdown/HTML 继续漂移 |
| **B 内核层 + 适配层（推荐）** | 抽出格式无关的产品不变量内核；HTML/Markdown 只做适配与解析；脚本接管确定性部分 | 规则单源、默认路径恢复语义深度、可增量迁移 | 需要重构验证器与部分 reference |
| C 重型编排器 | 多 Agent 流水线 + 全 JSON 中间态 + 脚本编排 | 理论上可控 | 与“保留产品判断在 AI、确定性在脚本”相比过重，且 prose 全 JSON 化损害可读性 |

推荐 B，并按阶段落地：先修缺陷，再迁内核，最后做真实 A/B 比较，避免在未验证时一次性重写。

## 5. 目录结构对比（前 → 后）

### 当前（v4.1.0）
```text
skills/define-product-and-roadmap/
  SKILL.md                     40 行，路由 + 工作流 + 边界
  references/
    intent-and-scenario-contract.md
    prd-contract.md
    roadmap-contract.md         引用已删除的“12 条呈现规则”
    html-prd-workflow.md
    quality-rubric.md           依赖仓库 spec.md
    revision-lessons.md
  scripts/
    validate_product_docs.py    1469 行，双入口
    html_prd_validator.py       445 行
    stamp_html_prd.py           23 行
    test_contract.py / test_html_contract.py
  assets/prd-template.html      含导出脚本（P0-2 缺陷）
```

### 候选（B 选项，示意）
```text
skills/define-product-and-roadmap/
  SKILL.md                     入口、路由、人工闸门、脚本入口
  references/
    product-invariants.md      格式无关的不变量：ID、落位、证据状态、验收、终稿闸门
    intent-and-scenario-contract.md
    prd-contract.md            产品语义（格式无关）
    roadmap-contract.md        去掉对已删除呈现规则的引用
    html-prd-workflow.md       只留 HTML 特有：结构锚点、SVG 语义、决定卡
    quality-rubric.md          去掉仓库专属依赖
    revision-lessons.md
  scripts/
    invariants/                内核：不变量检查（被所有格式复用）
    adapters/                  html 解析与 markdown 解析，输出同一中间结构
    validate_product_docs.py   薄 CLI：选适配器 → 跑内核 → 汇总
    stamp_html_prd.py
    check_project.py
    tests/                     契约测试 + 真实浏览器探针
  assets/prd-template.html     修复字段取值；尽量与内核共享枚举
```

要点：**一个入口、一份不变量、按格式适配**。不新增 README/CHANGELOG 之类附属文档；不为拆分而拆分文件。

## 6. 控制链条对比

| 环节 | 现在主要由谁控制 | 候选由谁控制 | 迁移原因 |
|---|---|---|---|
| 元数据齐全与一致性 | AI 写、脚本只查存在性 | 脚本查枚举、跨处一致、与 Roadmap 对齐 | 纯机械一致性，脚本不会疲劳 |
| 版本与内容指纹 | 脚本计算 + AI 记得重盖 | 脚本计算并在交付前断言未过期 | 忘记重盖会静默失效 |
| 需求 ID 稳定与唯一 | AI 维护、脚本查重复 | 脚本比对基线并报告改名／删除／新增 | 需要跨修订一致性，靠记忆不可靠 |
| 迁移表逐项覆盖 | AI 写表、脚本查字段 | 脚本用基线 diff 检查覆盖与删除授权 | 旧对象是否被盘点，机械可判定 |
| 决定记录与方向的绑定 | 模板 JS + 脚本校验 | 模板 JS 正确取值 + 脚本拒绝任何不匹配记录 | P0-2 证明 JS 取值会错且被 mock 掩盖 |
| 终稿与审批条件 | AI 写状态、脚本查记录存在 | 脚本拒绝与可见状态矛盾的记录；人工批准仍由人给出 | 可机械判定矛盾，真实身份与授权不能脚本代劳 |
| 需求五要素、形态表、假设同源、数值基线 | HTML 路径无检查 | 脚本查可枚举部分，AI 用评分表做语义判断 | 兼顾深度与可维护性 |
| 图文一致、SVG 几何、窄屏与打印 | AI 自查（常缺证据） | 脚本做可测的容纳与阅读顺序检查，缺浏览器时如实写“未验证” | 可用 `getBBox`/媒体查询机械测量 |
| 产品判断：用户、价值瓶颈、形态选择、取舍 | AI | AI | 不应当脚本化 |
| 是否标最终版、进入哪个闸门 | 人 | 人 | 授权只能由人作出 |

## 7. 分阶段验收

| 阶段 | 交付 | 可核验的通过标准 |
|---|---|---|
| 1 缺陷修复 | 模板导出字段修复、mock 换成真实 DOM 探针、解析器崩溃改结构化拒绝、嵌套 div 误拒修复、单份 Markdown 入口 | 真实浏览器导出记录等于用户选择；表格中 8 条坏样本被拒绝、1 条误拒转为通过、1 条崩溃转为结构化错误 |
| 2 内核层 | 不变量内核 + HTML/Markdown 适配，v3.2 语义检查在 HTML 路径恢复 | 同一份 HTML PRD 缺需求／空需求／非法形态／剥离流程元数据全部被拒；旧 Markdown 路径回归不退化 |
| 3 契约收口 | 引用拖拽修复、状态枚举统一、评分表去掉仓库专属依赖 | 全仓检索无悬空引用；打包技能内引用均可解析 |
| 4 真实 A/B | 同一原始输入跑 v3.2、v4.1、候选，盲评实际产物 | 报告遗漏项、无支撑断言、修订保留度、中断次数、产物可读性、运行轨迹成本；不用承诺的百分比 |

证据分级贯穿始终：静态／确定性、语义自审或独立评审、真实渲染、真实宿主运行、用户确认，五层不得互相冒充。

## 8. 待你拍板的决定

1. **产物权威源**：保持“HTML 即权威源”只修缺陷，还是改为“结构化/Markdown 源 + 渲染成 HTML”？前者改动小，后者更利于脚本校验但多一层产物。
2. **脚本语义化的边界**：需求五要素、形态表、假设同源这类检查，做到“能枚举即脚本”，还是保留为 AI 评分项？
3. **分支管理**：所有 `codex/*` 功能分支历史都已在 `main`（无待合并提交）；两个工作树仍有未提交的 v4.0 草稿，是否在本次一并处理。

## 9. Git 分支现状（本轮核对）

- `main` 与 `origin/main` 同为 `29cf020`；标签 `v3.1.0`、`v3.2.0`、`v4.0.0`、`v4.1.0` 均指向既有提交。
- `codex/prd-output-spec`、`codex/prd-skill-upgrade`、`codex/worktree-*`（4505/76ad/ebc0/branch-display-fix）历史均已被 `main` 包含，**没有需要合并的提交**。
- 未提交改动：`/Users/helloban/Documents/01 产品需求与产品路线图技能`（`codex/prd-skill-upgrade`）与 `/Users/helloban/.codex/worktrees/76ad/...`（`codex/worktree-76ad-recovery`）各有同一批 v4.0 草稿；本轮未改动、未清理。
- `import/ai-content-copilot-docs` 未被 `main` 包含，内容是独立业务案例材料，不在技能主线。
- 本轮新建 `codex/skill-architecture-review`，仅含 `docs/architecture-review/` 诊断材料，未提交。
