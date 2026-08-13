"""Azure Machine Learning Automated ML (SDK v2) integration.

Public API for building and submitting AutoML regression jobs. Implementation
lives in :mod:`revenue_prediction.integrations.automl.regression`; this package initializer
only re-exports the public names.
"""

from __future__ import annotations

from .regression import (
    AutoMLJobSpec,
    build_automl_job_spec,
    build_regression_job,
    submit_automl_job,
)

__all__ = [
    "AutoMLJobSpec",
    "build_automl_job_spec",
    "build_regression_job",
    "submit_automl_job",
]
