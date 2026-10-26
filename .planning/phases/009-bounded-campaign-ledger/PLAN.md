# Plan — Bounded campaign ledger for P02

## Execution controls

- `llm_mode`: `fake`; no network/provider access in this phase.
- `allowed_write_paths`:
  - `.planning/phases/009-bounded-campaign-ledger/**`
  - `scripts/campaign_ledger.py`
  - `scripts/run_live_campaign.py`
  - `tests/test_campaign_ledger.py`
  - `tests/test_live_campaign_preparation.py`
  - `docs/harness/decisions.md`
  - `docs/harness/failures.md`
  - `docs/harness/progress.md`
  - `docs/knowledge/live-campaign-ledger.md`
  - `artifacts/evidence/live-campaign-ledger/**`
- `forbidden_changes`: root `.env`, `harness.yaml` budget, campaign dataset/rubric/config approvals, toolkit/runtime contracts, historical reports, other repositories, harness-kit, provider/network calls, Docker mutation, refunds, external effects, paid spend, push, and weakened graders.
- Budget: configured paid spend remains USD 0. A campaign free-tier allowance and all cumulative request/token/spend/time ceilings are `PENDING`; do not infer authorization from earlier single-ticket runs or multiple credentials.
- Validation: focused stdlib ledger tests, P02 fast/full fake gates, CLI help, offline dry-run, blocked generation, and resume inspection. Record exact commands, exit codes, and sanitized outputs.
- Stop condition: no provider dispatcher or call in this phase. Missing any finite resource approval leaves campaign `INCOMPLETE`.

## Tasks

1. **Test durable accounting and lease first** — cover append-only reservations/outcomes, unknown-usage retention, duplicate refusal, cumulative cap races, and cross-process lease exclusion/release.
2. **Implement P02 campaign ledger and read-only resume** — add project-local SQLite state and OS lease; extend the preparation CLI only with sanitized resume inspection. Preserve the disabled-generation guard and immutable historical trials.
3. **Verify and record the incomplete boundary** — run focused and full fake gates, capture command evidence without replacing historical artifacts, update project records/knowledge, inspect staged paths and secret-free diff.

## Plan review

Reviewed against P02 Phase 008, current `evals/live-campaign.json`, runner CLI, and the portfolio live-readiness SPEC. The campaign remains within P02 ownership; dataset, rubric, runtime, profile, and historical evidence are excluded. Paid budget remains zero and unresolved free quota is not inferred. No sibling import or provider access is planned. Accepted for offline execution on 2026-10-26. Independent clean-context verification remains pending.
