"""Model definitions: baselines and code-first regression estimators.

Net-revenue prediction from partial-month snapshots is primarily a *structured
regression* problem, so the default candidates are regression models plus
simple, strong baselines. A recurrent (LSTM) approach is intentionally NOT the
default; see ``docs/modeling`` and ADR 0003 for the justification.
"""

from __future__ import annotations

from .baselines import PriorPeriodNaive, SeasonalNaive
from .factory import build_estimator, supported_models

__all__ = [
    "PriorPeriodNaive",
    "SeasonalNaive",
    "build_estimator",
    "supported_models",
]
