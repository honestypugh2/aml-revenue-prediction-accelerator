"""Generate an unseen-month snapshot dataset for inference demos.

Extends the configured synthetic series by ``--extra-months`` and keeps only the
appended months, so facility profiles and history stay continuous with the
training data while the accounting months are genuinely unseen.

Usage:
    uv run python scripts/generate_inference_data.py --env dev --extra-months 3
"""

from __future__ import annotations

import argparse
from pathlib import Path

from revenue_prediction.config.loader import load_settings
from revenue_prediction.core.data.synthetic import generate_synthetic_dataset


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--env", default="dev")
    parser.add_argument("--extra-months", type=int, default=3)
    parser.add_argument(
        "--out", type=Path, default=Path("data/synthetic/revenue_snapshots_new.parquet")
    )
    parser.add_argument(
        "--drop-target",
        action="store_true",
        help="Drop the target column to mimic an open accounting month.",
    )
    args = parser.parse_args()

    settings = load_settings(args.env)
    baseline_months = settings.data.n_months

    extended = settings.data.model_copy(update={"n_months": baseline_months + args.extra_months})
    frame = generate_synthetic_dataset(extended)

    months = sorted(frame["accounting_month"].unique())
    new_months = months[-args.extra_months :]
    new_rows = frame[frame["accounting_month"].isin(new_months)].reset_index(drop=True)

    if args.drop_target:
        new_rows = new_rows.drop(columns=["actual_month_end_net_revenue"])

    args.out.parent.mkdir(parents=True, exist_ok=True)
    new_rows.to_parquet(args.out, index=False)

    print(f"unseen months : {', '.join(new_months)}")
    print(f"rows          : {len(new_rows)}")
    print(f"facilities    : {new_rows['facility_id'].nunique()}")
    print(f"written to    : {args.out}")


if __name__ == "__main__":
    main()
