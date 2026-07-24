"""Unit tests for config, automl spec builders, and education content."""

from __future__ import annotations

import pytest

from revenue_prediction.automl import build_automl_job_spec
from revenue_prediction.config.loader import load_settings
from revenue_prediction.config.models import AutoMLConfig, AzureMLConfig
from revenue_prediction.data.schema import TARGET
from revenue_prediction.education import get_knowledge_checks, get_lessons, grade_answer

pytestmark = pytest.mark.unit


def test_layered_config_test_overrides_base() -> None:
    settings = load_settings("test")
    assert settings.environment == "test"
    assert settings.data.n_facilities == 3  # from configs/test
    assert settings.data.seed == 7


def test_placeholders_are_not_configured() -> None:
    settings = load_settings("dev")
    assert settings.azure_ml.is_configured() is False
    assert settings.fabric.is_configured() is False


def test_env_var_override(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("RPA_AZURE_ML__WORKSPACE_NAME", "real-ws")
    monkeypatch.setenv("RPA_AZURE_ML__SUBSCRIPTION_ID", "sub")
    monkeypatch.setenv("RPA_AZURE_ML__RESOURCE_GROUP", "rg")
    settings = load_settings("dev")
    assert settings.azure_ml.workspace_name == "real-ws"
    assert settings.azure_ml.is_configured() is True


def test_automl_spec_uses_target_and_config() -> None:
    spec = build_automl_job_spec(
        AutoMLConfig(max_trials=7),
        AzureMLConfig(compute_cluster="cpu-x"),
        training_data_asset="azureml:train:1",
    )
    assert spec.target_column == TARGET
    assert spec.max_trials == 7
    assert spec.compute == "cpu-x"


def test_education_content_is_consistent() -> None:
    lessons = get_lessons()
    checks = get_knowledge_checks()
    assert len(lessons) >= 5
    assert len(checks) >= 4
    for check in checks:
        assert 0 <= check.correct_index < len(check.options)
        assert grade_answer(check, check.correct_index) is True
