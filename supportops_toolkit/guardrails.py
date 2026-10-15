"""Deterministic authorization, injection screening, limits, and PII masking."""

from __future__ import annotations

import re
import time
import math
from dataclasses import dataclass, field


@dataclass(frozen=True)
class GuardVerdict:
    action: str
    reasons: tuple[str, ...] = ()
    sanitized_text: str | None = None


@dataclass
class ExecutionLimits:
    max_steps: int
    max_tokens: int
    max_seconds: float
    steps: int = 0
    tokens: int = 0
    started_at: float = field(default_factory=time.monotonic)

    def __post_init__(self) -> None:
        if (isinstance(self.max_steps, bool) or not isinstance(self.max_steps, int) or self.max_steps < 0
                or isinstance(self.max_tokens, bool) or not isinstance(self.max_tokens, int) or self.max_tokens < 0
                or isinstance(self.max_seconds, bool) or not isinstance(self.max_seconds, (int, float))
                or not math.isfinite(self.max_seconds) or self.max_seconds <= 0):
            raise ValueError("step/token limits must be non-negative and max_seconds positive")

    def remaining_seconds(self, *, now: float | None = None) -> float:
        elapsed = (time.monotonic() if now is None else now) - self.started_at
        remaining = self.max_seconds - elapsed
        if remaining <= 0:
            raise LimitExceeded("Execution limit exceeded: max_seconds")
        return remaining

    def consume(self, *, steps: int = 1, tokens: int = 0, now: float | None = None) -> None:
        if steps < 0 or tokens < 0:
            raise ValueError("consumption must be non-negative")
        proposed_steps, proposed_tokens = self.steps + steps, self.tokens + tokens
        exceeded = []
        if proposed_steps > self.max_steps:
            exceeded.append("max_steps")
        if proposed_tokens > self.max_tokens:
            exceeded.append("max_tokens")
        if (time.monotonic() if now is None else now) - self.started_at > self.max_seconds:
            exceeded.append("max_seconds")
        if exceeded:
            raise LimitExceeded("Execution limit exceeded: " + ", ".join(exceeded))
        self.steps, self.tokens = proposed_steps, proposed_tokens


class LimitExceeded(RuntimeError):
    pass


ROLE_TOOLS = {
    "support": frozenset({"lookup_invoice", "search_kb"}),
    "supervisor": frozenset({"lookup_invoice", "search_kb", "issue_refund"}),
    "auditor": frozenset({"lookup_invoice", "search_kb"}),
}


def authorize_tool(role: str, tool_name: str) -> None:
    if role not in ROLE_TOOLS:
        raise PermissionError("unknown role")
    if tool_name not in ROLE_TOOLS[role]:
        raise PermissionError(f"role {role!r} is not allowed to call {tool_name!r}")


_INJECTION_PATTERNS = (
    re.compile(r"\b(ignore|disregard|override|bypass)\b.{0,60}\b(previous|above|prior|system|developer|safety|policy|instructions?|rules?)\b", re.I),
    re.compile(r"\b(reveal|print|show|expose|dump|extract)\b.{0,50}\b(system prompt|hidden prompt|secrets?|credentials?|api keys?|passwords?|tokens?)\b", re.I),
    re.compile(r"\b(exfiltrat\w*|send|email|forward|upload|post)\b.{0,70}\b(secrets?|credentials?|customer data|account data|private data|api keys?|passwords?)\b", re.I),
    re.compile(r"\b(disable|turn off|remove)\b.{0,40}\b(redaction|guardrails?|security checks?)\b", re.I),
    re.compile(r"\b(act as|pretend to be)\b.{0,40}\b(admin|developer|system|supervisor)\b", re.I),
    re.compile(r"\b(prompt injection|indirect instruction|hidden instruction)\b", re.I),
    re.compile(r"\b(list|export|dump)\b.{0,45}\b(all customers|all cards|customer records|database)\b", re.I),
)

_EMAIL = re.compile(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", re.I)
_CARD = re.compile(r"\b(?:\d[ -]*?){13,19}\b")
_PHONE = re.compile(r"(?<!\w)(?:\+?\d[\d ().-]{8,}\d)(?!\w)")


def redact_pii(text: str) -> str:
    result = _CARD.sub("[REDACTED_CARD]", text)
    result = _EMAIL.sub("[REDACTED_EMAIL]", result)
    return _PHONE.sub("[REDACTED_PHONE]", result)


def classify_injection_fake(input_text: str) -> bool:
    """Local heuristic classifier used when no approved classifier is configured."""
    return any(pattern.search(input_text) for pattern in _INJECTION_PATTERNS)


def guard(input_text: str, *, role: str) -> GuardVerdict:
    reasons = []
    if role not in ROLE_TOOLS:
        return GuardVerdict("block", ("unknown_role",))
    if classify_injection_fake(input_text):
        return GuardVerdict("block", ("prompt_injection_heuristic",))
    sanitized = redact_pii(input_text)
    if sanitized != input_text:
        reasons.append("pii_redacted")
        return GuardVerdict("redact", tuple(reasons), sanitized)
    return GuardVerdict("allow")
