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

## References

- ONNX Runtime and models — Azure Machine Learning
- Prebuilt Docker images for inference — Azure Machine Learning
