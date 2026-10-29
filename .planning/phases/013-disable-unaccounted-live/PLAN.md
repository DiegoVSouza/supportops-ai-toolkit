# Plan

1. Add a fail-closed entry point and an offline test proving no credential, provider, or artifact access.
2. Replace unsafe current README guidance and run locked focused and full fake checks; record sanitized command, cwd, exit and output.

allowed_write_paths: `.planning/phases/013-disable-unaccounted-live/**`, `scripts/run_live_groq_eval.py`, `tests/test_live_groq_eval.py`, `README.md`, `artifacts/evidence/disable-unaccounted-live-013/**`.

forbidden_changes: historical evidence and evaluations, other projects, budgets, live calls, credentials, existing test assertions, provider/model fallback, paid use, customer data and external effects. Budget: zero calls and USD 0. max_tries: 3 per failure; never replay a live completion. Stop on unexpected provider access or preserved-source mismatch. Plan-check is implementer self-assessment, not independent review.
