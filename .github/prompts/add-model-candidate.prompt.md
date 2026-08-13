---
mode: agent
description: Add a new code-first model candidate with tests.
---

# Add a model candidate

Add a new regression candidate named `${input:name}` to the accelerator.

Steps:

1. In `src/revenue_prediction/core/models/factory.py`, add a branch in
   `build_estimator` returning the new estimator, and include it in
   `supported_models()`. If it consumes raw historical columns (like a
   baseline), also add it to `BASELINE_MODELS`.
2. If it needs new hyperparameters, add a typed field to `ModelConfig` in
   `src/revenue_prediction/config/models.py` with safe defaults, and surface it
   in `configs/base/config.yaml`.
3. Add the candidate to the `candidates` list in the relevant config profiles.
4. Add a unit test that builds the estimator and a smoke assertion that it trains
   on the `test` config split without leakage.
5. Ensure `make check` passes (ruff, pyright, pytest).

Constraints:

- Keep imports guarded if the library is optional.
- Do not make it the default champion by construction; it must win on metrics.
- Preserve time-aware validation and leakage safety.
