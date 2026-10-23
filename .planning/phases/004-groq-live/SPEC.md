# P02 Groq live evaluation

## Status

Implemented; verification is incomplete because the real case failed its tool assertion.

## Goal

Run a small, domain-relevant P02 SupportOps ticket-classification evaluation against Groq `openai/gpt-oss-20b`, with bounded key rotation and sanitized evidence, while keeping offline fake evaluation deterministic.

## Selection rationale

P02 is the selected project because it is an `eval-infra` toolkit with a versioned ten-case SupportOps dataset, code-first decision/tool/escalation assertions, an existing fake regression suite, and a live-evaluation script. P00, P01, P03, P04, and P05 are not selected: this phase does not need to add provider calls to their package/client, framework-comparison, observability, async-workflow, or retrieval-evaluation responsibilities.

## Existing state

P02 currently has `budget.max_usd_per_task: 0`, no integrated agent runtime, and an opt-in script that uses a different free provider for ten cases. Existing fake evaluation is offline. The live script stores a JSON report in `artifacts/evidence/`; its prior run is incomplete and must not be overwritten. This phase adds a distinct Groq report and preserves prior evidence.

## Requirements

- Use the official Groq SDK and model ID `openai/gpt-oss-20b`; check authenticated model availability before evaluation prompts.
- Verify the current SDK/model/rate-limit references before live calls; the SDK is pinned as an optional live extra so the default toolkit remains dependency-free.
- Read the lab-root `.env` without printing or persisting credential values. Support `GROQ_API_KEY` and `GROQ_API_KEY_1` through `_4`, deduplicate identical configured values in memory, and never emit key-derived identifiers.
- `LLM_MODE=live` must be explicit. Missing/invalid configuration fails closed; never fall back to fake or another provider.
- Make at most one availability request and one logical evaluation for one selected case per run. Cap completion at 512 tokens, request timeout at 20 seconds, and actual evaluation attempts to one bounded pass over configured unique keys. Do not fan out.
- Rotate only for HTTP 429 and transient transport/server failures. Apply capped exponential backoff with jitter, honor `Retry-After` values within the configured wait ceiling, and stop rather than retry early when the provider asks for a longer wait. Stop on auth, permission, model, validation, or policy errors. Do not retry a case after a successful provider response with invalid evaluation output.
- Enforce the existing USD 0 task budget by using only the user-designated free-plan credentials and stopping on exhausted free quota. The model's public developer-plan rate is nonzero and Groq's model-list API does not expose account billing tier; therefore never infer billed cost from that catalog or token usage, and report `PENDING` unless actual account billing confirms it.
- Assert the selected case's expected decision, tool, and escalation behavior using P02's versioned dataset; store sanitized prediction/checks and provider-reported token usage.
- Record command, exit code, timestamps, provider/model, sanitized outcome/error class and status, retry/key-rotation counts, case identifier, expected/predicted domain fields, provider-reported usage, and `PENDING` cost unless charged cost is confirmed. No prompts or raw provider bodies are needed in the report.
- Preserve fake/replay paths and deterministic offline checks.

## Acceptance criteria

1. Plan and verification files are complete and path ownership is disjoint before implementation.
2. Unit tests cover safe environment loading, rotation exhaustion, transient-only retry, non-retryable errors, bounded `Retry-After`, explicit live mode, model catalog validation, sanitization, and the domain assertion.
3. Existing offline fake evaluations remain deterministic and pass without network access.
4. A single real evaluation runs only after model listing; it succeeds or stores a precise sanitized failure report. Metrics are recorded only from a completed real provider response, including failed assertions.
5. No credential values, prefixes, hashes, or request headers appear in output, logs, diffs, or artifacts.
6. Full project validation passes or the phase is reported incomplete with command, exit code, and sanitized output saved under `artifacts/evidence/`.

## Risks and boundaries

The free-tier service can throttle or change model access. The bounded retry policy and fail-closed free-plan boundary stop further calls; there is no paid-provider fallback. The one-case run is a smoke evaluation, not a quality benchmark. Root `.env` remains local and must not be staged.

## Verified provider references

- Model capability, public developer-plan price, and SDK example: [Groq GPT-OSS 20B model page](https://console.groq.com/docs/model/openai/gpt-oss-20b).
- Free-plan per-model limits and `Retry-After` guidance: [Groq rate limits](https://console.groq.com/docs/rate-limits).
- Official Python SDK release pinned for the optional `live` extra: [groq-python releases](https://github.com/groq/groq-python/releases), version `1.7.0`.
