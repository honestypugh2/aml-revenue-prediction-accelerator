"""Azure Machine Learning SDK v2 helpers (workspace client, jobs, registration).

Every function defers importing ``azure.ai.ml`` / ``azure.identity`` so the
package imports cleanly without the optional ``azure`` extra. Authentication
uses ``DefaultAzureCredential`` (managed identity, Azure CLI, environment, or
interactive) — no secrets are ever read from source.
"""

from __future__ import annotations

from .client import get_ml_client
from .jobs import build_command_job, register_model_from_run

__all__ = ["build_command_job", "get_ml_client", "register_model_from_run"]
