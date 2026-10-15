"""Create explicit before/after cache and cost summaries."""

import json
from pathlib import Path
from typing import Any


def build_report(before: dict[str, Any] | None = None, after: dict[str, Any] | None = None) -> dict[str, Any]:
    if before is None or after is None:
        return {"status": "PENDING", "reason": "No comparable recorded runs were supplied", "before": "PENDING", "after": "PENDING", "delta": "PENDING"}
    keys = ("requests", "cache_hits", "tokens", "latency_ms", "cost_usd")
    delta = {}
    for key in keys:
        left, right = before.get(key), after.get(key)
        delta[key] = right - left if isinstance(left, (int, float)) and isinstance(right, (int, float)) else "PENDING"
    return {"status": "RECORDED_RUNS", "before": before, "after": after, "delta": delta}


def write_report(path: Path, before: dict[str, Any] | None = None, after: dict[str, Any] | None = None) -> dict[str, Any]:
    report = build_report(before, after)
    path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    return report


if __name__ == "__main__":
    print(json.dumps(build_report(), indent=2))
