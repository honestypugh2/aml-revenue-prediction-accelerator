"""Data layer: synthetic generation, schema, and contracts.

All default data produced here is fully synthetic and contains no customer,
patient, or organization-specific information.
"""

from __future__ import annotations

from .contracts import (
    ContractViolation,
    validate_leakage_rules,
    validate_raw_snapshots,
)
from .schema import (
    COLUMN_DTYPES,
    FEATURE_COLUMNS,
    HISTORICAL_FEATURES,
    KEY_COLUMNS,
    OPERATIONAL_FEATURES,
    TARGET,
    raw_snapshot_schema,
)
from .synthetic import SyntheticDataGenerator, generate_synthetic_dataset

__all__ = [
    "COLUMN_DTYPES",
    "FEATURE_COLUMNS",
    "HISTORICAL_FEATURES",
    "KEY_COLUMNS",
    "OPERATIONAL_FEATURES",
    "TARGET",
    "ContractViolation",
    "SyntheticDataGenerator",
    "generate_synthetic_dataset",
    "raw_snapshot_schema",
    "validate_leakage_rules",
    "validate_raw_snapshots",
]
