# P02 phase 006 verification

## Plan gate

- Confirm only `GROQ_API_KEY_1..4` are selected and secrets remain in memory.

## Offline gate

- Run credential-selection tests and the full P02 offline gate with fake mode.

## Live gate

- Confirm the model is available with numbered credentials and execute one synthetic P02 case under the existing budget.
- Preserve sanitized command, exit code, usage and assertions in phase-006 evidence.

## Review

- Keep cost pending when billing is unavailable. Inspect artifacts and staged diff for secret exposure. Commit locally without push.

## Recorded result — 2026-10-26

- Full P02 gate passed: 40 tests, fake eval 10/10 and adversarial suite 35/35. The four-key selection test passed.
- Live command: `LLM_MODE=live uv run --extra live python scripts/run_live_groq_eval.py`; exit 0. Authenticated preflight passed; `openai/gpt-oss-20b` matched expected answer, `lookup_invoice`, and no escalation. Usage was 319 prompt / 472 completion tokens; no retries or rotation; billed cost `PENDING`.
- The phase-005 remediation artifact is preserved. New phase-006 evidence is `artifacts/evidence/phase-006-groq-four-key.json/.txt`.
