"""Microsoft Fabric / OneLake integration.

OneLake exposes an ADLS Gen2-compatible endpoint
(``https://onelake.dfs.fabric.microsoft.com``). This module reads inputs and
writes predictions to a Lakehouse using ``azure-storage-file-datalake`` with
``DefaultAzureCredential``. It is import-safe without the ``fabric`` extra and
supports a local filesystem fallback for offline demos and tests.
"""

from __future__ import annotations

from .onelake import OneLakeClient, write_predictions_to_onelake

__all__ = ["OneLakeClient", "write_predictions_to_onelake"]
