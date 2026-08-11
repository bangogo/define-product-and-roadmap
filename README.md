# 定义产品与路线图 (define-product-and-roadmap)

> 给产品经理和业务负责人：把“这个产品到底成不成立”从拍脑袋，变成一份**证据驱动的产品契约**——说清“谁获得价值、现在能证明什么、第一个瓶颈在哪、哪个证据能解锁下一版”，并明确标出它**现在是否已具备审批条件**。

![version](https://img.shields.io/badge/version-2.2.0-blue)
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

**不要用于：** 单纯的工程任务清单、技术架构图、营销发布计划、仅限代码实现的评审——除非你**同时**需要一份产品契约。

---

## 2. 它怎么工作 & 会主动问你什么

### 产出什么

一对**元数据完全对齐**的 Markdown 文档：一份 PRD（`product-requirements.md`）+ 一份体验路线图（`product-roadmap.md`）。可以落成文件，也可以在对话里直接交付。仅审计模式只给报告、不动文件。

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
| 1. 确定范围与权限 | 判定操作（审计/创建/重写/对齐）、交付物、交付目标；“批准”只授权进入下一闸门 |
| 2. 阅读权威证据 | 按 已批准契约 → 已接受决策 → 运行时/产物证据 → 当前研究 → 历史 的顺序读 |
| 3. 构建内部产品简报 | 记录 当前用户与核心任务、价值载体、当前结果、最短价值路径、第一个弱转折、交付目的、下一闸门 等 12 个字段 |
| 4. 分类形态与风险 | 选定**唯一**主形态（用户在哪里获得价值的那一类）+ ≤2 个次级形态 + 风险修饰项 |
| 5. 关闭会改变决策的未知项 | **一次只问一个高影响问题**（见上 ①–⑥） |
| 6. 起草所选契约 | 合并 通用 + 主形态 + 次级形态 + 风险 契约，按模板填充 |
| 7. 验证确切交付物 | 对交付字节跑确定性验证器 |
| 8. 语义审查 | 12 维度评分，标注自审 / 独立审查 |

**结束条件**：业务、产品、体验、技术四个负责人，各自能答出 8 个问题（谁获得价值、现在什么能用+证据、哪些契约适用、什么被复用/新建/模拟、主旅程如何成功并恢复、Roadmap 顺序为何跟随价值证据、还剩哪些假设+是否具备审批条件、哪个证据退出当前版本激活哪个闸门）——全部能答，才结束。

### 一个真实运行示例

在“老友办事助手”（C 端交互形态）上完整跑一次（见 [`test-results/codex/cend/`](test-results/codex/cend/)）：技能基于证据包产出对齐的 PRD + Roadmap，验证器 `validation passed`，但带 1 条警告——

> `必须为真` 假设未确认：**老年用户愿意独立在线办理至少一类事项**

于是文档状态停留在 `Proposed`、`是否具备审批条件：否`。这正是设计意图：**结构全过、关键假设未证实，就如实保持不具备审批条件**，而不是假装已就绪。

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

从 [GitHub Release](https://github.com/bangogo/define-product-and-roadmap/releases) 下载 `dist/define-product-and-roadmap-2.2.0.zip`，在 WorkBuddy 打开**技能市场 → 添加技能 → 上传技能包**，选中该 zip，系统自动配置（CodeBuddy 同样支持此导入方式）。

### 安装后验证

```bash
python3 scripts/check_project.py
```

它会校验**仓库自带的四条项目级符号链接**、版本一致、35 个契约测试通过。

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
├── VERSION                   # 2.2.0（与技能内 VERSION 必须一致）
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
| `CHANGELOG.md` | 语义化版本变更记录（1.0.0-imported → 2.0.0 → 2.0.1 → 2.1.0） |
| `VERSION` | 单行版本号，必须与技能内 `VERSION` 一致（由检查门强制） |
| `LICENSE` | MIT，Copyright (c) 2026 luckyban |
| `.gitignore` | 排除 Python 字节码、`.DS_Store`、`dist` 临时文件、运行时产物等 |
| `scripts/check_project.py` | **项目总检查门**：必需文件、frontmatter 纯净、版本对齐、三平台符号链接、35 个契约测试、Python 编译、可选 `--verify-dist` |
| `scripts/package_skill.py` | 确定性打包：先跑检查门 → 生成 `dist/*.zip`（固定时间戳）+ SHA-256 |
| `dist/` | 发布归档（2.0.0 / 2.0.1 / 2.1.0）+ 各自 `.sha256` |
| `docs/` | `audit-report.md`（技能审计）、`test-report.md`（测试报告）、`baseline-source-sha256.txt`（导入基线） |
| `evals/` | `cases.jsonl`（12 个评估用例：触发 + 语义 + 仅审计）+ `fixtures/`（3 个证据包） |
| `test-results/` | Codex 4 组（子目录）+ Claude 2 份执行记录（平铺文件），作为有效性证据 |

### 技能本体 `skills/define-product-and-roadmap/`

| 文件 / 目录 | 作用 |
|---|---|
| [`SKILL.md`](skills/define-product-and-roadmap/SKILL.md) | **技能入口**（145 行）：frontmatter + 8 步工作流 + 发布元数据 + 硬边界 + 结束条件 |
| `VERSION` | 单行 `2.1.0` |
| `agents/openai.yaml` | Codex / OpenAI UI 元数据（display_name、short_description、`$define-product-and-roadmap` 调用） |
| [`references/intent-and-scenario-contract.md`](skills/define-product-and-roadmap/references/intent-and-scenario-contract.md) | 意图/场景契约：操作权限、证据台账、6 类主形态、风险修饰项、提问工作流、假设登记 |
| `references/prd-contract.md` | PRD 契约：11 章结构、通用表格、形态/风险专属契约、审批条件 |
| `references/roadmap-contract.md` | Roadmap 契约：能力语言、版本证据规则、治理状态 |
| `references/quality-rubric.md` | 12 维度语义评分表（满分 24）+ 审批阻塞项 + 结果标签 |
| `references/revision-lessons.md` | 修订经验：症状 → 目标形态 → 修复动作 |
| `assets/prd-template.md` | PRD 空白模板（11 个 H2 + 元数据块 + 规范表） |
| `assets/roadmap-template.md` | Roadmap 空白模板（6 个 H2 + 能力层级表 + 体验版本表） |
| `scripts/validate_product_docs.py` | **确定性验证器**（696 行）：校验结构、元数据、真值标签、形态契约、ID 与跨文档一致性 |
| `scripts/test_contract.py` | 验证器回归测试（35 个用例） |

> 想读完整的技能指令、8 步流程原文与硬边界，深入阅读 [SKILL.md](skills/define-product-and-roadmap/SKILL.md)。

---

## 5. 为什么不一样

大多数技能是**技术任务导向**。本技能是**产品契约导向**——它定义“产品要成立”必须说清的契约。五个差异点（机制细节见[第 2 节](#2-它怎么工作--会主动问你什么)）：

**用户视角切分，而非技术模块切分。** 用 6 类**产品主形态**描述产品，依据是“用户在哪里获得价值”（C 端交互 / 内容·产物生产 / 内部流程 / API·平台 / 服务编排 / 交易·市场），而非技术架构。AI、外部写入、敏感数据被归为**风险修饰项**，不伪装成形态。

**价值路径与第一个瓶颈。** 优先级来自“今天哪个转折阻挡了用户结果”，而非通用模块顺序或日期。

**当前效果 vs 目标态强制分离（最硬边界）。** 绝不把目标、计划、fixture、成功命令或历史声明当作当前产品证据。实测中最典型的错误：把“下一版计划”冒充为“当前已验证能力”。

**真值分层。** 8 类真实性标签让“现在到底有多真”一目了然——避免把“跑通一次命令”等同于“产品对用户成立”。（机制见[第 2 节](#2-它怎么工作--会主动问你什么)）

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
