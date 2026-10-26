# P02 phase 006 plan

## Tasks

1. Update the credential selector and tests to use only numbered Groq keys.
2. Run offline tests and the full P02 gate.
3. Run one live phase-006 case after confirming the model catalog; preserve the phase-005 run.

## Ownership

`allowed_write_paths`: `.planning/phases/006-four-key-live-allowlist/**`, `scripts/run_live_groq_eval.py`, `tests/test_live_groq_eval.py`, `docs/harness/decisions.md`, `docs/harness/progress.md`, `artifacts/evidence/phase-006-groq-*`.

## Limits

Use `openai/gpt-oss-20b`, explicit live mode, existing P02 USD cap, one ticket, max 512 completion tokens, max 20 seconds, and existing bounded rotation policy. Never fall back to a bare key, other provider, or fake mode.

## Validation

Run the focused tests and documented full gate; save command, exit code and sanitized output. Run one authenticated catalog check and live case only after offline gates pass.
