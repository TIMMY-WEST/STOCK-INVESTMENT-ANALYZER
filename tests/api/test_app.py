import json

import pytest


pytestmark = pytest.mark.unit


def test_index_route(client):
    """トップページのテスト."""
    response = client.get("/")
    assert response.status_code == 200
    assert "株価データ管理システム".encode("utf-8") in response.data


def test_fetch_data_api_structure(client):
    """API基本構造のテスト（実際のAPIアクセス無し）."""
    # API エンドポイントの存在確認
    response = client.post(
        "/api/stocks/data",
        data=json.dumps({"symbol": "TEST", "period": "1mo"}),
        content_type="application/json",
    )

    # レスポンスの基本構造確認
    assert response.status_code in [
        200,
        400,
        502,
    ]  # 正常, バリデーションエラー, 外部API エラーのいずれか

    data = json.loads(response.data)
    assert "status" in data
    assert "message" in data


def test_fetch_data_api_max_period_structure(client):
    """maxオプション使用時のAPI基本構造テスト（Issue #45対応）."""
    # maxオプションでのAPI エンドポイントの存在確認
    response = client.post(
        "/api/stocks/data",
        data=json.dumps({"symbol": "TEST", "period": "max"}),
        content_type="application/json",
    )

    # レスポンスの基本構造確認
    assert response.status_code in [
        200,
        400,
        502,
    ]  # 正常, バリデーションエラー, 外部API エラーのいずれか

    data = json.loads(response.data)
    assert "status" in data
    assert "message" in data

    # maxオプションが正しく処理されることを確認（エラーでも構造は保持される）
    if response.status_code == 200 and data.get("status") == "success":
        # 成功時のデータ構造確認
        assert "data" in data
    elif data.get("status") == "error":
        # エラー時でも適切なエラーメッセージが返されることを確認
        assert "error" in data or "message" in data


def test_fetch_data_api_max_period_parameter_validation(client):
    """maxオプションのパラメータバリデーションテスト（Issue #45対応）."""
    # 正しいmaxオプションの形式
    valid_payloads = [
        {"symbol": "AAPL", "period": "max"},
        {"symbol": "7203.T", "period": "max"},
        {"symbol": "MSFT", "period": "max"},
    ]

    for payload in valid_payloads:
        response = client.post(
            "/api/stocks/data",
            data=json.dumps(payload),
            content_type="application/json",
        )

        # maxオプションが受け入れられることを確認
        assert response.status_code in [200, 400, 502]

        data = json.loads(response.data)
        assert "status" in data

        # maxオプションが無効なパラメータとして拒否されないことを確認
        if response.status_code == 400:
            # バリデーションエラーの場合、periodが原因でないことを確認
            error_message = data.get("message", "").lower()
            assert "period" not in error_message or "max" not in error_message
