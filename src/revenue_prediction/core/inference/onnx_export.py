"""Optional ONNX export for portable, optimized inference.

Converts a fitted scikit-learn estimator (the champion's estimator) to ONNX so
it can run under ONNX Runtime for faster, framework-independent scoring — for
example inside an Azure ML managed endpoint using a prebuilt inference image.

Requires the optional ``onnx`` extra (``uv sync --extra onnx``). See
``docs/operations/onnx-optimization.md``.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any


def export_estimator_to_onnx(
    estimator: Any,
    n_features: int,
    path: str | Path,
) -> Path:
    """Convert a fitted sklearn estimator to ONNX and write it to ``path``.

    Parameters
    ----------
    estimator:
        A fitted scikit-learn regressor or pipeline (the champion's estimator).
    n_features:
        Number of input features the model expects (columns of the engineered
        feature matrix).
    path:
        Destination ``.onnx`` file.
    """
    try:
        from skl2onnx import convert_sklearn
        from skl2onnx.common.data_types import FloatTensorType
    except ImportError as exc:  # pragma: no cover - requires onnx extra
        raise ImportError(
            "skl2onnx is not installed. Install the 'onnx' extra: `uv sync --extra onnx`."
        ) from exc

    initial_type = [("input", FloatTensorType([None, n_features]))]
    onnx_model = convert_sklearn(estimator, initial_types=initial_type)
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(onnx_model.SerializeToString())
    return path


def predict_with_onnx(path: str | Path, features) -> Any:  # pragma: no cover - requires onnx extra
    """Run inference with an exported ONNX model via ONNX Runtime."""
    try:
        import numpy as np
        import onnxruntime as ort
    except ImportError as exc:
        raise ImportError(
            "onnxruntime is not installed. Install the 'onnx' extra: `uv sync --extra onnx`."
        ) from exc

    session = ort.InferenceSession(str(path), providers=["CPUExecutionProvider"])
    arr = np.asarray(features, dtype=np.float32)
    input_name = session.get_inputs()[0].name
    return session.run(None, {input_name: arr})[0]
