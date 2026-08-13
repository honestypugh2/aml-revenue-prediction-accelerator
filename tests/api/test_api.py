"""Tests for the FastAPI backend (offline, synthetic data)."""

from __future__ import annotations

import pytest

pytestmark = pytest.mark.api

pytest.importorskip("fastapi")
pytest.importorskip("httpx")

from fastapi.testclient import TestClient  # noqa: E402

from revenue_prediction.interfaces.api.app import app  # noqa: E402


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


def test_success_criteria_and_readiness_endpoints(client: TestClient) -> None:
    sc = client.get("/api/education/success-criteria").json()
    assert sc["headline"] and sc["metric_targets"] and sc["criteria"]
    dims = client.get("/api/education/data-readiness").json()
    assert len(dims) >= 5
    assert any(d["is_gate"] for d in dims)
    assert all(d["default_rating"] in {"green", "amber", "red"} for d in dims)


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


def test_walkthrough_is_ordered(client: TestClient) -> None:
    steps = client.get("/api/education/walkthrough").json()
    assert len(steps) >= 10
    numbers = [s["number"] for s in steps]
    assert numbers == sorted(numbers)
    assert steps[0]["phase"] == "Frame"
    assert all(s["action"] for s in steps)


def test_pipeline_leakage(client: TestClient) -> None:
    body = client.get("/api/pipeline/leakage", params={"env": "test"}).json()
    assert "actual_month_end_net_revenue" in body["forbidden_columns"]
    assert len(body["rules"]) >= 3


def test_pipeline_target_ratio_above_one(client: TestClient) -> None:
    body = client.get("/api/pipeline/target", params={"env": "test"}).json()
    assert body["items"]
    assert body["average_gross_to_net_ratio"] > 1.0


def test_pipeline_split_is_temporal(client: TestClient) -> None:
    body = client.get("/api/pipeline/split", params={"env": "test"}).json()
    assert body["train_months"] and body["test_months"]
    assert max(body["train_months"]) < min(body["test_months"])


def test_pipeline_features_expands_columns(client: TestClient) -> None:
    body = client.get("/api/pipeline/features", params={"env": "test"}).json()
    assert body["n_engineered"] >= body["n_raw"]
    assert set(body["example"]).issubset(set(body["engineered_features"]))


def test_pipeline_explain_returns_drivers(client: TestClient) -> None:
    body = client.get("/api/pipeline/explain", params={"env": "test", "top": 8}).json()
    assert body["model"]
    assert 1 <= len(body["items"]) <= 8
    assert all("feature" in i and "importance" in i for i in body["items"])


def test_pipeline_predict_scores_checkpoint(client: TestClient) -> None:
    body = client.get(
        "/api/pipeline/predict", params={"env": "test", "cutoff_day": 15, "limit": 5}
    ).json()
    assert body["cutoff_day"] == 15
    assert body["model_name"] and body["model_version"] and body["run_id"]
    assert body["scored_at"]
    assert 1 <= len(body["rows"]) <= 5
    row = body["rows"][0]
    assert row["predicted_month_end_net_revenue"] > 0
    # actuals are joined for teaching; every scored row is at the cutoff day
    assert all(r["snapshot_day"] == 15 for r in body["rows"])


def test_pipeline_cleaning(client: TestClient) -> None:
    body = client.get("/api/pipeline/cleaning", params={"env": "test"}).json()
    assert body["rows"] > 0
    assert body["outlier_note"]
    for c in body["columns_with_missing"]:
        assert c["missing_count"] > 0
        assert "median" in c["strategy"]


def test_pipeline_eda(client: TestClient) -> None:
    body = client.get("/api/pipeline/eda", params={"env": "test", "top": 8}).json()
    assert body["target"] == "actual_month_end_net_revenue"
    assert 1 <= len(body["correlations"]) <= 8
    assert all(-1.0 <= c["corr_with_target"] <= 1.0 for c in body["correlations"])
    assert body["skewness"]


def test_pipeline_optimize(client: TestClient) -> None:
    body = client.get("/api/pipeline/optimize", params={"env": "test"}).json()
    assert body["hyperparameter"] == "learning_rate"
    assert len(body["trials"]) >= 2
    best = [t for t in body["trials"] if t["is_best"]]
    assert len(best) == 1
    assert best[0]["setting"] == body["best_setting"]
    # the flagged best trial has the minimum WAPE
    assert best[0]["wape"] == min(t["wape"] for t in body["trials"])
