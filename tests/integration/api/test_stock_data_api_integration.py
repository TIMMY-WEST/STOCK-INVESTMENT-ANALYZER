"""株価データAPI統合テスト.

このモジュールは、株価データAPIの統合テストを提供します。
StockDataFetcherクラスの基本的な機能をテストします。
"""

from unittest.mock import Mock, patch

import pandas as pd
import pytest
import yfinance as yf

from app.exceptions import StockDataFetchError
from app.services.stock_data.fetcher import StockDataFetcher


pytestmark = pytest.mark.integration


class TestStockDataAPIIntegration:
    """株価データAPI統合テストクラス."""

    @pytest.fixture
    def api_service(self):
        """APIサービスのフィクスチャ."""
        return StockDataFetcher()

    def test_fetch_stock_data_with_valid_symbol_returns_success_response(
        self, api_service
    ):
        """有効な銘柄コードでの株価データ取得成功テスト."""
        # Arrange (準備)
        with patch.object(yf, "Ticker") as mock_ticker_class:
            mock_ticker = Mock()
            mock_ticker_class.return_value = mock_ticker
            mock_data = pd.DataFrame(
                {
                    "Open": [100.0],
                    "High": [110.0],
                    "Low": [95.0],
                    "Close": [105.0],
                    "Volume": [1000000],
                }
            )
            mock_ticker.history.return_value = mock_data

            # Act (実行)
            result = api_service.fetch_stock_data("7203")

            # Assert (検証)
            assert result is not None
            assert isinstance(result, pd.DataFrame)
            assert len(result) > 0
            mock_ticker_class.assert_called_once_with("7203.T")

    def test_fetch_stock_data_with_invalid_symbol_raises_exception(
        self, api_service
    ):
        """無効な銘柄コードでの例外発生テスト."""
        # Arrange (準備)
        with patch.object(yf, "Ticker") as mock_ticker_class:
            mock_ticker = Mock()
            mock_ticker_class.return_value = mock_ticker
            mock_data = pd.DataFrame()
            mock_ticker.history.return_value = mock_data

            # Act & Assert (実行と検証)
            with pytest.raises(StockDataFetchError):
                api_service.fetch_stock_data("INVALID")

    def test_fetch_stock_data_with_network_error_raises_exception(
        self, api_service
    ):
        """ネットワークエラー時の例外発生テスト."""
        # Arrange (準備)
        with patch.object(yf, "Ticker") as mock_ticker_class:
            mock_ticker_class.side_effect = Exception("Network error")

            # Act & Assert (実行と検証)
            with pytest.raises(StockDataFetchError):
                api_service.fetch_stock_data("7203")
