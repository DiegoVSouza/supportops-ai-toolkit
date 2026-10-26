# Phase 009 — P02 bounded campaign ledger

Status: `INCOMPLETE` for live adoption. Offline reservation and resume primitives pass; provider dispatch and promotion gates remain pending.

## Evidence

| Command | Exit | Result |
|---|---:|---|
| `uv run --locked python -m unittest discover -s tests -p test_campaign_ledger.py -v` | 0 | 6 ledger tests passed, including concurrent cap reservations and cross-process lease exclusion. |
| `uv run --locked python scripts/check_fast.py` | 0 | Required project metadata gate passed. |
| `uv run --locked python scripts/check_full.py` | 0 | 54 tests, fake regression eval, adversarial suite, and metadata gates passed. |
| `uv run --locked python -S scripts/run_live_campaign.py --help` | 0 | Help lists stages and read-only resume inspection. |
| `uv run --locked python -S scripts/run_live_campaign.py --stage pilot --dry-run` | 0 | Reports 6 pilot calls and pending reservations without provider/credential/network/Docker access. |
| `uv run --locked python -S scripts/run_live_campaign.py --stage pilot` | 2 | Generation is blocked while budget, quota, review, finite limits, and preflight are unresolved. |

Command output is captured beside this report. No historical live reports were modified, and no provider request was made.

## Remaining gates

- Groq catalog preflight and campaign dispatcher, plus crash-after-dispatch recovery and live-path lease integration.
- Reconciliation of the USD 0 project profile, finite free-tier quota/cumulative limits, confirmation funding, human dataset/rubric review, pacing, and time ceiling.
- Cross-project accounting and independent clean-context phase review.
- Canary and rollback evidence for any future promotion.
