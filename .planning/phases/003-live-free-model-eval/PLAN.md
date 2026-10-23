# PLAN — Live free model evaluation

## Allowed write paths

- `.planning/phases/003-live-free-model-eval/**`
- `scripts/run_live_free_eval.py`
- `tests/test_live_eval.py`
- `artifacts/evidence/phase-004-validation.txt`
- `artifacts/evidence/live-free-model-eval.json`

## Steps

1. Add a small standard-library runner that verifies the exact model and zero pricing from the authenticated OpenRouter catalog.
2. Attempt all ten synthetic cases sequentially using a required structured tool call, disabled reasoning, no retries, and at most 2,048 output tokens per case. Record invalid outputs per case and stop on HTTP 429.
3. Report decision/tool/escalation accuracy, per-case results, total usage and latency; leave groundedness `NOT_EVALUATED`.
4. Add unit coverage for response parsing and pricing/shape checks without network access.
5. Run P02's offline full gate and the live free-model evaluation; save sanitized evidence.
6. Review and commit the staged diff locally.

## Stop conditions

- Stop before chat requests if the key is rejected, the model is missing, or either token price is nonzero/unknown.
- Record HTTP failures or malformed output per case without retrying; stop immediately on HTTP 429.
- Never select a paid model as a fallback.
