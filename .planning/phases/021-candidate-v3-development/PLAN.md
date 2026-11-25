# Plan

1. Add a regression for selecting the v3 prompt by campaign and keeping v2/v1 prompts unchanged; record red before implementation.
2. Add the v3 prompt and bind it to the source fingerprint, root phase 065 authorization, CLI campaign choices, committed authorization preflight, and an exclusive one-time manifest.
3. Run focused fake tests and the complete fake gate; review the exact staged diff and commit source before freeze.
4. Reconcile 48 prior P02 development attempts and the root uncertainty snapshot. Freeze one 24-case manifest; run the six-case pilot, then the remaining cases only if all pilot attempts settle OK.
5. Save invocation outputs and the final content-free report/trials; retain `MODEL_QUALITY_PENDING` unless measured acceptance criteria pass.

allowed_write_paths: `.planning/phases/021-candidate-v3-development/**`, `agent/prompts/tool-selection-candidate-v2.md`, `scripts/candidate_corpus.py`, `scripts/campaign_execution.py`, `scripts/run_live_campaign.py`, `tests/test_campaign_candidate.py`, `evals/live-execution.json`, `artifacts/evidence/candidate-v3-development-021/**`, `artifacts/evals/live/p02-dev-v3/**`, `docs/harness/{progress,failures,feature_list}.md|json`.

forbidden_changes: `p02-dev-v1` and `p02-dev-v2` manifests, reports, trials, ledgers and frozen sources; dataset and rubric; holdout, confirmation and production; any credential or non-P02 path.
