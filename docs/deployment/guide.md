# Deployment guide

> Cloud steps are **opt-in** and require your own subscription and credentials.
> Nothing here runs automatically in CI. Never commit secrets or resource IDs.

## Paths

1. **Offline (no cloud):** `make data && make train` — full pipeline locally.
2. **Azure ML code-first:** submit a command job that runs the code-first
   trainer.
3. **Azure ML AutoML:** submit an AutoML regression job.
4. **Batch inference:** score data and write predictions (optionally to OneLake).
5. **Optional online endpoint:** managed online deployment for low-latency
   scoring.

## 0. Provision infrastructure

Pick a profile in [`infra/`](../../infra/):

- Quickstart (learning): `infra/terraform-quickstart/` or `infra/bicep/quickstart/`
- Secure (production-like): `infra/terraform/` or `infra/bicep/secure/`
- BYO VNet foundation: `infra/azure-ml-vnet/`

See [`infra/README.md`](../../infra/README.md) and
[`docs/security/networking.md`](../security/networking.md).

## 1. Configure

```bash
cp .env.example .env
# set RPA_AZURE_ML__SUBSCRIPTION_ID / RESOURCE_GROUP / WORKSPACE_NAME
uv sync --extra azure
az login
uv run revenue-prediction info --env dev   # verify configuration
```

## 2. Register data + environment

Upload the synthetic dataset as a data asset and register the training
environment from [`mlops/environments/`](../../mlops/environments/). Example
snippets are in [`notebooks/code_first/`](../../notebooks/code_first/) and
[`notebooks/automl/`](../../notebooks/automl/).

## 3. Submit training

- **Code-first:** `revenue_prediction.azureml.build_command_job(...)` then
  `ml_client.jobs.create_or_update(job)`.
- **AutoML:** `revenue_prediction.automl.build_regression_job(spec)` then submit.

Both log to MLflow (Azure ML tracking).

## 4. Register the champion

`revenue_prediction.azureml.register_model_from_run(...)` registers the MLflow
model produced by the run under `azure_ml.registered_model_name`.

## 5. Inference

- **Batch:** `revenue-prediction predict <bundle> <data>` locally, or an Azure ML
  batch endpoint/job in the cloud; write predictions to OneLake with
  `write_predictions_to_onelake(...)`.
- **Online (optional):** deploy the registered model to a managed online endpoint
  using [`mlops/endpoints/`](../../mlops/endpoints/). Delete it when idle.

## 6. Validate before deploying

Run pre-deployment checks: config, infra (Bicep/Terraform), RBAC/managed-identity
permissions, and prerequisites. See [`docs/deployment/checklist.md`](checklist.md).

## 7. Clean up

Follow [`docs/operations/cost-and-cleanup.md`](../operations/cost-and-cleanup.md).
