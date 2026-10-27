# Phase 010 run record

All runs were local, fake/offline, and used the locked environment. No credentials, provider, network, Docker, or external service was accessed.

| Command | Exit | Output |
|---|---:|---|
| `uv run --locked python -m unittest discover -s tests -p test_guardrails.py -v` | 0 | `guardrail-tests.txt` |
| `uv run --locked python -m unittest discover -s tests -p test_tools.py -v` | 0 | `tool-tests.txt` |
| `uv run --locked python -m unittest discover -s tests -p test_evals.py -v` | 0 | `eval-tests.txt` |
| `uv run --locked python scripts/check_fast.py` | 0 | `check-fast.txt` |
| `uv run --locked python scripts/check_full.py` | 0 | `full-gate.txt` |

The initial red contract run is `red-tests.txt` (exit 1, expected: missing retrieved-source parameter/provenance/citation API). Full gate reports 58 tests. SHA-256 comparison covers all existing files under `artifacts/` except this phase evidence, all `evals/` data/config/rubrics, and `scripts/campaign_ledger.py`; 71 files remained byte-identical.
