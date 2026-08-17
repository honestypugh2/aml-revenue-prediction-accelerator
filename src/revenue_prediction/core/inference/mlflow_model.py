"""MLflow model wrapper for leakage-safe raw-snapshot inference."""

from __future__ import annotations

from typing import Any

import mlflow.pyfunc
import pandas as pd

from revenue_prediction.core.inference.predict import ModelBundle, batch_predict


class RevenuePredictionModel(mlflow.pyfunc.PythonModel):  # pyright: ignore[reportPrivateImportUsage]
    """MLflow pyfunc implementation that packages preprocessing with the estimator."""

    def __init__(self, bundle: ModelBundle) -> None:
        self.bundle = bundle

    def predict(
        self,
        context: Any,
        model_input: pd.DataFrame,
        params: dict[str, Any] | None = None,
    ) -> pd.DataFrame:
        cutoff_day = None if params is None else params.get("cutoff_day")
        return batch_predict(self.bundle, model_input, cutoff_day=cutoff_day)


def inference_requirements() -> list[str]:
    """Return constrained dependencies for the portable MLflow model environment."""
    return [
        "mlflow==2.22.5",
        "cloudpickle>=3.0,<4.0",
        "numpy>=1.26,<3.0",
        "pandas>=2.1,<3.0",
        "pyarrow>=15,<20",
        "scikit-learn>=1.4,<2.0",
        "xgboost>=2.0,<3.0",
        "python-dateutil>=2.9",
        "pydantic>=2.6,<3.0",
        "pyyaml>=6.0",
    ]