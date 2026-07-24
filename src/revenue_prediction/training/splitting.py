"""Time-aware splitting utilities.

Random row splitting is intentionally avoided. Every function here splits by
*accounting month* so that all snapshots of a facility-month remain together,
and no future month ever informs the training of a past month.
"""

from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

from ..config.models import SplitConfig
from ..data.schema import MONTH_COL


@dataclass
class TemporalSplit:
    """A single train/validation/test split defined by month boundaries."""

    train: pd.DataFrame
    validation: pd.DataFrame
    test: pd.DataFrame
    train_months: list[str]
    validation_months: list[str]
    test_months: list[str]


def _ordered_months(frame: pd.DataFrame) -> list[str]:
    return sorted(frame[MONTH_COL].astype(str).unique().tolist())


def blocked_temporal_split(frame: pd.DataFrame, config: SplitConfig | None = None) -> TemporalSplit:
    """Split into contiguous train / validation / test blocks by month.

    The most recent ``n_test_months`` months form the test set, the block
    immediately preceding forms validation, and everything earlier is training.
    """
    config = config or SplitConfig()
    months = _ordered_months(frame)
    n_test = config.n_test_months
    n_val = config.n_val_months
    if len(months) <= n_test + n_val:
        raise ValueError(
            f"Not enough months ({len(months)}) for {n_val} validation + {n_test} test months"
        )

    test_months = months[-n_test:]
    val_months = months[-(n_test + n_val) : -n_test]
    train_months = months[: -(n_test + n_val)]

    return TemporalSplit(
        train=frame[frame[MONTH_COL].isin(train_months)].copy(),
        validation=frame[frame[MONTH_COL].isin(val_months)].copy(),
        test=frame[frame[MONTH_COL].isin(test_months)].copy(),
        train_months=train_months,
        validation_months=val_months,
        test_months=test_months,
    )


def rolling_origin_folds(
    frame: pd.DataFrame, config: SplitConfig | None = None
) -> list[tuple[pd.DataFrame, pd.DataFrame]]:
    """Rolling-origin (sliding window) backtest folds.

    Each fold trains on a fixed-length window and validates on the next
    ``horizon`` months, then the window slides forward.
    """
    config = config or SplitConfig()
    months = _ordered_months(frame)
    horizon = config.n_val_months
    n_folds = config.n_backtest_folds
    folds: list[tuple[pd.DataFrame, pd.DataFrame]] = []

    min_train = max(horizon, len(months) - n_folds * horizon)
    for fold in range(n_folds):
        train_end = min_train + fold * horizon
        val_end = train_end + horizon
        if val_end > len(months):
            break
        train_window = months[max(0, train_end - min_train) : train_end]
        val_window = months[train_end:val_end]
        if not val_window:
            break
        folds.append(
            (
                frame[frame[MONTH_COL].isin(train_window)].copy(),
                frame[frame[MONTH_COL].isin(val_window)].copy(),
            )
        )
    return folds


def expanding_window_folds(
    frame: pd.DataFrame, config: SplitConfig | None = None
) -> list[tuple[pd.DataFrame, pd.DataFrame]]:
    """Expanding-window backtest folds.

    The training window grows with each fold while the validation horizon slides
    forward. This is the recommended default for backtesting stable regimes.
    """
    config = config or SplitConfig()
    months = _ordered_months(frame)
    horizon = config.n_val_months
    n_folds = config.n_backtest_folds
    folds: list[tuple[pd.DataFrame, pd.DataFrame]] = []

    first_val = len(months) - n_folds * horizon
    if first_val < 1:
        first_val = horizon

    for fold in range(n_folds):
        train_end = first_val + fold * horizon
        val_end = train_end + horizon
        if val_end > len(months):
            break
        train_window = months[:train_end]
        val_window = months[train_end:val_end]
        if not val_window:
            break
        folds.append(
            (
                frame[frame[MONTH_COL].isin(train_window)].copy(),
                frame[frame[MONTH_COL].isin(val_window)].copy(),
            )
        )
    return folds
