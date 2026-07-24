# Copilot / AI agent instructions

This repository is a **reusable, customer-neutral** Azure Machine Learning
accelerator for predicting healthcare facility **month-end net revenue** from
**partial-month** data. When assisting in this repo, follow these rules.

## Non-negotiable constraints

- **Customer neutrality.** Never add customer names, acronyms, participant names,
  organization-specific facility names/identifiers, real patient information,
  realistic patient names, medical record numbers, actual finance data, emails,
  phone numbers, or any cloud identifiers/secrets (subscription/tenant/client
  IDs, tokens, SAS tokens, storage keys, connection strings, workspace/Fabric/
  Lakehouse IDs). Use placeholders: `FAC-001`, `WORKSPACE_PLACEHOLDER`,
  `LAKEHOUSE_PLACEHOLDER`.
- **Synthetic data only.** All default data comes from
  `revenue_prediction.data.synthetic`.
- **No Azure ML SDK v1.** Use `azure-ai-ml` (SDK v2) exclusively.
- **Leakage safety.** A feature for a snapshot must never use information from
  after its `snapshot_date`. Preserve time-aware splitting (never random row
  splits as the primary method) and the contract/leakage tests.
- **Regression-first.** Do not make an LSTM the default model (see
  `docs/architecture/adr/0003-model-choice.md`).

## Grain and target

- Grain: `facility_id × accounting_month × snapshot_date` (`snapshot_day`).
- Target: `actual_month_end_net_revenue` (known only after accounting close).

## Project conventions

- `uv` for env/deps; `src/` layout; Pydantic v2; type hints.
- Quality gates: `ruff`, `pyright`, `pytest`. Run `make check` before finishing.
- Optional cloud/UI deps are extras; keep their imports **guarded** so the core
  imports offline. Live tests are `-m live` and opt-in.
- Configuration is layered (`configs/base` → env → env vars). Secrets come only
  from environment variables; never commit them.

## Where things live

- Core package: `src/revenue_prediction/` (see `docs/architecture/overview.md`).
- Data contracts: `src/revenue_prediction/data/`, `data/contracts/`.
- Infra: `infra/` (Bicep validated; Terraform validated in CI).
- MLOps assets: `mlops/`. Notebooks: `notebooks/`, `fabric/`.

## When you change things

- Add/adjust tests for new behavior.
- Update docs and, for any third-party reuse, `THIRD_PARTY_NOTICES.md` and the
  relevant ADR.
- Keep the offline path working end-to-end (`make data && make train`).
