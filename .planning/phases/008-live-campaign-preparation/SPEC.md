# Phase 008 — Live campaign preparation

## Goal

Prepare a reviewed synthetic dataset, calibrated code-first rubrics, and a guarded reservation dry-run for P02's live evaluation toolkit. This phase does not call a provider or change the zero-budget product profile.

## Current evidence and constraints

- Revalidated repository HEAD: `f815be1a370344020ff9f13b5974a1ac195832bc` (`fix(evals): bound Groq reasoning and retain live attempts`).
- P02 profile and intake budget are USD 0. The one-case free-tier evaluations are bounded historical exceptions and do not authorize the 80-case campaign, fresh confirmation, hidden judges, or paid fallback.
- Historical one-case live failures remain preserved. Existing 10-case fixture/live metrics do not establish broad campaign quality.
- Do not inspect credentials, call Groq, modify Docker, change fixture labels to improve a score, or claim billed spend from estimates.

## Acceptance criteria

1. `evals/datasets/live-v1/` contains 80 unique semantic cases: 24 development and 56 sealed holdout, with reviewed outcomes for decision/tool/escalation accuracy, schema adherence, abstention, policy boundaries, fixture-vs-live separation, and grader correctness.
2. Every family has at least three cases; language coverage is 48 English and 32 Portuguese. Each case includes allowed/expected tool behavior, required/forbidden facts, rubric, criticality and finite call/token caps. No real refund action is possible.
3. The campaign config represents three trials, at most one normal provider call per trial, cumulative request/token/spend limits, confirmation reserve, deadlines, retry policy, chunk/pacing and budget approval source. Expanded ceilings remain `PENDING`; USD 0 stays USD 0.
4. Dry-run computes case/trial/call/reservation totals and blockers without SDK construction, credential reads, network access, or Docker changes. Live execution fails before dispatch when budget/quota/caps are not approved.
5. Graders reject deliberately wrong decisions/tools/schema/abstentions and unsafe refund behavior; evaluators distinguish fixture outcomes from real provider results. Evidence is sanitized and tied to commands and exit codes.

## Out of scope

Provider calls, paid usage, tool/runtime changes, production connectors, real refunds, customer data, kit changes, publication, push, or changing historical reports.
