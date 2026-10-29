import sqlite3
import tempfile
import unittest
from contextlib import closing
from pathlib import Path

from supportops_toolkit.accounted_generation import MODEL, OperationBlocked, run


class Session:
    provenance = "fixture"

    def __init__(self):
        self.calls = []
        self.result = {"status": "ok", "model": MODEL, "attempt_id": "a" * 32,
                       "usage": {"input_tokens": 100, "output_tokens": 20}, "content": "private"}

    def preview(self, envelope):
        self.calls.append(("preview", envelope))

    def complete(self, envelope):
        self.calls.append(("complete", envelope))
        if isinstance(self.result, Exception):
            raise self.result
        return self.result


class ProtocolTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.path = Path(self.tmp.name) / "operation.sqlite"
        self.session = Session()
        self.docs = [{"tenant": "fixture-a", "id": "one", "text": "invoice status"},
                     {"tenant": "fixture-b", "id": "secret", "text": "invoice private"}]

    def call(self, identity="fixture-one", query="invoice"):
        return run(self.path, identity, "fixture-a", query, self.docs, self.session)

    def test_envelope_is_scoped_and_reservation_precedes_dispatch(self):
        preview = self.session.preview
        def check(envelope):
            with closing(sqlite3.connect(self.path)) as db:
                self.assertEqual(db.execute("SELECT status FROM operations").fetchone()[0], "reserved")
            preview(envelope)
        self.session.preview = check
        result = self.call()
        self.assertNotIn("private", str(result))
        self.assertNotIn("secret", str(self.session.calls))
        self.assertEqual([row[0] for row in self.session.calls], ["preview", "complete"])
        with self.assertRaisesRegex(OperationBlocked, "already_reserved"):
            self.call()

    def test_failure_survives_restart_and_new_identity(self):
        self.session.result = TimeoutError("private")
        with self.assertRaisesRegex(OperationBlocked, "uncertain_attempt"):
            self.call()
        self.session = Session()
        with self.assertRaisesRegex(OperationBlocked, "prior_work"):
            self.call("fixture-two")
        self.assertEqual(self.session.calls, [])

    def test_invalid_usage_remains_reserved(self):
        self.session.result["usage"]["input_tokens"] = True
        with self.assertRaisesRegex(OperationBlocked, "invalid_accounted"):
            self.call()
        with self.assertRaisesRegex(OperationBlocked, "prior_work"):
            self.call("fixture-two")

    def test_no_match_and_live_session_never_dispatch(self):
        self.assertEqual(self.call(query="absent")["status"], "refuse")
        self.assertFalse(self.path.exists())
        self.session.provenance = "live"
        with self.assertRaisesRegex(OperationBlocked, "fixture_session"):
            self.call()

    def test_finite_cap_and_distinct_receipts(self):
        for index in range(4):
            self.session.result["attempt_id"] = str(index) * 32
            self.call("fixture-" + str(index))
        with self.assertRaisesRegex(OperationBlocked, "allocation_exhausted"):
            self.call("fixture-five")

    def test_duplicate_receipt_stops_following_work(self):
        self.call()
        with self.assertRaisesRegex(OperationBlocked, "duplicate_receipt"):
            self.call("fixture-two")
        with self.assertRaisesRegex(OperationBlocked, "prior_work"):
            self.call("fixture-three")
