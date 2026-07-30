"""FastAPI backend that serves the React educational UI over the Python core.

Runs fully offline on synthetic data. No Azure/Fabric calls are made here. Start
with:

    uv run revenue-prediction serve            # via the CLI
    uv run uvicorn revenue_prediction.api.app:app --reload

The built React app (``frontend/dist``) is served at ``/`` when present; the API
lives under ``/api``. In development the Vite dev server proxies ``/api`` here.
"""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from .. import __version__
from ..config.loader import load_settings
from ..education import (
    get_contextual_notes,
    get_knowledge_checks,
    get_lessons,
    grade_answer,
)
from ..ui.experience import (
    ExperienceState,
    build_comparison_view,
    build_dataset_overview,
    facility_month_series,
    load_experience,
    run_training_experience,
)
from .schemas import (
    ConfigResponse,
    ContextualNoteModel,
    DatasetOverview,
    FacilityPoint,
    FacilitySeries,
    GradeRequest,
    GradeResponse,
    GroupMetrics,
    HealthResponse,
    KnowledgeCheckModel,
    LessonModel,
    ModelMetrics,
    TrainRequest,
    TrainResponse,
)

try:
    from fastapi import FastAPI, HTTPException
    from fastapi.middleware.cors import CORSMiddleware
    from fastapi.responses import FileResponse
    from fastapi.staticfiles import StaticFiles
except ImportError as exc:  # pragma: no cover - requires the 'api' extra
    raise ImportError(
        "FastAPI is not installed. Install the 'api' extra: `uv sync --extra api`."
    ) from exc


# --- Cached experience/training state (per environment) --------------------
@lru_cache(maxsize=8)
def _experience(environment: str) -> ExperienceState:
    return load_experience(environment)


@lru_cache(maxsize=8)
def _training(environment: str):
    return run_training_experience(_experience(environment))


def _frontend_dist() -> Path:
    # repo_root/frontend/dist  (…/src/revenue_prediction/api/app.py -> parents[3])
    return Path(__file__).resolve().parents[3] / "frontend" / "dist"


def create_app() -> FastAPI:
    app = FastAPI(
        title="Revenue Prediction Accelerator API",
        version=__version__,
        description="Offline, synthetic-data API powering the React learning UI.",
    )

    # Allow the Vite dev server during development.
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            "http://localhost:5173",
            "http://127.0.0.1:5173",
        ],
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # ---- Meta ----
    @app.get("/api/health", response_model=HealthResponse, tags=["meta"])
    def health() -> HealthResponse:
        return HealthResponse(version=__version__)

    @app.get("/api/environments", tags=["meta"])
    def environments() -> list[str]:
        return ["dev", "test", "prod"]

    @app.get("/api/config", response_model=ConfigResponse, tags=["meta"])
    def config(env: str = "dev") -> ConfigResponse:
        s = load_settings(env)
        return ConfigResponse(
            environment=s.environment,
            facilities=s.data.n_facilities,
            months=s.data.n_months,
            snapshot_days=s.data.snapshot_days,
            demo_cutoff_day=s.data.demo_cutoff_day,
            candidates=s.model.candidates,
            primary_metric=s.model.primary_metric,
            azure_ml_configured=s.azure_ml.is_configured(),
            fabric_configured=s.fabric.is_configured(),
        )

    # ---- Dataset ----
    @app.get("/api/dataset/overview", response_model=DatasetOverview, tags=["dataset"])
    def dataset_overview(env: str = "dev") -> DatasetOverview:
        overview = build_dataset_overview(_experience(env))
        return DatasetOverview(environment=env, **overview)  # type: ignore[arg-type]

    @app.get("/api/dataset/facility-series", response_model=FacilitySeries, tags=["dataset"])
    def facility_series(facility_id: str, env: str = "dev") -> FacilitySeries:
        state = _experience(env)
        if facility_id not in set(state.data["facility_id"]):
            raise HTTPException(status_code=404, detail=f"Unknown facility_id {facility_id!r}")
        series = facility_month_series(state, facility_id)
        points = [
            FacilityPoint(
                accounting_month=str(row.accounting_month),
                actual_month_end_net_revenue=float(row.actual_month_end_net_revenue),
            )
            for row in series.itertuples(index=False)
        ]
        return FacilitySeries(facility_id=facility_id, points=points)

    @app.get("/api/dataset/sample", tags=["dataset"])
    def dataset_sample(env: str = "dev", limit: int = 50) -> list[dict]:
        limit = max(1, min(limit, 500))
        frame = _experience(env).data.head(limit)
        return frame.to_dict(orient="records")

    # ---- Training ----
    @app.post("/api/train", response_model=TrainResponse, tags=["training"])
    def train(request: TrainRequest) -> TrainResponse:
        output = _training(request.environment)
        table = build_comparison_view(output)
        ranking = [
            ModelMetrics(
                model=str(r.model),
                wape=float(r.wape),
                bias=float(r.bias),
                mae=float(r.mae),
                rmse=float(r.rmse),
                mape=float(r.mape),
                smape=float(r.smape),
                r2=float(r.r2),
                is_champion=bool(r.is_champion),
            )
            for r in table.itertuples(index=False)
        ]
        champ = output.results[output.selection.champion]

        def _groups(frame, key: str) -> list[GroupMetrics]:
            return [
                GroupMetrics(
                    group=str(getattr(row, key)),
                    n=int(row.n),
                    wape=float(row.wape),
                    bias=float(row.bias),
                    mae=float(row.mae),
                    rmse=float(row.rmse),
                    mape=float(row.mape),
                    smape=float(row.smape),
                    r2=float(row.r2),
                )
                for row in frame.itertuples(index=False)
            ]

        return TrainResponse(
            environment=request.environment,
            metric=output.selection.metric,
            champion=output.selection.champion,
            challenger=output.selection.challenger,
            challenger_promotable=output.selection.challenger_promotable,
            ranking=ranking,
            by_facility=_groups(champ.by_facility, "facility_id"),
            by_snapshot_day=_groups(champ.by_snapshot_day, "snapshot_day"),
        )

    # ---- Education ----
    @app.get("/api/education/lessons", response_model=list[LessonModel], tags=["education"])
    def lessons() -> list[LessonModel]:
        return [
            LessonModel(
                key=lesson.key,
                title=lesson.title,
                summary=lesson.summary,
                body=lesson.body,
                references=lesson.references,
            )
            for lesson in get_lessons()
        ]

    @app.get(
        "/api/education/contextual-notes",
        response_model=list[ContextualNoteModel],
        tags=["education"],
    )
    def contextual_notes(area: str | None = None) -> list[ContextualNoteModel]:
        return [
            ContextualNoteModel(
                area=note.area,
                title=note.title,
                detail=note.detail,
                lesson_key=note.lesson_key,
                tip=note.tip,
            )
            for note in get_contextual_notes(area)
        ]

    @app.get(
        "/api/education/knowledge-checks",
        response_model=list[KnowledgeCheckModel],
        tags=["education"],
    )
    def knowledge_checks() -> list[KnowledgeCheckModel]:
        # Deliberately omit the correct answer; grading happens server-side.
        return [
            KnowledgeCheckModel(key=c.key, question=c.question, options=c.options)
            for c in get_knowledge_checks()
        ]

    @app.post(
        "/api/education/knowledge-checks/{key}/grade",
        response_model=GradeResponse,
        tags=["education"],
    )
    def grade(key: str, request: GradeRequest) -> GradeResponse:
        check = next((c for c in get_knowledge_checks() if c.key == key), None)
        if check is None:
            raise HTTPException(status_code=404, detail=f"Unknown knowledge check {key!r}")
        return GradeResponse(
            key=key,
            correct=grade_answer(check, request.chosen_index),
            correct_index=check.correct_index,
            explanation=check.explanation,
        )

    _mount_frontend(app)
    return app


def _mount_frontend(app: FastAPI) -> None:
    """Serve the built React app at ``/`` when present (single-command run)."""
    dist = _frontend_dist()
    if not dist.exists():

        @app.get("/", tags=["meta"])
        def _no_frontend() -> dict[str, str]:
            return {
                "message": (
                    "React frontend not built. Run `npm --prefix frontend install` "
                    "and `npm --prefix frontend run build`, or use the Vite dev server "
                    "(`npm --prefix frontend run dev`). API docs at /docs."
                )
            }

        return

    assets = dist / "assets"
    if assets.exists():
        app.mount("/assets", StaticFiles(directory=assets), name="assets")

    @app.get("/", include_in_schema=False)
    def _index() -> FileResponse:
        return FileResponse(dist / "index.html")

    # Client-side routing fallback for non-API, non-asset paths.
    @app.get("/{full_path:path}", include_in_schema=False)
    def _spa(full_path: str) -> FileResponse:
        candidate = dist / full_path
        if candidate.is_file():
            return FileResponse(candidate)
        return FileResponse(dist / "index.html")


app = create_app()
