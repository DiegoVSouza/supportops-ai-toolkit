# Phase 011 plan

## Ownership

`allowed_write_paths`:

- `.planning/phases/011-retrieval-misses-and-interrupts/**`
- `supportops_toolkit/sample_tools.py`
- `supportops_toolkit/tools.py`
- `tests/test_tools.py`
- `artifacts/evidence/retrieval-misses-and-interrupts-011/**`
- `docs/harness/progress.md`
- `docs/harness/failures.md`
- `docs/harness/feature_list.json`
- `docs/architecture.md`
- `docs/knowledge/P02-prod-ai.md`

`forbidden_changes`: evaluation datasets/manifests/splits, baselines/rubrics/graders/thresholds, adversarial corpus, prior phase evidence and provider attempts, campaign config/ledger/registry, live runner/provider config, credentials, `harness.yaml`, dependencies/package metadata, sibling/root source, Docker/external services, customer data, refunds/external effects, budget, push/publication or approvals.

## Tasks

1. Add red regressions for zero-overlap retrieval and `KeyboardInterrupt`/`SystemExit` propagation with zero retries; preserve tests for injection provenance, citations, timeout uncertainty and explicitly retryable tool errors.
2. Filter zero-overlap documents from local `search_kb`; narrow the registry's handler exception boundary so ordinary `Exception` failures retain current classification while `BaseException` process-control signals propagate. Do not cancel/retry an already-running handler on timeout or interruption.
3. Run focused `test_tools.py`, project fast and full fake gates; compare immutable dataset/rubric/grader/adversarial/provider/ledger inputs, save commands/exits/output under this phase, update progress/failure/knowledge state, review the staged diff/secrets, and commit only owned paths.

## Validation

- Red-before-fix: `\.venv\Scripts\python.exe -m unittest discover -s tests -p test_tools.py -v`.
- Focused: `\.venv\Scripts\python.exe -m unittest discover -s tests -p test_tools.py -v`.
- Fast: `\.venv\Scripts\python.exe scripts/check_fast.py`.
- Full fake: set `LLM_MODE=fake`; run `\.venv\Scripts\python.exe scripts/check_full.py`.
- Capture immutable input file hashes before/after and verify unchanged. Store exact commands, exit codes, sanitized output and source commit under `artifacts/evidence/retrieval-misses-and-interrupts-011/`.

## Budget and stop conditions

- USD 0, zero provider/API calls, credential reads, network, Docker, external retrieval, or refund executions.
- Stop if a regression requires changing cases, expected evidence, grader thresholds, adversarial cases, or public tool schemas; record the criterion INCOMPLETE instead of substituting fixtures.
- Stop on any automatic retry after timeout/interruption, any source-ID/provenance drift, or any modified protected input. No independent/human review or live model quality claim is inferred.
