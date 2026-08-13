"""Azure Machine Learning Automated ML (SDK v2) regression integration.

Builds and (optionally) submits an AutoML *regression* job to predict
``actual_month_end_net_revenue`` using the Azure ML Python SDK v2 exclusively
(no deprecated SDK v1 APIs).

Imports of ``azure.ai.ml`` are deferred so this module can be imported and unit
tested without the optional ``azure`` extra installed. Nothing here contacts
Azure unless :func:`submit_automl_job` is called with a live ``MLClient``.

Overfitting / imbalanced-data guidance (per Microsoft docs) is applied via
cross-validation, automatic featurization, and early termination. See
``docs/patterns/automl-sdk.md`` and ``docs/modeling/automl.md``.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

from revenue_prediction.config.models import AutoMLConfig, AzureMLConfig
from revenue_prediction.core.data.schema import TARGET

if TYPE_CHECKING:  # pragma: no cover
    from azure.ai.ml import MLClient


@dataclass
class AutoMLJobSpec:
    """A cloud-agnostic description of the AutoML job to submit."""

    experiment_name: str
    target_column: str
    primary_metric: str
    compute: str
    training_data_asset: str
    validation_data_asset: str | None
    timeout_minutes: int
    trial_timeout_minutes: int
    max_trials: int
    max_concurrent_trials: int
    n_cross_validations: int
    enable_early_termination: bool
    featurization_mode: str = "auto"


def build_automl_job_spec(
    automl: AutoMLConfig,
    azure_ml: AzureMLConfig,
    training_data_asset: str,
    validation_data_asset: str | None = None,
) -> AutoMLJobSpec:
    """Create a validated, serializable AutoML job specification."""
    return AutoMLJobSpec(
        experiment_name=automl.experiment_name,
        target_column=TARGET,
        primary_metric=automl.primary_metric,
        compute=azure_ml.compute_cluster,
        training_data_asset=training_data_asset,
        validation_data_asset=validation_data_asset,
        timeout_minutes=automl.timeout_minutes,
        trial_timeout_minutes=automl.trial_timeout_minutes,
        max_trials=automl.max_trials,
        max_concurrent_trials=automl.max_concurrent_trials,
        n_cross_validations=automl.n_cross_validations,
        enable_early_termination=automl.enable_early_termination,
    )


def build_regression_job(spec: AutoMLJobSpec) -> Any:
    """Construct an Azure ML AutoML regression job object (SDK v2).

    Requires the ``azure`` extra. Returns an ``azure.ai.ml.automl`` job that can
    be submitted with an ``MLClient``.
    """
    try:
        from azure.ai.ml import Input, automl
        from azure.ai.ml.constants import AssetTypes
    except ImportError as exc:  # pragma: no cover - requires azure extra
        raise ImportError(
            "Azure ML SDK v2 not installed. Install the 'azure' extra: `uv sync --extra azure`."
        ) from exc

    training_input = Input(type=AssetTypes.MLTABLE, path=spec.training_data_asset)
    regression_job = automl.regression(
        compute=spec.compute,
        experiment_name=spec.experiment_name,
        training_data=training_input,
        target_column_name=spec.target_column,
        primary_metric=spec.primary_metric,
        n_cross_validations=spec.n_cross_validations,
        enable_model_explainability=True,
    )
    if spec.validation_data_asset:
        regression_job.set_data(
            training_data=training_input,
            target_column_name=spec.target_column,
            validation_data=Input(type=AssetTypes.MLTABLE, path=spec.validation_data_asset),
        )
    # Automatic featurization + cross-validation + early termination guard
    # against overfitting and imbalanced data (Microsoft AutoML guidance).
    regression_job.set_featurization(mode=spec.featurization_mode)
    regression_job.set_limits(
        timeout_minutes=spec.timeout_minutes,
        trial_timeout_minutes=spec.trial_timeout_minutes,
        max_trials=spec.max_trials,
        max_concurrent_trials=spec.max_concurrent_trials,
        enable_early_termination=spec.enable_early_termination,
    )
    return regression_job


def submit_automl_job(ml_client: MLClient, spec: AutoMLJobSpec) -> Any:  # pragma: no cover
    """Submit the AutoML job to Azure ML. Requires live credentials.

    Deliberately excluded from offline tests. Returns the submitted job handle.
    """
    job = build_regression_job(spec)
    return ml_client.jobs.create_or_update(job)
