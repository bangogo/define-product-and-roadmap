---
name: define-product-and-roadmap
description: Create, audit, rewrite, and align product-first PRDs and experience-driven Roadmaps from project evidence. Use for 产品需求文档, PRD, 产品价值, 产品形态, 当前效果, 用户界面, 用户路径, 内容或产物生产, 内部工作流, API/平台, 服务编排, AI 助手, Roadmap, MVP, 体验版本, 复用决策, 主动澄清, 发散方案, or assumption confirmation when product and technical owners need one readable contract.
---

# Define Product and Roadmap

Produce a product contract that reflects how users actually receive value, what the product currently proves, and which evidence should unlock the next version.

## Load the contracts

- Read [references/intent-and-scenario-contract.md](references/intent-and-scenario-contract.md) before classifying the product or asking questions.
- Read [references/prd-contract.md](references/prd-contract.md) for PRD work and load only the product-shape and risk contracts selected by the internal brief.
- Read [references/roadmap-contract.md](references/roadmap-contract.md) for Roadmap work.
- Read [references/revision-lessons.md](references/revision-lessons.md) when auditing, rewriting, or incorporating feedback.

## Workflow

### 1. Read authoritative evidence

Read the smallest relevant evidence set in this order:

`approved product contract → accepted decisions → current runtime or artifact evidence → current research → historical material`

Resolve discoverable facts before asking questions. Preserve each statement as confirmed decision, observed evidence, proposed assumption, open research, or historical evidence.

### 2. Establish the current-effect snapshot

Record the current user and task, working surfaces or production steps, visible results or artifacts, evidence, dead ends, value bottleneck, and truth status. Use `真实`, `测试接入`, `模拟`, `人工承接`, `仅有文档`, `已观察`, or `尚未验证` at the point of use.

Inspect the value surface that matters:

- consumer interface → pages, entry points, user routes, states, mobile behavior, and visible results;
- content or artifact production → inputs, stages, intermediate and final artifacts, quality gates, provenance, review, and recovery;
- internal workflow → roles, queues, handoffs, approvals, exceptions, and audit;
- API or platform → onboarding, first success, contracts, examples, self-service, compatibility, and reliability;
- service orchestration → touchpoints, providers, online/offline handoffs, return states, and recovery;
- marketplace → both sides, discovery, matching, trust, transaction, fulfillment, and disputes.

When execution is unavailable, state `文档记载`, `已观察`, or `尚未验证`; keep target behavior separate from current effect.

### 3. Classify product shape and delivery purpose

Build the internal classification in [references/intent-and-scenario-contract.md](references/intent-and-scenario-contract.md). Select one primary product shape and up to two secondary shapes. Treat AI, sensitive data, external writes, third-party reuse, publishing, and high-stakes decisions as risk modifiers.

Name the current delivery purpose: decision demo, user-value validation, production improvement, integration validation, real pilot, or scale. Keep the product user distinct from the reviewer, operator, buyer, or approver.

### 4. Close high-impact unknowns

Ask one question at a time when the answer changes the product user, primary value surface, delivery purpose, value bottleneck, route order, truth boundary, or approval readiness. State the evidence, the recommended answer, and what changes under each direction.

When two or more materially different directions remain credible, generate 2–3 alternatives and compare user value, business value, feasibility, differentiation, and evidence. Recommend one direction and ask for confirmation.

Record assumptions as `必须为真`, `重要假设`, `可逆默认`, or `高风险外部事实`, with status `已确认`, `建议假设，待确认`, `待调研`, or `已否决`. A document with an unresolved `必须为真` item remains `Proposed / Not approval-ready`.

Stop asking when further answers only refine wording or implementation detail. Keep raw discovery dialogue and discarded alternatives in working context; publish the selected product direction, remaining assumptions, and open decisions.

### 5. Select and draft the contracts

Combine:

1. the universal product contract;
2. the primary product-shape contract;
3. secondary-shape contracts that materially affect value delivery;
4. applicable risk contracts.

Draft the PRD with [references/prd-contract.md](references/prd-contract.md). Draft the Roadmap with [references/roadmap-contract.md](references/roadmap-contract.md). Derive priority from the first missing or weak transition in the value path. Preserve independently useful production modules as standalone versions; use thin end-to-end versions where value exists only through a complete journey.

Deliver the full product contract even when the requested output is chat Markdown. Make the first four PRD H2 sections `产品定位与目标 → 目标用户与核心问题 → 当前产品形态、效果与核心缺口 → 产品价值与价值循环`; make the first two Roadmap H2 sections `核心用户任务与演进目标 → 当前基线、价值瓶颈与能力优先级`. Place executive conclusions inside these product sections. Use every required universal, selected-shape, risk, truth, and assumption table from the loaded contracts.

Use identical canonical names, reuse decisions, truth states, version status, and approval status across PRD, Roadmap, and the current-state entrypoint. Write codes with names at the point of use: `A「模块」`, `A0「能力」`, `P0-01「要求」`, and `R1（第 1 个体验版本）「版本」`.

### 6. Validate and revise

Run:

```bash
python3 <skill-directory>/scripts/validate_product_docs.py --prd <prd-path> --roadmap <roadmap-path>
```

Fix reported locations, rerun the validator, and add project-required link, whitespace, diff, and repository checks. For substantial revisions, forward-test with fresh context on at least the target product and one unlike product shape. Pass raw project evidence and the user request, not the intended answer.

Validate the exact proposed PRD and Roadmap bytes. For chat-only delivery, place the proposed Markdown in a temporary directory, run the same validator, report its actual result, and remove the temporary directory. Existing project documents provide evidence; their validation result does not validate a newly summarized chat proposal.

## Published metadata

Use these fields in both documents:

- `产品主形态`
- `次级形态`
- `当前证据阶段`
- `当前交付目的`
- `适用产品合同`
- `文档状态`
- `是否具备审批条件`

## Hard boundaries

| Boundary | Required handling | Reason |
|---|---|---|
| Product facts | Use traceable evidence or label the assumption, status, and owner | Preserve decision integrity |
| Capability truth | Label real, test, simulated, manual, documented, and unverified behavior where used | Preserve evidence integrity |
| Sensitive data and external writes | Obtain explicit authority before real accounts, uploads, submissions, or publication | Preserve user safety and control |
| Delivery authority | Treat document approval as permission for the named next gate only | Preserve project governance |

## Acceptance

Finish when business, product, experience, and technical owners can each answer their core questions:

1. Who receives value, where value is realized, and why the product matters.
2. What currently works, what evidence proves it, and where the first value bottleneck sits.
3. Which product-shape contracts apply and why they fit the product.
4. What is reused, adapted, newly built, simulated, or still unverified.
5. How the user completes the primary journey or production task and recovers from failure.
6. Why the Roadmap order follows value evidence rather than a generic module sequence.
7. Which assumptions remain and whether the document is approval-ready.
8. What evidence exits the current version and which gate that evidence activates.
