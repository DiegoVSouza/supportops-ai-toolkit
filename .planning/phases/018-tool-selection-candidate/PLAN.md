# Plan

1. Write tests first for a versioned prompt and candidate payload, preserving the existing corpus and free-account bounds; record the red result.
2. Add the candidate prompt under `agent/prompts/` and a distinct offline payload builder. The tool is an assessment label only, not permission to execute a refund. Test on development cases without embedding expected labels or case identifiers.
3. Run focused and full fake checks, save command, exit code and output, and document that live quality and external RAG remain pending. Prepare a separate campaign plan only after the candidate is tested.

allowed_write_paths: `.planning/phases/018-tool-selection-candidate/**`, `agent/prompts/**`, `scripts/candidate_corpus.py`, `tests/test_candidate_corpus.py`, `artifacts/evidence/tool-selection-candidate-018/**`, `docs/harness/decisions.md`, `docs/harness/progress.md`.

forbidden_changes: old campaign code and artifacts, dataset and rubric, root account and policy, holdout and confirmation, credentials, other projects and real effects. `LLM_MODE=fake`; zero provider calls. Stop at three attempts per reproducible failure.
