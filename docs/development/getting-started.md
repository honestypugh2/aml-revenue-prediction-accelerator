# Getting started (developer guide)

## Prerequisites

- Python 3.11 or 3.12
- [`uv`](https://docs.astral.sh/uv/)
- (Optional) Azure CLI and an Azure subscription for cloud steps
- (Optional) A Microsoft Fabric workspace + Lakehouse for OneLake steps

## Install

```bash
uv sync --extra ui          # offline dev + UI (recommended)
# or
uv sync --all-extras        # include azure, fabric, notebooks, foundry
uv run pre-commit install   # optional git hooks
```

## Everyday commands

```bash
make data      # generate synthetic + sample + invalid datasets
make train     # train & compare candidates, save champion bundle
make predict   # batch score with the champion bundle
make ui        # launch the Streamlit experience
make check     # ruff + pyright + pytest
```

Or use the CLI directly:

```bash
uv run revenue-prediction --help
uv run revenue-prediction info --env dev
uv run revenue-prediction generate-data --env dev
uv run revenue-prediction train-local --env dev --out outputs
uv run revenue-prediction validate-data data/synthetic/revenue_snapshots.parquet
uv run revenue-prediction predict outputs/champion_bundle.joblib \
    data/synthetic/revenue_snapshots.parquet --out outputs/predictions.csv
```

## Configuration

Configuration is layered: `configs/base` → `configs/<env>` → environment
variables / `.env`. Secrets and cloud identifiers come **only** from environment
variables (prefix `RPA_`, nested delimiter `__`). Copy `.env.example` to `.env`
for local cloud runs.

## Testing

```bash
uv run pytest                 # offline suite
uv run pytest -m unit         # only unit tests
uv run pytest -m "not live"   # everything except opt-in live tests
RPA_RUN_LIVE=1 uv run pytest -m live   # live cloud tests (needs credentials)
```

## Project layout

See [`docs/architecture/overview.md`](../architecture/overview.md).
