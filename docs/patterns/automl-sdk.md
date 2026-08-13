# Pattern 2 — Automated ML via the Python SDK v2

Build and submit an AutoML **regression** job in code with `azure-ai-ml`.
Reproducible, reviewable, and CI/CD-friendly.

> Requires the `azure` extra: `uv sync --extra azure`. Synthetic data only.

## Where it lives

- Builder: [`src/revenue_prediction/integrations/automl/regression.py`](../../src/revenue_prediction/integrations/automl/regression.py)
  (`build_automl_job_spec`, `build_regression_job`, `submit_automl_job`).
- Notebook: [`notebooks/automl/01_automl_regression.ipynb`](../../notebooks/automl/01_automl_regression.ipynb).

## What the builder configures (aligned to Microsoft guidance)

`build_regression_job(spec)` creates an `azure.ai.ml.automl.regression` job with:

- `target_column_name = actual_month_end_net_revenue`
- `primary_metric` (default `normalized_root_mean_squared_error`)
- **`n_cross_validations`** — cross-validation to prevent overfitting
- **`set_featurization(mode="auto")`** — automatic encoding/imputation/scaling
  (helps with imbalanced/skewed inputs)
- **`enable_model_explainability=True`** — best-model explanations
- **`set_limits(..., enable_early_termination=True)`** — early stopping + trial
  and job timeouts

## Run it

```python
from revenue_prediction.config.loader import load_settings
from revenue_prediction.integrations.automl import build_automl_job_spec, build_regression_job
from revenue_prediction.integrations.azureml.client import get_ml_client

settings = load_settings("dev")
spec = build_automl_job_spec(
    settings.automl, settings.azure_ml,
    training_data_asset="azureml:revenue_snapshots_mltable@latest",
)
job = build_regression_job(spec)
ml_client = get_ml_client(settings.azure_ml)
submitted = ml_client.jobs.create_or_update(job)
print(submitted.studio_url)
```

## Evaluate

- Read the job's metrics and the best model's explanations via MLflow / Studio.
- Compare AutoML's best WAPE-equivalent against the code-first champion on the
  same time-aware test block.

## Register & hand off

Register the best model, then follow
[../governance/model-governance.md](../governance/model-governance.md) and
[../operations/inference-in-production.md](../operations/inference-in-production.md).

## References

- Set up AutoML with Python (v2)
- What is automated ML?
- Prevent overfitting and imbalanced data with Automated ML
- Evaluate AutoML experiment results
