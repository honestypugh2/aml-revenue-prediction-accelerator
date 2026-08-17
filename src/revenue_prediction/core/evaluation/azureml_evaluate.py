"""Azure ML command-component entry point for continuous evaluation.

Continuous evaluation compares **already-scored predictions** against the
**actual** month-end net revenue that becomes known after accounting close, and
logs WAPE/bias (overall and disaggregated by facility and snapshot day) to
MLflow. This is distinct from drift monitoring: drift compares input/prediction
*distributions*; continuous evaluation measures realized accuracy against ground
truth so degradation can trigger retraining.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from revenue_prediction.core.data.io import read_dataset
from revenue_prediction.core.data.schema import KEY_COLUMNS, TARGET
from revenue_prediction.core.evaluation.kpi import kpi_scorecard
from revenue_prediction.core.evaluation.metrics import (
    compute_metrics,
    metrics_by_facility,
    metrics_by_snapshot_day,
)

PREDICTION_COL = "predicted_month_end_net_revenue"


def main() -> None:
    parser = argparse.ArgumentParser(description="Continuous evaluation: predictions vs actuals")
    parser.add_argument("--predictions", required=True, help="Scored predictions (parquet/csv)")
    parser.add_argument("--actuals", required=True, help="Closed-month actuals (parquet/csv)")
    parser.add_argument("--output", required=True, help="Output directory for the metrics report")
    parser.add_argument(
        "--baseline-wape",
        type=float,
        default=None,
        help="Manual-analyst baseline WAPE (fraction) for the beat-baseline KPI",
    )
    args = parser.parse_args()

    predictions = read_dataset(args.predictions)
    actuals = read_dataset(args.actuals)

    join_keys = [c for c in KEY_COLUMNS if c in predictions.columns and c in actuals.columns]
    merged = predictions.merge(actuals[[*join_keys, TARGET]], on=join_keys, how="inner")
    if merged.empty:
        raise ValueError("No overlapping keys between predictions and actuals to evaluate.")

    overall = compute_metrics(merged[TARGET], merged[PREDICTION_COL])
    by_facility = metrics_by_facility(merged, TARGET, PREDICTION_COL)
    by_snapshot_day = metrics_by_snapshot_day(merged, TARGET, PREDICTION_COL)
    scorecard = kpi_scorecard(overall, by_snapshot_day, baseline_wape=args.baseline_wape)

    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "evaluation_overall.json").write_text(json.dumps(overall, indent=2))
    by_facility.to_csv(output_dir / "evaluation_by_facility.csv", index=False)
    by_snapshot_day.to_csv(output_dir / "evaluation_by_snapshot_day.csv", index=False)
    scorecard.to_csv(output_dir / "kpi_scorecard.csv", index=False)

    try:
        import mlflow

        mlflow.log_metrics({f"eval_{k}": v for k, v in overall.items() if v == v})
        mlflow.log_metric("eval_n", int(len(merged)))
        mlflow.log_metric("kpi_targets_met", int(scorecard["met"].sum()) if not scorecard.empty else 0)
    except Exception:  # pragma: no cover - MLflow optional / offline
        pass


if __name__ == "__main__":  # pragma: no cover
    main()
