"""Pure, testable logic backing the Streamlit UI (no streamlit import)."""

from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

from ..config.loader import load_settings
from ..config.models import Settings
from ..data.schema import FACILITY_COL, MONTH_COL, TARGET
from ..data.synthetic import generate_synthetic_dataset
from ..pipelines.local_pipeline import LocalPipelineOutput, run_local_pipeline


@dataclass
class ExperienceState:
    """State shared across UI panels."""

    settings: Settings
    data: pd.DataFrame


def load_experience(environment: str = "dev") -> ExperienceState:
    """Load settings and generate the synthetic dataset for the UI."""
    settings = load_settings(environment)
    data = generate_synthetic_dataset(settings.data)
    return ExperienceState(settings=settings, data=data)


def build_dataset_overview(state: ExperienceState) -> dict[str, object]:
    """Summarize the dataset for the overview panel."""
    df = state.data
    return {
        "rows": int(len(df)),
        "facilities": sorted(df[FACILITY_COL].unique().tolist()),
        "months": sorted(df[MONTH_COL].unique().tolist()),
        "snapshot_days": sorted(df["snapshot_day"].unique().tolist()),
        "target_mean": float(df[TARGET].mean()),
        "target_min": float(df[TARGET].min()),
        "target_max": float(df[TARGET].max()),
    }


def facility_month_series(state: ExperienceState, facility_id: str) -> pd.DataFrame:
    """Return one row per accounting month (actual target) for a facility."""
    df = state.data
    subset = df[df[FACILITY_COL] == facility_id]
    series = (
        subset.groupby(MONTH_COL)[TARGET]
        .first()
        .reset_index()
        .sort_values(MONTH_COL)
        .reset_index(drop=True)
    )
    return series


def run_training_experience(state: ExperienceState) -> LocalPipelineOutput:
    """Run the full offline pipeline for the training panel."""
    return run_local_pipeline(state.settings, frame=state.data)


def build_comparison_view(output: LocalPipelineOutput) -> pd.DataFrame:
    """Return the model comparison table with the champion flagged."""
    table = output.comparison.copy()
    table["is_champion"] = table["model"] == output.selection.champion
    return table
