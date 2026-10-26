# Verify — Bounded campaign ledger for P02

Save command output, exit codes, and sanitized evidence under `artifacts/evidence/live-campaign-ledger/`.

- [x] Ledger is append-only, reserves before dispatch, retains unknown usage, and forbids trial replays.
- [x] Cumulative request/token/estimated-cost caps are atomic across campaign IDs and concurrent processes.
- [x] OS lease blocks another local campaign and releases normally; metadata contains no secret or case content.
- [x] Resume inspection is read-only, sanitizes attempts, rejects unknown/empty campaign IDs with exit 2, and never dispatches.
- [x] Pilot/full execution stays blocked while quota, USD 0 budget reconciliation, finite limits, review, or preflight is missing.
- [x] Focused ledger tests (6) and fake fast/full gates (54 tests) pass without provider, credentials, network, or Docker access.
- [x] Evidence, report, decisions, failures, progress, and Portuguese/bilingual knowledge are updated; historical evidence is unchanged.
- [ ] Staged paths/diff are reviewed and locally committed; clean-context verifier review is separately recorded.

Promotion remains `INCOMPLETE` until campaign dispatch and every applicable evaluation, security, operations, budget, canary, and rollback gate have evidence.
