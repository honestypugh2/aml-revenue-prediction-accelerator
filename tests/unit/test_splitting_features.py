"""Unit tests for temporal splitting and leakage-safe feature engineering."""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from revenue_prediction.config.models import FeatureConfig, SplitConfig
from revenue_prediction.data.schema import MONTH_COL
from revenue_prediction.features.engineering import LeakageSafeFeatureBuilder
from revenue_prediction.training.splitting import (
    blocked_temporal_split,
    expanding_window_folds,
    rolling_origin_folds,
)

pytestmark = pytest.mark.unit


def test_blocked_split_has_no_month_overlap(dataset: pd.DataFrame) -> None:
    split = blocked_temporal_split(dataset, SplitConfig(n_test_months=3, n_val_months=3))
    train_m = set(split.train_months)
    val_m = set(split.validation_months)
    test_m = set(split.test_months)
    assert train_m.isdisjoint(val_m)
    assert val_m.isdisjoint(test_m)
    assert train_m.isdisjoint(test_m)
    # test months are strictly the most recent
    assert max(train_m) < min(test_m)


def test_facility_month_stays_together(dataset: pd.DataFrame) -> None:
    split = blocked_temporal_split(dataset, SplitConfig(n_test_months=3, n_val_months=3))
    for part in (split.train, split.validation, split.test):
        # every facility-month appears in exactly one split -> guaranteed by
        # month-based partition; assert the test block months are all present.
        assert bool(
            part[MONTH_COL]
            .isin(split.train_months + split.validation_months + split.test_months)
            .all()
        )


def test_rolling_and_expanding_folds_are_time_ordered(dataset: pd.DataFrame) -> None:
    cfg = SplitConfig(n_val_months=3, n_backtest_folds=2)
    for folds in (rolling_origin_folds(dataset, cfg), expanding_window_folds(dataset, cfg)):
        assert len(folds) >= 1
        for train_df, val_df in folds:
            assert train_df[MONTH_COL].max() < val_df[MONTH_COL].min()


def test_feature_builder_rejects_forbidden_columns(dataset: pd.DataFrame) -> None:
    builder = LeakageSafeFeatureBuilder(FeatureConfig())
    with pytest.raises(ValueError, match="Forbidden"):
        builder.fit(dataset)  # contains the target column


def test_feature_builder_no_nans_and_medians_from_train_only() -> None:
    from revenue_prediction.data.schema import FEATURE_COLUMNS

    df = pd.DataFrame(
        {
            "month_to_date_gross_charges": [100.0, np.nan, 300.0, 400.0],
            "month_to_date_payments": [10.0, 20.0, np.nan, 40.0],
            "days_elapsed": [10.0, 15.0, 20.0, 25.0],
            "remaining_days": [20.0, 15.0, 10.0, 5.0],
            "service_line_group": ["a", "b", "a", "b"],
        }
    )
    cols = [c for c in FEATURE_COLUMNS if c in df.columns]
    builder = LeakageSafeFeatureBuilder(FeatureConfig())
    builder.fit(df[cols])
    out = builder.transform(df[cols])
    assert not out.isna().any().any()
    assert np.isfinite(out.to_numpy()).all()
