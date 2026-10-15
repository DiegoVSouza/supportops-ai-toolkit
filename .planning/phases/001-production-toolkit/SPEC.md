# P02 Production AI Toolkit Specification

## Goal
Provide a versioned, dependency-light Python toolkit that makes SupportOps tools reliable, measurable, guarded, and cost-aware under deterministic fake execution.

## Acceptance criteria
- Tool registration validates JSON-compatible input/output contracts and enforces bounded retries, timeout, and retryable/fatal error classification.
- Sample invoice lookup, bounded refund, and knowledge search tools use local deterministic fixtures.
- Versioned eval dataset and runner report decision accuracy, tool-call accuracy, rule-based groundedness, escalation accuracy, and regression against baseline with a configurable failure threshold.
- Guardrails classify injection, enforce role tool allowlists, execution limits, and redact common PII; at least 30 adversarial cases span direct/indirect injection, exfiltration, abuse, and refund limits and expose misses.
- Cost utilities include exact cache, token budget, deterministic model routing, streaming helper, and before/after report. No model quality or live cost claims from fake runs.
- Unit and failure/boundary tests cover the above. `LLM_MODE=fake` is the only configured default; no paid model calls.
- README EN/PT-BR and knowledge doc PT-BR with interview answers in EN/PT.
- All implementation evidence is captured with command, exit code, output; validation distinguishes unit/eval. Missing integrations remain INCOMPLETE.

## Public contracts
Package `supportops_toolkit`; decorator `tool(schema_in, schema_out, timeout_s, retries)`, `ExecutionLimits`, `guard(input_text, role)`, `run_evals(runner, dataset)`, and `ModelRouter.pick(task)`. Any incompatible public change requires ADR and version update.

## Scope
Local contract doubles only. No sibling imports, external publication, paid LLM, tracing/dashboard, queues, or multi-agent orchestration.
