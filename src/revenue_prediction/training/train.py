"""Local training orchestration for code-first candidates.

This module trains each candidate on a temporal split, evaluates on the held-out
test block, and returns structured results. It is MLflow-aware but MLflow logging
is optional so it can run fully offline.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import numpy as np
import pandas as pd

from ..config.models import FeatureConfig, ModelConfig
from ..data.schema import FEATURE_COLUMNS, TARGET
from ..evaluation.metrics import (
    compute_metrics,
    metrics_by_facility,
    metrics_by_snapshot_day,
)
from ..features.engineering import LeakageSafeFeatureBuilder
from ..models.factory import BASELINE_MODELS, build_estimator
from .splitting import TemporalSplit


@dataclass
class TrainingResult:
    """Outcome of training and evaluating a single candidate."""

    name: str
    estimator: Any
    feature_builder: LeakageSafeFeatureBuilder | None
    metrics: dict[str, float]
    predictions: pd.DataFrame
    by_facility: pd.DataFrame = field(default_factory=pd.DataFrame)
    by_snapshot_day: pd.DataFrame = field(default_factory=pd.DataFrame)


def _prepare_features(
    split: TemporalSplit, feature_config: FeatureConfig | None
) -> tuple[pd.DataFrame, pd.DataFrame, LeakageSafeFeatureBuilder]:
    keep = [c for c in FEATURE_COLUMNS if c in split.train.columns]
    builder = LeakageSafeFeatureBuilder(config=feature_config)
    builder.fit(split.train[keep])
    x_train = builder.transform(split.train[keep])
    x_test = builder.transform(split.test[[c for c in keep if c in split.test.columns]])
    return x_train, x_test, builder


def train_candidate(
    name: str,
    split: TemporalSplit,
    model_config: ModelConfig | None = None,
    feature_config: FeatureConfig | None = None,
) -> TrainingResult:
    """Train and evaluate one candidate model on ``split``."""
    model_config = model_config or ModelConfig()
    estimator = build_estimator(name, model_config)

    y_train = split.train[TARGET].to_numpy(dtype=float)
    y_test = split.test[TARGET].to_numpy(dtype=float)

    if name in BASELINE_MODELS:
        # Baselines consume raw historical columns directly.
        estimator.fit(split.train, y_train)
        preds = np.asarray(estimator.predict(split.test), dtype=float)
        builder = None
    else:
        x_train, x_test, builder = _prepare_features(split, feature_config)
        estimator.fit(x_train, y_train)
        preds = np.asarray(estimator.predict(x_test), dtype=float)

    pred_frame = split.test[
        [
            c
            for c in ["facility_id", "accounting_month", "snapshot_date", "snapshot_day"]
            if c in split.test.columns
        ]
    ].copy()
    pred_frame["y_true"] = y_test
    pred_frame["y_pred"] = preds

    metrics = compute_metrics(y_test, preds)
    return TrainingResult(
        name=name,
        estimator=estimator,
        feature_builder=builder,
        metrics=metrics,
        predictions=pred_frame,
        by_facility=metrics_by_facility(pred_frame, "y_true", "y_pred"),
        by_snapshot_day=metrics_by_snapshot_day(pred_frame, "y_true", "y_pred"),
    )


def train_all_candidates(
    split: TemporalSplit,
    model_config: ModelConfig | None = None,
    feature_config: FeatureConfig | None = None,
) -> dict[str, TrainingResult]:
    """Train every configured candidate and return a name -> result mapping."""
    model_config = model_config or ModelConfig()
    results: dict[str, TrainingResult] = {}
    for name in model_config.candidates:
        results[name] = train_candidate(name, split, model_config, feature_config)
    return results
