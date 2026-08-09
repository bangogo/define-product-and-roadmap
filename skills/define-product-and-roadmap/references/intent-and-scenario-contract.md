# Evidence, Product Shape, and Clarification Contract

## Contents

1. Evidence and current-effect snapshot
2. Product-shape classification
3. Delivery purpose and value bottleneck
4. Question and divergence workflow
5. Assumption register and completion gate

## Evidence and current-effect snapshot

Build this private brief before drafting:

| Field | Required result |
|---|---|
| Product user | Person or team receiving the product value |
| Core task | Recognizable task the user needs to complete |
| Current effect | What the product currently lets the user do or receive |
| Evidence | Screen, route, artifact, output, record, interface, research, or observed result |
| Evidence status | Confirmed decision, observed, documented, simulated, test, manual, or unverified |
| Value surface | Where the user actually receives the benefit |
| Delivery purpose | Decision demo, user validation, production improvement, integration, pilot, or scale |
| Value path | Shortest route from trigger or input to meaningful result |
| Value bottleneck | First missing or weak transition that blocks the result |
| Existing foundation | Working pages, content, data, interfaces, services, Skills, or processes |
| Truth boundary | Frontend, backend, data, external service, model, manual, and permission state |
| Review gate | Reviewer, requested decision, and next gate activated |

Use this published snapshot table:

| Observation | Current effect | Evidence status | Evidence source | Current gap |
|---|---|---|---|---|

Separate current and target behavior. A target becomes current only after evidence exists at the declared level.

## Product-shape classification

Classify through six dimensions:

| Dimension | Choices and test |
|---|---|
| Primary beneficiary | Consumer, business user, internal operator, creator, developer, buyer/seller, or service staff |
| Primary value surface | Consumer interface, content/artifact production, internal workflow, API/platform, service orchestration, marketplace, or physical/hybrid |
| Evidence stage | Idea, static design, interactive prototype, test integration, limited real use, or live/scale |
| Delivery purpose | Decision demo, user validation, production improvement, integration validation, real pilot, or scale |
| Value bottleneck | Comprehension, activation, task completion, artifact quality, throughput, reliability, adoption, handoff, or cost |
| Risk modifier | AI, sensitive data, external write, third-party reuse/license, publishing, transaction, or high-stakes decision |

Select one primary shape and up to two secondary shapes. For a hybrid product, name the primary value surface instead of labeling every surface equally.

### Shape-specific observation lenses

| Product shape | Inspect first | Meaningful result |
|---|---|---|
| C-end interaction | Page inventory, entry points, information hierarchy, user route, state transitions, mobile/accessibility | User completes a task and understands the result |
| Content/artifact production | Input contract, production stages, intermediate/final artifacts, quality, provenance, review, recovery | User receives a usable and reviewable artifact |
| Internal workflow | Roles, trigger, queue, decisions, approval, handoff, exception, audit | Operator completes a real work item |
| API/platform | Consumer, onboarding, first success, contract, examples, self-service, compatibility, reliability | A new consumer reaches first successful use |
| Service orchestration | Touchpoints, providers, responsibility, online/offline handoff, return and support | User receives the service outcome, not only a link |
| Marketplace | Both sides, discovery, match, trust, transaction, fulfillment, settlement, dispute | Both sides complete a protected exchange |

AI assistant or Agent is usually a secondary shape or risk modifier. Inspect its trigger, context, role, control, action boundary, output, uncertainty, feedback, fallback, and evaluation.

## Delivery purpose and value bottleneck

Keep four roles separate:

| Role | Complete task | Evidence produced |
|---|---|---|
| Product user | Receives the lasting product value | Task, outcome, quality, or behavior evidence |
| Reviewer | Decides investment or the next delivery gate | Approval record and bounded next action |
| Operator | Performs manual or operational work | Handoff, audit, or support evidence |
| Technical owner | Delivers and maintains the declared boundary | Interface, state, recovery, and verification evidence |

Derive priority by asking:

1. Which user result matters most?
2. Where does that result become visible or usable?
3. Which parts already work and should remain reuse dependencies?
4. Which first transition prevents the result today?
5. Which evidence would change the next investment decision?

## Question and divergence workflow

Resolve project facts from evidence. Ask when an answer changes user, value surface, delivery purpose, primary bottleneck, route order, fidelity, truth boundary, or acceptance.

Use one question at a time:

```text
Evidence: what the project currently shows.
Recommended interpretation: the direction most consistent with the evidence.
Question: one high-impact choice.
Impact: what changes under each answer.
```

When several directions remain credible, compare 2–3 alternatives:

| Direction | User value | Business value | Feasibility | Differentiation | Evidence strength | Recommendation |
|---|---|---|---|---|---|---|

Select a direction before publishing the formal contract. Preserve only the chosen direction, remaining assumptions, and open decisions in the PRD/Roadmap.

## Assumption register and completion gate

Use:

| Type | Assumption or decision | Status | Evidence | Product impact | Confirmer or next step |
|---|---|---|---|---|---|

Canonical types:

- `必须为真`: the chosen product direction fails if false;
- `重要假设`: materially changes scope or value but allows a draft;
- `可逆默认`: low-risk choice that can be changed later;
- `高风险外部事实`: requires research or authority rather than inference.

Canonical statuses: `已确认`, `建议假设，待确认`, `待调研`, `已否决`.

Only `已确认` items may appear as product facts. An unresolved or denied `必须为真` item makes the document `Proposed / Not approval-ready`. Stop questioning when the user, value surface, current effect, delivery purpose, bottleneck, primary route, and truth boundary are stable; defer implementation detail to the active Spec.
