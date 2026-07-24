# ADR 0003: Model choice — regression-first, not LSTM-by-default

- Status: Accepted
- Date: 2026-07-24

## Context

The reference repository demonstrates LSTM time-series forecasting. The brief
asks whether to retain an LSTM. Predicting month-end net revenue from
partial-month snapshots is fundamentally a **structured regression** problem:
each row already carries strong, leakage-safe predictors (month-to-date
financial measures and historical net-revenue features), and the prediction is a
single scalar per facility-month-snapshot.

## Decision

Use a **regression-first** design. The default code-first candidates are:

1. `naive_prior` — prior-month net revenue (baseline).
2. `seasonal_naive` — same month last year (baseline).
3. `elastic_net` — regularized linear regression.
4. `hist_gradient_boosting` — histogram gradient boosting.
5. `xgboost` — gradient boosting (strong tabular default).

Azure AutoML is used in parallel for a regression task over the same target.

An LSTM (or other sequence model) is **not** the default. It may be added only
via an explicit experiment that demonstrates it is justified for a specific
data regime, and it must be compared fairly against the regression baselines on
the same time-aware test block.

## Rationale

- Tabular gradient boosting and regularized linear models are strong, fast, and
  explainable for this feature set.
- Time-awareness is handled by **splitting and features**, not by requiring a
  recurrent architecture.
- Simpler models are easier to govern, reproduce, and operate.

## When formal time-series forecasting is appropriate

If the task shifted to forecasting a facility's revenue trajectory multiple
months ahead from its own history (rather than estimating the current month from
within-month signal), classical or deep sequence forecasting would become
appropriate. See [`docs/modeling/strategy.md`](../../modeling/strategy.md).

## Consequences

- The accelerator stays lightweight (no GPU/PyTorch required by default).
- Model comparison is apples-to-apples across AutoML and code-first candidates.
