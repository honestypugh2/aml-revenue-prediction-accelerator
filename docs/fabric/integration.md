# Microsoft Fabric & OneLake integration

## Overview

The accelerator reads snapshot inputs from and writes predictions to a Microsoft
Fabric **Lakehouse** via **OneLake**. OneLake exposes an ADLS Gen2-compatible
endpoint, so we use `azure-storage-file-datalake` with `DefaultAzureCredential`.

- Client: `revenue_prediction.fabric.OneLakeClient`
- Writer: `revenue_prediction.fabric.write_predictions_to_onelake`

All identifiers are placeholders (`WORKSPACE_PLACEHOLDER`,
`LAKEHOUSE_PLACEHOLDER`) until supplied via environment variables.

## OneLake path convention

```
https://onelake.dfs.fabric.microsoft.com/<workspace>/<lakehouse>.Lakehouse/<path>
```

Defaults:

- input: `Files/revenue/input`
- predictions: `Files/revenue/predictions`

## Local fallback (offline demos and tests)

When credentials/the `fabric` extra are unavailable, or a `local_root` is
provided, the client transparently uses the local filesystem. This keeps demos,
workshops, and tests fully offline. The smoke test
`test_onelake_local_fallback` exercises this path.

## Power BI-ready output

Predictions are written as a **flat, typed Parquet table** with the primary
output (`predicted_month_end_net_revenue`), secondary outputs (model name and
version, run id, cutoff day, scoring timestamp), optional uncertainty bounds, and
the dimensions (`facility_id`, `accounting_month`, `snapshot_date`,
`snapshot_day`). A Fabric/Power BI **DirectLake** semantic model can consume this
table directly without copies.

## Recommended Fabric flow

1. Land raw or aggregated snapshots in the Lakehouse (`Files/revenue/input`).
2. Run inference (batch job or notebook) using a registered Azure ML model.
3. Write predictions to `Files/revenue/predictions`.
4. Build a DirectLake semantic model and Power BI report over the predictions.

See [`fabric/README.md`](../../fabric/README.md) and the notebooks under
[`fabric/notebooks/`](../../fabric/notebooks/) and
[`notebooks/fabric/`](../../notebooks/fabric/).

## Enabling live access

```bash
uv sync --extra fabric
export RPA_FABRIC__WORKSPACE_NAME="<your-workspace>"
export RPA_FABRIC__LAKEHOUSE_NAME="<your-lakehouse>"
az login   # DefaultAzureCredential picks this up
```

Never commit workspace or Lakehouse identifiers.
