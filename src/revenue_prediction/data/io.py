"""Dataset persistence helpers (Parquet + CSV) and sample-data authoring."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from ..config.models import DataConfig
from .synthetic import generate_synthetic_dataset


def write_dataset(frame: pd.DataFrame, path: str | Path) -> Path:
    """Write a dataframe to Parquet (preferred) or CSV based on suffix."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.suffix in {".parquet", ".pq"}:
        frame.to_parquet(path, index=False)
    elif path.suffix == ".csv":
        frame.to_csv(path, index=False)
    else:
        raise ValueError(f"Unsupported dataset suffix: {path.suffix}")
    return path


def read_dataset(path: str | Path) -> pd.DataFrame:
    """Read a Parquet or CSV dataset."""
    path = Path(path)
    if path.suffix in {".parquet", ".pq"}:
        return pd.read_parquet(path)
    if path.suffix == ".csv":
        return pd.read_csv(path)
    raise ValueError(f"Unsupported dataset suffix: {path.suffix}")


def build_invalid_sample(valid: pd.DataFrame) -> pd.DataFrame:
    """Return a deliberately-invalid copy used for contract tests.

    Introduces schema and leakage violations: a bad facility id, a negative
    target, and a snapshot_day inconsistent with snapshot_date.
    """
    invalid = valid.head(20).copy()
    invalid.loc[invalid.index[0], "facility_id"] = "FACILITY_1"  # bad pattern
    if "actual_month_end_net_revenue" in invalid.columns:
        invalid.loc[invalid.index[1], "actual_month_end_net_revenue"] = -1000.0
    invalid.loc[invalid.index[2], "snapshot_day"] = 99  # out of range + mismatched
    return invalid


def materialise_default_datasets(config: DataConfig | None = None) -> dict[str, Path]:
    """Generate and persist the default synthetic, sample, and invalid datasets."""
    config = config or DataConfig()
    frame = generate_synthetic_dataset(config)

    outputs: dict[str, Path] = {}
    outputs["synthetic"] = write_dataset(frame, config.raw_dir / "revenue_snapshots.parquet")

    sample = frame.head(200).copy()
    outputs["sample"] = write_dataset(sample, config.sample_dir / "revenue_snapshots_sample.csv")

    invalid = build_invalid_sample(sample)
    outputs["invalid"] = write_dataset(invalid, config.sample_dir / "revenue_snapshots_invalid.csv")
    return outputs
