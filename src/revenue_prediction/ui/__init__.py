"""Interactive educational / workshop UI (Streamlit).

The heavy logic lives in :mod:`revenue_prediction.ui.experience` (pure, testable
functions with no Streamlit dependency). ``app.py`` is a thin presentation layer.
"""

from __future__ import annotations

from .experience import (
    ExperienceState,
    build_comparison_view,
    build_dataset_overview,
    run_training_experience,
)

__all__ = [
    "ExperienceState",
    "build_comparison_view",
    "build_dataset_overview",
    "run_training_experience",
]
