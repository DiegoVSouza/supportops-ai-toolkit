# Verification

PASS: six focused protocol regressions, locked fast gate and locked full gate (78 unit tests plus fixture/adversarial gates), all exit 0. Evidence: `artifacts/evidence/accounted-protocol-015/attempt2.json` records command/cwd/exit/output. Attempt 1 failed during Windows temporary-file cleanup because the test used a SQLite transaction context without closing the connection. Explicit closing corrected the cause; attempt 2 passed, counter 2/3. The first failure remains preserved.

The adapter uses the shared envelope and receipt shape with injected fixture sessions only; durable cumulative four-request reservations, unknown-work stop, duplicate receipt rejection and scoped retrieval are verified offline. Live operation, funding migration, manifest, source authentication and human review remain INCOMPLETE/PENDING. Self-assessment only.
