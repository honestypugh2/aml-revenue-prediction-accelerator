# Pre-deployment checklist

Run through this before any cloud deployment. Do not proceed with unchecked
critical items.

## Configuration

- [ ] `.env` populated locally (never committed); `revenue-prediction info`
      shows `Azure ML configured: True`.
- [ ] Correct environment profile selected (`dev` / `test` / `prod`).
- [ ] No placeholders remain in the values you intend to use.

## Identity & RBAC

- [ ] Deploying principal has the required subscription/resource-group roles
      (see [security/networking.md](../security/networking.md)).
- [ ] Workspace managed identity has `Storage Blob Data Contributor` **and**
      `Storage File Data Privileged Contributor` on the default storage account
      (required for job submission).
- [ ] Least-privilege verified; no unnecessary `Owner` grants.

## Infrastructure

- [ ] Terraform `plan` / Bicep what-if reviewed; no unexpected changes.
- [ ] Networking matches the intended profile (public vs managed/BYO VNet).
- [ ] Private endpoints and private DNS resolve (secure profile).

## Data & model

- [ ] Training data passes schema + leakage contracts
      (`revenue-prediction validate-data ...`).
- [ ] Champion selected and registered; version recorded.
- [ ] Disaggregated accuracy (by facility, by snapshot day) reviewed.
- [ ] Responsible AI checklist complete
      ([governance/responsible-ai.md](../governance/responsible-ai.md)).

## Quality gates

- [ ] `uv run ruff check src tests` passes.
- [ ] `uv run pyright src` passes.
- [ ] `uv run pytest` passes.

## Operations

- [ ] Monitoring/drift plan in place ([operations/monitoring.md](../operations/monitoring.md)).
- [ ] Retraining triggers documented ([operations/retraining.md](../operations/retraining.md)).
- [ ] Cost controls set (compute `min_instances=0`; endpoint/Bastion lifecycle).
- [ ] Rollback plan verified (prior registered model version).
