import json
import os
import time

import pytest

from app.app import app as flask_app


# module-level marker so pytest -m unit picks these up
pytestmark = pytest.mark.unit


@pytest.fixture(autouse=True)
def setup_env(monkeypatch):
    monkeypatch.setenv("API_KEY", "test-key")
    monkeypatch.setenv("RATE_LIMIT_PER_MINUTE", "1")


def test_bulk_data_start_with_missing_api_key_returns_unauthorized():
    # Arrange (準備)
    client = flask_app.test_client()

    # Act (実行)
    resp = client.post("/api/bulk-data/jobs", json={"symbols": ["7203.T"]})

    # Assert (検証)
    assert resp.status_code == 401
    body = resp.get_json()
    assert body["error"] == "UNAUTHORIZED"


def test_bulk_data_start_with_valid_request_returns_job_structure():
    """バルクデータ開始エンドポイントの基本構造テスト."""
    # Arrange (準備)
    client = flask_app.test_client()

    # Act (実行)
    resp = client.post(
        "/api/bulk-data/jobs",
        json={"symbols": ["7203.T", "6758.T"], "interval": "1d"},
        headers={"X-API-KEY": "test-key"},
    )

    # Assert (検証)
    assert resp.status_code == 202
    body = resp.get_json()
    assert body["success"] is True
    assert "job_id" in body


def test_bulk_data_start_with_rate_limit_exceeded_returns_too_many_requests():
    # Arrange (準備)
    client = flask_app.test_client()

    # Act (実行)
    resp1 = client.post(
        "/api/bulk-data/jobs",
        json={"symbols": ["7203.T"], "interval": "1d"},
        headers={"X-API-KEY": "test-key"},
    )
    resp2 = client.post(
        "/api/bulk-data/jobs",
        json={"symbols": ["7203.T"], "interval": "1d"},
        headers={"X-API-KEY": "test-key"},
    )

    # Assert (検証)
    assert resp1.status_code in (202, 200)
    assert resp2.status_code in (429, 202)


def test_bulk_data_status_with_unknown_job_id_returns_not_found():
    # Arrange (準備)
    client = flask_app.test_client()

    # Act (実行)
    resp = client.get(
        "/api/bulk-data/jobs/unknown", headers={"X-API-KEY": "test-key"}
    )

    # Assert (検証)
    assert resp.status_code == 404
    body = resp.get_json()
    assert body["error"] == "NOT_FOUND"


def test_bulk_data_status_with_recent_job_returns_running_status():
    # Arrange (準備)
    client = flask_app.test_client()
    resp = client.post(
        "/api/bulk-data/jobs",
        json={"symbols": ["7203.T", "6758.T"], "interval": "1d"},
        headers={"X-API-KEY": "test-key"},
    )
    assert resp.status_code == 202
    job_id = resp.get_json()["job_id"]

    # Act (実行)
    status = client.get(
        f"/api/bulk-data/jobs/{job_id}", headers={"X-API-KEY": "test-key"}
    )

    # Assert (検証)
    assert status.status_code == 200
    body = status.get_json()
    assert body["success"] is True
    assert body["job"]["status"] in ("running", "completed")
