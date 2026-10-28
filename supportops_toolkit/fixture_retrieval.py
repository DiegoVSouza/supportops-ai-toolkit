"""Tenant-scoped retrieval of synthetic fixtures, without a model or connector."""

import re

from .guardrails import guard


def retrieve(tenant: str, query: str, documents: list[dict]) -> dict:
    if not isinstance(tenant, str) or not re.fullmatch(r"fixture-[A-Za-z0-9_-]{1,48}", tenant):
        raise ValueError("invalid synthetic tenant")
    if not isinstance(query, str) or not 1 <= len(query) <= 200 or not query.strip():
        raise ValueError("invalid query")
    if not isinstance(documents, list) or len(documents) > 100:
        raise ValueError("invalid fixture collection")
    seen = set()
    eligible = []
    for doc in documents:
        if (not isinstance(doc, dict) or set(doc) != {"tenant", "id", "text"}
                or not isinstance(doc["tenant"], str)
                or not re.fullmatch(r"fixture-[A-Za-z0-9_-]{1,48}", doc["tenant"])
                or not isinstance(doc["id"], str)
                or not re.fullmatch(r"[A-Za-z0-9_-]{1,64}", doc["id"])
                or not isinstance(doc["text"], str) or len(doc["text"]) > 4096):
            raise ValueError("invalid fixture document")
        identity = (doc["tenant"], doc["id"])
        if identity in seen:
            raise ValueError("duplicate fixture document")
        seen.add(identity)
        if doc["tenant"] == tenant:
            eligible.append(doc)
    terms = set(query.lower().split())
    matches = [(len(terms & set(doc["text"].lower().split())), doc) for doc in eligible]
    ranked = sorted((item for item in matches if item[0]), key=lambda item: (-item[0], item[1]["id"]))[:2]
    if not ranked or any(guard(doc["text"], role="support", source="retrieved").action != "allow" for _, doc in ranked):
        return {"status": "refuse", "sources": []}
    return {"status": "evidence", "sources": [
        {"source_id": "fixture:" + doc["id"], "text": doc["text"], "trust": "untrusted"}
        for _, doc in ranked
    ]}
