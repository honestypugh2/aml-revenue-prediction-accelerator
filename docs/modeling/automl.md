# Automated ML: configuration, overfitting, and imbalanced data

How this accelerator uses Azure **Automated ML** for the net-revenue regression,
and how it follows Microsoft's guidance on preventing overfitting and handling
imbalanced/skewed data.

## Task & target

- **Task:** regression.
- **Target:** `actual_month_end_net_revenue`.
- **Primary metric:** `normalized_root_mean_squared_error` (scale-invariant
  across facilities of different sizes). Compare AutoML's result to the
  code-first champion's **WAPE** on the same time-aware test period.

## Both authoring surfaces

- **SDK v2:** [`src/revenue_prediction/integrations/automl/regression.py`](../../src/revenue_prediction/integrations/automl/regression.py)
  and [pattern 2](../patterns/automl-sdk.md).
- **Studio UI:** [pattern 1](../patterns/automl-ui.md).

## Preventing overfitting (Microsoft guidance, applied)

| Technique | How we apply it |
| --- | --- |
| **Cross-validation** | `n_cross_validations` (default 5) instead of a single split |
| **Early termination** | `enable_early_termination=True` in `set_limits(...)` |
| **Automatic featurization** | `set_featurization(mode="auto")` (encoding, imputation, scaling) |
| **Held-out comparison** | AutoML's best model is judged against the code-first champion on the **most-recent** months, not a random split |
| **Watch the gap** | A large train-vs-validation gap on the best run is an overfitting signal |

> Time-aware evaluation matters for this use case: because the target is only
> known after close, we always compare models on the most recent held-out
> months, mirroring how the model will be used.

## Imbalanced / skewed data

Revenue features are right-skewed and facility sizes vary widely. Mitigations:

- **Automatic featurization** normalizes and imputes inputs.
- **WAPE** (dollar-weighted) as the headline business metric so a few small
  facilities cannot dominate the score (see [modeling/strategy.md](strategy.md)).
- **Disaggregated evaluation** by facility and snapshot day surfaces where the
  model is weak rather than hiding it in an aggregate.

## Explainability

AutoML runs with `enable_model_explainability=True`; the best run exposes global
feature importance in Studio. This should agree with the code-first drivers
(volume, gross charges, prior net revenue). See
[governance/responsible-ai.md](../governance/responsible-ai.md).

## References

- What is automated ML?
- Set up AutoML with Python (v2) · Set up AutoML for tabular data in the studio
- Prevent overfitting and imbalanced data with Automated ML
- Evaluate AutoML experiment results
