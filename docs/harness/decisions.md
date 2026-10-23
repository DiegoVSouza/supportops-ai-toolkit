# Intake decisions

- Task and measurable success criterion: build a reusable local toolkit; deterministic unit/contract checks, eval metrics, regression failure, at least 30 adversarial cases, and a real full check are reproducible from the repository.
- Pattern (single-call, workflow, or agent): workflow/tooling library, not a customer-facing autonomous agent; a workflow profile is appropriate.
- Runtime rationale: none. This project evaluates and supplies reusable controls; sample tools use local deterministic doubles and no LLM runtime.
- Risk and budget rationale: fake mode only, USD budget 0, no external calls. Untrusted content is in scope; PII can be handled by redaction and refund is an irreversible tool contract. Sensitive data and irreversible action therefore select full governance despite no real connectors.
- Harness modules: long-running Builder/reviewer are retained for staged implementation; eval capability/regression enabled with code-first graders. Production sampling disabled because no production agent/traces exist.
- Phase 004 decision (2026-10-23): add an opt-in Groq live evaluation using the user-designated free-plan credentials, capped at one SupportOps ticket per invocation. Keep the configured USD 0 task budget; because the public developer-plan model price is nonzero and the API does not expose account billing tier, report cost as `PENDING` until billing confirms it. The standard-library fake path remains the default and offline.
