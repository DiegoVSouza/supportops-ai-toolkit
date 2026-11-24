"""Capture fake gates and an isolated fixture campaign without provider access."""
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

root = Path(__file__).resolve().parents[3]
out = Path(__file__).resolve().parent
env = os.environ.copy()
env["LLM_MODE"] = "fake"
with tempfile.TemporaryDirectory(prefix="p02-candidate-fixture-") as temporary:
    output = Path(temporary) / "campaign"
    commands = [
        ("focused", [sys.executable, "-m", "unittest", "discover", "-s", "tests", "-p", "test_campaign_candidate.py", "-v"]),
        ("fixture", [sys.executable, "scripts/run_live_campaign.py", "--stage", "development", "--campaign", "p02-dev-v2", "--execute-fixture", "--max-trials", "24", "--output-dir", str(output)]),
        ("check_fast", [sys.executable, "scripts/check_fast.py"]),
        ("check_full", [sys.executable, "scripts/check_full.py"]),
    ]
    for name, command in commands:
        result = subprocess.run(command, cwd=root, env=env, capture_output=True, text=True, encoding="utf-8", errors="replace")
        report = f"command={' '.join(command)}\nworking_directory=projects/p02\nexit_code={result.returncode}\n{result.stdout}{result.stderr}"
        (out / (name + ".txt")).write_bytes(report.rstrip().encode("utf-8") + b"\n")
        print(name, "exit", result.returncode, flush=True)
        if name == "fixture" and result.returncode == 0:
            shutil.copy2(output / "report.json", out / "fixture-report.json")
        if result.returncode:
            sys.exit(result.returncode)
