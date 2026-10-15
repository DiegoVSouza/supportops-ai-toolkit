# Task 4 — Cost utilities, documentation, and full gate

## Validation
- Full gate command: `python scripts/check_full.py`
- Exit code: `0`; complete console transcript is in `check-full.log`.
- Gate classes: metadata/lock validation, check-fast, 20 unit/contract tests, fixture-only offline eval, and 35-case adversarial suite.
- Test summary: `Ran 20 tests ... OK`; `check-full: PASS; failures=[]`.
- Cost report command: `python cost/report.py`; exit code `0`.
- Cost report output: `{ "status": "PENDING", "reason": "No comparable recorded runs were supplied", "before": "PENDING", "after": "PENDING", "delta": "PENDING" }`.
- Packaging check: `python -m pip wheel --no-deps --no-build-isolation --wheel-dir <temporary wheel directory> .`; exit code `0`; built `supportops_ai_toolkit-0.1.0-py3-none-any.whl`.
- Local install check: `python -m pip install --no-deps --no-index --target <temporary install directory> <wheel>`; exit code `0`; import smoke printed `0.1.0 paid`.
- Runtime recorded: Python `3.13.12`; build backend `setuptools==78.1.0`; no runtime third-party dependencies.

No real latency, savings, token cost, provider quality, production integration, or E2E figures were recorded. The PENDING report is intentional.
