# Azure ML Studio — workspace tour (what each tab is)

A guided tour of the Azure Machine Learning Studio workspace and **where this
accelerator's assets appear**. The left navigation groups everything into three
sections: **Authoring**, **Assets**, and **Manage**.

> All names below use placeholders; your workspace shows your own values.

## Authoring — where you build models

| Tab | What it is | In this accelerator |
| --- | --- | --- |
| **Notebooks** | Managed Jupyter in the workspace (files + compute). | Run the notebooks under [`notebooks/`](../../notebooks/) here, or clone the repo into a compute instance. |
| **Automated ML** | The **no-code AutoML** wizard: pick data + target, it searches algorithms and builds a leaderboard. | **Pattern 1** — regression on `actual_month_end_net_revenue` (MLTable data asset). |
| **Designer** | Drag-and-drop pipeline builder from registered **components**. | **Pattern 4** — compose the `revenue_code_first_training` component into a pipeline with no code. |
| **Prompt flow** | Authoring for LLM/prompt apps. | **Not used** — this is classical regression, not generative AI. |

## Assets — what your work produces

| Tab | What it is | In this accelerator |
| --- | --- | --- |
| **Data** | Registered, versioned **data assets** (URI files, folders, MLTable). | `revenue_snapshots` (Parquet, code-first) and `revenue_snapshots_mltable` (AutoML). |
| **Jobs** | Every training/scoring **run**, grouped by experiment, with metrics + logs. | `revenue-code-first`, `revenue-automl-dev`, and batch scoring pipeline jobs. |
| **Components** | Reusable, versioned pipeline steps. | `revenue_code_first_training`, `revenue_batch_score`, `revenue_batch_scoring_pipeline`, `revenue_continuous_evaluation`. |
| **Pipelines** | Multi-step workflows built from components. | The training pipeline and the batch-scoring pipeline. |
| **Environments** | Versioned Docker/conda definitions for reproducible runs. | `revenue-prediction-env` (from [`mlops/environments/environment.yml`](../../mlops/environments/environment.yml)). |
| **Models** | The **registry** of versioned models with lineage + tags. | `revenue-net-revenue-model` — versions tagged `authoring_pattern` = `code_first` / `automl`. |
| **Endpoints** | Deployed **batch** and **online** endpoints. | `revenue-batch-endpoint` with the `champion-pipeline` deployment. |

> **Why the Models -> Endpoints tab can show "no endpoints"** even when a batch
> endpoint exists: our batch deployment is a **pipeline-component** deployment, so
> the model is consumed *inside* the pipeline (as an `mlflow_model` input) rather
> than referenced directly by the deployment. The endpoint still runs and uses the
> model — see [inference-in-production.md](inference-in-production.md#how-the-batch-deployment-works-pipeline-component).

## Manage — the platform underneath

| Tab | What it is | In this accelerator |
| --- | --- | --- |
| **Compute** | Compute instances (dev boxes) and **clusters** (training/scoring). | `cpu-cluster` runs the code-first, AutoML, and batch jobs; scales to zero when idle. |
| **Monitoring** | Model monitoring: data drift, prediction drift, data quality. | Wire up [`mlops/monitoring/monitoring-schedule.yml`](../../mlops/monitoring/monitoring-schedule.yml); pair with [continuous evaluation](monitoring.md#continuous-evaluation-predictions-vs-actuals). |
| **Data Labeling** | Human labeling projects (image/text). | **Not used** — labels here (`actual_month_end_net_revenue`) come from accounting close, not manual labeling. |
| **Linked Services** | Connections to other Azure/Fabric resources. | Link **OneLake/Fabric** for input snapshots and prediction output. |

## The typical path through the UI

1. **Assets -> Data** — confirm the registered dataset + version.
2. **Authoring -> Automated ML** (Pattern 1) or **Notebooks/SDK** (Patterns 2-3) — train.
3. **Assets -> Jobs** — open the run; read **Metrics** (see
   [run metrics glossary](../modeling/models-and-metrics.md#automl-run-metrics-in-azure-ml-studio))
   and **Explanations**.
4. **Assets -> Models** — register the champion; compare versions by
   `authoring_pattern`.
5. **Assets -> Endpoints** — deploy the batch endpoint; invoke it.
6. **Manage -> Monitoring** — schedule drift + continuous evaluation.

## Related

- [Model selection & evaluation across patterns](../patterns/model-selection-and-evaluation.md)
- [Models & metrics catalog](../modeling/models-and-metrics.md)
- [End-to-end patterns](../patterns/end-to-end-patterns.md)
