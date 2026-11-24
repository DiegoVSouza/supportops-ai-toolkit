import json
import subprocess
import sys
import unittest
from pathlib import Path

from scripts import campaign_execution as ex
from scripts.campaign_corpus import build_case

ROOT = Path(__file__).resolve().parents[1]
CASE = next(row for line in (ROOT / "evals/datasets/live-v1/cases.jsonl").read_text(encoding="utf-8").splitlines() if (row := json.loads(line))["split"] == "development")


class CampaignCandidateTests(unittest.TestCase):
    def tearDown(self):
        ex.use_campaign("p02-dev-v1")

    def test_candidate_prompt_is_part_of_frozen_source_set(self):
        self.assertIn("agent/prompts/tool-selection-candidate-v1.md", ex.source_paths(ROOT))

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

    def test_unknown_campaign_is_rejected(self):
        with self.assertRaises(ValueError):
            ex.use_campaign("p02-holdout-v1")

    def test_candidate_freeze_and_live_execution_are_closed(self):
        for option in ("--freeze", "--execute-free"):
            result = subprocess.run([sys.executable, "scripts/run_live_campaign.py", "--stage", "development", "--campaign", "p02-dev-v2", option, "--max-trials", "1"], cwd=ROOT, capture_output=True, text=True)
            self.assertEqual(result.returncode, 2)
            self.assertEqual(json.loads(result.stdout)["reason"], "candidate_campaign_not_enabled")
