"""Unit tests for explainability and inference bundle save/load."""

from __future__ import annotations

from pathlib import Path

import pytest

from revenue_prediction.config.loader import load_settings
from revenue_prediction.data.schema import FEATURE_COLUMNS, TARGET
from revenue_prediction.data.synthetic import generate_synthetic_dataset
from revenue_prediction.evaluation.explainability import (
    native_feature_importance,
    permutation_feature_importance,
)
from revenue_prediction.inference.predict import (
    ModelBundle,
    batch_predict,
    load_bundle,
    save_bundle,
)
from revenue_prediction.training.splitting import blocked_temporal_split
from revenue_prediction.training.train import train_candidate

pytestmark = pytest.mark.unit


def _trained():
    settings = load_settings("test")
    df = generate_synthetic_dataset(settings.data)
    split = blocked_temporal_split(df, settings.split)
    result = train_candidate("hist_gradient_boosting", split, settings.model, settings.features)
    return settings, df, split, result


def test_permutation_importance_ranks_features() -> None:
    _settings, _df, split, result = _trained()
    assert result.feature_builder is not None
    keep = [c for c in FEATURE_COLUMNS if c in split.test.columns]
    X_test = result.feature_builder.transform(split.test[keep])
    y_test = split.test[TARGET]
    imp = permutation_feature_importance(result.estimator, X_test, y_test, n_repeats=3)
    assert list(imp.columns) == ["feature", "importance_mean", "importance_std"]
    assert imp["importance_mean"].is_monotonic_decreasing


def test_native_importance_optional() -> None:
    _settings, _df, split, result = _trained()
    assert result.feature_builder is not None
    names = list(result.feature_builder.get_feature_names_out())
    # HistGradientBoosting has no feature_importances_ -> None; that's acceptable.
    native = native_feature_importance(result.estimator, names)
    assert native is None or set(native.columns) == {"feature", "importance"}


def test_bundle_save_load_and_score(tmp_path: Path) -> None:
    settings, df, _split, result = _trained()
    bundle = ModelBundle(
        model_name=result.name,
        estimator=result.estimator,
        feature_builder=result.feature_builder,
    )
    path = save_bundle(bundle, tmp_path / "b.joblib")
    reloaded = load_bundle(path)
    preds = batch_predict(reloaded, df, cutoff_day=15)
    assert len(preds) == len(df)
    assert (preds["model_version"] == bundle.model_version).all()
    assert (preds["run_id"] == bundle.run_id).all()
