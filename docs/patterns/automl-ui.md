# Pattern 1 — Automated ML via the Studio UI

Train the net-revenue model with the **Automated ML wizard** in Azure ML Studio
— no code. Best for analysts, enablement, and quick benchmarking.

> All data is synthetic. Run against a secure workspace for production
> ([../security/networking.md](../security/networking.md)).

## Prerequisites

- An Azure ML workspace and a compute cluster (see [`infra/`](../../infra/)).
- The training data registered as a **Data asset** (MLTable or tabular). Create
  the MLTable locally with [`notebooks/automl/`](../../notebooks/automl/) and
  register it, or upload `data/synthetic/revenue_snapshots.parquet`.

## Steps (Studio → Automated ML)

1. **Studio → Authoring → Automated ML → New Automated ML job.**
2. **Task type:** *Regression*.
3. **Data asset:** select the registered net-revenue dataset.
4. **Target column:** `actual_month_end_net_revenue`.
5. **Compute:** select your CPU cluster.
6. **Validation & limits:**
   - Validation type: **k-fold cross-validation** (e.g. 5 folds) — this is the
     primary guard against overfitting.
   - Set a job timeout and **enable early termination**.
7. **Featurization:** leave **Auto** on (handles encoding, imputation, and
   scaling; helps with imbalanced/skewed inputs).
8. **(Recommended) Additional settings:** set the **primary metric**
   (e.g. *Normalized root mean squared error*) and enable **model
   explainability**.
9. **Submit** and watch the leaderboard.

## Evaluate results

- Open the best run → **Metrics** and **Explanations** tabs.
- Compare the leaderboard's best model against the code-first champion's WAPE on
  the same test period.
- Review **model explainability** (top features) — it should agree with the
  code-first drivers (volume, gross charges, prior net revenue).

## Overfitting & imbalanced data (what the UI does for you)

Per Microsoft's guidance, AutoML mitigates these via **cross-validation**,
**automatic featurization**, and **early termination** — all set above. Also
watch for a large train/validation gap on the best run as an overfitting signal.

## Register & hand off

From the best run, **Register model**. From here it follows the same governance,
deployment, and monitoring path as every other pattern
([../governance/model-governance.md](../governance/model-governance.md),
[../operations/inference-in-production.md](../operations/inference-in-production.md)).

## References

- Set up AutoML for tabular data in the studio
- Evaluate AutoML experiment results
- Prevent overfitting and imbalanced data with Automated ML
