# 定义产品与路线图(define-product-and-roadmap)

> 创建、审计、重写或对齐基于真实证据的产品 PRD 与体验路线图(Roadmap)。兼容 Claude Code、Codex、CodeBuddy/WorkBuddy。

![version](https://img.shields.io/badge/version-2.1.0-blue)
![platform](https://img.shields.io/badge/platform-Claude%20Code%20%7C%20Codex%20%7C%20CodeBuddy-green)

这是一个**产品契约技能**:它产出一份可读的 PRD + Roadmap,回答四个问题——**谁获得价值、产品当前能证明什么、第一个价值瓶颈在哪里、哪个证据能解锁下一个版本**。

它不是技术架构工具、工程任务拆解工具或营销计划工具。

---

## 使用场景

| 操作 | 何时用 |
|---|---|
| 创建(create) | 从零产出一份对齐的 PRD + Roadmap,基于项目现有证据 |
| 仅审计(audit only) | 只报告现有 PRD/Roadmap 的问题,**不改动文件** |
| 重写(rewrite) | 按最新证据重写文档,保留原件并给出变更摘要 |
| 对齐(align) | 调和已有的 PRD/Roadmap 对,使其元数据与契约一致 |

**典型触发**:产品需求文档、PRD、产品价值、产品形态、当前效果、用户路径、内容或产物生产、内部工作流、API/平台、服务编排、marketplace、AI 助手、MVP、体验版本、复用决策、风险边界、假设确认、审批条件评估。

**不要用于**:单纯的工程任务清单、技术架构图、营销发布计划、仅限代码实现的评审——除非你同时需要一份产品契约。

---

## 与其他 Skill 的差异化

大多数 Skill 是**技术任务导向**(代码生成、代码审查、测试、部署)。本技能是**产品契约导向**:它定义“产品要成立”必须说清的契约,而不是“代码要怎么写”。

### 1. 用户体验视角切分,而非技术模块切分

用 6 类**产品主形态**描述一个产品,依据是“用户在哪里获得价值”,而不是技术架构:

- `C端交互产品` —— 用户在界面完成任务并理解结果
- `内容/产物生产` —— 用户获得一个可用且可审阅的产物
- `内部流程工具` —— 操作人完成一个真实工作项
- `API/平台` —— 一个新使用者达到首次成功使用
- `服务编排` —— 用户获得服务结果,而非仅一个链接
- `交易/市场` —— 双方完成一次受保护的交易

AI、外部写入、敏感数据等被归为**风险修饰项**,而非伪装成产品形态。每种形态有专属的契约表(如 C 端看场景/进入/行动/状态/结果/恢复;产物生产看输入/处理/产物/质量门/来源/审阅)。

### 2. 价值路径与第一个瓶颈

从触发到有意义结果的**最短价值路径**,找到第一个弱转折作为优先级来源。优先级不来自通用模块顺序或日期,而来自“今天哪个转折阻挡了用户结果”。

### 3. 当前效果 vs 目标态强制分离

这是本技能最硬的边界:**绝不把目标、计划、fixture、成功命令或历史声明当作当前产品证据**。当前效果必须带证据状态(真实/测试接入/模拟/人工承接/仅有文档/已观察/尚未验证/历史证据)。实测中最典型的错误,就是把“下一版计划”冒充为“当前已验证能力”。

### 4. 真值分层

8 类真实性标签让“现在到底有多真”一目了然,避免把“跑通一次命令”等同于“产品对用户成立”。

### 5. 完整的产品工作流定义

技能定义了一条端到端工作流:

1. **确定范围与权限** —— 审计/创建/重写/对齐,以及“审批只授权下一闸门”
2. **阅读权威证据** —— 按 已批准契约 → 已接受决策 → 运行时证据 → 研究 → 历史 的顺序
3. **构建内部产品简报** —— 用户、价值载体、瓶颈、真值边界、证据缺口
4. **分类形态与风险** —— 主形态 + 风险修饰项
5. **关闭会改变决策的未知项** —— 一次一个高影响问题
6. **起草所选契约** —— 通用 + 形态 + 风险契约
7. **验证确切交付物** —— 对交付字节运行确定性验证器
8. **语义审查** —— 12 维度评分,标注自审/独立

这套流程把“写一份 PRD”从拍脑袋变成“证据驱动的产品决策”。

---

## 安装

三个平台都采用标准 Agent Skills 格式(SKILL.md + frontmatter `name`/`description`),差别只在发现目录。本仓库用**符号链接**让三平台共享同一个规范源(`skills/define-product-and-roadmap`),无需维护多份副本。

### 方式一:克隆仓库(推荐,三平台共享)

```bash
git clone https://github.com/bangogo/define-product-and-roadmap.git
cd define-product-and-roadmap
```

仓库已内置三个平台的符号链接:

- Claude Code:`.claude/skills/define-product-and-roadmap`
- Codex:`.agents/skills/define-product-and-roadmap`
- CodeBuddy/WorkBuddy:`.codebuddy/skills/define-product-and-roadmap`

在该仓库目录下启动对应工具即可自动发现技能。

### 方式二:安装到用户级全局(任一平台)

把技能目录链接(或复制)到各平台的用户级发现目录:

```bash
# 先克隆(或在 Release 下载并解压 dist zip)
git clone https://github.com/bangogo/define-product-and-roadmap.git /path/to/define-product-and-roadmap

# Claude Code
ln -s /path/to/define-product-and-roadmap/skills/define-product-and-roadmap \
      ~/.claude/skills/define-product-and-roadmap

# Codex
ln -s /path/to/define-product-and-roadmap/skills/define-product-and-roadmap \
      ~/.codex/skills/define-product-and-roadmap

# CodeBuddy / WorkBuddy
ln -s /path/to/define-product-and-roadmap/skills/define-product-and-roadmap \
      ~/.codebuddy/skills/define-product-and-roadmap
```

### 方式三:WorkBuddy 技能市场导入本地包

从 [GitHub Release](https://github.com/bangogo/define-product-and-roadmap/releases) 下载 `dist/define-product-and-roadmap-2.1.0.zip`,在 WorkBuddy 技能市场选择“导入本地技能包”,上传该 zip。

### 调用

| 平台 | 调用方式 |
|---|---|
| Claude Code | `/define-product-and-roadmap ...` |
| Codex | `$define-product-and-roadmap ...` |
| CodeBuddy/WorkBuddy | 在技能菜单选择,或按其调用约定 |

---

## 使用方法

**创建一对对齐的 PRD + Roadmap**:

```text
基于当前 README、正式产品文档、ADR 和运行证据,创建对齐的 PRD 与 Roadmap。
```

**只审计,不改文件**:

```text
完整审计当前 PRD 和 Roadmap,只报告问题,不修改文件。
```

**重写并保留原件**:

```text
基于最新证据重写 PRD 与 Roadmap;保留原文件并给出变更摘要。
```

技能会:读取证据 → 分类形态与风险 → 起草契约 → 对交付字节运行验证器 → 给出 12 维语义评分与审批结论。

---

## 质量门与测试

```bash
# 项目总检查门(结构、35 个契约测试、版本、三平台符号链接、Python 编译)
python3 scripts/check_project.py

# 验证一对 PRD/Roadmap 文档
python3 skills/define-product-and-roadmap/scripts/validate_product_docs.py \
  --prd <你的 PRD 路径> \
  --roadmap <你的 Roadmap 路径>
```

验证器证明 Markdown 结构、规范状态、所选契约覆盖、ID 与跨文档一致性。**它不证明**底层事实或产品质量——那需要应用语义评分表与真实证据。

---

## 仓库结构

```
skills/define-product-and-roadmap/   # 规范源(唯一真相)
  SKILL.md                            # 技能入口(frontmatter + 指令)
  references/                         # 意图/PRD/Roadmap 契约、修订经验、质量评分表
  assets/                             # PRD、Roadmap 模板
  scripts/                            # 验证器 + 契约回归测试
  agents/openai.yaml                  # Codex/OpenAI UI 元数据
.claude/skills/...                    # Claude Code 发现(符号链接)
.agents/skills/...                    # Codex 发现(符号链接)
.codebuddy/skills/...                 # CodeBuddy/WorkBuddy 发现(符号链接)
scripts/                              # 项目检查门 + 打包
dist/                                 # 可移植发布 zip + SHA-256
evals/                                # 触发与语义评估用例
docs/                                 # 审计报告 + 测试报告
```

---

## 版本与发布工作流

遵循[语义化版本](https://semver.org/lang/zh-CN/):MAJOR 用于破坏文档/调用契约的变更,MINOR 用于向后兼容的能力扩展,PATCH 用于不改公开契约的修复。

1. 只编辑 `skills/define-product-and-roadmap` 规范源
2. 更新两个 `VERSION` 文件与 `CHANGELOG.md`
3. `python3 scripts/check_project.py`
4. 跑代表性评估并记录真实状态
5. `python3 scripts/package_skill.py`(生成 `dist/*.zip` + 校验和)
6. `python3 scripts/check_project.py --verify-dist`
7. 提交、创建注释 Git 标签,保留 zip 与校验和

---

## 证明边界

本技能的验证器与语义审查只证明**结构一致性**与**审查完整性**。它不证明运行时行为、用户价值、研究真值或审批。一份写得好的产品契约可能正确地保持“不具备审批条件”。

## 许可

MIT
