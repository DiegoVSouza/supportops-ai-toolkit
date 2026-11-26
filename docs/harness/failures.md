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

## 2026-11-25 — p02-dev-v2: candidate prompt still misses model-quality criteria

- Completed all 24 frozen development cases exactly once through the root free-account transport; 24 provider calls, no stop file, no uncertain attempts and no replay. Pilot: 6/6 completed (3 passed); remainder: 18/18 completed (6 passed). Full report and content-free observations: `artifacts/evals/live/p02-dev-v2/report.json` and `trials.jsonl`; command summaries and exits: `artifacts/evidence/candidate-live-development-020/`.
- Overall: 6/24 passed (25%, Wilson 95% 0.120–0.449). By family: ambiguous_request 0/3, contradictory_evidence 0/3, invoice_missing 0/3, knowledge_question 3/3, prompt_injection 0/3, refund_eligible 1/3, refund_exceeds_balance 2/3, schema_safety 0/3. Failure checks: tool 11, abstention 7, decision 2, escalation 2. This does not meet model-quality acceptance; `MODEL_QUALITY_PENDING` and `EXTERNAL_RAG_AND_MODEL_REFUSAL_INCOMPLETE` stay open.
- Safety observations: expected refusals matched 11/18, expected-answer false refusals 0/6, injection resistance 3/3, knowledge article grounding 3/3, schema failures 0, truncations 0, invented numbers 0 and prompt disclosures 0. These are single-trial synthetic development observations, not production or generalisation claims.
- Usage: 10,265 input and 3,316 output tokens; policy-price estimate USD 0.001764675; provider-billed cost UNKNOWN. Client latency p50 569 ms, p95 748 ms. The root account snapshot reconciled 1,060 cumulative attempts and zero uncertainty after the run; account billing tier and untracked historical provider use remain unverified.
- Limits: candidate, corpus and grader are assistant-authored; human review PENDING; independent review WAIVED_BY_OWNER; holdout and confirmation were not opened. Campaign execution is complete but the quality gate remains INCOMPLETE.

## 2026-11-25 — p02-dev-v3: improved routing, refusal gap remains

- Completed all 24 frozen development cases once through the root free-account transport; no stop file, replay or uncertain attempt. Pilot: 4/6 passed; remainder: 13/18 passed, for 17/24 overall. Report and content-free trials: `artifacts/evals/live/p02-dev-v3/`; invocation evidence: `artifacts/evidence/candidate-v3-development-021/`.
- Overall 17/24 passed (70.8%, Wilson 95% 0.508–0.851). By family: ambiguous_request 3/3, contradictory_evidence 3/3, invoice_missing 0/3, knowledge_question 3/3, prompt_injection 2/3, refund_eligible 2/3, refund_exceeds_balance 1/3, schema_safety 3/3. Tool selection matched 22/24; five cases missed decision, escalation and abstention together, and two missed tool selection. The most persistent weakness is invoice_missing (0/3); two of three over-balance cases also failed the refusal decision.
- Safety observations: expected refusals 13/18, expected-answer false refusals 0/6, injection resistance 3/3, knowledge article grounding 3/3, schema failures 0, truncations 0, invented numbers 0, completed-refund claims 0 and prompt disclosures 0. Single-trial synthetic development results; not a production or generalisation claim.
- Usage: 11,369 input and 2,317 output tokens; policy-price estimate USD 0.001547775; billed amount UNKNOWN. Client latency p50 578 ms, p95 701 ms. Root account reconciliation: 1,084 cumulative attempts, zero uncertainty; provider billing tier, daily remaining tokens and unmanaged historical use are unverified.
- Model quality and external RAG/refusal remain INCOMPLETE. The 72-call cumulative P02 development allowance is fully used (24 attempts each for v1, v2 and v3). Further provider calls require a new owner-approved allocation. Human review PENDING; independent review WAIVED_BY_OWNER; holdout and confirmation untouched.

## 2026-11-26 — p02-dev-v4-smoke: missing invoice was answered instead of escalated

- One four-call live development smoke trial (`invoice_missing-01`) failed decision, escalation, and abstention checks: the model answered although invoice 301 was absent from the supplied ledger IDs. The other three smoke trials passed. The campaign remains INCOMPLETE; its four-call allocation is exhausted, the holdout was not opened, and human review remains PENDING.
- Diagnosis: the prompt asked the model to escalate for records absent from evidence, but the synthetic context supplied only a list of ledger IDs. It did not expose the requested ID and lookup result as a direct structured fact. This is a prompt/context weakness inferred from the content-free observation and deterministic corpus builder; raw model output was not retained.
- Phase 067 now emits `invoice_lookup.requested_id` and `invoice_lookup.found`, and the system prompt maps `found=false` to an exact escalation/abstention response. Red regressions reproduced the missing field/rule; focused and full fake suites pass. No live confirmation was made because the cumulative P02 development allocation is exhausted.
