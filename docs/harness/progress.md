# Progress

## 2026-10-29 — Phase 015 accounted protocol preparation

- Added a fixture-only adapter matching the shared preview/complete envelope and accounted receipt schema. Tenant-scoped retrieval feeds bounded input; local durable reservations precede dispatch, survive uncertainty and enforce a cumulative four-request ceiling. Duplicate receipts and invalid/model-mismatched usage fail closed.
- Six focused regressions and the locked fast/full gates pass (78 unit tests). Attempt 1 found an unclosed SQLite connection in test cleanup; explicit closing fixed it on attempt 2. Evidence: `artifacts/evidence/accounted-protocol-015/`.
- This ceiling is an offline prototype limit, not a live allocation. Finite shared migration, committed live manifest and actual provider integration remain pending; no credentials, network or Docker were used.

- Kit initialization completed.

## 2026-10-15 — Roadmap remediation phase 002

- Created and reviewed `.planning/phases/002-remediation/` before implementation; planning commit: `a6b9087`.
- Added fail-closed behavior for indeterminate tool timeouts and generic transport errors. Automatic retries now require explicit `ToolError(retryable=True)` classification.
- Wired optional `execution_limits` into tool invocation: each call consumes a step and its wait is capped by the remaining wall-clock budget. Token use must be reported at a caller's LLM boundary; P02 has no integrated agent runtime, so whole-run token enforcement remains INCOMPLETE.
- Defined the supported JSON Schema subset and reject unsupported keywords; number validation rejects booleans and non-finite values for inputs and outputs.
- Fake unit and full local gates pass; evidence is in `artifacts/evidence/phase-002-regression-green.txt` and `phase-002-check-full.txt`. The earlier red regression is preserved in `phase-002-regression-red.txt`.
- Cost, latency, and real model quality remain PENDING; no live or replay model call was made.
- Package API/behavior change is recorded in ADR-001. Version `0.2.0` will be built as a local wheel after the source commit; P05 must consume its recorded hash before package integration can pass.

## 2026-10-23 — Phase 003 live free-model evaluation

- Added a standard-library evaluator for the ten synthetic cases using `cohere/north-mini-code:free`. It verifies zero pricing from the authenticated model catalog, uses a forced structured assessment tool call, never retries, stops on HTTP 429, and records malformed/provider-error cases.
- Offline full gate passed with 29 tests. Evidence: `artifacts/evidence/phase-004-validation.txt`.
- Live run attempted all ten cases: nine valid model assessments and one provider error. Decision/tool/escalation each scored 8/9 among valid outputs; groundedness is `NOT_EVALUATED` because the dataset does not supply independent retrieval context. Reported usage: 1,882 input and 726 output tokens; cost: USD 0. Evidence: `artifacts/evidence/live-free-model-eval.json`.
- Evaluation status is `INCOMPLETE`; the provider error is preserved, and these ten synthetic records do not establish production quality.

## 2026-10-23 — Phase 004 Groq live evaluation

- Added optional `groq==1.7.0` live extra, one-case live runner, bounded transient retry/key rotation, and offline control tests. The default toolkit remains dependency-free.
- Offline phase tests pass (9 tests); full P02 check passes (38 tests, fake eval 10/10, adversarial 35/35). Evidence: `artifacts/evidence/phase-004-groq-live-offline.txt` and `phase-004-groq-live-full.txt`.
- Authenticated model listing confirmed `openai/gpt-oss-20b`. The one real case used 206 prompt tokens and 204 completion tokens (410 total), no retries or rotation. Decision and escalation passed; tool selection failed (`issue_refund` predicted, `lookup_invoice` expected). Metrics: decision 1/1, escalation 1/1, tool 0/1. Evidence: `artifacts/evidence/phase-004-groq-live-run.json` and `.txt`.
- Phase result: `INCOMPLETE` at the capability gate because the selected real case failed its tool assertion. Cost is `PENDING`: the public developer-plan rate is nonzero and the provider SDK does not return account billing tier or charged amount. No additional live call was made.

## 2026-10-26 — Phase 005 Groq evaluation remediation

- Root cause: phase-004's valid response chose `issue_refund` because the prompt did not distinguish read-only invoice verification from the refund action, and the ticket omitted a verified invoice identifier/balance. The fixture label remains unchanged.
- The first remediation request returned HTTP 400 after adding a property-level tool-schema description; it was not retried. The field was removed while the semantic guidance remained in the system prompt. The failed request is preserved at `phase-005-groq-remediation-attempt-1.json`.
- Corrected live run passed decision, tool selection, and escalation for `refund-eligible`: 319 prompt tokens, 426 completion tokens, 745 total; no retries or key rotation. Cost remains `PENDING` because billed account usage is not exposed by the SDK. Evidence is in `phase-005-groq-remediation.json` and `phase-005-groq-remediation-live.txt`.
- Focused remediation suite: 11 tests passed. Full gate: 40 tests, fake eval 10/10, adversarial 35/35; all pass. Evidence: `phase-005-groq-offline.txt` and `phase-005-groq-full.txt`. Phase status: `PASS` for the one-case remediation; one sample is not a broad quality claim.

## 2026-10-26 — Phase 006 numbered-key allowlist

- P02 now selects only `GROQ_API_KEY_1..4`; the compatibility `GROQ_API_KEY` is not an evaluation credential. The phase-005 success/failure evidence remains unchanged.
- Full offline gate passed: 40 tests, fake regression 10/10, adversarial 35/35. The four-key live run passed `refund-eligible` with 319 prompt / 472 completion tokens, no retries or rotation, and cost `PENDING`.

## 2026-10-26 — Live Docker acceptance

The first real completion returned HTTP 400 after successful model preflight and was not retried. The request now uses max_completion_tokens=512 and reasoning_effort=low; a regression verifies those parameters. One corrective real evaluation passed the unchanged decision/tool/escalation assertions (319 input / 91 output tokens). The exact original HTTP 400 cause was not established because the response body was deliberately not retained. Evidence: artifacts/evidence/live-docker/.
## 2026-10-26 — Phase 009 bounded campaign ledger

- Added append-only reservation accounting, atomic cumulative caps, a cross-process lease, and read-only resume inspection. Unknown usage retains the original reservation; reserved or completed trials cannot be repeated.
- Focused ledger checks: 6 passed. Full fake project gate: 54 tests plus regression/adversarial checks passed. `-S` dry-run exited 0 and generation exited 2 while campaign requirements remain unresolved. No provider request or Docker mutation occurred.
- Dispatcher, authorized finite caps, human review, crash-after-dispatch recovery, lease integration into live execution and independent review remain incomplete. Phase status: `INCOMPLETE`; evidence: `artifacts/evidence/live-campaign-ledger/`.

## 2026-10-27 — Phase 010 local retrieval provenance and injection boundary

- The actual local `search_kb` output now includes stable `source_id`, exact source text, and `trust: untrusted`. The shared guard accepts explicit `user` or `retrieved` context and identifies detected retrieved injection as `indirect_prompt_injection`; a block verdict supplies no action or sanitized executable content.
- Added citation-ID membership validation against only the current supplied retrieval results. It does not measure entailment. Local contract tests cover retrieval -> screening and citation membership. Historical datasets, splits, rubrics, graders, thresholds, campaign configuration/ledgers, and live artifacts remain unchanged.
- Offline control checks are recorded in `artifacts/evidence/retrieval-provenance-injection/`. No credentials, network, provider, Docker, or external effects were used. External KB/RAG, tenant isolation, integrated model refusal, and real quality remain INCOMPLETE; human and independent review remain PENDING.

## 2026-10-27 — Phase 011 retrieval misses and interruption propagation

- Fixed local `search_kb` to return only documents with at least one query-term overlap. Zero-overlap requests now return no sources, so unrelated documents cannot be presented to the caller as attributable evidence. Stable source IDs, exact source text, the untrusted marker, and deterministic score/source ordering remain unchanged for matches.
- The tool registry no longer catches `BaseException` around `Future.result()`. `KeyboardInterrupt` and `SystemExit` propagate to the caller and do not cause a tool retry; ordinary exception classification, explicit retryable errors, and indeterminate timeout/no-retry behavior remain intact.
- Red tests reproduced both defects. Focused tool suite passed 11 tests; fast check and complete fake full gate passed; 60 unit tests and the 35-case adversarial suite passed. Fake evaluation remains fixture-only.
- The 71 protected paths from phase 010 (evaluation data, rubric/baseline, live history, campaign, ledger and prior evidence) have identical SHA-256 before/after hashes. No provider, credentials, external network, Docker or refund effect was used. Evidence: `artifacts/evidence/retrieval-misses-and-interrupts-011/`.
- External KB/RAG, tenant isolation, integrated model refusal, entailment verification, live quality, and independent/human review remain INCOMPLETE/PENDING.

## 2026-10-28 - Phase 012 fixture retrieval

- Added tenant-scoped synthetic fixture retrieval with attribution and refusal on no evidence or detected injection. Four focused tests and the full fake gate passed (64 tests). External identity, real RAG, model quality and independent review remain pending; see artifacts/evidence/fixture-retrieval-012/.
