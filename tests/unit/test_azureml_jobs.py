"""Unit tests for Azure ML SDK v2 command-job builders."""

from __future__ import annotations

import pytest

from revenue_prediction.config.models import AzureMLConfig
from revenue_prediction.integrations.azureml.jobs import build_command_job

pytestmark = pytest.mark.unit


def test_command_job_declares_model_output() -> None:
    pytest.importorskip("azure.ai.ml")

    job = build_command_job(
        AzureMLConfig(compute_cluster="cpu-cluster"),
        training_data_asset="azureml:revenue_snapshots:1",
        environment="azureml:revenue-prediction-env:1",
    )

    assert "model_dir" in job.outputs
    assert "${{outputs.model_dir}}" in job.command