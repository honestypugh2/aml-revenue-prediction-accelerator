"""Tag registered model versions with their authoring pattern and register the
AutoML best model under the same governed model name.

After this runs, the Azure ML **Models -> Versions** view shows both authoring
paths side by side via the ``authoring_pattern`` tag (``code_first`` / ``automl``).

Prerequisites:
    uv sync --extra azure
    az login --tenant <your-tenant>     # must match the subscription's tenant
    export RPA_AZURE_ML__SUBSCRIPTION_ID=... RPA_AZURE_ML__RESOURCE_GROUP=... \
           RPA_AZURE_ML__WORKSPACE_NAME=...

Usage:
    python scripts/tag_and_register_models.py --automl-job <automl_parent_job_name>
"""

from __future__ import annotations

import argparse

from revenue_prediction.config.loader import load_settings
from revenue_prediction.integrations.azureml.client import get_ml_client


def _best_automl_child(client, parent_job_name: str) -> str:
    """Return the AutoML child job with the best (lowest NRMSE) score."""
    scored: list[tuple[float, str]] = []
    for child in client.jobs.list(parent_job_name=parent_job_name):
        score = (getattr(child, "properties", {}) or {}).get("score")
        if score is None:
            continue
        try:
            scored.append((float(score), child.name))
        except ValueError:
            continue
    if not scored:
        raise SystemExit(f"No scored AutoML children found under {parent_job_name!r}")
    scored.sort()  # NRMSE: lower is better
    return scored[0][1]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--env", default="dev")
    parser.add_argument("--automl-job", required=True, help="AutoML parent job name")
    parser.add_argument(
        "--code-first-versions",
        nargs="*",
        default=["1", "2"],
        help="Existing versions to tag as code_first",
    )
    args = parser.parse_args()

    settings = load_settings(args.env)
    client = get_ml_client(settings.azure_ml)
    name = settings.azure_ml.registered_model_name

    # 1. Tag existing code-first versions.
    for version in args.code_first_versions:
        model = client.models.get(name=name, version=version)
        model.tags = {**(model.tags or {}), "authoring_pattern": "code_first"}
        client.models.create_or_update(model)
        print(f"tagged {name}:{version} authoring_pattern=code_first")

    # 2. Register the AutoML best model under the same governed name.
    best_child = _best_automl_child(client, args.automl_job)
    print(f"AutoML best child = {best_child}")

    from azure.ai.ml.constants import AssetTypes
    from azure.ai.ml.entities import Model

    automl_model = Model(
        path=f"azureml://jobs/{best_child}/outputs/artifacts/paths/outputs/mlflow-model/",
        name=name,
        type=AssetTypes.MLFLOW_MODEL,
        description="AutoML best net-revenue regression model.",
        tags={"authoring_pattern": "automl", "source_job": best_child},
    )
    registered = client.models.create_or_update(automl_model)
    print(f"registered {name}:{registered.version} authoring_pattern=automl")


if __name__ == "__main__":
    main()
