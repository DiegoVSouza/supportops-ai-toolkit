# Plan

1. Add tests for tenant isolation, missing evidence, detected injection, attribution and deterministic ordering using synthetic documents.
2. Implement the local boundary using existing retrieved-text guard; run focused and complete locked fake checks and record command outputs.

allowed_write_paths: `.planning/phases/012-fixture-retrieval-boundary/**`, `supportops_toolkit/fixture_retrieval.py`, `tests/test_fixture_retrieval.py`, `artifacts/evidence/fixture-retrieval-012/**`, `docs/harness/progress.md`.

forbidden_changes: datasets, rubrics, thresholds, ledgers, external data, provider access, production identity, model prompts, sibling projects, existing evidence and approvals.

llm_mode: fake; budget: zero provider calls and USD 0. Validate using locked focused tests, fast and full fake gate, saving commands, exit and outputs. Stop on real external access, unsafe evidence leakage, or test failure. Plan-check: self-assessment; independent review PENDING. Existing heuristic screening is not a guarantee against injection.
