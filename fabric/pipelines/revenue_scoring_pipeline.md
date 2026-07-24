# Fabric Data Pipeline (design)

A conceptual design for orchestrating recurring net-revenue scoring in Microsoft
Fabric. Recreate this as a **Data Pipeline** in your Fabric workspace (pipeline
JSON is workspace-specific and is not committed with real identifiers).

## Activities

1. **Copy / ingest** — land the latest snapshot extract into the Lakehouse at
   `Files/revenue/input/` (from your source system or an upstream pipeline).
2. **Notebook: score** — run `fabric/notebooks/revenue_scoring_fabric.ipynb` to
   read inputs, load the registered/exported model, and write predictions to
   `Files/revenue/predictions/`.
3. **(Optional) Notebook: drift check** — compute PSI on key features and the
   prediction, using `revenue_prediction.monitoring`, and record results.
4. **Refresh semantic model** — trigger a DirectLake semantic model refresh so
   the Power BI report reflects new predictions.

## Schedule

- Run at each intra-month cutoff (e.g. days 7, 10, 12, 15, 18, 21, 24, 27) to
  refresh predictions as the month progresses. Scoring does **not** require
  retraining.

## Parameters (use Fabric pipeline parameters / variables)

| Parameter | Example | Notes |
| --- | --- | --- |
| `input_path` | `Files/revenue/input` | Lakehouse-relative |
| `predictions_path` | `Files/revenue/predictions` | Lakehouse-relative |
| `cutoff_day` | `15` | Snapshot day being scored |
| `model_uri` | registered model reference | Azure ML registry or Lakehouse |

## Governance

Retraining is a **separate** scheduled/triggered pipeline (see
[`docs/operations/retraining.md`](../../docs/operations/retraining.md)); this
pipeline only scores with the approved champion model.
