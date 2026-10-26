# P02 Groq evaluation remediation

## Status

Implemented and verified: the corrected real run passed all three assertions after one non-retryable HTTP 400 request-schema failure was preserved separately.

## Goal

Diagnose and improve the P02 live ticket evaluation after the first real Groq response passed decision/escalation but selected `issue_refund` where the case expected the read-only `lookup_invoice` tool.

## Failure analysis

The run returned a valid structured response (410 reported tokens; no transport retries), so provider transport, model access, and JSON parsing worked. The failure is a domain/tool-selection mismatch. The current system prompt says to classify and choose a tool but does not define tool semantics or require a read-only verification step before an action. The prompt therefore leaves the expected behavior ambiguous for `refund-eligible`. Preserve the real failure report as a baseline.

The first remediation request returned sanitized HTTP 400 before generation. It received no retry because request-validation errors are non-transient. The only request-schema difference from the known-good phase-004 call was a new property-level `description`; remove that field, retain semantic instructions in the system prompt, and allow at most one corrected evaluation request after offline validation.

## Requirements

- Clarify the tool contracts in the prompt: `lookup_invoice` is read-only verification; `issue_refund` is an action and cannot be selected unless the workflow has verified the invoice and policy; the current first-stage assessment must select lookup for this case.
- Keep case labels and offline fake dataset unchanged. Do not rewrite a golden expected value to make a live score pass.
- Add tests that assert the prompt contains the tool safety semantics and that real evaluation still asserts expected decision/tool/escalation.
- Permit one corrected request after the recorded non-retryable HTTP 400; after it, make at most one completed evaluation request, after authenticated model listing, explicit live mode, and bounded free-plan use. Never automatically retry the 400 or a completed but incorrect model response.
- Record both the original failure and remediation run as separate sanitized artifacts. Cost remains `PENDING` until billing is confirmed; do not make further calls if quota/cost cannot be reconciled.

## Acceptance

1. Offline tests and full P02 fake gate pass.
2. The HTTP 400 is preserved, and at most one corrected remediation run reports expected vs predicted fields and the real per-case assertions; pass or fail is retained honestly.
3. The report shows actual returned model/usage, attempts, and sanitized errors with no secret leakage.
4. No fake/replay behavior or dataset baseline is changed.

## Scope

P02 only; prompt, runner tests, artifacts, and phase records. No kit, root `.env`, other project, or broad multi-case run.

## Verified references

- Model capabilities and public developer-plan rate: [Groq GPT-OSS 20B](https://console.groq.com/docs/model/openai/gpt-oss-20b).
- Free-plan limits and `Retry-After` behavior: [Groq rate limits](https://console.groq.com/docs/rate-limits).
- SDK used for the existing opt-in client: [groq-python 1.7.0](https://github.com/groq/groq-python/releases/tag/v1.7.0).
