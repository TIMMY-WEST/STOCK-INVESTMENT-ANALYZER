"""銘柄マスター・システム監視API統合テスト.

このモジュールは銘柄マスターとシステム監視関連APIエンドポイントの統合テストを提供します。
- 銘柄マスターの更新・一覧取得・ステータス確認
- システムヘルスチェック
- データベース接続テスト
- 外部API接続テスト
"""

import json

import pytest

from app.app import app as flask_app


@pytest.fixture
def client():
    """テスト用のFlaskクライアント."""
    flask_app.config["TESTING"] = True
    with flask_app.test_client() as client:
        yield client


@pytest.fixture(autouse=True)
def setup_env(monkeypatch):
    """テスト環境のセットアップ."""
    monkeypatch.setenv("API_KEY", "test-key")
    monkeypatch.setenv("RATE_LIMIT_PER_MINUTE", "10")


class TestStockMasterAPI:
    """銘柄マスターAPI統合テスト."""

    def test_update_stock_master_success(self, client, mocker):
        """POST /api/stock-master/ - 銘柄マスター更新成功."""
        # Arrange (準備)
        mock_result = {
            "status": "success",
            "message": "Stock master updated successfully",
        }
        mocker.patch(
            "app.services.jpx.jpx_stock_service.JPXStockService.update_stock_master",
            return_value=mock_result,
        )

        # Act (実行)
        response = client.post(
            "/api/stock-master/",
            headers={"X-API-KEY": "test-key"},
            json={},
            content_type="application/json",
        )

        # Assert (検証)
        assert response.status_code in [200, 202]
        data = response.get_json()
        assert "status" in data
        assert "message" in data

    def test_update_stock_master_unauthorized(self, client):
        """POST /api/stock-master/ - 認証エラー."""
        # Arrange (準備)
        # 認証ヘッダーなしでリクエストを準備

        # Act (実行)
        response = client.post("/api/stock-master/")

        # Assert (検証)
        assert response.status_code == 401
        data = response.get_json()
        assert "error" in data

    def test_update_stock_master_service_error(self, client, mocker):
        """POST /api/stock-master/ - サービスエラー."""
        # Arrange (準備)
        mocker.patch(
            "app.services.jpx.jpx_stock_service.JPXStockService.update_stock_master",
            side_effect=Exception("Service error"),
        )

        # Act (実行)
        response = client.post(
            "/api/stock-master/", headers={"X-API-KEY": "test-key"}
        )

        # Assert (検証)
        assert response.status_code in [500, 503]
        data = response.get_json()
        assert data.get("status") == "error" or "error" in data

    def test_get_stock_master_list_success(self, client, mocker):
        """GET /api/stock-master/ - 銘柄マスター一覧取得成功."""
        # Arrange (準備)
        mock_stocks = [
            {
                "symbol": "7203.T",
                "name": "Toyota Motor Corporation",
                "market": "Prime",
            },
            {
                "symbol": "6758.T",
                "name": "Sony Group Corporation",
                "market": "Prime",
            },
        ]
        mocker.patch(
            "app.api.stock_master.get_stock_master_list",
            return_value=({"data": mock_stocks}, 200),
        )

        # Act (実行)
        response = client.get(
            "/api/stock-master/", headers={"X-API-KEY": "test-key"}
        )

        # Assert (検証)
        assert response.status_code == 200
        data = response.get_json()
        assert "data" in data or "message" in data

    def test_get_stock_master_list_empty(self, client, mocker):
        """GET /api/stock-master/ - 空の銘柄マスター一覧."""
        # Arrange (準備)
        mocker.patch(
            "app.api.stock_master.get_stock_master_list",
            return_value=({"data": []}, 200),
        )

        # Act (実行)
        response = client.get(
            "/api/stock-master/", headers={"X-API-KEY": "test-key"}
        )

        # Assert (検証)
        assert response.status_code == 200
        data = response.get_json()
        assert "data" in data or "message" in data

    def test_get_stock_master_status_success(self, client, mocker):
        """GET /api/stock-master/status - 銘柄マスターステータス取得成功."""
        # Arrange (準備)
        mock_status = {
            "last_updated": "2025-01-01T00:00:00",
            "total_stocks": 100,
            "status": "healthy",
        }
        mocker.patch(
            "app.api.stock_master.get_stock_master_status",
            return_value=({"data": mock_status}, 200),
        )

        # Act (実行)
        response = client.get(
            "/api/stock-master/status", headers={"X-API-KEY": "test-key"}
        )

        # Assert (検証)
        assert response.status_code == 200
        data = response.get_json()
        assert "data" in data or "message" in data

    def test_stock_master_response_format(self, client, mocker):
        """銘柄マスターAPIレスポンス形式検証."""
        # Arrange (準備)
        mock_stocks = []
        mocker.patch(
            "app.api.stock_master.get_stock_master_list",
            return_value=({"data": mock_stocks}, 200),
        )

        # Act (実行)
        response = client.get(
            "/api/stock-master/", headers={"X-API-KEY": "test-key"}
        )

        # Assert (検証)
        assert "application/json" in response.content_type


class TestSystemMonitoringAPI:
    """システム監視API統合テスト."""

    def test_database_connection_success(self, client, mocker):
        """GET /api/system/database/connection - DB接続テスト成功."""
        # Arrange (準備)
        mock_result = {
            "status": "success",
            "message": "Database connection successful",
            "database": "postgresql",
        }
        mocker.patch(
            "app.api.system_monitoring.test_database_connection",
            return_value=(mock_result, 200),
        )

        # Act (実行)
        response = client.get("/api/system/database/connection")

        # Assert (検証)
        assert response.status_code == 200
        data = response.get_json()
        assert data["status"] == "success"
        assert "message" in data

    def test_database_connection_failure(self, client, mocker):
        """GET /api/system/database/connection - データベース接続失敗."""
        # Arrange (準備)
        mock_session = mocker.MagicMock()
        mock_session.execute.side_effect = Exception(
            "Database connection failed"
        )
        mock_session.__enter__.return_value = mock_session
        mock_session.__exit__.return_value = None
        mocker.patch(
            "app.api.system_monitoring.get_db_session",
            return_value=mock_session,
        )

        # Act (実行)
        response = client.get("/api/system/database/connection")

        # Assert (検証)
        assert response.status_code == 500
        data = response.get_json()
        assert data["status"] == "error"

    def test_external_api_connection_success(self, client, mocker):
        """GET /api/system/external-api/connection - 外部API接続テスト成功."""
        # Arrange (準備)
        mock_result = {
            "status": "success",
            "message": "External API connection successful",
        }
        mocker.patch(
            "app.api.system_monitoring.test_api_connection",
            return_value=(mock_result, 200),
        )

        # Act (実行)
        response = client.get("/api/system/external-api/connection")

        # Assert (検証)
        assert response.status_code == 200
        data = response.get_json()
        assert data["status"] == "success"

    def test_external_api_connection_failure(self, client, mocker):
        """GET /api/system/external-api/connection - 外部API接続失敗."""
        # Arrange (準備)
        mocker.patch(
            "app.services.stock_data.fetcher.StockDataFetcher.fetch_stock_data",
            side_effect=Exception("API connection failed"),
        )

        # Act (実行)
        response = client.get("/api/system/external-api/connection")

        # Assert (検証)
        assert response.status_code == 500
        data = response.get_json()
        assert data["status"] == "error"

    def test_health_check_success(self, client, mocker):
        """GET /api/system/health - ヘルスチェック成功."""
        # Arrange (準備)
        mock_result = {
            "data": {
                "overall_status": "healthy",
                "database": "ok",
                "external_api": "ok",
                "timestamp": "2025-01-01T00:00:00",
            }
        }
        mocker.patch(
            "app.api.system_monitoring.health_check",
            return_value=(mock_result, 200),
        )

        # Act (実行)
        response = client.get("/api/system/health")

        # Assert (検証)
        assert response.status_code == 200
        data = response.get_json()
        assert "data" in data
        assert "overall_status" in data["data"]

    def test_health_check_degraded(self, client, mocker):
        """GET /api/system/health - ヘルスチェック劣化状態."""
        # Arrange (準備)
        mocker.patch(
            "app.services.stock_data.fetcher.StockDataFetcher.fetch_stock_data",
            return_value=None,
        )

        # Act (実行)
        response = client.get("/api/system/health")

        # Assert (検証)
        assert response.status_code == 200
        data = response.get_json()
        assert data["data"]["overall_status"] == "degraded"

    def test_health_check_error(self, client, mocker):
        """GET /api/system/health - ヘルスチェックエラー."""
        # Arrange (準備)
        mock_session = mocker.MagicMock()
        mock_session.execute.side_effect = Exception(
            "Database connection failed"
        )
        mock_session.__enter__.return_value = mock_session
        mock_session.__exit__.return_value = None
        mocker.patch(
            "app.api.system_monitoring.get_db_session",
            return_value=mock_session,
        )

        # Act (実行)
        response = client.get("/api/system/health")

        # Assert (検証)
        assert response.status_code == 200
        data = response.get_json()
        assert data["data"]["overall_status"] == "error"

    def test_system_monitoring_response_format(self, client, mocker):
        """システム監視APIレスポンス形式検証."""
        # Arrange (準備)
        mock_result = {
            "data": {
                "overall_status": "healthy",
                "database": "ok",
                "external_api": "ok",
            }
        }
        mocker.patch(
            "app.api.system_monitoring.health_check",
            return_value=(mock_result, 200),
        )

        # Act (実行)
        response = client.get("/api/system/health")

        # Assert (検証)
        assert "application/json" in response.content_type


class TestSystemMonitoringAPIEdgeCases:
    """システム監視APIエッジケーステスト."""

    def test_database_connection_timeout(self, client, mocker):
        """GET /api/system/database/connection - タイムアウトテスト."""
        # Arrange (準備)
        mock_session = mocker.MagicMock()
        mock_session.execute.side_effect = TimeoutError("Connection timeout")
        mock_session.__enter__.return_value = mock_session
        mock_session.__exit__.return_value = None
        mocker.patch(
            "app.api.system_monitoring.get_db_session",
            return_value=mock_session,
        )

        # Act (実行)
        response = client.get("/api/system/database/connection")

        # Assert (検証)
        assert response.status_code in [500, 503, 504]

    def test_external_api_connection_timeout(self, client, mocker):
        """GET /api/system/external-api/connection - タイムアウトテスト."""
        # Arrange (準備)
        mocker.patch(
            "app.services.stock_data.fetcher.StockDataFetcher.fetch_stock_data",
            side_effect=TimeoutError("API timeout"),
        )

        # Act (実行)
        response = client.get("/api/system/external-api/connection")

        # Assert (検証)
        assert response.status_code in [500, 503, 504]

    def test_health_check_partial_failure(self, client, mocker):
        """GET /api/system/health - 部分的な障害."""
        # Arrange (準備)
        mock_session = mocker.MagicMock()
        mock_session.execute.side_effect = Exception(
            "Database connection failed"
        )
        mock_session.__enter__.return_value = mock_session
        mock_session.__exit__.return_value = None
        mocker.patch(
            "app.api.system_monitoring.get_db_session",
            return_value=mock_session,
        )
        mocker.patch(
            "app.services.stock_data.fetcher.StockDataFetcher.fetch_stock_data",
            return_value={"7203.T": {"price": 100.0}},
        )

        # Act (実行)
        response = client.get("/api/system/health")

        # Assert (検証)
        assert response.status_code in [200, 207]
        data = response.get_json()
        assert data["data"]["overall_status"] in ["degraded", "error"]


class TestCombinedAPIIntegration:
    """複合API統合テスト."""

    def test_combined_api_calls(self, client, mocker):
        """複数のAPIを連続して呼び出すテスト."""
        # Arrange (準備)
        mock_health = {"data": {"overall_status": "healthy", "database": "ok"}}
        mocker.patch(
            "app.api.system_monitoring.health_check",
            return_value=(mock_health, 200),
        )
        mock_stocks = {"data": []}
        mocker.patch(
            "app.api.stock_master.get_stock_master_list",
            return_value=(mock_stocks, 200),
        )

        # Act (実行)
        health_response = client.get("/api/system/health")
        stocks_response = client.get(
            "/api/stock-master/", headers={"X-API-KEY": "test-key"}
        )

        # Assert (検証)
        assert health_response.status_code == 200
        assert stocks_response.status_code == 200

    def test_api_response_consistency(self, client, mocker):
        """全APIのレスポンス形式の一貫性テスト."""
        # Arrange (準備)
        mock_health = {"data": {"overall_status": "healthy", "database": "ok"}}
        mocker.patch(
            "app.api.system_monitoring.health_check",
            return_value=(mock_health, 200),
        )
        mock_db = {"status": "success", "message": "Connected"}
        mocker.patch(
            "app.api.system_monitoring.test_database_connection",
            return_value=(mock_db, 200),
        )
        mock_api = {"status": "success", "message": "Connected"}
        mocker.patch(
            "app.api.system_monitoring.test_api_connection",
            return_value=(mock_api, 200),
        )
        endpoints = [
            "/api/system/health",
            "/api/system/database/connection",
            "/api/system/external-api/connection",
        ]

        # Act & Assert (実行と検証)
        for endpoint in endpoints:
            response = client.get(endpoint)
            assert "application/json" in response.content_type
            data = response.get_json()
            assert isinstance(data, dict)
