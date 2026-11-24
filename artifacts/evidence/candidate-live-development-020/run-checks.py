"""Capture offline campaign safety checks before freezing."""
import os
from pathlib import Path
import subprocess
import sys

root = Path(__file__).resolve().parents[3]
out = Path(__file__).resolve().parent
env = os.environ.copy()
env["LLM_MODE"] = "fake"
commands = [
    ("focused", [sys.executable, "-m", "unittest", "discover", "-s", "tests", "-p", "test_campaign_candidate.py", "-v"]),
    ("fast", [sys.executable, "scripts/check_fast.py"]),
    ("full", [sys.executable, "scripts/check_full.py"]),
]
for name, command in commands:
    result = subprocess.run(command, cwd=root, env=env, capture_output=True, text=True, encoding="utf-8", errors="replace")
    report = f"command={' '.join(command)}\nworking_directory=projects/p02\nexit_code={result.returncode}\n{result.stdout}{result.stderr}"
    (out / (name + "-final.txt")).write_bytes(report.rstrip().encode("utf-8") + b"\n")
    print(name, "exit", result.returncode, flush=True)
    if result.returncode:
        sys.exit(result.returncode)
