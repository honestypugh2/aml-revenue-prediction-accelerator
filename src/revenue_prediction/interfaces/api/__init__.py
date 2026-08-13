"""FastAPI backend serving the React educational UI over the Python core.

Import-safe without the ``api`` extra: importing this subpackage does not import
FastAPI. The application and its factory live in
:mod:`revenue_prediction.interfaces.api.app`; import them from there::

    from revenue_prediction.interfaces.api.app import app, create_app
"""

from __future__ import annotations

__all__: list[str] = []
