"""Model evaluation: metrics and grouped accuracy reporting."""

from __future__ import annotations

from .metrics import (
    compute_metrics,
    metrics_by_facility,
    metrics_by_snapshot_day,
    smape,
)
from .selection import Selection, comparison_table, select_champion_challenger

__all__ = [
    "Selection",
    "comparison_table",
    "compute_metrics",
    "metrics_by_facility",
    "metrics_by_snapshot_day",
    "select_champion_challenger",
    "smape",
]
