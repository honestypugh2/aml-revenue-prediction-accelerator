"""OneLake client with a local filesystem fallback for offline use."""

from __future__ import annotations

import io
from pathlib import Path
from typing import Any

import pandas as pd

from ..config.models import FabricConfig


class OneLakeClient:
    """Read/write Parquet data to a Fabric Lakehouse via OneLake.

    When ``local_root`` is provided (or the ``fabric`` extra / credentials are
    unavailable), the client transparently uses the local filesystem so demos,
    workshops, and tests run without any cloud dependency.
    """

    def __init__(self, config: FabricConfig, local_root: str | Path | None = None) -> None:
        self.config = config
        self.local_root = Path(local_root) if local_root is not None else None
        self._service: Any | None = None

    # -- connection ---------------------------------------------------------
    @property
    def uses_local(self) -> bool:
        return self.local_root is not None or not self.config.is_configured()

    def _lakehouse_uri(self, path: str) -> str:
        # OneLake path convention:
        # https://onelake.dfs.fabric.microsoft.com/<workspace>/<lakehouse>.Lakehouse/<path>
        return (
            f"{self.config.onelake_account_url}/{self.config.workspace_name}/"
            f"{self.config.lakehouse_name}.Lakehouse/{path}"
        )

    def _get_service_client(self) -> Any:  # pragma: no cover - needs fabric extra
        if self._service is not None:
            return self._service
        try:
            from azure.identity import DefaultAzureCredential
            from azure.storage.filedatalake import DataLakeServiceClient
        except ImportError as exc:
            raise ImportError("Install the 'fabric' extra: `uv sync --extra fabric`.") from exc

        self._service = DataLakeServiceClient(
            account_url=self.config.onelake_account_url,
            credential=DefaultAzureCredential(),
        )
        return self._service

    # -- IO -----------------------------------------------------------------
    def write_parquet(self, frame: pd.DataFrame, path: str) -> str:
        """Write ``frame`` as Parquet to ``path`` (relative to the Lakehouse)."""
        if self.uses_local:
            root = self.local_root or Path("outputs/onelake")
            target = root / path
            target.parent.mkdir(parents=True, exist_ok=True)
            frame.to_parquet(target, index=False)
            return str(target)

        return self._write_parquet_remote(frame, path)  # pragma: no cover

    def read_parquet(self, path: str) -> pd.DataFrame:
        """Read a Parquet dataset from ``path`` (relative to the Lakehouse)."""
        if self.uses_local:
            root = self.local_root or Path("outputs/onelake")
            return pd.read_parquet(root / path)
        return self._read_parquet_remote(path)  # pragma: no cover

    def _write_parquet_remote(self, frame: pd.DataFrame, path: str) -> str:  # pragma: no cover
        service = self._get_service_client()
        fs = service.get_file_system_client(self.config.workspace_name)
        file_path = f"{self.config.lakehouse_name}.Lakehouse/{path}"
        buffer = io.BytesIO()
        frame.to_parquet(buffer, index=False)
        buffer.seek(0)
        file_client = fs.get_file_client(file_path)
        file_client.upload_data(buffer.getvalue(), overwrite=True)
        return self._lakehouse_uri(path)

    def _read_parquet_remote(self, path: str) -> pd.DataFrame:  # pragma: no cover
        service = self._get_service_client()
        fs = service.get_file_system_client(self.config.workspace_name)
        file_path = f"{self.config.lakehouse_name}.Lakehouse/{path}"
        downloaded = fs.get_file_client(file_path).download_file().readall()
        return pd.read_parquet(io.BytesIO(downloaded))


def write_predictions_to_onelake(
    predictions: pd.DataFrame,
    config: FabricConfig,
    local_root: str | Path | None = None,
    filename: str = "predictions.parquet",
) -> str:
    """Write a predictions dataframe to the configured OneLake predictions path.

    The output is Power BI-ready: a flat, typed table that a Fabric/Power BI
    semantic model can consume directly via DirectLake.
    """
    client = OneLakeClient(config, local_root=local_root)
    target = f"{config.predictions_path}/{filename}"
    return client.write_parquet(predictions, target)
