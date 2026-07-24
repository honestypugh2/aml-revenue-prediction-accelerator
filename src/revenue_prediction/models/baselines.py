"""Simple, strong baselines for month-end net revenue.

These baselines operate directly on the historical features already present in
the snapshot data (which are leakage-safe: derived only from prior closed
months). They set the bar that learned models must beat.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.base import BaseEstimator, RegressorMixin


class _FeatureColumnBaseline(BaseEstimator, RegressorMixin):
    """Baseline that predicts a single historical feature column.

    Falls back to the training mean where the feature is missing.
    """

    feature: str = ""

    def fit(self, X: pd.DataFrame, y) -> _FeatureColumnBaseline:  # noqa: N803
        y_arr = np.asarray(y, dtype=float)
        self.fallback_ = float(np.nanmean(y_arr)) if len(y_arr) else 0.0
        return self

    def predict(self, X: pd.DataFrame) -> np.ndarray:  # noqa: N803
        if self.feature in X.columns:
            values = pd.to_numeric(X[self.feature], errors="coerce").to_numpy(dtype=float)
        else:
            values = np.full(len(X), np.nan)
        return np.where(np.isnan(values), self.fallback_, values)


class PriorPeriodNaive(_FeatureColumnBaseline):
    """Predict this month's net revenue as the prior month's net revenue."""

    feature = "prior_month_net_revenue"


class SeasonalNaive(_FeatureColumnBaseline):
    """Predict using the same month one year ago (seasonal naive)."""

    feature = "prior_year_same_month_net_revenue"
