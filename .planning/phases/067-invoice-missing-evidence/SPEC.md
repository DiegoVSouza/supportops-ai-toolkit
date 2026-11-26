# Invoice Missing Evidence Repair

## Problem

The P02 live development smoke returned an answer for `invoice_missing-01` even though the case should escalate. The current prompt tells the model to escalate for records absent from evidence, while the deterministic context provides only a list of ledger IDs and requires the model to infer that the requested ID is missing.

## Goal

Make invoice lookup evidence explicit and bind a missing lookup result to an escalation/abstention response. Keep the behavior deterministic and testable without provider calls.

## Acceptance criteria

- Every synthetic `invoice_missing` case carries its requested invoice ID and an explicit `found: false` lookup result.
- The system prompt requires `decision=escalate`, `tool=lookup_invoice`, `escalate=true`, and `abstain=true` for that result.
- Regression tests cover the evidence and prompt rule, and the full P02 fake test suite passes.
- No live provider call, holdout access, or replay occurs in this phase.

## Out of scope

No dataset mutation, campaign replay, budget change, or provider authorization.
