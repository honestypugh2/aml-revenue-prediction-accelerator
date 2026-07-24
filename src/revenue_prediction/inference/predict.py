"""Model bundle packaging and batch inference.

A :class:`ModelBundle` couples a fitted estimator with its leakage-safe feature
builder and metadata, so scoring is reproducible and self-describing. Batch
prediction emits the primary output (predicted month-end net revenue) plus the
required secondary outputs: model version, run id, cutoff date, scoring
timestamp, and the relevant dimensions. Uncertainty bounds are included when the
estimator exposes per-tree/per-estimator variance.
"""

from __future__ import annotations

import datetime as _dt
import uuid
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from ..data.schema import FEATURE_COLUMNS, KEY_COLUMNS
from ..features.engineering import LeakageSafeFeatureBuilder
from ..models.factory import BASELINE_MODELS


@dataclass
class ModelBundle:
    """Serializable inference bundle."""

    model_name: str
    estimator: Any
    feature_builder: LeakageSafeFeatureBuilder | None
    model_version: str = "0.1.0"
    run_id: str = field(default_factory=lambda: uuid.uuid4().hex[:12])
    trained_at: str = field(default_factory=lambda: _dt.datetime.now(_dt.UTC).isoformat())

    @property
    def is_baseline(self) -> bool:
        return self.model_name in BASELINE_MODELS


def save_bundle(bundle: ModelBundle, path: str | Path) -> Path:
    """Persist a bundle to disk with joblib."""
    import joblib

    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(bundle, path)
    return path


def load_bundle(path: str | Path) -> ModelBundle:
    """Load a bundle previously saved with :func:`save_bundle`."""
    import joblib

    return joblib.load(Path(path))


def _uncertainty(estimator: Any, X: pd.DataFrame) -> np.ndarray | None:
    """Best-effort per-row std estimate from tree ensembles, else ``None``."""
    estimators = getattr(estimator, "estimators_", None)
    if estimators is None:
        return None
    try:
        preds = np.stack([np.asarray(est.predict(X), dtype=float) for est in np.ravel(estimators)])
        return preds.std(axis=0)
    except Exception:  # pragma: no cover - defensive
        return None


def batch_predict(
    bundle: ModelBundle,
    frame: pd.DataFrame,
    cutoff_day: int | None = None,
) -> pd.DataFrame:
    """Score ``frame`` and return a self-describing prediction dataframe."""
    keys = [c for c in KEY_COLUMNS if c in frame.columns]
    output = frame[keys].copy()

    if bundle.is_baseline:
        preds = np.asarray(bundle.estimator.predict(frame), dtype=float)
        uncertainty = None
    else:
        if bundle.feature_builder is None:
            raise ValueError("Non-baseline bundle requires a fitted feature_builder")
        cols = [c for c in FEATURE_COLUMNS if c in frame.columns]
        X = bundle.feature_builder.transform(frame[cols])
        preds = np.asarray(bundle.estimator.predict(X), dtype=float)
        uncertainty = _uncertainty(bundle.estimator, X)

    output["predicted_month_end_net_revenue"] = preds
    if uncertainty is not None:
        output["prediction_std"] = uncertainty
        output["prediction_lower"] = preds - 1.96 * uncertainty
        output["prediction_upper"] = preds + 1.96 * uncertainty

    output["model_name"] = bundle.model_name
    output["model_version"] = bundle.model_version
    output["run_id"] = bundle.run_id
    output["cutoff_day"] = cutoff_day if cutoff_day is not None else frame.get("snapshot_day")
    output["scored_at"] = _dt.datetime.now(_dt.UTC).isoformat()
    return output
