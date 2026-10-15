# Task 2 — Evaluation gate evidence

## Unit tests
- Class: unit/evaluation tests over synthetic fixtures.
- Command: `python -m unittest discover -s tests -p 'test_evals.py' -v`
- Exit code: `0`.
- Output:

```text
test_deliberate_degradation_fails_gate (test_evals.EvalTests.test_deliberate_degradation_fails_gate) ... ok
test_groundedness_compares_answer_terms_to_evidence (test_evals.EvalTests.test_groundedness_compares_answer_terms_to_evidence) ... ok
test_invalid_dataset_rejected (test_evals.EvalTests.test_invalid_dataset_rejected) ... ok
test_regression_tolerance_boundary (test_evals.EvalTests.test_regression_tolerance_boundary) ... ok
test_versioned_dataset_fake_baseline (test_evals.EvalTests.test_versioned_dataset_fake_baseline) ... ok

Ran 5 tests in 0.014s
OK
```

## Fake fixture eval run
- Class: offline eval gate, deterministic fake fixture only.
- Command: `$env:LLM_MODE='fake'; python -m supportops_toolkit.evals.runner --dataset evals/datasets/v1/supportops.jsonl --baseline evals/baseline/v1.json`
- Exit code: `0`.
- Output:

```json
{
  "mode": "fake",
  "total": 10,
  "decision_accuracy": 1.0,
  "tool_call_accuracy": 1.0,
  "groundedness": 1.0,
  "escalation_accuracy": 1.0,
  "failures": [],
  "regression": "PASS",
  "quality_claim": "fixture-only; not a model measurement"
}
```

The baseline and labels are synthetic fixture data. These scores are not estimates of live model quality. No replay cassette, external system integration, E2E, or live model eval was run.
