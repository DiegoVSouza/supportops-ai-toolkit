# Plan — Retrieval provenance and indirect-injection boundary

## Execution controls

- `llm_mode`: `fake`; offline only. No credential lookup, SDK construction, network, or provider access.
- `allowed_write_paths`:
  - `.planning/phases/010-retrieval-provenance-injection-boundary/**`
  - `supportops_toolkit/guardrails.py`
  - `supportops_toolkit/sample_tools.py`
  - `supportops_toolkit/evals/runner.py`
  - `tests/test_guardrails.py`
  - `tests/test_tools.py`
  - `tests/test_evals.py`
  - `docs/architecture.md`
  - `docs/harness/progress.md`
  - `docs/harness/failures.md`
  - `docs/harness/feature_list.json`
  - `docs/knowledge/P02-prod-ai.md`
  - `artifacts/evidence/retrieval-provenance-injection/**`
- `forbidden_changes`: all evaluation dataset bytes, split/manifest, rubrics and grader thresholds; `harness.yaml`/budget; campaign configs, ledger/registry and historical evidence; live runners/provider settings; credentials; other repositories; root lab/harness-kit; Docker, external services/effects, refunds, paid or free provider calls, push/publication, or weakened tests.
- Budget: live/provider authorization is zero; this phase consumes zero provider calls and zero provider tokens. Local compute only.
- Validation commands: locked focused `python -m unittest` suites; `python scripts/check_fast.py`; `python scripts/check_full.py`; source/dataset/rubric/ledger byte-hash comparison; `git diff --check` and staged-path/secret review. Record commands, exit codes, sanitized outputs under the evidence path.
- Stop conditions: any required existing fixture, dataset, grader, rubric, or user-modified evidence would need alteration; a behavior requires an external source/runtime not present; any provider call would be needed; or a gate regresses. In these cases keep affected criterion INCOMPLETE and do not substitute fixtures as live evidence.

## Tasks

1. **Specify and test retrieval boundary first** — add red tests for attributable local search results, indirect injection screening, safe refusal/block disposition, and citations limited to supplied source IDs. Keep source content synthetic and do not use grader labels as retrieval context.
2. **Implement owned local contracts** — extend the common text guard to accept a typed source context without trusting it, return no executable action for blocked retrieved content, add source identifiers/trust markers to `search_kb`, and add citation-ID validation with an explicit non-entailment limitation.
3. **Verify integration and record limits** — run focused tests and full fake gates, preserve user artifacts, compare all forbidden data/ledger hashes, update feature/progress/failure/architecture/knowledge records, save evidence, and review/commit only owned paths.

## Plan check

Implementer self-check against P02 `harness.yaml`, project instructions, phase 008 frozen data contract, phase 009 campaign ledger, and actual `sample_tools.search_kb`/`guardrails.guard` interfaces. Scope is local toolkit-owned code only. Write paths are disjoint from immutable datasets/rubrics/ledgers. No independent review is claimed; independent and human reviews remain PENDING. No live call is in this phase.
