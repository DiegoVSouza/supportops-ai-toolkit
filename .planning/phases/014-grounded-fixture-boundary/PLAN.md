# Plan

1. Implement a fixture-only retrieval-to-transport boundary with explicit synthetic tenant, stable request ID, one call maximum, provenance and sanitized outcomes.
2. Test tenant isolation, refusal without dispatch, injected content, timeout/no replay and missing receipts; run locked fake full gate and save sanitized evidence.

allowed_write_paths: `.planning/phases/014-grounded-fixture-boundary/**`, `supportops_toolkit/fixture_generation.py`, `tests/test_fixture_generation.py`, `artifacts/evidence/grounded-fixture-boundary-014/**`.

forbidden_changes: external corpus/identity, provider calls, credentials, live opt-in, existing ledgers, sibling sources, budgets, real customer data, historical artifacts, external effects and weaker tests. Fake only; zero provider calls and USD 0. max_tries: 3 per local failure. No replay of uncertain provider work. Plan-check is implementer self-assessment.
