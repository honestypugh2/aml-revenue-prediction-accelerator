"""End-to-end offline smoke tests covering the full pipeline."""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest

from revenue_prediction.config.loader import load_settings
from revenue_prediction.core.data.io import materialise_default_datasets, read_dataset
from revenue_prediction.core.inference.predict import batch_predict, load_bundle
from revenue_prediction.pipelines.local_pipeline import run_local_pipeline

pytestmark = pytest.mark.smoke


def test_full_pipeline_selects_champion_and_scores(tmp_path: Path) -> None:
    settings = load_settings("test")
    output = run_local_pipeline(settings, output_dir=tmp_path)

    # A champion and challenger were selected.
    assert output.selection.champion in output.results
    assert output.selection.challenger is None or output.selection.challenger in output.results

    # Champion bundle was written and can be reloaded and used to score.
    assert output.bundle_path is not None and output.bundle_path.exists()
    bundle = load_bundle(output.bundle_path)

    from revenue_prediction.core.data.synthetic import generate_synthetic_dataset

    frame = generate_synthetic_dataset(settings.data)
    predictions = batch_predict(bundle, frame, cutoff_day=15)

    assert "predicted_month_end_net_revenue" in predictions.columns
    assert "model_version" in predictions.columns
    assert "run_id" in predictions.columns
    assert "scored_at" in predictions.columns
    assert len(predictions) == len(frame)


def test_materialise_datasets_roundtrip(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    settings = load_settings("test")
    settings.data.raw_dir = tmp_path / "synthetic"
    settings.data.sample_dir = tmp_path / "sample"
    outputs = materialise_default_datasets(settings.data)
    for path in outputs.values():
        assert path.exists()
    reloaded = read_dataset(outputs["synthetic"])
    assert len(reloaded) > 0


def test_reasonable_accuracy_on_dev_config(tmp_path: Path) -> None:
    # With more data (dev), the best model should achieve a low MAPE.
    settings = load_settings("dev")
    output = run_local_pipeline(settings, output_dir=tmp_path)
    best_mape = output.comparison["mape"].min()
    assert best_mape < 0.25  # < 25% error for the strongest candidate


def test_onelake_local_fallback(tmp_path: Path) -> None:
    from revenue_prediction.integrations.fabric.onelake import write_predictions_to_onelake

    settings = load_settings("test")
    df = pd.DataFrame({"facility_id": ["FAC-001"], "predicted_month_end_net_revenue": [1.0]})
    written = write_predictions_to_onelake(df, settings.fabric, local_root=tmp_path)
    assert Path(written).exists()
