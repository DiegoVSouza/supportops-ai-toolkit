# Plan

Allowed write paths: `scripts/campaign_corpus.py`, `tests/test_campaign_corpus.py`, `docs/harness/failures.md`, `docs/harness/progress.md`, `.planning/phases/067-invoice-missing-evidence/**`, and `artifacts/evidence/invoice-missing-repair/**`.

Forbidden: dataset edits, changes to completed campaign ledgers or results, new live calls, holdout access, and root account policy changes.

LLM mode: `fake` only. Stop before any provider access.

1. Add regression assertions for explicit missing-invoice evidence and the required escalation fields; run them to confirm they fail against the current implementation.
2. Update the deterministic case builder and system prompt to state the exact missing lookup result and required abstention/escalation response.
3. Run the focused regression and full P02 test suite, save command, exit code, and output under `artifacts/evidence/invoice-missing-repair/`, then review and commit the phase.

Validation commands:

- `uv run --with pytest python -m pytest tests/test_campaign_corpus.py -q`
- `uv run --with pytest python -m pytest tests -q`

Stop condition: both fake-mode test commands pass. Do not dispatch live calls; the prior four-call smoke allocation is exhausted.
