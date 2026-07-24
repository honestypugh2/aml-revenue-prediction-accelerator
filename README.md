# Revenue Prediction Accelerator

> **Reusable Azure Machine Learning accelerator** for predicting healthcare
> **facility month-end net revenue** from **partial-month** operational and
> financial data.

> [!IMPORTANT]
> **All sample data in this repository is fully synthetic.** It contains no
> customer, patient, or organization-specific information. Every sample output
> is illustrative only and **must be reviewed by qualified finance, data,
> security, privacy, compliance, and operational stakeholders before any
> production use.** This accelerator is **operational decision support and
> financial forecasting** — it is *not* clinical decision support, financial
> advice, an autonomous financial decision-making system, a compliance
> certification, or a production-ready solution without organization-specific
> review.

---

## What this accelerator does

Given **partial-month** data (for example, everything known by **day 15** of an
accounting month), it produces an **early, reliable estimate of month-end net
revenue by facility**. Inference can run repeatedly during the month without
retraining; retraining happens on an approved schedule or when drift,
degradation, schema changes, or upstream-data changes justify it.

The prediction grain is **facility × accounting month × as-of snapshot date**:

| Column | Meaning |
| --- | --- |
| `facility_id` | Neutral facility identifier (e.g. `FAC-001`) |
| `accounting_month` | Accounting month, `YYYY-MM` |
| `snapshot_date` | As-of date within the month, `YYYY-MM-DD` |
| `snapshot_day` | Day of month for the snapshot (7, 10, 12, 15, 18, 21, 24, 27) |

The target is `actual_month_end_net_revenue`, which is only known **after
accounting close**.

## Four purposes, one repository

1. **Reusable, production-oriented accelerator** — src-layout package, MLOps
   assets, secure infrastructure as code, CI/CD.
2. **End-to-end Azure ML + Microsoft Fabric demonstration** — AutoML *and*
   code-first training, OneLake I/O, Power BI-ready output.
3. **Self-guided educational experience** — an original interactive Streamlit
   experience plus structured docs.
4. **Instructor-led workshop** — exercises, facilitator guide, knowledge checks.

## Two Azure Machine Learning v2 approaches

- **Automated ML** using the Azure Machine Learning Python SDK v2.
- **Code-first ML** using Python, Azure ML SDK v2, MLflow, and appropriate
  **regression and forecasting** techniques (regression-first by design).

## Quickstart (fully offline)

```bash
# 1. Install dependencies (creates .venv)
uv sync --extra ui

# 2. Generate the synthetic dataset
uv run revenue-prediction generate-data

# 3. Train and compare code-first candidates locally
uv run revenue-prediction train-local

# 4. Launch the educational / workshop UI
uv run streamlit run src/revenue_prediction/ui/app.py
```

No Azure or Fabric credentials are required for the offline path. Cloud steps
(AutoML, code-first jobs, registration, endpoints, OneLake, deployment) are
**opt-in** and documented under [`docs/`](docs/).

## Repository map

| Path | Purpose |
| --- | --- |
| [`src/revenue_prediction/`](src/revenue_prediction/) | Core Python package |
| [`configs/`](configs/) | Layered base/dev/test/prod configuration |
| [`data/`](data/) | Synthetic data, contracts, dictionary, provenance |
| [`mlops/`](mlops/) | Components, environments, endpoints, monitoring, schemas |
| [`notebooks/`](notebooks/) | AutoML, code-first, Fabric, responsible AI notebooks |
| [`fabric/`](fabric/) | Fabric notebooks & pipeline guidance |
| [`infra/`](infra/) | Bicep + Terraform (quickstart, secure VNet, BYO VNet) |
| [`docs/`](docs/) | Architecture, deployment, governance, security, workshops |
| [`tests/`](tests/) | unit / contract / smoke / integration / ui tests |

## Documentation index

- Architecture & decisions: [`docs/architecture/`](docs/architecture/)
- Modeling strategy: [`docs/modeling/`](docs/modeling/)
- Fabric & OneLake: [`docs/fabric/`](docs/fabric/)
- Security & networking: [`docs/security/`](docs/security/)
- Deployment: [`docs/deployment/`](docs/deployment/)
- Governance & responsible AI: [`docs/governance/`](docs/governance/)
- Operations, monitoring, retraining: [`docs/operations/`](docs/operations/)
- Education & workshops: [`docs/education/`](docs/education/), [`docs/workshops/`](docs/workshops/)

## Safety, neutrality, and licensing

- Customer-neutral: neutral identifiers only (`FAC-001`, `WORKSPACE_PLACEHOLDER`,
  `LAKEHOUSE_PLACEHOLDER`). No secrets or resource identifiers are committed.
- Third-party reuse and licensing decisions are recorded in
  [`THIRD_PARTY_NOTICES.md`](THIRD_PARTY_NOTICES.md).
- See [`SECURITY.md`](SECURITY.md), [`SUPPORT.md`](SUPPORT.md),
  [`CONTRIBUTING.md`](CONTRIBUTING.md), and [`CODE_OF_CONDUCT.md`](CODE_OF_CONDUCT.md).

## License

Released under the [MIT License](LICENSE).
