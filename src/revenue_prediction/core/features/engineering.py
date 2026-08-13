"""Leakage-safe feature builder implemented as a scikit-learn transformer."""

from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.base import BaseEstimator, TransformerMixin

from revenue_prediction.config.models import FeatureConfig
from revenue_prediction.core.data.schema import (
    DIMENSION_COLUMNS,
    FEATURE_COLUMNS,
    HISTORICAL_FEATURES,
    OPERATIONAL_FEATURES,
)


class LeakageSafeFeatureBuilder(BaseEstimator, TransformerMixin):
    """Build model-ready features without leaking future information.

    Fitting learns:

    * numeric medians (for imputation),
    * the observed categories for each categorical column (for stable one-hot
      encoding across splits).

    ``transform`` derives a couple of safe ratio features from partial-month
    values, imputes, and one-hot encodes.
    """

    def __init__(self, config: FeatureConfig | None = None) -> None:
        self.config = config or FeatureConfig()

    # -- sklearn API --------------------------------------------------------
    def fit(self, X: pd.DataFrame, y: pd.Series | None = None) -> LeakageSafeFeatureBuilder:
        self._validate_no_forbidden(X)
        enriched = self._add_derived_features(X.copy())
        numeric = [
            c
            for c in OPERATIONAL_FEATURES + HISTORICAL_FEATURES + self._derived_names()
            if c in enriched.columns
        ]
        self.numeric_columns_: list[str] = numeric
        self.medians_: dict[str, float] = {}
        for c in numeric:
            arr = pd.to_numeric(enriched[c], errors="coerce").to_numpy(dtype=float)
            arr = arr[np.isfinite(arr)]
            # Fill any all-NaN column median with 0.0 to remain deterministic
            # (and to avoid a "Mean of empty slice" warning).
            self.medians_[c] = float(np.median(arr)) if arr.size else 0.0
        self.categories_: dict[str, list[str]] = {
            c: sorted(X[c].dropna().astype(str).unique().tolist())
            for c in DIMENSION_COLUMNS
            if c in X.columns
        }
        self.feature_names_out_: list[str] | None = None
        return self

    def transform(self, X: pd.DataFrame) -> pd.DataFrame:
        self._validate_no_forbidden(X)
        frame = X.copy()
        frame = self._add_derived_features(frame)

        # Impute numeric (operational, historical, and derived) using training
        # medians, and neutralise any residual infinities.
        for col in self.numeric_columns_:
            if col in frame.columns:
                arr = pd.to_numeric(frame[col], errors="coerce").to_numpy(dtype=float)
                frame[col] = np.where(np.isfinite(arr), arr, self.medians_[col])

        # One-hot encode with stable categories.
        encoded_parts: list[pd.DataFrame] = []
        for col, cats in self.categories_.items():
            series = (
                frame[col].astype(str) if col in frame.columns else pd.Series([""] * len(frame))
            )
            for cat in cats:
                encoded_parts.append(
                    pd.Series(
                        (series == cat).astype(float), name=f"{col}__{cat}", index=frame.index
                    )
                )

        numeric_out = [c for c in self.numeric_columns_ if c in frame.columns]
        out = frame[numeric_out].copy()
        if encoded_parts:
            out = pd.concat([out] + encoded_parts, axis=1)

        out = out.astype(float)
        self.feature_names_out_ = out.columns.tolist()
        return out

    def get_feature_names_out(self, input_features=None) -> np.ndarray:  # noqa: ARG002
        if self.feature_names_out_ is None:
            raise RuntimeError("transform must be called before get_feature_names_out")
        return np.asarray(self.feature_names_out_, dtype=object)

    # -- helpers ------------------------------------------------------------
    @staticmethod
    def _derived_names() -> list[str]:
        return [
            "mtd_collection_ratio",
            "mtd_denial_ratio",
            "mtd_adjustment_ratio",
            "mtd_gross_run_rate",
            "fraction_month_elapsed",
        ]

    def _add_derived_features(self, frame: pd.DataFrame) -> pd.DataFrame:
        eps = 1.0

        def col(name: str) -> np.ndarray:
            if name in frame.columns:
                return pd.to_numeric(frame[name], errors="coerce").to_numpy(dtype=float)
            return np.full(len(frame), np.nan, dtype=float)

        gross = col("month_to_date_gross_charges")
        payments = col("month_to_date_payments")
        denials = col("month_to_date_denials")
        adjustments = col("month_to_date_contractual_adjustments")
        days_elapsed = col("days_elapsed")
        remaining = col("remaining_days")

        total_days = days_elapsed + remaining
        total_days = np.where(total_days == 0, np.nan, total_days)

        frame["mtd_collection_ratio"] = payments / (gross + eps)
        frame["mtd_denial_ratio"] = denials / (gross + eps)
        frame["mtd_adjustment_ratio"] = adjustments / (gross + eps)
        frame["fraction_month_elapsed"] = days_elapsed / total_days
        frame["mtd_gross_run_rate"] = gross / (days_elapsed + eps)
        return frame

    def _validate_no_forbidden(self, X: pd.DataFrame) -> None:
        present = [c for c in self.config.forbidden_future_columns if c in X.columns]
        if present:
            raise ValueError(
                "Forbidden future/leakage columns present in feature input: "
                f"{present}. These are only known after accounting close."
            )


def build_feature_frame(
    train: pd.DataFrame,
    *frames: pd.DataFrame,
    config: FeatureConfig | None = None,
) -> tuple[pd.DataFrame, ...]:
    """Fit a :class:`LeakageSafeFeatureBuilder` on ``train`` and transform all.

    Only the training frame influences the fitted statistics. Returns the
    transformed frames in the same order (train first).
    """
    keep = [c for c in FEATURE_COLUMNS if c in train.columns]
    builder = LeakageSafeFeatureBuilder(config=config)
    builder.fit(train[keep])
    outputs = [builder.transform(train[keep])]
    for frame in frames:
        cols = [c for c in keep if c in frame.columns]
        outputs.append(builder.transform(frame[cols]))
    return tuple(outputs)
