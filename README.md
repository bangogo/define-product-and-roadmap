# Define Product and Roadmap Skill

This repository is the versioned, project-local source of truth for `define-product-and-roadmap`.

## Locations

| Purpose | Path |
|---|---|
| Original user-level source, preserved unchanged | `/Users/helloban/.codex/skills/define-product-and-roadmap` |
| Canonical project source | `skills/define-product-and-roadmap` |
| Codex project discovery | `.agents/skills/define-product-and-roadmap` |
| Claude Code project discovery | `.claude/skills/define-product-and-roadmap` |
| Portable release archives | `dist/` |

The Codex and Claude Code paths are relative symlinks to the same canonical directory. Edit only `skills/define-product-and-roadmap`; never maintain divergent copies.

## What the Skill does

The Skill creates, audits, rewrites, and aligns evidence-backed product PRDs and experience Roadmaps. It distinguishes the product user from reviewers and operators, separates current proof from target behavior, selects product-shape and risk contracts, derives versions from the first value bottleneck, and keeps document approval separate from implementation or release authority.

It does not replace technical architecture, implementation planning, user research, legal review, security review, runtime testing, usability testing, or business approval.

## Use in Codex

Start a new Codex task from this repository root so project Skill discovery sees `.agents/skills`:

```text
$define-product-and-roadmap 审计当前 PRD 和 Roadmap，只报告问题，不修改文件。
```

If a user-level Skill with the same name is also installed, start a fresh task and name the exact project path in the request: `.agents/skills/define-product-and-roadmap/SKILL.md`. Same-name precedence can vary by host/session; confirm the loaded path before accepting an evaluation result.

For creation or rewrite, name the desired files and authorization explicitly:

```text
$define-product-and-roadmap 基于当前 README、正式产品文档、ADR 和运行证据，重写 PRD 与 Roadmap；保留原文件并给出变更摘要。
```

## Use in Claude Code

Start Claude Code from this repository root. The project Skill is available as:

```text
/define-product-and-roadmap 审计当前 PRD 和 Roadmap，只报告问题，不修改文件。
```

Claude Code loads project skills from `.claude/skills`. The symlink keeps Claude on the same tested bytes as Codex.

This release proves Claude Code discovery on the local CLI. Its full audit execution remained blocked in the tested local host because that session did not expose `Read` or `Bash`; see `docs/test-report.md`. Do not turn discovery into an execution-pass claim.

## Use in another Agent Skills-compatible host

Use either method:

1. Point the host at `skills/define-product-and-roadmap`.
2. Extract `dist/define-product-and-roadmap-<version>.zip` into the host's supported skills directory.

The portable contract is the `SKILL.md` frontmatter (`name` and `description`), Markdown instructions, relative references, templates, and Python 3 standard-library scripts. `agents/openai.yaml` is optional OpenAI UI metadata; hosts that do not understand it can ignore it.

## Quality gates

Run all project checks:

```bash
python3 scripts/check_project.py
```

Run the product-document validator directly:

```bash
python3 skills/define-product-and-roadmap/scripts/validate_product_docs.py \
  --prd /absolute/path/to/product-requirements.md \
  --roadmap /absolute/path/to/product-roadmap.md
```

The validator proves Markdown structure, canonical states, selected contract coverage, IDs, and cross-document consistency. It does not prove the underlying facts or product quality. Apply the bundled semantic rubric and record fresh-context results separately.

## Version and release workflow

1. Edit the canonical Skill only.
2. Update both `VERSION` files and `CHANGELOG.md`.
3. Run `python3 scripts/check_project.py`.
4. Run representative fresh-context evaluations and record their actual status.
5. Build with `python3 scripts/package_skill.py`.
6. Re-run `python3 scripts/check_project.py --verify-dist`.
7. Commit, create an annotated Git tag, and keep the ZIP plus checksum under `dist/`.

Use MAJOR for contract-breaking document or invocation changes, MINOR for backward-compatible capability changes, and PATCH for fixes that do not change the public contract.

## Evidence reports

- `docs/audit-report.md`: baseline findings, repairs, and remaining limits.
- `docs/test-report.md`: exact executed checks and proof boundaries.
- `evals/cases.jsonl`: trigger and semantic evaluation inventory.
