# Follow-up — evidence-based groundedness grading

- Change: replaced the runner's trusted `grounded` boolean with a lexical overlap rule between non-stopword answer terms and case evidence. Empty answers fail; default minimum overlap is 0.6.
- Unit command: `python -m unittest discover -s tests -p 'test_evals.py' -v`; exit code `0`; 5 tests pass, including supported answer, unsupported answer, empty answer, and invalid threshold boundaries.
- Fake eval command: `LLM_MODE=fake python -m supportops_toolkit.evals.runner`; exit code `0`; 10 synthetic fixture cases report decision/tool/groundedness/escalation `1.0`, regression `PASS`.
- Full command: `python scripts/check_full.py`; exit code `0`; 21 unit tests plus fast, eval, and adversarial gates pass. Full output is in `groundedness-check.log`.
- Interpretation: lexical overlap is a simple deterministic grader, not semantic entailment. Fake answers and labels remain synthetic and do not measure real model quality.
