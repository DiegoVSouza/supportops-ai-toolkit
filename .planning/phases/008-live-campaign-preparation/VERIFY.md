# Verify — Live campaign preparation

Use repository artifacts and commands, not implementation-chat claims. Save each command, exit code, and sanitized output to `artifacts/evidence/live-campaign-preparation/`.

- [x] Dataset validator and tests confirm 80 unique cases, 24 development / 56 holdout, eight families with ten cases each, and 48 English / 32 Portuguese. Independent outcome review remains pending.
- [x] Source-group split isolation and all per-case contracts/caps are validated; each case explicitly forbids real refunds.
- [x] Focused tests reject wrong decision/tool/escalation/abstention, malformed schema, unsupported claims, unsafe refund claims, and fixture provenance counted as live.
- [x] Fixture/replay provenance is rejected as a live trial; config forbids raw provider text persistence.
- [x] Config displays 3 trials, 240 primary calls, 60 confirmation calls, finite task caps and timeout/retry/chunk controls. Unapproved cumulative quota/tokens/requests, pacing, wall-clock, and funding remain PENDING; USD 0 is unchanged.
- [x] `-S` pilot/development/holdout dry-runs and blocked generation pass without provider/credential/network/Docker access.
- [x] Changes are limited to preparation paths; historical case labels/reports were not edited and no live semantic rerun was made.
- [x] Fast and full checks pass, with exit codes and outputs saved; full gate reports 47 tests and all fake eval/adversarial checks pass.
- [x] No provider call, paid usage, or live quality metric is claimed.
- [x] Staged paths are within phase ownership; reviewed diff has no credentials or unrelated user data.


## Outstanding phase gates

- Independent reviewer approval of case outcomes and rubric: `PENDING`; this preparation agent cannot claim independent review.
- Clean-context phase verification: `PENDING`.
- Durable cumulative ledger and serialized campaign lease: `NOT IMPLEMENTED`; required before any bounded campaign runner.
- Budget, quota, cumulative caps, confirmation funding, pacing, and model catalog preflight: `PENDING`; no provider call is authorized.
