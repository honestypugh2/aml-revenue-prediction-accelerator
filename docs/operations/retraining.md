# Retraining

## When to retrain

Retrain on an **approved schedule** or when a trigger fires:

1. **Drift** — input or prediction PSI crosses the `moderate`/`drifted`
   thresholds for sustained windows.
2. **Performance degradation** — post-close MAE/MAPE worsens beyond an agreed
   tolerance, overall or for specific facilities/snapshot days.
3. **Schema changes** — new/removed columns or changed semantics (caught by data
   contracts).
4. **Upstream-data changes** — source system, payer contracts, or coding changes
   that alter feature distributions.

Do **not** retrain reflexively on every new month; unnecessary retraining adds
risk and cost. Prefer scheduled retraining plus trigger-based exceptions.

## Retraining procedure

1. Refresh the training dataset (append newly-closed months). Re-run data
   contracts and leakage checks.
2. Re-run code-first candidates **and** AutoML on a time-aware split that
   includes the new months in the test block.
3. Compare the new champion candidate against the **incumbent** production model
   on the same held-out block.
4. Promote only if the challenger beats the incumbent by the configured margin
   *and* passes the Responsible AI review (see
   [`docs/governance/`](../governance/)).
5. Register, then deploy via the standard governed promotion path.

## Reproducibility

- Fixed seeds for synthetic data and models.
- MLflow captures parameters, metrics, and artifacts.
- Config profiles (`configs/`) and `uv.lock` pin the environment.

## Automation

CI validates every change offline. A scheduled pipeline (see
[`mlops/pipelines/`](../../mlops/pipelines/)) can orchestrate refresh → train →
compare → register in the cloud, leaving promotion as a human-approved gate.
