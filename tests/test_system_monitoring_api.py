"""システム監視APIのテスト.
"""

import os
import sys


sys.path.insert(
    0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "app"))
)

from unittest.mock import MagicMock, patch

import pytest

import app as flask_app


@pytest.fixture
def client():
    """テスト用のFlaskクライアントを作成."""
    flask_app.app.config["TESTING"] = True
    with flask_app.app.test_client() as client:
        yield client


class TestDatabaseConnectionTest:
    """データベース接続テストのテストクラス."""

    @patch("models.get_db_session")
    def test_db_connection_success(self, mock_get_session, client):
        """正常系: データベース接続テスト成功."""
        # モックセッションの設定
        mock_session = MagicMock()

        # execute()を複数回呼び出すため、side_effectを適切に設定
        mock_result1 = MagicMock()  # SELECT 1の結果
        mock_result2 = MagicMock()  # current_database()の結果
        mock_result2.scalar.return_value = "test_db"
        mock_result3 = MagicMock()  # 接続数の結果
        mock_result3.scalar.return_value = 3
        mock_result4 = MagicMock()  # テーブル存在確認の結果
        mock_result4.scalar.return_value = True

        mock_session.execute.side_effect = [
            mock_result1,
            mock_result2,
            mock_result3,
            mock_result4,
        ]

        # コンテキストマネージャーとしてモックセッションを返す
        mock_get_session.return_value.__enter__.return_value = mock_session
        mock_get_session.return_value.__exit__.return_value = False

        # APIリクエスト
        response = client.post("/api/system/db-connection-test")

        # アサーション
        assert response.status_code == 200
        data = response.get_json()
        assert data["success"] is True
        assert "responseTime" in data
        assert data["message"] == "データベース接続正常"
        assert "details" in data
        assert "timestamp" in data

    @patch("models.get_db_session")
    def test_db_connection_failure(self, mock_get_session, client):
        """異常系: データベース接続テスト失敗."""
        # エラーをスローするモックを設定
        mock_get_session.side_effect = Exception("接続エラー")

        # APIリクエスト
        response = client.post("/api/system/db-connection-test")

        # アサーション
        assert response.status_code == 500
        data = response.get_json()
        assert data["success"] is False
        assert "接続エラー" in data["message"]


class TestAPIConnectionTest:
    """Yahoo Finance API接続テストのテストクラス."""

    @patch("services.stock_data_fetcher.StockDataFetcher")
    def test_api_connection_success(self, mock_fetcher_class, client):
        """正常系: Yahoo Finance API接続テスト成功."""
        # モックの設定
        mock_fetcher = MagicMock()
        mock_fetcher.fetch_stock_data.return_value = [
            {"date": "2024-01-15", "close": 2500}
        ]
        mock_fetcher_class.return_value = mock_fetcher

        # APIリクエスト
        response = client.post(
            "/api/system/api-connection-test", json={"symbol": "7203.T"}
        )

        # アサーション
        assert response.status_code == 200
        data = response.get_json()
        assert data["success"] is True
        assert data["message"] == "Yahoo Finance API接続正常"
        assert data["details"]["symbol"] == "7203.T"
        assert data["details"]["dataPoints"] > 0
        assert data["details"]["dataAvailable"] is True

    @patch("services.stock_data_fetcher.StockDataFetcher")
    def test_api_connection_no_data(self, mock_fetcher_class, client):
        """異常系: データ取得失敗."""
        # モックの設定（データなし）
        mock_fetcher = MagicMock()
        mock_fetcher.fetch_stock_data.return_value = []
        mock_fetcher_class.return_value = mock_fetcher

        # APIリクエスト
        response = client.post(
            "/api/system/api-connection-test", json={"symbol": "INVALID.T"}
        )

        # アサーション
        assert response.status_code == 404
        data = response.get_json()
        assert data["success"] is False
        assert "銘柄データを取得できませんでした" in data["message"]

    @patch("services.stock_data_fetcher.StockDataFetcher")
    def test_api_connection_failure(self, mock_fetcher_class, client):
        """異常系: API接続エラー."""
        # エラーをスローするモックを設定
        mock_fetcher_class.side_effect = Exception("API接続エラー")

        # APIリクエスト
        response = client.post("/api/system/api-connection-test")

        # アサーション
        assert response.status_code == 500
        data = response.get_json()
        assert data["success"] is False
        assert "API接続エラー" in data["message"]


class TestHealthCheck:
    """統合ヘルスチェックのテストクラス."""

    @patch("services.stock_data_fetcher.StockDataFetcher")
    @patch("models.get_db_session")
    def test_health_check_all_healthy(
        self, mock_get_session, mock_fetcher_class, client
    ):
        """正常系: 全てのサービスが正常."""
        # データベースモック（コンテキストマネージャー対応）
        mock_session = MagicMock()
        mock_get_session.return_value.__enter__.return_value = mock_session
        mock_get_session.return_value.__exit__.return_value = False

        # APIモック
        mock_fetcher = MagicMock()
        mock_fetcher.fetch_stock_data.return_value = [{"date": "2024-01-15"}]
        mock_fetcher_class.return_value = mock_fetcher

        # APIリクエスト
        response = client.get("/api/system/health-check")

        # アサーション
        assert response.status_code == 200
        data = response.get_json()
        assert data["status"] == "healthy"
        assert data["services"]["database"]["status"] == "healthy"
        assert data["services"]["yahoo_finance_api"]["status"] == "healthy"

    @patch("services.stock_data_fetcher.StockDataFetcher")
    @patch("models.get_db_session")
    def test_health_check_db_error(
        self, mock_get_session, mock_fetcher_class, client
    ):
        """異常系: データベースエラー."""
        # データベースエラー
        mock_get_session.side_effect = Exception("DB接続エラー")

        # APIモック
        mock_fetcher = MagicMock()
        mock_fetcher.fetch_stock_data.return_value = [{"date": "2024-01-15"}]
        mock_fetcher_class.return_value = mock_fetcher

        # APIリクエスト
        response = client.get("/api/system/health-check")

        # アサーション
        assert response.status_code == 200
        data = response.get_json()
        assert data["status"] == "error"
        assert data["services"]["database"]["status"] == "error"

    @patch("services.stock_data_fetcher.StockDataFetcher")
    @patch("models.get_db_session")
    def test_health_check_api_warning(
        self, mock_get_session, mock_fetcher_class, client
    ):
        """正常系: APIから警告（データなし）."""
        # データベースモック（コンテキストマネージャー対応）
        mock_session = MagicMock()
        mock_get_session.return_value.__enter__.return_value = mock_session
        mock_get_session.return_value.__exit__.return_value = False

        # APIモック（データなし）
        mock_fetcher = MagicMock()
        mock_fetcher.fetch_stock_data.return_value = []
        mock_fetcher_class.return_value = mock_fetcher

        # APIリクエスト
        response = client.get("/api/system/health-check")

        # アサーション
        assert response.status_code == 200
        data = response.get_json()
        assert data["status"] == "degraded"
        assert data["services"]["yahoo_finance_api"]["status"] == "warning"
