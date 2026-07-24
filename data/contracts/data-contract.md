# Data contract

This contract defines what a **valid** facility-month-snapshot dataset must
satisfy. It is enforced in code by `revenue_prediction.data.contracts`
(Pandera schema + leakage rules) and covered by `tests/contract`.

## Producer / consumer

- **Producer:** the synthetic generator, or an upstream Fabric/ETL process that
  aggregates operational and financial measures to the snapshot grain.
- **Consumer:** feature engineering, training, and inference in this accelerator.

## Structural rules (schema)

- `facility_id` matches `^FAC-\d{3}$`.
- `accounting_month` matches `^\d{4}-\d{2}$`; `snapshot_date` matches
  `^\d{4}-\d{2}-\d{2}$`.
- `snapshot_day` ∈ [1, 31]; `days_elapsed` ∈ [1, 31]; `remaining_days` ≥ 0.
- Operational and historical measures are numeric and non-negative where
  applicable; nulls are permitted for a controlled set of measures.
- `month` ∈ [1, 12]; `quarter` ∈ [1, 4].
- For **training** data, `actual_month_end_net_revenue` is present and > 0. For
  **inference** data, the target may be absent (`require_target=False`).

See [`schema.json`](schema.json) for the machine-readable definition and
[`data-dictionary.md`](data-dictionary.md) for descriptions.

## Temporal / leakage rules

1. `snapshot_day` equals the day component of `snapshot_date`.
2. `snapshot_date` lies within its `accounting_month`.
3. `days_elapsed == snapshot_day` (no future information).
4. `actual_month_end_net_revenue` is **constant** within a facility-month.
5. Historical features are derived only from strictly-prior closed months.
6. Forbidden post-close columns (`final_contractual_adjustments`,
   `final_denials`, `month_end_close_flag`) must not be used as model inputs.

## Validation

```bash
uv run revenue-prediction validate-data data/synthetic/revenue_snapshots.parquet
# inference data (no target):
uv run revenue-prediction validate-data path/to/inference.parquet --no-require-target
```

## Versioning

Changes to this contract are breaking if they add/remove required columns or
tighten types. Bump the accelerator version and note the change in the pull
request; update `schema.json`, the dictionary, and the tests together.
