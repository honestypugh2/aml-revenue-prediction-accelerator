# ADR 0002: Reference-repository reuse

- Status: Accepted
- Date: 2026-07-24

## Context

The project brief points to a reference repository,
`aml-v2-lstm-ts-forecasting-demo`, as a structural and architectural starting
point, and asks that its useful patterns — especially the `infra` directory —
be carried forward where the license permits.

## Decision

We inspected the reference repository. It is licensed under the **MIT License**,
which permits reuse and adaptation with attribution. We therefore:

- Adopt its **repository structure** conventions (`configs/`, `data/`,
  `docker/`, `infra/`, `mlops/`, `notebooks/`, `scripts/`, `src/`, `tests/`).
- Adopt its **`uv`-based** environment and dependency workflow.
- Re-implement its **three-tier infrastructure** approach originally for the
  net-revenue use case:
  - `infra/terraform-quickstart/` — minimal, public workspace for quick starts.
  - `infra/terraform/` — secure managed-VNet workspace with private endpoints,
    Bastion, and a jump box.
  - `infra/azure-ml-vnet/` — BYO-VNet networking foundation.
  - `infra/bicep/` — an additional Bicep implementation of the quickstart and
    secure profiles for teams that prefer Bicep.
- Record attribution in [`THIRD_PARTY_NOTICES.md`](../../../THIRD_PARTY_NOTICES.md).

## What we deliberately did NOT reuse

- **LSTM/PyTorch model code.** See ADR 0003. Net-revenue prediction is a
  regression-first problem; an LSTM is not the default.
- Any dataset or content whose license is absent, unclear, or restrictive.

## Consequences

- We benefit from a proven layout and secure-infrastructure approach while
  keeping the modeling stack appropriate to the problem.
- Attribution obligations are satisfied via the retained MIT notice and
  `THIRD_PARTY_NOTICES.md`.
