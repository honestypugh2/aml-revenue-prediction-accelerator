"""Tests for the KPI / success-metric scorecard."""

from __future__ import annotations

import pandas as pd
import pytest

from revenue_prediction.core.evaluation.kpi import (
    DEFAULT_CHECKPOINT_TARGETS,
    beats_baseline,
    evaluate_checkpoint_targets,
    kpi_scorecard,
)

pytestmark = pytest.mark.unit


def _by_snapshot_day() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "snapshot_day": [10, 15, 21],
            "n": [30, 30, 30],
            "wape": [0.06, 0.03, 0.05],  # day 10 met (<=.07), day 15 met (<=.04), day 21 miss (>.04)
            "bias": [0.0, 0.0, 0.0],
        }
    )


def test_evaluate_checkpoint_targets_verdicts() -> None:
    board = evaluate_checkpoint_targets(_by_snapshot_day())
    verdict = dict(zip(board["snapshot_day"], board["met"], strict=False))
    assert verdict[10] is True
    assert verdict[15] is True
    assert verdict[21] is False


def test_beats_baseline_kpi() -> None:
    result = beats_baseline(champion_wape=0.035, baseline_wape=0.06)
    assert result.met is True
    assert result.margin == pytest.approx(0.025, abs=1e-6)


def test_kpi_scorecard_includes_baseline_row() -> None:
    board = kpi_scorecard({"wape": 0.035}, _by_snapshot_day(), baseline_wape=0.06)
    assert "Beat manual analyst baseline" in set(board["checkpoint"])
    assert len(board) == len(DEFAULT_CHECKPOINT_TARGETS) + 1
