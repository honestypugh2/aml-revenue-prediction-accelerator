# End-to-end demo script — Azure Machine Learning

A complete **talking track** for demonstrating the accelerator end-to-end on
**Azure Machine Learning**: from partial-month data to a governed, deployed,
monitored month-end net-revenue model — across all **four authoring patterns**.

> [!IMPORTANT]
> All data is **synthetic**; all identifiers are **placeholders**
> (`FAC-001`, `WORKSPACE_PLACEHOLDER`, `LAKEHOUSE_PLACEHOLDER`). This is
> operational decision support and financial forecasting — not clinical
> decision support, financial advice, or a production-ready solution. Everything
> shown must be reviewed by qualified finance, data, security, privacy,
> compliance, and operational stakeholders before real use.

Format for each beat: **Say** (narration) · **Do** (actions) · **Show** (what's
on screen).

---

## 0. Audience, outcomes, and timing

**Who this is for:** data scientists, ML/platform engineers, and analytics
leaders evaluating an Azure ML + Microsoft Fabric approach to early revenue
forecasting.

**What they'll leave believing:**

1. The problem is framed correctly (partial-month → month-end, leakage-safe).
2. Azure ML supports **four** ways to author the same governed model.
3. The lifecycle (MLOps v2) is real: register → gate → deploy → monitor →
   retrain.
4. The teaching layer makes the process learnable, not a black box.

**Timing (flexible):**

| Segment | Full (60 min) | Short (25 min) |
| --- | --- | --- |
| Frame the problem | 5 | 3 |
| Build & Learn UI (process) | 12 | 6 |
| Register data + environment | 5 | skip (pre-done) |
| Pattern 2 — AutoML SDK (baseline) | 8 | 4 |
| Pattern 3 — code-first SDK (champion) | 10 | 5 |
| Patterns 1 & 4 — UI parity | 5 | mention only |
| Evaluate, register, gate | 6 | 3 |
| Deploy batch + score a checkpoint | 6 | 2 |
| OneLake → Power BI + monitoring | 3 | 2 |
| Close + cleanup | remaining | remaining |

> **Golden rule for a live demo:** pre-provision infrastructure, pre-register the
> data asset and environment, and (optionally) pre-run the long AutoML/code-first
> jobs so you can *open completed runs* instead of waiting. The script calls out
> exactly where to do this.

---

## 1. Pre-demo checklist (do this before the audience arrives)

**Do:**

```bash
# Backend + Azure SDK extras
uv sync --extra api --extra azure

# Build the React UI once so `serve` can host it at a single URL
npm --prefix frontend install && npm --prefix frontend run build

# Generate the synthetic dataset and a quick local model
uv run revenue-prediction generate-data
uv run revenue-prediction train-local

# Azure auth + config sanity check
cp .env.example .env   # set RPA_AZURE_ML__SUBSCRIPTION_ID / RESOURCE_GROUP / WORKSPACE_NAME
az login
uv run revenue-prediction info --env dev
```

**Pre-provision** a workspace (choose a profile in [`infra/`](../../infra/)):

- Learning/demo: [`infra/terraform-quickstart/`](../../infra/terraform-quickstart/) or [`infra/bicep/`](../../infra/bicep/) (quickstart param).
- Production-like secure managed-VNet: [`infra/terraform/`](../../infra/terraform/) or `infra/bicep` (secure param) — see [security/networking.md](../security/networking.md).

**Pre-stage on Azure ML** (so the demo is click-not-wait):

- Register the dataset as a **Data asset** (Parquet for code-first; **MLTable**
  for AutoML) — snippets in [`notebooks/code_first/`](../../notebooks/code_first/) and [`notebooks/automl/`](../../notebooks/automl/).
- Register the training **environment** from [`mlops/environments/environment.yml`](../../mlops/environments/environment.yml).
- Optionally submit the AutoML and code-first jobs an hour ahead so their runs
  are **Completed** when you present.

**Fallback:** if connectivity fails, the entire **offline path runs with no
cloud** (`make data && make train`, plus the Build & Learn UI). See §11.

---

## 2. Frame the problem  · 5 min

**Say:** "Finance needs the month-end **net** revenue number early — but they
only have **partial-month** data. By day 15, roughly half the month's activity
has posted, charges lag, denials aren't final, and the real number isn't known
until accounting close. We predict month-end net revenue per facility from what's
known *as of* a mid-month checkpoint — and we do it without leaking the future."

**Show:** the grain and target.

| Column | Meaning |
| --- | --- |
| `facility_id` | Neutral facility id (`FAC-001`) |
| `accounting_month` | `YYYY-MM` |
| `snapshot_date` / `snapshot_day` | As-of checkpoint (day 7, 10, 12, 15, 18, 21, 24, 27) |
| `actual_month_end_net_revenue` | **Target** — known only after close |

**Say:** "Two rules make or break this: (1) **leakage safety** — a feature for a
snapshot never uses anything after its `snapshot_date`; and (2) **time-aware
validation** — we split by time, never random rows, because random rows would let
the model peek at the future."

**Do:** open [architecture/overview.md](../architecture/overview.md) and show the
flow diagram; note the primary metric is **WAPE** (dollar-weighted) with **bias**
reported alongside.

---

## 3. Build & Learn — teach the process  · 12 min

**Say:** "Before touching Azure, let's teach the *process*. This React
experience walks the full data-science lifecycle and explains every step in
context — it's the same lifecycle we then run on Azure ML."

**Do:**

```bash
uv run revenue-prediction serve          # http://127.0.0.1:8000  (API docs at /docs)
```

**Show:** the **Build & Learn** walkthrough (17 steps). Click through the arc:

1. **Frame → Explore → Clean → EDA** — understand the data honestly.
2. **Target → Leakage → Split** — the safety trio. Pause on **Leakage**: show
   how post-close fields are excluded and why.
3. **Features → Baselines → Models → Optimize** — build from a naive prior up to
   gradient boosting; always beat the baseline before celebrating.
4. **Evaluate → Select → Explain** — WAPE/bias overall **and by facility and by
   snapshot day**; SHAP/permutation importance for drivers.
5. **Predict → Retrain → Deliver** — score a checkpoint, know when to retrain,
   hand results to Power BI.

**Say:** "Notice the contextual notes and knowledge checks — this isn't a black
box. Every choice (why WAPE, why time-aware splits, why regression-first) is
explained where you make it."

> Short version: click just **Leakage**, **Split**, **Evaluate**, and **Predict**.

---

## 4. Register data + environment on Azure ML  · 5 min (or pre-done)

**Say:** "Now to Azure. Everything downstream needs two registered assets: the
**data** and the **environment**. Registering them means every run is
reproducible and has lineage."

**Do / Show:** in Azure ML Studio, show the registered **Data asset**
(net-revenue snapshots; MLTable for AutoML) and the registered **environment**
`revenue-prediction-env` (from [`mlops/environments/environment.yml`](../../mlops/environments/environment.yml)).

**Say:** "These are the only two inputs the four patterns share. From here, the
*only* difference between patterns is **how the model is authored** — the
registered output is identical and governed the same way."

---

## 5. Pattern 2 — AutoML via the SDK (fast baseline)  · 8 min

**Say:** "Start with **Automated ML in code** to get a strong, explainable
baseline quickly. It handles featurization, model search, and explainability for
us — perfect for benchmarking WAPE."

**Do:** walk the builder [`src/revenue_prediction/integrations/automl/regression.py`](../../src/revenue_prediction/integrations/automl/regression.py), then submit:

```python
from revenue_prediction.config.loader import load_settings
from revenue_prediction.integrations.automl import build_automl_job_spec, build_regression_job
from revenue_prediction.integrations.azureml.client import get_ml_client

settings = load_settings("dev")
spec = build_automl_job_spec(
    settings.automl, settings.azure_ml,
    training_data_asset="azureml:revenue_snapshots_mltable@latest",
)
job = build_regression_job(spec)   # regression, target=actual_month_end_net_revenue,
                                   # n_cross_validations, featurization=auto,
                                   # model explainability on, early termination on
submitted = get_ml_client(settings.azure_ml).jobs.create_or_update(job)
print(submitted.studio_url)
```

**Show:** open the (pre-run) AutoML job's **leaderboard**, best run **Metrics**,
and **Explanations**. Reference [patterns/automl-sdk.md](../patterns/automl-sdk.md).

**Say:** "There's our benchmark. Analysts can reproduce this. But for the
production champion we want explicit control over leakage-safe features and
time-aware validation — that's the code-first path."

---

## 6. Pattern 3 — code-first via the SDK (the champion)  · 10 min

**Say:** "This is the recommended production path. Same data, same environment —
but *we* own the features, the validation, and the model choice, and it's fully
reproducible for governance and CI/CD."

**Do:** show the command job, which runs the training entry point on compute:

```python
from revenue_prediction.config.loader import load_settings
from revenue_prediction.integrations.azureml.client import get_ml_client
from revenue_prediction.integrations.azureml.jobs import build_command_job

settings = load_settings("dev")
job = build_command_job(
    settings.azure_ml,
    training_data_asset="azureml:revenue_snapshots@latest",
    environment="azureml:revenue-prediction-env@latest",
)
submitted = get_ml_client(settings.azure_ml).jobs.create_or_update(job)
```

**Say:** "On compute this runs `revenue_prediction.core.training.azureml_entry`,
which trains every candidate with **time-aware validation**, selects the champion
by **WAPE**, and logs the MLflow model. For multi-step reproducibility there's a
`@pipeline` (prep → train) in [`mlops/pipelines/azureml_pipeline.py`](../../mlops/pipelines/azureml_pipeline.py)."

**Show:** the completed run's **Metrics** and **Outputs + logs**; the logged
MLflow model. Reference [patterns/aml-sdk.md](../patterns/aml-sdk.md).

---

## 7. Patterns 1 & 4 — the same thing in the UI  · 5 min (or mention)

**Say:** "For analysts and enablement, both patterns exist **in the Studio UI**
with zero code — proving a team can start in the portal and graduate to code."

**Show (briefly):**

- **Pattern 1 — AutoML wizard:** Studio → Automated ML → Regression → target
  `actual_month_end_net_revenue`, k-fold CV, featurization Auto, explainability
  on. See [patterns/automl-ui.md](../patterns/automl-ui.md).
- **Pattern 4 — code-first in the UI:** Studio → Jobs → Create job (Command)
  running `python -m revenue_prediction.core.training.azureml_entry`, or the
  **Designer** with the registered component
  [`mlops/components/train_code_first.yml`](../../mlops/components/train_code_first.yml).
  See [patterns/aml-ui.md](../patterns/aml-ui.md).

**Say:** "Four authoring surfaces, **one** registered, governed, monitored model.
See [patterns/end-to-end-patterns.md](../patterns/end-to-end-patterns.md)."

---

## 8. Evaluate, register, and gate  · 6 min

**Say:** "A single WAPE number isn't enough for finance. We disaggregate — **by
facility and by snapshot day** — because accuracy at day 10 differs from day 24,
and a good average can hide a bad facility. We also report **bias** (are we
systematically over/under?) and the feature drivers."

**Show:** the evaluation view — overall WAPE/bias, the by-facility and
by-snapshot-day breakdowns, and explainability (drivers agree across AutoML and
code-first: volume, gross charges, prior net revenue). Reference the Responsible
AI notebook [`notebooks/responsible_ai/01_explainability_and_fairness.ipynb`](../../notebooks/responsible_ai/01_explainability_and_fairness.ipynb)
and [governance/responsible-ai.md](../governance/responsible-ai.md).

**Do / Say:** "We register the champion and pass a **governance gate** before it
can be promoted." Register the MLflow model
(`revenue_prediction.integrations.azureml.register_model_from_run(...)`), then walk
the champion/challenger promotion rule in
[governance/model-governance.md](../governance/model-governance.md).

---

## 9. Deploy batch + score a mid-month checkpoint  · 6 min

**Say:** "How is this used in production? **Train once, score many times.** The
target isn't known until close, so all month long we score the *same* registered
champion against each partial-month snapshot as it fills in."

**Say (endpoint choice):** "We score **all facilities on a schedule** with no
low-latency need — the textbook fit for a **managed batch endpoint**: no
always-on compute, lowest cost, scales over the whole file. A managed **online**
endpoint is only for on-demand single-facility sub-second scoring — delete it
when idle."

**Do:** validate a checkpoint is leakage-safe, then score it locally to make the
concept concrete:

```bash
# Inference never needs the target column
uv run revenue-prediction validate-data path/to/day15_snapshot.parquet --no-require-target
uv run revenue-prediction predict path/to/champion_bundle path/to/day15_snapshot.parquet
```

**Show:** the deployment assets in [`mlops/endpoints/`](../../mlops/endpoints/)
(`batch-endpoint.yml`, `batch-deployment.yml`) and the self-describing output
(every row carries `predicted_month_end_net_revenue`, `model_version`, `run_id`,
`cutoff_day`, `scored_at`). Full runbook:
[operations/inference-in-production.md](../operations/inference-in-production.md).

---

## 10. OneLake → Power BI, monitoring, and retraining  · 3 min

**Say:** "Predictions land in **OneLake**, and Power BI reads them via
**DirectLake** — so finance sees an early net-revenue estimate per facility, and
every number is traceable to the exact model version that produced it."

**Show:** the Fabric flow [fabric/integration.md](../fabric/integration.md) and
`revenue_scoring` notebook/pipeline under [`fabric/`](../../fabric/).

**Say:** "We **monitor** drift and quality; when drift, degradation, schema
change, or the approved cadence trigger it, we **retrain** — closing the MLOps v2
loop back to step one." Reference [operations/monitoring.md](../operations/monitoring.md)
and [operations/retraining.md](../operations/retraining.md).

---

## 11. Close, fallback, and cleanup

**Close (Say):** "One repository, one governed model, and **four** ways to author
it on Azure ML — all leakage-safe, time-aware, explainable, and taught
step-by-step. Start in the UI, graduate to code, deploy as a batch endpoint,
monitor, and retrain on a schedule."

**Fully-offline fallback** (no Azure needed — use if connectivity fails):

```bash
make data && make train          # end-to-end locally
uv run revenue-prediction serve  # Build & Learn UI at http://127.0.0.1:8000
```

Everything except the live Azure job submission and endpoint deploy can be shown
offline; use pre-captured Studio screenshots for the cloud beats.

**Cleanup (Do):** delete any online endpoint immediately; tear down demo infra to
avoid cost. Follow [operations/cost-and-cleanup.md](../operations/cost-and-cleanup.md).

---

## Appendix A — command cheat-sheet

```bash
# Offline
uv sync --extra api --extra azure
uv run revenue-prediction generate-data
uv run revenue-prediction train-local
uv run revenue-prediction serve                # UI + API at http://127.0.0.1:8000
uv run revenue-prediction validate-data <file> --no-require-target
uv run revenue-prediction predict <bundle> <file>
uv run revenue-prediction info --env dev

# Azure (opt-in; requires your subscription + `az login`)
#  1. provision infra/ (quickstart or secure)
#  2. register data asset (Parquet + MLTable) and environment
#  3. submit AutoML (pattern 2) and/or code-first (pattern 3) jobs
#  4. register champion, gate, deploy batch endpoint, monitor
```

## Appendix B — one-line talking points

- "Partial-month in, month-end net revenue out — **leakage-safe** and
  **time-aware**."
- "**WAPE** because dollars matter more than percentages; **bias** so we know the
  direction of error."
- "**By facility and by snapshot day** — averages hide problems."
- "Four authoring patterns, **one** governed model."
- "**Batch** endpoint: schedule all facilities, pay nothing when idle."
- "Train once, **score many times**; monitor, then retrain on a trigger."
- "The **Build & Learn** UI teaches the exact lifecycle we run on Azure."

## Related

- Patterns hub: [patterns/end-to-end-patterns.md](../patterns/end-to-end-patterns.md)
- MLOps v2 mapping: [architecture/mlops-v2.md](../architecture/mlops-v2.md)
- Deployment guide: [deployment/guide.md](../deployment/guide.md)
- Inference runbook: [operations/inference-in-production.md](../operations/inference-in-production.md)
- Facilitator guide (instructor-led): [workshops/facilitator-guide.md](../workshops/facilitator-guide.md)
</content>
