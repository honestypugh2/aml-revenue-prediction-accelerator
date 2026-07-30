# Multi-stage image: build the React frontend, then serve it (and the API) with
# FastAPI/uvicorn. All data is synthetic; no cloud credentials are needed.

# --- Stage 1: build the React frontend ---
FROM node:22-bookworm-slim AS frontend
WORKDIR /frontend
COPY frontend/package.json frontend/package-lock.json ./
RUN npm ci
COPY frontend/ ./
RUN npm run build

# --- Stage 2: Python runtime serving API + built SPA ---
FROM ghcr.io/astral-sh/uv:python3.11-bookworm-slim

ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    RPA_ENVIRONMENT=dev

WORKDIR /app

# Install dependencies first (better layer caching) using only the lock + project
# metadata, then copy the source.
COPY pyproject.toml uv.lock README.md ./
COPY src ./src
RUN uv sync --frozen --extra api --no-dev

COPY configs ./configs
COPY data ./data
# Bring in the built SPA so FastAPI serves it at "/".
COPY --from=frontend /frontend/dist ./frontend/dist

# Non-root user
RUN useradd --create-home --uid 10001 appuser && chown -R appuser:appuser /app
USER appuser

EXPOSE 8000

# Default: serve the API + built React UI. Override CMD to run the CLI instead.
CMD ["uv", "run", "uvicorn", "revenue_prediction.api.app:app", \
     "--host", "0.0.0.0", "--port", "8000"]
