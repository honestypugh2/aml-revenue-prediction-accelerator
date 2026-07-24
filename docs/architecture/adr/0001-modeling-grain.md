# ADR 0001: Modeling grain — facility × accounting month × snapshot

- Status: Accepted
- Date: 2026-07-24

## Context

The business goal is an early, reliable estimate of month-end **net revenue**
from partial-month data. There is a broader future ambition to incorporate
patient-level or encounter-level inputs, but the concrete, reusable
demonstration needs a stable, leakage-safe grain that is:

- available early in the month,
- free of identifiable healthcare data,
- aligned with how finance teams reason about revenue (by facility and month),
- able to support repeated intra-month inference.

## Decision

The default demonstration uses the grain:

- `facility_id`
- `accounting_month`
- `snapshot_date`
- `snapshot_day`

The target is `actual_month_end_net_revenue`, known only after accounting close.
Each facility-month has multiple intra-month snapshots (days 7, 10, 12, 15, 18,
21, 24, 27 by default), enabling repeated scoring without retraining.

## Consequences

- **Positive:** No identifiable healthcare data is required or generated. The
  grain is simple, auditable, and matches financial reporting. Time-aware
  splitting is straightforward at the month level.
- **Positive:** Snapshot-day granularity lets us evaluate accuracy by
  as-of-day, which is directly useful to operations.
- **Trade-off:** Facility-month aggregation hides encounter-level signal. This
  is acceptable for the reusable demonstration and is a documented extension
  point.

## Extension point: patient/encounter aggregation

Patient- or encounter-level records could later be aggregated into leakage-safe
facility snapshots by:

1. Filtering encounter events to those with a service/event date `<=`
   `snapshot_date`.
2. Aggregating month-to-date measures (counts, charges, payments, denials) per
   `facility_id × accounting_month × snapshot_date`.
3. Never joining any field finalized after close (e.g., final adjudicated
   amounts) into a snapshot.
4. Re-running the leakage contract tests to guarantee no post-snapshot leakage.

No patient names, diagnoses, medical record numbers, dates of birth, or
addresses are generated or required at any point.
