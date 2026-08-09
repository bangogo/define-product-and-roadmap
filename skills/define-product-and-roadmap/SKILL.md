---
name: define-product-and-roadmap
description: Create, audit, rewrite, or align evidence-backed product PRDs and experience Roadmaps. Use for 产品需求文档, PRD, 产品价值, 产品形态, 当前效果, 用户路径, 内容或产物生产, 内部工作流, API/平台, 服务编排, marketplace, AI 助手, MVP, 体验版本, 复用决策, 风险边界, 假设确认, or approval readiness. Do not use for a standalone engineering task list, technical architecture, marketing plan, or implementation-only review unless the user also needs a product contract.
---

# Define Product and Roadmap

Create one readable product contract that states who receives value, what the product currently proves, where the first value bottleneck sits, and which evidence unlocks the next version.

## Load only the needed resources

1. Always read [references/intent-and-scenario-contract.md](references/intent-and-scenario-contract.md) before classifying the product or asking questions.
2. Read [references/prd-contract.md](references/prd-contract.md) for PRD creation, audit, or rewrite.
3. Read [references/roadmap-contract.md](references/roadmap-contract.md) for Roadmap creation, audit, or rewrite.
4. Read [references/revision-lessons.md](references/revision-lessons.md) when auditing, revising, or incorporating feedback.
5. Read [references/quality-rubric.md](references/quality-rubric.md) before the final semantic review.
6. Use [assets/prd-template.md](assets/prd-template.md) and [assets/roadmap-template.md](assets/roadmap-template.md) only when creating new files or repairing a document whose structure is unusable.

## 1. Establish scope and authority

Identify the requested operation: `audit only`, `create`, `rewrite`, or `align`. Identify whether the user needs a PRD, a Roadmap, or an aligned pair, and whether the delivery target is a file or chat Markdown.

Do not edit files during an audit-only request. Treat approval of a document as permission only for the named next gate; it does not authorize implementation, publication, account access, or external writes.

## 2. Read authoritative evidence

Read the smallest relevant evidence set in this order:

`approved product contract → accepted decisions → current runtime or artifact evidence → current research → historical material`

Inspect current README, formal product documents, accepted ADRs or decisions, research, archives, and relevant runtime or artifacts before drafting. Resolve discoverable facts before asking the user. Preserve unrelated changes.

Classify every material statement as one of:

- `已确认决策`
- `已观察证据`
- `文档记载`
- `历史证据`
- `建议假设，待确认`
- `待调研`

Record source, date or revision when available, and conflicts. Never turn a target, plan, fixture, successful command, or historical claim into current product proof.

## 3. Build the private product brief

Record the current user and core task, value surface, current result, shortest value path, first weak transition, existing foundation, truth boundary, evidence gaps, delivery purpose, reviewer, requested decision, and next gate.

Use truth labels at the point of use: `真实`, `测试接入`, `模拟`, `人工承接`, `仅有文档`, `已观察`, `尚未验证`, or `历史证据`.

Keep the product user distinct from the reviewer, operator, buyer, approver, and technical owner.

## 4. Classify product shape and risk

Follow [references/intent-and-scenario-contract.md](references/intent-and-scenario-contract.md):

1. Select exactly one primary product shape.
2. Select no more than two secondary product shapes.
3. Record risk modifiers separately; do not disguise AI or external-write risk as a secondary product shape.
4. Name the current delivery purpose.
5. Derive priority from the first missing or weak transition in the value path.

## 5. Close only decision-changing unknowns

Ask one question at a time only when the answer changes the product user, primary value surface, delivery purpose, value bottleneck, route order, truth boundary, or approval readiness. State the evidence, recommended interpretation, question, and consequence of each direction.

When two or more materially different directions remain credible, compare 2–3 alternatives on user value, business value, feasibility, differentiation, and evidence strength. Recommend one and ask for confirmation.

Record assumptions as `必须为真`, `重要假设`, `可逆默认`, or `高风险外部事实`, with status `已确认`, `建议假设，待确认`, `待调研`, or `已否决`. Do not block on wording or implementation detail. If a non-blocking answer is unavailable, use a clearly labeled reversible default. An unresolved or denied `必须为真` item keeps the document `Proposed / Not approval-ready`.

## 6. Draft the selected contracts

Combine the universal contract, the primary-shape contract, materially relevant secondary-shape contracts, and every applicable risk contract.

For a PRD, follow [references/prd-contract.md](references/prd-contract.md). Make the first four H2 sections:

`产品定位与目标 → 目标用户与核心问题 → 当前产品形态、效果与核心缺口 → 产品价值与价值循环`

For a Roadmap, follow [references/roadmap-contract.md](references/roadmap-contract.md). Make the first two H2 sections:

`核心用户任务与演进目标 → 当前基线、价值瓶颈与能力优先级`

Use identical metadata, canonical names, reuse decisions, truth states, assumptions, version status, and approval status across the pair. Give every lasting module a distinct uppercase letter and keep its capability prefix aligned: `A「模块」` owns `A0「能力」`, while the next module uses `B「模块」` and `B0「能力」`. Write requirement and version codes with names at the point of use: `P0-01「要求」` and `R1（第 1 个体验版本）「版本」`.

Keep evidence provenance separate from runtime truth. The private evidence ledger uses `已确认决策`, `已观察证据`, or `文档记载`; published `证据状态` and `真实性` cells use only `真实`, `测试接入`, `模拟`, `人工承接`, `仅有文档`, `已观察`, `尚未验证`, or `历史证据`.

Preserve independently useful production modules as standalone versions. Use thin end-to-end versions when value exists only through a complete journey. Keep filenames, internal classes, commands, and implementation sequencing in the active technical Spec unless they define a lasting public contract.

## 7. Validate the exact deliverable

Run the deterministic validator against the exact bytes being delivered:

```bash
python3 <skill-directory>/scripts/validate_product_docs.py \
  --prd <prd-path> \
  --roadmap <roadmap-path>
```

Run the validator before reading its source. The contracts and templates define the format; use validator diagnostics to repair the document. Read or patch validator source only when a diagnostic is incorrect, unclear, or the user is maintaining this Skill.

If only one document was requested, create a temporary counterpart that states the same metadata and contract, validate the pair, and discard only the temporary file. For chat delivery, materialize the proposed Markdown in a temporary directory and validate those exact bytes.

Fix every error and review warnings. Then apply [references/quality-rubric.md](references/quality-rubric.md) to the exact deliverable. For substantial documents, report the 12-dimension total, semantic result label, approval blockers, weakest dimensions, and whether the review was self-review or independent. A validator pass proves structural consistency only; it does not prove product judgment, runtime behavior, research truth, user value, or approval.

For substantial work, use fresh-context review on the target product and one unlike product shape when the environment supports it. Pass raw evidence and the user request, not the intended answer. Label unrun, blocked, and conditional evaluation honestly.

## Published metadata

Use these fields in both documents:

- `文档版本`
- `证据截止日期`
- `产品主形态`
- `次级形态`
- `风险修饰项`
- `当前证据阶段`
- `当前交付目的`
- `适用产品合同`
- `文档状态`
- `是否具备审批条件`

Write `文档版本` as full semantic versioning such as `1.2.0` or `v1.2.0`, never `v1.2`.

## Hard boundaries

| Boundary | Required handling |
|---|---|
| Product facts | Cite traceable evidence or label assumption, status, impact, and owner |
| Capability truth | Label real, test, simulated, manual, documented, observed, historical, and unverified behavior where used |
| Sensitive data and external writes | Obtain explicit authority before real accounts, uploads, submissions, transactions, or publication |
| Reuse | Record source, pinned revision, license status, callable boundary, exclusions, and project-owned adapter; use `未声明` instead of inferring a license |
| Delivery authority | State the exact next gate; never convert document approval into Build or release authority |
| Validation claims | Separate structural pass, semantic review, runtime proof, user evidence, and external-operation state |

## Finish only when

Business, product, experience, and technical owners can each answer:

1. Who receives value, where, and why the product matters.
2. What works now, what evidence proves it, and where the first bottleneck sits.
3. Which product-shape and risk contracts apply and why.
4. What is reused, adapted, newly built, simulated, manual, or unverified.
5. How the primary journey or production task succeeds and recovers.
6. Why the Roadmap order follows value evidence instead of a generic module sequence.
7. Which assumptions remain and whether the documents are approval-ready.
8. What exact evidence exits the current version and which named gate it activates.
