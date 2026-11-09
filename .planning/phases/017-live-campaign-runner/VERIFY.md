# Verify

Status: PASS for the development stage (live, 24 trials); holdout and confirmation are out of scope and not run. Human review PENDING.

- [x] Unit tests: `tests/test_campaign_execution.py` was written before `scripts/campaign_execution.py` (import error first). `test_campaign_corpus.py` and `test_campaign_observe.py` were written together with their modules and passed on the first run; no red-first evidence is claimed for them.
- [x] Full fake gate exit 0: `artifacts/evidence/live-campaign-runner/check-full-fake.txt` (108 unit tests, eval, adversarial).
- [x] Root account tests green (87) in the lab repo, phase 058.
- [x] Fixture end-to-end run of the real entry point (`--execute-fixture`, 24 trials, no network) completes; `--execute-free` without `LLM_MODE=live` stops with `explicit_live_mode_required`.
- [x] Manifest frozen against committed candidate `95dbf8a` (`artifacts/evals/live/p02-dev-v1/manifest.json`).
- [x] Pilot run recorded: 4/6; `pilot-run.txt`, `pilot-report.json`, `pilot-trials.jsonl`, `catalog-preflight.txt` (PASS).
- [x] Development run recorded: exit 0, COMPLETE, 13/24; 24 reserved = 24 completed ok in the root usage ledger; report tokens equal the ledger (8,441 in, 2,189 out). `development-run.txt`, `dev-report.json`. Full fake gate after the live runs: `check-full-after-live.txt` exit 0. Root tests after the run: 87 OK (`artifacts/evidence/llm-live-readiness/p02-dev-campaign/tests-after-run.txt` in the lab repo).
