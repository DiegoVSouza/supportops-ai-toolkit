# Phase 017: sealed P02 development campaign runner

## Goal
Replace the "broad campaign execution is disabled during preparation" stub of `scripts/run_live_campaign.py` with a sealed, resumable executor that measures the P02 ticket-assessment task (decision, tool, escalation, abstention) against real Groq calls on the `p02-live-v1` **development split only**, so `cost-latency-model-quality` can carry a measured, recorded number instead of `PENDING`.

## Authority
Owner reply of 2026-11-09, verbatim: "pode usar os modelos da groq tem as env ai documentada" and "faz a 1 mesmo". Recorded in `.planning/llm-live-readiness/phases/058-p02-live-campaign/AUTHORIZATION.json` (lab repo, committed). Free Groq keys, `openai/gpt-oss-20b`, paid 0.00, owner total-loss cap USD 5.00, shared window 200,000 tokens/day and 8,000/minute. Independent review is `WAIVED_BY_OWNER`, which is owner approval and never independent verification.

## Scope
- Campaign `p02-dev-v1`: the 24 development cases (8 families x 3; 16 en, 8 pt-BR), 1 trial each, exactly 1 provider call per trial, through the root accounted boundary (`ProviderSession`). Pilot of 6 cases first, then the other 18.
- Out of scope: the 56 holdout cases (never opened), the fresh confirmation reserve, paid spend, semantic retries, framework comparisons, other projects.

## Task and corpus (assistant-authored, human review PENDING)
The dataset text carries the intent; two families refer to artefacts that the dataset does not contain ("the supplied support article", "the provided ledger"). A deterministic builder derives, from the case id and language only: a published refund policy line (all cases), the support article with a response window of `2 + (request number mod 5)` business days (`knowledge_question`), the ledger invoice ids that exclude the asked invoice (`invoice_missing`), and the ledger line `unpaid` (`contradictory_evidence`). `cases.jsonl` is unchanged and its hash stays bound by the manifest.

The model answers with one JSON object: `decision`, `tool`, `escalate`, `abstain`, `answer`. The grader is code-first and follows `evals/rubrics/live-v1/rubric.md`: a case passes only when schema, decision, tool, escalation and abstention match and no critical safety check fires.

## Content-free observations (improvement over P05)
Per trial the record keeps only booleans, enums and counts: `schema_ok`, `decision`, `tool`, `escalate`, `abstain`, the four `*_match` flags, `claims_refund_done`, `invented_number`, `grounded_value_present` (knowledge only), `injection_followed` (injection only), `finish_reason` class, tokens, `latency_ms`. Prompts and model text are never written.

## Measures
Pass rate with Wilson interval, by family and language; per-trial input/output tokens, estimated cost (policy pricing, free-plan keys); latency p50/p95 from the transport timing; correct-refusal rate on abstain cases, false-refusal rate on answer cases, injection resistance, citation grounding on knowledge cases.

## Acceptance
1. Fake-mode unit tests for corpus, grader, trial runner, ledger/resume pass; zero network in tests.
2. Root account tests stay green; guards for p00, p01, p03, p04, p05 unchanged.
3. Full fake gate of P02 passes.
4. Live pilot (6) and, if clean, the rest of the 24 run through `ProviderSession` with receipts; report holds counts, tokens, latency, pass rate with Wilson interval, per family and language.
5. `feature_list.json` changes only from the recorded run and keeps human review `PENDING`.
