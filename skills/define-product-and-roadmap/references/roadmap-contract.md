# Experience Roadmap Contract

## Contents

1. Roadmap structure and capability language
2. Route selection by value surface
3. Version and evidence rules
4. Acceptance

## Roadmap structure

Publish in this order:

1. Core user task and evolution goal.
2. Current baseline, value bottleneck, and capability priority.
3. Named capability levels.
4. Experience-version Roadmap.
5. Current-version deliverable and truth boundary.
6. Dependencies, risks, assumptions, gates, and status.

Use:

| Code | Meaning |
|---|---|
| `A「模块」` | Lasting product module |
| `A0「能力」` | Named maturity level inside module A |
| `R1（第 1 个体验版本）「名称」` | First experience version |

Repeat code and name together. A capability defines responsibility, input, user-visible output, ownership boundary, and exit evidence.

Name every nonzero version as `R<n>（第 <n> 个体验版本）「名称」` in the version table. Keep out-of-scope future directions outside the numbered version sequence until the product contract defines their user task, evidence, and approval boundary.

## Route selection by value surface

Derive the route from the first missing transition, not from a default module order.

### Consumer interface

Sequence a usable route through entry, comprehension, action, state change, visible result, and recovery. Establish a standalone screen version only when the screen itself settles a meaningful product decision; otherwise keep an end-to-end clickable path.

### Content or artifact production

Let a module stand alone when its output is independently usable, retainable, comparable, and acceptable. A valid pattern is:

```text
reference baselines → independent module upgrades → integration → recovery → history/reuse
```

Baseline evidence does not approve production reuse. Integration preserves the independent artifact contracts.

### Internal workflow

Sequence a real work item through trigger, processing, handoff/approval, outcome, exception, and audit. Prefer one end-to-end queue item over separate frontend/backend milestones.

### API or platform

Sequence discoverability, onboarding, first success, repeatable integration, self-service, reliability, and adoption. Exit versions with a consumer-owned successful use, not only an implemented endpoint.

### Service orchestration

Sequence entry, provider handoff, result or status return, failure recovery, additional service cases, and real integration. A link without provider responsibility or return state is not a service outcome.

### Marketplace

Sequence one protected exchange across both sides before expanding liquidity, matching depth, automation, or monetization.

### Decision demo

Use a bounded demo when the immediate purpose is investment or leadership alignment. Label fixed data, simulated services, manual setup, and presenter aids. The demo must still show the product user's task; reviewer narration remains delivery support.

## Version rules

Use this table:

| Experience version | User task | Core capability | User-visible result | Main increment | Primary validation question | Entry condition | Exit condition | Status |
|---|---|---|---|---|---|---|---|---|

For every version:

1. Describe one complete and meaningful experience sentence.
2. Validate one primary question.
3. Preserve accepted paths and artifacts as regression baselines.
4. Carry working assets as reuse dependencies until a named gap justifies change.
5. Replace one or a small number of truth boundaries.
6. Put frontend, backend, data, model, interface, integration, and test work below the experience version.
7. State evidence entry and exit conditions.
8. Treat scale and monetization as directions until pilot evidence supports a bounded milestone.

Shape-specific exit evidence:

| Product shape | Version exit evidence |
|---|---|
| C-end interaction | Clickable route, state and recovery evidence, comprehension or task evidence |
| Content/artifact production | Usable artifact, quality result, provenance, review, and replay evidence |
| Internal workflow | Completed work item, handoff/approval, exception, and audit evidence |
| API/platform | New consumer first success, contract checks, reliability, and onboarding evidence |
| Service orchestration | Provider handoff, visible result/status, return, responsibility, and recovery evidence |
| Marketplace | Both-side completion, trust, fulfillment/settlement, and dispute evidence |

## Current-version boundary

Show the current version's user-visible deliverable and truth boundary. Include only surfaces relevant to the selected product shape. State real, test, simulated, manual, documented, and unverified behavior where used.

## Acceptance

1. The Roadmap opens with the product user's task and current evidence baseline.
2. The route follows the primary value surface and value bottleneck.
3. Every code is named at its point of use.
4. Every version produces shape-appropriate evidence and answers one question.
5. Existing working assets remain reuse dependencies until a named uncertainty activates work.
6. Later versions preserve accepted user routes or artifact contracts.
7. Reviewers, demo aids, and technical tasks remain below product versions.
8. PRD and Roadmap share product shape, terminology, scope, reuse, truth, assumptions, and authority status.
