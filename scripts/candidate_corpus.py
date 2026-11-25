"""Separate offline-only development candidate; does not modify the spent campaign."""
from pathlib import Path
from typing import Any

from scripts.campaign_corpus import build_case, build_payload

PROMPT = Path(__file__).resolve().parents[1] / "agent/prompts/tool-selection-candidate-v1.md"
PROMPT_V3 = Path(__file__).resolve().parents[1] / "agent/prompts/tool-selection-candidate-v2.md"


def build_candidate_payload(case: dict[str, Any], model: str) -> dict[str, Any]:
    if case.get("split") != "development":
        raise ValueError("development split required")
    payload = build_payload(build_case(case), model)
    payload["messages"][0]["content"] = PROMPT.read_text(encoding="utf-8").strip()
    return payload


def build_v3_candidate_payload(case: dict[str, Any], model: str) -> dict[str, Any]:
    if case.get("split") != "development":
        raise ValueError("development split required")
    payload = build_payload(build_case(case), model)
    payload["messages"][0]["content"] = PROMPT_V3.read_text(encoding="utf-8").strip()
    return payload
