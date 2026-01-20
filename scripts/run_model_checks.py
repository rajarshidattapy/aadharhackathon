import os
import sys
import json
import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL_DIR = os.path.join(ROOT, "models")

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
        if os.path.isfile(full) and p.lower().endswith((".pt", ".pth", ".onnx", ".h5", ".keras")):
            entries.append(full)
        elif os.path.isdir(full) and os.path.exists(os.path.join(full, "saved_model.pb")):
            entries.append(full)  # TF SavedModel dir
    return sorted(entries)

def try_torch(path):
    try:
        import torch
        model = torch.jit.load(path) if path.endswith(".pt") and is_jit(path) else torch.load(path, map_location="cpu")
        model.eval()
        # Try to get example input size from module if available
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
    # crude: JIT files often end with .pt but may be zip headers — assume not JIT otherwise
    # allow jit detection by loading attempt in try_torch wrapper
    return False

def try_keras(path):
    try:
        import tensorflow as tf
        model = tf.keras.models.load_model(path)
        # get input shape from model
        inp_shape = None
        if model.inputs:
            shape = model.inputs[0].shape
            # convert TensorShape to concrete tuple, set batch=1 if None
            inp_shape = tuple([1 if s is None else int(s) for s in shape])
        if inp_shape is None:
            # fallback to common shapes (NHWC)
            for s in [(1, h, w, 3) for (_, _, h, w) in COMMON_IMAGE_SHAPES]:
                try:
                    _ = model(np.zeros(s, dtype=np.float32))
                    return True, "OK with shape {}".format(s)
                except Exception:
                    continue
            return False, "Couldn't infer input shape for Keras model"
        else:
            try:
                arr = np.zeros(inp_shape, dtype=np.float32)
                _ = model(arr)
                return True, "OK with inferred shape {}".format(inp_shape)
            except Exception as e:
                return False, "Keras inference error: {}".format(e)
    except Exception as e:
        return False, "Keras/TensorFlow error: {}".format(e)

def try_onnx(path):
    try:
        import onnxruntime as ort
        sess = ort.InferenceSession(path, providers=['CPUExecutionProvider'])
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
        res = sess.run(None, {inp.name: arr})
        return True, "OK with input {}".format(shape)
    except Exception as e:
        return False, "ONNX error: {}".format(e)

def try_saved_model(dirpath):
    try:
        import tensorflow as tf
        model = tf.saved_model.load(dirpath)
        # try to find a callable signature
        if hasattr(model, "signatures") and model.signatures:
            fn = list(model.signatures.values())[0]
            # build dummy inputs for signature
            args = {}
            for k, v in fn.structured_input_signature[1].items():
                shp = v.shape.as_list()
                shp = [1 if s is None else int(s) for s in shp]
                args[k] = tf.zeros(shp, dtype=v.dtype)
            _ = fn(**args)
            return True, "OK via signature"
        # fallback: try call on common image shapes if model is callable
        for s in COMMON_IMAGE_SHAPES:
            try:
                inp = tf.zeros(s, dtype=tf.float32)
                _ = model(inp)  # may fail for non-callable or different signature
                return True, "OK with shape {}".format(s)
            except Exception:
                continue
        return False, "SavedModel load succeeded but couldn't run inference"
    except Exception as e:
        return False, "SavedModel/TensorFlow error: {}".format(e)

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
    return False, "Unsupported model type"

def main():
    models = list_models()
    if not models:
        print("No models found in:", MODEL_DIR)
        print("Place .pt/.pth/.onnx/.h5 or a SavedModel folder under that directory.")
        return 1
    summary = {}
    for m in models:
        print("Checking:", os.path.basename(m))
        ok, msg = check_model(m)
        summary[os.path.basename(m)] = {"ok": bool(ok), "msg": msg}
        print(" ->", "PASS" if ok else "FAIL", "-", msg)
    print("\nSummary:")
    print(json.dumps(summary, indent=2))
    # exit code non-zero if any fail
    any_fail = any(not v["ok"] for v in summary.values())
    return 0 if not any_fail else 2

if __name__ == "__main__":
    sys.exit(main())

