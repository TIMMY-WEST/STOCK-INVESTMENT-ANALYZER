"""株価データAPI統合テスト.

このモジュールは株価データ関連APIエンドポイントの統合テストを提供します。
- レスポンス形式の検証
- エラーケースのテスト
- ページネーション・フィルタリングのテスト
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


class TestStockDataAPIIntegration:
    """株価データAPI統合テスト."""

    def test_fetch_stock_data_success_response(self, client, mocker):
        """POST /api/stocks/data - 成功時のレスポンス検証."""
        # yfinanceのモック
        from datetime import datetime

        import pandas as pd

        mock_df = pd.DataFrame(
            {
                "Open": [1000.0],
                "High": [1050.0],
                "Low": [990.0],
                "Close": [1020.0],
                "Volume": [1000000],
            },
            index=pd.DatetimeIndex([datetime(2025, 1, 1)]),
        )

        mock_ticker = mocker.Mock()
        mock_ticker.history.return_value = mock_df
        mocker.patch("yfinance.Ticker", return_value=mock_ticker)

        response = client.post(
            "/api/stocks/data",
            json={"symbol": "7203.T", "period": "1mo"},
            content_type="application/json",
        )

        assert response.status_code == 200
        data = response.get_json()

        # レスポンス形式の検証
        assert data["status"] == "success"
        assert "message" in data
        assert "data" in data

        # データ内容の検証
        assert isinstance(data["data"], dict)

    def test_fetch_stock_data_validation_error(self, client, mocker):
        """POST /api/stocks/data - バリデーションエラーのテスト."""
        # yfinance が空のデータフレームを返すケース
        import pandas as pd

        mock_df = pd.DataFrame()  # 空のDataFrame
        mock_ticker = mocker.Mock()
        mock_ticker.history.return_value = mock_df
        mocker.patch("yfinance.Ticker", return_value=mock_ticker)

        response = client.post(
            "/api/stocks/data",
            json={"symbol": "INVALID", "period": "1mo"},
            content_type="application/json",
        )

        # 空データはエラーとして扱われる
        data = response.get_json()
        assert data["status"] == "error"
        assert "message" in data

    def test_fetch_stock_data_invalid_symbol(self, client, mocker):
        """POST /api/stocks/data - 無効な銘柄コードのテスト."""
        # yfinanceがエラーを返す場合のモック
        mock_ticker = mocker.Mock()
        mock_ticker.history.side_effect = Exception("Invalid symbol")
        mocker.patch("yfinance.Ticker", return_value=mock_ticker)

        response = client.post(
            "/api/stocks/data",
            json={"symbol": "INVALID", "period": "1mo"},
            content_type="application/json",
        )

        # エラーレスポンスの検証
        data = response.get_json()
        assert data["status"] == "error"
        assert "message" in data

    def test_fetch_stock_data_external_api_error(self, client, mocker):
        """POST /api/stocks/data - 外部APIエラーのテスト."""
        # yfinanceがタイムアウトする場合のモック
        mocker.patch("yfinance.Ticker", side_effect=ConnectionError("Timeout"))

        response = client.post(
            "/api/stocks/data",
            json={"symbol": "7203.T", "period": "1mo"},
            content_type="application/json",
        )

        assert response.status_code in [500, 502, 503]
        data = response.get_json()
        assert data["status"] == "error"

    def test_get_stocks_list_success(self, client, mocker):
        """GET /api/stocks - 株価データ一覧取得成功."""
        # DBセッションのモック
        mock_session = mocker.Mock()
        mock_query = mocker.Mock()

        # サンプルデータ
        mock_stocks = [
            mocker.Mock(
                id=1,
                symbol="7203.T",
                date="2025-01-01",
                open=1000.0,
                high=1050.0,
                low=990.0,
                close=1020.0,
                volume=1000000,
            ),
            mocker.Mock(
                id=2,
                symbol="6758.T",
                date="2025-01-01",
                open=12000.0,
                high=12500.0,
                low=11900.0,
                close=12200.0,
                volume=500000,
            ),
        ]

        mock_query.offset.return_value = mock_query
        mock_query.limit.return_value = mock_query
        mock_query.all.return_value = mock_stocks
        mock_query.count.return_value = len(mock_stocks)

        mock_session.query.return_value = mock_query
        mock_session.__enter__ = mocker.Mock(return_value=mock_session)
        mock_session.__exit__ = mocker.Mock(return_value=False)

        mocker.patch("app.models.get_db_session", return_value=mock_session)

        response = client.get("/api/stocks")

        assert response.status_code == 200
        data = response.get_json()

        # レスポンス形式の検証
        assert data["status"] == "success"
        assert "data" in data
        assert isinstance(data["data"], list)

    def test_get_stocks_pagination(self, client, mocker):
        """GET /api/stocks - ページネーションのテスト."""
        mock_session = mocker.Mock()
        mock_query = mocker.Mock()

        # ページネーション用のモックデータ
        mock_stocks = []
        mock_query.offset.return_value = mock_query
        mock_query.limit.return_value = mock_query
        mock_query.all.return_value = mock_stocks
        mock_query.count.return_value = 0

        mock_session.query.return_value = mock_query
        mock_session.__enter__ = mocker.Mock(return_value=mock_session)
        mock_session.__exit__ = mocker.Mock(return_value=False)

        mocker.patch("app.models.get_db_session", return_value=mock_session)

        # limitとoffsetパラメータのテスト
        response = client.get("/api/stocks?limit=10&offset=0")

        assert response.status_code == 200
        data = response.get_json()

        assert data["status"] == "success"
        assert "data" in data

    def test_get_stocks_interval_filter(self, client, mocker):
        """GET /api/stocks - 時間間隔フィルタリングのテスト."""
        mock_session = mocker.Mock()
        mock_query = mocker.Mock()

        mock_stocks = []
        mock_query.offset.return_value = mock_query
        mock_query.limit.return_value = mock_query
        mock_query.all.return_value = mock_stocks
        mock_query.count.return_value = 0

        mock_session.query.return_value = mock_query
        mock_session.__enter__ = mocker.Mock(return_value=mock_session)
        mock_session.__exit__ = mocker.Mock(return_value=False)

        mocker.patch("app.models.get_db_session", return_value=mock_session)

        # intervalパラメータのテスト
        for interval in ["1m", "1h", "1d", "1wk", "1mo"]:
            response = client.get(f"/api/stocks?interval={interval}")

            assert response.status_code == 200
            data = response.get_json()
            assert data["status"] == "success"

    def test_get_stocks_invalid_interval(self, client):
        """GET /api/stocks - 無効な時間間隔のテスト."""
        response = client.get("/api/stocks?interval=invalid")

        # 無効なintervalはエラーまたは無視される
        data = response.get_json()
        assert "status" in data

    def test_get_stock_by_id_success(self, client, mocker):
        """GET /api/stocks/{stock_id} - 株価データ詳細取得成功."""
        # StockDailyCRUD.get_by_idをモック
        mock_stock = mocker.Mock()
        mock_stock.to_dict.return_value = {
            "id": 1,
            "symbol": "7203.T",
            "date": "2025-01-01",
            "open": 1000.0,
            "high": 1050.0,
            "low": 990.0,
            "close": 1020.0,
            "volume": 1000000,
        }

        mocker.patch(
            "app.models.StockDailyCRUD.get_by_id", return_value=mock_stock
        )

        response = client.get("/api/stocks/1")

        assert response.status_code == 200
        data = response.get_json()

        assert data["success"] is True
        assert "data" in data

    def test_get_stock_by_id_not_found(self, client, mocker):
        """GET /api/stocks/{stock_id} - 存在しない株価データのテスト."""
        # 存在しないIDの場合はNoneを返す
        mocker.patch("app.models.StockDailyCRUD.get_by_id", return_value=None)

        response = client.get("/api/stocks/9999")

        assert response.status_code == 404
        data = response.get_json()

        assert data["success"] is False
        assert "error" in data
        assert "message" in data

    def test_update_stock_success(self, client, mocker):
        """PUT /api/stocks/{stock_id} - 株価データ更新成功."""
        # StockDailyCRUD.updateをモック
        mock_stock = mocker.Mock()
        mock_stock.id = 1
        mock_stock.symbol = "7203.T"
        mock_stock.to_dict.return_value = {
            "id": 1,
            "symbol": "7203.T",
            "open": 1100.0,
            "high": 1150.0,
            "low": 1090.0,
            "close": 1120.0,
        }

        mocker.patch(
            "app.models.StockDailyCRUD.update", return_value=mock_stock
        )

        update_data = {
            "open": 1100.0,
            "high": 1150.0,
            "low": 1090.0,
            "close": 1120.0,
        }

        response = client.put(
            "/api/stocks/1", json=update_data, content_type="application/json"
        )

        assert response.status_code == 200
        data = response.get_json()

        assert data["success"] is True
        assert "message" in data

    def test_delete_stock_success(self, client, mocker):
        """DELETE /api/stocks/{stock_id} - 株価データ削除成功."""
        # StockDailyCRUD.deleteをモック(Trueを返す)
        mocker.patch("app.models.StockDailyCRUD.delete", return_value=True)

        response = client.delete("/api/stocks/1")

        assert response.status_code == 200
        data = response.get_json()

        assert data["success"] is True
        assert "message" in data

    def test_create_test_stock_success(self, client, mocker):
        """POST /api/stocks/test - テスト用株価データ作成成功."""
        # StockDailyCRUD.bulk_createをモック（実際のエンドポイントが使用するメソッド）
        mock_stocks = []
        for i in range(3):
            mock_stock = mocker.Mock()
            mock_stock.to_dict.return_value = {
                "id": i + 1,
                "symbol": "7203.T",
                "date": f"2024-09-0{i + 7}",
                "open": 2500.0,
                "high": 2550.0,
                "low": 2480.0,
                "close": 2530.0,
                "volume": 1500000,
            }
            mock_stocks.append(mock_stock)

        # データベースセッションをモック
        mock_session = mocker.Mock()
        mocker.patch("app.app.get_db_session", return_value=mock_session)
        mock_session.__enter__ = mocker.Mock(return_value=mock_session)
        mock_session.__exit__ = mocker.Mock(return_value=None)

        mocker.patch(
            "app.app.StockDailyCRUD.bulk_create", return_value=mock_stocks
        )

        response = client.post(
            "/api/stocks/test",
            content_type="application/json",
        )

        assert response.status_code in [200, 201]
        data = response.get_json()
        assert data["success"] is True
        assert "message" in data
        assert "data" in data
        assert len(data["data"]) == 3


class TestStockDataAPIResponseFormat:
    """レスポンス形式の検証テスト."""

    def test_success_response_structure(self, client, mocker):
        """成功時のレスポンス構造検証."""
        mock_session = mocker.Mock()
        mock_query = mocker.Mock()
        mock_query.offset.return_value = mock_query
        mock_query.limit.return_value = mock_query
        mock_query.all.return_value = []
        mock_query.count.return_value = 0

        mock_session.query.return_value = mock_query
        mock_session.__enter__ = mocker.Mock(return_value=mock_session)
        mock_session.__exit__ = mocker.Mock(return_value=False)

        mocker.patch("app.models.get_db_session", return_value=mock_session)

        response = client.get("/api/stocks")
        data = response.get_json()

        # 成功時の必須フィールド
        assert "status" in data
        assert data["status"] == "success"
        assert "data" in data

    def test_error_response_structure(self, client, mocker):
        """エラー時のレスポンス構造検証."""
        # 存在しないIDを取得してエラーをシミュレート
        mocker.patch("app.models.StockDailyCRUD.get_by_id", return_value=None)

        response = client.get("/api/stocks/9999")
        data = response.get_json()

        # エラー時の必須フィールド
        assert data["success"] is False
        assert "error" in data
        assert "message" in data

    def test_response_content_type(self, client, mocker):
        """レスポンスのContent-Typeがapplication/jsonであることを確認."""
        mock_session = mocker.Mock()
        mock_query = mocker.Mock()
        mock_query.offset.return_value = mock_query
        mock_query.limit.return_value = mock_query
        mock_query.all.return_value = []
        mock_query.count.return_value = 0

        mock_session.query.return_value = mock_query
        mock_session.__enter__ = mocker.Mock(return_value=mock_session)
        mock_session.__exit__ = mocker.Mock(return_value=False)

        mocker.patch("app.models.get_db_session", return_value=mock_session)

        response = client.get("/api/stocks")

        assert "application/json" in response.content_type


class TestStockDataAPIEdgeCases:
    """エッジケースのテスト."""

    def test_large_limit_pagination(self, client, mocker):
        """大きなlimit値のテスト."""
        mock_session = mocker.Mock()
        mock_query = mocker.Mock()
        mock_query.offset.return_value = mock_query
        mock_query.limit.return_value = mock_query
        mock_query.all.return_value = []
        mock_query.count.return_value = 0

        mock_session.query.return_value = mock_query
        mock_session.__enter__ = mocker.Mock(return_value=mock_session)
        mock_session.__exit__ = mocker.Mock(return_value=False)

        mocker.patch("app.models.get_db_session", return_value=mock_session)

        response = client.get("/api/stocks?limit=1000")

        assert response.status_code == 200

    def test_negative_offset_pagination(self, client, mocker):
        """負のoffset値のテスト."""
        mock_session = mocker.Mock()
        mock_query = mocker.Mock()
        mock_query.offset.return_value = mock_query
        mock_query.limit.return_value = mock_query
        mock_query.all.return_value = []
        mock_query.count.return_value = 0

        mock_session.query.return_value = mock_query
        mock_session.__enter__ = mocker.Mock(return_value=mock_session)
        mock_session.__exit__ = mocker.Mock(return_value=False)

        mocker.patch("app.models.get_db_session", return_value=mock_session)

        response = client.get("/api/stocks?offset=-1")

        # 負の値はエラーまたは0として扱われる
        assert response.status_code in [200, 400]
