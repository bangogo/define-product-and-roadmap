# 变更记录

项目本地 `define-product-and-roadmap` 技能的所有重要变更记录于此。项目对打包的技能遵循语义化版本。

## 2.1.0 - 2026-08-10

### 新增

- 兼容 CodeBuddy/WorkBuddy:新增 `.codebuddy/skills/define-product-and-roadmap` 符号链接,`check_project.py` 覆盖第三个平台。三平台(Claude Code、Codex、CodeBuddy/WorkBuddy)共享同一规范源。
- 重写中文 README:使用场景、用户体验视角切分的差异化、三平台安装指令、使用方法、质量门与发布工作流。
- 新增 MIT LICENSE,支持公开分享。

### 变更

- 全面中文化:SKILL.md、5 份 references、openai.yaml、`validate_product_docs.py` 与 `check_project.py` 等脚本的用户可见输出、docs 审计/测试报告、CHANGELOG。关键术语与机器契约(文档状态枚举、`semantic_*` 标签、能力/版本编码、`Do not use` 边界)保留原样。
- 验证器输出文案中文化,保留 `proof boundary` 子串与所有 `area` 短码;同步 `test_contract.py` 的 WARNING 断言。

### 说明

- 不改产品契约语义(形态/真值/编码/工作流不变),属 MINOR。35 个契约测试与验证器正/负例行为不变。

## 2.0.1 - 2026-08-10

### 变更

- Claude Code 执行证据由 Blocked 升级为 Pass:项目技能的仅审计操作在一个暴露 `Read` 与 `Bash` 的 Claude Code host 中运行,对 audit-only fixture 产出结构审计(49 个错误)与语义自审(0/24 `semantic_fail`),且 fixture 字节未变。
- 在 `test-results/claude/audit-only-execution.txt` 下新增 Claude Code 审计执行产物;将 `test-results/claude/discovery-blocked.md` 重命名为 `test-results/claude/execution-passed.md`。

### 说明

- 无技能契约变更(`SKILL.md`、references、模板与验证器逻辑均未改动)。这是一个记录 Claude Code 执行里程碑与刷新测试证据的 PATCH 发布。

## 2.0.0 - 2026-08-09

### 新增

- 在 `skills/define-product-and-roadmap` 下建立一个规范的 Agent Skills 包。
- 为 Codex 与 Claude Code 提供项目发现链接。
- 独立的风险修饰项元数据与契约。
- 证据来源、文档版本、证据截止日期、生命周期与审批规则。
- 用于可靠创建新文档的 PRD 与 Roadmap 模板。
- 一份 12 维度的语义质量评分表,带明确的证明边界。
- 机器可读的验证器输出与项目/包验证。
- 触发、边界与语义评估用例。
- 可复现的 ZIP 打包与 SHA-256 校验和。

### 变更

- 把模块真值收紧到正式模块表,而非把每个类模块引用都当作定义。
- 将验证从 20 个基线用例扩展到 35 个契约用例。
- 要求物质性假设、真值边界与审批元数据在 PRD 与 Roadmap 之间对齐。
- 要求版本 ID、需求 ID、规范生命周期状态、非空表格与风险覆盖。
- 把证据来源标签与已发布的运行时真值标签分开,并明确模块字母归属。
- 把能力编码验证限定在能力层级与版本能力单元格,使 `G1` 等闸门 ID 不再误报。
- 澄清结构验证不等于语义质量、运行时证据、用户证据或审批。

### 破坏性

- 文档现在要求 `文档版本`、`证据截止日期` 与 `风险修饰项` 元数据。
- 参考/复用、能力、成功、当前交付、假设与闸门表使用更强的 v2 表头。
- AI 被建模为风险修饰项,而非次级产品形态。

## 1.0.0-imported - 2026-08-09

- 导入时 `/Users/helloban/.codex/skills/define-product-and-roadmap` 的精确副本。
- 保留在 Git 提交 `dc5a8c0` 与注释标签 `v1.0.0-imported`。
- 基线证据:OpenAI `quick_validate.py` 通过;直接调用时,所有 20 个内置契约测试通过。
