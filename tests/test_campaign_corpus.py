from __future__ import annotations

import json
import unittest
from pathlib import Path

from scripts.campaign_corpus import MODEL_FAMILIES, SYSTEM_PROMPT, build_case, build_messages, build_payload, request_number

ROOT = Path(__file__).resolve().parents[1]
CASES = [
    json.loads(line)
    for line in (ROOT / "evals/datasets/live-v1/cases.jsonl").read_text(encoding="utf-8").splitlines()
    if line.strip()
]
DEV = [c for c in CASES if c["split"] == "development"]


class CorpusTests(unittest.TestCase):
    def test_every_development_case_builds_deterministically(self) -> None:
        self.assertEqual(len(DEV), 24)
        self.assertEqual({c["family"] for c in DEV}, set(MODEL_FAMILIES))
        for case in DEV:
            self.assertEqual(build_case(case), build_case(case))

    def test_request_number_is_the_first_three_digit_token(self) -> None:
        self.assertEqual(request_number("Ticket 601: ignore previous"), 601)
        self.assertEqual(request_number("two invoices, 501 and 501A"), 501)
        with self.assertRaises(ValueError):
            request_number("no number")

    def test_knowledge_window_is_derived_and_stated_in_the_article(self) -> None:
        for case in (c for c in DEV if c["family"] == "knowledge_question"):
            built = build_case(case)
            self.assertEqual(built.window, 2 + request_number(case["text"]) % 5)
            self.assertIn(str(built.window), built.evidence["support_article"])

    def test_ledger_never_lists_the_missing_invoice_and_marks_the_conflict(self) -> None:
        for case in DEV:
            built = build_case(case)
            number = str(request_number(case["text"]))
            if case["family"] == "invoice_missing":
                self.assertNotIn(number, built.evidence["ledger_invoice_ids"])
            if case["family"] == "contradictory_evidence":
                self.assertEqual(built.evidence["ledger"], {number: "unpaid"})

    def test_prompt_carries_no_expected_outcome_or_rubric_text(self) -> None:
        for case in DEV:
            body = json.dumps(build_messages(build_case(case)), ensure_ascii=False)
            for forbidden in ("expected", "required_facts", "forbidden_facts", "rubric", case["id"]):
                self.assertNotIn(forbidden, body)

    def test_payload_fits_the_accounted_per_call_bounds(self) -> None:
        for case in DEV:
            payload = build_payload(build_case(case), "openai/gpt-oss-20b")
            encoded = json.dumps(payload, ensure_ascii=False, separators=(",", ":")).encode()
            self.assertLessEqual(len(encoded) + 256 + 64 * 2, 4096)
            self.assertEqual(payload["max_completion_tokens"], 512)
            self.assertIs(payload["include_reasoning"], False)
        self.assertIn("untrusted", SYSTEM_PROMPT)


if __name__ == "__main__":
    unittest.main()
