# Define Product and Roadmap 技能测试报告

## 结果汇总

| 层 | 结果 | 证明边界 |
|---|---|---|
| 导入基线 | 通过 | 精确原始副本;20 个测试与 OpenAI 快速验证通过 |
| v2 契约测试 | 通过,35/35 | 仅验证器行为 |
| Python 编译 | 通过 | 仅脚本语法/导入编译 |
| OpenAI `quick_validate` | 通过 | 仅技能包结构与元数据 |
| 项目发现链接 | 通过 | 三个符号链接(Claude Code、Codex、CodeBuddy/WorkBuddy)都解析到规范源 |
| Codex C 端生成 | 通过,1 个预期警告 | 项目技能调用与文档产物 |
| Codex 产物生成 | 通过,自审 20/24 | 项目技能调用、结构通过、语义自审 |
| Codex 产物审计 | 通过,22/24 | 全新上下文文档审计;审查者标注为非独立 |
| Codex 仅审计负例 | 正确失败,49 个错误,0/24 | 坏文档检测与不编辑行为 |
| Claude Code 发现 | 通过 | 加载了正确的 `.claude/skills` 目录 |
| Claude Code 审计执行 | 通过 | 在有 Read 与 Bash 的 host 中的结构审计 + 语义自审 |
| 可移植 ZIP | 通过 | 归档内容、校验和、解压验证与源一致性 |

## 确定性检查

从仓库根目录运行:

```bash
python3 scripts/check_project.py
```

该门验证必需文件、可移植 frontmatter、相对链接、版本对齐、项目发现符号链接、评估 schema、35 个回归用例、Python 编译与 OpenAI `quick_validate.py`。

回归覆盖包括全部六类主形态、次级形态、AI 与交易风险、缺失契约、无效真值与生命周期状态、未解决假设、元数据不匹配、重复元数据、版本缺口、需求/模块映射、无来源数字目标、开放标记、空表、失效链接、能力命名唯一性、`G1` 闸门范围,以及对模块字母 `L` 的支持。

## Codex 实时评估

### C 端创建

- 调用:隔离仓库,精确的项目 `.agents/skills` 路径。
- 结果:创建一对对齐的 PRD/Roadmap,以一个未解决假设的警告通过精确验证。
- 接受证据:`test-results/codex/cend/`。
- 边界:调用与文档产物;非产品运行时或用户证据。

### 内容/产物创建

- 调用:隔离仓库,精确的项目 `.agents/skills` 路径,`evidence/README.md` 作为唯一产品事实来源。
- 首次验证器运行:失败,41 个错误,包括真值标签误用与非唯一模块/能力编码。
- 恢复:Agent 用诊断修复这对文档。
- 最终验证器运行:通过,一个未解决的 `必须为真` 警告。
- 语义自审:`20/24 semantic_pass`;正确地 `Not approval-ready`。
- 接受证据:`test-results/codex/artifact/`。
- 边界:技能调用、自我修复、精确文档字节与自审;非独立判断或产品证据。

### 对接受产物对的全新上下文审计

- 加载确切的最终 v2 项目技能。
- 验证器:通过,一个未解决假设的警告。
- 语义得分:`22/24 semantic_pass`。
- 最弱维度:当前效果/证据与复用/归属。
- Agent 报告的审查标签:已执行自审,非独立。
- 接受证据:`test-results/codex/independent-audit/final.txt`。

### 仅审计负例

- 输入:故意不完整且矛盾的 PRD/Roadmap fixture。
- 改动检查:目标 fixture 文件保持不变;仅 CLI 最终消息文件未被跟踪。
- 验证器:`49 个错误,0 个警告`。
- 语义结果:`0/24 semantic_fail`。
- 正确发现:下一版计划被冒充为当前真值、PRD/Roadmap 形态与目的冲突、技术任务清单被用作 Roadmap、缺失用户/价值/证据/授权契约。
- 接受证据:`test-results/codex/audit-only/final.txt`。

### 被排除与被阻塞的运行

- 一次内容/产物尝试加载了用户级同名技能而非项目副本。它被中断并从验收证据中排除。
- 配置的默认模型在技能工作前失败,服务器响应要求更新的 Codex 版本。成功的验收运行显式使用 `gpt-5.4`。

## Claude Code 评估

Claude Code 加载项目目录 `.claude/skills/define-product-and-roadmap`(指向规范源的符号链接),证明项目发现。v2.0.0 运行(Claude Code 2.1.226,在 `/private/tmp/dpr-claude-v2.wZLPwS`)被阻塞:非交互 host 既未暴露 `Read` 也未暴露 `Bash`,因此审计执行停止,无产物被接受。v2.0.1 运行在一个有 `Read` 与 `Bash` 的 host 中端到端执行:技能加载、两个 `evals/fixtures/audit-only` 文件被读取、`validate_product_docs.py` 运行(49 个错误)、12 维语义自审得分 0/24 `semantic_fail`,fixture 字节未变。见 `test-results/claude/execution-passed.md` 与 `test-results/claude/audit-only-execution.txt`。

状态分类(v2.0.1):

- 已提及:Claude 兼容性是发布目标。
- 已声明:存在标准技能 frontmatter 与 `.claude/skills` 路径。
- 可用:Claude 加载了确切的项目目录。
- 已执行:发现已运行,且仅审计执行在一个有 `Read` 与 `Bash` 的 host 中完成。
- 接受产物:`test-results/claude/audit-only-execution.txt`(对负例 fixture 的结构 + 语义审计)。
- 语义/产品证据:未运行(对 fixture 的仅审计自审不是产品证据)。

## 包验证

发布构建运行了:

```bash
python3 scripts/package_skill.py
python3 scripts/check_project.py --verify-dist
```

验证确认了根 `define-product-and-roadmap/SKILL.md`、匹配的内部 `VERSION`、排除了缓存与编辑器文件,以及匹配的 SHA-256 校验和。归档被解压到一个新的临时目录,通过 OpenAI `quick_validate.py`,并用 `diff -qr` 匹配规范技能目录。

- 归档:`dist/define-product-and-roadmap-2.1.0.zip`
- SHA-256:`88444cd46fc12e80f5f7f881419450f5659d0f573863105ef7224d8664cc4a99`
- 契约测试:`35/35 通过`
- 带 `--verify-dist` 的项目门:通过
