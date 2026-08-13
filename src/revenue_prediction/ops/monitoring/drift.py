"""Lightweight drift metrics used to prepare for Azure ML model monitoring.

These offline metrics let teams reason about input and prediction drift before
wiring up Azure ML's managed data-drift / model-monitoring signals. They are not
a replacement for the platform monitor; see ``docs/operations``.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd


def population_stability_index(expected: np.ndarray, actual: np.ndarray, bins: int = 10) -> float:
    """Population Stability Index (PSI) between two numeric distributions.

    PSI < 0.1 = negligible shift, 0.1-0.25 = moderate, > 0.25 = significant.
    """
    expected = np.asarray(expected, dtype=float)
    actual = np.asarray(actual, dtype=float)
    expected = expected[~np.isnan(expected)]
    actual = actual[~np.isnan(actual)]
    if expected.size == 0 or actual.size == 0:
        return float("nan")

    quantiles = np.linspace(0, 1, bins + 1)
    edges = np.unique(np.quantile(expected, quantiles))
    if edges.size < 2:
        return 0.0
    edges[0], edges[-1] = -np.inf, np.inf

    exp_counts, _ = np.histogram(expected, bins=edges)
    act_counts, _ = np.histogram(actual, bins=edges)
    exp_rate = np.clip(exp_counts / exp_counts.sum(), 1e-6, None)
    act_rate = np.clip(act_counts / act_counts.sum(), 1e-6, None)
    return float(np.sum((act_rate - exp_rate) * np.log(act_rate / exp_rate)))


@dataclass
class DriftReport:
    """Per-feature PSI report with an overall status."""

    feature_psi: dict[str, float]
    max_psi: float
    status: str  # "stable" | "moderate" | "drifted"


def _classify(max_psi: float) -> str:
    if np.isnan(max_psi):
        return "unknown"
    if max_psi < 0.1:
        return "stable"
    if max_psi < 0.25:
        return "moderate"
    return "drifted"


def prediction_drift_report(
    reference: pd.DataFrame,
    current: pd.DataFrame,
    columns: list[str],
) -> DriftReport:
    """Compute PSI for each column and summarize overall drift status."""
    feature_psi: dict[str, float] = {}
    for col in columns:
        if col in reference.columns and col in current.columns:
            feature_psi[col] = population_stability_index(
                reference[col].to_numpy(dtype=float),
                current[col].to_numpy(dtype=float),
            )
    valid = [v for v in feature_psi.values() if not np.isnan(v)]
    max_psi = max(valid) if valid else float("nan")
    return DriftReport(feature_psi=feature_psi, max_psi=max_psi, status=_classify(max_psi))
