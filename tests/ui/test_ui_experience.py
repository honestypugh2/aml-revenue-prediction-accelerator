"""Tests for the UI logic layer (framework-agnostic; no web runtime required)."""

from __future__ import annotations

import pytest

from revenue_prediction.ui.experience import (
    build_comparison_view,
    build_dataset_overview,
    facility_month_series,
    load_experience,
    run_training_experience,
)

pytestmark = pytest.mark.ui


def test_load_experience_and_overview() -> None:
    state = load_experience("test")
    overview = build_dataset_overview(state)
    assert overview["rows"] > 0
    assert len(overview["facilities"]) == 3
    assert overview["target_max"] >= overview["target_min"]


def test_facility_series_is_monthly() -> None:
    state = load_experience("test")
    facility = build_dataset_overview(state)["facilities"][0]
    series = facility_month_series(state, facility)
    assert list(series.columns) == ["accounting_month", "actual_month_end_net_revenue"]
    assert series["accounting_month"].is_monotonic_increasing


def test_training_experience_produces_comparison() -> None:
    state = load_experience("test")
    output = run_training_experience(state)
    table = build_comparison_view(output)
    assert "is_champion" in table.columns
    assert table["is_champion"].sum() == 1
