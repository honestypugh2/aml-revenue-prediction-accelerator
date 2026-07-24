"""Azure ML workspace client factory."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from ..config.models import AzureMLConfig

if TYPE_CHECKING:  # pragma: no cover
    from azure.ai.ml import MLClient


def get_ml_client(config: AzureMLConfig) -> MLClient:  # pragma: no cover - needs azure
    """Create an authenticated :class:`MLClient` from configuration.

    Uses ``DefaultAzureCredential`` which supports managed identity (jumpbox),
    Azure CLI, environment credentials, and interactive fallback. Raises a clear
    error if the workspace is not configured (placeholders still present).
    """
    if not config.is_configured():
        raise ValueError(
            "Azure ML workspace is not configured. Set RPA_AZURE_ML__SUBSCRIPTION_ID, "
            "RPA_AZURE_ML__RESOURCE_GROUP, and RPA_AZURE_ML__WORKSPACE_NAME "
            "(never commit these values)."
        )
    try:
        from azure.ai.ml import MLClient
        from azure.identity import DefaultAzureCredential
    except ImportError as exc:
        raise ImportError(
            "Azure ML SDK v2 not installed. Install the 'azure' extra: " "`uv sync --extra azure`."
        ) from exc

    credential: Any = DefaultAzureCredential(exclude_interactive_browser_credential=False)
    return MLClient(
        credential=credential,
        subscription_id=config.subscription_id,
        resource_group_name=config.resource_group,
        workspace_name=config.workspace_name,
    )
