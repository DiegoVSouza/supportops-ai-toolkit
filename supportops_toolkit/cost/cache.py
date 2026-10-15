"""Bounded in-memory exact and lexical-similarity response caches."""

from __future__ import annotations

import hashlib
import json
import re
from collections import OrderedDict
from dataclasses import dataclass
from typing import Any


def _stable_key(value: Any) -> str:
    payload = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


class ExactCache:
    def __init__(self, max_entries: int = 256) -> None:
        if max_entries < 1:
            raise ValueError("max_entries must be >= 1")
        self.max_entries = max_entries
        self._items: OrderedDict[str, Any] = OrderedDict()
        self.hits = self.misses = 0

    def get(self, key: Any) -> Any | None:
        stable = _stable_key(key)
        if stable not in self._items:
            self.misses += 1
            return None
        self.hits += 1
        self._items.move_to_end(stable)
        return self._items[stable]

    def put(self, key: Any, value: Any) -> None:
        stable = _stable_key(key)
        self._items[stable] = value
        self._items.move_to_end(stable)
        while len(self._items) > self.max_entries:
            self._items.popitem(last=False)


def _terms(text: str) -> frozenset[str]:
    return frozenset(re.findall(r"[a-z0-9]+", text.lower()))


@dataclass
class _SemanticEntry:
    query_terms: frozenset[str]
    response: Any
    namespace: str


class SemanticCache:
    """Lexical Jaccard cache; intentionally not an embedding or truth cache."""

    def __init__(self, threshold: float = 0.9, max_entries: int = 128) -> None:
        if not 0 < threshold <= 1 or max_entries < 1:
            raise ValueError("threshold must be in (0, 1] and max_entries >= 1")
        self.threshold = threshold
        self.max_entries = max_entries
        self._entries: list[_SemanticEntry] = []
        self.hits = self.misses = 0

    def get(self, query: str, *, namespace: str = "default") -> Any | None:
        terms = _terms(query)
        best: tuple[float, _SemanticEntry] | None = None
        for entry in self._entries:
            if entry.namespace != namespace:
                continue
            union = terms | entry.query_terms
            score = len(terms & entry.query_terms) / len(union) if union else 1.0
            if best is None or score > best[0]:
                best = (score, entry)
        if best is not None and best[0] >= self.threshold:
            self.hits += 1
            return best[1].response
        self.misses += 1
        return None

    def put(self, query: str, response: Any, *, namespace: str = "default") -> None:
        self._entries.append(_SemanticEntry(_terms(query), response, namespace))
        self._entries = self._entries[-self.max_entries:]
