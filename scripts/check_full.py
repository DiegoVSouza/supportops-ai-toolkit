#!/usr/bin/env python3
"""Run actual unit, eval, security, and metadata gates."""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def run(label: str, command: list[str], *, env: dict[str, str] | None = None) -> int:
    print(f"\n[{label}] {' '.join(command)}", flush=True)
    result = subprocess.run(command, cwd=ROOT, env=env, text=True)
    print(f"[{label}] exit_code={result.returncode}", flush=True)
    return result.returncode


def main() -> int:
    failures = []
    required = [
        "pyproject.toml", "requirements-build.lock", "docs/harness/sources.lock.json",
        "evals/datasets/v1/supportops.jsonl", "evals/baseline/v1.json",
        "guardrails/adversarial.jsonl",
        ".planning/phases/001-production-toolkit/SPEC.md",
        ".planning/phases/001-production-toolkit/PLAN.md",
        ".planning/phases/001-production-toolkit/VERIFY.md",
    ]
    missing = [path for path in required if not (ROOT / path).is_file()]
    if missing:
        print(f"[metadata] FAIL missing={missing}", flush=True)
        failures.append("metadata")
    else:
        sources = json.loads((ROOT / "docs/harness/sources.lock.json").read_text(encoding="utf-8"))
        project = (ROOT / "pyproject.toml").read_text(encoding="utf-8")
        build_lock = (ROOT / "requirements-build.lock").read_text(encoding="utf-8")
        if sources.get("runtime_dependencies") != [] or "dependencies = []" not in project:
            print("[metadata] FAIL runtime dependency lock mismatch", flush=True)
            failures.append("metadata")
        elif "setuptools==78.1.0" not in build_lock or "setuptools==78.1.0" not in project:
            print("[metadata] FAIL build backend lock mismatch", flush=True)
            failures.append("metadata")
        else:
            print("[metadata] PASS required artifacts and locked dependencies", flush=True)
    if run("fast", [sys.executable, "scripts/check_fast.py"]):
        failures.append("fast")
    if run("unit", [sys.executable, "-m", "unittest", "discover", "-s", "tests", "-v"]):
        failures.append("unit")
    env = os.environ.copy()
    env["LLM_MODE"] = "fake"
    if run("eval", [sys.executable, "-m", "supportops_toolkit.evals.runner"], env=env):
        failures.append("eval")
    if run("adversarial", [sys.executable, "-m", "supportops_toolkit.adversarial"]):
        failures.append("adversarial")
    print(f"\ncheck-full: {'FAIL' if failures else 'PASS'}; failures={failures}", flush=True)
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
