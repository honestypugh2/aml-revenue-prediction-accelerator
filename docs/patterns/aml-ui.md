# Pattern 4 — Azure ML code-first via the Studio UI

Run the code-first training as a job **from Azure ML Studio** using the **Job
creation UI**, and compose components visually with the **Designer**. Same code,
authored through the portal — good for enablement and for teams not yet on CI/CD.

> All data is synthetic. Use a secure workspace for production.

## Option A — Job creation UI (command job)

1. **Studio → Authoring → Jobs → Create job (Command).**
2. **Code:** point to the [`src`](../../src/) folder (or an uploaded snapshot).
3. **Command:**
   ```
   python -m revenue_prediction.core.training.azureml_entry \
     --data ${{inputs.training_data}} --env dev --output ${{outputs.model_dir}}
   ```
4. **Environment:** select the registered `revenue-prediction-env` (from
   [`mlops/environments/environment.yml`](../../mlops/environments/environment.yml)).
5. **Inputs:** `training_data` → the registered net-revenue Data asset.
   **Outputs:** `model_dir` (uri_folder).
6. **Compute:** your CPU cluster. **Submit.**

The job trains all candidates with time-aware validation, selects the champion by
WAPE, and logs the MLflow model — identical to the SDK path.

## Option B — Designer (component pipeline)

1. Register the training component
   [`mlops/components/train_code_first.yml`](../../mlops/components/train_code_first.yml).
2. **Studio → Authoring → Designer → new pipeline.**
3. Drag the registered component onto the canvas, wire the **data asset** to its
   input and a **uri_folder** to its output, pick compute, and **Submit**.
4. Save the pipeline as a **draft/endpoint** to re-run on a schedule.

## Evaluate, register, hand off

- Open the completed job → **Metrics** / **Outputs + logs** / **Explanations**.
- **Register model** from the run.
- Continue with [../governance/model-governance.md](../governance/model-governance.md)
  and [../operations/inference-in-production.md](../operations/inference-in-production.md).

## References

- Create a training job with the Job creation UI
- Create and run component-based ML pipelines (UI / Designer)
