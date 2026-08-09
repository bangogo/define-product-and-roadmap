# Experience Roadmap Contract

## Contents

1. Roadmap structure and capability language
2. Route selection by value surface
3. Version and evidence rules
4. Current-version and governance contracts
5. Acceptance

## Roadmap structure and capability language

Publish in this order:

1. `核心用户任务与演进目标`.
2. `当前基线、价值瓶颈与能力优先级`.
3. `产品能力层级`.
4. `体验版本路线图`.
5. `当前版本交付与真实性`.
6. `依赖、风险、假设与版本闸门`.

Use:

| Code | Meaning |
|---|---|
| `A「模块」` | Lasting product module |
| `A0「能力」` | Named maturity level inside module A |
| `R1（第 1 个体验版本）「名称」` | First experience version |

Repeat code and name together at every decision point. A capability defines responsibility, input, user-visible output, ownership boundary, and exit evidence. Define each module's maturity levels:

Assign a different uppercase letter to every module. Capability codes inherit that letter: `A「采集」` may contain `A0「手工采集」`, while a separate `B「审阅」` module uses `B0「人工审阅」`. Do not reuse `A` for several differently named modules. Gate identifiers such as `G1` are not capability codes and may be named independently.

| 产品模块 | L0 | L1 | L2 |
|---|---|---|---|

Do not assign every module the same level progression. Each level must represent an observable improvement for its own responsibility.

## Route selection by value surface

Derive the route from the first missing or weak transition, not from a default module order.

### Consumer interface

Sequence a usable route through entry, comprehension, action, state change, visible result, and recovery. Establish a standalone screen version only when the screen itself settles a meaningful product decision; otherwise keep an end-to-end clickable path.

### Content or artifact production

Let a module stand alone when its output is independently usable, retainable, comparable, and acceptable. A valid pattern is:

```text
reference baselines → independent module upgrades → integration → recovery → history/reuse
```

Baseline evidence does not approve production reuse. Integration preserves independent artifact contracts and provenance.

### Internal workflow

Sequence one real work item through trigger, processing, handoff/approval, outcome, exception, and audit. Prefer one end-to-end queue item over separate frontend/backend milestones.

### API or platform

Sequence discoverability, onboarding, first success, repeatable integration, self-service, reliability, and adoption. Exit versions with a consumer-owned successful use, not only an implemented endpoint.

### Service orchestration

Sequence entry, provider handoff, result or status return, failure recovery, additional service cases, and real integration. A link without provider responsibility or return state is not a service outcome.

### Marketplace

Sequence one protected exchange across both sides before expanding liquidity, matching depth, automation, or monetization.

### Decision demo

Use a bounded demo when the immediate purpose is investment or leadership alignment. Label fixed data, simulated services, manual setup, and presenter aids. The demo must still show the product user's task; reviewer narration remains delivery support.

## Version and evidence rules

Use this table:

| 体验版本 | 用户任务 | 核心能力 | 用户可见结果 | 本版主要增量 | 主要验证问题 | 进入条件 | 退出条件 | 状态 |
|---|---|---|---|---|---|---|---|---|

Use `R0「当前基线」` only for observed or documented current state. Number planned versions contiguously from R1. Use canonical status values: `已有`, `Proposed`, `Ready`, `In Progress`, `Blocked`, `Complete`, or `Superseded`.

For every nonzero version:

1. Describe one complete and meaningful user experience sentence.
2. Validate one primary decision-changing question.
3. Preserve accepted paths and artifacts as regression baselines.
4. Carry working assets as reuse dependencies until a named gap justifies change.
5. Replace one or a small number of truth boundaries.
6. Put frontend, backend, data, model, interface, integration, and test work below the experience version.
7. State evidence-bearing entry and exit conditions.
8. Name the gate activated by exit evidence.
9. Keep scale and monetization as directions until pilot evidence supports a bounded version.

Shape-specific exit evidence:

| Product shape | Version exit evidence |
|---|---|
| C-end interaction | Clickable route, state and recovery evidence, comprehension or task evidence |
| Content/artifact production | Usable artifact, quality result, provenance, review, and replay evidence |
| Internal workflow | Completed work item, handoff/approval, exception, and audit evidence |
| API/platform | New consumer first success, contract checks, reliability, and onboarding evidence |
| Service orchestration | Provider handoff, visible result/status, return, responsibility, and recovery evidence |
| Marketplace | Both-side completion, trust, fulfillment/settlement, and dispute evidence |

Do not mark a version `Complete` from task completion, exit code, HTTP response, or document approval alone. Require the version's declared user-visible result and exit evidence.

## Current-version and governance contracts

Show the active or proposed current version's exact deliverable:

| 交付项 | 用户可见结果 | 当前实现 | 真实性 | 验收证据 | 不包含 |
|---|---|---|---|---|---|

Include only surfaces relevant to the selected product shape. State real, test, simulated, manual, documented, observed, historical, and unverified behavior where used.

Publish the same material assumption rows as the PRD:

| 类型 | 假设或决策 | 状态 | 依据 | 对产品影响 | 确认人/下一步 |
|---|---|---|---|---|---|

State dependencies and gates:

| 闸门 | 所需证据 | 决策人 | 通过后授权 | 未通过处理 |
|---|---|---|---|---|

Keep the following states distinct:

- document state: Draft, Proposed, Review Candidate, Approved, or Superseded;
- version state: 已有, Proposed, Ready, In Progress, Blocked, Complete, or Superseded;
- runtime truth: real, test, simulated, manual, documented, observed, historical, or unverified;
- external-operation state: not attempted, pending, confirmed, failed, or unknown;
- approval readiness: ready or not ready for the named gate.

## Acceptance

1. The Roadmap opens with the product user's task and current evidence baseline.
2. The route follows the primary value surface and the first value bottleneck.
3. Every code is named at its point of use.
4. Every version produces shape-appropriate evidence and answers one primary question.
5. Existing working assets remain reuse dependencies until a named uncertainty activates work.
6. Later versions preserve accepted user routes or artifact contracts.
7. Reviewers, demo aids, and technical tasks remain below product versions.
8. PRD and Roadmap share metadata, terminology, scope, reuse decisions, truth, assumptions, and authority status.
9. The current version states user-visible deliverables, exclusions, evidence, and the exact next gate.
