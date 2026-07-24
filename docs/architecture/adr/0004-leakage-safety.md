# ADR 0004: Leakage safety and time-aware validation

- Status: Accepted
- Date: 2026-07-24

## Context

Partial-month prediction is highly susceptible to target leakage. If a feature
for a snapshot uses any information that only becomes available after that
snapshot date — or after accounting close — evaluation metrics become
optimistic and the model fails in production.

## Decision

Enforce the following, in code and in tests:

1. **Forbidden future columns.** The target and any post-close fields
   (`final_contractual_adjustments`, `final_denials`, `month_end_close_flag`)
   are never used as model inputs. `LeakageSafeFeatureBuilder` raises if they
   appear.
2. **As-of consistency.** `days_elapsed == snapshot_day`, and `snapshot_date`
   lies within its `accounting_month`. Enforced by `validate_leakage_rules`.
3. **Historical features from closed months only.** Rolling and prior-period
   net-revenue features are computed strictly from months earlier than the
   current accounting month.
4. **Constant target within a facility-month.** The target cannot vary by
   snapshot; enforced by contract.
5. **Time-aware splitting.** Splitting is by accounting month
   (`blocked_temporal`, `rolling_origin`, or `expanding_window`). All snapshots
   of a facility-month stay in the same split. **Random row splitting is not
   used** as the primary evaluation method.
6. **Fit-on-train-only preprocessing.** Imputation medians and encoder
   categories are learned only from training data.

## Consequences

- Metrics reflect realistic, deployable performance.
- The contract and unit tests (`tests/contract`, `tests/unit`) fail fast if any
  rule is violated, protecting future contributors from reintroducing leakage.
