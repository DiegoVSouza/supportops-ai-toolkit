"""Deterministic cost-tier routing and token budget enforcement."""

from dataclasses import dataclass


@dataclass(frozen=True)
class TaskProfile:
    complexity: int = 1
    risk: int = 1
    require_strong: bool = False


class ModelRouter:
    def __init__(self, cheap: str = "model-cheap", expensive: str = "model-strong", *, complexity_threshold: int = 4, risk_threshold: int = 4) -> None:
        if not cheap or not expensive or complexity_threshold < 1 or risk_threshold < 1:
            raise ValueError("model names and positive thresholds are required")
        self.cheap = cheap
        self.expensive = expensive
        self.complexity_threshold = complexity_threshold
        self.risk_threshold = risk_threshold

    def pick(self, task: TaskProfile) -> str:
        if not 1 <= task.complexity <= 5 or not 1 <= task.risk <= 5:
            raise ValueError("complexity and risk must be from 1 to 5")
        if task.require_strong or task.complexity >= self.complexity_threshold or task.risk >= self.risk_threshold:
            return self.expensive
        return self.cheap


@dataclass
class TokenBudget:
    max_tokens: int
    used: int = 0

    def __post_init__(self) -> None:
        if self.max_tokens < 0:
            raise ValueError("max_tokens must be non-negative")

    @property
    def remaining(self) -> int:
        return self.max_tokens - self.used

    def consume(self, tokens: int) -> None:
        if tokens < 0:
            raise ValueError("tokens must be non-negative")
        if self.used + tokens > self.max_tokens:
            raise ValueError("token budget exceeded")
        self.used += tokens
