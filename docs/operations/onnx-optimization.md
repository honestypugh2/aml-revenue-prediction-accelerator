# ONNX model optimization

Export the champion to **ONNX** for portable, optimized inference under **ONNX
Runtime** — useful for faster batch scoring and for online endpoints using Azure
ML **prebuilt inference images**.

> Optional. Requires the `onnx` extra: `uv sync --extra onnx`. Synthetic data
> only.

## Why ONNX for this use case

- **Portability:** one model artifact runs across CPU/GPU and OS via ONNX
  Runtime, independent of the training framework.
- **Speed & footprint:** ONNX Runtime often lowers latency and memory, which
  helps a managed online endpoint and keeps batch jobs cheap.
- **Prebuilt images:** Azure ML offers prebuilt inference Docker images that
  include ONNX Runtime, so no-code deployment is possible.

## Export the champion

```python
from revenue_prediction.config.loader import load_settings
from revenue_prediction.core.data.schema import FEATURE_COLUMNS
from revenue_prediction.core.inference.onnx_export import export_estimator_to_onnx
from revenue_prediction.pipelines.local_pipeline import run_local_pipeline

settings = load_settings("dev")
out = run_local_pipeline(settings)
champ = out.results[out.selection.champion]

# n_features = engineered feature count (skip for naive baselines, which have no
# feature_builder and are not typically the deployed champion)
if champ.feature_builder is not None:
    n = len(champ.feature_builder.get_feature_names_out())
    export_estimator_to_onnx(champ.estimator, n_features=n, path="outputs/model.onnx")
```

## Score with ONNX Runtime

```python
from revenue_prediction.core.inference.onnx_export import predict_with_onnx
preds = predict_with_onnx("outputs/model.onnx", engineered_features_matrix)
```

## Notes & caveats

- Convert the **estimator** on the **engineered feature matrix**; apply the same
  `LeakageSafeFeatureBuilder` before scoring so inputs match training.
- Naive baselines (`naive_prior`, `seasonal_naive`) are not sklearn models with a
  feature matrix; export the learned champion instead.
- Validate parity: compare ONNX predictions to the Python model on a sample
  before relying on the ONNX artifact.

## Real-world use: a low-latency "what-if" endpoint for finance

**Scenario.** After the batch job lands month-end estimates, a finance analyst
opens an internal web app and nudges a facility's mid-month inputs (e.g. "what if
gross charges finish 3% higher?") to see the revised net-revenue estimate
**instantly**. This is on-demand, single-facility, sub-second scoring — the one
case where a **managed online endpoint** beats batch.

**Why ONNX here.**

- **Latency:** ONNX Runtime typically returns a single-row prediction in low
  single-digit milliseconds, versus loading a Python model per request.
- **Cost & density:** the smaller runtime lets a modest online endpoint handle
  many analysts; you can pair it with an Azure ML **prebuilt inference image**
  (ONNX Runtime included) for no-code deployment.
- **Portability:** the same `model.onnx` also runs inside the Power BI/Fabric
  layer or an edge tool without shipping the training stack.

**Shape of the deployment.**

1. Export the champion estimator to `model.onnx` (below) and register it.
2. Deploy to a **managed online endpoint** using a prebuilt ONNX inference image;
   the scoring script applies the `LeakageSafeFeatureBuilder`, then calls ONNX
   Runtime.
3. Keep the **batch** pipeline as the system of record for scheduled, all-facility
   scoring; the online ONNX endpoint serves only interactive what-if traffic and
   is deleted when idle to avoid always-on cost.

> Rule of thumb: **batch (pickle/MLflow) for the scheduled run; ONNX online for
> interactive, low-latency what-if scoring.** Most teams need only the batch path.

## References

- ONNX Runtime and models — Azure Machine Learning
- Prebuilt Docker images for inference — Azure Machine Learning
