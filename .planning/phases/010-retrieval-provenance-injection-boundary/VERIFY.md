# Verify — Retrieval provenance and indirect-injection boundary

Status: PLANNED. Execute only after plan check; retain command, exit code, and output in `artifacts/evidence/retrieval-provenance-injection/`.

- [ ] Local retrieval returns stable source IDs, exact text, and explicit untrusted provenance.
- [ ] The shared guard screens user and retrieved text; detected indirect injection yields a typed block/refusal and no executable action.
- [ ] PII redaction and existing direct-injection behavior remain correct.
- [ ] Citation references must belong to the current retrieval result; missing/unknown IDs fail. Documentation states this is not entailment verification.
- [ ] Tests cover the real `search_kb` then guard/citation path without credentials or network.
- [ ] Focused, fast, and full locked offline gates pass; user-modified and historical artifacts are byte-preserved.
- [ ] Dataset, split, rubric, graders/thresholds, campaign configs/ledgers, and historical live evidence are unchanged.
- [ ] Staged diff contains only phase-owned paths and no secrets; commit is local and atomic.
- [ ] External source integration, tenant auth, model-level refusal, live quality, and independent/human review remain INCOMPLETE/PENDING.

No live quality, security certification, or production RAG readiness claim may be made from fixture tests.
