"""Tests for the portable MLflow inference model."""

from __future__ import annotations

from pathlib import Path

import mlflow.pyfunc
import pandas as pd
import pytest

from revenue_prediction.config.loader import load_settings
from revenue_prediction.core.data.synthetic import generate_synthetic_dataset
from revenue_prediction.core.inference.azureml_batch_score import main as batch_score_main
from revenue_prediction.core.inference.mlflow_model import RevenuePredictionModel
from revenue_prediction.pipelines.local_pipeline import run_local_pipeline

pytestmark = pytest.mark.unit


def test_mlflow_model_scores_raw_snapshots(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    settings = load_settings("test")
    frame = generate_synthetic_dataset(settings.data)
    output = run_local_pipeline(settings, frame=frame)
    checkpoint = frame.drop(columns=["actual_month_end_net_revenue"]).tail(4)

    model_path = tmp_path / "model"
    mlflow.pyfunc.save_model(
        path=model_path,
        python_model=RevenuePredictionModel(output.champion_bundle),
    )
    model = mlflow.pyfunc.load_model(model_path)
    predictions = model.predict(checkpoint)

    assert isinstance(predictions, pd.DataFrame)
    assert len(predictions) == len(checkpoint)
    assert predictions["predicted_month_end_net_revenue"].notna().all()
    assert {"model_version", "run_id", "scored_at"}.issubset(predictions.columns)

    input_path = tmp_path / "checkpoint.csv"
    output_path = tmp_path / "predictions"
    checkpoint.to_csv(input_path, index=False)
    monkeypatch.setattr(
        "sys.argv",
        [
            "azureml_batch_score",
            "--model",
            str(model_path),
            "--data",
            str(input_path),
            "--output",
            str(output_path),
        ],
    )

    batch_score_main()

    batch_predictions = pd.read_csv(output_path / "predictions.csv")
    assert len(batch_predictions) == len(checkpoint)
    assert batch_predictions["predicted_month_end_net_revenue"].notna().all()