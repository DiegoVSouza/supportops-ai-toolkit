# P02 package build and local install provenance

- Package: `supportops-ai-toolkit==0.1.0`.
- Source repository root: `C:/estudo/Golpe/lab/projects/p02`.
- Source commit: `8a3ddbbcf64ab22aadac8aec996390c9d62d7a5b`.
- Build command: `python -m pip wheel --no-deps --no-build-isolation --wheel-dir <temporary wheel directory> .`
- Build exit code: `0`.
- Artifact: `C:/Users/dvsdi/AppData/Local/Temp/supportops-p02-wheel-8a3ddbb/supportops_ai_toolkit-0.1.0-py3-none-any.whl`.
- SHA-256: `22579A982191A41D83E2FFF3DB032B2D812EE0EDA288064605DA80C564D6D69F`.
- Install command: `python -m pip install --no-deps --no-index --target <temporary install directory> <wheel>`.
- Install exit code: `0`; import exit code: `0`.
- Import smoke output: `{'version': '0.1.0', 'tool_status': 'paid'}`.
- Full gate against the same source commit: `python scripts/check_full.py`, exit code `0`; full output in `postcommit-check.log`.

The wheel is a local temporary artifact and was not published. The install used `--no-index` and `--no-deps`; the runtime has no third-party dependencies. Temporary artifact path may not persist beyond this machine/session; rebuild with the command above and verify the recorded hash.
