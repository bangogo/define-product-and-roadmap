# Product Contract Quality Rubric

Use this rubric after deterministic validation. Score the exact PRD/Roadmap pair, not a summary of it.

## Decision rules

- Score each dimension `0`, `1`, or `2` and cite document evidence.
- `0`: missing, contradicted, or materially unsafe.
- `1`: present but generic, incomplete, weakly evidenced, or inconsistent.
- `2`: specific, evidence-bounded, internally consistent, and decision-usable.
- Do not average away a gate failure.
- A self-review is `performed`, not `independent`. A fresh-context review may be independent only if it did not receive the intended answer or hidden diagnosis.

## Dimensions

| Dimension | 0 | 1 | 2 |
|---|---|---|---|
| User and core task | User is missing or is actually the reviewer | User exists but task/context is generic | Product user, context, task, workaround, and priority are specific |
| Current effect and evidence | Target is presented as current or source is absent | Current state is listed but evidence layer is vague | Current effects, sources, dates/revisions, truth labels, and limitations align |
| Value path and bottleneck | Module list substitutes for value delivery | A route exists but the first weak transition is unclear | Shortest value path and first bottleneck explain current priority |
| Product-shape fit | Generic interface/module template dominates | Primary shape is named but selected contracts are incomplete | Primary/secondary shapes fit the value surface and drive the right contracts |
| Product value and business logic | Feature claims replace outcomes | Benefits are plausible but not linked into a loop | User result, business result, repeated-use reason, evidence loop, and stop condition connect |
| Experience/production completeness | Happy path only | Main path plus some states or gates | Entry, states, visible result, failure, recovery, permissions, and review are complete for the shape |
| Reuse and ownership | Reuse is asserted without boundary | Source or decision exists but ownership/license/version is incomplete | Source, revision, license, proof, decision, adapter, exclusions, and project addition are explicit |
| Requirements and acceptance | Requirements are slogans or technical tasks | IDs and acceptance exist but are weakly observable | Unique requirements map to modules and observable product plus technical evidence |
| Roadmap logic | Generic feature sequence or dates without evidence | Versions are named but questions/exits are weak | Each version follows the bottleneck, yields user value, answers one question, and activates one gate |
| Truth, risk, and authority | Risk or authority is hidden; unsafe action implied | Risks are listed but controls/status are incomplete | Truth layers, modifiers, controls, unknown states, assumptions, readiness, and next authority are explicit |
| Cross-document consistency | Material contradiction exists | Minor naming or scope drift exists | Metadata, modules, reuse, truth, assumptions, versions, and approval state align |
| Readability and decision utility | Owners cannot find the decision | Complete but repetitive or overly technical | Business, product, experience, and technical owners can each locate their decision evidence |

Maximum score: 24.

## Approval blockers and quality-critical failures

The pair is not approval-ready if any of these approval blockers applies:

1. Any unresolved or denied `必须为真` item exists.
2. Current behavior is materially unsupported, contradictory, or mislabeled.
3. Product user, primary value surface, or selected direction remains mixed.
4. Sensitive data, external writes, publishing, transactions, or high-stakes decisions lack explicit authority and recovery.
5. Direct third-party reuse lacks source revision or license status.
6. PRD and Roadmap disagree on product shape, current version, truth, assumptions, or next gate.
7. The current version lacks user-visible exit evidence.

A well-written product contract may correctly remain not approval-ready. Do not lower semantic quality merely because an approval blocker is honestly recorded. Treat the following as quality-critical failures instead:

1. A material approval blocker is hidden, mislabeled, or contradicted by readiness metadata.
2. Current behavior is invented or promoted beyond its evidence layer.
3. Sensitive data, external writes, publishing, transactions, or high-stakes decisions are authorized without explicit authority and recovery.
4. PRD and Roadmap materially contradict each other.
5. The selected route cannot be derived from the stated user value and bottleneck.

## Result labels

| Result | Rule |
|---|---|
| `semantic_pass` | At least 20/24, no dimension below 1, no quality-critical failure, and every approval blocker is accurately reported |
| `semantic_conditional` | At least 16/24 with no uncontained safety/authority failure, but quality or evidence handling remains materially incomplete |
| `semantic_fail` | Below 16/24, any quality-critical failure, or a material contradiction |
| `not_run` | Exact bytes were not reviewed |
| `blocked` | Review could not run because required evidence or environment was unavailable |

Report the score, result label, approval blockers, quality-critical failures, weakest dimensions, exact revisions reviewed, and review independence. Never convert `semantic_pass` into runtime proof, user validation, approval, or release authority.
