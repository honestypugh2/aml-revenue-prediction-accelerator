"""Model evaluation: metrics and grouped accuracy reporting."""

from __future__ import annotations

from .kpi import (
    CheckpointTarget,
    KpiResult,
    beats_baseline,
    evaluate_checkpoint_targets,
    kpi_scorecard,
)
from .metrics import (
    bias,
    compute_metrics,
    metrics_by_facility,
    metrics_by_snapshot_day,
    smape,
    wape,
)
from .selection import Selection, comparison_table, select_champion_challenger

__all__ = [
    "CheckpointTarget",
    "KpiResult",
    "Selection",
    "beats_baseline",
    "bias",
    "comparison_table",
    "compute_metrics",
    "evaluate_checkpoint_targets",
    "kpi_scorecard",
    "metrics_by_facility",
    "metrics_by_snapshot_day",
    "select_champion_challenger",
    "smape",
    "wape",
]
