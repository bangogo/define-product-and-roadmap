# Claude Code compatibility result

## v2.0.1 — execution pass (2026-08-10)

- Host: Claude Code (model `claude-fable-5`) with `Read` and `Bash` available.
- Invocation: `Skill` tool → `define-product-and-roadmap`, operation `audit only` against `evals/fixtures/audit-only`.
- Loaded directory: `.claude/skills/define-product-and-roadmap` (symlink to the canonical source).
- Discovery result: pass.
- Runtime result: pass — both fixture files read, `validate_product_docs.py` executed (49 errors), 12-dimension semantic self-review scored 0/24 `semantic_fail`, fixture bytes unchanged.
- Accepted artifact: `test-results/claude/audit-only-execution.txt`.
- Proof boundary: structural audit + semantic self-review only. Not runtime proof, user evidence, or approval.

## v2.0.0 — discovery only, execution blocked (2026-08-09, superseded)

Claude Code 2.1.226 loaded `/private/tmp/dpr-claude-v2.wZLPwS/.claude/skills/define-product-and-roadmap`, proving project discovery. Two non-interactive attempts then reported that the local session exposed neither `Read` nor `Bash`; it made no edits and did not claim a fabricated result. No artifact was accepted.

The v2.0.0 block was an environment limitation (host tool exposure), not a skill defect, and is resolved by the v2.0.1 run above.
