# Progress

- Kit initialization completed.

## 2026-10-15 — Roadmap remediation phase 002

- Created and reviewed `.planning/phases/002-remediation/` before implementation; planning commit: `a6b9087`.
- Added fail-closed behavior for indeterminate tool timeouts and generic transport errors. Automatic retries now require explicit `ToolError(retryable=True)` classification.
- Wired optional `execution_limits` into tool invocation: each call consumes a step and its wait is capped by the remaining wall-clock budget. Token use must be reported at a caller's LLM boundary; P02 has no integrated agent runtime, so whole-run token enforcement remains INCOMPLETE.
- Defined the supported JSON Schema subset and reject unsupported keywords; number validation rejects booleans and non-finite values for inputs and outputs.
- Fake unit and full local gates pass; evidence is in `artifacts/evidence/phase-002-regression-green.txt` and `phase-002-check-full.txt`. The earlier red regression is preserved in `phase-002-regression-red.txt`.
- Cost, latency, and real model quality remain PENDING; no live or replay model call was made.
- Package API/behavior change is recorded in ADR-001. Version `0.2.0` will be built as a local wheel after the source commit; P05 must consume its recorded hash before package integration can pass.

## 2026-10-23 — Phase 003 live free-model evaluation

- Added a standard-library evaluator for the ten synthetic cases using `cohere/north-mini-code:free`. It verifies zero pricing from the authenticated model catalog, uses a forced structured assessment tool call, never retries, stops on HTTP 429, and records malformed/provider-error cases.
- Offline full gate passed with 29 tests. Evidence: `artifacts/evidence/phase-004-validation.txt`.
- Live run attempted all ten cases: nine valid model assessments and one provider error. Decision/tool/escalation each scored 8/9 among valid outputs; groundedness is `NOT_EVALUATED` because the dataset does not supply independent retrieval context. Reported usage: 1,882 input and 726 output tokens; cost: USD 0. Evidence: `artifacts/evidence/live-free-model-eval.json`.
- Evaluation status is `INCOMPLETE`; the provider error is preserved, and these ten synthetic records do not establish production quality.
