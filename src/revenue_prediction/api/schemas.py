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
