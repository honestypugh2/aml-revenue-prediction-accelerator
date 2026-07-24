# MLOps assets

Azure Machine Learning SDK v2 / CLI v2 assets for the accelerator. All commands
target your own workspace; nothing here runs automatically. Synthetic data only.

| Directory | Contents |
| --- | --- |
| `environments/` | Conda spec + AML environment definition |
| `components/` | Code-first training command component |
| `pipelines/` | Training pipeline job |
| `endpoints/` | Batch (default) and optional online endpoints/deployments |
| `monitoring/` | Model monitoring schedule (drift + data quality) |
| `schemas/` | Inference request/response JSON schema |

## Typical flow

```bash
# 1. Register the environment
az ml environment create -f mlops/environments/environment.yml -g <rg> -w <ws>

# 2. Register data (example)
az ml data create --name revenue_snapshots --type uri_file \
  --path data/synthetic/revenue_snapshots.parquet -g <rg> -w <ws>

# 3. Run the training pipeline
az ml job create -f mlops/pipelines/training-pipeline.yml -g <rg> -w <ws>

# 4. Register the champion model (from the completed run), then deploy:
az ml batch-endpoint create   -f mlops/endpoints/batch-endpoint.yml   -g <rg> -w <ws>
az ml batch-deployment create -f mlops/endpoints/batch-deployment.yml -g <rg> -w <ws> --set-default

# 5. (Optional) online endpoint — delete when idle
az ml online-endpoint create   -f mlops/endpoints/online-endpoint.yml   -g <rg> -w <ws>
az ml online-deployment create -f mlops/endpoints/online-deployment.yml -g <rg> -w <ws> --all-traffic
```

## AutoML

AutoML jobs are built in code via `revenue_prediction.automl` (see
[`notebooks/automl/`](../notebooks/automl/)). They use the same environment and
compute.

## Governance

Model registration, champion/challenger promotion, and monitoring integrate with
the guidance in [`docs/governance/`](../docs/governance/) and
[`docs/operations/`](../docs/operations/).
