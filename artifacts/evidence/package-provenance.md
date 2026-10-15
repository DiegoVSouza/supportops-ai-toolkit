# P02 package build and local install provenance

- Package: `supportops-ai-toolkit==0.1.0`.
- Source repository root: `C:/estudo/Golpe/lab/projects/p02`.
- Source commit: `00a5f9b8e1f9c78ea26f09839d24847cfcfbf6f6` (includes the evidence-based groundedness grader).
- Build command: `python -m pip wheel --no-deps --no-build-isolation --wheel-dir <temporary wheel directory> .`
- Build exit code: `0`.
- Committed artifact: `artifacts/packages/supportops_ai_toolkit-0.1.0-py3-none-any.whl`.
- Original temporary artifact used for the copy: `C:/Users/dvsdi/AppData/Local/Temp/supportops-p02-wheel-00a5f9b/supportops_ai_toolkit-0.1.0-py3-none-any.whl`.
- SHA-256: `5B7F1BBD9DD015620D5CB9CBCF6B4B39B1D2DC668805B066E7A2D9A930D48A52`.
- Install command: `python -m pip install --no-deps --no-index --target <temporary install directory> <wheel>`.
- Install exit code: `0`; import exit code: `0`.
- Import smoke output: `{'version': '0.1.0', 'groundedness_supported': True}`.
- Full gate: `python scripts/check_full.py`, exit code `0`; 21 tests and full output in `groundedness-check.log`.

The earlier wheel from commit `8a3ddbb` was superseded after the groundedness fix. The current wheel is committed inside this project and was not published. The install used `--no-index` and `--no-deps`; the runtime has no third-party dependencies. Copy verification and isolated install evidence are in `artifact-install.md`.
