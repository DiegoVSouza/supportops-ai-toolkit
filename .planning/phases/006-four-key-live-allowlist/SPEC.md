# P02 four-key Groq credential boundary

## Status

Implemented and verified. The four-key allowlist passed both the offline suite and a real P02 evaluation without rotation.

## Goal

Align P02's live runner with the lab instruction to use only `GROQ_API_KEY_1` through `GROQ_API_KEY_4`. The root `GROQ_API_KEY` may exist for unrelated compatibility and must not silently become an additional evaluation credential.

## Requirements

- Read root `.env` silently and collect only the four numbered variable names, deduplicating equal values in memory.
- Preserve explicit `LLM_MODE=live`, authenticated model preflight, bounded transient retries and the existing phase-005 budget.
- Keep failures and prior real evidence intact; do not print or persist secrets or secret-derived identifiers.
- Fake/replay behavior remains deterministic and network-free.

## Acceptance

1. Offline tests prove the bare key is ignored and numbered keys are deduplicated.
2. The existing P02 real evaluation passes with the four-key allowlist, or leaves a sanitized failure.
3. Existing phase-005 successful and failed evidence remains untouched.

## Scope

P02 runner, unit tests, this phase, and new phase-006 evidence only. No kit/sibling project changes.
