# Pattern 3 — Azure ML code-first via the Python SDK v2

Train the champion with full control using **command jobs** and **pipeline
jobs**. This is the recommended production path for this use case.

> Requires the `azure` extra: `uv sync --extra azure`. Synthetic data only.

## Where it lives

- Workspace client: [`src/revenue_prediction/integrations/azureml/client.py`](../../src/revenue_prediction/integrations/azureml/client.py)
- Command job + registration: [`src/revenue_prediction/integrations/azureml/jobs.py`](../../src/revenue_prediction/integrations/azureml/jobs.py)
- Training entry point run on compute: [`src/revenue_prediction/core/training/azureml_entry.py`](../../src/revenue_prediction/core/training/azureml_entry.py)
- Component + pipeline: [`mlops/components/train_code_first.yml`](../../mlops/components/train_code_first.yml),
  [`mlops/pipelines/training-pipeline.yml`](../../mlops/pipelines/training-pipeline.yml),
  and the Python SDK pipeline [`mlops/pipelines/azureml_pipeline.py`](../../mlops/pipelines/azureml_pipeline.py)
- Environment: [`mlops/environments/environment.yml`](../../mlops/environments/environment.yml)
- Notebook: [`notebooks/code_first/`](../../notebooks/code_first/)

## Command job

```python
from revenue_prediction.config.loader import load_settings
from revenue_prediction.integrations.azureml.client import get_ml_client
from revenue_prediction.integrations.azureml.jobs import build_command_job

settings = load_settings("dev")
ml_client = get_ml_client(settings.azure_ml)
job = build_command_job(
    settings.azure_ml,
    training_data_asset="azureml:revenue_snapshots@latest",
    environment="azureml:revenue-prediction-env@latest",
)
submitted = ml_client.jobs.create_or_update(job)
```

The job runs `revenue_prediction.core.training.azureml_entry`, which trains all
candidates with **time-aware validation**, selects the champion by **WAPE**, and
logs the MLflow model.

## Pipeline job (SDK v2, `@pipeline`)

For multi-step (prep → train) reproducibility, use the DSL pipeline in
[`mlops/pipelines/azureml_pipeline.py`](../../mlops/pipelines/azureml_pipeline.py).
It composes components and is submitted the same way with `ml_client.jobs`.

## What makes this code-first path strong

- Explicit **leakage-safe** feature engineering (fit on train only).
- **Time-aware** splitting/backtesting (never random rows).
- **WAPE + bias**, disaggregated by facility and snapshot day.
- Full reproducibility for governance and CI/CD.

## Register & hand off

`register_model_from_run(...)` registers the MLflow model, then follow
[../governance/model-governance.md](../governance/model-governance.md) and
[../operations/inference-in-production.md](../operations/inference-in-production.md).

## References

- Train ML models (Azure ML, Python)
- Tutorial: Train a model; Tutorial: ML pipelines with the Python SDK v2
- Distributed GPU training (only if a future deep model warrants it — not the
  default here; see [../architecture/adr/0003-model-choice.md](../architecture/adr/0003-model-choice.md))
- Open-source foundation models / Healthcare AI models (extension points, not
  used for this structured-regression problem)
