# Workshop exercises

All exercises run offline unless marked **(cloud, optional)**. Work in the repo
root with `uv sync --extra ui` completed.

---

## Exercise 1 — Explore the data and the target

**Goal:** understand the grain and why billing ≠ net revenue.

1. Generate data: `uv run revenue-prediction generate-data --env dev`.
2. Launch the UI: `make ui`. In **Overview**, pick a facility and read its
   monthly net-revenue series.
3. In a Python shell, load the dataset and compute, per facility-month at day 15,
   the ratio of `month_to_date_gross_charges` to `actual_month_end_net_revenue`.

**Questions:** Why is that ratio well above 1? Which columns explain the gap?

---

## Exercise 2 — Make leakage tangible

**Goal:** see why future information must never enter a snapshot.

1. Load the dataset. Add a "cheating" feature equal to the target and try to fit
   `LeakageSafeFeatureBuilder`. Observe the raised error.
2. Tamper with `days_elapsed` for one row and call `validate_leakage_rules`.
   Observe the contract failure.
3. Change the target for a single snapshot within a facility-month and re-run the
   leakage check.

**Question:** Which real-world fields would be "post-close" and therefore
forbidden as inputs?

---

## Exercise 3 — Train and compare code-first candidates

**Goal:** run time-aware training and interpret results.

1. `uv run revenue-prediction train-local --env dev --out outputs`.
2. Read the comparison table and the champion.
3. In code, call `train_all_candidates` and inspect `by_snapshot_day` for the
   champion. Does accuracy improve later in the month?

**Question:** If a naive baseline wins, what does that tell you? What would you
change to give the learned models a fair chance (more data, more features)?

---

## Exercise 4 — Change the validation strategy

**Goal:** understand backtesting.

1. Use `rolling_origin_folds` and `expanding_window_folds` on the dataset.
2. Compare fold boundaries. Confirm every training window ends before its
   validation window begins.

**Question:** When would you prefer expanding-window over rolling-origin?

---

## Exercise 5 — Governance: champion/challenger

**Goal:** apply the promotion rule.

1. From `train_all_candidates`, call `select_champion_challenger` with different
   `metric` values (`mae`, `rmse`, `r2`).
2. Inspect `challenger_promotable`. Adjust
   `evaluation.challenger_improvement_threshold` and observe the effect.

**Question:** Why require a *margin* before promoting a challenger?

---

## Exercise 6 — Predictions to a (local) Lakehouse

**Goal:** produce Power BI-ready output.

1. Score the dataset with the champion bundle (`revenue-prediction predict ...`).
2. Write predictions with `write_predictions_to_onelake(..., local_root=...)`.
3. Open the resulting Parquet and confirm the primary output, secondary outputs
   (model version, run id, cutoff day, scoring timestamp), and dimensions.

---

## Exercise 7 — Drift check

**Goal:** reason about monitoring.

1. Split the data into an early "reference" window and a later "current" window.
2. Compute `prediction_drift_report` on a few features.
3. Interpret the PSI and status.

---

## Exercise 8 — (cloud, optional) Submit to Azure ML

**Goal:** run the same training in the cloud.

1. Provision a workspace (`infra/terraform-quickstart/`).
2. Configure `.env`, `uv sync --extra azure`, `az login`.
3. Build and submit a code-first command job **and** an AutoML regression job.
4. Compare the AutoML leaderboard against your local champion.

> Delete compute/endpoints afterward — see cost & cleanup.

---

## Solutions

Facilitators: reference implementations of the offline exercises mirror the code
in `src/revenue_prediction` and the tests in `tests/`. Encourage learners to read
the corresponding tests to check their work.
