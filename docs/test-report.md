# Define Product and Roadmap Skill v2.0.0 Test Report

## Result summary

| Layer | Result | Evidence boundary |
|---|---|---|
| Imported baseline | Pass | Exact original copy; 20 tests and OpenAI quick validation passed |
| v2 contract tests | Pass, 35/35 | Validator behavior only |
| Python compilation | Pass | Script syntax/import compilation only |
| OpenAI `quick_validate` | Pass | Skill package structure and metadata only |
| Project discovery links | Pass | Both symlinks resolve to the canonical source |
| Codex C-end generation | Pass with 1 expected warning | Project Skill invocation and document artifact |
| Codex artifact generation | Pass, self-review 20/24 | Project Skill invocation, structural pass, semantic self-review |
| Codex artifact audit | Pass, 22/24 | Fresh-context document audit; reviewer labeled not independent |
| Codex audit-only negative case | Correct fail, 49 errors, 0/24 | Bad-document detection and no-edit behavior |
| Claude Code discovery | Pass | Correct `.claude/skills` directory loaded |
| Claude Code audit execution | Blocked | Local host exposed no `Read` or `Bash`; no accepted artifact |
| Portable ZIP | Pass | Archive contents, checksum, extracted validation, and source equality |

## Deterministic checks

Run from the repository root:

```bash
python3 scripts/check_project.py
```

The gate validates required files, portable frontmatter, relative links, version alignment, project discovery symlinks, evaluation schema, 35 regression cases, Python compilation, and OpenAI `quick_validate.py`.

Regression coverage includes all six primary shapes, secondary shapes, AI and transaction risk, missing contracts, invalid truth and lifecycle states, unresolved assumptions, metadata mismatch, duplicate metadata, version gaps, requirement/module mapping, unsourced numeric targets, open markers, empty tables, broken links, distinct capability naming, `G1` gate scoping, and support for module letter `L`.

## Live Codex evaluations

### C-end creation

- Invocation: isolated repository, exact project `.agents/skills` path.
- Result: created an aligned PRD/Roadmap pair and passed exact validation with one unresolved-assumption warning.
- Accepted evidence: `test-results/codex/cend/`.
- Boundary: invocation and document artifact; not product runtime or user proof.

### Content/artifact creation

- Invocation: isolated repository, exact project `.agents/skills` path, `evidence/README.md` as the only product fact source.
- First validator run: failed with 41 errors, including truth-label misuse and non-unique module/capability codes.
- Recovery: the Agent used diagnostics to repair the pair.
- Final validator run: passed with one unresolved `必须为真` warning.
- Semantic self-review: `20/24 semantic_pass`; correctly `Not approval-ready`.
- Accepted evidence: `test-results/codex/artifact/`.
- Boundary: skill invocation, self-repair, exact document bytes, and self-review; not independent judgment or product proof.

### Fresh-context audit of the accepted artifact pair

- Exact final v2 project Skill loaded.
- Validator: pass with one unresolved-assumption warning.
- Semantic score: `22/24 semantic_pass`.
- Weakest dimensions: current effect/evidence and reuse/ownership.
- Review label reported by the Agent: self-review performed, not independent.
- Accepted evidence: `test-results/codex/independent-audit/final.txt`.

### Audit-only negative case

- Input: intentionally incomplete and contradictory PRD/Roadmap fixture.
- Mutation check: target fixture files remained unchanged; only the CLI final-message file was untracked.
- Validator: `49 errors, 0 warnings`.
- Semantic result: `0/24 semantic_fail`.
- Correct findings: next-version plan promoted to current truth, PRD/Roadmap shape and purpose conflicts, technical task list used as a Roadmap, missing user/value/evidence/authority contracts.
- Accepted evidence: `test-results/codex/audit-only/final.txt`.

### Excluded and blocked runs

- One content/artifact attempt loaded the user-level same-name Skill instead of the project copy. It was interrupted and excluded from acceptance evidence.
- The configured default model failed before Skill work with a server response requiring a newer Codex version. Successful acceptance runs explicitly used `gpt-5.4`.

## Claude Code evaluation

Claude Code 2.1.226 loaded the exact directory `/private/tmp/dpr-claude-v2.wZLPwS/.claude/skills/define-product-and-roadmap`, proving project discovery. Two audit attempts then reported that the host exposed neither local `Read` nor `Bash`, including an attempt with default tools and bypassed permission prompts. No document result was accepted. See `test-results/claude/discovery-blocked.md`.

Status taxonomy:

- Mentioned: Claude compatibility is a release goal.
- Declared: standard Skill frontmatter and `.claude/skills` path exist.
- Available: Claude loaded the exact project directory.
- Executed: discovery ran; audit execution stopped at missing host tools.
- Accepted artifact: none.
- Semantic/product proof: not run.

## Package verification

The release build ran:

```bash
python3 scripts/package_skill.py
python3 scripts/check_project.py --verify-dist
```

Verification confirmed a root `define-product-and-roadmap/SKILL.md`, matching internal `VERSION`, excluded caches and editor files, and a matching SHA-256 checksum. The archive was extracted to a new temporary directory, passed OpenAI `quick_validate.py`, and matched the canonical Skill directory with `diff -qr`.

- Archive: `dist/define-product-and-roadmap-2.0.0.zip`
- SHA-256: `1bd8cf4ca464ee195b733952e7500cbcbad31496c718080c8c70d12eadb69f5c`
- Contract tests: `35/35 passed`
- Project gate with `--verify-dist`: passed
