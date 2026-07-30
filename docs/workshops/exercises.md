# Workshop exercises

All exercises run offline unless marked **(cloud, optional)**. Work in the repo
root with `uv sync --extra api` completed.

> Learning is woven throughout. Each exercise opens with a **Concept** callout
> (the idea you are practising) and closes with a **Question** to check
> understanding. The same guidance appears live in the app's **Learn panel** as
> you work, and deeper lessons are on the app's **Learn** page.

---

## Exercise 1 — Explore the data and the target

**Goal:** understand the grain and why billing ≠ net revenue.

> **Concept:** the target is *net* revenue (after contractual adjustments,
> denials, bad debt, charity care), so gross charges systematically over-state
> it. That gap is exactly what the model must learn to close.

1. Generate data: `uv run revenue-prediction generate-data --env dev`.
2. Launch the UI: `make ui`. In **Overview**, pick a facility and read its
   monthly net-revenue series.
3. In a Python shell, load the dataset and compute, per facility-month at day 15,
   the ratio of `month_to_date_gross_charges` to `actual_month_end_net_revenue`.

**Questions:** Why is that ratio well above 1? Which columns explain the gap?

---

## Exercise 2 — Make leakage tangible

**Goal:** see why future information must never enter a snapshot.

> **Concept:** a feature for a snapshot may only use information available *as
> of* that snapshot date. Post-close fields and the target itself are forbidden
> inputs; the contracts enforce this so leakage fails loudly.

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

> **Concept:** models are compared on a held-out, most-recent test block. Strong
> baselines set the bar; a complex model must beat them to justify itself.

1. `uv run revenue-prediction train-local --env dev --out outputs`.
2. Read the comparison table and the champion.
3. In code, call `train_all_candidates` and inspect `by_snapshot_day` for the
   champion. Does accuracy improve later in the month?

**Question:** If a naive baseline wins, what does that tell you? What would you
change to give the learned models a fair chance (more data, more features)?

---

## Exercise 4 — Change the validation strategy

**Goal:** understand backtesting.

> **Concept:** backtesting evaluates across multiple time-ordered folds so a
> single lucky/unlucky split does not mislead you. Training always precedes its
> validation window in time.

1. Use `rolling_origin_folds` and `expanding_window_folds` on the dataset.
2. Compare fold boundaries. Confirm every training window ends before its
   validation window begins.

**Question:** When would you prefer expanding-window over rolling-origin?

---

## Exercise 5 — Governance: champion/challenger

**Goal:** apply the promotion rule.

> **Concept:** a challenger replaces the champion only if it beats it by a
> configured margin. The margin prevents promoting models on noise.

1. From `train_all_candidates`, call `select_champion_challenger` with different
   `metric` values (`mae`, `rmse`, `r2`).
2. Inspect `challenger_promotable`. Adjust
   `evaluation.challenger_improvement_threshold` and observe the effect.

**Question:** Why require a *margin* before promoting a challenger?

---

## Exercise 6 — Predictions to a (local) Lakehouse

**Goal:** produce Power BI-ready output.

> **Concept:** every prediction is self-describing (model version, run id,
> cutoff day, timestamp) so any number is traceable to the exact model that
> produced it — the foundation of auditability.

1. Score the dataset with the champion bundle (`revenue-prediction predict ...`).
2. Write predictions with `write_predictions_to_onelake(..., local_root=...)`.
3. Open the resulting Parquet and confirm the primary output, secondary outputs
   (model version, run id, cutoff day, scoring timestamp), and dimensions.

---

## Exercise 7 — Drift check

**Goal:** reason about monitoring.

> **Concept:** distributions shift over time. PSI quantifies how far a recent
> window has moved from a reference window, signalling when to investigate or
> retrain.

1. Split the data into an early "reference" window and a later "current" window.
2. Compute `prediction_drift_report` on a few features.
3. Interpret the PSI and status.

---

## Exercise 8 — (cloud, optional) Submit to Azure ML

**Goal:** run the same training in the cloud.

> **Concept:** the same code-first pipeline runs locally and on Azure ML; AutoML
> searches models in parallel. Compare both against the same test block.

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
