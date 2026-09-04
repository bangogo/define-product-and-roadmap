# 定义产品与路线图 (define-product-and-roadmap)

> 给产品经理和业务负责人：把“这个产品到底成不成立”从拍脑袋，变成一份**证据驱动的产品契约**——说清“谁获得价值、现在能证明什么、第一个瓶颈在哪、哪个证据能解锁下一版”，并明确标出它**现在是否已具备审批条件**。

![version](https://img.shields.io/badge/version-3.2.0-blue)
![platform](https://img.shields.io/badge/platform-Claude%20Code%20%7C%20Codex%20%7C%20WorkBuddy-green)
![license](https://img.shields.io/badge/license-MIT-orange)
![python](https://img.shields.io/badge/validator-Python%203-blue)

**目录**

- [1. 这是什么](#1-这是什么)
- [2. 它怎么工作 & 会主动问你什么](#2-它怎么工作--会主动问你什么)
- [3. 三平台一键安装](#3-三平台一键安装)
- [4. 文件结构速览](#4-文件结构速览)
- [5. 为什么不一样](#5-为什么不一样)
- [6. 版本与发布工作流 / 质量门](#6-版本与发布工作流--质量门)
- [7. 贡献 / 许可](#7-贡献--许可)

---

## 1. 这是什么

一句话：**它产出一份“产品契约”——即产品要成立，必须说清且彼此对齐的那组判断（谁获得价值、现在能证明什么、第一个瓶颈在哪、哪个证据解锁下一版），而不是“代码要怎么写”。** 大多数 AI 技能是技术任务导向（生成代码、审查、测试、部署）；本技能是**产品契约导向**——产出一份可读的 PRD + 体验路线图（Roadmap），让业务、产品、体验、技术四方对“现在到底做到了哪一步”达成一致。

**四种操作，覆盖产品文档的全生命周期：**

| 操作 | 何时用 | 会改动文件吗 |
|---|---|---|
| **创建** create | 从零产出一份对齐的 PRD + Roadmap，基于项目现有证据 | 创建新文件 |
| **仅审计** audit only | 只报告现有 PRD/Roadmap 的问题与修复建议 | **不改文件** |
| **重写** rewrite | 按最新证据重写，保留原件并给出变更摘要 | 保留原件 + 另出新版 |
| **对齐** align | 调和已有的 PRD/Roadmap 对，使其元数据与契约一致 | 只触碰必需文件 |

**适合的场景：**

- **产品文档类：** PRD / 产品需求文档 / MVP / 体验版本 / 当前效果
- **产品形态类：** 产品价值 / 产品形态 / 用户路径 / 内容·产物生产 / 内部工作流 / API·平台 / 服务编排 / marketplace / AI 助手
- **决策类：** 复用决策 / 风险边界 / 假设确认 / 审批条件评估
- **项目阶段：** 0→1 新产品（场景 A）与存量产品迭代（场景 B）**同一套契约、按场景变形**（见下节）

**不要用于：** 单纯的工程任务清单、技术架构图、营销发布计划、仅限代码实现的评审——除非你**同时**需要一份产品契约。

---

## 2. 它怎么工作 & 会主动问你什么

### 产出什么：两个场景，一套契约

一对**元数据完全对齐**的 Markdown 文档：一份 PRD（`product-requirements.md`）+ 一份体验路线图（`product-roadmap.md`）。可以落成文件，也可以在对话里直接交付。仅审计模式只给报告、不动文件。

起草前技能先从证据判定**适用场景**（写入元数据第 8 字段 `适用场景`），两场景共用同一套 7 章/6 章骨架、按维度矩阵变形：

| | 场景 A（0→1 新产品） | 场景 B（存量迭代） |
|---|---|---|
| **何时触发** | 产品还没有可观察的真实使用（证据阶段为想法 / 仅有文档 / 静态设计 / 交互原型） | 已有有限真实使用或线上运行 |
| **现状章（PRD §2）** | 变形：问题假设与冷启动（没有“当前效果实测”，写的是假设与风险） | 实测现状：当前效果表（观察对象/当前效果/证据状态/证据来源/当前缺口） |
| **复用章（PRD §6）** | 变形：外部依赖注册（依赖/用途/可用性/许可状态/失败影响） | 复用决策注册（原样复用/直接复用/参考复用/方法借鉴/新建） |
| **R0 基线（Roadmap）** | 省略——首个版本即 R1，真值表显式全为“尚未验证” | 必选——R0 行记录当前基线，后续版本对比它 |
| **A→B 承接** | 当证据阶段进入 `有限真实使用`，验证器警告提示切换；用户确认后回填 R0 基线、升 minor 版、重过审阅闸门 | — |

产出结构（3.0.0 新版式）：

```
PRD（7 章）                          Roadmap（6 章）
├─ 0 目录（3.2.0 新增，与标题逐字一致）├─ 0 目录（3.2.0 新增，与标题逐字一致）
├─ 1 产品定位与承诺                  ├─ 1 用户与终局
├─ 2 现状与问题        ← 场景变形    ├─ 2 现状与总路线
├─ 3 产品方案：能力、需求与运转       ├─ 3 本版详单（真值边界表在这里）
│     └─ 需求按 P0/P1/P2 分组成块    ├─ 4 体验版本路线图
├─ 4 规则与红线                      │     └─ 4.4 需求落位映射（唯一权威）
├─ 5 价值与成功指标                  ├─ 5 能力层级
├─ 6 复用与依赖        ← 场景变形    └─ 6 闸门与假设
└─ 7 风险与假设
```

**各司其职（3.0.0 硬校验）**：PRD 按优先级组织需求、只定“做什么与怎么验收”、**不标版本**；每条需求进哪个版本，只在 Roadmap §4.4 需求落位映射维护——它是唯一权威，验证器双向比对两文档编号一一对应。旧版两头写版本编排、一处更新他处遗漏的问题就此根治。分工一句话：**PRD 写需求与生效逻辑，Roadmap 写各阶段执行拆解**；两文档 ≥30 字的相同正文行会被验证器报警，收敛到单文档+引用。

**信息结构化（3.2.0）**：两份文档都在元数据后带「## 目录」节，目录行与实际 H2/H3 标题逐字双向一致（验证器错误级）——单看目录就能重建文档逻辑地图；语言精炼进契约（需求块「做什么」≤2 句、段落建议 ≤5 句、修饰性空话不入契约）；需求分组标题声明「N 条」与实际块数核对（错误级）。

**存量升级先摸排（3.2.0，B 场景硬约束）**：升级/重写存量产品文档前，先做只读 7 维现状摸排（交互触点 / 流程主链 / 大模型与脚本分工 / 边界兜底 / 安装分发 / 资产生命周期 / 初始化与扩展性），产出问题清单、你确认优先级后才动笔——避免“没摸清现状就重写”造成的整轮返工。

**施工期运行兼容（3.2.0，B 场景）**：历史版本还在运行、数据持续产生时，时间口径三时点锚定——基线锚定**执行日快照**（其后新增走日常机制）、验收锚定**验收时点**（回涨即失败）、「连续 N 天」从交付项**合入上线日**起算（老路径天数不计入）；安全网（回滚点/可观测性）最先合入。不写工期估计，只写依赖顺序。

**发布前评审矩阵（3.2.0，每次必做）**：验证器 0 错误后，必须跑 4 个独立只读评审——诉求覆盖度、跨文档一致性、现状事实一致性、双视角可读性（产品经理+业务负责人 3 分钟四问）；发现按「阻塞/建议」分级处理完毕才可交付。

### 它会主动问你什么（核心设计）

这是本技能最克制、也最值得讲清的地方。**它宁可先从证据里找答案，绝不轻易打断你。**

**① 问之前，先查证据。** 优先从 README、正式文档、已接受决策、运行时证据里解决；只有“查不到、且答案会改变决策”时才提问。缺失的业务选择**要么问、要么显式标成假设，绝不默默替你决定**。

**② 只在答案会改变这 7 件事之一时，才问：**

1. **产品用户**（谁获得价值）
2. **主价值载体**（产品形态）
3. **交付目的**（决策演示 / 用户价值验证 / 生产改进 / 集成验证 / 真实试点 / 规模化）
4. **价值瓶颈**（第一个阻挡结果的弱转折）
5. **路线顺序**（Roadmap 排序）
6. **真值边界**（真实 / 测试接入 / 模拟 / 人工承接 / …）
7. **审批条件与验收**

措辞、实现细节这类**不会改变决策**的问题，它一律不问。

**③ 每个问题都是固定四段式**，不抛孤立问题：

```
证据：    项目当前展示什么
建议解读： 与证据最一致的方向
问题：    一个高影响选择
影响：    每个答案下，什么会改变
```

**④ 多个方向都可信时，给你一张对比表**，在用户价值 / 业务价值 / 可行性 / 差异化 / 证据强度上对比 2–3 个备选，**推荐一个并请你确认**：

| 方向 | 用户价值 | 业务价值 | 可行性 | 差异化 | 证据强度 | 推荐 |
|---|---|---|---|---|---|---|

**⑤ 假设分级，诚实保持“不具备审批条件”。** 每条假设分 4 级（`必须为真` / `重要假设` / `可逆默认` / `高风险外部事实`）× 4 种状态（`已确认` / `建议假设，待确认` / `待调研` / `已否决`）。**只要还有一条 `必须为真` 未解决或已被否决，文档就保持 `Proposed / 不具备审批条件`**——不会用“看起来很完整”掩盖未验证的关键假设。

**⑥ 何时停止提问：** 当用户、价值载体、当前效果、交付目的、瓶颈、主路线、真值边界、下一闸门都稳定时。

> 想看完整的提问工作流与假设登记规则，深入阅读 [references/intent-and-scenario-contract.md](skills/define-product-and-roadmap/references/intent-and-scenario-contract.md)。

### 走到什么程度：8 步流程

上面“会问什么”是第 5 步的核心；完整流程如下（每步一句话）：

| 步骤 | 做什么 |
|---|---|
| 1. 确定范围与权限 | 判定操作（审计/创建/重写/对齐）、交付物、交付目标；rewrite 先出目录提案等你拍板；“批准”只授权进入下一闸门 |
| 2. 阅读权威证据 | 按 已批准契约 → 已接受决策 → 运行时/产物证据 → 当前研究 → 历史 的顺序读；**存量升级先做只读 7 维现状摸排，问题清单确认优先级后才起草** |
| 3. 构建内部产品简报 | 记录 当前用户与核心任务、价值载体、当前结果、最短价值路径、第一个弱转折、交付目的、下一闸门 等 12 个字段 |
| 4. 分类形态与风险 | 选定**唯一**主形态（用户在哪里获得价值的那一类）+ ≤2 个次级形态 + 风险修饰项 |
| 5. 关闭会改变决策的未知项 | **一次只问一个高影响问题**（见上 ①–⑥） |
| 6. 起草所选契约 | 合并 通用 + 主形态 + 次级形态 + 风险 契约，按模板填充 |
| 7. 验证确切交付物 | 对交付字节跑确定性验证器；**0 错误后必跑 4 视角独立只读评审矩阵**，阻塞项清零才结束 |
| 8. 语义审查 | 12 维度评分，标注自审 / 独立审查 |

**结束条件**：业务、产品、体验、技术四个负责人，各自能答出 8 个问题（谁获得价值、现在什么能用+证据、哪些契约适用、什么被复用/新建/模拟、主旅程如何成功并恢复、Roadmap 顺序为何跟随价值证据、还剩哪些假设+是否具备审批条件、哪个证据退出当前版本激活哪个闸门）——全部能答，才结束。

### 一个真实运行示例

在“老友办事助手”（C 端交互形态）上完整跑一次（见 [`test-results/codex/cend/`](test-results/codex/cend/)）：技能基于证据包产出对齐的 PRD + Roadmap，验证器 `validation passed`，但带 1 条警告——

> `必须为真` 假设未确认：**老年用户愿意独立在线办理至少一类事项**

于是文档状态停留在 `Proposed`、`是否具备审批条件：否`。这正是设计意图：**结构全过、关键假设未证实，就如实保持不具备审批条件**，而不是假装已就绪。

### 3.0.0 结构改造的前后对比（真实项目实测）

在老年大学“业务操作系统”（B 场景，27 条需求、10 个模块）上，用新契约重排了 1.2.0 文档对并跑通验证器：

| 维度 | 改造前（≤2.2.0 结构） | 改造后（3.0.0 结构） |
|---|---|---|
| PRD 章数 | 11 章 | 7 章（定位/现状/方案/红线/指标/复用/假设） |
| 需求形态 | 8 列大表，每条需求一行读到底 | 按 P0/P1/P2 分组的需求块，五要素子弹（做什么/你会看到/规则/验收/证据） |
| 版本编排 | PRD 与 Roadmap 两头写 R1/R2 落位，双头维护 | PRD 不标版本；Roadmap §4.4 落位映射唯一权威 |
| 真值边界表 | 在 PRD | 迁入 Roadmap 本版详单，唯一权威 |
| 版本总表 | 9 列巨表 | 4 列总表（含“你会看到什么·对比上一版”）+ 每版 8 小节详述 |
| 46 条历史评审问题 | — | 复评：34 条解决、9 条部分解决、3 条属用户决策（v1.1.0 原文未留档，以复评记录为等价证据） |
| 验证器 | 旧结构 23 项结构错（迁移中间态） | **0 错 0 警**；契约测试 62 个全绿 |

---

## 3. 三平台一键安装

Claude Code、Codex、WorkBuddy（及其编程向姊妹产品 CodeBuddy）都采用标准 Agent Skills 格式（`SKILL.md` + frontmatter `name`/`description`），差别只在发现目录。本仓库用**符号链接**让各平台共享同一个规范源，无需维护多份副本。

> **平台小贴士：** Claude Code、Codex、WorkBuddy、CodeBuddy 都兼容标准 SKILL.md。四者都支持“放符号链接到各自 skills 目录即发现”的轻量形态——发现目录分别是 `.claude/skills/`、`.agents/skills/`（Codex）、`.workbuddy/skills/`、`.codebuddy/skills/`。其中 WorkBuddy（腾讯，AI 办公 Agent）与 CodeBuddy（编程向）是两个独立产品；WorkBuddy 额外支持“技能市场导入 zip”（见方式三）。本项目 frontmatter（`name`+`description`）天然通过 WorkBuddy 的 `quick_validate.py`，无需 `plugin.json` 等额外清单。

### 前置条件

- **Python 3**（验证器需要）、**git**。
- 符号链接需类 Unix 环境（macOS / Linux / WSL）；Windows 原生不支持，请用 WSL 或管理员 `mklink /D`。

### 方式一：克隆仓库，即装即用（推荐体验）

```bash
git clone https://github.com/bangogo/define-product-and-roadmap.git
cd define-product-and-roadmap
```

仓库已内置四个符号链接，**在该目录下启动对应工具即自动发现技能**：

- Claude Code → `.claude/skills/define-product-and-roadmap`
- Codex → `.agents/skills/define-product-and-roadmap`
- WorkBuddy → `.workbuddy/skills/define-product-and-roadmap`
- CodeBuddy → `.codebuddy/skills/define-product-and-roadmap`

### 方式二：装到用户级全局（任一平台，可粘贴）

在你自己的任意项目里都能用。**注意：符号链接目标必须是绝对路径**（下方用 `$PWD` 保证）。

```bash
git clone https://github.com/bangogo/define-product-and-roadmap.git
cd define-product-and-roadmap

# Claude Code
mkdir -p ~/.claude/skills
ln -sfn "$PWD/skills/define-product-and-roadmap" ~/.claude/skills/define-product-and-roadmap

# Codex（用户级目录为 ~/.codex/skills/，与本仓库项目级的 .agents/skills/ 不同名——前者是全局发现，后者是项目内发现）
mkdir -p ~/.codex/skills
ln -sfn "$PWD/skills/define-product-and-roadmap" ~/.codex/skills/define-product-and-roadmap

# WorkBuddy
mkdir -p ~/.workbuddy/skills
ln -sfn "$PWD/skills/define-product-and-roadmap" ~/.workbuddy/skills/define-product-and-roadmap

# CodeBuddy
mkdir -p ~/.codebuddy/skills
ln -sfn "$PWD/skills/define-product-and-roadmap" ~/.codebuddy/skills/define-product-and-roadmap
```

> **同名冲突提示：** 若目标位置（`~/.claude/`、`~/.codex/`、`~/.workbuddy/`、`~/.codebuddy/` 下）已存在同名的**真实目录**（非符号链接，例如旧版本残留），`ln -s` 会在其内部新建链接而非报错，导致看似装好实际无效。请先 `rm -rf` 旧目录再链接（上方已用 `ln -sfn` 覆盖既有符号链接）。

### 方式三：WorkBuddy 技能市场导入本地包

从 [GitHub Release](https://github.com/bangogo/define-product-and-roadmap/releases) 下载 `dist/define-product-and-roadmap-3.2.0.zip`，在 WorkBuddy 打开**技能市场 → 添加技能 → 上传技能包**，选中该 zip，系统自动配置（CodeBuddy 同样支持此导入方式）。

### 安装后验证

```bash
python3 scripts/check_project.py
```

它会校验**仓库自带的四条项目级符号链接**、版本一致、62 个契约测试通过。

> 注意：`check_project.py` 只校验仓库内的项目级链接，**不检查方式二在你家目录创建的全局链接**。方式二装完后，建议自行确认指向正确，例如 `ls -l ~/.codex/skills/define-product-and-roadmap`。

### 调用

| 平台 | 调用方式 |
|---|---|
| Claude Code | `/define-product-and-roadmap …` |
| Codex | `$define-product-and-roadmap …`（见 `agents/openai.yaml`） |
| WorkBuddy / CodeBuddy | 启用后在对话中自动触发，或从技能菜单选择 |

**卸载：** 删除对应符号链接（`rm ~/.claude/skills/define-product-and-roadmap` 等）；WorkBuddy 在技能市场里卸载。

---

## 4. 文件结构速览

```
define-product-and-roadmap/
├── README.md                 # 本文件（项目级指引）
├── CHANGELOG.md              # 版本变更记录
├── VERSION                   # 3.2.0（与技能内 VERSION 必须一致）
├── LICENSE                   # MIT
├── scripts/                  # 项目级检查门 + 打包
├── dist/                     # 可移植发布 zip + SHA-256
├── docs/                     # 审计报告 + 测试报告
├── evals/                    # 触发与语义评估用例 + fixture
├── test-results/             # 真实运行证据（Codex / Claude）
├── .claude/skills/… → …      # Claude Code 发现（符号链接）
├── .agents/skills/… → …      # Codex 发现（符号链接）
├── .workbuddy/skills/… → …   # WorkBuddy 发现（符号链接）
├── .codebuddy/skills/… → …   # CodeBuddy 发现（符号链接）
└── skills/define-product-and-roadmap/   ★ 规范源（唯一真相）
```

### 项目根文件

| 文件 / 目录 | 作用 |
|---|---|
| `README.md` | 项目级指引（你正在看的） |
| `CHANGELOG.md` | 语义化版本变更记录（1.0.0-imported → 2.0.0 → … → 3.2.0，含旧→新契约校验点映射表） |
| `VERSION` | 单行版本号，必须与技能内 `VERSION` 一致（由检查门强制） |
| `LICENSE` | MIT，Copyright (c) 2026 luckyban |
| `.gitignore` | 排除 Python 字节码、`.DS_Store`、`dist` 临时文件、运行时产物等 |
| `scripts/check_project.py` | **项目总检查门**：必需文件、frontmatter 纯净、版本对齐、三平台符号链接、62 个契约测试、Python 编译、可选 `--verify-dist` |
| `scripts/package_skill.py` | 确定性打包：先跑检查门 → 生成 `dist/*.zip`（固定时间戳）+ SHA-256 |
| `dist/` | 发布归档（2.0.0 – 3.2.0）+ 各自 `.sha256` |
| `docs/` | `audit-report.md`（技能审计）、`skill-standards-audit.md`（3.1.0 标准符合性评估）、`test-report.md`（测试报告）、`baseline-source-sha256.txt`（导入基线） |
| `evals/` | `cases.jsonl`（15 个评估用例：触发 + 语义 + 场景 A/B + 仅审计）+ `fixtures/`（5 个证据包） |
| `test-results/` | Codex 4 组（子目录）+ Claude 2 份执行记录（平铺文件），作为有效性证据 |

### 技能本体 `skills/define-product-and-roadmap/`

| 文件 / 目录 | 作用 |
|---|---|
| [`SKILL.md`](skills/define-product-and-roadmap/SKILL.md) | **技能入口**（195 行）：frontmatter + 8 步工作流（目录提案确认、B 场景摸排、4 视角评审矩阵）+ 发布元数据 + 硬边界 + 结束条件 |
| `VERSION` | 单行 `3.2.0` |
| `agents/openai.yaml` | Codex / OpenAI UI 元数据（display_name、short_description、`$define-product-and-roadmap` 调用） |
| [`references/intent-and-scenario-contract.md`](skills/define-product-and-roadmap/references/intent-and-scenario-contract.md) | 意图/场景契约：操作权限、证据台账、适用场景判定（A/B）、B 场景 7 维现状摸排、快照维护规则、6 类主形态、风险修饰项、提问工作流、假设登记 |
| `references/prd-contract.md` | PRD 契约：7 章结构、场景维度矩阵（A/B 变形）、各司其职三分工、呈现规则 12 条（目录即地图/语言精炼）、通用表格与需求块、形态/风险专属契约（含 AI 评估表）、审批条件 |
| `references/roadmap-contract.md` | Roadmap 契约：6 章新版式、本版详单与真值边界表、版本总表+每版详述、需求落位映射唯一权威、能力语言、评价先行、施工期运行兼容三时点口径、闸门执行就绪结论、治理状态 |
| `references/quality-rubric.md` | 12 维度语义评分表（满分 24）+ 8 项审批阻塞项 + 4 视角评审矩阵 brief + 结果标签 |
| `references/revision-lessons.md` | 修订经验 36 条：症状 → 目标形态 → 修复动作 |
| `assets/prd-template.md` | PRD 空白模板（目录节 + 7 个 H2 + 元数据块 + 需求块分组 + A/B 变形占位注释） |
| `assets/roadmap-template.md` | Roadmap 空白模板（目录节 + 6 个 H2 + 版本总表 + 每版详述 + 需求落位映射） |
| `scripts/validate_product_docs.py` | **确定性验证器**（1427 行）：校验结构、11 字段元数据、场景分支（A/B + A→B 切换警告）、需求块、各司其职 3 硬校验、真值标签、形态契约、ID 与跨文档一致性、呈现规则、目录↔标题双向一致、分组计数、跨文档重复行、连续 N 天口径 |
| `scripts/test_contract.py` | 验证器回归测试（72 个用例） |

> 想读完整的技能指令、8 步流程原文与硬边界，深入阅读 [SKILL.md](skills/define-product-and-roadmap/SKILL.md)。

---

## 5. 为什么不一样

大多数技能是**技术任务导向**。本技能是**产品契约导向**——它定义“产品要成立”必须说清的契约。八个差异点（机制细节见[第 2 节](#2-它怎么工作--会主动问你什么)）：

**用户视角切分，而非技术模块切分。** 用 6 类**产品主形态**描述产品，依据是“用户在哪里获得价值”（C 端交互 / 内容·产物生产 / 内部流程 / API·平台 / 服务编排 / 交易·市场），而非技术架构。AI、外部写入、敏感数据被归为**风险修饰项**，不伪装成形态。

**场景自适应（3.0.0）。** 0→1 新产品不再被逼着填“当前效果实测”——现状章变形为问题假设与冷启动、复用章变形为外部依赖注册、无 R0、真值表显式全“尚未验证”；证据阶段进入真实使用时提示切换场景并回填基线。

**各司其职（3.0.0）。** PRD 只答“做什么、为什么、怎么验收”（按优先级组织、不标版本），Roadmap 只答“什么时候、什么顺序、怎么判过关”（落位映射唯一权威）；两头写版本编排会被验证器当错误拦下。

**价值路径与第一个瓶颈。** 优先级来自“今天哪个转折阻挡了用户结果”，而非通用模块顺序或日期。

**当前效果 vs 目标态强制分离（最硬边界）。** 绝不把目标、计划、fixture、成功命令或历史声明当作当前产品证据。实测中最典型的错误：把“下一版计划”冒充为“当前已验证能力”。

**真值分层。** 8 类真实性标签让“现在到底有多真”一目了然——避免把“跑通一次命令”等同于“产品对用户成立”。（机制见[第 2 节](#2-它怎么工作--会主动问你什么)）

**呈现由总到分、单源化。** 每章先给结论或总览再给论证；同一规则只在一处完整定义、他处引用；枚举只引用权威表编码、不散文重列；修订史外置。逐字重复、考古括号、版本自引用矛盾、同轴多表都会被验证器拦下（warning/error）。

**评价先行。** AI 生成类能力默认按「先评价 → 再生成 → 后执行」排序：先定义评估载体、维度、最小基线采集动作与裁决机制，再生成，通过裁决后解锁执行；每个未知基线必须带采集路径——“不能够很好地评价，也就不能够很好地执行”。

**克制的互动澄清。** 只在答案会改变决策时才问，四段式提问，假设分级，未解决的 `必须为真` 让文档保持不具备审批条件。（完整规则见[第 2 节](#2-它怎么工作--会主动问你什么)）

> **证明边界：** 本技能的验证器与语义审查只证明**结构一致性**与**审查完整性**。它**不证明**运行时行为、用户价值、研究真值或审批。一份写得好的产品契约，可能正确地保持“不具备审批条件”。

---

## 6. 版本与发布工作流 / 质量门

遵循[语义化版本](https://semver.org/lang/zh-CN/)：MAJOR 破坏文档/调用契约，MINOR 向后兼容的能力扩展，PATCH 不改公开契约的修复。

**发布工作流：**

1. 只编辑 `skills/define-product-and-roadmap` 规范源
2. 同步两个 `VERSION` 文件与 `CHANGELOG.md`
3. `python3 scripts/check_project.py`
4. 跑代表性评估并记录真实状态
5. `python3 scripts/package_skill.py`（生成 `dist/*.zip` + 校验和）
6. `python3 scripts/check_project.py --verify-dist`
7. 提交、创建注释 Git 标签，保留 zip 与校验和

**验证一对已有 PRD/Roadmap：**

```bash
python3 skills/define-product-and-roadmap/scripts/validate_product_docs.py \
  --prd <你的 PRD 路径> \
  --roadmap <你的 Roadmap 路径>
```

验证器证明 Markdown 结构、规范状态、所选契约覆盖、ID 与跨文档一致性；**它不证明**底层事实或产品质量（证明边界见[第 5 节](#5-为什么不一样)）。

---

## 7. 贡献 / 许可

- **许可：** MIT（见 [LICENSE](LICENSE)）
- **变更记录：** [CHANGELOG.md](CHANGELOG.md)
- **质量证据：** [docs/audit-report.md](docs/audit-report.md)、[docs/test-report.md](docs/test-report.md)
- **贡献：** 改动请先跑 `python3 scripts/check_project.py`；技能目录内禁止放 README/CHANGELOG/INSTALLATION 等辅助文档（检查门强制），项目级文档只放根目录或 `docs/`。
