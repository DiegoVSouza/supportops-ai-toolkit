# Plan

1. Write failing tests for selecting a new development campaign, binding the candidate prompt to source provenance, preserving the old campaign, refusing non-development data and preventing duplicate or uncertain work.
2. Implement the smallest campaign-aware executor and fixture plumbing; keep live dispatch closed until the separately owned root guard and committed authorization are ready. Do not weaken existing tests.
3. Run fixture and full fake gates and capture results. Reconcile prior root and project ledgers against the cumulative 72-call development ceiling before proposing any live run. Freeze only a clean committed candidate after root guard and authorization verification.

allowed_write_paths: `.planning/phases/019-candidate-development-campaign/**`, `scripts/campaign_execution.py`, `scripts/run_live_campaign.py`, `tests/test_campaign_*.py`, `evals/live-execution.json`, `artifacts/evidence/candidate-development-019/**`, `docs/harness/decisions.md`, `docs/harness/progress.md`.

forbidden_changes: existing campaign evidence and ledgers, dataset, rubric, prior prompt, confirmation and holdout, credentials, root guard or policy, other projects. Mode fake for preparation; no provider calls. Three total attempts per reproducible failure.
