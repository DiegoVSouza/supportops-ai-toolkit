import json
import io
import os
import subprocess
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch

from scripts import campaign_execution as ex
from scripts.campaign_corpus import build_case
from scripts import run_live_campaign as cli

ROOT = Path(__file__).resolve().parents[1]
CASE = next(row for line in (ROOT / "evals/datasets/live-v1/cases.jsonl").read_text(encoding="utf-8").splitlines() if (row := json.loads(line))["split"] == "development")


class CampaignCandidateTests(unittest.TestCase):
    def tearDown(self):
        ex.use_campaign("p02-dev-v1")

    def test_candidate_prompt_is_part_of_frozen_source_set(self):
        self.assertIn("agent/prompts/tool-selection-candidate-v1.md", ex.source_paths(ROOT))
        self.assertIn("agent/prompts/tool-selection-candidate-v2.md", ex.source_paths(ROOT))

    def test_v3_candidate_requires_versioned_prompt_source(self):
        self.assertIn("agent/prompts/tool-selection-candidate-v2.md", ex.source_paths(ROOT))
        ex.use_campaign("p02-dev-v3")

    def test_new_campaign_uses_candidate_and_old_campaign_keeps_original_prompt(self):
        class Session:
            def preview(self, envelope):
                self.envelope = envelope

            def complete(self, envelope):
                return {"status": "ok", "usage": {"input_tokens": 1, "output_tokens": 1}, "content": "{}"}

        session = Session()
        ex.use_campaign("p02-dev-v2")
        ex.call_provider(CASE, build_case(CASE), session)
        self.assertEqual(session.envelope["campaign_id"], "p02-dev-v2")
        self.assertIn("does not execute", session.envelope["payload"]["messages"][0]["content"])
        ex.use_campaign("p02-dev-v1")
        ex.call_provider(CASE, build_case(CASE), session)
        self.assertNotIn("does not execute", session.envelope["payload"]["messages"][0]["content"])

    def test_v3_uses_its_prompt_and_binds_its_own_root_authorization(self):
        class Session:
            def preview(self, envelope):
                self.envelope = envelope

            def complete(self, envelope):
                return {"status": "ok", "usage": {"input_tokens": 1, "output_tokens": 1}, "content": "{}"}

        session = Session()
        ex.use_campaign("p02-dev-v3")
        ex.call_provider(CASE, build_case(CASE), session)
        content = session.envelope["payload"]["messages"][0]["content"]
        self.assertIn("These fields must agree", content)
        self.assertEqual(content, (ROOT / "agent/prompts/tool-selection-candidate-v2.md").read_text(encoding="utf-8").strip())
        self.assertIn(".planning/llm-live-readiness/phases/065-p02-candidate-v3/AUTHORIZATION.json", ex.root_files())

    def test_unknown_campaign_is_rejected(self):
        with self.assertRaises(ValueError):
            ex.use_campaign("p02-holdout-v1")

    def test_live_candidate_requires_frozen_manifest_before_provider_session(self):
        output = io.StringIO()
        with patch.object(ex, "verify_candidate_authority", return_value={}), patch.object(ex, "validate_manifest", side_effect=ex.ExecutionBlocked("manifest_missing")), patch.object(ex, "live_session") as session, patch.dict(os.environ, {"LLM_MODE": "live"}), redirect_stdout(output):
            code = cli.main(["--stage", "development", "--campaign", "p02-dev-v2", "--execute-free", "--max-trials", "1"])
        self.assertEqual(code, 2)
        self.assertEqual(json.loads(output.getvalue())["reason"], "manifest_missing")
        session.assert_not_called()

    def test_candidate_fingerprint_binds_its_own_root_authorization(self):
        ex.use_campaign("p02-dev-v2")
        self.assertIn(".planning/llm-live-readiness/phases/064-p02-candidate-development/AUTHORIZATION.json", ex.root_files())

    def test_existing_candidate_manifest_is_never_overwritten(self):
        ex.use_campaign("p02-dev-v2")
        with tempfile.TemporaryDirectory() as temporary:
            out = Path(temporary)
            manifest = out / "manifest.json"
            manifest.write_text("existing", encoding="utf-8")
            with patch.object(ex, "fingerprint", return_value="a" * 64), patch.object(ex, "git", return_value="b" * 40):
                with self.assertRaisesRegex(ex.ExecutionBlocked, "manifest_already_exists"):
                    ex.freeze(ROOT, ROOT.parents[1], out, ROOT / "evals/datasets/live-v1/cases.jsonl", [CASE])
            self.assertEqual(manifest.read_text(encoding="utf-8"), "existing")

    def test_preflight_requires_authorization_capacity_and_unspent_freeze(self):
        ex.use_campaign("p02-dev-v2")
        class Account:
            def __init__(self, authorized, rows):
                self.authorized, self.rows = authorized, rows

            def _p02_campaigns(self):
                return {ex.CAMPAIGN: 24} if self.authorized else {}

            def _history(self):
                return self.rows

        prior = [{"project": "p02", "campaign": "p02-dev-v1", "event": "completed", "status": "ok"}] * 24
        with self.assertRaisesRegex(ex.ExecutionBlocked, "candidate_authorization_missing"):
            ex.candidate_preflight(Account(False, prior), freezing=True)
        self.assertEqual(ex.candidate_preflight(Account(True, prior), freezing=True)["development_used"], 24)
        with self.assertRaisesRegex(ex.ExecutionBlocked, "development_capacity_insufficient"):
            ex.candidate_preflight(Account(True, prior * 3), freezing=True)
        uncertain = prior + [{"project": "p05", "campaign": "other", "event": "reserved", "status": None}]
        with self.assertRaisesRegex(ex.ExecutionBlocked, "uncertain_attempt_requires_reconciliation"):
            ex.candidate_preflight(Account(True, uncertain), freezing=True)
        spent = prior + [{"project": "p02", "campaign": "p02-dev-v2", "event": "completed", "status": "ok"}]
        with self.assertRaisesRegex(ex.ExecutionBlocked, "candidate_already_started"):
            ex.candidate_preflight(Account(True, spent), freezing=True)
        stopped = prior + [{"project": "p02", "campaign": "p02-dev-v2", "event": "completed", "status": "provider_error"}]
        with self.assertRaisesRegex(ex.ExecutionBlocked, "candidate_stopped_requires_review"):
            ex.candidate_preflight(Account(True, stopped), freezing=False)

    def test_cli_checks_account_before_freeze_or_live(self):
        for option in ("--freeze", "--execute-free"):
            output = io.StringIO()
            with self.subTest(option=option), patch.object(ex, "verify_candidate_authority", side_effect=ex.ExecutionBlocked("candidate_authorization_missing")) as gate, redirect_stdout(output):
                code = cli.main(["--stage", "development", "--campaign", "p02-dev-v2", option, "--max-trials", "1"])
            self.assertEqual(code, 2)
            self.assertEqual(json.loads(output.getvalue())["reason"], "candidate_authorization_missing")
            gate.assert_called_once()
