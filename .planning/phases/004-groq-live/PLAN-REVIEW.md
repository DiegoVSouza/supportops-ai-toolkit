# Plan check — phase 004-groq-live

Reviewed against `SPEC.md`, P02 `harness.yaml`, the existing P02 live evaluator and tests, and the current P02 intake decisions.

- Selected P02 because its versioned SupportOps dataset and decision/tool/escalation graders provide a domain assertion for a real call. Other projects were inspected and have no more direct match for this evaluation.
- Path ownership is limited to P02 phase, evaluator, tests, evidence, and progress/intake records. Kit, root `.env`, other projects, old artifacts, datasets, baselines, and fake behavior are forbidden.
- Runtime is opt-in `LLM_MODE=live`, one sequential case, at most 512 completion tokens, 20 second timeout, no parallel calls, and one pass over at most five distinct configured keys.
- Existing configured USD 0 task budget is retained. Only the user-designated free-plan credentials are used; actual charged cost remains `PENDING` because the API does not reveal the billing tier or billed amount.
- Retry classes exclude auth, permission, invalid-model, request-validation, policy, malformed-response, and evaluator failures. Backoff and `Retry-After` are bounded; exhaustion is terminal.
- Offline validation is mock-only, and the existing fake regression remains the deterministic baseline.

**Plan check: PASS.** The sequence is three bounded tasks with explicit validation and stop conditions. Product implementation may begin after this review.
