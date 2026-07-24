"""Deterministic synthetic data generator for facility-month-snapshot data.

The generator produces a fully synthetic dataset that mimics the *shape* of
healthcare revenue-cycle data without using any real, identifiable, or
customer-specific information. It is seeded for reproducibility.

Design goals
------------
* Realistic-looking seasonality, facility effects, service-line and payer-mix
  effects, payment lag, denial and adjustment patterns.
* Multiple intra-month snapshots per facility-month.
* Historical features derived ONLY from prior, closed months (leakage-safe).
* Partial-month operational features that reflect only information available
  as-of the snapshot day.
* Controlled missingness, outliers, and noise.

The "actual" month-end net revenue (the target) is identical across all
snapshots for a given facility-month, reflecting the fact that it is only known
after accounting close.
"""

from __future__ import annotations

import calendar
from dataclasses import dataclass

import numpy as np
import pandas as pd

from ..config.models import DataConfig
from .schema import ALL_COLUMNS

_SERVICE_LINES = ["acute_inpatient", "ambulatory_surgery", "emergency", "outpatient_clinic"]
_PAYER_GROUPS = ["commercial", "managed_government", "government", "self_pay"]
_ENCOUNTER_CLASSES = ["inpatient", "outpatient", "emergency", "observation"]


def _business_days_elapsed(year: int, month: int, day: int) -> int:
    """Count Monday-Friday days from the 1st through ``day`` inclusive."""
    start = np.datetime64(f"{year:04d}-{month:02d}-01")
    end = np.datetime64(f"{year:04d}-{month:02d}-{day:02d}") + np.timedelta64(1, "D")
    return int(np.busday_count(start, end))


@dataclass
class _FacilityProfile:
    facility_id: str
    base_monthly_revenue: float
    trend_per_month: float
    seasonal_amplitude: float
    collection_rate: float
    denial_rate: float
    adjustment_rate: float
    payer_mix: float
    service_line: str
    payer_group: str
    encounter_class: str
    inpatient_share: float
    case_mix_index: float


class SyntheticDataGenerator:
    """Generate a synthetic facility-month-snapshot dataset."""

    def __init__(self, config: DataConfig | None = None) -> None:
        self.config = config or DataConfig()
        self._rng = np.random.default_rng(self.config.seed)

    # -- public API ---------------------------------------------------------
    def generate(self) -> pd.DataFrame:
        """Return the full synthetic snapshot dataframe."""
        facilities = self._build_facility_profiles()
        months = self._build_month_index()

        # Step 1: compute the ground-truth month-end net revenue per
        # facility-month (independent of snapshots).
        actuals = self._compute_monthly_actuals(facilities, months)

        # Step 2: expand each facility-month into intra-month snapshots.
        rows: list[dict[str, object]] = []
        for profile in facilities:
            series = actuals[profile.facility_id]
            for m_idx, (year, month) in enumerate(months):
                rows.extend(self._build_snapshots(profile, year, month, m_idx, series))

        frame = pd.DataFrame(rows)
        frame = self._inject_missing_and_outliers(frame)
        # Enforce deterministic column ordering.
        frame = frame[[c for c in ALL_COLUMNS if c in frame.columns]]
        return frame.reset_index(drop=True)

    # -- internal helpers ---------------------------------------------------
    def _build_facility_profiles(self) -> list[_FacilityProfile]:
        profiles: list[_FacilityProfile] = []
        for i in range(self.config.n_facilities):
            fac_id = f"FAC-{i + 1:03d}"
            base = float(self._rng.uniform(1.2e6, 6.5e6))
            profiles.append(
                _FacilityProfile(
                    facility_id=fac_id,
                    base_monthly_revenue=base,
                    trend_per_month=float(self._rng.uniform(-0.004, 0.010)) * base,
                    seasonal_amplitude=float(self._rng.uniform(0.04, 0.12)),
                    collection_rate=float(self._rng.uniform(0.30, 0.52)),
                    denial_rate=float(self._rng.uniform(0.04, 0.12)),
                    adjustment_rate=float(self._rng.uniform(0.35, 0.55)),
                    payer_mix=float(self._rng.uniform(0.35, 0.70)),
                    service_line=_SERVICE_LINES[i % len(_SERVICE_LINES)],
                    payer_group=_PAYER_GROUPS[i % len(_PAYER_GROUPS)],
                    encounter_class=_ENCOUNTER_CLASSES[i % len(_ENCOUNTER_CLASSES)],
                    inpatient_share=float(self._rng.uniform(0.25, 0.65)),
                    case_mix_index=float(self._rng.uniform(1.1, 1.9)),
                )
            )
        return profiles

    def _build_month_index(self) -> list[tuple[int, int]]:
        months: list[tuple[int, int]] = []
        year = self.config.start_year
        month = self.config.start_month
        for _ in range(self.config.n_months):
            months.append((year, month))
            month += 1
            if month > 12:
                month = 1
                year += 1
        return months

    def _compute_monthly_actuals(
        self, facilities: list[_FacilityProfile], months: list[tuple[int, int]]
    ) -> dict[str, np.ndarray]:
        actuals: dict[str, np.ndarray] = {}
        for profile in facilities:
            values = np.zeros(len(months), dtype=float)
            for idx, (_year, month) in enumerate(months):
                seasonal = 1.0 + profile.seasonal_amplitude * np.sin(2 * np.pi * (month - 1) / 12.0)
                trend = profile.trend_per_month * idx
                noise = self._rng.normal(1.0, self.config.noise_scale)
                values[idx] = max(
                    5.0e4,
                    (profile.base_monthly_revenue + trend) * seasonal * noise,
                )
            actuals[profile.facility_id] = values
        return actuals

    def _build_snapshots(
        self,
        profile: _FacilityProfile,
        year: int,
        month: int,
        m_idx: int,
        series: np.ndarray,
    ) -> list[dict[str, object]]:
        days_in_month = calendar.monthrange(year, month)[1]
        actual = float(series[m_idx])

        # Historical features derived only from strictly prior months.
        history = series[:m_idx]
        prior_month = float(history[-1]) if m_idx >= 1 else float("nan")
        prior_year = float(series[m_idx - 12]) if m_idx >= 12 else float("nan")
        roll3 = float(np.mean(history[-3:])) if m_idx >= 1 else float("nan")
        roll6 = float(np.mean(history[-6:])) if m_idx >= 1 else float("nan")
        roll12 = float(np.mean(history[-12:])) if m_idx >= 1 else float("nan")

        quarter = (month - 1) // 3 + 1
        month_sin = float(np.sin(2 * np.pi * (month - 1) / 12.0))
        month_cos = float(np.cos(2 * np.pi * (month - 1) / 12.0))

        snapshots: list[dict[str, object]] = []
        for day in self.config.snapshot_days:
            if day > days_in_month:
                continue
            frac = day / days_in_month
            bdays = _business_days_elapsed(year, month, day)

            # Gross charges accrue slightly faster than linear early in month.
            gross_frac = min(1.0, frac**0.92)
            gross_charges = actual / profile.collection_rate * gross_frac
            # Payments lag charges (payment lag effect).
            payment_frac = max(0.0, frac - 0.18) ** 1.05
            payments = actual * min(1.0, payment_frac) * self._rng.normal(1.0, 0.03)
            denials = gross_charges * profile.denial_rate * self._rng.normal(1.0, 0.05)
            adjustments = gross_charges * profile.adjustment_rate * self._rng.normal(1.0, 0.04)
            bad_debt = gross_charges * 0.02 * self._rng.normal(1.0, 0.1)
            charity = gross_charges * 0.015 * self._rng.normal(1.0, 0.1)

            encounters = profile.base_monthly_revenue / 4200.0 * gross_frac
            discharges = encounters * profile.inpatient_share * 0.35
            inpatient_vol = encounters * profile.inpatient_share
            outpatient_vol = encounters * (1.0 - profile.inpatient_share)
            los = self._rng.normal(4.2, 0.4) * profile.case_mix_index

            snapshots.append(
                {
                    "facility_id": profile.facility_id,
                    "accounting_month": f"{year:04d}-{month:02d}",
                    "snapshot_date": f"{year:04d}-{month:02d}-{day:02d}",
                    "snapshot_day": int(day),
                    "service_line_group": profile.service_line,
                    "generic_payer_group": profile.payer_group,
                    "encounter_class_group": profile.encounter_class,
                    "month_to_date_encounters": round(encounters, 2),
                    "month_to_date_discharges": round(discharges, 2),
                    "month_to_date_case_mix_index": round(profile.case_mix_index, 4),
                    "month_to_date_gross_charges": round(gross_charges, 2),
                    "month_to_date_payments": round(max(0.0, payments), 2),
                    "month_to_date_denials": round(max(0.0, denials), 2),
                    "month_to_date_contractual_adjustments": round(max(0.0, adjustments), 2),
                    "month_to_date_bad_debt": round(max(0.0, bad_debt), 2),
                    "month_to_date_charity_care": round(max(0.0, charity), 2),
                    "month_to_date_length_of_stay": round(max(0.0, los), 3),
                    "month_to_date_inpatient_volume": round(inpatient_vol, 2),
                    "month_to_date_outpatient_volume": round(outpatient_vol, 2),
                    "days_elapsed": float(day),
                    "business_days_elapsed": float(bdays),
                    "remaining_days": float(days_in_month - day),
                    "prior_month_net_revenue": prior_month,
                    "prior_year_same_month_net_revenue": prior_year,
                    "rolling_3_month_net_revenue": roll3,
                    "rolling_6_month_net_revenue": roll6,
                    "rolling_12_month_net_revenue": roll12,
                    "historical_collection_rate": round(profile.collection_rate, 4),
                    "historical_denial_rate": round(profile.denial_rate, 4),
                    "historical_adjustment_rate": round(profile.adjustment_rate, 4),
                    "historical_payer_mix": round(profile.payer_mix, 4),
                    "month": int(month),
                    "quarter": int(quarter),
                    "month_sin": round(month_sin, 6),
                    "month_cos": round(month_cos, 6),
                    "actual_month_end_net_revenue": round(actual, 2),
                }
            )
        return snapshots

    def _inject_missing_and_outliers(self, frame: pd.DataFrame) -> pd.DataFrame:
        frame = frame.copy()
        maskable = [
            "month_to_date_denials",
            "month_to_date_contractual_adjustments",
            "month_to_date_bad_debt",
            "month_to_date_charity_care",
            "month_to_date_case_mix_index",
        ]
        if self.config.missing_rate > 0:
            for col in maskable:
                mask = self._rng.random(len(frame)) < self.config.missing_rate
                frame.loc[mask, col] = np.nan

        if self.config.outlier_rate > 0:
            outlier_mask = self._rng.random(len(frame)) < self.config.outlier_rate
            multipliers = self._rng.uniform(2.5, 4.0, size=int(outlier_mask.sum()))
            frame.loc[outlier_mask, "month_to_date_gross_charges"] *= multipliers
        return frame


def generate_synthetic_dataset(config: DataConfig | None = None) -> pd.DataFrame:
    """Convenience wrapper returning a synthetic dataframe."""
    return SyntheticDataGenerator(config).generate()
