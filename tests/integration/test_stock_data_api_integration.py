"""株価データAPI統合テスト.

このモジュールは、株価データAPIの統合テストを提供します。
外部APIとの連携、データ取得、エラーハンドリングなどを包括的にテストします。
"""

from datetime import date, datetime
from unittest.mock import Mock, patch

import pytest
import requests

from app.exceptions import (
    ExternalAPIError,
    NetworkError,
    RateLimitError,
    StockDataError,
)
from app.services.stock_data_api import StockDataAPIService


class TestStockDataAPIIntegration:
    """株価データAPI統合テストクラス."""

    @pytest.fixture
    def api_service(self):
        """APIサービスのフィクスチャ."""
        return StockDataAPIService()

    @pytest.fixture
    def mock_response_data(self):
        """モックレスポンスデータのフィクスチャ."""
        return {
            "symbol": "7203",
            "name": "トヨタ自動車",
            "price": 2500.0,
            "change": 50.0,
            "change_percent": 2.04,
            "volume": 1000000,
            "market_cap": 35000000000,
            "timestamp": "2024-01-15T15:00:00Z",
        }

    def test_fetch_stock_data_with_valid_symbol_returns_success_response(
        self, api_service, mock_response_data
    ):
        """有効な銘柄コードでの株価データ取得成功テスト."""
        with patch("requests.get") as mock_get:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = mock_response_data
            mock_response.raise_for_status.return_value = None
            mock_get.return_value = mock_response

            result = api_service.fetch_stock_data("7203")

            assert result is not None
            assert result["symbol"] == "7203"
            assert result["name"] == "トヨタ自動車"
            assert result["price"] == 2500.0
            mock_get.assert_called_once()

    def test_fetch_stock_data_with_invalid_symbol_returns_error_response(
        self, api_service
    ):
        """無効な銘柄コードでの株価データ取得エラーテスト."""
        with patch("requests.get") as mock_get:
            mock_response = Mock()
            mock_response.status_code = 404
            mock_response.raise_for_status.side_effect = (
                requests.exceptions.HTTPError("404 Not Found")
            )
            mock_get.return_value = mock_response

            with pytest.raises(StockDataError) as exc_info:
                api_service.fetch_stock_data("INVALID")

            assert "404" in str(exc_info.value)

    def test_fetch_stock_data_with_network_timeout_returns_timeout_error(
        self, api_service
    ):
        """ネットワークタイムアウトでの株価データ取得エラーテスト."""
        with patch("requests.get") as mock_get:
            mock_get.side_effect = requests.exceptions.Timeout(
                "Request timeout"
            )

            with pytest.raises(NetworkError) as exc_info:
                api_service.fetch_stock_data("7203")

            assert "timeout" in str(exc_info.value).lower()

    def test_fetch_stock_data_with_connection_error_returns_network_error(
        self, api_service
    ):
        """接続エラーでの株価データ取得エラーテスト."""
        with patch("requests.get") as mock_get:
            mock_get.side_effect = requests.exceptions.ConnectionError(
                "Connection failed"
            )

            with pytest.raises(NetworkError) as exc_info:
                api_service.fetch_stock_data("7203")

            assert "connection" in str(exc_info.value).lower()

    def test_fetch_stock_data_with_rate_limit_returns_rate_limit_error(
        self, api_service
    ):
        """レート制限での株価データ取得エラーテスト."""
        with patch("requests.get") as mock_get:
            mock_response = Mock()
            mock_response.status_code = 429
            mock_response.raise_for_status.side_effect = (
                requests.exceptions.HTTPError("429 Too Many Requests")
            )
            mock_response.headers = {"Retry-After": "60"}
            mock_get.return_value = mock_response

            with pytest.raises(RateLimitError) as exc_info:
                api_service.fetch_stock_data("7203")

            assert "rate limit" in str(exc_info.value).lower()

    def test_fetch_stock_data_with_server_error_returns_external_api_error(
        self, api_service
    ):
        """サーバーエラーでの株価データ取得エラーテスト."""
        with patch("requests.get") as mock_get:
            mock_response = Mock()
            mock_response.status_code = 500
            mock_response.raise_for_status.side_effect = (
                requests.exceptions.HTTPError("500 Internal Server Error")
            )
            mock_get.return_value = mock_response

            with pytest.raises(ExternalAPIError) as exc_info:
                api_service.fetch_stock_data("7203")

            assert "500" in str(exc_info.value)

    def test_fetch_multiple_stocks_with_valid_symbols_returns_success_responses(
        self, api_service, mock_response_data
    ):
        """複数銘柄の株価データ一括取得成功テスト."""
        symbols = ["7203", "6758", "9984"]

        with patch("requests.get") as mock_get:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.raise_for_status.return_value = None

            # 各銘柄に対して異なるレスポンスを設定
            responses = []
            for i, symbol in enumerate(symbols):
                data = mock_response_data.copy()
                data["symbol"] = symbol
                data["price"] = 2500.0 + (i * 100)
                responses.append(data)

            mock_response.json.side_effect = responses
            mock_get.return_value = mock_response

            results = api_service.fetch_multiple_stocks(symbols)

            assert len(results) == 3
            assert all(result["symbol"] in symbols for result in results)
            assert mock_get.call_count == 3

    def test_fetch_multiple_stocks_with_partial_failures_returns_mixed_results(
        self, api_service, mock_response_data
    ):
        """複数銘柄取得での部分的失敗テスト."""
        symbols = ["7203", "INVALID", "6758"]

        with patch("requests.get") as mock_get:

            def side_effect(url, **kwargs):
                if "INVALID" in url:
                    mock_response = Mock()
                    mock_response.status_code = 404
                    mock_response.raise_for_status.side_effect = (
                        requests.exceptions.HTTPError("404 Not Found")
                    )
                    return mock_response
                else:
                    mock_response = Mock()
                    mock_response.status_code = 200
                    mock_response.json.return_value = mock_response_data
                    mock_response.raise_for_status.return_value = None
                    return mock_response

            mock_get.side_effect = side_effect

            results = api_service.fetch_multiple_stocks(
                symbols, ignore_errors=True
            )

            # 成功した2件のみが返される
            assert len(results) == 2
            assert all(
                result["symbol"] in ["7203", "6758"] for result in results
            )

    def test_fetch_historical_data_with_date_range_returns_time_series_data(
        self, api_service
    ):
        """日付範囲指定での履歴データ取得テスト."""
        symbol = "7203"
        start_date = date(2024, 1, 1)
        end_date = date(2024, 1, 31)

        mock_historical_data = [
            {
                "date": "2024-01-01",
                "open": 2450.0,
                "high": 2500.0,
                "low": 2400.0,
                "close": 2480.0,
                "volume": 800000,
            },
            {
                "date": "2024-01-02",
                "open": 2480.0,
                "high": 2520.0,
                "low": 2460.0,
                "close": 2500.0,
                "volume": 900000,
            },
        ]

        with patch("requests.get") as mock_get:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {"data": mock_historical_data}
            mock_response.raise_for_status.return_value = None
            mock_get.return_value = mock_response

            result = api_service.fetch_historical_data(
                symbol, start_date, end_date
            )

            assert "data" in result
            assert len(result["data"]) == 2
            assert result["data"][0]["date"] == "2024-01-01"
            assert result["data"][1]["close"] == 2500.0

    def test_api_authentication_with_valid_token_returns_authenticated_request(
        self, api_service
    ):
        """有効なトークンでのAPI認証テスト."""
        api_service.set_api_token("valid_token_123")

        with patch("requests.get") as mock_get:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {"authenticated": True}
            mock_response.raise_for_status.return_value = None
            mock_get.return_value = mock_response

            result = api_service.fetch_stock_data("7203")

            assert result is not None
            assert result["symbol"] == "7203"
            assert result["name"] == "トヨタ自動車"
            assert result["price"] == 2500.0
            # 認証ヘッダーが含まれていることを確認
            call_args = mock_get.call_args
            headers = call_args[1].get("headers", {})
            assert "Authorization" in headers
            assert "valid_token_123" in headers["Authorization"]

    def test_api_retry_mechanism_with_temporary_failure_returns_success_after_retry(
        self, api_service, mock_response_data
    ):
        """一時的な失敗後のリトライ機能テスト."""
        with patch("requests.get") as mock_get:
            # 最初の2回は失敗、3回目は成功
            responses = [
                Mock(
                    status_code=503,
                    raise_for_status=Mock(
                        side_effect=requests.exceptions.HTTPError(
                            "503 Service Unavailable"
                        )
                    ),
                ),
                Mock(
                    status_code=503,
                    raise_for_status=Mock(
                        side_effect=requests.exceptions.HTTPError(
                            "503 Service Unavailable"
                        )
                    ),
                ),
                Mock(
                    status_code=200,
                    json=Mock(return_value=mock_response_data),
                    raise_for_status=Mock(return_value=None),
                ),
            ]
            mock_get.side_effect = responses

            result = api_service.fetch_stock_data_with_retry(
                "7203", max_retries=3
            )

            assert result is not None
            assert result["symbol"] == "7203"
            assert mock_get.call_count == 3

    def test_api_cache_mechanism_with_repeated_requests_returns_cached_data(
        self, api_service, mock_response_data
    ):
        """キャッシュ機能での重複リクエスト処理テスト."""
        with patch("requests.get") as mock_get:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = mock_response_data
            mock_response.raise_for_status.return_value = None
            mock_get.return_value = mock_response

            # 同じ銘柄を2回取得
            result1 = api_service.fetch_stock_data_cached("7203")
            result2 = api_service.fetch_stock_data_cached("7203")

            assert result1 == result2
            # キャッシュが効いているため、APIは1回のみ呼ばれる
            assert mock_get.call_count == 1

    def test_api_response_validation_with_invalid_data_returns_validation_error(
        self, api_service
    ):
        """無効なレスポンスデータでのバリデーションエラーテスト."""
        invalid_response_data = {
            "symbol": "7203",
            # 必須フィールドが不足
            "price": "invalid_price",  # 数値でない
        }

        with patch("requests.get") as mock_get:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = invalid_response_data
            mock_response.raise_for_status.return_value = None
            mock_get.return_value = mock_response

            with pytest.raises(StockDataError) as exc_info:
                api_service.fetch_stock_data_validated("7203")

            assert "validation" in str(exc_info.value).lower()

    def test_api_rate_limiting_with_burst_requests_returns_controlled_execution(
        self, api_service, mock_response_data
    ):
        """バーストリクエストでのレート制限テスト."""
        symbols = [f"symbol_{i}" for i in range(10)]

        with patch("requests.get") as mock_get:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = mock_response_data
            mock_response.raise_for_status.return_value = None
            mock_get.return_value = mock_response

            start_time = datetime.now()
            results = api_service.fetch_multiple_stocks_rate_limited(
                symbols, requests_per_second=5
            )
            end_time = datetime.now()

            # レート制限により実行時間が制御されていることを確認
            execution_time = (end_time - start_time).total_seconds()
            expected_min_time = (len(symbols) - 1) / 5  # 5 requests per second

            assert len(results) == len(symbols)
            assert execution_time >= expected_min_time
