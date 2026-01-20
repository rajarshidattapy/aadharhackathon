import os
import sys
import subprocess
import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL_DIR = os.path.join(ROOT, "models")
# Try script in scripts/ and at repo root (convenience for local runs)
SCRIPT_CANDIDATES = [
    os.path.join(ROOT, "scripts", "run_model_checks.py"),
    os.path.join(ROOT, "run_model_checks.py"),
]
SCRIPT = next((p for p in SCRIPT_CANDIDATES if os.path.exists(p)), SCRIPT_CANDIDATES[0])
SUPPORTED_EXTS = (".pt", ".pth", ".onnx", ".h5", ".keras")

def has_models():
    if not os.path.isdir(MODEL_DIR):
        return False
    for name in os.listdir(MODEL_DIR):
        full = os.path.join(MODEL_DIR, name)
        if os.path.isfile(full) and name.lower().endswith(SUPPORTED_EXTS):
            return True
        if os.path.isdir(full) and os.path.exists(os.path.join(full, "saved_model.pb")):
            return True
    return False

def test_run_model_checks():
    if not os.path.exists(SCRIPT):
        pytest.skip("run_model_checks.py not found (looked for {})".format(", ".join(SCRIPT_CANDIDATES)))
    if not has_models():
        pytest.skip("No model files found under {}".format(MODEL_DIR))
    # Run script with the same Python interpreter running tests
    proc = subprocess.run([sys.executable, SCRIPT], capture_output=True, text=True)
    # Print outputs for diagnostic on failure
    if proc.returncode != 0:
        print("STDOUT:\n", proc.stdout)
        print("STDERR:\n", proc.stderr)
    assert proc.returncode == 0, "Model checks failed (exit code {})".format(proc.returncode)
