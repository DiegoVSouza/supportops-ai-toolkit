"""Code-first eval runner; fake outcomes are fixtures, not model measurements."""

from __future__ import annotations

import argparse
import json
import os
import re
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Callable


class RegressionError(AssertionError):
    pass


@dataclass(frozen=True)
class EvalReport:
    total: int
    decision_accuracy: float
    tool_call_accuracy: float
    groundedness: float
    escalation_accuracy: float
    failures: tuple[str, ...]

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


def load_dataset(dataset: Path) -> list[dict[str, Any]]:
    rows = []
    for line_number, line in enumerate(dataset.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        try:
            row = json.loads(line)
        except json.JSONDecodeError as exc:
            raise ValueError(f"invalid JSONL at {dataset}:{line_number}: {exc.msg}") from exc
        required = {"id", "text", "expected_decision", "expected_tool", "expected_escalate", "evidence"}
        if not required <= row.keys():
            raise ValueError(f"dataset row {line_number} missing {sorted(required - row.keys())}")
        rows.append(row)
    if not rows:
        raise ValueError("evaluation dataset is empty")
    if len({row["id"] for row in rows}) != len(rows):
        raise ValueError("evaluation case IDs must be unique")
    return rows


def run_evals(runner: Callable[[dict[str, Any]], dict[str, Any]], dataset: Path) -> EvalReport:
    cases = load_dataset(dataset)
    decision = tool_call = grounded = escalation = 0
    failures = []
    for case in cases:
        result = runner(case)
        checks = {
            "decision": result.get("decision") == case["expected_decision"],
            "tool": result.get("tool") == case["expected_tool"],
            "groundedness": is_grounded(result.get("answer", ""), case["evidence"]) if case.get("requires_evidence", True) else True,
            "escalation": bool(result.get("escalate")) == bool(case["expected_escalate"]),
        }
        decision += checks["decision"]
        tool_call += checks["tool"]
        grounded += checks["groundedness"]
        escalation += checks["escalation"]
        failed = [name for name, passed in checks.items() if not passed]
        if failed:
            failures.append(f"{case['id']}: {', '.join(failed)}")
    total = len(cases)
    return EvalReport(total, decision / total, tool_call / total, grounded / total, escalation / total, tuple(failures))


_STOP_WORDS = frozenset({"a", "an", "and", "are", "as", "at", "be", "by", "for", "from", "in", "is", "it", "of", "on", "or", "the", "to", "with"})


def is_grounded(answer: str, evidence: str, *, min_overlap: float = 0.6) -> bool:
    """Check whether most answer terms are present in supplied evidence."""
    if not 0 < min_overlap <= 1:
        raise ValueError("min_overlap must be in (0, 1]")
    answer_terms = set(re.findall(r"[a-z0-9]+", answer.lower())) - _STOP_WORDS
    evidence_terms = set(re.findall(r"[a-z0-9]+", evidence.lower())) - _STOP_WORDS
    return bool(answer_terms) and len(answer_terms & evidence_terms) / len(answer_terms) >= min_overlap


def validate_citations(citation_ids: list[str], supplied_sources: list[dict[str, Any]]) -> bool:
    """Check citation membership only; this does not verify claim entailment."""
    if not isinstance(citation_ids, list) or any(not isinstance(item, str) or not item for item in citation_ids):
        raise ValueError("citation_ids must be a list of non-empty strings")
    if len(citation_ids) != len(set(citation_ids)):
        raise ValueError("citation_ids must be unique")
    if not isinstance(supplied_sources, list):
        raise ValueError("supplied_sources must be a list")
    available = []
    for source in supplied_sources:
        if not isinstance(source, dict) or not isinstance(source.get("source_id"), str) or not source["source_id"]:
            raise ValueError("each supplied source must have a non-empty source_id")
        available.append(source["source_id"])
    if len(available) != len(set(available)):
        raise ValueError("supplied source IDs must be unique")
    return bool(citation_ids) and set(citation_ids) <= set(available)


def assert_regression(current: EvalReport, baseline: dict[str, float], max_drop: float = 0.05) -> None:
    if not 0 <= max_drop <= 1:
        raise ValueError("max_drop must be between 0 and 1")
    metrics = ("decision_accuracy", "tool_call_accuracy", "groundedness", "escalation_accuracy")
    drops = {metric: baseline[metric] - getattr(current, metric) for metric in metrics if baseline[metric] - getattr(current, metric) > max_drop + 1e-12}
    if drops:
        detail = ", ".join(f"{key}: drop={value:.3f}" for key, value in sorted(drops.items()))
        raise RegressionError(f"evaluation regression exceeds {max_drop:.3f}: {detail}")


def fake_runner(case: dict[str, Any]) -> dict[str, Any]:
    """A fixture adapter: returns deterministic canned labels in fake mode."""
    return {
        "decision": case["fake_decision"],
        "tool": case["fake_tool"],
        "answer": case["fake_answer"],
        "escalate": case["fake_escalate"],
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset", type=Path, default=Path("evals/datasets/v1/supportops.jsonl"))
    parser.add_argument("--baseline", type=Path, default=Path("evals/baseline/v1.json"))
    parser.add_argument("--max-drop", type=float, default=0.05)
    args = parser.parse_args()
    mode = os.getenv("LLM_MODE", "fake")
    if mode != "fake":
        raise SystemExit(f"LLM_MODE={mode!r} is unsupported by this local runner; use fake or provide a separately approved replay adapter")
    report = run_evals(fake_runner, args.dataset)
    baseline = json.loads(args.baseline.read_text(encoding="utf-8"))
    assert_regression(report, baseline, args.max_drop)
    print(json.dumps({"mode": mode, **report.as_dict(), "regression": "PASS", "quality_claim": "fixture-only; not a model measurement"}, indent=2))


if __name__ == "__main__":
    main()
