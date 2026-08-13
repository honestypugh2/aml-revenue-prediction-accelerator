"""Batch and online inference for the revenue prediction accelerator."""

from __future__ import annotations

from .predict import (
    ModelBundle,
    batch_predict,
    load_bundle,
    save_bundle,
)

__all__ = ["ModelBundle", "batch_predict", "load_bundle", "save_bundle"]
