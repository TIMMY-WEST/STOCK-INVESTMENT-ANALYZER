import json

import pytest


pytestmark = pytest.mark.unit


def test_index_route_with_get_request_returns_success_response(client):
    """トップページのテスト."""
    # Arrange (準備)
    endpoint = "/"

    # Act (実行)
    response = client.get(endpoint)

    # Assert (検証)
    assert response.status_code == 200
    assert "株価データ管理システム".encode("utf-8") in response.data


def test_fetch_data_api_with_basic_request_returns_valid_structure(client):
    """API基本構造のテスト（実際のAPIアクセス無し）."""
    # Arrange (準備)
    endpoint = "/api/stocks/data"
    payload = {"symbol": "TEST", "period": "1mo"}

    # Act (実行)
    response = client.post(
        endpoint,
        data=json.dumps(payload),
        content_type="application/json",
    )

    # Assert (検証)
    assert response.status_code in [
        200,
        400,
        502,
    ]  # 正常, バリデーションエラー, 外部API エラーのいずれか

    data = json.loads(response.data)
    assert "status" in data
    assert "message" in data


def test_fetch_data_api_with_max_period_returns_valid_structure(client):
    """maxオプション使用時のAPI基本構造テスト（Issue #45対応）."""
    # Arrange (準備)
    endpoint = "/api/stocks/data"
    payload = {"symbol": "TEST", "period": "max"}

    # Act (実行)
    response = client.post(
        endpoint,
        data=json.dumps(payload),
        content_type="application/json",
    )

    # Assert (検証)
    assert response.status_code in [
        200,
        400,
        502,
    ]  # 正常, バリデーションエラー, 外部API エラーのいずれか

    data = json.loads(response.data)
    assert "status" in data
    assert "message" in data

    if response.status_code == 200 and data.get("status") == "success":
        assert "data" in data
    elif data.get("status") == "error":
        assert "error" in data or "message" in data


def test_fetch_data_api_with_max_period_parameter_passes_validation(client):
    """maxオプションのパラメータバリデーションテスト（Issue #45対応）."""
    # Arrange (準備)
    endpoint = "/api/stocks/data"
    valid_payloads = [
        {"symbol": "AAPL", "period": "max"},
        {"symbol": "7203.T", "period": "max"},
        {"symbol": "MSFT", "period": "max"},
    ]

    for payload in valid_payloads:
        # Act (実行)
        response = client.post(
            endpoint,
            data=json.dumps(payload),
            content_type="application/json",
        )

        # Assert (検証)
        assert response.status_code in [200, 400, 502]

        data = json.loads(response.data)
        assert "status" in data

        if response.status_code == 400:
            error_message = data.get("message", "").lower()
            assert "period" not in error_message or "max" not in error_message
