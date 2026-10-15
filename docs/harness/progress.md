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
