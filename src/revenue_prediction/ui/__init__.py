"""Framework-agnostic UI logic.

The heavy logic lives in :mod:`revenue_prediction.ui.experience` (pure, testable
functions with no web-framework dependency). It backs the FastAPI service in
:mod:`revenue_prediction.api`, which in turn serves the React frontend.
"""

from __future__ import annotations

from .experience import (
    ExperienceState,
    build_comparison_view,
    build_dataset_overview,
    facility_month_series,
    load_experience,
    run_training_experience,
)

__all__ = [
    "ExperienceState",
    "build_comparison_view",
    "build_dataset_overview",
    "facility_month_series",
    "load_experience",
    "run_training_experience",
]
