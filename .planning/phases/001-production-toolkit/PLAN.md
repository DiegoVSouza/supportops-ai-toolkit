# P02 Phase 001 Plan

## Task 1 — Intake and contract plan
Complete harness rationale/decisions, source lock, SPEC/PLAN/VERIFY, and record plan review before product code.

## Task 2 — Reliable tools and eval gates
Implement tool registry, retry/timeout/error contracts, local SupportOps tools, versioned dataset, runner, baseline and regression gate with unit/failure tests.

## Task 3 — Guardrails and adversarial suite
Implement injection checks, role allowlist, execution limits, PII redaction, and >=30 adversarial cases with tests and visible misses.

## Task 4 — Cost utilities, docs, and release validation
Implement exact/semantic cache interface, routing, token budget, streaming and report; replace check_full placeholder; write bilingual docs; run/save full validation.

## Ownership and constraints
- `allowed_write_paths`: `.planning/**`, `harness.yaml`, `docs/harness/**`, `docs/knowledge/**`, `supportops_toolkit/**`, `tools/**`, `evals/**`, `guardrails/**`, `cost/**`, `tests/**`, `scripts/**`, `README.md`, `README.pt-BR.md`, `.github/workflows/**`, `pyproject.toml`, `artifacts/**`.
- `forbidden_changes`: files outside this project, harness kit, sibling projects, global Git config, public contracts without ADR/version, secrets, paid/live calls, push/publication.
- Dependency contract: no sibling imports; standard library only in initial version; fixtures are local doubles. No external runtime APIs are assumed.
- `LLM_MODE=fake`; eval/test command: `python scripts/check_full.py`.
- Validation commands and outputs are saved under `artifacts/evidence/`; commit only explicit task paths after checking repo root/status/diff and staged diff.
- Stop if a public contract change or external package install is required; record an ADR and report the dependency.

## Plan review
Reviewed against P02 acceptance: four observable tasks, paths are confined to this repository, validation is deterministic and fake-mode, and product code starts only after intake and plan commit.
