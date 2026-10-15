# Task 3 — Guardrails evidence

- Unit class: guardrail behavior, authorization, PII, and execution boundaries.
- Command: `python -m unittest discover -s tests -p 'test_guardrails.py' -v`
- Exit code: `0`.
- Output:

```text
test_adversarial_suite_all_cases_block (test_guardrails.GuardrailTests.test_adversarial_suite_all_cases_block) ... ok
test_injection_blocks_and_normal_text_passes (test_guardrails.GuardrailTests.test_injection_blocks_and_normal_text_passes) ... ok
test_pii_redaction_email_phone_and_card (test_guardrails.GuardrailTests.test_pii_redaction_email_phone_and_card) ... ok
test_roles_allow_only_configured_tools (test_guardrails.GuardrailTests.test_roles_allow_only_configured_tools) ... ok
test_step_token_time_limits_and_exact_boundary (test_guardrails.GuardrailTests.test_step_token_time_limits_and_exact_boundary) ... ok
test_suite_rejects_smaller_than_required (test_guardrails.GuardrailTests.test_suite_rejects_smaller_than_required) ... ok

Ran 6 tests in 0.011s
OK
```

- Adversarial class: deterministic synthetic attack suite.
- Command: `python -c "from pathlib import Path; from supportops_toolkit.adversarial import run_adversarial; print(run_adversarial(Path('guardrails/adversarial.jsonl')))"`
- Exit code: `0`.
- Output: `AdversarialReport(total=35, blocked=35, block_rate=1.0, misses=())`.

Coverage is 10 direct injection, 10 indirect knowledge-content injection, 8 exfiltration, 4 tool abuse, and 3 over-limit refund attempts. The 100% result applies only to these synthetic test cases; it is not a measured production attack-block rate. Heuristics are not a semantic security guarantee.
