# Plan check — P02 phase 005

- Evidence identifies a domain/tool-selection mismatch: valid provider response, no transport retries, expected read-only lookup, predicted refund action.
- The prompt lacks definitions and sequence constraints; plan fixes this without altering the dataset label or faking a pass.
- One live rerun is explicitly bounded to one case, 512 output tokens, and one actual evaluation attempt; the completed mismatch is never retried.
- Phase-004 report remains immutable; P02 paths only, with cost recorded `PENDING` absent actual billing data.
- The initial remediation request was rejected with HTTP 400 and was not retried. The plan allows one new, explicitly corrected request after removing the only new tool-schema field, subject to offline gates.

**Plan check: PASS.** The test-first remediation may begin.
