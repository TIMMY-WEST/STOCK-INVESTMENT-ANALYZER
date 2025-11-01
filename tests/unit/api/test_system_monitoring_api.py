"""システム監視APIのテスト."""

import os
import sys


sys.path.insert(
    0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "app"))
)

from unittest.mock import MagicMock, patch  # noqa: E402

import pytest  # noqa: E402

import app as flask_app  # noqa: E402


# module-level marker so pytest -m unit picks these up
pytestmark = pytest.mark.unit


@pytest.fixture
def client():
    """テスト用のFlaskクライアントを作成."""
    flask_app.app.config["TESTING"] = True
    with flask_app.app.test_client() as client:
        yield client


class TestDatabaseConnectionTest:
    """データベース接続テストのテストクラス."""

    @patch("app.api.system_monitoring.get_db_session")
    def test_system_monitoring_db_connection_with_valid_session_returns_success(
        self, mock_get_session, client
    ):
        """正常系: データベース接続テスト成功."""
        # Arrange (準備)
        mock_session = MagicMock()
        mock_result1 = MagicMock()
        mock_result2 = MagicMock()
        mock_result2.scalar.return_value = "test_db"
        mock_result3 = MagicMock()
        mock_result3.scalar.return_value = 3
        mock_result4 = MagicMock()
        mock_result4.scalar.return_value = True
        mock_session.execute.side_effect = [
            mock_result1,
            mock_result2,
            mock_result3,
            mock_result4,
        ]
        mock_get_session.return_value.__enter__.return_value = mock_session
        mock_get_session.return_value.__exit__.return_value = False

        # Act (実行)
        response = client.get("/api/system/database/connection")

        # Assert (検証)
        assert response.status_code == 200
        data = response.get_json()
        assert data["status"] == "success"
        assert "response_time_ms" in data["meta"]
        assert data["message"] == "データベース接続正常"
        assert "data" in data
        assert "timestamp" in data["meta"]

    @patch("app.api.system_monitoring.get_db_session")
    def test_system_monitoring_db_connection_with_error_returns_internal_error(
        self, mock_get_session, client
    ):
        """異常系: データベース接続テスト失敗."""
        # Arrange (準備)
        mock_get_session.side_effect = Exception("接続エラー")

        # Act (実行)
        response = client.get("/api/system/database/connection")

        # Assert (検証)
        assert response.status_code == 500
        data = response.get_json()
        assert data["status"] == "error"
        assert "error" in data
        assert "接続エラー" in data["error"]["message"]


class TestAPIConnectionTest:
    """Yahoo Finance API接続テストのテストクラス."""

    @patch("app.api.system_monitoring.StockDataFetcher")
    def test_system_monitoring_api_connection_with_valid_symbol_returns_success(
        self, mock_fetcher_class, client
    ):
        """正常系: Yahoo Finance API接続テスト成功."""
        # Arrange (準備)
        mock_fetcher = MagicMock()
        mock_fetcher.fetch_stock_data.return_value = [
            {"date": "2024-01-15", "close": 2500}
        ]
        mock_fetcher_class.return_value = mock_fetcher

        # Act (実行)
        response = client.get(
            "/api/system/external-api/connection?symbol=7203.T"
        )

        # Assert (検証)
        assert response.status_code == 200
        data = response.get_json()
        assert data["status"] == "success"
        assert data["message"] == "Yahoo Finance API接続正常"
        assert data["data"]["symbol"] == "7203.T"
        assert data["data"]["data_points"] > 0
        assert data["data"]["data_available"] is True

    @patch("app.api.system_monitoring.StockDataFetcher")
    def test_system_monitoring_api_connection_with_invalid_symbol_returns_not_found(
        self, mock_fetcher_class, client
    ):
        """異常系: データ取得失敗."""
        # Arrange (準備)
        mock_fetcher = MagicMock()
        mock_fetcher.fetch_stock_data.return_value = []
        mock_fetcher_class.return_value = mock_fetcher

        # Act (実行)
        response = client.get(
            "/api/system/external-api/connection?symbol=INVALID.T"
        )

        # Assert (検証)
        assert response.status_code == 404
        data = response.get_json()
        assert data["status"] == "error"
        assert "error" in data
        assert "銘柄データを取得できませんでした" in data["error"]["message"]

    @patch("app.api.system_monitoring.StockDataFetcher")
    def test_system_monitoring_api_connection_with_error_returns_internal_error(
        self, mock_fetcher_class, client
    ):
        """異常系: API接続エラー."""
        # Arrange (準備)
        mock_fetcher_class.side_effect = Exception("API接続エラー")

        # Act (実行)
        response = client.get("/api/system/external-api/connection")

        # Assert (検証)
        assert response.status_code == 500
        data = response.get_json()
        assert data["status"] == "error"
        assert "error" in data
        assert "API接続エラー" in data["error"]["message"]


class TestHealthCheck:
    """統合ヘルスチェックのテストクラス."""

    @patch("app.api.system_monitoring.StockDataFetcher")
    @patch("app.api.system_monitoring.get_db_session")
    def test_system_monitoring_health_check_with_all_services_healthy_returns_success(
        self, mock_get_session, mock_fetcher_class, client
    ):
        """正常系: 全てのサービスが正常."""
        # Arrange (準備)
        mock_session = MagicMock()
        mock_get_session.return_value.__enter__.return_value = mock_session
        mock_get_session.return_value.__exit__.return_value = False
        mock_fetcher = MagicMock()
        mock_fetcher.fetch_stock_data.return_value = [{"date": "2024-01-15"}]
        mock_fetcher_class.return_value = mock_fetcher

        # Act (実行)
        response = client.get("/api/system/health")

        # Assert (検証)
        assert response.status_code == 200
        data = response.get_json()
        assert data["data"]["overall_status"] == "healthy"
        assert data["data"]["services"]["database"]["status"] == "healthy"
        assert (
            data["data"]["services"]["yahoo_finance_api"]["status"]
            == "healthy"
        )

    @patch("app.api.system_monitoring.StockDataFetcher")
    @patch("app.api.system_monitoring.get_db_session")
    def test_system_monitoring_health_check_with_db_error_returns_partial_failure(
        self, mock_get_session, mock_fetcher_class, client
    ):
        """異常系: データベースエラー."""
        # Arrange (準備)
        mock_get_session.side_effect = Exception("DB接続エラー")
        mock_fetcher = MagicMock()
        mock_fetcher.fetch_stock_data.return_value = [{"date": "2024-01-15"}]
        mock_fetcher_class.return_value = mock_fetcher

        # Act (実行)
        response = client.get("/api/system/health")

        # Assert (検証)
        assert response.status_code == 200
        data = response.get_json()
        assert data["data"]["overall_status"] == "error"
        assert data["data"]["services"]["database"]["status"] == "error"

    @patch("app.api.system_monitoring.StockDataFetcher")
    @patch("app.api.system_monitoring.get_db_session")
    def test_system_monitoring_health_check_with_api_warning_returns_degraded_status(
        self, mock_get_session, mock_fetcher_class, client
    ):
        """正常系: APIから警告（データなし）."""
        # Arrange (準備)
        mock_session = MagicMock()
        mock_get_session.return_value.__enter__.return_value = mock_session
        mock_get_session.return_value.__exit__.return_value = False
        mock_fetcher = MagicMock()
        mock_fetcher.fetch_stock_data.return_value = []
        mock_fetcher_class.return_value = mock_fetcher

        # Act (実行)
        response = client.get("/api/system/health")

        # Assert (検証)
        assert response.status_code == 200
        data = response.get_json()
        assert data["data"]["overall_status"] == "degraded"
        assert (
            data["data"]["services"]["yahoo_finance_api"]["status"]
            == "warning"
        )
