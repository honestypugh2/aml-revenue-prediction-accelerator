# Dependency decisions

## Tooling

- **Python** `>=3.11,<3.13` — compatible with the selected stable versions of
  Azure ML SDK v2, MLflow, scikit-learn, XGBoost, Streamlit, and the Fabric
  ADLS client.
- **uv** for environment and dependency management, with a committed `uv.lock`.
- **src layout**, type hints, Pydantic v2 + pydantic-settings, Ruff, Pyright,
  pytest, pytest-cov, and pre-commit.

## Dependency groups

Core runtime deps (`[project.dependencies]`) are intentionally **cloud-agnostic**
so the accelerator runs fully offline for development, education, and workshops:
NumPy, pandas, PyArrow, scikit-learn, XGBoost, Pandera, MLflow, Pydantic,
pydantic-settings, Typer, Rich, PyYAML, python-dateutil.

Optional integrations live under `[project.optional-dependencies]`:

| Extra | Purpose |
| --- | --- |
| `azure` | `azure-ai-ml`, `azure-identity`, `azureml-mlflow`, `mltable` |
| `fabric` | `azure-storage-file-datalake`, `azure-identity` (OneLake) |
| `ui` | `streamlit`, `plotly`, `matplotlib` |
| `notebooks` | `jupyter`, `ipykernel`, `nbformat` |
| `foundry` | `azure-ai-projects` (optional Azure AI Foundry) |

Dev tooling is a PEP 735 `[dependency-groups]` (`dev`), installed by default by
`uv`.

## No Azure ML SDK v1

The project uses **Azure Machine Learning Python SDK v2** (`azure-ai-ml`)
exclusively. No deprecated v1 packages or APIs are used.

## Optional Foundry and Agent Framework

The core forecasting solution and the workshop **do not depend on an agent**.

- **Azure AI Foundry** (`azure-ai-projects`) is provided as an optional `foundry`
  extra for teams that want to extend the accelerator (for example, to add a
  natural-language explainer over predictions). It is kept out of the core
  environment so it cannot destabilize the accelerator.
- **Microsoft Agent Framework** is intentionally **not** added as a dependency.
  At the time of writing it is early/preview; pinning it into the core or even an
  optional group risks resolver instability across platforms. The extension point
  is documented here instead. Teams that need it should add it in their own fork
  behind a clearly-scoped optional group and validate the lockfile on their
  target platforms.

This satisfies the guidance: keep immature/optional integrations outside the
core, document the extension point, and do not destabilize the accelerator to
force their inclusion.

## Why some Pyright rules are disabled

pandas and NumPy ship dynamic inline types. Under Pyright, ordinary pandas
idioms (e.g. `DataFrame.__getitem__` returning a `Series | DataFrame` union,
Series arithmetic widening to large unions) generate a high volume of
false-positive diagnostics that do not indicate real bugs. To keep type-checking
signal high without sprinkling dozens of `# type: ignore` comments, the
following report categories are disabled in `pyproject.toml`:

`reportArgumentType`, `reportAttributeAccessIssue`, `reportCallIssue`,
`reportOperatorIssue`, `reportReturnType`, `reportIndexIssue`.

Genuinely valuable checks remain enabled (undefined variables, unbound locals,
self/cls parameters, redeclarations, optional-call, etc.). This is a deliberate,
documented trade-off; it caught a real parameter-shadowing bug during
development.

## Reproducing the environment

```bash
uv sync --all-extras   # everything
uv sync --extra ui     # offline dev + UI (recommended default)
```
