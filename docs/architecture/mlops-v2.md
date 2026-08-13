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
