"""Small JSON-schema subset and resilient local tool registry."""

from __future__ import annotations

import math
import random
import threading
import time
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FutureTimeout
from dataclasses import dataclass
from typing import Any, Callable, Mapping

from supportops_toolkit.guardrails import ExecutionLimits, LimitExceeded


class ToolError(Exception):
    """A structured tool failure safe to return to a caller."""

    def __init__(self, code: str, message: str, *, retryable: bool = False) -> None:
        super().__init__(message)
        self.code = code
        self.retryable = retryable


_SCHEMA_KEYS = frozenset({"type", "enum", "required", "properties", "additionalProperties", "minLength", "maxLength", "minimum", "maximum"})
_SCHEMA_TYPES = frozenset({"object", "array", "string", "integer", "number", "boolean", "null"})


def _is_finite_number(value: Any) -> bool:
    return not isinstance(value, bool) and (isinstance(value, int) or isinstance(value, float) and math.isfinite(value))


def _validate_schema_definition(schema: Any, path: str = "$schema") -> None:
    if schema is None or (callable(schema) and not isinstance(schema, Mapping)):
        return
    if not isinstance(schema, Mapping):
        raise TypeError("schema must be a mapping, callable, or None")
    unsupported = set(schema) - _SCHEMA_KEYS
    if unsupported:
        raise ValueError(f"unsupported schema keywords at {path}: {sorted(unsupported)}")
    expected = schema.get("type")
    if expected is not None and expected not in _SCHEMA_TYPES:
        raise ValueError(f"unsupported schema type at {path}: {expected!r}")
    if "enum" in schema and not isinstance(schema["enum"], (list, tuple)):
        raise TypeError(f"enum at {path} must be a list or tuple")
    required = schema.get("required", [])
    if not isinstance(required, (list, tuple)) or any(not isinstance(item, str) for item in required):
        raise TypeError(f"required at {path} must contain only strings")
    properties = schema.get("properties", {})
    if not isinstance(properties, Mapping):
        raise TypeError(f"properties at {path} must be a mapping")
    if "additionalProperties" in schema and not isinstance(schema["additionalProperties"], bool):
        raise TypeError(f"additionalProperties at {path} must be a boolean")
    for key in ("minLength", "maxLength"):
        if key in schema and (not isinstance(schema[key], int) or isinstance(schema[key], bool) or schema[key] < 0):
            raise ValueError(f"{key} at {path} must be a non-negative integer")
    for key in ("minimum", "maximum"):
        if key in schema and not _is_finite_number(schema[key]):
            raise ValueError(f"{key} at {path} must be a finite number")
    if schema.get("minLength", 0) > schema.get("maxLength", float("inf")):
        raise ValueError(f"minLength exceeds maxLength at {path}")
    if schema.get("minimum", float("-inf")) > schema.get("maximum", float("inf")):
        raise ValueError(f"minimum exceeds maximum at {path}")
    for key, child in properties.items():
        _validate_schema_definition(child, f"{path}.properties.{key}")


def classify_error(error: BaseException) -> str:
    if isinstance(error, ToolError):
        return "retryable" if error.retryable else "fatal"
    # Generic transport/timeouts are outcome-ambiguous for writes. Retrying is
    # opt-in through ToolError(retryable=True) after the adapter establishes safety.
    return "fatal"


def _validate(value: Any, schema: Any, path: str = "$") -> None:
    if schema is None:
        return
    if callable(schema) and not isinstance(schema, Mapping):
        result = schema(value)
        if result is False:
            raise ToolError("invalid_schema", f"{path} failed custom validation")
        return
    if not isinstance(schema, Mapping):
        raise TypeError("schema must be a mapping, callable, or None")
    types = {
        "object": dict,
        "array": list,
        "string": str,
        "integer": int,
        "number": (int, float),
        "boolean": bool,
        "null": type(None),
    }
    expected = schema.get("type")
    if expected is not None:
        pytype = types.get(expected)
        if pytype is None or not isinstance(value, pytype) or (expected == "integer" and isinstance(value, bool)):
            raise ToolError("invalid_input" if path == "$" else "invalid_output", f"{path} must be {expected}")
        if expected == "number" and not _is_finite_number(value):
            raise ToolError("invalid_input" if path == "$" else "invalid_output", f"{path} must be a finite number")
    if "enum" in schema and value not in schema["enum"]:
        raise ToolError("invalid_input" if path == "$" else "invalid_output", f"{path} is not an allowed value")
    if isinstance(value, dict):
        for key in schema.get("required", []):
            if key not in value:
                raise ToolError("invalid_input" if path == "$" else "invalid_output", f"{path}.{key} is required")
        props = schema.get("properties", {})
        if schema.get("additionalProperties") is False:
            unknown = set(value) - set(props)
            if unknown:
                raise ToolError("invalid_input" if path == "$" else "invalid_output", f"{path} has unknown fields: {sorted(unknown)}")
        for key, child in props.items():
            if key in value:
                _validate(value[key], child, f"{path}.{key}")
    if isinstance(value, str):
        if len(value) < schema.get("minLength", 0) or len(value) > schema.get("maxLength", float("inf")):
            raise ToolError("invalid_input" if path == "$" else "invalid_output", f"{path} length is out of bounds")
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        if value < schema.get("minimum", float("-inf")) or value > schema.get("maximum", float("inf")):
            raise ToolError("invalid_input" if path == "$" else "invalid_output", f"{path} is out of bounds")


@dataclass(frozen=True)
class ToolSpec:
    name: str
    handler: Callable[..., Any]
    schema_in: Any
    schema_out: Any
    timeout_s: float
    retries: int
    base_delay_s: float = 0.01

    def __call__(self, *, execution_limits: ExecutionLimits | None = None, **kwargs: Any) -> Any:
        timeout_s = self.timeout_s
        if execution_limits is not None:
            execution_limits.consume(steps=1)
            timeout_s = min(timeout_s, execution_limits.remaining_seconds())
        _validate(kwargs, self.schema_in)
        attempts = 0
        while True:
            attempts += 1
            executor = ThreadPoolExecutor(max_workers=1)
            future = executor.submit(self.handler, **kwargs)
            try:
                result = future.result(timeout=timeout_s)
            except FutureTimeout as exc:
                future.cancel()
                if execution_limits is not None and timeout_s < self.timeout_s:
                    raise LimitExceeded("Execution limit exceeded: max_seconds") from exc
                # The handler may still be running after this thread times out. Its
                # side effect is indeterminate, so retrying can duplicate it.
                raise ToolError("timeout", f"{self.name} exceeded {timeout_s}s; outcome is indeterminate", retryable=False) from exc
            except Exception as exc:
                error = exc
                if classify_error(error) != "retryable" or attempts > self.retries:
                    if isinstance(error, ToolError):
                        raise
                    raise ToolError("tool_failed", str(error), retryable=False) from exc
            else:
                _validate(result, self.schema_out, "$.result")
                return result
            finally:
                executor.shutdown(wait=False, cancel_futures=True)
            delay = self.base_delay_s * (2 ** (attempts - 1))
            time.sleep(delay + random.uniform(0, delay * 0.1))


_REGISTRY: dict[str, ToolSpec] = {}
_LOCK = threading.Lock()


def tool(*, schema_in: Any, schema_out: Any, timeout_s: float = 5.0, retries: int = 0, base_delay_s: float = 0.01) -> Callable[[Callable[..., Any]], ToolSpec]:
    if timeout_s <= 0 or retries < 0 or base_delay_s < 0:
        raise ValueError("timeout_s must be positive and retries/base_delay_s non-negative")
    _validate_schema_definition(schema_in, "$input")
    _validate_schema_definition(schema_out, "$output")

    def register(handler: Callable[..., Any]) -> ToolSpec:
        spec = ToolSpec(handler.__name__, handler, schema_in, schema_out, timeout_s, retries, base_delay_s)
        with _LOCK:
            if spec.name in _REGISTRY:
                raise ValueError(f"tool already registered: {spec.name}")
            _REGISTRY[spec.name] = spec
        return spec

    return register


def get_tool(name: str) -> ToolSpec:
    try:
        return _REGISTRY[name]
    except KeyError as exc:
        raise ToolError("unknown_tool", f"Tool not registered: {name}") from exc


def list_tools() -> tuple[str, ...]:
    return tuple(sorted(_REGISTRY))
