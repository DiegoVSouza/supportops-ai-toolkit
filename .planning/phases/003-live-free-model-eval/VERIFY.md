# VERIFY — Live free model evaluation

- Offline gate: `python scripts/check_full.py` must pass with fake mode.
- Unit tests: parser and free-price guard pass without network access.
- Live run: at most ten bounded synthetic requests to `cohere/north-mini-code:free`, zero-priced route verified before execution, per-case failures saved, and command exit code recorded. HTTP 429 stops the run.
- No conclusion about groundedness, production quality, or general model capability is drawn from the synthetic dataset.

## Execution results — 2026-10-23

- Offline gate: `python scripts/check_full.py` — exit 0; 29 tests passed, fake eval and adversarial suite passed. Output: `artifacts/evidence/phase-004-validation.txt`.
- Live evaluation: `python scripts/run_live_free_eval.py` — exit 1 / `INCOMPLETE`. The authenticated catalog confirmed zero prompt/completion pricing. Ten requests were attempted, nine returned valid assessments and one returned a provider error. On the nine valid outputs, decision, tool, and escalation accuracy were each 8/9 (0.889); groundedness was not evaluated. Reported usage was 1,882 prompt and 726 completion tokens; reported cost was USD 0.
- Full per-case output, the failed provider response status, and timings are saved in `artifacts/evidence/live-free-model-eval.json`. The nine-case metrics are a small synthetic result, not a production claim.
