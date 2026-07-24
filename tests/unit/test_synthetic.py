"""Unit tests for the synthetic data generator."""

from __future__ import annotations

import pandas as pd
import pytest

from revenue_prediction.config.models import DataConfig
from revenue_prediction.data.schema import ALL_COLUMNS, FACILITY_COL, MONTH_COL, TARGET
from revenue_prediction.data.synthetic import generate_synthetic_dataset

pytestmark = pytest.mark.unit


def test_generator_is_deterministic() -> None:
    cfg = DataConfig(seed=123, n_facilities=3, n_months=15, snapshot_days=[10, 20])
    a = generate_synthetic_dataset(cfg)
    b = generate_synthetic_dataset(cfg)
    pd.testing.assert_frame_equal(a, b)


def test_generator_produces_expected_columns(dataset: pd.DataFrame) -> None:
    assert set(ALL_COLUMNS).issubset(dataset.columns)


def test_neutral_facility_identifiers(dataset: pd.DataFrame) -> None:
    assert dataset[FACILITY_COL].str.match(r"^FAC-\d{3}$").all()


def test_target_positive(dataset: pd.DataFrame) -> None:
    assert (dataset[TARGET] > 0).all()


def test_target_constant_within_facility_month(dataset: pd.DataFrame) -> None:
    counts = dataset.groupby([FACILITY_COL, MONTH_COL])[TARGET].nunique()
    assert (counts == 1).all()


def test_multiple_snapshots_per_facility_month(dataset: pd.DataFrame) -> None:
    per = dataset.groupby([FACILITY_COL, MONTH_COL])["snapshot_day"].nunique()
    assert (per > 1).all()


def test_history_length_respected() -> None:
    cfg = DataConfig(n_months=24)
    df = generate_synthetic_dataset(cfg)
    assert df[MONTH_COL].nunique() >= 24
