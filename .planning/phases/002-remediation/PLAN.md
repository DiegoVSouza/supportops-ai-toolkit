# P02 Phase 002 Plan — Safe execution remediation

## Task 1 — Specify failure and boundary contracts

Inspect current tool, guardrail, and feature state. Add regression tests for ambiguous timeout on a side-effecting tool, explicit idempotency behavior, execution limits at the call path, and JSON schema boundary values. Confirm current public API and record an ADR/versioning decision if compatibility must change.

## Task 2 — Make timeout and retry semantics safe

Implement the smallest safe behavior: do not automatically retry a non-idempotent operation after an indeterminate timeout unless a tested idempotency key/contract makes repetition safe. Use cancellable isolation only if its semantics can be proven. Preserve retry classification and bounded backoff for safe operations.

## Task 3 — Enforce execution and schema limits

Wire step, token, and elapsed-time budgets into the execution entry point. Define and enforce the supported schema subset, including bool-vs-number handling, finite numbers, and input/output validation. Add adversarial and boundary regressions without removing existing coverage.

## Task 4 — Reconcile state and run gates

Populate feature statuses and progress from actual evidence. Run and save fast/full fake-mode gates; label replay/model and comparable cost/latency checks `PENDING` unless prerequisites exist. Review documentation and package compatibility.

## Path ownership

- `allowed_write_paths`: `.planning/phases/002-remediation/**`, `supportops_toolkit/**`, `tests/**`, `docs/harness/feature_list.json`, `docs/harness/progress.md`, `docs/harness/failures.md`, `docs/knowledge/**`, `docs/decisions/**`, `README.md`, `README.pt-BR.md`, `artifacts/evidence/**`, `artifacts/packages/**`; `pyproject.toml` and package version metadata only if a reviewed public contract change requires it.
- `forbidden_changes`: paths outside `projects/p02/**`; shared harness/kit; sibling repositories; secrets; existing tests weakened or deleted; public contract/version changes without ADR and consumer plan; live/paid calls; external publication, push, deploy, PR, or merge.

## Dependencies and execution mode

- Depends on phase 001 package/tests and the committed portfolio remediation acceptance criteria.
- Python project dependencies already present in the repository; do not add dependencies without documenting need and lock/provenance updates.
- `LLM_MODE=fake`; replay is conditional on available sanitized, traceable cassettes. Cost/latency comparison requires comparable recorded runs.

## Checks

- `python scripts/check_fast.py` — local fast regression.
- `python -m unittest discover -s tests -v` — unit and contract coverage, where included by the repository gate.
- `python scripts/check_full.py` — full fake-mode gate; must return nonzero when required local checks fail or are skipped.
- Additional focused tests for timeout side effects, idempotency, automatic limit enforcement, schema type/finite boundaries, and unchanged adversarial coverage.
- Save command, exit code, and output under `artifacts/evidence/`; classify each gate separately.

## Plan review

Reviewed against GSD-LITE-PLUS and the P02 remediation acceptance criteria: four observable tasks, tests precede implementation, write ownership is project-local, constraints and dependencies are explicit, and every required check has saved evidence. The plan is approved for execution.

## Stop condition

Stop before changing a public contract without an ADR, version increment, and consumer update plan; stop any replay/live work without eligible cassettes or explicit authorization; mark unavailable service/model checks `INCOMPLETE`/`PENDING` and continue independent local work.
