# Data

> **All data in this repository is fully synthetic.** It contains no customer,
> patient, or organization-specific information. Do not place real patient or
> finance data in this directory.

## Contents

| Path | Description |
| --- | --- |
| `synthetic/` | Generated dataset (git-ignored; regenerate on demand) |
| `sample/` | Small committed samples for tests and quick inspection |
| `contracts/` | Schema and data-contract definitions |

Regenerate datasets:

```bash
uv run revenue-prediction generate-data --env dev
```

This writes `synthetic/revenue_snapshots.parquet`,
`sample/revenue_snapshots_sample.csv`, and a deliberately-invalid
`sample/revenue_snapshots_invalid.csv` used by contract tests.

## Grain

`facility_id × accounting_month × snapshot_date` (with `snapshot_day`). Each
facility-month has multiple intra-month snapshots (default days 7, 10, 12, 15,
18, 21, 24, 27). See [ADR 0001](../docs/architecture/adr/0001-modeling-grain.md).

## Provenance & generation assumptions

The dataset is produced by `revenue_prediction.data.synthetic` with a fixed seed
for reproducibility. It models — synthetically — seasonality, facility effects,
service-line and payer-mix effects, payment lag, denial and adjustment patterns,
missing values, outliers, and controlled noise. The "actual" month-end net
revenue is computed per facility-month and is identical across that month's
snapshots (it is only known after close).

No third-party dataset is redistributed. The dataset references listed in the
project brief were reviewed for domain understanding only; none were copied. See
[`THIRD_PARTY_NOTICES.md`](../THIRD_PARTY_NOTICES.md).

## Billing amount vs net revenue

`month_to_date_gross_charges` is a **billing** amount and overstates collectible
revenue. The target `actual_month_end_net_revenue` is **net** of contractual
adjustments, denials, bad debt, and charity care. See
[`docs/modeling/strategy.md`](../docs/modeling/strategy.md).

## Target availability & leakage rules

- The target is known only **after accounting close**.
- A feature for a snapshot must never use information from after its
  `snapshot_date`.
- Historical features use only strictly-prior closed months.

These rules are enforced by `revenue_prediction.data.contracts` and covered by
tests in `tests/contract`.

## Data dictionary

See [`contracts/data-dictionary.md`](contracts/data-dictionary.md).
