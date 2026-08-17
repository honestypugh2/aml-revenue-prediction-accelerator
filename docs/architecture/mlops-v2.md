# MLOps v2 mapping (classical ML)

This accelerator implements the Azure Architecture Center **classical machine
learning MLOps v2** pattern. This page maps our components to that reference so
the end-to-end design is explicit.

## The two loops

```mermaid
flowchart TB
    subgraph Inner[Inner loop - experimentation and development]
      DA[Data estate / flash report] --> DP[Data prep + contracts]
      DP --> FE[Leakage-safe features]
      FE --> TR[Train: AutoML or code-first]
      TR --> EV[Evaluate + explain]
    end
    EV --> REG[Model registry - versioned, lineage]
    subgraph Outer[Outer loop - operationalization]
      REG --> GATE{Governance gate}
      GATE -->|approved| DEP[Deploy: batch default / online optional]
      DEP --> MON[Monitor: drift + quality]
      MON -->|trigger| DP
    end
    CI[CI: lint, type, tests, contracts] -.-> Inner
    CD[CD: env promotion dev->test->prod] -.-> Outer
```

## Reference architecture — dev → test → prod

This expands the two loops to the **classical machine learning** reference
([Azure Architecture Center](https://learn.microsoft.com/azure/architecture/ai-ml/guide/machine-learning-operations-v2#classical-machine-learning-architecture)),
showing that **both** authoring paths — **no-code AutoML** and **code-first** —
converge on one registered model that is promoted across environments with
human-gated approval, then monitored with drift **and** continuous evaluation.

```mermaid
flowchart LR
    subgraph DEV[Dev workspace - inner loop]
      D[Data asset + environment]
      D --> A1[No-code AutoML<br/>UI + SDK]
      D --> C1[Code-first<br/>UI + SDK]
      A1 --> EV[Evaluate + explain<br/>WAPE/bias, SHAP]
      C1 --> EV
      EV --> REG[Register model<br/>versioned + lineage]
    end
    REG --> G1{Gate: CI + RAI +<br/>human approval}
    subgraph TEST[Test / staging workspace]
      G1 -->|promote| ST[Deploy to test endpoint]
      ST --> VT[Validate: accuracy,<br/>endpoint smoke, contracts]
    end
    VT --> G2{Gate: human approval}
    subgraph PROD[Prod workspace - outer loop]
      G2 -->|promote| DP[Deploy: batch default /<br/>online optional]
      DP --> MON[Monitor: drift +<br/>continuous evaluation]
    end
    MON -->|threshold / schedule| ACT[Events & actions]
    ACT -->|retrain| D
    ACT -->|investigate| EV
```

Environment behavior is driven by the `configs/dev|test|prod` profiles (dataset
size, AutoML budget, model set); cloud identifiers come only from environment
variables. See
[operations/runbooks/promote-across-environments.md](../operations/runbooks/promote-across-environments.md).

## Component mapping

| MLOps v2 element | In this repo |
| --- | --- |
| Data estate / ingestion | Synthetic generator + Fabric/OneLake input ([`src/revenue_prediction/core/data/`](../../src/revenue_prediction/core/data/), [`fabric/`](../../fabric/)) |
| Data prep & validation | Contracts + schema ([`data/contracts/`](../../data/contracts/), `core.data.contracts`) |
| Feature engineering | `core.features.LeakageSafeFeatureBuilder` (fit on train only) |
| Experimentation (inner) | 4 patterns ([patterns](../patterns/end-to-end-patterns.md)): AutoML UI/SDK, code-first UI/SDK |
| Evaluation & explainability | `core.evaluation` (WAPE/bias, by facility/day; permutation + SHAP) |
| Model registry | `integrations.azureml.register_model_from_run` → Azure ML registry |
| Governance gate | Champion/challenger + promotion rule ([governance](../governance/model-governance.md)) |
| Deployment | Batch (default) / online endpoints ([`mlops/endpoints/`](../../mlops/endpoints/)) |
| Monitoring | Drift/quality ([`mlops/monitoring/`](../../mlops/monitoring/), [operations/monitoring.md](../operations/monitoring.md)) |
| Continuous evaluation | Predictions vs post-close actuals ([`mlops/components/continuous_evaluation.yml`](../../mlops/components/continuous_evaluation.yml), `core.evaluation.azureml_evaluate`) |
| Retraining trigger | Scheduled/drift/degradation ([operations/retraining.md](../operations/retraining.md)) |
| CI | [`.github/workflows/ci.yml`](../../.github/workflows/ci.yml) (ruff, pyright, pytest, contracts, neutrality, bicep, frontend) |
| CD / environment promotion | `configs/dev|test|prod` + [deployment](../deployment/guide.md) |
| Infrastructure | Secure workspace ([`infra/`](../../infra/), [security/networking.md](../security/networking.md)) |
| Interactive learning | React Build & Learn UI teaches this exact lifecycle |

## Environments

`dev` → `test` → `prod` config profiles drive the same code across environments.
Promotion is gated by passing CI, disaggregated-accuracy review, the Responsible
AI checklist, and human approval.

## Reference

- Machine learning operations (MLOps) v2 — Azure Architecture Center
  (classical machine learning architecture).
