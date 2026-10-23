"""Run the ten-case P02 dataset against one verified zero-priced OpenRouter model."""

from __future__ import annotations

import json
import os
import re
import sys
import time
from datetime import UTC, datetime
from decimal import Decimal, InvalidOperation
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
LAB_ROOT = ROOT.parents[1]
sys.path.insert(0, str(ROOT))

from supportops_toolkit.evals.runner import load_dataset

MODEL = "cohere/north-mini-code:free"
MODELS_URL = "https://openrouter.ai/api/v1/models"
CHAT_URL = "https://openrouter.ai/api/v1/chat/completions"
MAX_BUDGET_USD = Decimal("0.05")
MAX_CASES = 10


def load_root_env() -> None:
    path = LAB_ROOT / ".env"
    if not path.is_file():
        raise RuntimeError("lab-root .env is missing")
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        name, value = line.split("=", 1)
        name, value = name.strip(), value.strip().strip('"').strip("'")
        if name and value and name not in os.environ:
            os.environ[name] = value


def verify_zero_price_model(api_key: str) -> dict[str, object]:
    request = Request(MODELS_URL, headers={"Authorization": f"Bearer {api_key}"})
    try:
        with urlopen(request, timeout=15) as response:
            body = json.loads(response.read())
    except HTTPError as exc:
        raise RuntimeError(f"OpenRouter model-list request returned HTTP {exc.code}") from exc
    except (TimeoutError, URLError, OSError) as exc:
        raise RuntimeError(f"OpenRouter model-list request failed: {type(exc).__name__}") from exc
    entry = next(
        (item for item in body.get("data", []) if isinstance(item, dict) and item.get("id") == MODEL),
        None,
    )
    if entry is None:
        raise RuntimeError(f"{MODEL} is absent from the authenticated model catalog")
    try:
        prompt_price = Decimal(str(entry["pricing"]["prompt"]))
        completion_price = Decimal(str(entry["pricing"]["completion"]))
    except (KeyError, InvalidOperation, TypeError) as exc:
        raise RuntimeError("model catalog did not provide verifiable token prices") from exc
    if prompt_price != 0 or completion_price != 0:
        raise RuntimeError("free model price is nonzero; refusing to send evaluation prompts")
    return entry


def parse_model_reply(content: str) -> dict[str, object]:
    match = re.search(r"\{.*\}", content, flags=re.DOTALL)
    if not match:
        raise ValueError("model response did not contain a JSON object")
    result = json.loads(match.group())
    if not isinstance(result, dict):
        raise ValueError("model response JSON must be an object")
    if result.get("decision") not in {"answer", "escalate"}:
        raise ValueError("model response has an invalid decision")
    if result.get("tool") not in {"lookup_invoice", "issue_refund", "search_kb"}:
        raise ValueError("model response has an invalid tool")
    if not isinstance(result.get("escalate"), bool) or not isinstance(result.get("answer"), str):
        raise ValueError("model response must include boolean escalate and string answer")
    return result


def parse_tool_arguments(message: dict[str, object]) -> dict[str, object]:
    calls = message.get("tool_calls", [])
    if not isinstance(calls, list) or not calls:
        raise ValueError("model response did not include the required assessment tool call")
    function = calls[0].get("function", {}) if isinstance(calls[0], dict) else {}
    arguments = function.get("arguments") if isinstance(function, dict) else None
    if not isinstance(arguments, str):
        raise ValueError("assessment tool arguments must be JSON text")
    return parse_model_reply(arguments)


def evaluate_case(api_key: str, case: dict[str, object]) -> tuple[dict[str, object], dict[str, int], int]:
    messages = [
        {
            "role": "system",
            "content": (
                "Classify the support ticket. Choose exactly one tool: lookup_invoice, issue_refund, "
                "or search_kb. Escalate policy exceptions, missing records, unsupported promises, "
                "or missing evidence. Submit your assessment with the provided function. "
                "Do not invent facts; use only the ticket text."
            ),
        },
        {"role": "user", "content": str(case["text"])},
    ]
    payload = json.dumps(
        {
            "model": MODEL,
            "messages": messages,
            "temperature": 0,
            "max_tokens": 2048,
            "reasoning_effort": "none",
            "reasoning": {"effort": "none", "exclude": True},
            "tools": [
                {
                    "type": "function",
                    "function": {
                        "name": "submit_assessment",
                        "description": "Return the ticket decision for evaluation.",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "decision": {"type": "string", "enum": ["answer", "escalate"]},
                                "tool": {
                                    "type": "string",
                                    "enum": ["lookup_invoice", "issue_refund", "search_kb"],
                                },
                                "answer": {"type": "string"},
                                "escalate": {"type": "boolean"},
                            },
                            "required": ["decision", "tool", "answer", "escalate"],
                            "additionalProperties": False,
                        },
                    },
                }
            ],
            "tool_choice": {
                "type": "function",
                "function": {"name": "submit_assessment"},
            },
        }
    ).encode("utf-8")
    request = Request(
        CHAT_URL,
        data=payload,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://openrouter.ai/",
            "X-Title": "P02 Free Model Evaluation",
        },
        method="POST",
    )
    started = time.perf_counter()
    try:
        with urlopen(request, timeout=25) as response:
            body = json.loads(response.read())
    except HTTPError as exc:
        raise RuntimeError(f"model request for {case['id']} returned HTTP {exc.code}") from exc
    except (TimeoutError, URLError, OSError) as exc:
        raise RuntimeError(f"model request for {case['id']} failed: {type(exc).__name__}") from exc
    latency_ms = round((time.perf_counter() - started) * 1000)
    try:
        message = body["choices"][0]["message"]
        usage = body.get("usage", {})
        prediction = parse_tool_arguments(message)
    except (KeyError, IndexError, TypeError, ValueError, json.JSONDecodeError) as exc:
        choices = body.get("choices", [])
        finish_reason = choices[0].get("finish_reason") if choices and isinstance(choices[0], dict) else None
        message_fields = sorted(message) if "message" in locals() and isinstance(message, dict) else []
        content_type = type(message.get("content")).__name__ if "message" in locals() else "missing"
        raise RuntimeError(
            f"model response for {case['id']} was malformed: {type(exc).__name__}: {str(exc)[:80]}; "
            f"content_type={content_type}, finish_reason={finish_reason}, message_fields={message_fields}"
        ) from exc
    checks = {
        "decision": prediction["decision"] == case["expected_decision"],
        "tool": prediction["tool"] == case["expected_tool"],
        "escalation": prediction["escalate"] == case["expected_escalate"],
    }
    row = {
        "id": case["id"],
        "prediction": prediction,
        "expected": {
            "decision": case["expected_decision"],
            "tool": case["expected_tool"],
            "escalate": case["expected_escalate"],
        },
        "checks": checks,
        "latency_ms": latency_ms,
    }
    token_use = {
        "prompt_tokens": int(usage.get("prompt_tokens", 0)),
        "completion_tokens": int(usage.get("completion_tokens", 0)),
    }
    return row, token_use, latency_ms


def write_evidence(result: dict[str, object]) -> None:
    evidence = ROOT / "artifacts" / "evidence" / "live-free-model-eval.json"
    evidence.parent.mkdir(parents=True, exist_ok=True)
    evidence.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def main() -> int:
    result: dict[str, object] = {
        "command": "python scripts/run_live_free_eval.py",
        "provider": "openrouter",
        "model": MODEL,
        "budget_cap_usd": str(MAX_BUDGET_USD),
        "status": "INCOMPLETE",
        "exit_code": 1,
        "started_at_utc": datetime.now(UTC).isoformat(),
        "groundedness": "NOT_EVALUATED: the synthetic dataset has no independent retrieval context",
        "cases": [],
    }
    exit_code = 1
    try:
        load_root_env()
        api_key = os.getenv("OPENROUTER_API_KEY", "").strip()
        if not api_key:
            raise RuntimeError("OPENROUTER_API_KEY is missing")
        catalog_entry = verify_zero_price_model(api_key)
        result["catalog_price"] = {
            "prompt": catalog_entry["pricing"]["prompt"],
            "completion": catalog_entry["pricing"]["completion"],
        }
        dataset = load_dataset(ROOT / "evals/datasets/v1/supportops.jsonl")
        if len(dataset) != MAX_CASES:
            raise RuntimeError(f"expected exactly {MAX_CASES} evaluation cases")
        token_total = {"prompt_tokens": 0, "completion_tokens": 0}
        latency_total = 0
        cases = []
        for case in dataset:
            try:
                row, token_use, latency = evaluate_case(api_key, case)
            except RuntimeError as exc:
                error = str(exc)
                cases.append({"id": case["id"], "status": "ERROR", "error": error[:180]})
                result["cases"] = cases
                result["completed_cases"] = len(cases)
                write_evidence(result)
                if "HTTP 429" in error:
                    raise
                continue
            row["status"] = "PASS"
            cases.append(row)
            for name, count in token_use.items():
                token_total[name] += count
            latency_total += latency
            result["cases"] = cases
            result["usage"] = token_total
            result["completed_cases"] = len(cases)
            write_evidence(result)
        valid_cases = [case for case in cases if case.get("status") == "PASS"]
        total = len(valid_cases)
        if not total:
            raise RuntimeError("no valid model assessments were returned")
        complete = total == MAX_CASES
        result.update(
            status="PASS" if complete else "INCOMPLETE",
            exit_code=0 if complete else 1,
            completed_cases=len(cases),
            valid_case_count=total,
            failed_case_count=MAX_CASES - total,
            usage=token_total,
            total_latency_ms=latency_total,
            average_latency_ms=round(latency_total / total),
            metrics={
                metric: sum(bool(case["checks"][metric]) for case in valid_cases) / total
                for metric in ("decision", "tool", "escalation")
            },
            estimated_cost_usd="0",
        )
        exit_code = 0 if complete else 1
    except (RuntimeError, ValueError, OSError, HTTPError, URLError, json.JSONDecodeError) as exc:
        result["error"] = f"{type(exc).__name__}: {str(exc)[:180]}"
    finally:
        result["finished_at_utc"] = datetime.now(UTC).isoformat()
        result["exit_code"] = exit_code
        write_evidence(result)
        print(json.dumps(result, sort_keys=True))
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
