# P02 Verification Plan

## Before implementation
- Verify local project Git root and clean/intended status; verify hook accepts Conventional Commit and rejects malformed message.
- Validate harness fields and record the profile/risk/budget rationale.

## Unit and contract validation
- Run `python -m unittest discover -s tests -v`.
- Cover schema failures, output validation, retryable versus fatal exceptions, retries, timeouts, local tool outcomes, injection and role policies, limits, redaction, cache, routing, and token budget.

## Evaluation validation
- Run `LLM_MODE=fake python -m supportops_toolkit.evals.runner --dataset evals/datasets/v1/supportops.jsonl`.
- Confirm baseline regression passes and deliberately degraded runner fails threshold in a unit test; report fake outputs as deterministic fixture behavior, not model quality.
- Run adversarial suite and list blocked count and any misses; no suppressed failures.

## Full gate
- `python scripts/check_full.py` runs real validation and returns nonzero on failures; output saved in evidence with exit code.
- Distinguish unit, eval, and unrun integration/E2E. There is no real model or external system integration, so those remain INCOMPLETE/PENDING.
