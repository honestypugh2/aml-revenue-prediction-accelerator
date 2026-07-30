# Frontend — React + TypeScript educational UI

The self-guided learning UI for the accelerator, built with **React 19**,
**TypeScript**, **Vite**, **React Router**, and **TanStack Query** (all latest
stable, minimal dependency set — charts are dependency-free inline SVG). It talks
to the FastAPI backend under `/api`. **All data is synthetic.**

## Pervasive learning

Learning is woven throughout, not siloed in one tab:

- A persistent **Learn panel** (right side) shows contextual notes for whatever
  you are doing (overview, training, evaluation, governance, …).
- Inline **callouts** explain what you are seeing at the moment you see it.
- A dedicated **Learn** page (lessons) and **Knowledge Checks** (server-graded).

## Prerequisites

- Node.js 20+ (tested on Node 24)
- The backend running: `uv sync --extra api && uv run revenue-prediction serve`

## Develop

```bash
npm install
npm run dev        # Vite dev server on http://localhost:5173 (proxies /api -> :8000)
```

Run the backend in another terminal:

```bash
uv run revenue-prediction serve --reload
```

## Build (served by FastAPI)

```bash
npm run build      # type-checks (tsc -b) then builds to frontend/dist
```

Then start the backend and open `http://localhost:8000` — FastAPI serves
`frontend/dist` at `/` with the API at `/api` and docs at `/docs`.

## Scripts

| Script | Purpose |
| --- | --- |
| `npm run dev` | Vite dev server with API proxy |
| `npm run build` | Type-check + production build |
| `npm run typecheck` | Type-check only (`tsc -b --noEmit`) |
| `npm run preview` | Preview the production build |

## Structure

```
src/
  api/        # typed client + TanStack Query hooks + types
  components/ # Nav, LearnPanel, Callout, Charts (SVG)
  pages/      # Overview, Train, Learn, KnowledgeChecks
  env.tsx     # environment (dev/test/prod) context
  App.tsx     # layout + routes + area-aware Learn panel
```
