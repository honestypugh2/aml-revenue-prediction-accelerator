# Docker

A container image for running the accelerator's **offline** core and the
educational/workshop UI. All data is synthetic; no cloud credentials are needed.

## Build

```bash
docker build -f docker/Dockerfile -t revenue-prediction-accelerator .
```

## Run the UI

```bash
docker run --rm -p 8501:8501 revenue-prediction-accelerator
# open http://localhost:8501
```

## Run the CLI

```bash
docker run --rm revenue-prediction-accelerator \
  uv run revenue-prediction train-local --env dev --out /tmp/outputs
```

## Notes

- The image installs the `ui` extra only (offline path). To use Azure/Fabric
  features, build a variant that adds `--extra azure --extra fabric` and provide
  credentials at runtime via environment variables (never bake secrets into the
  image).
- Runs as a non-root user.
