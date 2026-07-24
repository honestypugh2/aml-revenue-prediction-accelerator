"""Local training: temporal splitting, model factory, and orchestration."""

from __future__ import annotations

from .splitting import (
    TemporalSplit,
    blocked_temporal_split,
    expanding_window_folds,
    rolling_origin_folds,
)
from .train import TrainingResult, train_all_candidates, train_candidate

__all__ = [
    "TemporalSplit",
    "TrainingResult",
    "blocked_temporal_split",
    "expanding_window_folds",
    "rolling_origin_folds",
    "train_all_candidates",
    "train_candidate",
]
