"""Model factory mapping candidate names to estimators."""

from __future__ import annotations

from typing import Any

from sklearn.ensemble import HistGradientBoostingRegressor
from sklearn.linear_model import ElasticNet
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

from revenue_prediction.config.models import ModelConfig

from .baselines import PriorPeriodNaive, SeasonalNaive

# Names that consume RAW snapshot columns rather than engineered features.
BASELINE_MODELS = {"naive_prior", "seasonal_naive"}


def supported_models() -> list[str]:
    return [
        "naive_prior",
        "seasonal_naive",
        "elastic_net",
        "gradient_boosting",
        "hist_gradient_boosting",
        "random_forest",
        "xgboost",
    ]


def build_estimator(name: str, config: ModelConfig | None = None) -> Any:
    """Return an unfitted estimator for the given candidate ``name``."""
    config = config or ModelConfig()
    rs = config.random_state

    if name == "naive_prior":
        return PriorPeriodNaive()
    if name == "seasonal_naive":
        return SeasonalNaive()
    if name == "elastic_net":
        return Pipeline(
            [
                ("scale", StandardScaler()),
                ("model", ElasticNet(alpha=0.5, l1_ratio=0.3, max_iter=10000, random_state=rs)),
            ]
        )
    if name == "hist_gradient_boosting":
        params = dict(config.hgb_params)
        return HistGradientBoostingRegressor(random_state=rs, **params)
    if name == "gradient_boosting":
        # Classic sklearn Gradient Boosting Regressor (the reference default).
        from sklearn.ensemble import GradientBoostingRegressor

        params = dict(config.gbr_params)
        return GradientBoostingRegressor(random_state=rs, **params)
    if name == "random_forest":
        from sklearn.ensemble import RandomForestRegressor

        return RandomForestRegressor(n_estimators=300, max_depth=12, n_jobs=-1, random_state=rs)
    if name == "xgboost":
        try:
            from xgboost import XGBRegressor
        except ImportError as exc:  # pragma: no cover
            raise ImportError("xgboost is required for the 'xgboost' candidate") from exc
        params = dict(config.xgboost_params)
        return XGBRegressor(
            random_state=rs,
            n_jobs=-1,
            tree_method="hist",
            objective="reg:squarederror",
            **params,
        )
    raise ValueError(f"Unknown model candidate: {name!r}. Supported: {supported_models()}")
