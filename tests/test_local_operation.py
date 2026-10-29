import json
import os
import sqlite3
import subprocess
import tempfile
import unittest
from contextlib import closing
from pathlib import Path
from unittest.mock import patch

from scripts.local_operation import CASES, DOCS, MANIFEST, QUERY, LazySession, execute, fingerprint, validate
from supportops_toolkit.accounted_generation import OperationBlocked, _run


class LocalOperationTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)

    def test_default_fake_mode_stops_before_manifest_or_credentials(self):
        with patch.dict(os.environ, {"LLM_MODE": "fake"}), patch("scripts.local_operation.validate") as check:
            with self.assertRaisesRegex(OperationBlocked, "explicit_synthetic"):
                execute(CASES[0], project=self.root)
            check.assert_not_called()

    def test_reservation_precedes_startup_and_uncertainty_stops_new_id(self):
        path = self.root / "op.sqlite"
        def factory():
            with closing(sqlite3.connect(path)) as db:
                self.assertEqual(db.execute("SELECT status FROM operations").fetchone()[0], "reserved")
            raise TimeoutError("private")
        session = LazySession(factory)
        with self.assertRaisesRegex(OperationBlocked, "uncertain_attempt"):
            _run(path, CASES[0], "fixture-local", QUERY, DOCS, session, campaign="local-operation-v1")
        with self.assertRaisesRegex(OperationBlocked, "prior_work"):
            _run(path, CASES[1], "fixture-local", QUERY, DOCS, session, campaign="local-operation-v1")

    def test_manifest_binds_actual_committed_source(self):
        def git(*args):
            return subprocess.run(["git", *args], cwd=self.root, capture_output=True, text=True, check=True).stdout.strip()
        (self.root / "evals").mkdir()
        (self.root / "pyproject.toml").write_text("fixture")
        (self.root / "evals/live-execution.json").write_text(json.dumps({"execution_enabled": True}))
        git("init", "-q")
        git("config", "user.email", "fixture@example.invalid")
        git("config", "user.name", "Fixture")
        git("add", ".")
        git("commit", "-qm", "test: freeze fixture")
        manifest = {"project": "p02", "campaign_id": "local-operation-v1", "case_ids": CASES,
                    "paid_usd": 0, "candidate": git("rev-parse", "HEAD"), "source_fingerprint": fingerprint(self.root)}
        target = self.root / MANIFEST
        target.parent.mkdir(parents=True)
        target.write_text(json.dumps(manifest))
        self.assertEqual(validate(self.root), manifest)
        (self.root / "pyproject.toml").write_text("changed")
        with self.assertRaisesRegex(OperationBlocked, "source_provenance"):
            validate(self.root)

    def test_missing_manifest_is_categorical(self):
        with self.assertRaisesRegex(OperationBlocked, "manifest_missing"):
            validate(self.root)
