"""Pydantic response/request models for the API.

These typed models keep the OpenAPI schema clean and decouple the HTTP surface
from internal dataframes.
"""

from __future__ import annotations

from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    status: str = "ok"
    version: str


class ConfigResponse(BaseModel):
    environment: str
    facilities: int
    months: int
    snapshot_days: list[int]
    demo_cutoff_day: int
    candidates: list[str]
    primary_metric: str
    azure_ml_configured: bool
    fabric_configured: bool


class DatasetOverview(BaseModel):
    environment: str
    rows: int
    facilities: list[str]
    months: list[str]
    snapshot_days: list[int]
    target_mean: float
    target_min: float
    target_max: float


class FacilityPoint(BaseModel):
    accounting_month: str
    actual_month_end_net_revenue: float


class FacilitySeries(BaseModel):
    facility_id: str
    points: list[FacilityPoint]


class ModelMetrics(BaseModel):
    model: str
    wape: float
    bias: float
    mae: float
    rmse: float
    mape: float
    smape: float
    r2: float
    is_champion: bool = False


class GroupMetrics(BaseModel):
    group: str
    n: int
    wape: float
    bias: float
    mae: float
    rmse: float
    mape: float
    smape: float
    r2: float


class TrainRequest(BaseModel):
    environment: str = Field(default="dev", pattern="^(dev|test|prod)$")


class TrainResponse(BaseModel):
    environment: str
    metric: str
    champion: str
    challenger: str | None
    challenger_promotable: bool
    ranking: list[ModelMetrics]
    by_facility: list[GroupMetrics]
    by_snapshot_day: list[GroupMetrics]


class LessonModel(BaseModel):
    key: str
    title: str
    summary: str
    body: str
    references: list[str]


class ContextualNoteModel(BaseModel):
    area: str
    title: str
    detail: str
    lesson_key: str | None = None
    tip: str | None = None


class KnowledgeCheckModel(BaseModel):
    """Knowledge check WITHOUT the correct answer (to avoid leaking it)."""

    key: str
    question: str
    options: list[str]


class GradeRequest(BaseModel):
    chosen_index: int = Field(ge=0)


class GradeResponse(BaseModel):
    key: str
    correct: bool
    correct_index: int
    explanation: str


class WalkthroughStepModel(BaseModel):
    key: str
    number: int
    phase: str
    title: str
    goal: str
    concept: str
    what_we_do: str
    interpret: str
    action: str
    lesson_key: str | None = None


class MetricTargetModel(BaseModel):
    checkpoint: str
    primary_metric: str
    target: str
    must_beat: str


class SuccessCriterionModel(BaseModel):
    category: str
    name: str
    target: str


class SuccessCriteriaModel(BaseModel):
    headline: str
    metric_targets: list[MetricTargetModel]
    criteria: list[SuccessCriterionModel]


class ReadinessDimensionModel(BaseModel):
    key: str
    dimension: str
    description: str
    default_rating: str
    is_gate: bool
    guidance: str


class SplitPreview(BaseModel):
    environment: str
    train_months: list[str]
    validation_months: list[str]
    test_months: list[str]
    train_rows: int
    validation_rows: int
    test_rows: int


class TargetPreviewItem(BaseModel):
    facility_id: str
    accounting_month: str
    snapshot_day: int
    gross_charges: float
    net_revenue: float
    gross_to_net_ratio: float


class TargetPreview(BaseModel):
    environment: str
    items: list[TargetPreviewItem]
    average_gross_to_net_ratio: float


class LeakageInfo(BaseModel):
    forbidden_columns: list[str]
    rules: list[str]


class FeaturePreview(BaseModel):
    environment: str
    raw_columns: list[str]
    engineered_features: list[str]
    n_raw: int
    n_engineered: int
    example: dict[str, float]


class ImportanceItem(BaseModel):
    feature: str
    importance: float


class ExplainResponse(BaseModel):
    environment: str
    model: str
    items: list[ImportanceItem]


class PredictionRow(BaseModel):
    facility_id: str
    accounting_month: str
    snapshot_date: str
    snapshot_day: int
    predicted_month_end_net_revenue: float
    actual_month_end_net_revenue: float | None = None
    abs_pct_error: float | None = None
    prediction_lower: float | None = None
    prediction_upper: float | None = None


class PredictPreview(BaseModel):
    environment: str
    model_name: str
    model_version: str
    run_id: str
    cutoff_day: int
    scored_at: str
    has_intervals: bool
    wape: float
    rows: list[PredictionRow]


class CleaningColumn(BaseModel):
    column: str
    missing_count: int
    missing_pct: float
    strategy: str


class CleaningPreview(BaseModel):
    environment: str
    rows: int
    columns_with_missing: list[CleaningColumn]
    outlier_note: str


class CorrelationItem(BaseModel):
    feature: str
    corr_with_target: float


class SkewItem(BaseModel):
    feature: str
    skewness: float


class EdaPreview(BaseModel):
    environment: str
    target: str
    correlations: list[CorrelationItem]
    skewness: list[SkewItem]


class OptimizeTrial(BaseModel):
    setting: str
    wape: float
    is_best: bool = False


class OptimizePreview(BaseModel):
    environment: str
    model: str
    hyperparameter: str
    trials: list[OptimizeTrial]
    best_setting: str
