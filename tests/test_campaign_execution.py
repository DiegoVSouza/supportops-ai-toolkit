from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from typing import Any

from scripts import campaign_execution as ex
from scripts.campaign_corpus import build_case

ROOT = Path(__file__).resolve().parents[1]
CASES = [
    json.loads(line)
    for line in (ROOT / "evals/datasets/live-v1/cases.jsonl").read_text(encoding="utf-8").splitlines()
    if line.strip()
]


def oracle() -> ex.OracleFixtureSession:
    return ex.OracleFixtureSession({build_case(c).text: c for c in ex.ordered_cases(CASES)})


def no_sleep(_seconds: float) -> None:
    return None


class FailingSession:
    provenance = "fixture"

    def __init__(self, result: Any = None, error: Exception | None = None, content: str | None = None):
        self.result, self.error, self.content = result, error, content
        self.calls = 0

    def preview(self, envelope: dict[str, Any]) -> None:
        return None

    def complete(self, envelope: dict[str, Any]) -> dict[str, Any]:
        self.calls += 1
        if self.error:
            raise self.error
        if self.content is not None:
            return {"status": "ok", "model": ex.MODEL, "attempt_id": "0" * 32, "content": self.content,
                    "finish_reason": "length", "usage": {"input_tokens": 100, "output_tokens": 512}, "latency_ms": 5.0}
        return self.result


class FakeAccountBlocked(Exception):
    pass


FakeAccountBlocked.__name__ = "AccountBlocked"


class ExecutionTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.out = Path(self.temp.name) / "run"

    def run_campaign(self, session: Any, max_trials: int, reader=None):
        return ex.execute_campaign(
            cases=CASES, session=session, out_dir=self.out, usage_reader=reader or session.usage_for,
            max_trials=max_trials, min_gap_seconds=0, sleep=no_sleep,
        )

    def trials(self) -> list[dict[str, Any]]:
        return ex.read_jsonl(self.out / "trials.jsonl")

    def test_pilot_cases_run_first_and_cover_six_distinct_families(self) -> None:
        order = [c["id"] for c in ex.ordered_cases(CASES)]
        self.assertEqual(order[:6], list(ex.PILOT_IDS))
        self.assertEqual(len(order), 24)
        self.assertEqual(len({i.rsplit("-", 1)[0] for i in ex.PILOT_IDS}), 6)

    def test_full_fixture_run_passes_every_case_and_stays_content_free(self) -> None:
        session = oracle()
        progress = self.run_campaign(session, 100)
        self.assertEqual(progress, {"ran": 24, "remaining": 0})
        rows = self.trials()
        self.assertEqual(len(rows), 24)
        self.assertTrue(all(r["pass"] and r["provenance"] == "fixture" and r["provider_calls"] == 1 for r in rows))
        blob = (self.out / "trials.jsonl").read_text(encoding="utf-8")
        for case in CASES:
            if case["split"] == "development":
                self.assertNotIn(case["text"][:30], blob)
        self.assertNotIn("business days", blob)
        self.assertNotIn('"answer":', blob)
        report = ex.build_report(CASES, self.out, provenance="fixture")
        self.assertEqual(report["status"], "COMPLETE")
        self.assertEqual(report["live_model"]["passed"], 24)
        self.assertEqual(report["live_model"]["latency_ms"]["n"], 24)

    def test_resume_never_repeats_a_finished_case(self) -> None:
        session = oracle()
        self.assertEqual(self.run_campaign(session, 6), {"ran": 6, "remaining": 18})
        self.assertEqual(self.run_campaign(session, 100), {"ran": 18, "remaining": 0})
        ids = [r["case_id"] for r in self.trials()]
        self.assertEqual(len(ids), len(set(ids)))
        self.assertEqual(self.run_campaign(session, 5), {"ran": 0, "remaining": 0})
        self.assertTrue(all(session.calls[i] == 1 for i in ids))

    def test_a_non_ok_provider_result_stops_the_campaign_without_replay(self) -> None:
        session = FailingSession(result={"status": "INCOMPLETE", "reason": "rate_limit", "attempt_id": "1" * 32})
        with self.assertRaisesRegex(ex.ExecutionBlocked, "rate_limit"):
            self.run_campaign(session, 3, reader=lambda _id: {"calls": 1, "input_tokens": 0, "output_tokens": 0})
        self.assertEqual(session.calls, 1)
        self.assertTrue((self.out / "stop.json").exists())
        with self.assertRaisesRegex(ex.ExecutionBlocked, "campaign_stopped_requires_review"):
            self.run_campaign(session, 3, reader=lambda _id: {"calls": 1, "input_tokens": 0, "output_tokens": 0})
        self.assertEqual(session.calls, 1)
        self.assertEqual(self.trials(), [])

    def test_safe_account_reasons_survive_and_unknown_errors_become_uncertain(self) -> None:
        reader = lambda _id: {"calls": 0, "input_tokens": 0, "output_tokens": 0}  # noqa: E731
        with self.assertRaisesRegex(ex.ExecutionBlocked, "cumulative_account_cap"):
            self.run_campaign(FailingSession(error=FakeAccountBlocked("cumulative_account_cap")), 1, reader=reader)
        other = Path(self.temp.name) / "other"
        with self.assertRaisesRegex(ex.ExecutionBlocked, "uncertain_attempt"):
            ex.execute_campaign(
                cases=CASES, session=FailingSession(error=RuntimeError("secret prompt text")), out_dir=other,
                usage_reader=reader, max_trials=1, min_gap_seconds=0, sleep=no_sleep,
            )
        self.assertNotIn("secret", (other / "stop.json").read_text(encoding="utf-8"))

    def test_usage_that_disagrees_with_the_root_ledger_stops_the_campaign(self) -> None:
        session = oracle()
        with self.assertRaisesRegex(ex.ExecutionBlocked, "usage_mismatch"):
            self.run_campaign(session, 1, reader=lambda _id: {"calls": 1, "input_tokens": 1, "output_tokens": 1})
        self.assertEqual(self.trials(), [])

    def test_a_reservation_without_a_result_blocks_until_reviewed(self) -> None:
        session = oracle()
        self.run_campaign(session, 1)
        ledger = ex.CampaignLedger(self.out / "ledger.sqlite", campaign_id=ex.CAMPAIGN)
        ledger.reserve(
            case_id="stranded", trial=1, input_tokens=4096, output_tokens=512,
            estimated_cost_usd=ex.TRIAL_CAPS["estimated_cost_usd"], caps=ex.campaign_caps(),
        )
        with self.assertRaisesRegex(ex.ExecutionBlocked, "uncertain_trial_requires_review"):
            self.run_campaign(session, 1)

    def test_a_truncated_reply_is_a_graded_schema_failure_not_a_stop(self) -> None:
        session = FailingSession(content='{"decision": "answ')
        ex.execute_campaign(
            cases=CASES, session=session, out_dir=self.out,
            usage_reader=lambda _id: {"calls": 1, "input_tokens": 100, "output_tokens": 512},
            max_trials=1, min_gap_seconds=0, sleep=no_sleep,
        )
        row = self.trials()[0]
        self.assertFalse(row["pass"])
        self.assertEqual(row["errors"], ["schema"])
        self.assertEqual(row["observation"]["finish_reason_class"], "length")
        self.assertFalse((self.out / "stop.json").exists())

    def test_percentile_is_nearest_rank_and_wilson_is_bounded(self) -> None:
        values = [float(i) for i in range(1, 21)]
        self.assertEqual(ex.percentile(values, 50), 10.0)
        self.assertEqual(ex.percentile(values, 95), 19.0)
        self.assertIsNone(ex.percentile([], 50))
        low, high = ex.wilson(12, 24)
        self.assertTrue(0 < low < 0.5 < high < 1)
        self.assertIsNone(ex.wilson(0, 0))

    def test_report_measures_refusal_grounding_and_injection(self) -> None:
        self.run_campaign(oracle(), 100)
        report = ex.build_report(CASES, self.out, provenance="fixture")
        safety = report["safety"]
        self.assertEqual(safety["correct_refusal"], {"expected": 18, "correct": 18})
        self.assertEqual(safety["false_refusal"], {"expected_answers": 6, "refused": 0})
        self.assertEqual(safety["injection_resistance"], {"cases": 3, "resisted": 3})
        self.assertEqual(safety["citation_grounding"], {"cases": 3, "grounded": 3})
        self.assertEqual(safety["completed_refund_claims"], 0)
        self.assertEqual(safety["invented_number_trials"], 0)
        self.assertEqual(report["human_review"], "PENDING")
        self.assertEqual(report["independent_review"], "WAIVED_BY_OWNER")
        self.assertFalse(report["raw_provider_content_persisted"])

    def test_manifest_is_required_before_a_live_run(self) -> None:
        with self.assertRaisesRegex(ex.ExecutionBlocked, "manifest_missing"):
            ex.validate_manifest(ROOT, ROOT.parents[1], self.out, ROOT / "evals/datasets/live-v1/cases.jsonl", CASES)


if __name__ == "__main__":
    unittest.main()
