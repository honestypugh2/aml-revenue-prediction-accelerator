"""Data contracts: schema validation and leakage-rule enforcement."""

from __future__ import annotations

import pandas as pd

from .schema import (
    FACILITY_COL,
    MONTH_COL,
    SNAPSHOT_DATE_COL,
    SNAPSHOT_DAY_COL,
    TARGET,
    raw_snapshot_schema,
)


class ContractViolation(ValueError):
    """Raised when a dataframe violates the data contract."""


def validate_raw_snapshots(frame: pd.DataFrame, require_target: bool = True) -> pd.DataFrame:
    """Validate ``frame`` against the raw snapshot schema.

    Returns the (coerced) dataframe on success, raises
    :class:`ContractViolation` on failure.
    """
    from pandera import errors as pa_errors

    schema = raw_snapshot_schema(require_target=require_target)
    try:
        return schema.validate(frame, lazy=True)
    except pa_errors.SchemaErrors as exc:  # pragma: no cover - message formatting
        raise ContractViolation(f"Raw snapshot contract failed:\n{exc.failure_cases}") from exc


def validate_leakage_rules(frame: pd.DataFrame) -> pd.DataFrame:
    """Enforce temporal leakage rules on a snapshot dataframe.

    Rules
    -----
    1. ``snapshot_day`` must equal the day component of ``snapshot_date``.
    2. ``snapshot_date`` must fall within its ``accounting_month``.
    3. ``days_elapsed`` must equal ``snapshot_day`` (no future information).
    4. The target must be constant within a facility-month (it is only known
       after close and cannot vary by snapshot).
    """
    errors: list[str] = []

    snap_dt = pd.to_datetime(frame[SNAPSHOT_DATE_COL], errors="coerce")
    if snap_dt.isna().any():
        errors.append("snapshot_date contains unparseable dates")
    else:
        if not (snap_dt.dt.day == frame[SNAPSHOT_DAY_COL]).all():
            errors.append("snapshot_day does not match the day component of snapshot_date")
        month_str = snap_dt.dt.strftime("%Y-%m")
        if not (month_str == frame[MONTH_COL]).all():
            errors.append("snapshot_date falls outside its accounting_month")

    if (
        "days_elapsed" in frame.columns
        and not (frame["days_elapsed"].astype(float) == frame[SNAPSHOT_DAY_COL].astype(float)).all()
    ):
        errors.append("days_elapsed disagrees with snapshot_day (potential future leakage)")

    if TARGET in frame.columns:
        variability = frame.groupby([FACILITY_COL, MONTH_COL])[TARGET].nunique()
        if (variability > 1).any():
            offenders = variability[variability > 1].index.tolist()
            errors.append(
                f"target varies within facility-month(s) {offenders[:3]} (leakage / inconsistency)"
            )

    if errors:
        raise ContractViolation("; ".join(errors))
    return frame
