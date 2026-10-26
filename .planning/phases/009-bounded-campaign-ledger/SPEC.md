# Phase 009 — Bounded campaign ledger for P02

## Goal

Add durable, project-local campaign reservations, a serialized process lease, and read-only resume inspection to P02's existing Core evaluation preparation. Keep provider generation blocked until finite campaign resources, profile authorization, dataset/rubric review, and model preflight are evidenced.

## Starting evidence

- Phase 008 froze 80 synthetic cases (24 development / 56 holdout; 48 English / 32 Portuguese) and an offline reservation report: 6 pilot calls, 240 primary calls, 60 fresh confirmation calls, or 306 additive calls.
- P02's configured task budget remains USD 0. Historical free-plan single-case exceptions do not authorize this campaign.
- Provider quota, finite cumulative limits, confirmation funding, reviewer approval, pacing, wall-clock cap, and authenticated model preflight remain pending. The campaign config disables generation.
- P00/P01 ledger code is design reference only. Implement P02-owned state without sibling imports, cross-project accounting claims, or product runtime changes.

## Acceptance criteria

1. An append-only SQLite ledger records reservations before attempts, reconciles known usage, retains full reservations for unknown usage, and prevents uncertain/completed trials from being repeated.
2. Cumulative request/token/estimated-cost caps are checked atomically across P02 campaign IDs; concurrent reservations cannot exceed them.
3. A local OS lease excludes simultaneous P02 campaign processes and releases after normal exit. Metadata contains only operational identifiers, never credentials or case content.
4. `--resume CAMPAIGN_ID --dry-run` is read-only, reports sanitized recorded attempts/usage, and fails with exit 2 for unknown/empty campaigns. It never retries uncertain provider calls.
5. The existing campaign CLI remains blocked while any approval, quota, cumulative cap, or model-preflight requirement is unresolved; dry-run does not construct the SDK, read `.env`, access the network, or mutate Docker.
6. Focused regressions and the fake fast/full gates pass; evidence and project knowledge are updated.

## Out of scope

Groq dispatch, cap/quota approvals, changing the USD 0 profile, edits to frozen cases/rubrics, hidden judges, runtime changes, real refunds, Docker changes, cross-project ledger integration, paid or free provider calls, public deployment, or external effects.

## Status

`PLANNED`; campaign execution and local-live promotion remain `INCOMPLETE`.
