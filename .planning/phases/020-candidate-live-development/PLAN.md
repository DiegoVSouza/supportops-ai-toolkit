# Plan

1. Test authorization denial before freeze or live dispatch, frozen-manifest requirement before provider initialization, single-use freeze, candidate fingerprint, cumulative capacity and old campaign behavior. Record red then green.
2. Enable the candidate only through the tested CLI and root guard. Add its owner allocation, commit sources, run full fake gate and reconcile previous usage. Freeze only after clean committed fingerprints and guard authorization pass.
3. Run the six-case development pilot, stop on infrastructure or accounting anomalies, then run remaining development cases if the pilot has no stop. Preserve all receipts and content-free evidence; report actual results and limits. No holdout or confirmation, semantic replay, paid use or external RAG claims.

allowed_write_paths: `.planning/phases/020-candidate-live-development/**`, `scripts/campaign_execution.py`, `scripts/run_live_campaign.py`, `tests/test_campaign_*.py`, `evals/live-execution.json`, `artifacts/evidence/candidate-live-development-020/**`, `artifacts/evals/live/p02-dev-v2/**`, `docs/harness/{decisions,progress,failures,feature_list}.md|json`.

forbidden_changes: prior campaigns, their ledgers and artifacts, dataset and rubric, root guard/policy, other projects, credentials, holdout or confirmation. Root guard owns global limits. At most three attempts for a reproducible offline failure; a live failed or uncertain attempt is never retried.
