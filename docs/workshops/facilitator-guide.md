# Facilitator guide — Net-Revenue Prediction workshop

A hands-on workshop teaching Azure Machine Learning (AutoML and code-first),
Microsoft Fabric/OneLake, MLOps, and model governance through a healthcare
net-revenue prediction accelerator. **All data is synthetic.**

## Audience & prerequisites

- Data scientists, ML/ MLOps engineers, and solution architects.
- Comfortable with Python; basic ML familiarity.
- For the offline portion: a laptop with Python 3.11+ and `uv`.
- For the optional cloud portion: an Azure subscription and (optionally) a Fabric
  workspace.

## Duration & format

| Segment | Time | Mode |
| --- | --- | --- |
| 1. Problem framing & data | 30 min | Talk + UI |
| 2. Leakage & time-aware validation | 30 min | Exercise |
| 3. Code-first training & comparison | 45 min | Exercise |
| 4. Azure AutoML | 30 min | Demo / optional hands-on |
| 5. Governance & Responsible AI | 30 min | Discussion + exercise |
| 6. Fabric/OneLake & Power BI | 30 min | Demo |
| 7. Deploy, monitor, retrain | 30 min | Demo + discussion |
| Knowledge checks & wrap-up | 15 min | Quiz |

Adjust to a 2-hour or full-day format by including/excluding the cloud demos.

## Setup (facilitator, before the session)

```bash
uv sync --extra api
uv run revenue-prediction generate-data --env dev
npm --prefix frontend install && npm --prefix frontend run build
uv run revenue-prediction serve            # sanity check -> http://127.0.0.1:8000
```

Have `make check` passing so learners see a green baseline.

## Running each segment

- Use the **React app** (`make ui`, or the Vite dev server) for framing, data
  exploration, live training, and the built-in knowledge checks. A persistent
  **Learn panel** shows contextual guidance for whatever segment you are on, so
  learning is woven through every screen rather than siloed in one tab.
- Use the **exercises** in [`exercises.md`](exercises.md) for hands-on work.
- Use the **knowledge checks** in [`knowledge-checks.md`](knowledge-checks.md)
  (also embedded in the UI, graded server-side) to assess understanding.

## Facilitation tips

- Emphasize *why random splitting is wrong here* — it is the most common
  mistake. Exercise 2 makes leakage tangible.
- When a baseline beats a complex model (it can, on small synthetic data), use it
  to teach that **baselines matter** and complexity must earn its place.
- Keep the cloud portions optional; the whole learning arc works offline.

## Safety framing (say this out loud)

This is decision support and forecasting on synthetic data — not clinical
decision support, not financial advice, not autonomous decisioning, and not
production-ready without organization-specific finance, data, security, privacy,
compliance, and operational review.

## Assessment

Learners should be able to: explain the grain and target; identify and prevent
leakage; run and interpret code-first and AutoML results; describe
champion/challenger governance; and outline a Fabric + deploy + monitor +
retrain flow. Target: 4/5 on the knowledge checks.
