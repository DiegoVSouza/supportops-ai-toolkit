# Live campaign preparation — planning checks

No provider calls or Docker mutations were made. The project budget remains USD 0.

| Command | Exit | Observed result |
|---|---:|---|
| `uv run --locked python scripts/check_fast.py` | 0 | `check-fast: OK`. |
| `uv run --locked python scripts/check_full.py` | 0 | Metadata and fast checks passed; 41 unit tests passed; fake evaluation 10/10 with `quality_claim=fixture-only`; adversarial suite blocked 35/35; `check-full: PASS`. |

These offline fixtures do not measure model quality or authorize live calls. The historical real tool-selection failure and remediation artifacts were not changed.
