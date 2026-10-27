# Phase 010 — Retrieval provenance and indirect-injection boundary

Status: PLANNED. This is an offline toolkit contract phase; live campaigns, external knowledge sources, and model quality remain INCOMPLETE.

## Goal

Make P02's actual local knowledge-search tool return attributable, explicitly untrusted evidence and provide a fail-closed screening boundary for retrieved text. Preserve the existing deterministic injection guard and its false-positive/false-negative limitations. Make no claim that this toolkit is a production RAG runtime.

## Context and constraints

- P02 owns `supportops_toolkit.sample_tools.search_kb`, the local `ARTICLES` fixture, guardrails, and deterministic evaluation helpers. It owns no external retrieval service, tenant authorization layer, or integrated LLM runtime.
- Retrieved content is data, not policy or instructions. Each result must identify its source and state that provenance does not imply trust.
- Direct and indirect injection must use an explicitly named screening boundary; screening is heuristic and cannot certify content as safe.
- Answers that cite evidence must cite source identifiers actually supplied to the caller. Unsupported or unknown citations fail closed.
- No expected labels, hidden rubric facts, or holdout content may be inserted into retrieval prompts or implementation decisions.
- Preserve datasets, splits, rubrics, graders, thresholds, historical reports, provider ledgers, and all live campaign configuration.
- No provider calls, credentials, network, Docker changes, refund execution, external effects, or paid/free live evaluation.

## Acceptance criteria

1. Local search results include stable source IDs, exact source text, and an explicit untrusted-content marker; search ordering and existing local behavior remain deterministic.
2. A single shared screening function can be applied to both user text and retrieved text, returning a sanitized typed verdict and a non-executable refusal/block outcome for detected injection. PII redaction remains intact.
3. The real local retrieval-to-screening path has contract tests for safe policy text, indirect injection, PII, and no conversion of tool text into executable actions.
4. Citation validation accepts only source IDs made available in the current retrieval result; unknown/missing citations fail. It does not claim entailment or model groundedness from ID matching alone.
5. Fake/offline tests and complete P02 gates pass. Outputs are saved without changing pre-existing user-modified artifacts.
6. External KB, tenant isolation, real refusal behavior in a live model, human rubric review, and campaign quality remain explicitly INCOMPLETE/PENDING.

## Out of scope

External RAG connectors, vector databases, auth/tenant systems, prompt/model runtime, tool execution authorization, refund execution, dataset/rubric/grader/threshold changes, live calls, hidden judges, Docker, budget changes, other projects, or promotion.
