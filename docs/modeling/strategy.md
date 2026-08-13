# Modeling strategy

## The problem is regression-first

We estimate a single scalar — `actual_month_end_net_revenue` — for each
`facility_id × accounting_month × snapshot_date`. Each row already carries
strong, leakage-safe predictors (month-to-date financial measures and historical
net-revenue features). This makes **structured regression** the natural default.
See [ADR 0003](../architecture/adr/0003-model-choice.md).

## Billing amount is not net revenue

Gross charges (billed amounts) systematically **overstate** collectible revenue.
Net revenue subtracts:

- contractual adjustments (payer-negotiated reductions),
- denials,
- bad debt,
- charity care.

The synthetic generator models each effect, so a naive "sum of month-to-date
charges" is visibly a poor estimator of the target. This mirrors the domain
reality described in healthcare net-revenue-forecasting literature.

## Feature availability and recommendations

Not every useful feature is available at the mid-month checkpoint. Based on a
customer feature-discovery review, the drivers fall into **availability tiers**.
The accelerator's schema
([`core.data.schema`](../../src/revenue_prediction/core/data/schema.py)) already
covers each tier; the practical constraint is that **only numeric inputs are
reliably available in the current feed** — categorical dimensions and the
mid-month net-conversion drivers still need sourcing/validation.

| Tier | What it is | Examples (this schema) | Use now? |
| --- | --- | --- | --- |
| **Available now (numeric)** | Volume, occupancy, procedure counts, gross charges, calendar progress | `month_to_date_discharges`, `..._average_daily_census`, `..._occupancy_rate`, `..._length_of_stay`, `..._observation_rate`, `..._surgeries_inpatient/outpatient`, `..._cath_lab_procedures`, `..._imaging_procedures`, `..._gross_charges(_inpatient/outpatient)`, `days_elapsed`, `business_days_elapsed`, `remaining_days` | ✅ Yes |
| **Available now (historical proxy)** | Prior/rolling net revenue and historical **rates** that bridge gross→net | `prior_month_net_revenue`, `prior_year_same_month_net_revenue`, `rolling_3/6/12_month_net_revenue`, `historical_collection_rate`, `historical_denial_rate`, `historical_adjustment_rate`, `historical_payer_mix`, `historical_charge_lag_rate`, `month_sin/cos` | ✅ Yes (the bridge) |
| **Recommended · to validate** | As-of net-conversion / acuity drivers that are sparse, lagged, or not yet mapped mid-month | `month_to_date_contractual_adjustments`, `..._denials`, `..._bad_debt`, `..._charity_care`, `..._case_mix_index`, as-of **payer mix**, categorical dimensions (`service_line_group`, `generic_payer_group`, `encounter_class_group`) | ⚠️ Acquire/validate |
| **Excluded (leakage)** | Only known after close | `final_contractual_adjustments`, `final_denials`, `month_end_close_flag`, and the target itself | ❌ Never an input |

### Building on numeric-only inputs

When the initial numeric features are **not enough** — because the net-revenue
gap (contractual adjustments, denials, bad debt, charity) is exactly what turns
gross into net — we bridge it without waiting for the missing feeds:

1. **Historical-rate proxies (default).** Multiply the available as-of gross
   charges by learned `historical_collection_rate` / `historical_adjustment_rate`
   / `historical_denial_rate` (per facility, and ideally per payer). This is why
   those columns exist and are fit on training data only.
2. **Run-rate + calendar normalization.** Extrapolate `days_elapsed` /
   `business_days_elapsed` to a full month (guarding divide-by-zero early in the
   month) to stabilize the early-checkpoint signal.
3. **Lag/seasonality anchors.** `prior_month_net_revenue` and
   `prior_year_same_month_net_revenue` anchor the level and seasonality.

### Recommended features to acquire next

To move from a numeric-only baseline toward the customer's **±3–5% facility /
WAPE ≤ 4% at day 15** target, prioritize validating and adding, in order:

1. **As-of payer/plan mix** (net-to-gross varies most by payer) — map raw payer
   codes to `generic_payer_group`.
2. **Contractual adjustment & denial rates as-of** (with a documented lag), not
   just historical averages.
3. **Case-mix index (CMI) as-of** for acuity — expect DRG-coding lag; use
   prior-period until validated.
4. **Charge-lag / completeness** per facility (point-in-time posting curves).

Each new feature must stay **leakage-safe** (known by `snapshot_date`) and pass
the [data contract](../../data/contracts/data-contract.md); post-close fields are
excluded by rule.

### Open-source references

Feature-engineering and forecasting practice this approach follows (all
permissively licensed unless noted):

- **scikit-learn** `Pipeline` / `ColumnTransformer` — fit preprocessing on train
  only (the leakage-safe pattern used by `LeakageSafeFeatureBuilder`).
- **feature-engine** — sklearn-compatible encoders/imputers for tabular data.
- **Featuretools** — deep feature synthesis for relational/temporal data.
- **tsfresh** — automated time-series feature extraction (lag/rolling/statistical).
- **Nixtla** `mlforecast` / `statsforecast` — lag & rolling-window features and
  strong forecasting baselines, if the problem shifts to multi-month-ahead.
- **Healthcare open data for domain features:** **CMS** public datasets (HCRIS
  Medicare cost reports; Medicare Provider Utilization & Payment) for payer mix,
  charges, and payments; **PhysioNet MIMIC-IV** (credentialed access) for
  operational/encounter feature-engineering patterns. Use for methodology only;
  no third-party data is redistributed here.

## Target availability

The actual target is only known **after accounting close**. Therefore:

- inference runs repeatedly during the month (at each snapshot) without
  retraining,
- retraining happens on an approved schedule or when drift, degradation, schema
  changes, or upstream-data changes justify it (see
  [`docs/operations/retraining.md`](../operations/retraining.md)).

## Candidates

| Candidate | Type | Role |
| --- | --- | --- |
| `naive_prior` | Baseline | Prior-month net revenue |
| `seasonal_naive` | Baseline | Same month last year |
| `elastic_net` | Linear | Regularized regression |
| `hist_gradient_boosting` | Trees | Fast gradient boosting |
| `xgboost` | Trees | Strong tabular default |

Azure AutoML runs a regression task over the same target for comparison.

## Time-aware validation (never random splits)

Random row splitting leaks future into past. Instead we use:

- **Blocked temporal holdout** (default): most-recent months are test, the
  block before is validation, earlier months are training.
- **Rolling-origin** backtesting: fixed-length window slides forward.
- **Expanding-window** backtesting: growing window, sliding horizon.

All snapshots of a facility-month stay in the same split. Preprocessing is fit
on training data only.

## When formal time-series forecasting is appropriate

If the objective changed to forecasting a facility's revenue **several months
ahead from its own history** (rather than estimating the current month from
within-month signal), sequence models (classical ARIMA/ETS or deep
LSTM/Temporal Fusion) would be appropriate. That is a different problem than the
snapshot-based regression demonstrated here, and would be introduced only via an
explicit, benchmarked experiment.

## Evaluation

Primary metric: **WAPE** (weighted absolute percentage error =
`sum|y-ŷ| / sum|y|`). WAPE is dollar-weighted and stable when some facilities
are small, so a few tiny facilities can't dominate the score the way they can
with MAPE — which is why it is the recommended headline metric for net-revenue
forecasting. **Bias** (signed relative error) is reported alongside it so
directional over-/under-forecasting is visible.

Full bundle: WAPE, bias, MAE, RMSE, MAPE, sMAPE, R². Reported **overall**, **by
facility** (aggregate accuracy), and **by snapshot day** (does accuracy improve
as the month progresses?). See `revenue_prediction.core.evaluation`.

## Champion / challenger

The champion is the best model on the held-out test block by the configured
primary metric; the challenger is the runner-up (or, during retraining, a new
candidate). A challenger is promotable only if it beats the incumbent by a
configured margin, guarding against promotion on noise. See
[`docs/governance/model-governance.md`](../governance/model-governance.md).
