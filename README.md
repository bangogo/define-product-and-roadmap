# define-product-and-roadmap

基于证据创建、审计、重写或修订 PRD 与体验 Roadmap 的 Agent Skill。当前版本见 [`VERSION`](VERSION)。

## 交付方式

- 新建、增量修订、重写 PRD：默认交付一份 HTML 审阅稿，包含正文、目录、图表和确认入口；按需读取 [`SKILL.md`](skills/define-product-and-roadmap/SKILL.md) 中的细则。用户明确要求其他格式时遵从要求。
- 仅审计：指出确切版本的问题位置、证据等级、影响和修订建议，不改被审文档。
- Roadmap：只在用户需要版本编排时创建。只请求 PRD 时不生成临时 Roadmap。
- 旧 Markdown PRD/Roadmap 仍保留原校验入口，供既有文档兼容使用。

## 安装

### 在本仓库中使用

```bash
git clone https://github.com/bangogo/define-product-and-roadmap.git
cd define-product-and-roadmap
python3 scripts/check_project.py
```

仓库包含项目级技能发现链接：Claude Code 使用 `.claude/skills/`，Codex 使用 `.agents/skills/`，WorkBuddy 使用 `.workbuddy/skills/`，CodeBuddy 使用 `.codebuddy/skills/`。在仓库目录中启动相应宿主即可使用其发现的技能。

### 安装到用户级目录

在克隆仓库后，从仓库根目录运行所需平台对应命令：

```bash
# Claude Code
mkdir -p ~/.claude/skills
ln -sfn "$PWD/skills/define-product-and-roadmap" ~/.claude/skills/define-product-and-roadmap

# Codex
mkdir -p ~/.codex/skills
ln -sfn "$PWD/skills/define-product-and-roadmap" ~/.codex/skills/define-product-and-roadmap

# WorkBuddy
mkdir -p ~/.workbuddy/skills
ln -sfn "$PWD/skills/define-product-and-roadmap" ~/.workbuddy/skills/define-product-and-roadmap

# CodeBuddy
mkdir -p ~/.codebuddy/skills
ln -sfn "$PWD/skills/define-product-and-roadmap" ~/.codebuddy/skills/define-product-and-roadmap
```

这些命令适用于 macOS/Linux shell。链接目标依赖仓库位置；移动仓库后需重建链接。`ln -sfn` 适用于既有符号链接，若目标位置已有同名真实目录，应先检查并自行迁移该目录，避免链接落入目录内部。

如果宿主提供本地 Skill 包导入功能，可使用 `dist/define-product-and-roadmap-<版本>.zip`；具体导入步骤以该宿主当前界面为准。发布包由 `scripts/package_skill.py` 生成。

## 校验与维护

```bash
python3 scripts/check_project.py
python3 scripts/package_skill.py
python3 scripts/check_project.py --verify-dist
```

`check_project.py` 检查项目级发现链接、技能元数据、回归测试和脚本；`--verify-dist` 还会逐文件比较发布包与技能源码。它们是静态/确定性检查，不代表语义质量、实际渲染、真实宿主调用或用户效果已经通过。

HTML PRD 源稿修改后，用 `skills/define-product-and-roadmap/scripts/stamp_html_prd.py <path>` 重算内容指纹，再运行：

```bash
python3 skills/define-product-and-roadmap/scripts/validate_product_docs.py --prd-html <path>
```

决定记录使用 `--decisions <path>`，并须绑定卡片声明的稳定方向 ID。4.1.0 起不采纳 4.0 的无方向确认记录；修订和重写 HTML 内必须提供逐项迁移表。旧 Markdown 入口为 `--prd <PRD.md> --roadmap <Roadmap.md>`。本轮升级的来源、映射和证据边界分别见 [`spec.md`](spec.md)、[`problem.md`](problem.md)、[`acceptance-map.md`](evals/prd-output-spec/acceptance-map.md) 与 [`验证报告`](evals/prd-output-spec/validation-report.md)。`problem.md` 是历史问题及来源索引，不表示 22 项仍是当前缺陷；案例 PRD 状态独立管理。
