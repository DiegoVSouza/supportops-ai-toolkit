# SupportOps AI Toolkit

Version `0.2.0` is a standard-library runtime toolkit for deterministic SupportOps workflows. It demonstrates contracts for tool schemas, resilient execution, code-first evaluation, safety controls, and local cost helpers. Sample data and fake eval results are fixtures, not production measurements.

## Problem

Tool calls inside an agent workflow need explicit schemas, bounded execution, and a way to reject unsafe input before a model or adapter can act on it.

## Architecture

The toolkit separates the tool registry, guardrails, deterministic evaluators, and local cost helpers. It has no provider adapter or external connector.

## Quickstart

- Python `3.13+` (the verified environment is recorded in `docs/harness/sources.lock.json`).
- Runtime has no third-party dependencies. Build tooling is pinned in `requirements-build.lock`.
- Default mode is `LLM_MODE=fake`; there is no live model adapter and no external connector.
- The optional `live` extra installs the official Groq SDK for a bounded evaluation script; it is not required by the default toolkit.

Run the full deterministic gate from the repository root:

```powershell
$env:LLM_MODE = 'fake'
python scripts/check_full.py
```

Run a local tool example:

```powershell
python -c "from supportops_toolkit.sample_tools import lookup_invoice; print(lookup_invoice(invoice_id='inv-100'))"
```

## How it works

Use the `tool` decorator with the documented JSON-schema subset: `object`, `array`, `string`, `integer`, `number`, `boolean`, and `null`; `enum`; object `required`, `properties`, and `additionalProperties`; string `minLength`/`maxLength`; and numeric `minimum`/`maximum`. Unsupported keywords fail at registration. Boolean values are not numbers, and numeric inputs/outputs must be finite. This is not a complete JSON Schema implementation.

```python
from supportops_toolkit.tools import tool

@tool(
    schema_in={"type": "object", "required": ["query"], "properties": {"query": {"type": "string", "minLength": 1}}, "additionalProperties": False},
    schema_out={"type": "object", "required": ["matches"]},
    timeout_s=2,
    retries=1,
)
def search(query: str) -> dict:
    return {"matches": []}
```

Retries apply only to explicitly marked `ToolError(retryable=True)` failures. Generic timeouts and transport errors have an indeterminate outcome and are never retried automatically, because a handler may still be running or may have committed a side effect. The in-process thread timeout stops waiting but cannot terminate a running thread; use process/service isolation for hard cancellation. Pass `execution_limits=limits` to a tool call to consume one step and cap its wait by the remaining wall-clock budget. The LLM boundary must call `limits.consume(tokens=...)` with reported usage; this toolkit does not own an LLM execution path, so token enforcement across model calls remains incomplete.

## Results

```powershell
$env:LLM_MODE = 'fake'
python -m supportops_toolkit.evals.runner --dataset evals/datasets/v1/supportops.jsonl --baseline evals/baseline/v1.json
```

The runner reports decision accuracy, tool-call accuracy, rule-based groundedness, escalation accuracy, and failed case IDs. A drop greater than the configured `--max-drop` fails the gate. The current perfect scores come from canned synthetic labels and only prove fixture consistency. They do not measure model quality.

## Security & reliability

`supportops_toolkit.guardrails.guard` screens user and retrieved text, returns `allow`, `block`, or `redact`, and masks email, phone, and card-like strings. `authorize_tool(role, tool_name)` independently enforces role-specific tool allowlists. `ExecutionLimits` counts tool steps and enforces elapsed time in the tool call path; token usage is enforced when an LLM adapter reports it through `consume(tokens=...)`. The adversarial cases in `guardrails/adversarial.jsonl` cover direct and retrieved-content injection, exfiltration, role/tool abuse, and excessive refunds. The suite prints misses instead of hiding them.

These lexical checks are defense-in-depth, not a guarantee against novel attacks. Refunds remain `approved_pending_human`; this project does not connect to a payment system.

## Interpret cost reports

`ExactCache` uses canonical JSON keys; `SemanticCache` uses token-set Jaccard similarity within an explicit namespace. The semantic cache is lexical and may return a poor match; use a high threshold and domain/version namespaces. `ModelRouter` chooses the configured cheap or strong model name from an explicit task profile; it makes no provider call. `TokenBudget` enforces a local counter, and `stream_text` forwards string chunks.

`python cost/report.py` prints `PENDING` because no comparable recorded runs exist. Supply two recorded run dictionaries to `build_report` to calculate deltas. No fake savings, latency, or token figures are presented as real results.

## Testing

- Unit/contract: `python -m unittest discover -s tests -v`.
- Offline eval gate: `LLM_MODE=fake python -m supportops_toolkit.evals.runner`.
- Adversarial suite: `python -m supportops_toolkit.adversarial`.
- Full deterministic CI gate: `python scripts/check_full.py`.
- Live Groq evaluation: set `$env:LLM_MODE = 'live'`, then run `uv run --extra live python scripts/run_live_groq_eval.py`. It checks model availability and evaluates one versioned SupportOps case, using the lab-root `.env` without printing credentials. It exits nonzero when a domain assertion fails. The free-plan allowance is required; cost remains `PENDING` until actual billing is confirmed. See `.planning/phases/004-groq-live/` for limits and evidence.
- External integrations and E2E: `INCOMPLETE` (no connectors are part of this project).

Evidence files under `artifacts/evidence/` record commands, exit codes, and output. See `.planning/phases/001-production-toolkit/` for the spec, plan, and verify checklist.

## Design decisions

Retries require an explicit safe-to-retry signal, schema support stays intentionally small, and fake results are labeled as fixtures rather than model measurements.

## Limitations

Lexical screening is defense in depth, not a general prompt-injection solution. Live models, external tools, and E2E integrations remain `INCOMPLETE`.
