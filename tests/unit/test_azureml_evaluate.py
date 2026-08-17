"""Tests for the continuous-evaluation entry point (predictions vs actuals)."""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
import pytest

from revenue_prediction.core.evaluation.azureml_evaluate import PREDICTION_COL, main

pytestmark = pytest.mark.unit


def test_continuous_evaluation_writes_reports(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    keys = {
        "facility_id": ["FAC-001", "FAC-001", "FAC-002"],
        "accounting_month": ["2023-01", "2023-02", "2023-01"],
        "snapshot_date": ["2023-01-15", "2023-02-15", "2023-01-15"],
        "snapshot_day": [15, 15, 15],
    }
    predictions = pd.DataFrame({**keys, PREDICTION_COL: [1000.0, 2000.0, 3000.0]})
    actuals = pd.DataFrame({**keys, "actual_month_end_net_revenue": [1100.0, 1900.0, 3200.0]})

    pred_path = tmp_path / "predictions.csv"
    actual_path = tmp_path / "actuals.csv"
    out_dir = tmp_path / "report"
    predictions.to_csv(pred_path, index=False)
    actuals.to_csv(actual_path, index=False)

    monkeypatch.setattr(
        "sys.argv",
        [
            "azureml_evaluate",
            "--predictions",
            str(pred_path),
            "--actuals",
            str(actual_path),
            "--output",
            str(out_dir),
        ],
    )

    main()

    overall = json.loads((out_dir / "evaluation_overall.json").read_text())
    assert {"wape", "bias", "mae"}.issubset(overall)
    assert (out_dir / "evaluation_by_facility.csv").exists()
    assert (out_dir / "evaluation_by_snapshot_day.csv").exists()

    by_facility = pd.read_csv(out_dir / "evaluation_by_facility.csv")
    assert len(by_facility) == 2  # FAC-001 and FAC-002
