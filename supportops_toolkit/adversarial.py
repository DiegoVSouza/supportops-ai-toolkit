"""Run the versioned adversarial guardrail suite and expose every missed case."""

import json
import argparse
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .guardrails import authorize_tool, guard

REFUND_LIMIT = 100.0


@dataclass(frozen=True)
class AdversarialReport:
    total: int
    blocked: int
    block_rate: float
    misses: tuple[str, ...]


def run_adversarial(dataset: Path) -> AdversarialReport:
    rows = [json.loads(line) for line in dataset.read_text(encoding="utf-8").splitlines() if line.strip()]
    if len(rows) < 30:
        raise ValueError("adversarial suite must contain at least 30 cases")
    if len({row.get("id") for row in rows}) != len(rows):
        raise ValueError("adversarial case IDs must be unique")
    blocked = 0
    misses = []
    for row in rows:
        verdict = guard(row["text"], role=row["role"])
        denied = verdict.action == "block"
        try:
            authorize_tool(row["role"], row["tool"])
        except PermissionError:
            denied = True
        if row.get("tool") == "issue_refund" and row.get("amount", 0) > REFUND_LIMIT:
            denied = True
        if denied:
            blocked += 1
        else:
            misses.append(row["id"])
    return AdversarialReport(len(rows), blocked, blocked / len(rows), tuple(misses))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset", type=Path, default=Path("guardrails/adversarial.jsonl"))
    args = parser.parse_args()
    report = run_adversarial(args.dataset)
    print(json.dumps({"total": report.total, "blocked": report.blocked, "block_rate": report.block_rate, "misses": report.misses}, indent=2))
    raise SystemExit(bool(report.misses))
