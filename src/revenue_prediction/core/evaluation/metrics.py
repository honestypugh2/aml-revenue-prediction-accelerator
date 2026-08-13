"""Regression metrics, including grouped accuracy by facility and snapshot day."""

from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

from revenue_prediction.core.data.schema import FACILITY_COL, SNAPSHOT_DAY_COL


def smape(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    """Symmetric mean absolute percentage error (as a fraction, 0-2)."""
    y_true = np.asarray(y_true, dtype=float)
    y_pred = np.asarray(y_pred, dtype=float)
    denom = np.abs(y_true) + np.abs(y_pred)
    denom = np.where(denom == 0, 1.0, denom)
    return float(np.mean(2.0 * np.abs(y_pred - y_true) / denom))


def _mape(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    y_true = np.asarray(y_true, dtype=float)
    y_pred = np.asarray(y_pred, dtype=float)
    denom = np.where(np.abs(y_true) < 1e-9, 1e-9, np.abs(y_true))
    return float(np.mean(np.abs((y_true - y_pred) / denom)))


def wape(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    """Weighted absolute percentage error = sum|y-yhat| / sum|y|.

    Dollar-weighted and stable when some facilities are small, which is why it
    is the recommended headline metric for net-revenue forecasting (small
    facilities cannot dominate the error the way they can with MAPE).
    """
    y_true = np.asarray(y_true, dtype=float)
    y_pred = np.asarray(y_pred, dtype=float)
    denom = float(np.sum(np.abs(y_true)))
    if denom < 1e-9:
        return float("nan")
    return float(np.sum(np.abs(y_true - y_pred)) / denom)


def bias(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    """Signed relative bias = sum(yhat - y) / sum(y).

    Positive means the model over-forecasts revenue in aggregate; negative means
    it under-forecasts. Reported alongside WAPE so directional error is visible.
    """
    y_true = np.asarray(y_true, dtype=float)
    y_pred = np.asarray(y_pred, dtype=float)
    denom = float(np.sum(y_true))
    if abs(denom) < 1e-9:
        return float("nan")
    return float(np.sum(y_pred - y_true) / denom)


def compute_metrics(y_true, y_pred) -> dict[str, float]:
    """Compute the standard metric bundle used across the accelerator."""
    y_true = np.asarray(y_true, dtype=float)
    y_pred = np.asarray(y_pred, dtype=float)
    mse = float(mean_squared_error(y_true, y_pred))
    return {
        "wape": wape(y_true, y_pred),
        "bias": bias(y_true, y_pred),
        "mae": float(mean_absolute_error(y_true, y_pred)),
        "rmse": float(np.sqrt(mse)),
        "mape": _mape(y_true, y_pred),
        "smape": smape(y_true, y_pred),
        "r2": float(r2_score(y_true, y_pred)) if len(y_true) > 1 else float("nan"),
    }


def _grouped(frame: pd.DataFrame, group_col: str, y_true_col: str, y_pred_col: str) -> pd.DataFrame:
    records: list[dict[str, float | str | int]] = []
    for key, group in frame.groupby(group_col):
        metrics = compute_metrics(group[y_true_col], group[y_pred_col])
        metrics[group_col] = key
        metrics["n"] = int(len(group))
        records.append(metrics)
    result = pd.DataFrame(records)
    cols = [group_col, "n", "wape", "bias", "mae", "rmse", "mape", "smape", "r2"]
    return result[[c for c in cols if c in result.columns]]


def metrics_by_facility(frame: pd.DataFrame, y_true_col: str, y_pred_col: str) -> pd.DataFrame:
    """Facility-level aggregate accuracy."""
    return _grouped(frame, FACILITY_COL, y_true_col, y_pred_col)


def metrics_by_snapshot_day(frame: pd.DataFrame, y_true_col: str, y_pred_col: str) -> pd.DataFrame:
    """Accuracy broken down by intra-month snapshot day."""
    return _grouped(frame, SNAPSHOT_DAY_COL, y_true_col, y_pred_col)
