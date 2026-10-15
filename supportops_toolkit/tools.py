"""Small JSON-schema subset and resilient local tool registry."""

from __future__ import annotations

import functools
import random
import threading
import time
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FutureTimeout
from dataclasses import dataclass
from typing import Any, Callable, Mapping


class ToolError(Exception):
    """A structured tool failure safe to return to a caller."""

    def __init__(self, code: str, message: str, *, retryable: bool = False) -> None:
        super().__init__(message)
        self.code = code
        self.retryable = retryable


def classify_error(error: BaseException) -> str:
    if isinstance(error, ToolError):
        return "retryable" if error.retryable else "fatal"
    if isinstance(error, (TimeoutError, FutureTimeout, ConnectionError)):
        return "retryable"
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

    def __call__(self, **kwargs: Any) -> Any:
        _validate(kwargs, self.schema_in)
        attempts = 0
        while True:
            attempts += 1
            executor = ThreadPoolExecutor(max_workers=1)
            future = executor.submit(self.handler, **kwargs)
            try:
                result = future.result(timeout=self.timeout_s)
            except FutureTimeout as exc:
                future.cancel()
                error: BaseException = ToolError("timeout", f"{self.name} exceeded {self.timeout_s}s", retryable=True)
                if attempts > self.retries:
                    raise error from exc
            except BaseException as exc:
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
