#Requires -Version 5.1
<#
.SYNOPSIS
    Setup script for Windows. Installs uv (if needed), syncs the environment,
    installs pre-commit hooks, and runs a quick verification.
.PARAMETER Extras
    Which extra to install (default 'ui'). Pass 'all' to install everything.
#>
param(
    [string]$Extras = "api"
)

$ErrorActionPreference = "Stop"
Write-Host "==> Revenue Prediction Accelerator setup (Windows)"

if (-not (Get-Command uv -ErrorAction SilentlyContinue)) {
    Write-Host "==> Installing uv"
    powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
    $env:PATH = "$env:USERPROFILE\.local\bin;$env:PATH"
}

Write-Host "==> uv version: $(uv --version)"

if ($Extras -eq "all") {
    Write-Host "==> Installing ALL extras + dev"
    uv sync --all-extras
} else {
    Write-Host "==> Installing core + dev + '$Extras' extra"
    uv sync --extra $Extras
}

Write-Host "==> Installing pre-commit hooks (best-effort)"
try { uv run pre-commit install } catch { Write-Host "   (pre-commit not installed; skipping)" }

Write-Host "==> Verifying environment"
try { uv run python scripts/verify_environment.py } catch { }

Write-Host @"

Next steps:
  uv run revenue-prediction generate-data --env dev
  uv run revenue-prediction train-local  --env dev --out outputs

  # Backend API (serves the built React UI at / if present):
  uv run revenue-prediction serve --reload

  # React frontend (dev server, proxies /api -> backend):
  npm --prefix frontend install; npm --prefix frontend run dev

All data is synthetic. Cloud steps are opt-in; see docs/deployment/guide.md.
"@
