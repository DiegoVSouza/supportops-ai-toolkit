"""Capture offline check output without touching existing evidence."""
import os
from pathlib import Path
import subprocess
import sys

root = Path(__file__).resolve().parents[3]
out = Path(__file__).resolve().parent
env = os.environ.copy()
env["LLM_MODE"] = "fake"
for script in ("scripts/check_fast.py", "scripts/check_full.py"):
    command = [sys.executable, script]
    result = subprocess.run(command, cwd=root, env=env, capture_output=True, text=True, encoding="utf-8", errors="replace")
    report = f"command={' '.join(command)}\nworking_directory=projects/p02\nexit_code={result.returncode}\n{result.stdout}{result.stderr}"
    (out / (Path(script).stem + ".txt")).write_bytes(report.rstrip().encode("utf-8") + b"\n")
    print(script, "exit", result.returncode, flush=True)
    if result.returncode:
        sys.exit(result.returncode)
