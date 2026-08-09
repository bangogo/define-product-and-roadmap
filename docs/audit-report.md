# Define Product and Roadmap Skill v2.0.0 Audit

## Conclusion

The imported Skill already had a useful product-first core and a deterministic validator, but it was not yet reliable enough to treat as a portable, versioned audit product. Version 2.0.0 closes the largest gaps: evidence provenance, runtime truth, product shape, risk modifiers, authority, approval readiness, exact-byte validation, semantic scoring, project discovery, packaging, and release evidence.

The release is suitable for project-local Codex use and portable Agent Skills distribution. Claude Code discovery is proven, but Claude-side execution is conditional because the tested local Claude host did not expose file or shell tools. No test here proves a real product, user outcome, implementation, publication, or approval.

## Scope and sources

The audit covered the complete original directory at `/Users/helloban/.codex/skills/define-product-and-roadmap`, the migrated project package, its scripts, fixtures, generated artifacts, and live host invocations. The original directory was preserved unchanged. Its imported bytes are recorded in `docs/baseline-source-sha256.txt`, Git commit `dc5a8c0`, and tag `v1.0.0-imported`.

The design was checked against current first-party or specification-owner guidance:

- [OpenAI: Build skills](https://developers.openai.com/plugins/build/skills)
- [OpenAI: Build skills in ChatGPT](https://learn.chatgpt.com/docs/build-skills)
- [Agent Skills specification](https://agentskills.io/specification)
- [Claude Code: Extend Claude with skills](https://code.claude.com/docs/en/skills)

Applied guidance includes a required `SKILL.md`, minimal portable frontmatter, trigger-oriented descriptions, progressive loading, deterministic scripts for repeatable work, project-local discovery, relative references, fresh-session evaluation, and explicit separation between discovery and execution.

## Capability status

| Surface | Mentioned | Declared | Available | Executed | Accepted result |
|---|---|---|---|---|---|
| Canonical package | Yes | `SKILL.md` + `VERSION` | `skills/define-product-and-roadmap` | Structural and package checks | Yes, v2.0.0 source |
| Codex project Skill | Yes | `.agents/skills` + `agents/openai.yaml` | Symlink resolves to canonical source | Three valid project-path invocations plus one invalid same-name run excluded | Yes, generation and audit evidence |
| Claude Code project Skill | Yes | `.claude/skills` | Symlink resolves and Claude reports the exact directory | Discovery executed; document audit blocked by missing local tools | Discovery only; no accepted audit artifact |
| Other Agent Skills host | Yes | Standard `name` and `description`, relative resources and scripts | Portable ZIP | No unnamed third-party host was executed | Conditional portability only |

## Baseline assessment

### What was already strong

- Product value and current effect came before implementation planning.
- PRD and Roadmap were treated as one aligned contract.
- Product shape influenced requirements instead of forcing one interface template.
- A Python validator and 20 regression cases already existed.
- Historical plans and target behavior were explicitly distinguished from current proof.

### Material gaps found

| Gap | Risk | v2 repair |
|---|---|---|
| No packaged version or immutable baseline | Changes could not be reproduced or rolled back cleanly | Git baseline commit/tag, semantic versions, changelog, deterministic ZIP and checksum |
| No project-local multi-host layout | Users could copy divergent Skill trees | One canonical source with `.agents` and `.claude` symlinks |
| Evidence source and runtime truth could be conflated | A document statement could be presented as real behavior | Separate evidence ledger classifications from canonical truth states |
| AI and external operations were easy to model as product shapes | Risk controls and product value could become mixed | Independent risk modifiers and matching control contracts |
| Audit/create/rewrite authority was implicit | Audit-only work could mutate files; approval could be over-read | Explicit operation modes, mutation limits, and next-gate authority |
| Structural success could sound like product proof | False confidence in runtime or user value | Machine-readable proof boundary plus 12-dimension semantic rubric |
| Module and capability naming was under-specified | One letter could refer to multiple modules | Distinct module letters, aligned capability prefixes, cross-document checks |
| Whole-document capability regex produced false positives | `G1` gates could be rejected as capability codes | Scope capability checks to hierarchy and version capability cells |
| Reuse/license wording could be inferred | Unknown legal or version state could be overstated | Pinned revision/license fields and mandatory `未声明` when unknown |
| No forward-test corpus or host evidence | Unit tests alone could be mistaken for usefulness | Trigger inventory, three shapes of semantic fixtures, live generation and audit runs |

## v2 product contract

The Skill now distinguishes four operations (`audit only`, `create`, `rewrite`, `align`), six primary product shapes, up to two secondary shapes, seven risk modifiers, seven evidence stages, six delivery purposes, five document states, seven version states, eight truth states, and four assumption types.

The PRD and Roadmap publish the same version, evidence cutoff, shape, risk, lifecycle, purpose, applicable contracts, readiness, modules, assumptions, and next authority. The validator checks those structures and alignments; the semantic rubric separately judges evidence quality and product usefulness across 12 dimensions.

## Effectiveness evidence

- A C-end fixture produced aligned documents and passed exact-byte validation while retaining an unresolved assumption warning.
- A content/artifact fixture initially failed with 41 actionable errors, repaired itself from validator diagnostics, then passed with one honest approval warning and self-scored `20/24 semantic_pass`.
- A fresh-context audit of the accepted content/artifact pair passed structurally and scored `22/24 semantic_pass`; the weakest dimensions were current evidence and reuse ownership.
- An intentionally bad audit-only pair was not edited, failed with 49 structural errors, and was correctly judged `0/24 semantic_fail`. The review identified target-as-current promotion, product-shape conflict, and a technical-task roadmap.
- A regression test created after the live run proves `G1` gate identifiers are no longer false capability positives.

These results show useful generation, self-repair, and rejection behavior. They remain document-level evidence, not product runtime or user evidence.

## Remaining limits and release judgment

1. Deterministic validation checks structure and cross-document consistency, not whether source claims are true or whether the product direction is good.
2. Semantic reviews are model judgments. The recorded reviewers labeled themselves self-review, not independent, even when invoked in a fresh context.
3. The live fixtures are synthetic and bounded. No real project stakeholder approved their product decisions.
4. The local Codex default model could not run because Codex CLI 0.142.5 was rejected as too old for that model; successful runs used `gpt-5.4`. This is an environment issue, not a Skill pass.
5. Same-name user and project Skills can create ambiguous host selection. Exact-path invocation and loaded-path reporting are required for acceptance tests.
6. Claude Code loaded the correct project directory but the local non-interactive host exposed no local read/shell tools. Claude execution is therefore `blocked_environment`, not passed.
7. Other Agent Skills-compatible hosts are package-compatible by structure; their runtime behavior remains unexecuted until tested in that host.

Release judgment: `v2.0.0` is accepted for versioned project-local use and portable distribution, with Claude runtime and unnamed-host runtime explicitly conditional. It is not evidence that any downstream PRD is approved or any product is built.
