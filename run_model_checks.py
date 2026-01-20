#!/usr/bin/env python
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent

def main() -> int:
    # Candidate test targets (checked in order)
    candidates = [
        PROJECT_ROOT / "tests" / "model_checks",
        PROJECT_ROOT / "tests" / "test_model_checks.py",
        PROJECT_ROOT / "tests",
    ]

    target = next((p for p in candidates if p.exists()), None)

    if target is None:
        print("No model test paths found under `tests/` — skipping model checks.")
        return 0

    cmd = [sys.executable, "-m", "pytest", str(target)]

    try:
        result = subprocess.run(cmd, cwd=PROJECT_ROOT, check=False)
        return result.returncode
    except FileNotFoundError:
        print("Model checks command not found. Please install dependencies or update run_model_checks.py.")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
