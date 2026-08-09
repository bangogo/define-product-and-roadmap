# Evidence, Product Shape, and Clarification Contract

## Contents

1. Operation and authority
2. Evidence and current-effect snapshot
3. Product-shape classification
4. Risk modifiers and delivery purpose
5. Question and divergence workflow
6. Assumption register and completion gate

## Operation and authority

Classify the requested operation before changing files:

| Operation | Allowed result | Default mutation rule |
|---|---|---|
| Audit only | Findings, evidence, severity, and repair proposal | Do not edit product documents |
| Create | New PRD, Roadmap, or aligned pair | Create only requested deliverables |
| Rewrite | Replacement document plus material-change summary | Preserve originals through version control or a new path |
| Align | Reconcile an existing PRD/Roadmap pair and current-state entrypoint | Touch only required files; preserve project authority |

Record the reviewer, requested decision, and exact next gate. A product contract can authorize only that gate. It cannot silently authorize Build, publication, live accounts, sensitive-data use, transactions, or external writes.

## Evidence and current-effect snapshot

Build this private brief before drafting:

| Field | Required result |
|---|---|
| Product user | Person or team receiving lasting product value |
| Core task | Recognizable job the product user needs to complete |
| Current effect | What the product currently lets the user do or receive |
| Value surface | Where the benefit becomes visible or usable |
| Value path | Shortest route from trigger or input to meaningful result |
| Value bottleneck | First missing or weak transition that blocks the result |
| Existing foundation | Working pages, artifacts, data, interfaces, services, Skills, or processes |
| Truth boundary | Frontend, backend, data, model, external service, manual, permission, and output state |
| Delivery purpose | Decision demo, user-value validation, production improvement, integration validation, real pilot, or scale |
| Review gate | Reviewer, requested decision, and next gate activated |

Maintain a compact evidence ledger for every material conclusion:

| Claim or observation | Classification | Source | Date/revision | Confidence | Conflict or limitation |
|---|---|---|---|---|---|

Use these classifications:

- `已确认决策`: explicitly approved and still authoritative;
- `已观察证据`: directly inspected current behavior or artifact;
- `文档记载`: stated by a current document but not independently observed;
- `历史证据`: useful precedent that may be stale;
- `建议假设，待确认`: reversible or material proposal awaiting a decision;
- `待调研`: external or project fact that cannot safely be inferred.

When sources conflict, prefer the higher-authority and newer source only after confirming it still governs the same scope. Publish the conflict if it changes the product direction or approval readiness.

Use this current-effect table in the PRD:

| 观察对象 | 当前效果 | 证据状态 | 证据来源 | 当前缺口 |
|---|---|---|---|---|

The ledger classifications above describe where a claim came from. They are not runtime truth states. In the published current-effect table, the column named `证据状态` uses only the canonical truth states `真实`, `测试接入`, `模拟`, `人工承接`, `仅有文档`, `已观察`, `尚未验证`, and `历史证据`. The same set applies to every published `真实性` cell. A target becomes current only after evidence exists at the declared level. A command exit code, HTTP 200, fixture, transcript, or document statement proves only its own layer.

## Product-shape classification

Classify through six dimensions:

| Dimension | Choices and test |
|---|---|
| Primary beneficiary | Consumer, business user, internal operator, creator, developer, buyer/seller, or service staff |
| Primary value surface | Consumer interface, content/artifact production, internal workflow, API/platform, service orchestration, marketplace, or physical/hybrid |
| Evidence stage | Idea, static design, interactive prototype, test integration, limited real use, or live/scale |
| Delivery purpose | Decision demo, user-value validation, production improvement, integration validation, real pilot, or scale |
| Value bottleneck | Comprehension, activation, task completion, artifact quality, throughput, reliability, adoption, handoff, trust, or cost |
| Risk modifier | AI, sensitive data, external write, third-party reuse/license, publishing, transaction, or high-stakes decision |

Select exactly one primary shape from:

- `C端交互产品`
- `内容/产物生产`
- `内部流程工具`
- `API/平台`
- `服务编排`
- `交易/市场`

Select no more than two secondary shapes from the same list. For a hybrid product, name the primary value surface rather than labeling every surface equally. Put AI and risk conditions in `风险修饰项`, not `次级形态`.

### Shape-specific observation lenses

| Product shape | Inspect first | Meaningful result |
|---|---|---|
| C-end interaction | Page inventory, entry points, information hierarchy, user route, state transitions, mobile/accessibility | User completes a task and understands the result |
| Content/artifact production | Input contract, stages, intermediate/final artifacts, quality, provenance, review, recovery | User receives a usable and reviewable artifact |
| Internal workflow | Roles, trigger, queue, decisions, approval, handoff, exception, audit | Operator completes a real work item |
| API/platform | Consumer, onboarding, first success, contract, examples, self-service, compatibility, reliability | A new consumer reaches first successful use |
| Service orchestration | Touchpoints, providers, responsibility, online/offline handoff, return and support | User receives the service outcome, not only a link |
| Marketplace | Both sides, discovery, match, trust, transaction, fulfillment, settlement, dispute | Both sides complete a protected exchange |

## Risk modifiers and delivery purpose

Publish zero or more canonical modifiers: `AI`, `敏感数据`, `外部写入`, `第三方复用`, `发布`, `交易`, or `高风险决策`. Use `无` only after checking each modifier.

An AI assistant or Agent is normally a modifier, not a primary shape. Inspect its trigger, context, role, control, action boundary, output, uncertainty, feedback, fallback, and evaluation. A transaction can be both the primary marketplace surface and a risk modifier.

Use these canonical delivery purposes:

- `决策演示`
- `用户价值验证`
- `生产改进`
- `集成验证`
- `真实试点`
- `规模化`

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

Resolve project facts from evidence. Ask only when an answer changes user, value surface, delivery purpose, primary bottleneck, route order, fidelity, truth boundary, or acceptance.

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

Select a direction before publishing the formal contract. Preserve only the chosen direction, remaining assumptions, and open decisions in the PRD/Roadmap. Keep raw dialogue and rejected options in working context unless the user requests a decision log.

## Assumption register and completion gate

Publish the same material assumptions in both documents:

| 类型 | 假设或决策 | 状态 | 依据 | 对产品影响 | 确认人/下一步 |
|---|---|---|---|---|---|

Canonical types:

- `必须为真`: the chosen product direction fails if false;
- `重要假设`: materially changes scope or value but allows a draft;
- `可逆默认`: low-risk choice that can be changed later;
- `高风险外部事实`: requires research or authority rather than inference.

Canonical statuses: `已确认`, `建议假设，待确认`, `待调研`, or `已否决`.

Only confirmed items may appear as product facts. Any unresolved or denied `必须为真` item makes the document `Proposed / Not approval-ready`. Stop questioning when the user, value surface, current effect, delivery purpose, bottleneck, primary route, truth boundary, and next gate are stable; defer implementation detail to the active technical Spec.
