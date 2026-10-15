# P02 committed wheel copy and isolated offline install

## Provenance and copy
- Repository: `C:/estudo/Golpe/lab/projects/p02`; `git rev-parse --show-toplevel` exit `0`.
- Source code commit embedded in package provenance: `00a5f9b8e1f9c78ea26f09839d24847cfcfbf6f6`.
- Source wheel: `%TEMP%/supportops-p02-wheel-00a5f9b/supportops_ai_toolkit-0.1.0-py3-none-any.whl`.
- Pre-copy source SHA-256: `5B7F1BBD9DD015620D5CB9CBCF6B4B39B1D2DC668805B066E7A2D9A930D48A52` (matched expected hash).
- Destination before copy: absent. The file was copied only because `artifacts/packages/supportops_ai_toolkit-0.1.0-py3-none-any.whl` did not exist; no existing artifact was overwritten.
- Post-copy command: `Get-FileHash -LiteralPath artifacts/packages/supportops_ai_toolkit-0.1.0-py3-none-any.whl -Algorithm SHA256`.
- Post-copy exit code: `0`.
- Post-copy SHA-256: `5B7F1BBD9DD015620D5CB9CBCF6B4B39B1D2DC668805B066E7A2D9A930D48A52`.
- `git check-ignore artifacts/packages/supportops_ai_toolkit-0.1.0-py3-none-any.whl` exit code: `1` (not ignored; Git will track it).

## Isolated offline install
- Create environment: `python -m venv %TEMP%/p02-artifact-smoke-venv`; exit code `0`.
- Install: `%TEMP%/p02-artifact-smoke-venv/Scripts/python.exe -m pip install --no-index --no-deps --disable-pip-version-check artifacts/packages/supportops_ai_toolkit-0.1.0-py3-none-any.whl`; exit code `0`.
- Import/tool smoke: `%TEMP%/p02-artifact-smoke-venv/Scripts/python.exe -c "import supportops_toolkit; from supportops_toolkit.sample_tools import lookup_invoice; from supportops_toolkit.evals.runner import is_grounded; print({'version': supportops_toolkit.__version__, 'invoice_status': lookup_invoice(invoice_id='inv-100')['status'], 'groundedness': is_grounded('refund policy', 'refund policy under policy')})"`; exit code `0`.
- Smoke output: `{'version': '0.1.0', 'invoice_status': 'paid', 'groundedness': True}`.

No package was rebuilt, external dependency resolved, model called, or artifact published during this task.
