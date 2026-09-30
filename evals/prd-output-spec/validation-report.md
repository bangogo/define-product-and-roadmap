# `define-product-and-roadmap` 4.1.0 验证报告

日期：2026-09-30
目标：[`spec.md`](../../spec.md)，唯一目标规格。  
范围：Skill 说明、PRD 契约、HTML 模板与确认交互、静态校验、兼容性和回归样本。案例 PRD 未修改。

## 结果摘要

| 层级 | 结果 | 证据与边界 |
|---|---|---|
| 静态/确定性 | 通过 | 72 个旧契约测试、11 个 HTML 契约测试、Python 编译、OpenAI `quick_validate`、项目结构检查、合成 HTML 样本、4.1.0 ZIP 逐文件比较。 |
| 语义 | 部分通过 | P-01—P-22 来源与规格映射已补齐；合成修订稿内嵌迁移表并覆盖需求 ID；案例 draft.4—draft.6、配套规范/候选能力记录做了只读语义抽查。没有独立评审者或真实模型生成结果。 |
| 视觉 | 未验证 | 本机浏览器拒绝打开 `file://` 样本；未尝试代理、localhost 或其他入口。桌面、390px 窄屏和打印的实际渲染均无证据。 |
| 真实宿主交互 | 未验证 | Node 测试在模拟 DOM 中验证交互逻辑；没有真实浏览器下载、宿主对话回传或外部平台调用证据。 |
| 用户确认/效果 | 未验证 | 没有用户对具体 4.0.0 PRD 内容和视觉效果的确认，也没有真实产品用户任务结果。 |

## 已运行检查

- `python3 scripts/check_project.py`：通过。运行旧契约测试 **72/72**、HTML 契约测试 **11/11**、Python 编译、OpenAI `quick_validate` 和维护文档链接检查。
- `python3 evals/prd-output-spec/check_scenarios.py`：通过。模板与 3 份合成存量 PRD 样本满足独立校验；两轮修订后的规则只保留一个正文定义；修订稿内嵌迁移表；新增表列、SVG 节点和文字路径同步；没有生成 Roadmap。
- `node evals/prd-output-spec/interaction_smoke.mjs`：通过。检查两步方向、空选、缺方向、修改缺意见阻止导出，有效方向记录导出、版本级确认字段、无待决项仍可导出。
- HTML 负例由 `scripts/test_html_contract.py` 覆盖：修订缺迁移表、迁移表字段缺失/信息损失缺失/非法处理方式、4.0 无方向记录、未声明方向、缺项、重复/过期决定、内容指纹不匹配、最终版缺确认、SVG 失败边指向普通节点或缺正文规则、无效 HTML 结构等均被拒绝；状态单独变化可复用同一内容指纹。共 11 项通过。
- 旧 Markdown CLI：通过。用 `test_contract.py` 的既有工厂构建 PRD/Roadmap 样本，`validate_product_docs.py --prd ... --roadmap ...` 返回 0；输出边界为结构与跨文档一致性。
- 合成图形越界负例：静态 HTML 校验仍通过，说明当前确定性检查不能判定 SVG 几何容纳。此负例用于明确静态检查盲区，不代表视觉合格。
- 案例项目 `python3 scripts/check_docs.py --version 2.1.0-draft.6`：通过。案例仓库明确说明这是静态文档检查，不验证运行产品、平台集成、用户效果或内容质量。
- `python3 scripts/package_skill.py` 后执行 `python3 scripts/check_project.py --verify-dist`：通过。校验清单、ZIP 内文件集合、每个文件字节、版本和 SHA-256 与当前源码一致。

## C1—C9 场景验收

| 用例 | 结果 | 实际证据 |
|---|---|---|
| C1 新建与明确非 HTML | 部分 | HTML 模板可独立校验；`requested-markdown.md` 和 eval 语义用例记录明确格式路径。未运行模型生成新产品 PRD。 |
| C2 两轮增量修订 | 合成通过 | `.draft.1`→`.draft.3` 样本验证同一需求原位修订、HTML 内迁移表、表格新增维度、SVG/正文同步、无 Roadmap。 |
| C3 重写迁移 | 合成通过 | `inputs-and-migration.md` 记录输入；修订样本 HTML 内 `data-migration-table="v1"` 覆盖当前需求 ID 并说明语义变化/信息损失。 |
| C4 draft.4→draft.6 案例复核 | 只读语义抽查 | 复核了章节合并、三行蛇形十阶段、创作者自行发布与评审副本状态；未改案例。检查仅针对源稿语义，不等于内容批准或渲染验收。 |
| C5 图形/窄屏/打印失败 | 静态盲区已证实；渲染未验证 | 越界 SVG 负例结构仍通过；浏览器拒绝 `file://` 后停止视觉路径。 |
| C6 决定卡 | 模拟交互通过 | 11 个 Python 契约用例及 Node 模拟 DOM 冒烟通过；确认/修改均绑定稳定方向。真实浏览器下载未验证。 |
| C7 能力与证据边界 | 部分语义通过 | 合成样本及 draft.6 候选能力记录保持候选、公开资料与运行证据区分；未调用宿主工具。 |
| C8 配套文件一致性/清理授权 | 只读抽查通过；操作未执行 | draft.6 PRD 将产品行为、可见结果和失败选择指向交付规范；交付规范承接字段、状态、交接与逐步失败恢复；候选能力记录明确“待复核/不表示集成”。本轮没有清理请求，故没有删除文件。 |
| C9 旧格式兼容 | 通过 | 72 个既有契约测试通过；Markdown PRD+Roadmap CLI 样本通过。单份 PRD 的测试确认不需临时 Roadmap。 |

案例配套文档核对为源稿抽样：PRD 与交付规范对确认失败后转 Agent 对话、对象/修订绑定、创作者自行发布及宿主未验证的边界相互指向；候选能力记录把产品能力、候选提供方和宿主适配拆开，并把本轮能力选择保留为后续决定。此为本次自查，不是独立审查。

## Documents 工作树未提交 4.0 改动（只读核对）

位置：`/Users/helloban/Documents/01 产品需求与产品路线图技能`，分支 `codex/prd-skill-upgrade`，基线 `a523a33`。检查前后均只读取状态和差异；未修改、暂存或清理该工作树。

| 改动 | 处理判断 |
|---|---|
| 精简后的 `SKILL.md` 与 PRD 契约，增量/继承说明、HTML 模板、确认工作流、指纹校验和新 CLI 分支 | 可复用其结构和部分实现；本分支按 `spec.md` 重写边界并补独立验收，避免直接整套合并。 |
| HTML 模板、`html_prd_validator.py`、旧 Markdown+Roadmap 兼容改造 | 可复用；本分支已调整记录字段、状态转换、确认放行条件和单份 PRD 校验，并加入正反例。 |
| `quality-rubric.md`、`revision-lessons.md` | 可复用其增量修订与分层验收思路；本分支纳入规格要求且保留 Roadmap 原契约。 |
| Documents 根 `README.md` 被删除 | 与保留有效安装说明的收尾要求冲突；本分支重写精简 README，恢复仓库链接、用户级链接、包导入提示和静态验证说明。 |
| Documents 中未提交的 `spec.md` | 不采用为本轮规则来源；目标工作树的 `spec.md` 才是唯一规格。历史问题材料只作为来源索引。 |
| Documents 的 `prd-contract.md` 删减固定章节/场景约束 | 只能按目标规格逐项吸收。对本轮“章节随产品调整”“存量现状摸排需证据决定”“不为单份 PRD 生成 Roadmap”的边界，不以旧草案覆盖。 |

以上处理不改变 Documents 工作树文件。其当前未提交状态由该工作树的 Git 状态保留。

## 视觉和真实宿主限制

4.1.0 隔离实战回归已通过本地 HTTP 服务打开第二轮冻结 HTML 的隔离副本，并使用 Playwright Chromium 捕获：

- 桌面 1440x1000 初始视图与全页截图。
- 390px 窄屏初始视图与全页截图。
- 打印媒体 PDF。
- 真实点击两步确认卡、版本级内容/视觉确认和导出按钮后的下载 JSON。

实际下载记录通过 4.1.0 校验器。记录中的 D-01/D-02/D-03 方向与勾选值为合成测试数据，不代表用户批准。证据目录：`/Users/helloban/.codex/evals/define-product-and-roadmap-r1/20260930-r3-f473ab25/4.1.0-isolated-regression/`。

技能模板与合成 fixture 之外，被描述产品本身仍未运行，也没有真实 Agent 宿主执行 R1 三项语义工作或外部平台操作。

## 发布包与分支状态

已生成 `dist/define-product-and-roadmap-4.0.0.zip` 和 SHA-256 文件，并逐文件对照技能源码。包仅供审阅；没有合并、安装或发布。所有实施改动仍留在 `codex/prd-output-spec` 工作树，且未提交。

## 4.1.0 发布状态

已生成 `dist/define-product-and-roadmap-4.1.0.zip` 和 SHA-256 文件，并通过 `scripts/check_project.py --verify-dist` 逐文件对照技能源码。包仅供审阅；没有合并、安装或发布。4.1.0 实施改动留在 `codex/prd-output-spec` 工作树，未提交。
