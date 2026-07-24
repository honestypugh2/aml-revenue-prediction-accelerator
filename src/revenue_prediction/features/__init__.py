"""Leakage-safe feature engineering.

The transformer here is deliberately simple and transparent so it can be used
for education. It is a scikit-learn compatible transformer that:

* selects the allowed feature columns (never the forbidden future columns),
* one-hot encodes low-cardinality categoricals,
* imputes missing numeric values using statistics fit ONLY on training data.

Preprocessing statistics are learned in ``fit`` and applied in ``transform`` so
that validation/test data never influence the fitted parameters.
"""

from __future__ import annotations

from .engineering import LeakageSafeFeatureBuilder, build_feature_frame

__all__ = ["LeakageSafeFeatureBuilder", "build_feature_frame"]
