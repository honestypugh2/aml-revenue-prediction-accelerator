# Architecture overview

## Purpose

Predict **month-end net revenue** per facility from **partial-month** data, at
the grain `facility_id × accounting_month × snapshot_date`. See
[ADR 0001](adr/0001-modeling-grain.md).

## End-to-end flow

```mermaid
flowchart TD
    A[Synthetic data generator<br/>or Fabric Lakehouse input] --> B[Data contracts<br/>schema + leakage rules]
    B --> C[Temporal split<br/>blocked / rolling / expanding]
    C --> D1[Code-first training<br/>baselines + regressors]
    C --> D2[Azure AutoML<br/>regression]
    D1 --> E[Evaluation<br/>overall + by facility + by snapshot day]
    D2 --> E
    E --> F[Model comparison<br/>champion / challenger]
    F --> G[Explainability +<br/>Responsible AI review]
    G --> H[Model registration<br/>Azure ML registry]
    H --> I1[Batch inference]
    H --> I2[Optional managed online endpoint]
    I1 --> J[Predictions to OneLake<br/>Power BI-ready]
    I2 --> J
    J --> K[Monitoring + drift<br/>retraining triggers]
    K --> C
```

## Layers

| Layer | Package | Responsibility |
| --- | --- | --- |
| Configuration | `config` | Layered base/dev/test/prod, env-var overrides, no secrets |
| Data | `core.data` | Synthetic generation, schema, contracts, leakage rules, IO |
| Features | `core.features` | Leakage-safe, fit-on-train-only transformer |
| Splitting | `core.training.splitting` | Time-aware splits and backtest folds |
| Models | `core.models` | Baselines + regressors + factory |
| Training | `core.training` | Orchestration + Azure ML entry point |
| Evaluation | `core.evaluation` | Metrics, grouped accuracy, selection, explainability |
| Inference | `core.inference` | Model bundle, batch scoring, uncertainty |
| AutoML | `integrations.automl` | Azure ML SDK v2 AutoML regression |
| Azure ML | `integrations.azureml` | Workspace client, command jobs, registration |
| Fabric | `integrations.fabric` | OneLake read/write with local fallback |
| Monitoring | `ops.monitoring` | PSI / drift preparation |
| Security | `security` | Redaction, neutrality scanning |
| Education | `education` | Original lessons and knowledge checks |
| UI logic | `interfaces.ui` | Framework-agnostic experience helpers (pure, testable) |
| API | `interfaces.api` | FastAPI backend serving the React UI over the core |
| CLI | `interfaces.cli` | Typer command-line entry point |
| Pipelines | `pipelines` | Offline end-to-end orchestration |

## Environments

`dev`, `test`, and `prod` configuration profiles support progression from local
development through governed promotion. See
[`docs/deployment/`](../deployment/) and [`docs/governance/`](../governance/).

## End-to-end patterns & MLOps v2

The accelerator demonstrates four authoring patterns — Automated ML (UI & SDK)
and code-first Azure ML (UI & SDK) — all following the classical-ML **MLOps v2**
reference architecture and deployable to a secure managed-VNet workspace. See
[`docs/patterns/end-to-end-patterns.md`](../patterns/end-to-end-patterns.md) and
[`docs/architecture/mlops-v2.md`](mlops-v2.md).

## Security posture

No secrets or resource identifiers are committed. Production deployments use
network isolation and private endpoints; see [`docs/security/`](../security/).
