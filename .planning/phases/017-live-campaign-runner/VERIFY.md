# Verify

Status: INCOMPLETE until the live pilot and development runs are recorded in `artifacts/evidence/live-campaign-runner/`.

- [x] Unit tests: `tests/test_campaign_execution.py` was written before `scripts/campaign_execution.py` (import error first). `test_campaign_corpus.py` and `test_campaign_observe.py` were written together with their modules and passed on the first run; no red-first evidence is claimed for them.
- [x] Full fake gate exit 0: `artifacts/evidence/live-campaign-runner/check-full-fake.txt` (108 unit tests, eval, adversarial).
- [x] Root account tests green (87) in the lab repo, phase 058.
- [x] Fixture end-to-end run of the real entry point (`--execute-fixture`, 24 trials, no network) completes; `--execute-free` without `LLM_MODE=live` stops with `explicit_live_mode_required`.
- [ ] Manifest frozen against a committed candidate.
- [ ] Pilot run recorded.
- [ ] Development run recorded.
