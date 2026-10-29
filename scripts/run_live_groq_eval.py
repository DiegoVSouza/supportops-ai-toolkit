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
ARTIFACT = (
    ROOT
    / "artifacts"
    / "evidence"
    / (
        "phase-007-groq-live-"
        + datetime.now(UTC).strftime("%Y%m%dT%H%M%S%fZ")
        + ".json"
    )
)


class ProviderFailure(RuntimeError):
    def __init__(self, error_class, status, code=None):
        super().__init__(
            f"non-retryable provider failure: {error_class}, status={status}"
        )
        self.status = status
        self.code = (
            code
            if code
            in {
                "tool_use_failed",
                "json_validate_failed",
                "invalid_request_error",
                "model_not_found",
                "rate_limit_exceeded",
                "context_length_exceeded",
                "invalid_api_key",
            }
            else None
        )


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
    for name in (
        "GROQ_API_KEY_1",
        "GROQ_API_KEY_2",
        "GROQ_API_KEY_3",
        "GROQ_API_KEY_4",
    ):
        value = environ.get(name, "").strip()
        if value and value not in keys:
            keys.append(value)
    return keys


def require_live_mode(environ: dict[str, str]) -> None:
    if environ.get("LLM_MODE", "").strip().lower() != "live":
        raise RuntimeError("set LLM_MODE=live explicitly to enable Groq evaluation")


def verify_model_available(response: object) -> None:
    if not any(
        getattr(item, "id", None) == MODEL for item in getattr(response, "data", [])
    ):
        raise RuntimeError(
            "requested model is unavailable in the authenticated Groq catalog"
        )


def classify_error(exc: Exception) -> tuple[bool, str, int | None]:
    status = getattr(exc, "status_code", None)
    if status is None:
        response = getattr(exc, "response", None)
        status = getattr(response, "status_code", None)
    if isinstance(status, int):
        retryable = status == 429 or status in {408, 409, 500, 502, 503, 504}
        return retryable, "http_error", status
    name = type(exc).__name__
    if name in {
        "APIConnectionError",
        "APITimeoutError",
        "TimeoutError",
        "ConnectionError",
    }:
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
                body = getattr(exc, "body", None)
                detail = body.get("error", {}) if isinstance(body, dict) else {}
                code = detail.get("code") if isinstance(detail, dict) else None
                raise ProviderFailure(error_class, status, code) from None
            if index == len(keys) - 1:
                break
            headers = getattr(exc, "headers", None)
            delay = retry_delay(index, headers, jitter=jitter)
            if delay is None:
                raise RuntimeError(
                    "provider Retry-After exceeds the configured wait ceiling"
                ) from None
            sleep(delay)
    raise RuntimeError(
        "retryable failures exhausted after one configured key pass"
    ) from None


def parse_assessment(message: object) -> dict[str, object]:
    calls = (
        message.get("tool_calls")
        if isinstance(message, dict)
        else getattr(message, "tool_calls", None)
    ) or []
    if not calls:
        raise ValueError("missing assessment tool call")
    call = calls[0]
    function = (
        call.get("function")
        if isinstance(call, dict)
        else getattr(call, "function", None)
    )
    name = (
        function.get("name")
        if isinstance(function, dict)
        else getattr(function, "name", None)
    )
    arguments = (
        function.get("arguments")
        if isinstance(function, dict)
        else getattr(function, "arguments", None)
    )
    if name != "submit_assessment":
        raise ValueError("unexpected assessment tool")
    try:
        value = json.loads(arguments)
    except (TypeError, json.JSONDecodeError) as exc:
        raise ValueError("malformed assessment arguments") from exc
    if not isinstance(value, dict):
        raise ValueError("assessment must be an object")
    decision, tool, escalate = (
        value.get("decision"),
        value.get("tool"),
        value.get("escalate"),
    )
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
        raise RuntimeError(
            "official Groq SDK is unavailable; install the project's live extra"
        ) from exc
    return Groq(api_key=key, timeout=TIMEOUT_SECONDS, max_retries=0)


def _load_case() -> dict[str, object]:
    dataset = load_dataset(ROOT / "evals/datasets/v1/supportops.jsonl")
    case = next((item for item in dataset if item["id"] == CASE_ID), None)
    if case is None:
        raise RuntimeError(
            "selected evaluation case is missing from the versioned dataset"
        )
    return case


def _predict(client: object, case: dict[str, object]) -> object:
    return client.chat.completions.create(
        model=MODEL,
        messages=build_messages(case),
        tools=[
            {
                "type": "function",
                "function": {
                    "name": "submit_assessment",
                    "description": "Return the ticket decision for evaluation.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "decision": {
                                "type": "string",
                                "enum": ["answer", "escalate"],
                            },
                            "tool": {
                                "type": "string",
                                "enum": ["lookup_invoice", "issue_refund", "search_kb"],
                            },
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
        max_completion_tokens=MAX_COMPLETION_TOKENS,
        reasoning_effort="low",
    )


def build_messages(case: dict[str, object]) -> list[dict[str, str]]:
    return [
        {
            "role": "system",
            "content": (
                "Classify this SupportOps ticket and submit exactly one assessment using the required tool. "
                "Use only ticket facts. Escalate policy exceptions, missing evidence, or unsupported actions. "
                "Tool semantics: lookup_invoice is a read-only lookup to verify invoice identity, paid status, "
                "and balance; issue_refund is a downstream action and is appropriate only after the ticket "
                "provides a verified invoice and an allowed refund amount; search_kb is a read-only policy lookup. "
                "For this initial triage, when the ticket does not identify an invoice or verified balance, "
                "choose lookup_invoice even if it claims the invoice is paid or within policy. Never imply that "
                "choosing issue_refund itself authorizes or performs a refund. Return a concise answer grounded "
                "only in the ticket."
            ),
        },
        {"role": "user", "content": str(case["text"])},
    ]


def _write_result(result: dict[str, object]) -> None:
    ARTIFACT.parent.mkdir(parents=True, exist_ok=True)
    serialized = json.dumps(result, indent=2, sort_keys=True) + "\n"
    ARTIFACT.write_text(serialized, encoding="utf-8")
    ARTIFACT.with_suffix(".txt").write_text(
        "Command: LLM_MODE=live uv run --extra live python scripts/run_live_groq_eval.py\n"
        f"Exit code: {result.get('exit_code', 1)}\n"
        f"Sanitized result: {json.dumps(result, sort_keys=True)}\n",
        encoding="utf-8",
    )


def main(environ: dict[str, str] | None = None) -> int:
    # This historical runner lacks the shared accounting and uncertainty guards.
    print(
        json.dumps(
            {
                "status": "INCOMPLETE",
                "reason": "accounted_guard_required",
                "provider_accessed": False,
                "credentials_read": False,
            }
        )
    )
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
