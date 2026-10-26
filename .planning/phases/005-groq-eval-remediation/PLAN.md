# P02 remediation plan

## Task 1 — Test the failure explanation

Extract the system instructions into a testable prompt builder. Add offline tests for read-only lookup versus refund action semantics, the expected first-stage tool for `refund-eligible`, and no retry after a valid response with a failed domain assertion.

## Task 2 — Clarify the P02 live prompt

Change only the prompt builder and report schema to include expected values and a concise failure category (`tool_selection_mismatch`, `decision_mismatch`, or `escalation_mismatch`). Keep the request schema compatible with the last successful request by removing the new property-level description. Keep dataset, fake runner, offline baseline, and prior phase-004 report unchanged.

## Task 3 — Re-evaluate once and close the phase

Preserve the first sanitized HTTP 400, run focused and full offline checks, then make at most one corrected live re-evaluation of `refund-eligible` after model-list preflight. Preserve phase-004 failure and store the final phase-005 result separately. Do not automatically retry the 400 or repeat calls to tune toward a single sample.

## Ownership

`allowed_write_paths`: `.planning/phases/005-groq-eval-remediation/**`, `scripts/run_live_groq_eval.py`, `tests/test_live_groq_eval.py`, `README.md`, `docs/harness/decisions.md`, `docs/harness/progress.md`, `artifacts/evidence/phase-005-groq-*`, `artifacts/runs/phase-005/**`.

`forbidden_changes`: `harness-kit/**`, `.env`, other projects, dataset/baseline, phase-004 artifacts, generic toolkit APIs, and unrelated source.

## Limits

At most two total evaluation HTTP requests for this phase: the recorded HTTP 400 and one corrected attempt. One synthetic case, 512 completion tokens, 20s timeout, no provider fallback, no automatic retry of the 400 or completed response, and USD 0 configured budget using only the user's free-plan Groq credentials. Report billed cost `PENDING` unless confirmed.

## Validation

Run focused P02 tests and `scripts/check_full.py`; save exact commands, exit codes, sanitized outputs, and the real rerun result. The live gate may remain incomplete if the model repeats the assertion failure.
