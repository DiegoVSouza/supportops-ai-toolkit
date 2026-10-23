# Execution plan: P02 Groq live evaluation

## Task 1 — Test bounded provider control

Add offline tests for safe environment loading, catalog/model validation, retry classification and limits, key rotation exhaustion, response parsing, redaction, and the one-case domain assertion. Mock SDK/network boundaries; tests must make no network requests.

## Task 2 — Implement opt-in Groq evaluation

Implement the official-SDK live path, sequential one-case execution, fail-closed USD 0 free-plan boundary, bounded retry/rotation, usage capture, and separate sanitized JSON evidence. Keep existing fake runner and old provider artifacts untouched. Add/update only the P02 dependency lock/manifest if required by the installed official SDK convention.

## Task 3 — Verify and record evidence

Run focused and full offline checks, then perform one model-availability check and at most one real case evaluation using the user-designated free-plan credentials. Stop on free quota exhaustion and report cost as `PENDING` unless actual billing confirms zero. Save every command, exit code, and sanitized output in `artifacts/evidence/`; review artifacts and staged diff for secrets and generated files.

## Ownership

`allowed_write_paths`:
- `.planning/phases/004-groq-live/**`
- `scripts/run_live_groq_eval.py`
- `tests/test_live_groq_eval.py`
- `README.md` for the opt-in live-eval command and budget semantics
- `pyproject.toml` and the existing dependency lock only if official Groq SDK dependency management requires it
- `artifacts/evidence/phase-004-groq-live-*`
- `docs/harness/progress.md`
- `docs/harness/decisions.md` only to record the bounded zero-dollar live exception

`forbidden_changes`:
- `harness-kit/**`, shared lab policies, other projects, `.env`, previous live reports, datasets/baselines, fake behavior, unrelated P02 code.

## Runtime and budget

- `LLM_MODE=live` only for live run; fake/replay remain offline.
- Provider: Groq official SDK. Model: `openai/gpt-oss-20b`, confirmed against authenticated catalog before case request.
- Budget: existing `max_usd_per_task: 0`; use only the user-designated free-plan account, stop on quota exhaustion, and report cost `PENDING` because the model-list API cannot verify billing tier. Do not make additional runs when actual billing cannot be reconciled.
- Request ceiling: one selected case, one evaluation request, <=512 completion tokens, <=20 second timeout; one sequential rotation pass across at most five configured unique keys, with no parallelism. Availability query is a separate preflight. Retries only for throttling/transient failures, with capped backoff and bounded `Retry-After`.
- Stop on model/catalog unavailability, free-plan quota exhaustion, auth/permission/validation/policy error, an unbounded `Retry-After`, exhausted retry pass, or malformed response.

## Validation command

Use the project's pinned Python environment and `python -m unittest discover -s tests -p "test_live_groq_eval.py"` plus `python -m unittest discover -s tests -p "test_evals.py"`; then run the documented P02 full check from its README. Save output and exit status. The real evaluation is conditional on successful model preflight and use of the user-designated free plan.

## Stop condition

Do not make an evaluation call if explicit live mode, user-designated free-plan access, valid model access, or bounded configuration is absent. Stop after one case and do not retry domain-level/model-output failures.
