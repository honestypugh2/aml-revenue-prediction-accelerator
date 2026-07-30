"""Tests for the FastAPI backend (offline, synthetic data)."""

from __future__ import annotations

import pytest

pytestmark = pytest.mark.api

pytest.importorskip("fastapi")
pytest.importorskip("httpx")

from fastapi.testclient import TestClient  # noqa: E402

from revenue_prediction.api.app import app  # noqa: E402


@pytest.fixture(scope="module")
def client() -> TestClient:
    return TestClient(app)


def test_health(client: TestClient) -> None:
    resp = client.get("/api/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"


def test_config(client: TestClient) -> None:
    body = client.get("/api/config", params={"env": "test"}).json()
    assert body["environment"] == "test"
    assert body["facilities"] == 3
    assert body["azure_ml_configured"] is False


def test_dataset_overview(client: TestClient) -> None:
    body = client.get("/api/dataset/overview", params={"env": "test"}).json()
    assert body["rows"] > 0
    assert len(body["facilities"]) == 3


def test_facility_series_and_404(client: TestClient) -> None:
    ok = client.get(
        "/api/dataset/facility-series", params={"env": "test", "facility_id": "FAC-001"}
    )
    assert ok.status_code == 200
    assert len(ok.json()["points"]) > 0

    missing = client.get(
        "/api/dataset/facility-series", params={"env": "test", "facility_id": "FAC-999"}
    )
    assert missing.status_code == 404


def test_train(client: TestClient) -> None:
    body = client.post("/api/train", json={"environment": "test"}).json()
    assert body["champion"] in {m["model"] for m in body["ranking"]}
    assert sum(m["is_champion"] for m in body["ranking"]) == 1
    assert len(body["by_snapshot_day"]) >= 1
    assert len(body["by_facility"]) == 3


def test_education_lessons_and_notes(client: TestClient) -> None:
    lessons = client.get("/api/education/lessons").json()
    assert len(lessons) >= 5
    notes = client.get("/api/education/contextual-notes", params={"area": "training"}).json()
    assert notes and all(n["area"] == "training" for n in notes)


def test_knowledge_checks_do_not_leak_answers(client: TestClient) -> None:
    checks = client.get("/api/education/knowledge-checks").json()
    assert checks
    for c in checks:
        assert "correct_index" not in c  # answer must not be exposed


def test_grade_endpoint(client: TestClient) -> None:
    correct = client.post(
        "/api/education/knowledge-checks/grain/grade", json={"chosen_index": 1}
    ).json()
    assert correct["correct"] is True
    wrong = client.post(
        "/api/education/knowledge-checks/grain/grade", json={"chosen_index": 0}
    ).json()
    assert wrong["correct"] is False
    assert (
        client.post(
            "/api/education/knowledge-checks/nope/grade", json={"chosen_index": 0}
        ).status_code
        == 404
    )
