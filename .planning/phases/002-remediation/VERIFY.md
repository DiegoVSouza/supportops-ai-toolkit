# P02 Phase 002 Verification Plan

## Unit and contract

- Prove a timeout with an indeterminate side effect does not trigger an unsafe automatic retry.
- Prove explicitly idempotent retry behavior and key propagation if that contract is supported.
- Prove steps, tokens, and wall-clock time are stopped/rejected at the actual execution path, including boundaries.
- Prove input/output schema behavior for booleans, integers/floats, NaN/infinity, malformed structures, and documented supported constraints.
- Retain and run the existing fake regression and adversarial suite; surface any adversarial misses.

## Package and full gate

- Run `python scripts/check_fast.py`, focused unit/contract commands, and `python scripts/check_full.py` in fake mode.
- The full gate must return nonzero for a required local gate that failed or did not execute.
- Save every command, exit code, and output in `artifacts/evidence/`.

## Replay, model, and performance

- Run replay only when sanitized cassettes have traceable provenance; otherwise report `PENDING`.
- Do not make model-quality, cost, or latency claims from fake tests. Record cost/latency as `PENDING` until comparable runs are saved.

## Evidence review

Check each result is labeled unit/contract, package integration, service integration, E2E, or agent evaluation. PASS requires executed command and output; unavailable gates are `INCOMPLETE` or `PENDING` with the missing prerequisite recorded.
