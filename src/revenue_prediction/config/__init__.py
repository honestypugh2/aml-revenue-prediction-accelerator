"""Configuration models and loading for the revenue prediction accelerator.

Configuration is layered:

1. YAML files under ``configs/base`` provide defaults.
2. Environment-specific YAML (``configs/dev``, ``configs/test``, ``configs/prod``)
   overrides the base.
3. Environment variables (prefixed ``RPA_``) and a local ``.env`` file override
   file values, and are the only place secrets or cloud identifiers should live.

No secrets, subscription IDs, tenant IDs, or resource identifiers are stored in
source control. Placeholder values are used everywhere by default.
"""

from __future__ import annotations

from .loader import load_settings
from .models import (
    AutoMLConfig,
    AzureMLConfig,
    DataConfig,
    EvaluationConfig,
    FabricConfig,
    FeatureConfig,
    ModelConfig,
    Settings,
    SplitConfig,
)

__all__ = [
    "AutoMLConfig",
    "AzureMLConfig",
    "DataConfig",
    "EvaluationConfig",
    "FabricConfig",
    "FeatureConfig",
    "ModelConfig",
    "Settings",
    "SplitConfig",
    "load_settings",
]
