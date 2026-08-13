"""Fully-offline end-to-end local pipeline.

Ties together: synthetic data (or provided data) -> contract + leakage checks ->
temporal split -> train all candidates -> compare -> select champion/challenger
-> package champion bundle. Optionally logs to MLflow (local file store).
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import pandas as pd

from revenue_prediction.config.models import Settings
from revenue_prediction.core.data.contracts import validate_leakage_rules, validate_raw_snapshots
from revenue_prediction.core.data.synthetic import generate_synthetic_dataset
from revenue_prediction.core.evaluation.selection import Selection, select_champion_challenger
from revenue_prediction.core.inference.predict import ModelBundle, save_bundle
from revenue_prediction.core.training.splitting import blocked_temporal_split
from revenue_prediction.core.training.train import TrainingResult, train_all_candidates


@dataclass
class LocalPipelineOutput:
    results: dict[str, TrainingResult]
    selection: Selection
    champion_bundle: ModelBundle
    comparison: pd.DataFrame
    bundle_path: Path | None = None


def run_local_pipeline(
    settings: Settings,
    frame: pd.DataFrame | None = None,
    output_dir: str | Path | None = None,
    track_mlflow: bool = False,
) -> LocalPipelineOutput:
    """Run the complete offline training + selection pipeline."""
    if frame is None:
        frame = generate_synthetic_dataset(settings.data)

    validate_raw_snapshots(frame)
    validate_leakage_rules(frame)

    split = blocked_temporal_split(frame, settings.split)
    results = train_all_candidates(split, settings.model, settings.features)
    selection = select_champion_challenger(
        results, settings.evaluation, metric=settings.model.primary_metric
    )

    if track_mlflow:
        _log_to_mlflow(results, selection, settings)

    champ = results[selection.champion]
    bundle = ModelBundle(
        model_name=champ.name,
        estimator=champ.estimator,
        feature_builder=champ.feature_builder,
    )

    bundle_path: Path | None = None
    if output_dir is not None:
        bundle_path = save_bundle(bundle, Path(output_dir) / "champion_bundle.joblib")

    return LocalPipelineOutput(
        results=results,
        selection=selection,
        champion_bundle=bundle,
        comparison=selection.ranking,
        bundle_path=bundle_path,
    )


def _log_to_mlflow(
    results: dict[str, TrainingResult], selection: Selection, settings: Settings
) -> None:
    try:
        import mlflow
    except ImportError:  # pragma: no cover
        return

    mlflow.set_experiment("revenue-local")
    for name, res in results.items():
        with mlflow.start_run(run_name=name):
            mlflow.log_params({"model": name, "environment": settings.environment})
            mlflow.log_metrics({f"test_{k}": v for k, v in res.metrics.items() if v == v})
            mlflow.set_tag("is_champion", name == selection.champion)
