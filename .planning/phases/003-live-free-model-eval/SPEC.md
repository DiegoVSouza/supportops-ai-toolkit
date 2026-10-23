# SPEC — Evaluate the support workflow with a free hosted model

## Goal

Run P02's existing ten-case SupportOps dataset through a real, named free model endpoint and report model results separately from the deterministic fake baseline.

## Acceptance criteria

- Read `OPENROUTER_API_KEY` from the lab-root `.env` without logging it.
- Confirm `cohere/north-mini-code:free` is present in OpenRouter's model catalog and reports zero prompt/completion price before sending prompts.
- Send one request per synthetic case, sequentially, with bounded output tokens and no automatic retries.
- Score only decision, tool choice, and escalation; the fixture lacks independent retrieval context for a valid groundedness score, so that metric remains `NOT_EVALUATED`.
- Save sanitized per-case output, aggregate metrics, token usage, latency, model ID, command, and exit code under `artifacts/evidence/`.
- Do not alter the existing fake-mode regression gate or call paid models.

## Scope

This phase evaluates the P02 dataset against one real free model. It does not evaluate P01 framework adapters or P05's fake-only runtime, and it does not claim production quality from a ten-case synthetic set.

## Budget

The named `:free` model reports zero input/output price. The script still enforces a USD 0.05 local cap and makes at most ten requests, under OpenRouter's current free tier allowance of 50 requests/day.
