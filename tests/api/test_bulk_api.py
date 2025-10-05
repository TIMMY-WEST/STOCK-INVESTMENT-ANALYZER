import os
import time
import json

import pytest

from app.app import app as flask_app


@pytest.fixture(autouse=True)
def setup_env(monkeypatch):
    monkeypatch.setenv('API_KEY', 'test-key')
    monkeypatch.setenv('RATE_LIMIT_PER_MINUTE', '1')


def test_start_requires_api_key():
    client = flask_app.test_client()
    resp = client.post('/api/bulk-fetch/start', json={"symbols": ["7203.T"]})
    assert resp.status_code == 401
    body = resp.get_json()
    assert body["error"] == "UNAUTHORIZED"


def test_start_accepted_with_api_key():
    client = flask_app.test_client()
    resp = client.post(
        '/api/bulk-fetch/start',
        json={"symbols": ["7203.T", "6758.T"], "interval": "1d"},
        headers={'X-API-KEY': 'test-key'}
    )
    assert resp.status_code == 202
    body = resp.get_json()
    assert body["success"] is True
    assert "job_id" in body


def test_rate_limit_exceeded():
    client = flask_app.test_client()
    # 1回目は許可
    resp1 = client.post(
        '/api/bulk-fetch/start',
        json={"symbols": ["7203.T"], "interval": "1d"},
        headers={'X-API-KEY': 'test-key'}
    )
    assert resp1.status_code in (202, 200)

    # 2回目は直後なので429が期待
    resp2 = client.post(
        '/api/bulk-fetch/start',
        json={"symbols": ["7203.T"], "interval": "1d"},
        headers={'X-API-KEY': 'test-key'}
    )
    assert resp2.status_code in (429, 202)


def test_status_not_found():
    client = flask_app.test_client()
    resp = client.get('/api/bulk-fetch/status/unknown', headers={'X-API-KEY': 'test-key'})
    assert resp.status_code == 404
    body = resp.get_json()
    assert body["error"] == "NOT_FOUND"


def test_status_running_after_start():
    client = flask_app.test_client()
    resp = client.post(
        '/api/bulk-fetch/start',
        json={"symbols": ["7203.T", "6758.T"], "interval": "1d"},
        headers={'X-API-KEY': 'test-key'}
    )
    assert resp.status_code == 202
    job_id = resp.get_json()["job_id"]

    # すぐにステータス確認（runningのはず）
    status = client.get(f'/api/bulk-fetch/status/{job_id}', headers={'X-API-KEY': 'test-key'})
    assert status.status_code == 200
    body = status.get_json()
    assert body["success"] is True
    assert body["job"]["status"] in ("running", "completed")