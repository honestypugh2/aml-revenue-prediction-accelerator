"""Unit tests for the model factory (including the gradient_boosting candidate)."""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from revenue_prediction.core.models.factory import build_estimator, supported_models

pytestmark = pytest.mark.unit


def test_gradient_boosting_is_supported() -> None:
    assert "gradient_boosting" in supported_models()


def test_gradient_boosting_builds_and_fits() -> None:
    est = build_estimator("gradient_boosting")
    rng = np.random.default_rng(0)
    X = pd.DataFrame(rng.normal(size=(60, 4)), columns=["a", "b", "c", "d"])
    y = X["a"] * 2.0 + rng.normal(scale=0.1, size=60)
    est.fit(X, y)
    preds = est.predict(X)
    assert len(preds) == 60


def test_unknown_model_raises() -> None:
    with pytest.raises(ValueError, match="Unknown model candidate"):
        build_estimator("not_a_model")
