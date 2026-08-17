"""Azure ML command-component entry point for batch scoring."""

from __future__ import annotations

import argparse
from pathlib import Path

from revenue_prediction.core.data.io import read_dataset


def main() -> None:
    parser = argparse.ArgumentParser(description="Score revenue snapshots with an MLflow model")
    parser.add_argument("--model", required=True, help="Downloaded MLflow model directory")
    parser.add_argument("--data", required=True, help="Snapshot dataset (parquet/csv)")
    parser.add_argument("--output", required=True, help="Output directory")
    args = parser.parse_args()

    import mlflow.pyfunc

    model = mlflow.pyfunc.load_model(args.model)
    predictions = model.predict(read_dataset(args.data))

    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)
    predictions.to_csv(output_dir / "predictions.csv", index=False)


if __name__ == "__main__":  # pragma: no cover
    main()