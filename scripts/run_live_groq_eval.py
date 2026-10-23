"""Run one bounded P02 support-ticket case against Groq when explicitly enabled."""

from __future__ import annotations

import json
import os
import random
import sys
import time
from datetime import UTC, datetime
from pathlib import Path
from typing import Callable

ROOT = Path(__file__).resolve().parents[1]
LAB_ROOT = ROOT.parents[1]
sys.path.insert(0, str(ROOT))

from supportops_toolkit.evals.runner import load_dataset

MODEL = "openai/gpt-oss-20b"
CASE_ID = "refund-eligible"
MAX_COMPLETION_TOKENS = 512
TIMEOUT_SECONDS = 20
MAX_RETRY_AFTER_SECONDS = 2.0
MAX_BACKOFF_SECONDS = 2.0
ARTIFACT = ROOT / "artifacts" / "evidence" / "phase-004-groq-live-run.json"


def load_root_env(environ: dict[str, str] | None = None) -> dict[str, str]:
    """Load root .env into a private mapping; never print or persist values."""
    values = dict(os.environ if environ is None else environ)
    env_path = LAB_ROOT / ".env"
    if not env_path.is_file():
        return values
    for raw in env_path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        name, value = line.split("=", 1)
        name = name.strip()
        if name and name not in values:
            values[name] = value.strip().strip('"').strip("'")
    return values


def configured_keys(environ: dict[str, str]) -> list[str]:
    keys: list[str] = []
    for name in ("GROQ_API_KEY", "GROQ_API_KEY_1", "GROQ_API_KEY_2", "GROQ_API_KEY_3", "GROQ_API_KEY_4"):
        value = environ.get(name, "").strip()
        if value and value not in keys:
            keys.append(value)
    return keys


def require_live_mode(environ: dict[str, str]) -> None:
    if environ.get("LLM_MODE", "").strip().lower() != "live":
        raise RuntimeError("set LLM_MODE=live explicitly to enable Groq evaluation")


def verify_model_available(response: object) -> None:
    if not any(getattr(item, "id", None) == MODEL for item in getattr(response, "data", [])):
        raise RuntimeError("requested model is unavailable in the authenticated Groq catalog")


def classify_error(exc: Exception) -> tuple[bool, str, int | None]:
    status = getattr(exc, "status_code", None)
    if status is None:
        response = getattr(exc, "response", None)
        status = getattr(response, "status_code", None)
    if isinstance(status, int):
        retryable = status == 429 or status in {408, 409, 500, 502, 503, 504}
        return retryable, "http_error", status
    name = type(exc).__name__
    if name in {"APIConnectionError", "APITimeoutError", "TimeoutError", "ConnectionError"}:
        return True, "transport_error", None
    return False, "provider_error", None


def retry_delay(
    retry_index: int,
    headers: object = None,
    *,
    jitter: Callable[[], float] = random.random,
) -> float | None:
    retry_after = None
    if headers is not None:
        try:
            raw = headers.get("retry-after") or headers.get("Retry-After")
            if raw is not None:
                retry_after = float(raw)
        except (AttributeError, TypeError, ValueError):
            retry_after = None
    if retry_after is not None and retry_after >= 0:
        return retry_after if retry_after <= MAX_RETRY_AFTER_SECONDS else None
    base = min(0.5 * (2**retry_index), MAX_BACKOFF_SECONDS)
    return min(base + jitter() * 0.25, MAX_BACKOFF_SECONDS)


def run_with_rotation(
    keys: list[str],
    client_factory: Callable[[str], object],
    operation: Callable[[object], object],
    *,
    sleep: Callable[[float], None] = time.sleep,
    jitter: Callable[[], float] = random.random,
) -> tuple[object, int]:
    if not keys:
        raise RuntimeError("no Groq API key is configured")
    for index, key in enumerate(keys):
        client = client_factory(key)
        try:
            return operation(client), index
        except Exception as exc:
            retryable, error_class, status = classify_error(exc)
            if not retryable:
                raise RuntimeError(f"non-retryable provider failure: {error_class}, status={status}") from None
            if index == len(keys) - 1:
                break
            headers = getattr(exc, "headers", None)
            delay = retry_delay(index, headers, jitter=jitter)
            if delay is None:
                raise RuntimeError("provider Retry-After exceeds the configured wait ceiling") from None
            sleep(delay)
    raise RuntimeError("retryable failures exhausted after one configured key pass") from None


def parse_assessment(message: object) -> dict[str, object]:
    calls = (message.get("tool_calls") if isinstance(message, dict) else getattr(message, "tool_calls", None)) or []
    if not calls:
        raise ValueError("missing assessment tool call")
    call = calls[0]
    function = call.get("function") if isinstance(call, dict) else getattr(call, "function", None)
    name = function.get("name") if isinstance(function, dict) else getattr(function, "name", None)
    arguments = function.get("arguments") if isinstance(function, dict) else getattr(function, "arguments", None)
    if name != "submit_assessment":
        raise ValueError("unexpected assessment tool")
    try:
        value = json.loads(arguments)
    except (TypeError, json.JSONDecodeError) as exc:
        raise ValueError("malformed assessment arguments") from exc
    if not isinstance(value, dict):
        raise ValueError("assessment must be an object")
    decision, tool, escalate = value.get("decision"), value.get("tool"), value.get("escalate")
    if decision not in {"answer", "escalate"}:
        raise ValueError("invalid decision")
    if tool not in {"lookup_invoice", "issue_refund", "search_kb"}:
        raise ValueError("invalid tool")
    if not isinstance(escalate, bool):
        raise ValueError("invalid escalation value")
    return {"decision": decision, "tool": tool, "escalate": escalate}


def _new_client(key: str) -> object:
    try:
        from groq import Groq
    except ImportError as exc:
        raise RuntimeError("official Groq SDK is unavailable; install the project's live extra") from exc
    return Groq(api_key=key, timeout=TIMEOUT_SECONDS, max_retries=0)


def _load_case() -> dict[str, object]:
    dataset = load_dataset(ROOT / "evals/datasets/v1/supportops.jsonl")
    case = next((item for item in dataset if item["id"] == CASE_ID), None)
    if case is None:
        raise RuntimeError("selected evaluation case is missing from the versioned dataset")
    return case


def _predict(client: object, case: dict[str, object]) -> object:
    return client.chat.completions.create(
        model=MODEL,
        messages=[
            {
                "role": "system",
                "content": (
                    "Classify this SupportOps ticket. Submit exactly one assessment using the required tool. "
                    "Use only ticket facts. Escalate policy exceptions, missing evidence, or unsupported actions."
                ),
            },
            {"role": "user", "content": str(case["text"])},
        ],
        tools=[
            {
                "type": "function",
                "function": {
                    "name": "submit_assessment",
                    "description": "Return the ticket decision for evaluation.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "decision": {"type": "string", "enum": ["answer", "escalate"]},
                            "tool": {"type": "string", "enum": ["lookup_invoice", "issue_refund", "search_kb"]},
                            "escalate": {"type": "boolean"},
                        },
                        "required": ["decision", "tool", "escalate"],
                        "additionalProperties": False,
                    },
                },
            }
        ],
        tool_choice={"type": "function", "function": {"name": "submit_assessment"}},
        temperature=0,
        max_tokens=MAX_COMPLETION_TOKENS,
    )


def _write_result(result: dict[str, object]) -> None:
    ARTIFACT.parent.mkdir(parents=True, exist_ok=True)
    ARTIFACT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def main(environ: dict[str, str] | None = None) -> int:
    output: dict[str, object] = {
        "command": "LLM_MODE=live python scripts/run_live_groq_eval.py",
        "provider": "groq",
        "requested_model": MODEL,
        "case_id": CASE_ID,
        "status": "INCOMPLETE",
        "started_at_utc": datetime.now(UTC).isoformat(),
        "retry_count": 0,
        "rotated_key_count": 0,
        "usage": "PENDING",
        "cost_usd": "PENDING",
    }
    try:
        values = load_root_env(environ)
        require_live_mode(values)
        keys = configured_keys(values)
        if not keys:
            raise RuntimeError("no Groq API key is configured")
        case = _load_case()
        preflight_client = _new_client(keys[0])
        catalog = preflight_client.models.list()
        verify_model_available(catalog)
        output["model_available"] = True

        # The user explicitly designated these credentials for the free plan. The public
        # developer-plan token price is nonzero; only the free-plan allowance is permitted.
        response, rotated = run_with_rotation(
            keys,
            _new_client,
            lambda client: _predict(client, case),
        )
        output["rotated_key_count"] = rotated
        output["retry_count"] = rotated
        choice = response.choices[0]
        prediction = parse_assessment(choice.message)
        checks = {
            "decision": prediction["decision"] == case["expected_decision"],
            "tool": prediction["tool"] == case["expected_tool"],
            "escalation": prediction["escalate"] == case["expected_escalate"],
        }
        expected = {
            "decision": case["expected_decision"],
            "tool": case["expected_tool"],
            "escalate": case["expected_escalate"],
        }
        usage = response.usage
        output.update(
            actual_model=getattr(response, "model", MODEL),
            prediction=prediction,
            expected=expected,
            checks=checks,
            metrics={name: int(value) for name, value in checks.items()},
            usage={
                "prompt_tokens": getattr(usage, "prompt_tokens", None),
                "completion_tokens": getattr(usage, "completion_tokens", None),
                "total_tokens": getattr(usage, "total_tokens", None),
            },
            status="PASS" if all(checks.values()) else "FAIL",
            cost_usd="PENDING",
        )
    except Exception as exc:
        # Never serialize provider messages: SDK errors may include request metadata.
        output["error"] = {
            "class": type(exc).__name__ if type(exc).__name__ in {"ValueError", "RuntimeError"} else "ProviderError",
            "detail": str(exc)[:120] if type(exc).__name__ in {"ValueError", "RuntimeError"} else "sanitized provider failure",
        }
    finally:
        output["finished_at_utc"] = datetime.now(UTC).isoformat()
        output["exit_code"] = 0 if output["status"] == "PASS" else 1
        _write_result(output)
        print(json.dumps(output, sort_keys=True))
    return int(output["exit_code"])


if __name__ == "__main__":
    raise SystemExit(main())
