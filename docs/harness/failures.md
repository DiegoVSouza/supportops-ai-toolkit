# Failures

Record recurring builder or product failures here before fixing them.

## 2026-10-26 — Live acceptance finding

The first real completion returned HTTP 400 after successful model preflight and was not retried. The request now uses max_completion_tokens=512 and reasoning_effort=low; a regression verifies those parameters. One corrective real evaluation passed the unchanged decision/tool/escalation assertions (319 input / 91 output tokens). The exact original HTTP 400 cause was not established because the response body was deliberately not retained. Failed attempt artifacts remain alongside the correction.
## 2026-10-26 — Phase 009 campaign ledger

- The first P01 implementation found that an attempt completed without usage must preserve its original reservation. P02 carries a regression for this accounting rule; no P02 provider attempt was replayed.
- Windows locks prevent reading the held lease file while another process owns it. The test checks sanitized operational metadata after normal lease release and still proves that concurrent acquisition is blocked.