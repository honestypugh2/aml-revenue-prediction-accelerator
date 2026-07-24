"""Canonical schema definitions for the facility-month-snapshot grain.

This module is the single source of truth for column names, groupings, and
expected dtypes. Feature engineering, contracts, training, and inference all
import from here to stay consistent.
"""

from __future__ import annotations

import pandera as pa
from pandera import Column, DataFrameSchema

# --- Grain / key columns ---------------------------------------------------
FACILITY_COL = "facility_id"
MONTH_COL = "accounting_month"
SNAPSHOT_DATE_COL = "snapshot_date"
SNAPSHOT_DAY_COL = "snapshot_day"

KEY_COLUMNS = [FACILITY_COL, MONTH_COL, SNAPSHOT_DATE_COL, SNAPSHOT_DAY_COL]

# --- Dimension columns -----------------------------------------------------
DIMENSION_COLUMNS = [
    "service_line_group",
    "generic_payer_group",
    "encounter_class_group",
]

# --- Partial-month operational features (known as-of snapshot) -------------
OPERATIONAL_FEATURES = [
    "month_to_date_encounters",
    "month_to_date_discharges",
    "month_to_date_case_mix_index",
    "month_to_date_gross_charges",
    "month_to_date_payments",
    "month_to_date_denials",
    "month_to_date_contractual_adjustments",
    "month_to_date_bad_debt",
    "month_to_date_charity_care",
    "month_to_date_length_of_stay",
    "month_to_date_inpatient_volume",
    "month_to_date_outpatient_volume",
    "days_elapsed",
    "business_days_elapsed",
    "remaining_days",
]

# --- Historical features (only from prior, closed months) ------------------
HISTORICAL_FEATURES = [
    "prior_month_net_revenue",
    "prior_year_same_month_net_revenue",
    "rolling_3_month_net_revenue",
    "rolling_6_month_net_revenue",
    "rolling_12_month_net_revenue",
    "historical_collection_rate",
    "historical_denial_rate",
    "historical_adjustment_rate",
    "historical_payer_mix",
    "month",
    "quarter",
    "month_sin",
    "month_cos",
]

# --- Target ----------------------------------------------------------------
TARGET = "actual_month_end_net_revenue"

# Full set of model-input feature columns (everything a model may consume).
FEATURE_COLUMNS = DIMENSION_COLUMNS + OPERATIONAL_FEATURES + HISTORICAL_FEATURES

# All non-target columns produced by the generator.
ALL_COLUMNS = KEY_COLUMNS + FEATURE_COLUMNS + [TARGET]

COLUMN_DTYPES: dict[str, str] = {
    FACILITY_COL: "object",
    MONTH_COL: "object",
    SNAPSHOT_DATE_COL: "object",
    SNAPSHOT_DAY_COL: "int64",
    **{c: "object" for c in DIMENSION_COLUMNS},
    **{c: "float64" for c in OPERATIONAL_FEATURES},
    **{c: "float64" for c in HISTORICAL_FEATURES},
    "month": "int64",
    "quarter": "int64",
    TARGET: "float64",
}


def raw_snapshot_schema(require_target: bool = True) -> DataFrameSchema:
    """Return a Pandera schema describing a valid raw snapshot dataframe.

    Parameters
    ----------
    require_target:
        When ``True`` the target column must be present and non-null (training
        data). When ``False`` the target may be absent (inference data).
    """
    columns: dict[str, Column] = {
        FACILITY_COL: Column(str, pa.Check.str_matches(r"^FAC-\d{3}$"), nullable=False),
        MONTH_COL: Column(str, pa.Check.str_matches(r"^\d{4}-\d{2}$"), nullable=False),
        SNAPSHOT_DATE_COL: Column(
            str, pa.Check.str_matches(r"^\d{4}-\d{2}-\d{2}$"), nullable=False
        ),
        SNAPSHOT_DAY_COL: Column(int, pa.Check.in_range(1, 31), nullable=False),
    }

    for col in DIMENSION_COLUMNS:
        columns[col] = Column(str, nullable=False)

    # Operational features must be non-negative (except remaining_days can be 0).
    for col in OPERATIONAL_FEATURES:
        columns[col] = Column(float, pa.Check.ge(0), nullable=True)

    columns["days_elapsed"] = Column(float, pa.Check.in_range(1, 31), nullable=False)
    columns["business_days_elapsed"] = Column(float, pa.Check.ge(0), nullable=False)
    columns["remaining_days"] = Column(float, pa.Check.ge(0), nullable=False)

    for col in HISTORICAL_FEATURES:
        if col in {"month", "quarter"}:
            continue
        columns[col] = Column(float, nullable=True)

    columns["month"] = Column(int, pa.Check.in_range(1, 12), nullable=False)
    columns["quarter"] = Column(int, pa.Check.in_range(1, 4), nullable=False)

    if require_target:
        columns[TARGET] = Column(float, pa.Check.gt(0), nullable=False)

    return DataFrameSchema(columns, strict=False, coerce=True)
