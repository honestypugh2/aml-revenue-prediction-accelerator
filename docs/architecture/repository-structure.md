# Repository structure

The Python package is organized into a few clear areas so the layout is easy to
follow. This reflects the **adopted** structure (the grouping described below is
in place).

## Principles we follow

- **`src/` layout** (imports resolve only from the installed package, not the
  CWD) — already in place.
- **One responsibility per package**; deep logic lives in modules, not
  `__init__.py`.
- **`__init__.py` is for packaging + a curated public API** (re-export imports),
  *not* implementation. Per the Real Python guidance, small `__init__.py` files
  that just re-export names are idiomatic and encouraged; large ones with
  business logic are not. We removed the only implementation-heavy initializer
  (AutoML now lives in `automl/regression.py`).

## Current top level (what each folder is for)

```
configs/     layered dev/test/prod configuration
data/        synthetic data, contracts, dictionary
docs/        architecture, patterns, modeling, governance, ops, security, workshops
fabric/      Fabric-native notebooks & pipeline design
frontend/    React + TypeScript educational UI
infra/       Bicep + Terraform (quickstart / secure VNet / BYO VNet)
mlops/       AML assets: components, pipelines, endpoints, environments, monitoring, schemas
notebooks/   AutoML, code-first, Fabric, Responsible AI notebooks
scripts/     setup + environment verification
src/revenue_prediction/   the Python package
tests/       unit / contract / smoke / api / ui / integration
```

This is close to the Azure ML accelerator conventions and is discoverable. The
Python package under `src/revenue_prediction/` is grouped by concern (below) so
it does not sprawl into many flat sibling packages.

## The package, grouped by concern (adopted)

The package is grouped into three big ideas — **core** (offline ML),
**integrations** (Azure/Fabric), and **interfaces** (API/CLI/UI) — plus
top-level `config`, `security`, `education`, `ops`, and `pipelines`:

```
src/revenue_prediction/
├── config/                       # layered settings
├── core/                         # offline ML core
│   ├── data/  features/  models/
│   └── training/  evaluation/  inference/
├── integrations/                 # cloud-facing (guarded imports)
│   ├── azureml/  automl/  fabric/
├── ops/                          # operations
│   └── monitoring/
├── security/                     # redaction / neutrality
├── education/                    # lessons, checks, walkthrough
├── interfaces/                   # entry surfaces
│   ├── api/  cli/  ui/
└── pipelines/                    # offline orchestration
```

A newcomer sees **core / integrations / interfaces** instead of 15 flat peers.
Import paths follow the layout, e.g. `revenue_prediction.core.data`,
`revenue_prediction.integrations.automl`, `revenue_prediction.interfaces.api`.
Cross-package imports are absolute; same-package imports stay relative.

## Recommendation B — keep `__init__.py` thin (done)

- Implementation belongs in modules; `__init__.py` only re-exports the public
  API. Verified: only `automl/__init__.py` had logic (moved to
  `regression.py`), and `api/__init__.py`'s wrapper was removed.

## Recommendation C — consolidate docs navigation (done)

`docs/` is comprehensive but broad, so [`docs/README.md`](../README.md) is a
single index (table of contents) giving readers one entry point, with
[`docs/patterns/`](../patterns/end-to-end-patterns.md) as the "how do I run this
on Azure" hub and [`docs/demo/`](../demo/end-to-end-demo-script.md) as the
end-to-end demo track.

## Recommendation D — colocate tests by type (already good)

`tests/` is split by kind (unit/contract/smoke/api/ui/integration) with markers.
Keep it; it maps cleanly to CI stages.

## What NOT to change

- The `src/` layout, `configs/` layering, and `infra/` three-profile split are
  best practice — keep them.
- Re-export `__init__.py` files are fine and should stay.
