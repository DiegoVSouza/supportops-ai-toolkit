# Plan

1. Implement a fixture session adapter for the actual shared envelope, durable bounded reservations and sanitized receipts.
2. Verify success, isolation, invalid usage, cap exhaustion and uncertain restart without replay; run locked fast/full gates and save command/cwd/exit/output.

allowed_write_paths: `.planning/phases/015-accounted-protocol/**`, `supportops_toolkit/accounted_generation.py`, `tests/test_accounted_generation.py`, `artifacts/evidence/accounted-protocol-015/**`, `docs/harness/progress.md`.

forbidden_changes: existing ledgers/evidence/manifests, sibling imports, provider execution, credentials, budgets, holdout/confirmation, production identity/corpus, Docker and weaker tests.

Budget: fake only, zero calls and USD 0 paid. Local prototype ceiling: four requests, each 4096 input/512 output, persisted cumulatively; this is not live funding. max_tries: 3 per stable failure. Stop on unexpected provider access or unknown work. Plan-check: implementer self-assessment, independent review pending.
