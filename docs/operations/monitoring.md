# Monitoring & drift

## Goals

Detect when the deployed model's inputs or predictions shift enough to warrant
attention or retraining, and prepare for Azure ML managed model monitoring.

## Offline drift metrics (included)

`revenue_prediction.ops.monitoring` provides:

- `population_stability_index(expected, actual, bins=10)` — PSI for a numeric
  distribution. Interpretation: `< 0.1` negligible, `0.1–0.25` moderate,
  `> 0.25` significant.
- `prediction_drift_report(reference, current, columns)` — per-feature PSI with
  an overall status (`stable` / `moderate` / `drifted`).

Use these to compare a recent scoring window against a reference (training)
window for key features and for the prediction itself.

## What to monitor

| Signal | Example |
| --- | --- |
| Input drift | PSI on `month_to_date_gross_charges`, payer mix, volumes |
| Prediction drift | PSI on `predicted_month_end_net_revenue` |
| Performance (post-close) | MAE/MAPE once actuals are known, overall and by facility/snapshot day |
| Data quality | Contract failures, rising missingness, new categories |
| Operational | Scoring latency, job failures, endpoint errors |

## Azure ML managed monitoring

For production, wire these into Azure Machine Learning **model monitoring** to
get scheduled data-drift, prediction-drift, and data-quality signals with alerts.
The offline metrics here are a lightweight bridge and a teaching tool, not a
replacement for the platform monitor. See the schema stubs under
[`mlops/monitoring/`](../../mlops/monitoring/).

## Continuous evaluation (predictions vs actuals)

Drift monitoring compares *distributions*; **continuous evaluation** measures
**realized accuracy** against ground truth once a month closes. It re-scores the
deployed champion's predictions against the known `actual_month_end_net_revenue`
and logs **WAPE/bias overall and by facility and snapshot day** to MLflow, so
degradation can trigger retraining.

Run it in the cloud as an Azure ML command component:

| Asset | Role |
| --- | --- |
| [`mlops/components/continuous_evaluation.yml`](../../mlops/components/continuous_evaluation.yml) | Command component (predictions + actuals → metrics report). |
| [`src/revenue_prediction/core/evaluation/azureml_evaluate.py`](../../src/revenue_prediction/core/evaluation/azureml_evaluate.py) | Entry point; reuses `core.evaluation.metrics`; logs `eval_*` metrics to MLflow. |

```bash
az ml component create -f mlops/components/continuous_evaluation.yml -g <rg> -w <workspace>
# Schedule it (e.g. monthly, after close) as a pipeline job; compare eval_wape
# across runs in the Azure ML job history / MLflow to see accuracy over time.
```

Because metrics land in MLflow (Azure ML tracking when run in the cloud), you
get a **continuous accuracy trend** per model version alongside the drift
signals above.

## Alerting

Route drift/quality alerts to your operations channel with the affected
facilities, the metric, and the window. Include `model_version` and `run_id`
from the prediction outputs to speed triage.
