"""Azure Machine Learning pipeline (SDK v2, ``@pipeline``) — code-first training.

Builds a component-based pipeline job with the Python SDK v2 as an alternative
to the YAML pipeline in ``training-pipeline.yml``. Import of ``azure.ai.ml`` is
deferred so this module imports without the optional ``azure`` extra. Run it with
a live ``MLClient``:

    uv sync --extra azure
    python -m mlops.pipelines.azureml_pipeline   # requires configured workspace

See ``docs/patterns/aml-sdk.md``.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

_COMPONENT = Path(__file__).resolve().parent.parent / "components" / "train_code_first.yml"


def build_training_pipeline(training_data_asset: str, environment: str = "dev") -> Any:
    """Return a submittable Azure ML pipeline job (SDK v2 DSL).

    Requires the ``azure`` extra. Composes the registered training component into
    a single-step pipeline; extend with a data-prep step as needed.
    """
    try:
        from azure.ai.ml import Input
        from azure.ai.ml.constants import AssetTypes
        from azure.ai.ml.dsl import pipeline
        from azure.ai.ml import load_component
    except ImportError as exc:  # pragma: no cover - requires azure extra
        raise ImportError(
            "Azure ML SDK v2 not installed. Install the 'azure' extra: `uv sync --extra azure`."
        ) from exc

    train_component = load_component(source=str(_COMPONENT))

    @pipeline(  # type: ignore[misc]
        name="revenue_code_first_pipeline",
        description="Train and select the net-revenue champion (code-first).",
    )
    def _revenue_pipeline(training_data: Any, environment_name: str):
        train_step = train_component(
            training_data=training_data,
            environment_name=environment_name,
        )
        return {"model_dir": train_step.outputs.model_dir}

    return _revenue_pipeline(
        training_data=Input(type=AssetTypes.URI_FILE, path=training_data_asset),
        environment_name=environment,
    )


def submit_training_pipeline(  # pragma: no cover - requires live workspace
    ml_client: Any,
    training_data_asset: str,
    compute: str,
    environment: str = "dev",
) -> Any:
    """Submit the pipeline to Azure ML and return the job handle."""
    job = build_training_pipeline(training_data_asset, environment=environment)
    job.settings.default_compute = compute
    return ml_client.jobs.create_or_update(job)


if __name__ == "__main__":  # pragma: no cover
    from revenue_prediction.integrations.azureml.client import get_ml_client
    from revenue_prediction.config.loader import load_settings

    settings = load_settings("dev")
    client = get_ml_client(settings.azure_ml)
    submitted = submit_training_pipeline(
        client,
        training_data_asset="azureml:revenue_snapshots@latest",
        compute=settings.azure_ml.compute_cluster,
    )
    print(submitted.studio_url)
