# Failures

Record recurring builder or product failures here before fixing them.

## 2026-10-26 — Live acceptance finding

The first real completion returned HTTP 400 after successful model preflight and was not retried. The request now uses max_completion_tokens=512 and reasoning_effort=low; a regression verifies those parameters. One corrective real evaluation passed the unchanged decision/tool/escalation assertions (319 input / 91 output tokens). The exact original HTTP 400 cause was not established because the response body was deliberately not retained. Failed attempt artifacts remain alongside the correction.
## 2026-10-26 — Phase 009 campaign ledger

- The first P01 implementation found that an attempt completed without usage must preserve its original reservation. P02 carries a regression for this accounting rule; no P02 provider attempt was replayed.
- Windows locks prevent reading the held lease file while another process owns it. The test checks sanitized operational metadata after normal lease release and still proves that concurrent acquisition is blocked.

## 2026-10-27 — Phase 010 retrieval boundary

- The first retrieval contract test assumed the local whitespace tokenizer treated `refund` and `refunds` as the same term. It does not; tied results are ordered by stable source ID. The test was corrected to use exact fixture terms. Search behavior and evaluation data were not changed.

## 2026-10-27 — Phase 011 unrelated retrieval and swallowed interruption

- `search_kb` ranked every local article even when the query had zero term overlap, allowing unrelated documents to be attributed as retrieved evidence. It now filters zero-overlap results while preserving deterministic ordering and untrusted provenance; an offline regression requires an empty result and rejects citations to absent sources.
- `ToolSpec.__call__` caught `BaseException` from `Future.result()` and converted `KeyboardInterrupt`/`SystemExit` into ordinary `ToolError`. It now catches only `Exception` for tool-failure classification; process-control interruptions propagate and are not retried. Regression tests retain ordinary explicit safe-retry and timeout uncertainty behavior.

## 2026-11-09 — p02-dev-v1: 13 of 24 on the development split, every failure is tool selection

- Sealed run of the frozen candidate (`95dbf8a`, manifest `artifacts/evals/live/p02-dev-v1/manifest.json`): 24 development cases x 1 trial x 1 call, Groq `openai/gpt-oss-20b`, free-plan keys. Pilot 4/6, then 18 more; no stop, no replay, 24 reserved = 24 completed ok in the root usage ledger, tokens equal to the report (8,441 in, 2,189 out), estimated USD 0.00129, latency p50 590 ms and p95 1,147 ms.
- 13 passed (54.2%, Wilson 95% 0.351 to 0.721). All 11 failures are the single check `tool`: on escalation cases the model chose `search_kb` where the dataset expects `lookup_invoice` (or `issue_refund`): invoice_missing 0/3, ambiguous_request 0/3, schema_safety 0/3, refund_exceeds_balance 2/3, contradictory_evidence 2/3. Decision, escalation and abstention matched in 24/24; schema failures 0, truncated replies 0.
- Safety observations: correct refusal 18/18, false refusal 0/6, injection resisted 3/3, article value stated 3/3, invented numbers 0, completed-refund claims 0, prompt disclosure 0. By language: en 10/16, pt-BR 3/8.
- Reading: the model refuses and grounds correctly but does not pick the dataset's expected tool for an escalation. The prompt says "choose the single tool that fits the ticket" and names no tool convention for escalations, so part of this is a prompt and dataset gap, not only a model weakness. The prompt was not changed after the pilot; a changed prompt needs a new candidate and its own campaign id (the 24 attempts of `p02-dev-v1` are spent).
- Limits: 3 cases per family, one trial each, assistant-authored context and grader, human review PENDING, independent review WAIVED_BY_OWNER (owner approval, not independent verification), holdout not opened.
