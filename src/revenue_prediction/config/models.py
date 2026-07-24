"""Pydantic v2 configuration models.

These models describe the full configuration surface of the accelerator. They
are deliberately conservative: every field has a safe, synthetic-friendly
default so the accelerator runs end-to-end offline with zero setup.
"""

from __future__ import annotations

from pathlib import Path

from pydantic import BaseModel, Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

# Canonical grain / key columns used throughout the accelerator.
FACILITY_COL = "facility_id"
MONTH_COL = "accounting_month"
SNAPSHOT_DATE_COL = "snapshot_date"
SNAPSHOT_DAY_COL = "snapshot_day"
TARGET_COL = "actual_month_end_net_revenue"


class DataConfig(BaseModel):
    """Synthetic data generation and dataset layout configuration."""

    seed: int = 42
    n_facilities: int = 6
    n_months: int = 30
    start_year: int = 2023
    start_month: int = 1
    snapshot_days: list[int] = Field(default_factory=lambda: [7, 10, 12, 15, 18, 21, 24, 27])
    demo_cutoff_day: int = 15
    missing_rate: float = Field(default=0.03, ge=0.0, le=0.5)
    outlier_rate: float = Field(default=0.01, ge=0.0, le=0.5)
    noise_scale: float = Field(default=0.04, ge=0.0)
    raw_dir: Path = Path("data/synthetic")
    sample_dir: Path = Path("data/sample")

    @field_validator("snapshot_days")
    @classmethod
    def _sorted_unique_days(cls, value: list[int]) -> list[int]:
        if not value:
            raise ValueError("snapshot_days must not be empty")
        if any(d < 1 or d > 28 for d in value):
            raise ValueError("snapshot_days must be between 1 and 28")
        return sorted(set(value))


class FeatureConfig(BaseModel):
    """Leakage-safe feature engineering configuration."""

    # Columns that are only known AFTER accounting close and therefore must
    # never be used as model inputs (they would leak the target).
    forbidden_future_columns: list[str] = Field(
        default_factory=lambda: [
            TARGET_COL,
            "final_contractual_adjustments",
            "final_denials",
            "month_end_close_flag",
        ]
    )
    rolling_windows: list[int] = Field(default_factory=lambda: [3, 6, 12])
    include_calendar_features: bool = True
    categorical_columns: list[str] = Field(
        default_factory=lambda: [
            "service_line_group",
            "generic_payer_group",
            "encounter_class_group",
        ]
    )


class SplitConfig(BaseModel):
    """Temporal (time-aware) splitting configuration.

    Random row splitting is intentionally NOT supported as a primary strategy.
    All rows belonging to a single facility-month stay in the same split.
    """

    strategy: str = Field(
        default="blocked_temporal", pattern="^(blocked_temporal|rolling_origin|expanding_window)$"
    )
    n_test_months: int = 4
    n_val_months: int = 4
    n_backtest_folds: int = 3

    @field_validator("n_test_months", "n_val_months", "n_backtest_folds")
    @classmethod
    def _positive(cls, value: int) -> int:
        if value < 1:
            raise ValueError("split month/fold counts must be >= 1")
        return value


class ModelConfig(BaseModel):
    """Code-first model configuration."""

    candidates: list[str] = Field(
        default_factory=lambda: [
            "naive_prior",
            "seasonal_naive",
            "elastic_net",
            "hist_gradient_boosting",
            "xgboost",
        ]
    )
    primary_metric: str = Field(default="mae", pattern="^(mae|rmse|mape|smape|r2)$")
    random_state: int = 42
    xgboost_params: dict[str, float | int | str] = Field(
        default_factory=lambda: {
            "n_estimators": 300,
            "max_depth": 5,
            "learning_rate": 0.05,
            "subsample": 0.9,
            "colsample_bytree": 0.9,
            "reg_lambda": 1.0,
        }
    )
    hgb_params: dict[str, float | int | str] = Field(
        default_factory=lambda: {
            "max_iter": 300,
            "learning_rate": 0.05,
            "max_depth": 6,
        }
    )


class EvaluationConfig(BaseModel):
    """Model evaluation configuration."""

    metrics: list[str] = Field(default_factory=lambda: ["mae", "rmse", "mape", "smape", "r2"])
    by_snapshot_day: bool = True
    by_facility: bool = True
    challenger_improvement_threshold: float = Field(default=0.02, ge=0.0)


class AutoMLConfig(BaseModel):
    """Azure Machine Learning Automated ML configuration."""

    task: str = "regression"
    primary_metric: str = "normalized_root_mean_squared_error"
    experiment_name: str = "revenue-automl"
    timeout_minutes: int = 30
    trial_timeout_minutes: int = 5
    max_trials: int = 20
    max_concurrent_trials: int = 4
    enable_early_termination: bool = True
    n_cross_validations: int = 5


class AzureMLConfig(BaseModel):
    """Azure Machine Learning workspace connection settings.

    All values default to safe placeholders. Real values must be provided via
    environment variables (never committed).
    """

    subscription_id: str = "SUBSCRIPTION_ID_PLACEHOLDER"
    resource_group: str = "RESOURCE_GROUP_PLACEHOLDER"
    workspace_name: str = "WORKSPACE_PLACEHOLDER"
    location: str = "eastus2"
    compute_cluster: str = "cpu-cluster"
    environment_name: str = "revenue-prediction-env"
    registered_model_name: str = "revenue-net-revenue-model"
    online_endpoint_name: str = "revenue-online-endpoint"

    def is_configured(self) -> bool:
        """Return True only when real (non-placeholder) values are present."""
        return "PLACEHOLDER" not in (
            self.subscription_id + self.resource_group + self.workspace_name
        )


class FabricConfig(BaseModel):
    """Microsoft Fabric / OneLake settings.

    OneLake is accessed via the ADLS Gen2 endpoint
    ``https://onelake.dfs.fabric.microsoft.com``. All identifiers default to
    placeholders.
    """

    onelake_account_url: str = "https://onelake.dfs.fabric.microsoft.com"
    workspace_name: str = "WORKSPACE_PLACEHOLDER"
    lakehouse_name: str = "LAKEHOUSE_PLACEHOLDER"
    input_path: str = "Files/revenue/input"
    predictions_path: str = "Files/revenue/predictions"

    def is_configured(self) -> bool:
        return "PLACEHOLDER" not in (self.workspace_name + self.lakehouse_name)


class Settings(BaseSettings):
    """Root settings object.

    Environment variables are read with the ``RPA_`` prefix and nested keys use
    ``__`` (e.g. ``RPA_AZURE_ML__WORKSPACE_NAME``).
    """

    model_config = SettingsConfigDict(
        env_prefix="RPA_",
        env_nested_delimiter="__",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    environment: str = Field(default="dev", pattern="^(dev|test|prod)$")
    data: DataConfig = Field(default_factory=DataConfig)
    features: FeatureConfig = Field(default_factory=FeatureConfig)
    split: SplitConfig = Field(default_factory=SplitConfig)
    model: ModelConfig = Field(default_factory=ModelConfig)
    evaluation: EvaluationConfig = Field(default_factory=EvaluationConfig)
    automl: AutoMLConfig = Field(default_factory=AutoMLConfig)
    azure_ml: AzureMLConfig = Field(default_factory=AzureMLConfig)
    fabric: FabricConfig = Field(default_factory=FabricConfig)
