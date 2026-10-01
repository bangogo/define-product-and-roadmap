# `define-product-and-roadmap` v4.1.0 → v5.0.0 升级方案

状态：**待确认的执行方案**。本轮只做分支管理与诊断，未改动技能源码，未改版本号，未安装或发布。
分支：`codex/skill-architecture-review`；基线 `v4.1.0` / `29cf020`。
诊断依据见 [README.md](README.md)（唯一问题诊断入口）。

## 0. 已确认与待确认

| 编号 | 决定 | 状态 |
|---|---|---|
| D-01 | 产物权威源继续以 HTML 为唯一权威源稿，不引入结构化中间源 | **已确认** |
| D-02 | 语义检查脚本化的粒度 | **待你选择**，候选见第 4 节 |
| D-03 | 两个工作树的 v4.0 草稿一并处理 | **已执行**，见第 6 节 |

## 1. 目标

1. **同一份 PRD 无论走哪条交付路径，都接受同一套产品不变量检查。** 现在 HTML 是默认路径，却只做结构校验；Markdown 旧路径反而跑完整语义校验。这个倒挂必须消除。
2. **确定性部分交给脚本，判断部分留给 AI，授权留给人类。** 减少“提示词要求 AI 记住”的机械约束，让机械约束可执行、可复现。
3. **修掉真实交互缺陷。** 真实浏览器里导出的决定记录字段错位，而现有测试全绿，说明验证体系没有覆盖真实行为。
4. **保留 v4.1 的正确决策。** 章节随读者问题与既有结构确定、单份 PRD 不造临时 Roadmap、不把案例约束推广为通用默认值——这些不回退。
5. **让回归可复现。** 探针脚本化，任何人能一键复现本轮所有观察。

非目标：不重写案例 PRD；不改动 Roadmap 契约语义；不引入多 Agent 编排器；不把 prose 全量 JSON 化；不改 HTML 为默认权威源这一决定。

## 2. 问题（诊断结论）

### P0-1 默认路径丢失产品语义校验
`validate_product_docs.py:1408-1439` 的 HTML 分支只调用 `validate_html_prd`，有 Roadmap 时再比对 4 个元数据字段与需求 ID 集合。v3.2 已有的 `validate_metadata`、`validate_outline`、`validate_universal_tables`、`validate_shape_contracts`、`validate_requirement_blocks`、`validate_separation_of_duties`、`validate_assumptions`、`validate_numeric_targets`、`validate_presentation`、`validate_group_counts`、`validate_window_consistency`、`validate_ai_evaluation` 在默认路径全部不执行。
实测：没有需求、需求内容为空、主形态取值非法的 HTML PRD 都“验证通过”。

### P0-2 真实导出记录字段错位
`assets/prd-template.html:119` 用 `card.querySelector('input[type="radio"]:checked')` 取 choice，先命中方向组。真实浏览器复现：选「确认」却导出 `choice: "user-review"`（1440 与 390 均复现），该记录随后被自己的验证器拒绝。
掩盖原因：`evals/prd-output-spec/interaction_smoke.mjs:35-40` 的假卡片对任何 input 选择器都按状态返回，不反映真实 DOM 顺序。

### P1-3 检查可被最小改动绕过
流程语义只校验已声明的边（删掉 `data-flow-*` 即通过）；规则短语检查在整份源码里找，命中自身属性也算通过；迁移表只校验新文档内部的旧 ID 与当前需求覆盖，没有基线输入，无法证明旧对象被逐项盘点、删除获得授权、有效内容被保留。

### P1-4 终稿闸门可被自证
可见「是否具备审批条件＝否」、决定仍为「修改且未落地」的稿子都能标最终版并通过。哈希只绑定内容，不能证明真人身份与批准。

### P1-5 健壮性与入口缺口
数组型字段触发 `TypeError` 而非结构化拒绝；无害嵌套 `div` 让解析器误判决定卡结束（`html_prd_validator.py:195-198`）造成误拒；没有独立的单份 Markdown PRD 校验入口（`--prd` 强制要求 `--roadmap`）。

### P2-6 契约引用拖拽
`roadmap-contract.md:30,50,207,237` 引用已从 `prd-contract.md` 删除的「12 条呈现规则／场景矩阵／第 7 章」；`intent-and-scenario-contract.md:207` 仍用 `Proposed`，与 HTML 的中文状态枚举不一致；`quality-rubric.md:117-119` 依赖仓库 `spec.md` 与案例草稿史，不在打包技能内。

### P2-7 效率证据不足
`SKILL.md` 由 v3.1 的 179 行、v3.2 的 195 行降到 40 行。这是字符数不是 token，入口变短本身不构成“更高效”的证据，需要同一输入的真实轨迹比较。

## 3. 改动点

### 阶段 1：缺陷修复（无架构改动，可独立发布为 4.1.1）

| 编号 | 改动 | 文件 |
|---|---|---|
| 1.1 | 决定卡按 `name` 精确取值：方向与 choice 分别用 `[name="<id>-direction"]:checked` 与 `[name="<id>"]:checked`，并导出前校验 | `assets/prd-template.html` |
| 1.2 | 用真实浏览器探针替换假 DOM mock；保留 mock 只做无浏览器环境的降级路径 | `evals/prd-output-spec/interaction_smoke.mjs`、`docs/architecture-review/probes/browser_probe.mjs` |
| 1.3 | 结构化拒绝取代异常：记录字段类型不合法返回错误而非 `TypeError` | `scripts/html_prd_validator.py` |
| 1.4 | 修嵌套 `div` 误判决定卡结束的解析缺陷 | `scripts/html_prd_validator.py:195-198` |
| 1.5 | 新增单份 Markdown PRD 校验入口（`--prd` 不再强制 `--roadmap`） | `scripts/validate_product_docs.py:157-175` |
| 1.6 | 终稿闸门：可见「不具备审批条件」、存在未落地的修改决定时拒绝标最终版 | `scripts/html_prd_validator.py` |

### 阶段 2：不变量内核 + 适配层（架构改动，目标 5.0.0）

目录结构（当前 → 候选）：

```text
当前                                   候选
scripts/                               scripts/
  validate_product_docs.py  1469 行      validate_product_docs.py   薄 CLI
  html_prd_validator.py      445 行      invariants/   格式无关不变量
  stamp_html_prd.py           23 行      adapters/     html 解析 / markdown 解析
  test_contract.py                      stamp_html_prd.py
  test_html_contract.py                 check_project.py
                                        tests/        契约测试 + 真实浏览器探针
references/                            references/
  prd-contract.md（产品语义）            product-invariants.md  新增：格式无关不变量
  html-prd-workflow.md（HTML 细节）      prd-contract.md        只留产品语义
  roadmap-contract.md（引用已失效）      roadmap-contract.md    修引用
  quality-rubric.md（依赖仓库 spec）     quality-rubric.md      去掉仓库专属依赖
```

关键约束：**一个入口、一份不变量、按格式适配**；不新增 README/CHANGELOG 之类附属文档；不为拆分而拆分文件。

| 编号 | 改动 | 说明 |
|---|---|---|
| 2.1 | 抽出 `invariants/` | ID 稳定与唯一、证据状态枚举、验收可观察性、终稿闸门、迁移覆盖等，格式无关 |
| 2.2 | 抽出 `adapters/` | HTML 与 Markdown 解析后输出同一中间结构，供内核消费 |
| 2.3 | `validate_product_docs.py` 变薄 CLI | 选适配器 → 跑内核 → 汇总，双入口保留 |
| 2.4 | 新增 `--baseline` 参数 | 迁移表覆盖、删除授权、有效内容保留才能真正可判 |
| 2.5 | 恢复 v3.2 语义检查到 HTML 路径 | 按第 4 节选定的粒度落地 |
| 2.6 | 新增 `references/product-invariants.md` | 枚举与不变量的唯一权威定义，模板与脚本共享 |

### 阶段 3：契约收口

| 编号 | 改动 |
|---|---|
| 3.1 | `roadmap-contract.md` 去掉对已删除「12 条呈现规则／场景矩阵／第 7 章」的引用，改为指向现行契约 |
| 3.2 | `intent-and-scenario-contract.md:207` 的 `Proposed` 与 HTML 中文状态枚举统一 |
| 3.3 | `quality-rubric.md` 的 HTML 专项审查去掉对仓库 `spec.md` 与案例草稿史的依赖，改为可独立使用的通用清单 |
| 3.4 | `SKILL.md` 补：脚本入口、不变量引用、五层证据报告要求 |

### 控制链条迁移（谁控制什么）

| 环节 | 现在 | 候选 | 原因 |
|---|---|---|---|
| 元数据枚举、跨处一致 | AI 写、脚本只查存在性 | 脚本查枚举与一致 | 纯机械一致性 |
| 指纹是否过期 | AI 记得重盖 | 脚本在交付前断言未过期 | 忘记重盖会静默失效 |
| 需求 ID 稳定唯一、跨修订一致 | AI 维护、脚本查重复 | 脚本比对基线并报告改名/删除/新增 | 需跨修订一致性 |
| 迁移表逐项覆盖与删除授权 | AI 写表、脚本查字段 | 脚本用基线 diff 判定 | 旧对象是否被盘点可机械判定 |
| 决定记录与方向绑定 | 模板 JS + 脚本校验 | JS 正确取值 + 脚本拒绝不匹配记录 | P0-2 已证明 JS 会错 |
| 终稿与审批条件 | AI 写状态、脚本查记录存在 | 脚本拒绝与可见状态矛盾的记录 | 矛盾可机械判定 |
| 需求五要素、形态表、假设同源、数值基线 | HTML 路径无检查 | 脚本查可枚举部分（粒度见第 4 节） | 兼顾深度与可维护性 |
| 图文一致、SVG 几何、窄屏与打印 | AI 自查，常缺证据 | 脚本做可测量部分；无浏览器时如实写「未验证」 | 可用 `getBBox`/媒体查询测量 |
| 产品判断：用户、瓶颈、形态、取舍 | AI | AI | 不应脚本化 |
| 是否标最终版、进入哪个闸门 | 人 | 人 | 授权只能由人作出 |

## 4. 语义检查粒度：四个候选（待你选择）

| 候选 | 覆盖 | 误报风险 | 工作量 | 说明 |
|---|---|---|---|---|
| **S1 最小** | 元数据枚举与一致、指纹过期、ID 唯一与跨修订稳定、决定记录绑定、终稿矛盾 | 低 | 小 | 只修“能 100% 判定”的部分，不碰语义 |
| **S2 推荐** | S1 ＋ 需求五要素与验收可观察性、形态表存在性、证据状态枚举、假设同源、数值基线须有采集动作、迁移表覆盖与删除授权（需基线输入） | 中低 | 中 | 把 v3.2 已实现的确定性检查接回默认路径；误报可用 warn 分级收敛 |
| S3 更严 | S2 ＋ 跨章重复与单源化、图文同名、短语级检查、SVG 几何测量、窄屏与打印容纳 | 中高 | 大 | 需要警告分级与豁免机制；几何测量依赖浏览器，缺环境时只能标未验证 |
| S4 全脚本化 | S3 ＋ 把质量评分表也脚本化 | 高 | 很大 | 不推荐：评分需要产品判断，脚本化会把“看起来完整”误判为“可用于决策” |

推荐 **S2**，并把 S3 中可测量的部分（SVG 几何、窄屏与打印）先以警告形式试运行一个版本，确认误报可控再升为错误。

## 5. 预期与验证方案

### 5.1 预期效果（可核验，不是承诺百分比）

| 维度 | 现在 | 升级后预期 |
|---|---|---|
| 默认路径语义深度 | 缺需求/空需求/非法形态均通过 | 全部被拒（按选定粒度） |
| 真实交互正确性 | 导出记录字段错位 | 导出记录等于用户选择 |
| 测试有效性 | mock 掩盖真实 DOM 行为 | 真实浏览器探针为默认，mock 仅降级 |
| 健壮性 | 数组字段崩溃、嵌套 div 误拒 | 结构化拒绝、误拒消失 |
| 旧路径 | Markdown 完整校验 | 回归不退化（72 旧契约测试保持通过） |
| 效率 | 无证据 | 同一输入的真实轨迹对比，报告 token/耗时，不用承诺数值 |

### 5.2 分阶段验收

| 阶段 | 通过标准 |
|---|---|
| 1 缺陷修复 | 真实浏览器（1440 与 390）导出记录等于用户选择；14 条探针中 8 条坏样本被拒、1 条误拒转通过、1 条崩溃转结构化错误；单份 Markdown 可独立校验 |
| 2 内核层 | 同一份 HTML PRD 的坏样本全部被拒；72 个旧契约测试与 11 个 HTML 契约测试保持通过；`--baseline` 能检出未盘点旧对象与未授权删除 |
| 3 契约收口 | 全仓检索无悬空引用；打包技能内引用均可解析；`check_project.py --verify-dist` 通过 |
| 4 真实 A/B | 同一原始输入跑 v3.2、v4.1、候选三版，盲评实际产物 |

### 5.3 A/B 比较方法

同一组原始输入（含至少一次增量修订与一次重写迁移），三个版本各自产出，由未参与生成的评审者盲评：

- 遗漏项数量（用户明确要求但未落位）
- 无支撑断言数量（把候选写成已运行、把目标写成现状）
- 修订保留度（旧有效内容是否被保留或说明去向）
- 中断次数（需要回头向用户追问的次数）
- 产物可读性（产品经理/业务负责人视角定位决策证据的时间）
- 运行轨迹成本（token、耗时、工具调用次数）

不使用指南文档中承诺的百分比作为证据；只报告实测数字与边界。

### 5.4 五层证据报告（贯穿始终）

| 层 | 内容 | 不能冒充 |
|---|---|---|
| 静态/确定性 | 脚本校验结果 | 不能写成语义通过 |
| 语义自审或独立评审 | 评分表与发现分级表 | 自审不能称独立 |
| 真实渲染 | 浏览器测量与截图 | 截图只证明该尺寸显示 |
| 真实宿主运行 | 宿主调用轨迹 | 缺轨迹即写未验证 |
| 用户确认 | 对确切版本内容与视觉的认可 | 导出记录或静态通过不等于确认 |

## 6. 分支与工作树处理（已执行）

核对结果：

- `main` 与 `origin/main` 同为 `29cf020`；`v3.1.0`/`v3.2.0`/`v4.0.0`/`v4.1.0` 标签均指向既有提交。
- `codex/prd-output-spec`、`codex/prd-skill-upgrade`、`codex/worktree-*`（4505/76ad/ebc0/branch-display-fix）用 `git merge-base --is-ancestor` 逐一核对，**历史全部已被 `main` 包含**，没有需要合并的提交。
- `import/ai-content-copilot-docs` 未被 `main` 包含，内容是独立业务案例材料，不属于技能主线，未并入。

已执行：

1. `/Users/helloban/Documents/01 产品需求与产品路线图技能`（`codex/prd-skill-upgrade`）的 14 项未提交 v4.0 草稿提交为快照 `82994ea`。
2. `/Users/helloban/.codex/worktrees/76ad/...`（`codex/worktree-76ad-recovery`）的同一批草稿提交为快照 `bb2375a`（两份内容字节一致，逐文件哈希已核对）。
3. 主目录（也是主工作树）从 `codex/prd-skill-upgrade` 切回 `main`，状态干净，README 已回到 4.1.0 版本。

保留未动的：`1648`、`4505`、`ebc0`、`5658` 四个工作树。它们均干净（无未提交改动），且历史已被 `main` 包含，但属于其他任务的检出，本轮未删除。归档工具只作用于本任务挂载的工作树，因此未强行清理。

下一步可选：确认后删除上述四个已被 `main` 包含且干净的工作树与对应分支指针；历史提交与版本标签保留。

## 7. 风险与边界

- 阶段 2 是破坏性重构：`validate_product_docs.py` 的 CLI 参数与错误文案可能变化，需同步更新 `SKILL.md`、`check_project.py` 与测试。
- 语义检查越深，误报越高；所有新增检查先以警告运行一个版本，观察真实误报再决定是否升为错误。
- 脚本无法约束其调用路径之外的 Agent 行为；终稿批准与下一闸门授权仍必须由人给出。
- 真实浏览器探针依赖可用浏览器；缺环境时如实写「未验证」，不得把静态检查写成渲染通过。
