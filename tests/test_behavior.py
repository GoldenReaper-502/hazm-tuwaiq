import sys
import subprocess
import pytest


def test_validate_behavior_runs():
    """Run the validate_behavior.py script as a subprocess and ensure it exits 0."""
    proc = subprocess.run([sys.executable, "backend/validate_behavior.py"], capture_output=True, text=True, timeout=30)
    if proc.returncode != 0:
        print(proc.stdout)
        print(proc.stderr)
    assert proc.returncode == 0
