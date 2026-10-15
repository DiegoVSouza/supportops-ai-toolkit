import json
import tempfile
import unittest
from pathlib import Path

from supportops_toolkit.evals.runner import EvalReport, RegressionError, assert_regression, fake_runner, is_grounded, run_evals

DATASET = Path("evals/datasets/v1/supportops.jsonl")


class EvalTests(unittest.TestCase):
    def test_versioned_dataset_fake_baseline(self):
        report = run_evals(fake_runner, DATASET)
        self.assertEqual(report.total, 10)
        self.assertEqual(report.decision_accuracy, 1.0)
        self.assertEqual(report.tool_call_accuracy, 1.0)
        self.assertEqual(report.groundedness, 1.0)
        self.assertEqual(report.escalation_accuracy, 1.0)
        baseline = json.loads(Path("evals/baseline/v1.json").read_text())
        assert_regression(report, baseline)

    def test_deliberate_degradation_fails_gate(self):
        report = run_evals(lambda _: {"decision": "wrong", "tool": "wrong", "grounded": False, "escalate": False}, DATASET)
        self.assertEqual(report.decision_accuracy, 0.0)
        with self.assertRaises(RegressionError):
            assert_regression(report, {"decision_accuracy": 1.0, "tool_call_accuracy": 1.0, "groundedness": 1.0, "escalation_accuracy": 1.0})

    def test_regression_tolerance_boundary(self):
        current = EvalReport(1, 0.95, 0.95, 1, 1, ())
        baseline = {"decision_accuracy": 1.0, "tool_call_accuracy": 1.0, "groundedness": 1.0, "escalation_accuracy": 1.0}
        assert_regression(current, baseline, 0.05)
        with self.assertRaises(ValueError):
            assert_regression(current, baseline, 1.1)

    def test_groundedness_compares_answer_terms_to_evidence(self):
        self.assertTrue(is_grounded("carrier status after dispatch", "carrier status is available after dispatch"))
        self.assertFalse(is_grounded("refund was already issued", "carrier status is available after dispatch"))
        self.assertFalse(is_grounded("", "some evidence"))
        with self.assertRaises(ValueError):
            is_grounded("answer", "evidence", min_overlap=0)

    def test_invalid_dataset_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "bad.jsonl"
            path.write_text('{"id":"duplicate"}\n', encoding="utf-8")
            with self.assertRaises(ValueError):
                run_evals(fake_runner, path)


if __name__ == "__main__":
    unittest.main()
