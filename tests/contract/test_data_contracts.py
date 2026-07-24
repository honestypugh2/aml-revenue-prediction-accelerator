"""Data-contract tests: valid data passes, invalid data is rejected."""

from __future__ import annotations

import pandas as pd
import pytest

from revenue_prediction.data.contracts import (
    ContractViolation,
    validate_leakage_rules,
    validate_raw_snapshots,
)
from revenue_prediction.data.io import build_invalid_sample

pytestmark = pytest.mark.contract


def test_valid_data_passes_schema(dataset: pd.DataFrame) -> None:
    validated = validate_raw_snapshots(dataset)
    assert len(validated) == len(dataset)


def test_valid_data_passes_leakage_rules(dataset: pd.DataFrame) -> None:
    validate_leakage_rules(dataset)


def test_invalid_sample_fails_schema(dataset: pd.DataFrame) -> None:
    invalid = build_invalid_sample(dataset)
    with pytest.raises(ContractViolation):
        validate_raw_snapshots(invalid)


def test_days_elapsed_leakage_detected(dataset: pd.DataFrame) -> None:
    tampered = dataset.copy()
    # Simulate future information: days_elapsed beyond snapshot_day.
    tampered.loc[tampered.index[0], "days_elapsed"] = 99.0
    with pytest.raises(ContractViolation, match="days_elapsed"):
        validate_leakage_rules(tampered)


def test_target_variation_within_month_detected(dataset: pd.DataFrame) -> None:
    tampered = dataset.copy()
    idx = tampered.index[0]
    tampered.loc[idx, "actual_month_end_net_revenue"] += 1234.0
    with pytest.raises(ContractViolation, match="target varies"):
        validate_leakage_rules(tampered)


def test_inference_data_without_target_passes(dataset: pd.DataFrame) -> None:
    inference = dataset.drop(columns=["actual_month_end_net_revenue"])
    validate_raw_snapshots(inference, require_target=False)
