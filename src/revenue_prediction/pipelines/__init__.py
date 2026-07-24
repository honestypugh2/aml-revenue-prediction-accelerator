"""Pipeline orchestration (local end-to-end + Azure ML pipeline builders)."""

from __future__ import annotations

from .local_pipeline import LocalPipelineOutput, run_local_pipeline

__all__ = ["LocalPipelineOutput", "run_local_pipeline"]
