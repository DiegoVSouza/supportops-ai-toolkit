"""Install a local wheel in an isolated target and verify its import/version."""

from __future__ import annotations

import os
import subprocess
import sys
import tempfile
from pathlib import Path


def main() -> int:
    if len(sys.argv) != 3:
        raise SystemExit("usage: verify_local_wheel.py WHEEL EXPECTED_VERSION")
    wheel = Path(sys.argv[1]).resolve()
    expected = sys.argv[2]
    with tempfile.TemporaryDirectory(prefix="p02-wheel-consumer-") as temporary:
        root = Path(temporary)
        target = root / "site-packages"
        subprocess.run(
            [sys.executable, "-m", "pip", "install", "--no-index", "--no-deps", "--target", str(target), str(wheel)],
            check=True,
        )
        environment = os.environ.copy()
        environment["PYTHONPATH"] = str(target)
        subprocess.run(
            [
                sys.executable,
                "-c",
                "import importlib.metadata, supportops_toolkit; "
                "assert importlib.metadata.version('supportops-ai-toolkit') == " + repr(expected) + "; "
                "print(importlib.metadata.version('supportops-ai-toolkit')); "
                "print(supportops_toolkit.__file__)",
            ],
            cwd=root,
            env=environment,
            check=True,
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
