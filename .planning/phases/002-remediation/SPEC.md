# Phase 002: Safe execution limits and tool contracts

## Goal

Close the evidenced P02 safety and execution-control gaps while preserving the public `supportops_toolkit` contract unless an ADR and versioned consumer update are approved.

## Baseline

- Phase 001 has an installed local package and a fake-mode test/evaluation gate.
- The portfolio remediation audit identifies caller-driven execution limits, timeout behavior that may leave a worker thread running, and an empty `docs/harness/feature_list.json`.
- Comparable cost and latency runs do not exist; those measurements remain `PENDING`.

## Acceptance criteria

1. A timed-out non-idempotent tool is never automatically retried when its side effect may have occurred. Retry may proceed only under a documented and tested idempotency contract, or execution is isolated in a cancellable process/service.
2. Step, token, and wall-clock limits are enforced by the execution path itself. Tests demonstrate rejection/termination at boundaries without requiring callers to remember a separate counter operation.
3. The supported JSON input/output schema subset is documented and enforced. Boundary tests distinguish booleans from numbers and reject non-finite numeric values; any promise of full JSON Schema/Pydantic semantics must use a conforming validator.
4. Fake regression and adversarial checks remain in the local gate; no existing test is weakened. Replay/model evaluation runs only with traceable sanitized cassettes or explicit authorization.
5. Feature checklist and progress reflect evidence-backed statuses. Cost and latency comparisons remain `PENDING` until comparable recorded runs exist.

## Constraints

- `LLM_MODE=fake`; no paid/live provider calls.
- No public contract change without an ADR, package version update, and consumer update plan.
- No sibling imports, publication, deployment, push, or changes to shared kit files.
- Distinguish unit/contract, package integration, service integration, E2E, and agent evaluation. Missing runs are `INCOMPLETE` or `PENDING`, never PASS.

## Out of scope

New model-quality claims, cost/latency benchmarking without comparable real runs, P03 telemetry, P04 queues, and P05 integration.
