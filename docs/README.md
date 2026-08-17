# Documentation index

One entry point for the accelerator's documentation. All examples use
**synthetic data** and **placeholder identifiers** (`FAC-001`,
`WORKSPACE_PLACEHOLDER`). Review every output with your finance, data, security,
privacy, compliance, and operational stakeholders before any production use.

## Start here

| I want to… | Read |
| --- | --- |
| Understand the whole system | [architecture/overview.md](architecture/overview.md) |
| See how it maps to MLOps v2 | [architecture/mlops-v2.md](architecture/mlops-v2.md) |
| Understand the package layout | [architecture/repository-structure.md](architecture/repository-structure.md) |
| Run a full end-to-end **demo** | [demo/end-to-end-demo-script.md](demo/end-to-end-demo-script.md) |
| Walk it end to end in a **notebook** | [`notebooks/end_to_end/00_end_to_end_walkthrough.ipynb`](../notebooks/end_to_end/00_end_to_end_walkthrough.ipynb) |
| Run it **offline** on my laptop | [development/getting-started.md](development/getting-started.md) |

## The four Azure ML authoring patterns

Start at the hub: [patterns/end-to-end-patterns.md](patterns/end-to-end-patterns.md).
For **selecting, comparing, and evaluating** models across all four, see
[patterns/model-selection-and-evaluation.md](patterns/model-selection-and-evaluation.md).

| # | Pattern | Guide |
| --- | --- | --- |
| 1 | Automated ML via the Studio **UI** | [patterns/automl-ui.md](patterns/automl-ui.md) |
| 2 | Automated ML via the **SDK** v2 | [patterns/automl-sdk.md](patterns/automl-sdk.md) |
| 3 | Code-first via the **SDK** v2 (champion path) | [patterns/aml-sdk.md](patterns/aml-sdk.md) |
| 4 | Code-first via the Studio **UI** / Designer | [patterns/aml-ui.md](patterns/aml-ui.md) |

## By topic

- **Architecture & decisions:** [architecture/](architecture/) (incl. [ADRs](architecture/adr/))
- **Modeling:** [modeling/strategy.md](modeling/strategy.md), [modeling/automl.md](modeling/automl.md),
  [modeling/models-and-metrics.md](modeling/models-and-metrics.md),
  [modeling/success-metrics-and-kpis.md](modeling/success-metrics-and-kpis.md)
- **Fabric & OneLake:** [fabric/integration.md](fabric/integration.md)
- **Security & networking:** [security/networking.md](security/networking.md)
- **Deployment:** [deployment/guide.md](deployment/guide.md),
  [deployment/checklist.md](deployment/checklist.md),
  [deployment/python-dependencies-and-vnet.md](deployment/python-dependencies-and-vnet.md)
- **Operations:** [operations/runbooks/](operations/runbooks/README.md) (task runbooks index),
  [operations/inference-in-production.md](operations/inference-in-production.md),
  [operations/monitoring.md](operations/monitoring.md),
  [operations/retraining.md](operations/retraining.md),
  [operations/onnx-optimization.md](operations/onnx-optimization.md),
  [operations/cost-and-cleanup.md](operations/cost-and-cleanup.md)
- **Governance & responsible AI:** [governance/model-governance.md](governance/model-governance.md),
  [governance/responsible-ai.md](governance/responsible-ai.md)
- **Education & workshops:** [education/inspiration.md](education/inspiration.md),
  [workshops/facilitator-guide.md](workshops/facilitator-guide.md),
  [workshops/exercises.md](workshops/exercises.md),
  [workshops/knowledge-checks.md](workshops/knowledge-checks.md)
- **Development:** [development/getting-started.md](development/getting-started.md),
  [development/dependencies.md](development/dependencies.md)

## Conventions

- **Grain:** `facility_id × accounting_month × snapshot_date` (`snapshot_day`).
- **Target:** `actual_month_end_net_revenue` (known only after accounting close).
- **Primary metric:** WAPE (dollar-weighted); bias reported alongside.
- **Leakage safety:** a feature for a snapshot never uses information from after
  its `snapshot_date`; splits are time-aware, never random rows.
</content>
</invoke>
