# Changelog

All notable changes to the project-local `define-product-and-roadmap` Skill are recorded here. The project follows Semantic Versioning for the packaged Skill.

## 2.0.1 - 2026-08-10

### Changed

- Claude Code execution evidence upgraded from Blocked to Pass: the project-skill audit-only operation ran in a Claude Code host that exposes `Read` and `Bash`, producing a structural audit (49 errors) and a semantic self-review (0/24 `semantic_fail`) of the audit-only fixture, with fixture bytes left unchanged.
- Added Claude Code audit-execution artifact under `test-results/claude/audit-only-execution.txt`; renamed `test-results/claude/discovery-blocked.md` to `test-results/claude/execution-passed.md`.

### Notes

- No skill-contract change (`SKILL.md`, references, templates, and validator logic are untouched). This is a PATCH release recording the Claude Code execution milestone and refreshed test evidence.

## 2.0.0 - 2026-08-09

### Added

- One canonical Agent Skills package under `skills/define-product-and-roadmap`.
- Project discovery links for Codex and Claude Code.
- Separate risk-modifier metadata and contracts.
- Evidence provenance, document version, evidence cutoff date, lifecycle, and approval rules.
- PRD and Roadmap templates for reliable new-document creation.
- A 12-dimension semantic quality rubric with explicit proof boundaries.
- Machine-readable validator output and project/package validation.
- Trigger, boundary, and semantic evaluation cases.
- Reproducible ZIP packaging with SHA-256 checksum.

### Changed

- Tightened module truth to the formal module table instead of treating every module-like reference as a definition.
- Expanded validation from 20 baseline cases to 35 contract cases.
- Required material assumptions, truth boundaries, and approval metadata to align across PRD and Roadmap.
- Required version IDs, requirement IDs, canonical lifecycle states, non-empty tables, and risk coverage.
- Separated evidence provenance labels from published runtime-truth labels and made module-letter ownership explicit.
- Scoped capability-code validation to capability and version tables so gate IDs such as `G1` are not false positives.
- Clarified that structural validation is not semantic quality, runtime proof, user evidence, or approval.

### Breaking

- Documents now require `文档版本`, `证据截止日期`, and `风险修饰项` metadata.
- Reference/reuse, capability, success, current-delivery, assumption, and gate tables use stronger v2 headers.
- AI is modeled as a risk modifier instead of a secondary product shape.

## 1.0.0-imported - 2026-08-09

- Exact copy of `/Users/helloban/.codex/skills/define-product-and-roadmap` at import time.
- Preserved in Git commit `dc5a8c0` and annotated tag `v1.0.0-imported`.
- Baseline evidence: OpenAI `quick_validate.py` passed; all 20 bundled contract tests passed when invoked directly.
