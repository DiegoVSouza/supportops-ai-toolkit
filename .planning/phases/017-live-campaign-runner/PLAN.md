# Plan

1. Tests first: `tests/test_campaign_corpus.py` (deterministic context, hash-stable cases), `tests/test_campaign_observe.py` (schema, matches, safety observations, content-freeness), `tests/test_campaign_execution.py` (fixture session end to end, resume, stop on infrastructure failure, no replay, manifest and fingerprint checks). Run red.
2. `scripts/campaign_corpus.py` and `scripts/campaign_observe.py`; then `scripts/campaign_execution.py` modelled on P05 `scripts/campaign_execution.py` (single-call trials, latency from the transport receipt).
3. Wire `scripts/run_live_campaign.py` (`--freeze`, `--execute-fixture`, `--execute-free`, `--max-trials`, `--output-dir`); add `p02-dev-v1` to `evals/live-execution.json`.
4. Full fake gate, commit sources, freeze the manifest against the committed candidate and commit it.
5. Live: catalog preflight, pilot (6), review, then the remaining 18; stop after development. No edit to prompt, corpus or grader after the pilot.
6. Update `feature_list.json`, README, `failures.md`, `progress.md`, VERIFY from the recorded run only; regenerate the P07 catalog.

allowed_write_paths: `.planning/phases/017-live-campaign-runner/**`, `scripts/campaign_corpus.py`, `scripts/campaign_observe.py`, `scripts/campaign_execution.py`, `scripts/run_live_campaign.py`, `tests/test_campaign_*.py`, `evals/live-execution.json`, `artifacts/evals/live/p02-dev-v1/**`, `artifacts/evidence/live-campaign-runner/**`, `docs/harness/{decisions,failures,progress,feature_list}.json|md`, `README.md`, `README.pt-BR.md`.
forbidden_changes: `evals/datasets/**`, `evals/rubrics/**`, `evals/live-campaign.json`, holdout and confirmation, other projects, credentials, `scripts/campaign_ledger.py` semantics, paid use.
max_tries: 3 per step; stop on the first provider or accounting anomaly.
