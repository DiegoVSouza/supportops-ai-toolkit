# Plan

1. Refactor the prepared protocol for an owning live controller while retaining fixture-only public defaults; add fixed synthetic configuration, source-bound manifest validation and shared lease/session startup.
2. Test source mismatch, missing live opt-in, reservation-before-startup, uncertain failure, no replay and fake contracts; run locked fast/full gates, save evidence and commit sources.
3. Freeze manifest against the committed source, verify official docs/catalog and funded allocation, then run one bounded synthetic operation; stop on any failure/uncertainty and reconcile without replay.

allowed_write_paths: .planning/phases/016-accounted-local-operation/**; supportops_toolkit/accounted_generation.py; scripts/local_operation.py; tests/test_local_operation.py; evals/live-execution.json; artifacts/evals/live/local-operation-v1/manifest.json; artifacts/evals/live/operations.sqlite* (new append-only identity/reservation/result); artifacts/evals/live/provider-usage.sqlite* (shared guard only); artifacts/evidence/accounted-local-operation-016/**; docs/harness/progress.md; .runtime shared registry (normal P02 registration only), account/campaign locks (normal operation only).

forbidden_changes: old attempts/manifests, sibling sources, legacy runner enablement, other budgets, holdout/confirmation, paid use, fallback/retries, real identity/customer data, Docker, human approvals. Budget: at most one live call this phase, within applied four-call envelope; 4096 input/512 output, timeout 20s, USD 0 paid. max_tries: 3 local validation attempts per failure; live completion never replayed. Stop on unknown work, invalid source/manifest, quota/provider/semantic error. Plan-check: implementer self-assessment.
