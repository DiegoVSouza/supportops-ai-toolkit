# Verification: P02 Groq live evaluation

Use a clean-context review against SPEC.md and PLAN.md.

## Planning gate

- Confirm selected project rationale and existing state from P02 files.
- Confirm `allowed_write_paths` do not include the kit, root `.env`, or other projects.
- Confirm model, request/token caps, USD 0 policy, retry classes, and stop conditions are explicit.
- Confirm this file existed before implementation.

## Offline gate

- Run `python -m unittest discover -s tests -p "test_live_groq_eval.py"` and `python -m unittest discover -s tests -p "test_evals.py"` from P02 with no live mode. Confirm mocks only and deterministic fake baseline.
- Run the P02 documented full check.
- Save exact command, exit code, and sanitized output under `artifacts/evidence/phase-004-groq-live-offline.txt`.

## Live gate

- Check `openai/gpt-oss-20b` availability using the official SDK and credentials loaded silently from the lab-root `.env`.
- Use the user-designated free-plan credentials and confirm the requested model in the authenticated catalog before the single logical evaluation. The public model page lists developer-plan rates, while the SDK catalog does not report the account tier; record cost as `PENDING` unless actual billing confirms zero.
- Run exactly one sequential dataset case with `LLM_MODE=live`, <=512 output tokens, and bounded timeout/retries.
- Save sanitized report and command/exit code under `artifacts/evidence/phase-004-groq-live-run.json` and `.txt`.
- Review all artifacts for secrets, raw headers, prompts, and unredacted provider errors.

## Acceptance review

- Fake/replay remains offline and deterministic.
- Rotation and retry unit tests prove the one-pass ceiling and that non-retryable failures do not rotate.
- A real run reports only provider-returned token usage; per-case decision/tool/escalation metrics are reported only when a real case completed. Cost remains `PENDING` until actual billing is confirmed.
- Review `git diff --check`, staged diff, and local commit hook. Commit the completed phase atomically; never push.

If any gate cannot run, record `INCOMPLETE`, the sanitized command output and exit code, and do not claim completion.
