# Product Requirements Contract

## Contents

1. Universal PRD structure
2. Reference, reuse, requirements, and truth contracts
3. Product-shape contracts
4. Risk contracts and approval readiness

## Universal PRD structure

Use this complete product-facing order. The first four H2 headings carry these concepts in this sequence; place executive conclusions inside them instead of adding a preceding summary section:

1. Metadata, product positioning, and goals.
2. Target users and core problems.
3. Current product shape, current effect, evidence, and value bottleneck.
4. Product value and value loop.
5. Reference products, existing assets, external services, and reuse strategy.
6. Primary product experience or production contract.
7. Product capability architecture and current priority.
8. Product requirements and acceptance.
9. Data, service, state, permission, quality, and recovery boundaries.
10. Current-version scope and truth boundary.
11. Success model, risks, non-goals, assumptions, status, and next gate.

Keep discovery notes, creator-intent analysis, route-pattern rationale, and discarded alternatives in working context. State conclusions in product language.

A requested PRD means the full contract, including current evidence, references, selected shape tables, requirements, truth boundary, and assumptions. A shorter current-version brief applies only when the user explicitly asks for a brief or summary.

## Universal contracts

### Reference and reuse

Place references before the architecture they shape:

| Source | Responsibility | Proven capability | Product mapping | Reuse decision | Project addition | User value | Evidence boundary |
|---|---|---|---|---|---|---|---|

Use consistent modes:

- `「方法借鉴」`: apply a method while the project owns the resulting rules;
- `「原样复用」`: retain a working product capability and build only the named connection;
- `「直接复用」`: call a pinned capability through a bounded adapter after source, version, license, interface, and exclusions are known;
- `「参考复用」`: use structure, constraints, or fixtures as design and test input;
- `「新建」`: own contract, implementation, tests, and maintenance.

Map each module responsibility to one reuse decision and project-owned addition.

### Capability and priority

Define lasting modules as `A「名称」`. For each module state responsibility, input, user-visible output, ownership, main states, recovery, and current priority reason. Put demo controllers, narration, reset tools, and approval decks inside current-version delivery support.

### Requirements

Use stable IDs and include both product and technical acceptance:

| ID | Priority | Module | Product requirement | User-visible result | Business rule | Technical acceptance boundary | Evidence status |
|---|---|---|---|---|---|---|---|

Keep filenames, commands, schemas, fixtures, and mechanics in the active Spec unless they define a lasting public contract.

### Current-version truth

| Surface | Current implementation | Truth status | User-visible label | Later replacement |
|---|---|---|---|---|

Cover frontend or task surface, backend/process, data/input, model, external service, manual support, and output quality when applicable.

## Product-shape contracts

Load the primary shape and any secondary shape that materially affects value delivery.

### C-end interaction

Describe page inventory, information architecture, entry points, mobile/accessibility, and the core route:

| Scene | Entry page | Page presentation | User action | State change | Visible result | Failure and recovery |
|---|---|---|---|---|---|---|

Define loading, empty, error, permission, cancel, return, and repeated-use states where relevant. Use clickable journey evidence for version exits.

### Content or artifact production

Define the production contract:

| Stage | Input | Processing responsibility | Intermediate or final artifact | Quality gate | Failure and recovery | Evidence |
|---|---|---|---|---|---|---|

Include provenance, immutable revisions, human review, artifact usability, rework, and output separation. Measure quality, throughput, cycle time, and rework only after a baseline exists.

### Internal workflow

| Role | Trigger | Processing steps | Handoff or approval | Visible result | Exception recovery | Audit evidence |
|---|---|---|---|---|---|---|

Define ownership, queue state, permissions, escalation, and responsibility transfer. Describe UI only where it changes the operator task.

### API or platform

| Consumer | Onboarding entry | First-success task | Interface or contract | Visible result | Failure recovery | Adoption evidence |
|---|---|---|---|---|---|---|

Include examples, docs/SDK boundaries, credentials, compatibility, deprecation, self-service, reliability, and time to first value.

### Service orchestration

| Service scene | User touchpoint | Provider | Service action | State return | Failure recovery | Responsibility boundary |
|---|---|---|---|---|---|---|

Cover online/offline handoffs, provider truth, support, cancellation, unknown external outcomes, and return to the originating task.

### Marketplace or transaction

| Side | Discovery or match | Trust protection | Transaction action | Fulfillment result | Dispute recovery | Evidence |
|---|---|---|---|---|---|---|

Define both sides' value, supply/demand constraints, settlement, fraud, and dispute ownership.

## Risk contracts

### AI assistant or Agent

| Scene | Trigger entry | Carried context | Assistant response | Key question | Action boundary | Visible result | Fallback |
|---|---|---|---|---|---|---|---|

Define model role, human control, uncertainty, feedback, correction, permissions, external actions, evaluation, and non-AI fallback. Keep runtime behavior separate from presenter narration.

### Evidence-sensitive or externally connected products

Name sensitive data, consent, external write authority, service responsibility, truth labels, failure status, reconciliation, support, and audit. A successful local action does not prove the external outcome.

### Third-party reuse and publishing

Record pinned source, version, license, callable boundary, exclusions, provenance, review, approval, publication authority, and current proof. Separate generation, review, approval, external operation, and release eligibility.

## Approval readiness

Publish the assumption register from the internal contract. Set `是否具备审批条件：否` when a `必须为真` item is not confirmed or has been denied. Approval of the PRD activates only the project-declared next gate.
