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
as the month progresses?). See `revenue_prediction.evaluation`.

## Champion / challenger

The champion is the best model on the held-out test block by the configured
primary metric; the challenger is the runner-up (or, during retraining, a new
candidate). A challenger is promotable only if it beats the incumbent by a
configured margin, guarding against promotion on noise. See
[`docs/governance/model-governance.md`](../governance/model-governance.md).
