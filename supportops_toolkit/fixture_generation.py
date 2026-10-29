"""Fixture-only retrieval and single-attempt transport boundary."""

import json
import re
import sqlite3
from contextlib import closing
from pathlib import Path

from .fixture_retrieval import retrieve


class FixtureBlocked(RuntimeError):
    """A categorical refusal without private input or model output."""


def run(path: Path, request_id: str, tenant: str, query: str, documents: list[dict], transport) -> dict:
    if not isinstance(request_id, str) or not re.fullmatch(r"fixture-[A-Za-z0-9_-]{1,48}", request_id):
        raise FixtureBlocked("invalid_request")
    if getattr(transport, "provenance", None) != "fixture":
        raise FixtureBlocked("fixture_transport_required")
    evidence = retrieve(tenant, query, documents)
    if evidence["status"] != "evidence":
        return {"status": "refuse", "sources": []}
    payload = {"query": query, "sources": evidence["sources"]}
    if len(json.dumps(payload, ensure_ascii=False).encode("utf-8")) > 8192:
        raise FixtureBlocked("input_bound_exceeded")
    with closing(sqlite3.connect(path, timeout=5)) as db:
        db.execute("PRAGMA synchronous=FULL")
        db.execute("CREATE TABLE IF NOT EXISTS attempts (request_id TEXT PRIMARY KEY, status TEXT NOT NULL)")
        try:
            db.execute("BEGIN IMMEDIATE")
            if db.execute("SELECT 1 FROM attempts WHERE status='reserved' LIMIT 1").fetchone():
                raise FixtureBlocked("prior_uncertain_attempt")
            db.execute("INSERT INTO attempts VALUES (?, 'reserved')", (request_id,))
            db.commit()
        except sqlite3.IntegrityError:
            raise FixtureBlocked("already_reserved") from None
    try:
        response = transport.request({"request_id": request_id, "payload": payload})
    except Exception:
        raise FixtureBlocked("uncertain_attempt") from None
    if (not isinstance(response, dict) or response.get("status") != "ok"
            or not isinstance(response.get("receipt"), str)
            or not re.fullmatch(r"[0-9a-f]{32}", response["receipt"])):
        raise FixtureBlocked("missing_receipt")
    with closing(sqlite3.connect(path, timeout=5)) as db:
        db.execute("PRAGMA synchronous=FULL")
        db.execute("UPDATE attempts SET status='completed' WHERE request_id=? AND status='reserved'", (request_id,))
        db.commit()
    return {"status": "ok", "source_ids": [source["source_id"] for source in evidence["sources"]],
            "receipt": response["receipt"], "provenance": "fixture"}
