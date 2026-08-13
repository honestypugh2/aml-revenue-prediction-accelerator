"""Azure ML command-job builders and model registration (SDK v2)."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from revenue_prediction.config.models import AzureMLConfig

if TYPE_CHECKING:  # pragma: no cover
    from azure.ai.ml import MLClient


def build_command_job(
    azure_ml: AzureMLConfig,
    training_data_asset: str,
    environment: str,
    code_dir: str = "src",
    command_override: str | None = None,
) -> Any:
    """Build an Azure ML command job that runs the code-first trainer.

    The job invokes :mod:`revenue_prediction.core.training.azureml_entry` on the
    configured compute cluster. Requires the ``azure`` extra.
    """
    try:
        from azure.ai.ml import Input, command
        from azure.ai.ml.constants import AssetTypes
    except ImportError as exc:  # pragma: no cover
        raise ImportError("Install the 'azure' extra: `uv sync --extra azure`.") from exc

    default_command = (
        "python -m revenue_prediction.core.training.azureml_entry "
        "--data ${{inputs.training_data}} --output ${{outputs.model_dir}}"
    )
    return command(
        code=code_dir,
        command=command_override or default_command,
        inputs={"training_data": Input(type=AssetTypes.URI_FILE, path=training_data_asset)},
        environment=environment,
        compute=azure_ml.compute_cluster,
        experiment_name="revenue-code-first",
        display_name="revenue-code-first-training",
    )


def register_model_from_run(  # pragma: no cover - needs azure
    ml_client: MLClient,
    run_name: str,
    azure_ml: AzureMLConfig,
    model_path: str = "model",
) -> Any:
    """Register the model produced by a completed job run.

    Uses the MLflow model produced by the training job. Returns the registered
    model object.
    """
    try:
        from azure.ai.ml.constants import AssetTypes
        from azure.ai.ml.entities import Model
    except ImportError as exc:
        raise ImportError("Install the 'azure' extra: `uv sync --extra azure`.") from exc

    model = Model(
        path=f"azureml://jobs/{run_name}/outputs/artifacts/paths/{model_path}",
        name=azure_ml.registered_model_name,
        type=AssetTypes.MLFLOW_MODEL,
        description="Champion net-revenue regression model (facility-month-snapshot grain).",
    )
    return ml_client.models.create_or_update(model)
