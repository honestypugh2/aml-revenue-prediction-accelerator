"""FastAPI backend serving the React educational UI over the Python core.

Import-safe without the ``api`` extra: importing this subpackage does not import
FastAPI. Import :mod:`revenue_prediction.api.app` (which requires the extra) to
build the application.
"""

from __future__ import annotations

__all__ = ["create_app"]


def create_app():  # pragma: no cover - thin lazy wrapper
    """Lazily build and return the FastAPI app (requires the ``api`` extra)."""
    from .app import create_app as _create_app

    return _create_app()
