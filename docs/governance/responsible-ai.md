# Responsible AI

> This accelerator is **operational decision support and financial
> forecasting**. It is **not** clinical decision support, financial advice, an
> autonomous financial decision-making system, or a compliance certification. It
> is not production-ready without organization-specific review.

## Intended use

Provide an early, explainable estimate of month-end net revenue by facility to
support finance and operations planning. A qualified human reviews and decides;
the model informs, it does not decide.

## Out-of-scope / prohibited uses

- Any clinical or patient-care decision.
- Autonomous financial actions without human review.
- Use with real, identifiable patient or finance data before a full privacy,
  security, and compliance review.

## Fairness and disaggregated evaluation

Accuracy is reported **by facility** and **by snapshot day**, not just in
aggregate, so that systematically worse performance for particular facilities or
early-in-month snapshots is visible and can be addressed.

## Transparency and explainability

- Model comparison is published (all candidates, all metrics).
- Global explanations use permutation and native feature importances
  (`revenue_prediction.evaluation.explainability`); AutoML runs with model
  explainability enabled.
- Every prediction is self-describing: model name/version, run id, cutoff day,
  and scoring timestamp travel with the output.

## Data, privacy, and neutrality

- Default data is fully synthetic; no identifiable healthcare data is generated
  or required.
- No customer, participant, or organization-specific identifiers appear anywhere.
- Real deployments must complete a data-protection review before using real
  data.

## Reliability and safety

- Leakage-safe features and time-aware validation prevent optimistic,
  non-deployable metrics (see [ADR 0004](../architecture/adr/0004-leakage-safety.md)).
- Uncertainty bounds are surfaced where the model supports them.
- Drift monitoring and retraining triggers are defined
  ([`docs/operations/`](../operations/)).

## Accountability

- Champion/challenger selection, registration, and promotion follow a documented
  governance process ([model-governance.md](model-governance.md)).
- A human review gate precedes any production promotion.

## Review checklist before production

- [ ] Finance stakeholders validated the target definition and accuracy.
- [ ] Data/privacy review completed for real data sources.
- [ ] Security review completed (network isolation, RBAC, secrets).
- [ ] Disaggregated accuracy reviewed (by facility and snapshot day).
- [ ] Monitoring, alerting, and retraining runbooks in place.
- [ ] Rollback plan and model versioning verified.
