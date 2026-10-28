# Phase 011 — Empty retrieval results and interruption propagation

## Goal

Tighten two P02-owned local runtime boundaries without changing evaluation data or adding an agent/runtime: local retrieval must not attribute unrelated documents when a query has zero lexical overlap, and the tool registry must propagate process-control interruptions rather than converting them into ordinary tool failures. Preserve source IDs, untrusted provenance, injection screening, citation membership, and no-retry behavior for uncertain operations.

## Acceptance criteria

1. `search_kb` returns only sources with at least one query-term match; empty or punctuation-only effective queries return `{"matches": []}`. Matching documents preserve existing stable source IDs, exact text, untrusted marker, and deterministic score/source ordering.
2. A nonmatching query cannot be used as evidence for citation membership because its supplied-source list is empty.
3. `KeyboardInterrupt` and `SystemExit` raised while waiting for a tool result propagate to the caller, are not wrapped as `ToolError`, and do not trigger retries. Ordinary explicit retryable `ToolError` behavior remains unchanged.
4. Existing timeout uncertainty remains unchanged: a timed-out running handler is not automatically retried and is documented as still possibly running.
5. Focused, fast, and complete offline fake gates pass. Dataset/split, rubric, graders, thresholds, adversarial cases, provider history, campaign config/ledger, and historical evidence are unchanged.
6. No provider, credential, external source/network, Docker, customer data, refund side effect, or paid use occurs. External retrieval, tenant isolation, and model-level refusal remain INCOMPLETE.

## Constraints

- This remains a local toolkit contract phase, not a production RAG connector or integrated LLM runtime.
- Do not weaken injection tests, citation membership rules, timeouts, role authorization, schema checks, or no-retry handling for ambiguous failures.
- Do not treat sample articles or golden facts as real product retrieval evidence.
