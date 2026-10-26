# Plan — Live campaign preparation

## Execution controls

- `llm_mode`: `fake`; dataset/rubric checks and dry-run must be offline.
- `allowed_write_paths`:
  - `.planning/phases/008-live-campaign-preparation/**`
  - `evals/datasets/live-v1/**`
  - `evals/rubrics/live-v1/**`
  - `evals/live-campaign.json`
  - `scripts/run_live_campaign.py`
  - `tests/test_live_campaign_preparation.py`
  - `docs/harness/decisions.md`
  - `artifacts/evidence/live-campaign-preparation/**`
- `forbidden_changes`: `supportops_toolkit/**` runtime/public contracts, other repositories, harness-kit, root `.env`, credentials, historical evidence, network/provider calls, Docker mutation, paid spend, external effects/refunds, publishing, push, or relaxed thresholds.
- Budget source: project profile and intake decision are USD 0. Prior free-plan single-case runs are scoped exceptions only. Campaign, confirmation and any judge reservations are `PENDING`; the campaign must not execute until finite approved caps are documented. Numbered keys do not represent independent quotas.
- Planned load to display, not authorization: pilot 6 development cases × 1 trial = at most 6 normal provider calls; full campaign 80 cases × 3 trials = at most 240 calls before a separate 20-case × 3-trial confirmation (60 calls). Pilot + primary + confirmation is 306 additive calls. Since profile authorization is zero, every live reservation remains blocked.
- Validation: P02 fast/full fake checks; dataset/split/family/language and rubric calibration; fake-vs-live provenance checks; dry-run and blocked-generation tests. Save command, exit code, and sanitized output in the evidence path.
- Stop condition: stop before dispatch if USD 0 policy is not explicitly reconciled, or quota, confirmation reserve, reviewers, model preflight, caps, or case/rubric review is missing. Result stays `INCOMPLETE`.

## Tasks

1. **Freeze reviewed evaluation data and rubrics** — inspect existing dataset schemas, tool contracts, and failure taxonomy; create 80 unique synthetic cases in the 24/56 fixed split and 48/32 language composition. Keep related scenarios in one split and preserve all historical case labels.
2. **Add dry-run and fail-closed reservation config** — validate stages/config, report calls and unresolved budget fields without reading credentials or constructing the Groq SDK. Block generation on zero/unapproved budget, quota uncertainty, or any missing cap; prohibit retries for semantic failures and real refund invocation.
3. **Calibrate graders and record offline evidence** — test deliberate bad predictions across all applicable families, verify fake/live provenance separation and dataset integrity, run the fake-mode project gates, and review the staged diff.

## Plan review

Coordinator review completed against P02's zero-budget decision, historical live failure reports, and portfolio requirements. The 24/56 split, 48/32 language allocation, 6-call pilot, and 240-call maximum are consistent. The paths avoid runtime changes and historical artifacts; all live execution remains blocked until explicit budget reconciliation. Accepted for preparation execution on 2026-10-26. A clean-context verifier is still required for the finished phase gates.
