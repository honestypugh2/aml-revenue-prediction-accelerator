# Third-Party Notices

This project is released under the [MIT License](LICENSE). It depends on and was
informed by third-party software and references. This file records reuse and
licensing decisions.

## 1. Reference repository (architectural inspiration)

- **Project:** `aml-v2-lstm-ts-forecasting-demo`
- **URL:** https://github.com/honestypugh2/aml-v2-lstm-ts-forecasting-demo
- **License:** MIT License
- **How it was used:** Used as a *structural and architectural* reference for
  the repository layout (`configs/`, `data/`, `docker/`, `infra/`, `mlops/`,
  `notebooks/`, `scripts/`, `src/`, `tests/`), the `uv`-based environment
  workflow, and the three-tier infrastructure approach (quickstart, secure
  managed-VNet, and BYO-VNet). Infrastructure patterns (managed VNet, private
  endpoints, Bastion, jump box, private DNS) were re-implemented originally for
  the net-revenue use case.
- **What was NOT carried over:** LSTM/PyTorch model code and any
  forecasting-model specifics. Net-revenue prediction is treated as a
  regression-first problem; see `docs/architecture/adr/0003-model-choice.md`.
- **Decision record:** `docs/architecture/adr/0002-reference-repository-reuse.md`.

The MIT license permits reuse with attribution. This notice, together with the
retained MIT license text, satisfies the attribution requirement. Where any
snippet was adapted, the adaptation is original work covered by this project's
MIT license.

## 2. Educational experience (conceptual inspiration only)

- **Article:** "ArchAngel: Skilling the next developer generation for the
  Agentic transformation" (Microsoft Tech Community blog).
- **Supporting repository:** `rohitmadhavk/ArchAngel`
  (https://github.com/rohitmadhavk/ArchAngel).
- **How it was used:** As *conceptual inspiration only* for the idea of
  contextual, repository-grounded, interactive learning. **No source code,
  prose, prompts, screenshots, visual design, diagrams, branded terminology,
  names, logos, characters, product identity, UI structure, or repository
  structure were copied from either the article or the supporting repository.**
  The React UI, FastAPI backend, contextual-note layer, lessons, and knowledge
  checks in this project are original work. See `docs/education/inspiration.md`.
  This project is not a fork, reproduction, derivative, or official
  implementation of that work.

## 3. Microsoft documentation

Azure Machine Learning, Microsoft Fabric/OneLake, and secure-workspace guidance
were consulted as authoritative references for APIs, authentication, networking,
and deployment behavior. No documentation text was copied verbatim; all prose in
this repository is original.

## 4. Open-source dependencies

This project uses open-source Python packages declared in `pyproject.toml`,
including (non-exhaustive): NumPy, pandas, PyArrow, scikit-learn, XGBoost,
Pandera, MLflow, Pydantic, pydantic-settings, Typer, Rich, and (optional)
FastAPI, Uvicorn, `azure-ai-ml`, `azure-identity`, `azureml-mlflow`, `mltable`,
`azure-storage-file-datalake`, and `azure-ai-projects`. The React frontend under
`frontend/` uses npm packages declared in `frontend/package.json` — React,
React DOM, TanStack Query, and (dev) Vite, TypeScript, and
`@vitejs/plugin-react`. Each is distributed under its own license (predominantly
BSD-3-Clause, Apache-2.0, or MIT). Their license texts are available in the
installed package metadata and on
their respective project pages. No source from these packages is redistributed
here beyond normal dependency usage.

## 5. Datasets

The default dataset is **generated synthetically** by
`revenue_prediction.core.data.synthetic` and is original to this project. No
third-party dataset is redistributed. Dataset references listed in the project
brief were reviewed for domain understanding only; none were copied or
redistributed. See `data/README.md` for provenance and `docs/modeling/` for the
billing-amount-versus-net-revenue discussion.

If a third-party dataset is ever added, its license must explicitly permit
redistribution, and its provenance and license must be documented here and in
`data/README.md`.
