# P02 local wheel provenance

- Distribution: `supportops-ai-toolkit` version `0.2.0`.
- Artifact: `supportops_ai_toolkit-0.2.0-py3-none-any.whl`.
- Source commit: `b4966c54fa3feda3ff1eae36ee872e5c407a4102` (`fix(toolkit): fail closed on indeterminate tool calls`).
- SHA-256: `7126517f9c64202b034b8a067dedf29e1313bb3139f15a984e93660654eb4d10`.
- Build: `python -m pip wheel --no-deps --no-build-isolation -w artifacts/packages .`; exit 0; setuptools 78.1.0 was already installed and no network access was used. Output is saved in `artifacts/evidence/package-build-0.2.0.txt`.
- Consumer smoke: installed with `pip --no-index --no-deps --target` in a temporary directory, then verified package metadata and import origin outside the source checkout. Exit 0; output is `artifacts/evidence/package-install-0.2.0.txt`.
- P05 must pin and install this exact wheel, record this version/commit/hash, and pass its consumer contract checks before package integration is PASS.
- No publication occurred.
