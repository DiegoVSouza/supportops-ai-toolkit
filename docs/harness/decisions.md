# Intake decisions

- Task and measurable success criterion: build a reusable local toolkit; deterministic unit/contract checks, eval metrics, regression failure, at least 30 adversarial cases, and a real full check are reproducible from the repository.
- Pattern (single-call, workflow, or agent): workflow/tooling library, not a customer-facing autonomous agent; a workflow profile is appropriate.
- Runtime rationale: none. This project evaluates and supplies reusable controls; sample tools use local deterministic doubles and no LLM runtime.
- Risk and budget rationale: fake mode only, USD budget 0, no external calls. Untrusted content is in scope; PII can be handled by redaction and refund is an irreversible tool contract. Sensitive data and irreversible action therefore select full governance despite no real connectors.
- Harness modules: long-running Builder/reviewer are retained for staged implementation; eval capability/regression enabled with code-first graders. Production sampling disabled because no production agent/traces exist.
- Phase 004 decision (2026-10-23): add an opt-in Groq live evaluation using the user-designated free-plan credentials, capped at one SupportOps ticket per invocation. Keep the configured USD 0 task budget; because the public developer-plan model price is nonzero and the API does not expose account billing tier, report cost as `PENDING` until billing confirms it. The standard-library fake path remains the default and offline.
- Phase 005 decision (2026-10-26): retain the real phase-004 tool-selection failure, clarify the prompt's read-only lookup versus refund-action semantics, and make at most one remediation call against the same case. Do not change fixture labels; cost remains `PENDING` absent billing confirmation.

## 2026-10-26 — Live Docker acceptance

Use opt-in Groq live mode with numbered credentials and authenticated model preflight. Preserve deterministic fake defaults and fail closed on provider/contract failures. Only local synthetic acceptance and the designated free allowance are authorized; billed cost remains PENDING. Evidence: artifacts/evidence/live-docker/.

## 2026-10-26 — Broad evaluation preparation

Prepare an 80-case synthetic Core toolkit campaign with a fixed 24/56 development/holdout split and 48/32 English/Portuguese coverage. The project profile remains USD 0. Existing single-case free-tier runs do not authorize pilot, primary campaign, confirmation, or hidden judges. Preparation dry-runs only; every live cap, quota, reviewer approval, and cumulative ledger remains `PENDING` or not implemented.

## 2026-10-26 — Bounded campaign ledger

Phase 009 adds P02-local reservation accounting, process exclusion, and read-only resume inspection. It does not change the USD 0 profile or authorize free-tier campaign calls. Reviewer sign-off, quota evidence, finite cumulative limits, confirmation funding, pacing and model preflight remain `PENDING`; generation stays disabled. No provider request was made.

## 2026-11-09 — Sealed development campaign p02-dev-v1

Owner reply of 2026-11-09 ("pode usar os modelos da groq tem as env ai documentada", "faz a 1 mesmo") authorizes free Groq model runs; the root guard admits only campaign `p02-dev-v1` (24 attempts, development split, one trial per case, one call per trial) through the committed `AUTHORIZATION.json` of lab phase 058. P02 builds its own sealed executor (`scripts/campaign_execution.py`): deterministic context for the two families whose text points to artefacts the dataset does not carry, a code-first grader, content-free per-trial observations and a report with tokens, cost, latency percentiles, refusal, injection and grounding measures. The 56 holdout cases and the confirmation reserve stay closed. Corpus context and grader are assistant-authored; human review is PENDING and independent review is WAIVED_BY_OWNER (owner approval, not independent verification). Paid spend stays USD 0.

## 2026-11-23 — Tool-selection candidate

Phase 018 prepares a separate prompt candidate from the recorded development failures. The spent campaign and its prompt stay unchanged; model quality and external RAG remain pending. Candidate tests do not authorize a provider call or any tool effect.

Phase 019 prepares a separate development campaign and binds the candidate prompt to its fingerprint. The original development ceiling and prior usage remain cumulative; holdout and confirmation remain protected. Live dispatch stays closed until root guard, accounting and authorization are verified.
