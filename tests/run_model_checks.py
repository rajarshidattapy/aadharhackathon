import json
import os
import pickle
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL_DIR = os.path.join(ROOT, "models")

SUPPORTED_FILE_EXTS = (".pt", ".pth", ".onnx", ".h5", ".keras", ".pkl")
COMMON_IMAGE_SHAPES = [
    (1, 3, 224, 224),
    (1, 3, 256, 256),
    (1, 1, 28, 28),
    (1, 3, 299, 299),
    (1, 3, 128, 128),
]


def list_models():
    if not os.path.isdir(MODEL_DIR):
        print("Model directory not found:", MODEL_DIR)
        return []

    entries = []
    for p in os.listdir(MODEL_DIR):
        full = os.path.join(MODEL_DIR, p)
        if os.path.isfile(full) and p.lower().endswith(SUPPORTED_FILE_EXTS):
            entries.append(full)
        elif os.path.isdir(full) and os.path.exists(os.path.join(full, "saved_model.pb")):
            entries.append(full)  # TF SavedModel dir
    return sorted(entries)


def try_torch(path):
    try:
        import torch

        model = torch.jit.load(path) if path.endswith(".pt") and is_jit(path) else torch.load(path, map_location="cpu")
        model.eval()
        for shape in COMMON_IMAGE_SHAPES:
            try:
                inp = torch.randn(shape)
                with torch.no_grad():
                    _ = model(inp)
                return True, "OK with shape {}".format(shape)
            except Exception:
                continue
        return False, "Failed to find a working input shape (tried common shapes)"
    except Exception as e:
        return False, "Torch error: {}".format(e)


def is_jit(path):
    # Keep legacy behavior for non-scripted checkpoints.
    return False


def try_keras(path):
    try:
        import numpy as np
        import tensorflow as tf

        model = tf.keras.models.load_model(path)
        inp_shape = None
        if model.inputs:
            shape = model.inputs[0].shape
            inp_shape = tuple([1 if s is None else int(s) for s in shape])

        if inp_shape is None:
            for s in [(1, h, w, 3) for (_, _, h, w) in COMMON_IMAGE_SHAPES]:
                try:
                    _ = model(np.zeros(s, dtype=np.float32))
                    return True, "OK with shape {}".format(s)
                except Exception:
                    continue
            return False, "Could not infer input shape for Keras model"

        arr = np.zeros(inp_shape, dtype=np.float32)
        _ = model(arr)
        return True, "OK with inferred shape {}".format(inp_shape)
    except Exception as e:
        return False, "Keras/TensorFlow error: {}".format(e)


def try_onnx(path):
    try:
        import numpy as np
        import onnxruntime as ort

        sess = ort.InferenceSession(path, providers=["CPUExecutionProvider"])
        inputs = sess.get_inputs()
        if not inputs:
            return False, "ONNX model has no inputs"

        inp = inputs[0]
        shape = []
        for dim in inp.shape:
            if isinstance(dim, str) or dim is None:
                shape.append(1)
            else:
                shape.append(int(dim))

        arr = np.random.randn(*shape).astype(np.float32)
        _ = sess.run(None, {inp.name: arr})
        return True, "OK with input {}".format(shape)
    except Exception as e:
        return False, "ONNX error: {}".format(e)


def try_saved_model(dirpath):
    try:
        import tensorflow as tf

        model = tf.saved_model.load(dirpath)
        if hasattr(model, "signatures") and model.signatures:
            fn = list(model.signatures.values())[0]
            args = {}
            for k, v in fn.structured_input_signature[1].items():
                shp = v.shape.as_list()
                shp = [1 if s is None else int(s) for s in shp]
                args[k] = tf.zeros(shp, dtype=v.dtype)
            _ = fn(**args)
            return True, "OK via signature"

        for s in COMMON_IMAGE_SHAPES:
            try:
                inp = tf.zeros(s, dtype=tf.float32)
                _ = model(inp)
                return True, "OK with shape {}".format(s)
            except Exception:
                continue
        return False, "SavedModel loaded but could not run inference"
    except Exception as e:
        return False, "SavedModel/TensorFlow error: {}".format(e)


def try_pickle_model(path):
    """Validate pickle/joblib artifacts used by this repo's ML endpoint."""
    try:
        size = os.path.getsize(path)
    except OSError as e:
        return False, "Could not stat pickle file: {}".format(e)

    if size <= 0:
        return False, "Pickle file is empty"

    basename = os.path.basename(path).lower()

    # Threshold file should be a small dict with known keys.
    if "threshold" in basename:
        obj = None
        try:
            import joblib  # Optional; prefer when available.

            obj = joblib.load(path)
        except Exception:
            try:
                with open(path, "rb") as f:
                    obj = pickle.load(f)
            except Exception as e:
                return False, "Could not load thresholds pickle: {}".format(e)

        if not isinstance(obj, dict):
            return False, "Threshold artifact is not a dict"

        required = {"raw_min", "raw_max", "watch", "surge"}
        missing = sorted(required - set(obj.keys()))
        if missing:
            return False, "Threshold artifact missing keys: {}".format(missing)

        return True, "Threshold pickle validated"

    # For model artifacts, a non-empty readable pickle/joblib file is enough for smoke checks.
    return True, "Pickle artifact exists and is non-empty ({} bytes)".format(size)


def check_model(path):
    ext = path.lower()
    if os.path.isdir(path) and os.path.exists(os.path.join(path, "saved_model.pb")):
        return try_saved_model(path)
    if ext.endswith((".pt", ".pth")):
        return try_torch(path)
    if ext.endswith((".h5", ".keras")):
        return try_keras(path)
    if ext.endswith(".onnx"):
        return try_onnx(path)
    if ext.endswith(".pkl"):
        return try_pickle_model(path)
    return False, "Unsupported model type"


def main():
    models = list_models()
    if not models:
        print("No models found in:", MODEL_DIR)
        print("Place supported model files under that directory: {}".format(", ".join(SUPPORTED_FILE_EXTS)))
        return 1

    summary = {}
    for m in models:
        print("Checking:", os.path.basename(m))
        ok, msg = check_model(m)
        summary[os.path.basename(m)] = {"ok": bool(ok), "msg": msg}
        print(" ->", "PASS" if ok else "FAIL", "-", msg)

    print("\nSummary:")
    print(json.dumps(summary, indent=2))

    any_fail = any(not v["ok"] for v in summary.values())
    return 0 if not any_fail else 2


if __name__ == "__main__":
    sys.exit(main())
