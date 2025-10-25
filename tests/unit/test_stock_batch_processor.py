"""StockBatchProcessorのテスト."""

from unittest.mock import MagicMock, patch

import pandas as pd
import pytest

from services.stock_batch_processor import (
    StockBatchProcessingError,
    StockBatchProcessor,
)


class TestStockBatchProcessor:
    """StockBatchProcessorのテスト."""

    @pytest.fixture
    def processor(self):
        """プロセッサーインスタンス."""
        return StockBatchProcessor()

    @pytest.fixture
    def sample_dataframe(self):
        """サンプルDataFrame."""
        return pd.DataFrame(
            {
                "Open": [100.0, 103.0],
                "High": [105.0, 108.0],
                "Low": [99.0, 102.0],
                "Close": [103.0, 106.0],
                "Volume": [1000000, 1100000],
            },
            index=pd.date_range("2024-01-01", periods=2),
        )

    @patch("services.stock_data_fetcher.StockDataFetcher.fetch_stock_data")
    def test_fetch_multiple_timeframes_success(
        self, mock_fetch, processor, sample_dataframe
    ):
        """複数時間軸データ取得成功のテスト."""
        mock_fetch.return_value = sample_dataframe

        result = processor.fetch_multiple_timeframes("7203.T", ["1d", "1wk"])

        assert len(result) == 2
        assert "1d" in result
        assert "1wk" in result
        assert result["1d"]["success"] is True
        assert result["1wk"]["success"] is True
        assert mock_fetch.call_count == 2

    @patch("services.stock_data_fetcher.StockDataFetcher.fetch_stock_data")
    def test_fetch_multiple_timeframes_partial_failure(
        self, mock_fetch, processor, sample_dataframe
    ):
        """複数時間軸データ取得部分失敗のテスト."""
        # 最初の呼び出しは成功、2回目は失敗
        mock_fetch.side_effect = [sample_dataframe, Exception("API Error")]

        result = processor.fetch_multiple_timeframes("7203.T", ["1d", "1wk"])

        assert len(result) == 2
        assert "1d" in result
        assert "1wk" in result
        assert result["1d"]["success"] is True
        assert result["1wk"]["success"] is False

    @patch("yfinance.download")
    def test_fetch_batch_stock_data_success(self, mock_download, processor):
        """複数銘柄一括取得成功のテスト."""
        # MultiIndex DataFrameを作成
        symbols = ["AAPL", "GOOGL"]
        dates = pd.date_range("2024-01-01", periods=2)

        multi_df = pd.DataFrame(
            {
                ("AAPL", "Open"): [150.0, 152.0],
                ("AAPL", "Close"): [155.0, 157.0],
                ("GOOGL", "Open"): [2800.0, 2820.0],
                ("GOOGL", "Close"): [2850.0, 2870.0],
            },
            index=dates,
        )

        mock_download.return_value = multi_df

        result = processor.fetch_batch_stock_data(symbols, "1d")

        assert len(result) == 2
        assert "AAPL" in result
        assert "GOOGL" in result

    def test_fetch_batch_stock_data_invalid_symbols(self, processor):
        """無効な銘柄コードでの一括取得テスト."""
        invalid_symbols = ["", "INVALID", None]

        result = processor.fetch_batch_stock_data(invalid_symbols, "1d")

        # 無効な銘柄はエラー情報を含む辞書が返される
        assert isinstance(result, dict)
        for symbol in ["", "INVALID"]:  # Noneは除外される
            if symbol in result:
                assert result[symbol]["success"] is False
                assert "error" in result[symbol]

    @patch("yfinance.Tickers")
    def test_download_batch_from_yahoo_success(
        self, mock_tickers, processor, sample_dataframe
    ):
        """Yahoo Financeからの一括ダウンロード成功テスト."""
        mock_tickers_instance = MagicMock()
        mock_tickers_instance.history.return_value = sample_dataframe
        mock_tickers.return_value = mock_tickers_instance

        result = processor._download_batch_from_yahoo(["7203.T", "AAPL"], "1d")

        assert result is not None
        mock_tickers.assert_called_once_with("7203.T AAPL")
        mock_tickers_instance.history.assert_called_once()

    @patch("yfinance.Tickers")
    def test_download_batch_from_yahoo_failure(self, mock_tickers, processor):
        """Yahoo Financeからの一括ダウンロード失敗テスト."""
        mock_tickers.side_effect = Exception("API Error")

        with pytest.raises(Exception, match="API Error"):
            processor._download_batch_from_yahoo(["7203.T", "AAPL"], "1d")

    def test_fetch_multiple_timeframes_invalid_symbol(self, processor):
        """無効な銘柄コードでの複数時間軸取得テスト."""
        result = processor.fetch_multiple_timeframes("", ["1d", "1wk"])

        # 無効な銘柄の場合、各時間軸でエラー情報が返される
        assert len(result) == 2
        assert "1d" in result
        assert "1wk" in result
        assert result["1d"]["success"] is False
        assert result["1wk"]["success"] is False

    def test_fetch_multiple_timeframes_invalid_intervals(self, processor):
        """無効な時間軸での複数時間軸取得テスト."""
        # 全ての時間軸で失敗した場合は例外が発生する
        with pytest.raises(StockBatchProcessingError):
            processor.fetch_multiple_timeframes(
                "7203.T", ["invalid", "also_invalid"]
            )

    @patch("services.stock_data_fetcher.StockDataFetcher.fetch_stock_data")
    def test_fetch_multiple_timeframes_empty_data(self, mock_fetch, processor):
        """空データでの複数時間軸取得テスト."""
        mock_fetch.return_value = pd.DataFrame()

        result = processor.fetch_multiple_timeframes("7203.T", ["1d"])

        # 空データの場合、成功として扱われるが、データは空
        assert len(result) == 1
        assert "1d" in result
        assert result["1d"]["success"] is True
        assert result["1d"]["record_count"] == 0
