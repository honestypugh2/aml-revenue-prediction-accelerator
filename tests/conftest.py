"""Shared pytest fixtures."""

from __future__ import annotations

import pandas as pd
import pytest

from revenue_prediction.config.loader import load_settings
from revenue_prediction.config.models import Settings
from revenue_prediction.data.synthetic import generate_synthetic_dataset


@pytest.fixture(scope="session")
def settings() -> Settings:
    return load_settings("test")


@pytest.fixture(scope="session")
def dataset(settings: Settings) -> pd.DataFrame:
    return generate_synthetic_dataset(settings.data)
