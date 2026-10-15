# Task 2 — Reliable tools evidence

- Class: unit and contract tests (local deterministic doubles).
- Command: `python -m unittest discover -s tests -p 'test_tools.py' -v`
- Exit code: `0`.
- Python: `3.13` (runtime command `python --version`, exit 0).
- Output:

```text
test_input_shape_and_refund_bounds (test_tools.ToolContractTests.test_input_shape_and_refund_bounds) ... ok
test_registry_and_sample_tool_success (test_tools.ToolContractTests.test_registry_and_sample_tool_success) ... ok
test_retry_transient_but_fail_fatal (test_tools.ToolContractTests.test_retry_transient_but_fail_fatal) ... ok
test_timeout_and_invalid_configuration (test_tools.ToolContractTests.test_timeout_and_invalid_configuration) ... ok
test_unknown_invoice_and_output_validation (test_tools.ToolContractTests.test_unknown_invoice_and_output_validation) ... ok

Ran 5 tests in 0.021s
OK
```

The tools use in-memory fixtures. No external connector, paid model, performance metric, or production quality claim is covered by these unit tests.
