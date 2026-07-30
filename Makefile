# Makefile for the revenue prediction accelerator.
# Requires `uv` (https://docs.astral.sh/uv/).

.DEFAULT_GOAL := help
.PHONY: help setup sync data train predict test test-cov lint format typecheck check ui clean live-test

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-14s\033[0m %s\n", $$1, $$2}'

setup: ## Full setup (install all extras + dev + pre-commit hooks)
	uv sync --all-extras
	uv run pre-commit install

sync: ## Install core + dev + api dependencies
	uv sync --extra api

data: ## Generate synthetic, sample, and invalid datasets
	uv run revenue-prediction generate-data --env dev

train: ## Train and compare code-first candidates locally
	uv run revenue-prediction train-local --env dev --out outputs

predict: ## Batch score with the champion bundle (requires prior `make train`)
	uv run revenue-prediction predict outputs/champion_bundle.joblib \
		data/synthetic/revenue_snapshots.parquet --out outputs/predictions.csv

test: ## Run the offline test suite
	uv run pytest -q

test-cov: ## Run tests with coverage report
	uv run pytest --cov=revenue_prediction --cov-report=term-missing

live-test: ## Run opt-in live cloud integration tests (needs credentials)
	RPA_RUN_LIVE=1 uv run pytest -m live

lint: ## Lint with ruff
	uv run ruff check src tests

format: ## Format with ruff
	uv run ruff format src tests

typecheck: ## Type check with pyright
	uv run pyright src

check: lint typecheck test ## Run all quality gates

serve: ## Run the FastAPI backend (serves the built React UI at / if present)
	uv run revenue-prediction serve --reload

frontend-install: ## Install the React frontend dependencies
	npm --prefix frontend install

frontend-dev: ## Run the Vite dev server (proxies /api to the backend)
	npm --prefix frontend run dev

frontend-build: ## Build the React frontend into frontend/dist
	npm --prefix frontend run build

ui: frontend-build ## Build the UI and serve it via the backend at http://127.0.0.1:8000
	uv run revenue-prediction serve

clean: ## Remove caches and generated artifacts
	rm -rf .pytest_cache .ruff_cache .coverage htmlcov outputs mlruns frontend/dist
	find . -type d -name __pycache__ -exec rm -rf {} +
