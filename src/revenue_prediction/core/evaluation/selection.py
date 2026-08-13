"""Model comparison and champion / challenger selection."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

import pandas as pd

from revenue_prediction.config.models import EvaluationConfig

if TYPE_CHECKING:  # avoid a circular import at runtime
    from revenue_prediction.core.training.train import TrainingResult


@dataclass
class Selection:
    """Champion / challenger selection outcome."""

    champion: str
    challenger: str | None
    ranking: pd.DataFrame
    metric: str
    challenger_promotable: bool


def comparison_table(results: dict[str, TrainingResult]) -> pd.DataFrame:
    """Return a tidy comparison table of all candidate metrics."""
    rows = []
    for name, res in results.items():
        row = {"model": name, **res.metrics}
        rows.append(row)
    frame = pd.DataFrame(rows)
    return frame


def select_champion_challenger(
    results: dict[str, TrainingResult],
    config: EvaluationConfig | None = None,
    metric: str = "mae",
) -> Selection:
    """Select champion (best) and challenger (second best) by ``metric``.

    Lower-is-better metrics (mae/rmse/mape/smape) are sorted ascending; ``r2``
    is sorted descending. The challenger is flagged promotable only if it beats
    the champion by more than ``challenger_improvement_threshold`` (which, for
    the standard case, it never does — the check exists for the retraining
    workflow where a new model is compared against the incumbent).
    """
    config = config or EvaluationConfig()
    ascending = metric != "r2"
    table = (
        comparison_table(results).sort_values(metric, ascending=ascending).reset_index(drop=True)
    )

    champion = str(table.loc[0, "model"])
    challenger = str(table.loc[1, "model"]) if len(table) > 1 else None

    promotable = False
    if challenger is not None:
        champ_score = float(table.loc[0, metric])
        chall_score = float(table.loc[1, metric])
        if ascending:  # lower is better
            improvement = (champ_score - chall_score) / max(abs(champ_score), 1e-9)
        else:
            improvement = (chall_score - champ_score) / max(abs(champ_score), 1e-9)
        promotable = improvement > config.challenger_improvement_threshold

    return Selection(
        champion=champion,
        challenger=challenger,
        ranking=table,
        metric=metric,
        challenger_promotable=promotable,
    )
