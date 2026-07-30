# Docker

A container image that builds the **React** frontend and serves it together with
the **FastAPI** backend over the accelerator's **offline** core. All data is
synthetic; no cloud credentials are needed.

## Build

```bash
docker build -f docker/Dockerfile -t revenue-prediction-accelerator .
```

## Run the UI + API

```bash
docker run --rm -p 8000:8000 revenue-prediction-accelerator
# open http://localhost:8000  (API docs at http://localhost:8000/docs)
```

## Run the CLI

```bash
docker run --rm revenue-prediction-accelerator \
  uv run revenue-prediction train-local --env dev --out /tmp/outputs
```

## Notes

- Stage 1 builds the React SPA with Node; stage 2 installs the `api` extra and
  serves the built SPA plus the API with uvicorn. To use Azure/Fabric features,
  build a variant that adds `--extra azure --extra fabric` and provide
  credentials at runtime via environment variables (never bake secrets into the
  image).
- Runs as a non-root user.
