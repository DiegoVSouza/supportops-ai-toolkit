# P02 Git setup audit

Commands were run from `C:\estudo\Golpe\lab\projects\p02` on 2026-10-15. Exit codes are PowerShell `$LASTEXITCODE`/the Git command exit status.

| Check | Command | Exit | Result |
|---|---|---:|---|
| Exact repository root | `git rev-parse --show-toplevel` | 0 | `C:/estudo/Golpe/lab/projects/p02` |
| Branch | `git branch --show-current` | 0 | `main` |
| Hook path installed | `git rev-parse --git-path hooks/commit-msg; Test-Path .githooks/commit-msg` | 0 | `.githooks/commit-msg`; file exists |
| Invalid message | `python scripts/validate_commit.py .audit-invalid-msg` (`bad message`) | 1 | Rejected: `Invalid commit. Expected type(scope): imperative English description` |
| Valid message | `python scripts/validate_commit.py .audit-valid-msg` (`docs(audit): record P02 Git setup evidence`) | 0 | Accepted |
| Initial commit | `git log -1 --format='%H %s'` | 0 | `3850a7af51f44e6377cf24f395a9b7d5c7e10127 chore(harness): initialize project repository` |

The commit validator was invoked directly with real message files, exercising the same validator called by `.githooks/commit-msg`. Direct execution of the POSIX hook wrapper is unavailable in this PowerShell environment (`sh` is not installed); actual commit validation will additionally be confirmed by a normal local commit without bypassing hooks.

Ignore checks after updating `.gitignore`:

| Path | `git check-ignore` exit | Rule |
|---|---:|---|
| `.env` | 0 | `.env` |
| `.env.local` | 0 | `.env.*` |
| `venv/pyvenv.cfg` | 0 | `venv/` |
| `.venv/pyvenv.cfg` | 0 | `.venv/` |
| `__pycache__/module.pyc` | 0 | `__pycache__/` |
| `.pytest_cache/README.md` | 0 | `.pytest_cache/` |
| `dist/package.whl` | 0 | `dist/` |

## Captured outputs

```text
root=C:/estudo/Golpe/lab/projects/p02
branch=main
invalid_exit=1
invalid_output=Invalid commit. Expected type(scope): imperative English description
valid_exit=0
valid_output=(empty; accepted)
initial_commit=3850a7af51f44e6377cf24f395a9b7d5c7e10127 chore(harness): initialize project repository
```
