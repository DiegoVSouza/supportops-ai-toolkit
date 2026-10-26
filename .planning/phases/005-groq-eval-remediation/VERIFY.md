# P02 remediation verification

- Review the recorded phase-004 mismatch and confirm it was a completed provider response, not a retryable request error.
- Verify a deterministic unit test checks the prompt's tool definitions and no retry of evaluator failures.
- Run focused tests and the full offline P02 gate; save output and exit codes in phase-005 evidence.
- Reconfirm `openai/gpt-oss-20b` availability before one remediation call. Use one case, no more than 512 output tokens, and no extra retries after a response.
- Preserve the recorded HTTP 400 and confirm the corrected request uses the last known-good tool schema shape; this is a new planned attempt, not an automatic retry.
- Preserve phase-004 failure; save sanitized phase-005 prediction, expected fields, usage, status, and command/exit code separately.
- Review artifacts/diff for credentials and ensure cost is `PENDING` unless actual billing is confirmed.
- Commit the P02 phase locally without push. Report the capability gate incomplete if the tool assertion still fails.
