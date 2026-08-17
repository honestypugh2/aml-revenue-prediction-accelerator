# Models & evaluation metrics — a plain-language catalog

This page defines **every model** the accelerator trains and compares, the
**class/type** of problem it is, and **every evaluation metric** — what it
measures, its units, and how to use it. It is the reference behind the
[model selection & evaluation guide](../patterns/model-selection-and-evaluation.md).

## What kind of ML problem is this?

| Dimension | This accelerator |
| --- | --- |
| Learning type | **Supervised** — every training row has a known label (`actual_month_end_net_revenue`) after close |
| Task | **Regression** — predict a continuous dollar amount (not a class, so **not classification**) |
| Data shape | **Tabular**, panel/longitudinal (facility × month × snapshot) with **time-aware** validation |
| Time series? | Time-*aware* regression, not a pure univariate time-series model. Sequence models (e.g. LSTM) are possible but **not** the default — see [ADR 0003](../architecture/adr/0003-model-choice.md) |
| Deep learning? | **No** by default — tabular gradient-boosted trees outperform deep nets here and are cheaper and more explainable |
| Generative AI? | **No** — this is classical, predictive ML, not an LLM/generative system |
| Unsupervised? | **No** — labels exist; we do not cluster or reduce dimensions as the objective |

> One-line: **supervised, tabular, time-aware regression** with classical models,
> mapped to the classical-ML MLOps v2 architecture.

## Models compared

The code-first path trains these candidates and picks a champion by **WAPE**
([`core.models.factory`](../../src/revenue_prediction/core/models/factory.py)).
Baselines set the bar the learned models must beat.

| Model | Class / family | Type | Why it's here | Tends to win when… |
| --- | --- | --- | --- | --- |
| `naive_prior` | Heuristic **baseline** ([`PriorPeriodNaive`](../../src/revenue_prediction/core/models/baselines.py)) | Non-learned | "This month ≈ last month's net revenue." The honesty check. | Revenue is very stable month to month |
| `seasonal_naive` | Heuristic **baseline** (`SeasonalNaive`) | Non-learned | "This month ≈ same month last year." | Strong yearly seasonality |
| `elastic_net` | **Linear regression** (L1+L2 regularized) | Supervised, parametric | Fast, interpretable coefficients; a strong linear reference | Relationships are mostly linear; few interactions |
| `gradient_boosting` | **Gradient-boosted trees** (sklearn `GradientBoostingRegressor`) | Supervised, ensemble | The reference **default champion**; captures non-linearities and interactions | Tabular data with mixed, non-linear drivers (typical here) |
| `hist_gradient_boosting` | **Histogram GBM** (sklearn) | Supervised, ensemble | Faster boosting on larger data; handles missing values natively | Larger datasets; speed matters |
| `random_forest` | **Bagged trees** (sklearn) | Supervised, ensemble | Robust, low-variance baseline ensemble | Noisy data; you want a stable, low-tuning model |
| `xgboost` | **Gradient-boosted trees** (XGBoost) | Supervised, ensemble | Highly competitive boosting with regularization | You need max accuracy and can tune |
| **AutoML best** | **Azure ML AutoML regression** | Supervised, ensemble/search | Searches many algorithms + stacked ensembles automatically | You want a strong benchmark fast, no manual tuning |

**How AutoML compares models:** Azure ML AutoML trains many candidate algorithms
(elastic net, LightGBM, XGBoost, random forest, extra trees, and stacked/voting
**ensembles**) and ranks them on a **leaderboard** by the primary metric. It also
generates model explanations automatically. In this accelerator AutoML is the
**benchmark**; the code-first `gradient_boosting` is the governed **champion**.

## Evaluation metrics — what each measures and how to use it

Computed in [`core.evaluation.metrics`](../../src/revenue_prediction/core/evaluation/metrics.py)
and reported **overall and by facility and by snapshot day**.

| Metric | Formula (intuition) | Units | Lower/Higher better | What it measures | How to use it |
| --- | --- | --- | --- | --- | --- |
| **WAPE** *(primary)* | Σ\|y−ŷ\| / Σ\|y\| | fraction (× 100 = %) | **Lower** | **Dollar-weighted** error: total error as a share of total revenue | Headline accuracy. Robust when facilities differ in size (big facilities can't be hidden by tiny ones) |
| **bias** | Σ(ŷ−y) / Σy | fraction | **0 is ideal** | Directional error: are we systematically over/under-forecasting? | Read *with* WAPE. Positive = over-forecast; negative = under-forecast. A low WAPE with high bias still misleads finance |
| **MAE** | mean\|y−ŷ\| | dollars | Lower | Average absolute dollar miss per row | Communicate typical error in **dollars** to stakeholders |
| **RMSE** | √mean((y−ŷ)²) | dollars | Lower | Like MAE but **penalizes big misses** more | Use when large one-off errors are especially costly |
| **MAPE** | mean\|(y−ŷ)/y\| | fraction | Lower | Average **percentage** error per row | Intuitive %, but unstable for small facilities — why WAPE is primary |
| **sMAPE** | mean(2\|ŷ−y\|/(\|y\|+\|ŷ\|)) | fraction (0–2) | Lower | Symmetric percentage error (bounded) | A more stable % than MAPE for small denominators |
| **R²** | 1 − SS_res/SS_tot | unitless (≤1) | **Higher** | Share of variance explained vs. the mean | Sanity check that the model beats predicting the average |

**Uncertainty / interval coverage** (ensemble models): the batch output includes
`prediction_lower`/`prediction_upper`. Target ~80% **coverage** (the share of
actuals that fall inside the interval) so finance can see confidence, not just a
point estimate.

### Why WAPE is the primary metric

Finance cares about **dollars in aggregate**, not the average of per-row
percentages. MAPE lets a tiny facility with a 40% miss dominate; WAPE weights by
revenue so the number reflects the real dollar risk. Bias is reported alongside
so directional error is never hidden. See
[modeling/strategy.md](strategy.md) and
[success-metrics-and-kpis.md](success-metrics-and-kpis.md).

## AutoML run metrics in Azure ML Studio

When you open a run in **Assets -> Jobs -> Metrics**, Studio shows a broader set
of regression metrics than the headline WAPE. Here is how to read them for this
use case (example values from a synthetic AutoML run):

| Studio metric | Example | What it measures | How to read it here |
| --- | --- | --- | --- |
| **Explained variance** | 0.99997 | Share of variance captured (like R² but not penalizing bias) | Near 1 = model tracks the ups/downs of revenue well |
| **Mean absolute error (MAE)** | 1274.2 | Average absolute **dollar** miss | Typical dollar error per facility-month; communicate this to finance |
| **Mean absolute percentage error (MAPE)** | 0.030281 | Average **%** error per row | ~3% average; unstable for tiny facilities (why WAPE is primary) |
| **Median absolute error** | ~0 | Middle absolute error | Very low = most rows nearly exact; a few large misses pull MAE up |
| **Normalized MAE** | 0.00025 | MAE scaled to the target range | Scale-free; compare across datasets |
| **Normalized median absolute error** | ~0 | Median error, scaled | Robust to outliers |
| **Normalized RMSE (NRMSE)** | 0.0015 | RMSE scaled to range — **AutoML's primary metric here** | Lower is better; the leaderboard ranks on this |
| **Normalized RMSE log error** | 0.0012 | NRMSE on a log scale | Emphasizes proportional error |
| **R² score** | 0.99997 | Variance explained vs. predicting the mean | Near 1 = far better than the naive average |
| **Root mean squared error (RMSE)** | 7566.7 | Dollar error, **penalizing large misses** | Bigger than MAE => a few large errors exist; investigate those facilities |
| **Root mean squared log error (RMSLE)** | 0.0016 | RMSE on a log scale | Penalizes under-prediction less harshly |
| **Spearman correlation** | 0.99991 | Rank correlation of predicted vs. actual | Near 1 = ranks facilities correctly (useful for prioritization) |

**How to use this screen:**

- **Rank/select** on AutoML's primary metric (**NRMSE**); confirm **R²** and
  **Explained variance** are high and similar (large gaps hint at bias).
- **Translate to dollars** with **MAE** (typical miss) and **RMSE** (worst-case
  sensitivity). If RMSE >> MAE, a few facilities have large errors — disaggregate.
- **Cross-check** against the accelerator's headline **WAPE + bias**, then grade
  against the [KPI scorecard](success-metrics-and-kpis.md). Studio's built-ins are
  per-row; WAPE is dollar-weighted, which is why we report both.

> Very high R²/low error on **synthetic** data is expected — the generator is
> learnable by design. On real data, expect more modest numbers and rely on the
> disaggregated WAPE/bias and the KPI scorecard, not a single headline metric.

## From metrics to a decision

1. **Compare** candidates on WAPE (code-first) or the leaderboard (AutoML).
2. **Select** the champion (lowest WAPE) and a challenger; promotion needs the
   challenger to beat the incumbent by the configured margin.
3. **Disaggregate** by facility and snapshot day — a good average can hide a bad
   facility or a weak early checkpoint.
4. **Grade** against per-checkpoint targets and business KPIs
   ([scorecard](success-metrics-and-kpis.md)).
5. **Govern** — human-gated promotion after Responsible AI review.

## Model file format & safety (what image 1 shows)

A registered MLflow model's artifacts include `MLmodel`, `conda.yaml`,
`requirements.txt`, and a serialized model — here `python_model.pkl` (the pyfunc
wrapper) plus the estimator. `.pkl` is **Python pickle** (MLflow uses
`cloudpickle`), the standard MLflow/scikit-learn serialization format.

**Is pickle safe here?** Pickle can execute arbitrary code on load, so the rule
is: **only load models from a trusted source.** In this accelerator that holds
because:

- Models are produced by **our** training jobs and stored in the **Azure ML
  registry** with lineage (job/run id) — not downloaded from the internet.
- Access is controlled by **workspace RBAC**; the batch scorer loads the model
  from the registry inside the workspace, not from user input.
- The MLflow **model signature** and pinned `requirements.txt` make the
  environment reproducible.

**When to prefer another format:** for portable, faster, or cross-language
serving, export the estimator to **ONNX** (no arbitrary-code-execution risk on
load) — see [operations/onnx-optimization.md](../operations/onnx-optimization.md).
Do **not** load `.pkl`/`.joblib` files from untrusted sources.

## Related

- [Model selection & evaluation across patterns](../patterns/model-selection-and-evaluation.md)
- [Success metrics & KPIs](success-metrics-and-kpis.md)
- [Modeling strategy](strategy.md) · [ADR 0003 — model choice](../architecture/adr/0003-model-choice.md)
