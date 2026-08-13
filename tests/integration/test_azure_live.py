"""Opt-in live integration tests for Azure ML and Fabric/OneLake.

These are skipped unless real credentials and configuration are supplied via
environment variables. They NEVER run in CI by default and never fabricate
cloud results. To run:

    RPA_RUN_LIVE=1 \
    RPA_AZURE_ML__SUBSCRIPTION_ID=... \
    RPA_AZURE_ML__RESOURCE_GROUP=... \
    RPA_AZURE_ML__WORKSPACE_NAME=... \
    uv run pytest -m live
"""

from __future__ import annotations

import os

import pytest

from revenue_prediction.config.loader import load_settings

pytestmark = pytest.mark.live

_RUN_LIVE = os.environ.get("RPA_RUN_LIVE") == "1"

skip_reason = "Set RPA_RUN_LIVE=1 and provide real workspace config to run live tests."


@pytest.mark.skipif(not _RUN_LIVE, reason=skip_reason)
def test_ml_client_connects() -> None:
    from revenue_prediction.integrations.azureml.client import get_ml_client

    settings = load_settings(os.environ.get("RPA_ENVIRONMENT", "dev"))
    if not settings.azure_ml.is_configured():
        pytest.skip("Azure ML workspace not configured via environment variables.")
    client = get_ml_client(settings.azure_ml)
    # A trivial read verifies auth + connectivity without mutating anything.
    ws = client.workspaces.get(settings.azure_ml.workspace_name)
    assert ws.name == settings.azure_ml.workspace_name


@pytest.mark.skipif(not _RUN_LIVE, reason=skip_reason)
def test_onelake_write_read_roundtrip() -> None:
    import pandas as pd

    from revenue_prediction.integrations.fabric.onelake import OneLakeClient

    settings = load_settings(os.environ.get("RPA_ENVIRONMENT", "dev"))
    if not settings.fabric.is_configured():
        pytest.skip("Fabric/OneLake not configured via environment variables.")
    client = OneLakeClient(settings.fabric)
    df = pd.DataFrame({"facility_id": ["FAC-001"], "predicted_month_end_net_revenue": [1.0]})
    path = "Files/revenue/predictions/_live_test.parquet"
    client.write_parquet(df, path)
    back = client.read_parquet(path)
    assert len(back) == 1
