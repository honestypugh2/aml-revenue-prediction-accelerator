# Container image for the revenue prediction accelerator (offline core + UI).
# Uses the official uv base image for fast, reproducible installs.
FROM ghcr.io/astral-sh/uv:python3.11-bookworm-slim

ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    RPA_ENVIRONMENT=dev

WORKDIR /app

# Install dependencies first (better layer caching) using only the lock + project
# metadata, then copy the source.
COPY pyproject.toml uv.lock README.md ./
COPY src ./src
RUN uv sync --frozen --extra ui --no-dev

COPY configs ./configs
COPY data ./data

# Non-root user
RUN useradd --create-home --uid 10001 appuser && chown -R appuser:appuser /app
USER appuser

EXPOSE 8501

# Default: launch the educational / workshop UI. Override CMD to run the CLI.
CMD ["uv", "run", "streamlit", "run", "src/revenue_prediction/ui/app.py", \
     "--server.address=0.0.0.0", "--server.port=8501"]
