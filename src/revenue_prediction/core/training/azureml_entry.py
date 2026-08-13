"""Code-first training entry point (runs locally or on Azure ML compute).

This is the script executed by the Azure ML command job. It is also runnable
locally:

    python -m revenue_prediction.core.training.azureml_entry --data data/synthetic/revenue_snapshots.parquet --output outputs/model

It trains all code-first candidates using time-aware splitting, logs metrics and
the champion model to MLflow (Azure ML's tracking URI when running in the cloud;
a local file store otherwise), and writes the champion MLflow model to
``--output``.
"""

from __future__ import annotations

import argparse
from pathlib import Path

from revenue_prediction.config.loader import load_settings
from revenue_prediction.core.data.io import read_dataset


def main() -> None:
    parser = argparse.ArgumentParser(description="Code-first net-revenue training")
    parser.add_argument("--data", required=True, help="Path to snapshot dataset (parquet/csv)")
    parser.add_argument("--output", default="outputs/model", help="Model output directory")
    parser.add_argument("--env", default="dev", help="Config environment: dev|test|prod")
    args = parser.parse_args()

    import mlflow

    settings = load_settings(args.env)
    frame = read_dataset(args.data)

    from revenue_prediction.pipelines.local_pipeline import run_local_pipeline

    with mlflow.start_run(run_name="revenue-code-first"):
        result = run_local_pipeline(settings, frame=frame)
        mlflow.log_param("champion", result.selection.champion)
        mlflow.log_param("environment", settings.environment)
        champ = result.results[result.selection.champion]
        mlflow.log_metrics({f"test_{k}": v for k, v in champ.metrics.items() if v == v})

        # Log the champion estimator as an MLflow sklearn model.
        try:
            import mlflow.sklearn as mlflow_sklearn

            mlflow_sklearn.log_model(champ.estimator, artifact_path="model")
        except Exception as exc:  # pragma: no cover - defensive for exotic estimators
            mlflow.log_param("model_log_error", str(exc)[:250])

    out_dir = Path(args.output)
    out_dir.mkdir(parents=True, exist_ok=True)
    from revenue_prediction.core.inference.predict import save_bundle

    save_bundle(result.champion_bundle, out_dir / "champion_bundle.joblib")
    print(f"Champion: {result.selection.champion}; bundle written to {out_dir}")


if __name__ == "__main__":  # pragma: no cover
    main()
