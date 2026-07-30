#!/usr/bin/env bash
# Setup script for Linux/macOS. Installs uv (if needed), syncs the environment,
# installs pre-commit hooks, and runs a quick verification.
set -euo pipefail

echo "==> Revenue Prediction Accelerator setup (Linux/macOS)"

if ! command -v uv >/dev/null 2>&1; then
  echo "==> Installing uv"
  curl -LsSf https://astral.sh/uv/install.sh | sh
  export PATH="$HOME/.local/bin:$PATH"
fi

echo "==> uv version: $(uv --version)"

EXTRAS="${1:-api}"   # pass "all" to install everything
if [ "$EXTRAS" = "all" ]; then
  echo "==> Installing ALL extras + dev"
  uv sync --all-extras
else
  echo "==> Installing core + dev + '$EXTRAS' extra"
  uv sync --extra "$EXTRAS"
fi

echo "==> Installing pre-commit hooks (best-effort)"
uv run pre-commit install || echo "   (pre-commit not installed; skipping)"

echo "==> Verifying environment"
uv run python scripts/verify_environment.py || true

cat <<'EOF'

Next steps:
  uv run revenue-prediction generate-data --env dev
  uv run revenue-prediction train-local  --env dev --out outputs

  # Backend API (serves the built React UI at / if present):
  uv run revenue-prediction serve --reload

  # React frontend (dev server, proxies /api -> backend):
  npm --prefix frontend install && npm --prefix frontend run dev

All data is synthetic. Cloud steps are opt-in; see docs/deployment/guide.md.
EOF
