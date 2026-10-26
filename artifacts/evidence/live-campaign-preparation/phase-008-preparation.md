# P02 Phase 008 — campaign preparation evidence

All work below is offline. No Groq request, catalog lookup, credential read, network access, Docker mutation, or refund action occurred. Paid authorization remains USD 0.

| Command | Exit | Result |
|---|---:|---|
| `uv run --locked python scripts/run_live_campaign.py --stage pilot --dry-run` | 0 | 6 cases × 1 trial = 6 calls; USD 0; blockers reported. |
| `uv run --locked python scripts/run_live_campaign.py --stage development --dry-run` | 0 | 24 cases × 3 trials = 72 calls; 16 English / 8 Portuguese. |
| `uv run --locked python scripts/run_live_campaign.py --stage holdout --dry-run` | 0 | 56 cases × 3 trials = 168 calls; 32 English / 24 Portuguese. |
| `uv run --locked python -m unittest discover -s tests -p test_live_campaign_preparation.py -v` | 0 | 6 focused preparation tests passed; output is saved in `focused-tests.txt`. |
| `uv run --locked python scripts/check_fast.py` | 0 | `check-fast: OK`. |
| `uv run --locked python scripts/check_full.py` | 0 | 47 tests passed; fake evaluation and adversarial suite passed; `check-full: PASS`. |

Dataset SHA-256: `1d9643cef2bf475361079e33e0e7cf2de2095664531ab74da474ceeeb5f01985`. It contains 80 synthetic cases, 24 development / 56 holdout, 48 English / 32 Portuguese, eight families with ten cases each. Each case has one-call, 4,096-input-token and 512-output-token per-trial ceilings; campaign uses three trials except the six-case, one-trial pilot.

Reservations are planned maxima, not approval or consumption: primary campaign 240 calls / 983,040 input / 122,880 output tokens; fresh confirmation 20 cases × 3 trials = 60 calls / 245,760 input / 30,720 output tokens; pilot + primary + confirmation additive maximum 306 calls / 1,253,376 input / 156,672 output tokens. Paid budget remains USD 0. Quota, cumulative limits, review, confirmation funding, pacing, wall-clock cap, authenticated catalog preflight, clean-context verification, and a durable lease/ledger remain unresolved. Generation remains disabled.

Detailed dry-run JSON and gate output are saved beside this report. Independent human review is pending, so no quality or promotion claim is made.
