"""Unit tests for metrics, selection, monitoring, and security helpers."""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from revenue_prediction.evaluation.metrics import (
    bias,
    compute_metrics,
    metrics_by_snapshot_day,
    smape,
    wape,
)
from revenue_prediction.monitoring.drift import (
    population_stability_index,
    prediction_drift_report,
)
from revenue_prediction.security.redaction import redact, scan_for_neutrality_violations

pytestmark = pytest.mark.unit


def test_compute_metrics_perfect_prediction() -> None:
    y = np.array([1.0, 2.0, 3.0, 4.0])
    m = compute_metrics(y, y)
    assert m["mae"] == 0
    assert m["rmse"] == 0
    assert m["r2"] == pytest.approx(1.0)
    assert m["wape"] == pytest.approx(0.0)
    assert m["bias"] == pytest.approx(0.0)


def test_wape_is_dollar_weighted() -> None:
    y_true = np.array([100.0, 900.0])
    y_pred = np.array([110.0, 990.0])  # +10% on each -> WAPE = 10%
    assert wape(y_true, y_pred) == pytest.approx(0.10)
    # A small facility's large % error cannot dominate the dollar-weighted score.
    y_true2 = np.array([10.0, 9990.0])
    y_pred2 = np.array([20.0, 9990.0])  # 100% error on the tiny facility only
    assert wape(y_true2, y_pred2) < 0.01


def test_bias_sign() -> None:
    y_true = np.array([100.0, 100.0])
    assert bias(y_true, np.array([110.0, 110.0])) == pytest.approx(0.10)  # over-forecast
    assert bias(y_true, np.array([90.0, 90.0])) == pytest.approx(-0.10)  # under-forecast


def test_smape_bounded() -> None:
    y_true = np.array([100.0, 200.0])
    y_pred = np.array([110.0, 190.0])
    assert 0 <= smape(y_true, y_pred) <= 2


def test_metrics_by_snapshot_day_groups() -> None:
    frame = pd.DataFrame(
        {
            "snapshot_day": [10, 10, 20, 20],
            "y_true": [100.0, 200.0, 300.0, 400.0],
            "y_pred": [110.0, 190.0, 330.0, 360.0],
        }
    )
    out = metrics_by_snapshot_day(frame, "y_true", "y_pred")
    assert set(out["snapshot_day"]) == {10, 20}


def test_psi_zero_for_identical() -> None:
    rng = np.random.default_rng(0)
    x = rng.normal(size=1000)
    assert population_stability_index(x, x) == pytest.approx(0.0, abs=1e-9)


def test_psi_flags_shift() -> None:
    rng = np.random.default_rng(0)
    ref = pd.DataFrame({"f": rng.normal(0, 1, 2000)})
    cur = pd.DataFrame({"f": rng.normal(3, 1, 2000)})
    report = prediction_drift_report(ref, cur, ["f"])
    assert report.status in {"moderate", "drifted"}
    assert report.max_psi > 0.1


def test_redaction_masks_secrets() -> None:
    text = "key=AccountKey=abc123; email a@b.com guid 12345678-1234-1234-1234-1234567890ab"
    redacted = redact(text)
    assert "abc123" not in redacted
    assert "a@b.com" not in redacted
    assert "12345678-1234-1234-1234-1234567890ab" not in redacted


def test_neutrality_scan_detects_violations() -> None:
    assert "email" in scan_for_neutrality_violations("contact me at x@y.org")
    assert scan_for_neutrality_violations("FAC-001 clean text") == []
