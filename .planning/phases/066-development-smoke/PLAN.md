# Plan

Allowed write paths: `scripts/campaign_execution.py`, `scripts/run_live_campaign.py`, `evals/live-execution.json`, `tests/test_campaign_execution.py`, `.planning/phases/066-development-smoke/**`, and new output under `artifacts/evals/live/p02-dev-v4-smoke/`.

1. Add a distinct sealed campaign and exact four-trial project ceiling.
2. Keep selection limited to the first four development cases and v3 payload construction.
3. Run focused regression and full project fake gate; record exit codes and outputs.
4. Commit, freeze the candidate, then run up to four live attempts through the root-account transport.

No holdout, confirmation, old campaign resume, paid calls, or retry after uncertainty.
