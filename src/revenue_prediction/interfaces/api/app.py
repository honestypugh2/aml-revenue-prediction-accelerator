"""FastAPI backend that serves the React educational UI over the Python core.

Runs fully offline on synthetic data. No Azure/Fabric calls are made here. Start
with:

    uv run revenue-prediction serve            # via the CLI
    uv run uvicorn revenue_prediction.interfaces.api.app:app --reload

The built React app (``frontend/dist``) is served at ``/`` when present; the API
lives under ``/api``. In development the Vite dev server proxies ``/api`` here.
"""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from revenue_prediction import __version__
from revenue_prediction.config.loader import load_settings
from revenue_prediction.education import (
    SUCCESS_HEADLINE,
    get_contextual_notes,
    get_knowledge_checks,
    get_lessons,
    get_metric_targets,
    get_readiness_dimensions,
    get_success_criteria,
    get_walkthrough,
    grade_answer,
)
from revenue_prediction.interfaces.ui.experience import (
    ExperienceState,
    build_comparison_view,
    build_dataset_overview,
    facility_month_series,
    load_experience,
    run_training_experience,
)

from .schemas import (
    CleaningColumn,
    CleaningPreview,
    ConfigResponse,
    ContextualNoteModel,
    CorrelationItem,
    DatasetOverview,
    EdaPreview,
    ExplainResponse,
    FacilityPoint,
    FacilitySeries,
    FeaturePreview,
    GradeRequest,
    GradeResponse,
    GroupMetrics,
    HealthResponse,
    ImportanceItem,
    KnowledgeCheckModel,
    LeakageInfo,
    LessonModel,
    MetricTargetModel,
    ModelMetrics,
    OptimizePreview,
    OptimizeTrial,
    PredictionRow,
    PredictPreview,
    ReadinessDimensionModel,
    SkewItem,
    SplitPreview,
    SuccessCriteriaModel,
    SuccessCriterionModel,
    TargetPreview,
    TargetPreviewItem,
    TrainRequest,
    TrainResponse,
    WalkthroughStepModel,
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


@lru_cache(maxsize=8)
def _explain(environment: str, top: int) -> tuple[str, list[tuple[str, float]]]:
    """Permutation importance for the champion on the held-out test split."""
    from revenue_prediction.core.data.schema import FEATURE_COLUMNS, TARGET
    from revenue_prediction.core.evaluation.explainability import permutation_feature_importance

    state = _experience(environment)
    output = _training(environment)
    # Explain the best model that actually engineers features; if the champion
    # is a naive baseline, fall back to the top-ranked learned model so the
    # importance chart is instructive.
    champ = output.results[output.selection.champion]
    if champ.feature_builder is None:
        for name in output.selection.ranking["model"].tolist():
            candidate = output.results[str(name)]
            if candidate.feature_builder is not None:
                champ = candidate
                break
    if champ.feature_builder is None:
        return output.selection.champion, [("prior_period_baseline", 1.0)]

    from revenue_prediction.core.training.splitting import blocked_temporal_split

    split = blocked_temporal_split(state.data, state.settings.split)
    raw = [c for c in FEATURE_COLUMNS if c in split.test.columns]
    x_test = champ.feature_builder.transform(split.test[raw])
    y_test = split.test[TARGET]
    frame = permutation_feature_importance(champ.estimator, x_test, y_test, n_repeats=5)
    items = [
        (str(r.feature), float(r.importance_mean)) for r in frame.head(top).itertuples(index=False)
    ]
    return champ.name, items


@lru_cache(maxsize=16)
def _predict(environment: str, cutoff_day: int, limit: int):
    """Score held-out test snapshots at a cutoff day with the champion bundle.

    Mirrors a production batch job: the champion scores an as-of snapshot and
    returns self-describing predictions. Actuals are joined only for teaching
    (in production they are known later, after close).
    """
    import numpy as np

    from revenue_prediction.core.data.schema import TARGET
    from revenue_prediction.core.inference.predict import batch_predict
    from revenue_prediction.core.training.splitting import blocked_temporal_split

    state = _experience(environment)
    output = _training(environment)
    bundle = output.champion_bundle

    split = blocked_temporal_split(state.data, state.settings.split)
    at_cutoff = split.test[split.test["snapshot_day"] == cutoff_day]
    if at_cutoff.empty:
        at_cutoff = split.test[split.test["snapshot_day"] == state.settings.data.demo_cutoff_day]

    scored = batch_predict(bundle, at_cutoff, cutoff_day=cutoff_day).reset_index(drop=True)
    actual = at_cutoff[TARGET].to_numpy(dtype=float)
    pred = scored["predicted_month_end_net_revenue"].to_numpy(dtype=float)

    denom = float(np.sum(np.abs(actual)))
    wape = float(np.sum(np.abs(actual - pred)) / denom) if denom else float("nan")
    ape = np.where(actual != 0, np.abs(actual - pred) / np.abs(actual), np.nan)

    has_intervals = "prediction_lower" in scored.columns
    rows = []
    for i, row in enumerate(scored.head(limit).itertuples(index=False)):
        rows.append(
            {
                "facility_id": str(row.facility_id),
                "accounting_month": str(row.accounting_month),
                "snapshot_date": str(row.snapshot_date),
                "snapshot_day": int(row.snapshot_day),
                "predicted": round(float(pred[i]), 2),
                "actual": round(float(actual[i]), 2),
                "abs_pct_error": None if np.isnan(ape[i]) else round(float(ape[i]), 4),
                "lower": round(float(row.prediction_lower), 2) if has_intervals else None,
                "upper": round(float(row.prediction_upper), 2) if has_intervals else None,
            }
        )
    meta = {
        "model_name": str(scored["model_name"].iloc[0]),
        "model_version": str(scored["model_version"].iloc[0]),
        "run_id": str(scored["run_id"].iloc[0]),
        "scored_at": str(scored["scored_at"].iloc[0]),
        "has_intervals": has_intervals,
        "wape": round(wape, 6),
    }
    return meta, rows


@lru_cache(maxsize=8)
def _optimize(environment: str) -> tuple[str, str, list[tuple[str, float]]]:
    """Small hyperparameter sweep to demonstrate optimization/tuning.

    Trains histogram gradient boosting at a few learning rates on the split and
    reports test-block WAPE per setting, so learners see how tuning moves the
    metric. Kept small so it runs quickly.
    """
    import numpy as np

    from revenue_prediction.core.data.schema import TARGET
    from revenue_prediction.core.evaluation.metrics import wape as wape_fn
    from revenue_prediction.core.features.engineering import LeakageSafeFeatureBuilder
    from revenue_prediction.core.models.factory import build_estimator
    from revenue_prediction.core.training.splitting import blocked_temporal_split

    state = _experience(environment)
    split = blocked_temporal_split(state.data, state.settings.split)
    from revenue_prediction.core.data.schema import FEATURE_COLUMNS

    keep = [c for c in FEATURE_COLUMNS if c in split.train.columns]
    builder = LeakageSafeFeatureBuilder(state.settings.features)
    builder.fit(split.train[keep])
    x_train = builder.transform(split.train[keep])
    x_test = builder.transform(split.test[keep])
    y_train = split.train[TARGET].to_numpy(dtype=float)
    y_test = split.test[TARGET].to_numpy(dtype=float)

    trials: list[tuple[str, float]] = []
    for lr in (0.03, 0.05, 0.1, 0.2):
        cfg = state.settings.model.model_copy(deep=True)
        cfg.hgb_params = {**cfg.hgb_params, "learning_rate": lr}
        est = build_estimator("hist_gradient_boosting", cfg)
        est.fit(x_train, y_train)
        pred = np.asarray(est.predict(x_test), dtype=float)
        trials.append((f"learning_rate={lr}", round(wape_fn(y_test, pred), 6)))
    return "hist_gradient_boosting", "learning_rate", trials


def _frontend_dist() -> Path:
    # repo_root/frontend/dist
    # (.../src/revenue_prediction/interfaces/api/app.py -> parents[4] = repo root)
    return Path(__file__).resolve().parents[4] / "frontend" / "dist"


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

    # ---- Guided walkthrough (learn-by-building curriculum) ----
    @app.get(
        "/api/education/walkthrough",
        response_model=list[WalkthroughStepModel],
        tags=["education"],
    )
    def walkthrough() -> list[WalkthroughStepModel]:
        return [
            WalkthroughStepModel(
                key=s.key,
                number=s.number,
                phase=s.phase,
                title=s.title,
                goal=s.goal,
                concept=s.concept,
                what_we_do=s.what_we_do,
                interpret=s.interpret,
                action=s.action,
                lesson_key=s.lesson_key,
            )
            for s in get_walkthrough()
        ]

    @app.get(
        "/api/education/success-criteria",
        response_model=SuccessCriteriaModel,
        tags=["education"],
    )
    def success_criteria() -> SuccessCriteriaModel:
        return SuccessCriteriaModel(
            headline=SUCCESS_HEADLINE,
            metric_targets=[
                MetricTargetModel(
                    checkpoint=t.checkpoint,
                    primary_metric=t.primary_metric,
                    target=t.target,
                    must_beat=t.must_beat,
                )
                for t in get_metric_targets()
            ],
            criteria=[
                SuccessCriterionModel(category=c.category, name=c.name, target=c.target)
                for c in get_success_criteria()
            ],
        )

    @app.get(
        "/api/education/data-readiness",
        response_model=list[ReadinessDimensionModel],
        tags=["education"],
    )
    def data_readiness() -> list[ReadinessDimensionModel]:
        return [
            ReadinessDimensionModel(
                key=d.key,
                dimension=d.dimension,
                description=d.description,
                default_rating=d.default_rating,
                is_gate=d.is_gate,
                guidance=d.guidance,
            )
            for d in get_readiness_dimensions()
        ]

    # ---- Pipeline steps that power the walkthrough actions ----
    @app.get("/api/pipeline/leakage", response_model=LeakageInfo, tags=["pipeline"])
    def leakage(env: str = "dev") -> LeakageInfo:
        settings = load_settings(env)
        return LeakageInfo(
            forbidden_columns=settings.features.forbidden_future_columns,
            rules=[
                "days_elapsed must equal snapshot_day (no future information).",
                "snapshot_date must fall within its accounting_month.",
                "The target is constant within a facility-month (known only after close).",
                "Historical features use only strictly-prior closed months.",
                "Preprocessing statistics are fit on the training split only.",
            ],
        )

    @app.get("/api/pipeline/target", response_model=TargetPreview, tags=["pipeline"])
    def target_preview(env: str = "dev", limit: int = 8) -> TargetPreview:
        import pandas as pd

        from revenue_prediction.core.data.schema import TARGET

        df = _experience(env).data
        cutoff = load_settings(env).data.demo_cutoff_day
        at_cutoff = df[df["snapshot_day"] == cutoff]
        sample = at_cutoff.head(max(1, min(limit, 50)))
        items: list[TargetPreviewItem] = []
        ratios: list[float] = []
        for row in sample.itertuples(index=False):
            gross = float(row.month_to_date_gross_charges)
            net = float(getattr(row, TARGET))
            ratio = gross / net if net else float("nan")
            if net:
                ratios.append(ratio)
            items.append(
                TargetPreviewItem(
                    facility_id=str(row.facility_id),
                    accounting_month=str(row.accounting_month),
                    snapshot_day=int(row.snapshot_day),
                    gross_charges=round(gross, 2),
                    net_revenue=round(net, 2),
                    gross_to_net_ratio=round(ratio, 3),
                )
            )
        avg = float(pd.Series(ratios).mean()) if ratios else float("nan")
        return TargetPreview(environment=env, items=items, average_gross_to_net_ratio=round(avg, 3))

    @app.get("/api/pipeline/split", response_model=SplitPreview, tags=["pipeline"])
    def split_preview(env: str = "dev") -> SplitPreview:
        from revenue_prediction.core.training.splitting import blocked_temporal_split

        state = _experience(env)
        split = blocked_temporal_split(state.data, state.settings.split)
        return SplitPreview(
            environment=env,
            train_months=split.train_months,
            validation_months=split.validation_months,
            test_months=split.test_months,
            train_rows=int(len(split.train)),
            validation_rows=int(len(split.validation)),
            test_rows=int(len(split.test)),
        )

    @app.get("/api/pipeline/features", response_model=FeaturePreview, tags=["pipeline"])
    def features_preview(env: str = "dev") -> FeaturePreview:
        from revenue_prediction.core.data.schema import FEATURE_COLUMNS
        from revenue_prediction.core.features.engineering import LeakageSafeFeatureBuilder
        from revenue_prediction.core.training.splitting import blocked_temporal_split

        state = _experience(env)
        split = blocked_temporal_split(state.data, state.settings.split)
        raw = [c for c in FEATURE_COLUMNS if c in split.train.columns]
        builder = LeakageSafeFeatureBuilder(state.settings.features)
        builder.fit(split.train[raw])
        engineered = builder.transform(split.train[raw])
        first = engineered.iloc[0]
        # A small, illustrative slice of engineered features.
        example_keys = [
            k
            for k in [
                "mtd_collection_ratio",
                "mtd_denial_ratio",
                "mtd_adjustment_ratio",
                "fraction_month_elapsed",
                "mtd_gross_run_rate",
            ]
            if k in engineered.columns
        ]
        example = {k: round(float(first[k]), 4) for k in example_keys}
        return FeaturePreview(
            environment=env,
            raw_columns=raw,
            engineered_features=list(engineered.columns),
            n_raw=len(raw),
            n_engineered=int(engineered.shape[1]),
            example=example,
        )

    @app.get("/api/pipeline/explain", response_model=ExplainResponse, tags=["pipeline"])
    def explain(env: str = "dev", top: int = 12) -> ExplainResponse:
        importance = _explain(env, top)
        return ExplainResponse(
            environment=env,
            model=importance[0],
            items=[ImportanceItem(feature=f, importance=round(v, 6)) for f, v in importance[1]],
        )

    @app.get("/api/pipeline/predict", response_model=PredictPreview, tags=["pipeline"])
    def predict_preview(env: str = "dev", cutoff_day: int = 0, limit: int = 8) -> PredictPreview:
        day = cutoff_day if cutoff_day > 0 else load_settings(env).data.demo_cutoff_day
        meta, rows = _predict(env, day, max(1, min(limit, 50)))
        return PredictPreview(
            environment=env,
            model_name=meta["model_name"],
            model_version=meta["model_version"],
            run_id=meta["run_id"],
            cutoff_day=day,
            scored_at=meta["scored_at"],
            has_intervals=bool(meta["has_intervals"]),
            wape=float(meta["wape"]),
            rows=[
                PredictionRow(
                    facility_id=r["facility_id"],
                    accounting_month=r["accounting_month"],
                    snapshot_date=r["snapshot_date"],
                    snapshot_day=r["snapshot_day"],
                    predicted_month_end_net_revenue=r["predicted"],
                    actual_month_end_net_revenue=r["actual"],
                    abs_pct_error=r["abs_pct_error"],
                    prediction_lower=r["lower"],
                    prediction_upper=r["upper"],
                )
                for r in rows
            ],
        )

    @app.get("/api/pipeline/cleaning", response_model=CleaningPreview, tags=["pipeline"])
    def cleaning_preview(env: str = "dev") -> CleaningPreview:
        import numpy as np

        df = _experience(env).data
        cols: list[CleaningColumn] = []
        for c in df.columns:
            miss = int(df[c].isna().sum())
            if miss:
                cols.append(
                    CleaningColumn(
                        column=c,
                        missing_count=miss,
                        missing_pct=round(miss / len(df), 4),
                        strategy="median imputation (fit on training split only)",
                    )
                )
        cols.sort(key=lambda x: x.missing_count, reverse=True)
        gross = df["month_to_date_gross_charges"].to_numpy(dtype=float)
        hi = float(np.nanpercentile(gross, 99))
        n_out = int((gross > hi * 1.5).sum())
        return CleaningPreview(
            environment=env,
            rows=int(len(df)),
            columns_with_missing=cols,
            outlier_note=(
                f"~{n_out} extreme gross-charge outliers flagged (> 1.5x the 99th pct). "
                "Trees tolerate them; ratios and run-rate are guarded against divide-by-zero."
            ),
        )

    @app.get("/api/pipeline/eda", response_model=EdaPreview, tags=["pipeline"])
    def eda_preview(env: str = "dev", top: int = 10) -> EdaPreview:
        from revenue_prediction.core.data.schema import OPERATIONAL_FEATURES, TARGET

        df = _experience(env).data
        numeric = [c for c in OPERATIONAL_FEATURES if c in df.columns]
        corr = (
            df[numeric + [TARGET]]
            .corr(numeric_only=True)[TARGET]
            .drop(labels=[TARGET])
            .sort_values(key=lambda s: s.abs(), ascending=False)
        )
        correlations = [
            CorrelationItem(feature=str(k), corr_with_target=round(float(v), 4))
            for k, v in corr.head(top).items()
        ]
        skew = (
            df[numeric].skew(numeric_only=True).sort_values(key=lambda s: s.abs(), ascending=False)
        )
        skewness = [
            SkewItem(feature=str(k), skewness=round(float(v), 3)) for k, v in skew.head(top).items()
        ]
        return EdaPreview(
            environment=env, target=TARGET, correlations=correlations, skewness=skewness
        )

    @app.get("/api/pipeline/optimize", response_model=OptimizePreview, tags=["pipeline"])
    def optimize_preview(env: str = "dev") -> OptimizePreview:
        model, hp, trials = _optimize(env)
        best = min(trials, key=lambda t: t[1])[0]
        return OptimizePreview(
            environment=env,
            model=model,
            hyperparameter=hp,
            trials=[OptimizeTrial(setting=s, wape=w, is_best=(s == best)) for s, w in trials],
            best_setting=best,
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
