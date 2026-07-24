"""Model explainability helpers (offline, model-agnostic)."""

from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.inspection import permutation_importance


def permutation_feature_importance(
    estimator,
    X: pd.DataFrame,
    y,
    n_repeats: int = 10,
    random_state: int = 42,
) -> pd.DataFrame:
    """Return permutation importances as a sorted dataframe.

    Model-agnostic and leakage-aware: it should be computed on a held-out set,
    never on the training data used to fit the estimator.
    """
    result = permutation_importance(
        estimator, X, np.asarray(y, dtype=float), n_repeats=n_repeats, random_state=random_state
    )
    frame = pd.DataFrame(
        {
            "feature": list(X.columns),
            "importance_mean": result.importances_mean,
            "importance_std": result.importances_std,
        }
    )
    return frame.sort_values("importance_mean", ascending=False).reset_index(drop=True)


def native_feature_importance(estimator, feature_names: list[str]) -> pd.DataFrame | None:
    """Return native feature importances if the estimator exposes them."""
    importances = getattr(estimator, "feature_importances_", None)
    if importances is None:
        return None
    frame = pd.DataFrame({"feature": feature_names, "importance": importances})
    return frame.sort_values("importance", ascending=False).reset_index(drop=True)
