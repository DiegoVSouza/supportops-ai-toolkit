import json
import unittest
from pathlib import Path

from scripts.campaign_corpus import SYSTEM_PROMPT
from scripts.candidate_corpus import build_candidate_payload

ROOT = Path(__file__).resolve().parents[1]
DEV = [row for line in (ROOT / "evals/datasets/live-v1/cases.jsonl").read_text(encoding="utf-8").splitlines() if (row := json.loads(line))["split"] == "development"]


class CandidateCorpusTests(unittest.TestCase):
    def test_development_payloads_are_bounded_and_hide_answer_keys(self):
        for case in DEV:
            payload = build_candidate_payload(case, "openai/gpt-oss-20b")
            body = json.dumps(payload, ensure_ascii=False, separators=(",", ":"))
            self.assertLessEqual(len(body.encode("utf-8")) + 256 + 64 * 2, 4096)
            for forbidden in (case["id"], "required_facts", "forbidden_facts", "expected", "rubric"):
                self.assertNotIn(forbidden, body)
            self.assertNotEqual(payload["messages"][0]["content"], SYSTEM_PROMPT)
            self.assertEqual(payload["max_completion_tokens"], 512)

    def test_refuses_holdout_and_unknown_split_before_building(self):
        for split in ("holdout", "confirmation", "unknown"):
            with self.subTest(split=split), self.assertRaises(ValueError):
                build_candidate_payload({"split": split}, "model")

    def test_candidate_states_that_tool_selection_is_not_execution(self):
        prompt = build_candidate_payload(DEV[0], "model")["messages"][0]["content"]
        self.assertIn("not execute", prompt.lower())
        self.assertIn("untrusted", prompt.lower())
        self.assertIn("lookup_invoice", prompt)
        self.assertIn("issue_refund", prompt)
        self.assertIn("search_kb", prompt)
