"""Measure model/evaluation metrics against use-case success metrics and KPIs.

The education layer (``revenue_prediction.education``) defines the *narrative*
success criteria and per-checkpoint accuracy targets. This module turns those
into a **measurable scorecard**: given computed metrics (overall and by snapshot
day), it reports whether each checkpoint WAPE target is met and whether the model
beats the manual-analyst baseline — the primary business KPI for the use case.

All thresholds are expressed as fractions (WAPE 0.04 == 4%). Targets mirror
``education.get_metric_targets`` but are structured for computation.
"""

from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

from revenue_prediction.core.data.schema import SNAPSHOT_DAY_COL


@dataclass(frozen=True)
class CheckpointTarget:
    """A structured, measurable WAPE target for one mid-month checkpoint."""

    label: str
    snapshot_day: int
    wape_max: float  # system-level WAPE ceiling (fraction)
    by_facility_wape_max: float | None = None  # per-facility ceiling (fraction)


# Structured mirror of education.get_metric_targets(); see docs/modeling/
# success-metrics-and-kpis.md. "Pre-close" maps to the last configured snapshot.
DEFAULT_CHECKPOINT_TARGETS: list[CheckpointTarget] = [
    CheckpointTarget("Day 10 (early read)", 10, 0.07),
    CheckpointTarget("Day 15 (primary)", 15, 0.04, by_facility_wape_max=0.05),
    CheckpointTarget("Day 21 (second)", 21, 0.04),
]


@dataclass(frozen=True)
class KpiResult:
    """One measured KPI line: value vs. target with a met/not-met verdict."""

    name: str
    metric: str
    value: float
    target: float
    met: bool
    margin: float  # target - value for "lower is better" (positive == headroom)


def evaluate_checkpoint_targets(
    by_snapshot_day: pd.DataFrame,
    targets: list[CheckpointTarget] | None = None,
) -> pd.DataFrame:
    """Score system-level WAPE at each checkpoint against its target.

    ``by_snapshot_day`` is the output of
    ``core.evaluation.metrics.metrics_by_snapshot_day`` (columns include
    ``snapshot_day`` and ``wape``). Returns a tidy scorecard DataFrame.
    """
    targets = targets or DEFAULT_CHECKPOINT_TARGETS
    indexed = by_snapshot_day.set_index(SNAPSHOT_DAY_COL)
    rows: list[dict[str, object]] = []
    for target in targets:
        if target.snapshot_day not in indexed.index:
            continue
        value = float(indexed.loc[target.snapshot_day, "wape"])
        rows.append(
            {
                "checkpoint": target.label,
                "snapshot_day": target.snapshot_day,
                "metric": "wape",
                "value": round(value, 4),
                "target": target.wape_max,
                "met": bool(value <= target.wape_max),
                "margin": round(target.wape_max - value, 4),
            }
        )
    return pd.DataFrame(rows)


def beats_baseline(champion_wape: float, baseline_wape: float) -> KpiResult:
    """Primary business KPI: does the model beat the manual-analyst baseline?"""
    met = champion_wape < baseline_wape
    return KpiResult(
        name="Beat manual analyst baseline",
        metric="wape",
        value=round(float(champion_wape), 4),
        target=round(float(baseline_wape), 4),
        met=met,
        margin=round(float(baseline_wape) - float(champion_wape), 4),
    )


def kpi_scorecard(
    overall: dict[str, float],
    by_snapshot_day: pd.DataFrame,
    baseline_wape: float | None = None,
    targets: list[CheckpointTarget] | None = None,
) -> pd.DataFrame:
    """Build a single scorecard of checkpoint targets and business KPIs.

    Combines per-checkpoint WAPE verdicts with the "beat baseline" KPI (when a
    baseline is supplied). Returns a tidy DataFrame suitable for CSV/logging.
    """
    scorecard = evaluate_checkpoint_targets(by_snapshot_day, targets)
    if baseline_wape is not None and "wape" in overall:
        kpi = beats_baseline(overall["wape"], baseline_wape)
        scorecard = pd.concat(
            [
                scorecard,
                pd.DataFrame(
                    [
                        {
                            "checkpoint": kpi.name,
                            "snapshot_day": pd.NA,
                            "metric": kpi.metric,
                            "value": kpi.value,
                            "target": kpi.target,
                            "met": kpi.met,
                            "margin": kpi.margin,
                        }
                    ]
                ),
            ],
            ignore_index=True,
        )
    return scorecard
