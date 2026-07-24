# Data dictionary — facility-month-snapshot

All values are synthetic. Grain: `facility_id × accounting_month ×
snapshot_date` (`snapshot_day`).

## Keys / dimensions

| Column | Type | Description |
| --- | --- | --- |
| `facility_id` | string | Neutral facility id, pattern `FAC-\d{3}` (e.g. `FAC-001`) |
| `accounting_month` | string | Accounting month, `YYYY-MM` |
| `snapshot_date` | string | As-of date within the month, `YYYY-MM-DD` |
| `snapshot_day` | int | Day-of-month of the snapshot |
| `service_line_group` | string | Generic service-line grouping |
| `generic_payer_group` | string | Generic payer grouping |
| `encounter_class_group` | string | Generic encounter-class grouping |

## Partial-month operational features (known as-of snapshot)

| Column | Type | Description |
| --- | --- | --- |
| `month_to_date_encounters` | float | MTD encounter count |
| `month_to_date_discharges` | float | MTD discharges |
| `month_to_date_case_mix_index` | float | MTD case-mix index |
| `month_to_date_gross_charges` | float | MTD **billed** charges (not net) |
| `month_to_date_payments` | float | MTD payments received (lags charges) |
| `month_to_date_denials` | float | MTD denied amounts |
| `month_to_date_contractual_adjustments` | float | MTD contractual adjustments |
| `month_to_date_bad_debt` | float | MTD bad debt |
| `month_to_date_charity_care` | float | MTD charity care |
| `month_to_date_length_of_stay` | float | MTD average length of stay |
| `month_to_date_inpatient_volume` | float | MTD inpatient volume |
| `month_to_date_outpatient_volume` | float | MTD outpatient volume |
| `days_elapsed` | float | Days elapsed = `snapshot_day` |
| `business_days_elapsed` | float | Business days elapsed through snapshot |
| `remaining_days` | float | Days remaining in the month |

## Historical features (from strictly-prior closed months)

| Column | Type | Description |
| --- | --- | --- |
| `prior_month_net_revenue` | float | Net revenue of the prior month |
| `prior_year_same_month_net_revenue` | float | Net revenue, same month last year |
| `rolling_3_month_net_revenue` | float | Trailing 3-month mean |
| `rolling_6_month_net_revenue` | float | Trailing 6-month mean |
| `rolling_12_month_net_revenue` | float | Trailing 12-month mean |
| `historical_collection_rate` | float | Facility collection rate |
| `historical_denial_rate` | float | Facility denial rate |
| `historical_adjustment_rate` | float | Facility contractual-adjustment rate |
| `historical_payer_mix` | float | Facility primary-payer share |
| `month` | int | Calendar month (1–12) |
| `quarter` | int | Calendar quarter (1–4) |
| `month_sin` | float | Seasonality encoding, sin |
| `month_cos` | float | Seasonality encoding, cos |

## Target

| Column | Type | Description |
| --- | --- | --- |
| `actual_month_end_net_revenue` | float | **Net** revenue at month-end; known only after close; constant within a facility-month |

## Derived features (created at transform time)

`mtd_collection_ratio`, `mtd_denial_ratio`, `mtd_adjustment_ratio`,
`fraction_month_elapsed`, `mtd_gross_run_rate` — computed by the leakage-safe
feature builder from the columns above.

## Forbidden as inputs (would leak the target)

`actual_month_end_net_revenue`, `final_contractual_adjustments`,
`final_denials`, `month_end_close_flag` (post-close fields).
