"""株価データサービスのテスト."""

from datetime import date, datetime
from unittest.mock import MagicMock, Mock, patch

import pandas as pd
import pytest

from app.models import Stocks1d, Stocks1h, Stocks1m
from app.services.stock_data.converter import StockDataConverter
from app.services.stock_data.fetcher import (
    StockDataFetcher,
    StockDataFetchError,
)
from app.services.stock_data.orchestrator import StockDataOrchestrator
from app.services.stock_data.saver import StockDataSaveError, StockDataSaver
from app.utils.timeframe_utils import (
    get_all_intervals,
    get_model_for_interval,
    validate_interval,
)


pytestmark = pytest.mark.unit


@pytest.fixture
def mock_yfinance_data():
    """モックyfinanceデータ (モジュールスコープ)."""
    data = {
        "Open": [100.0, 101.0, 102.0],
        "High": [105.0, 106.0, 107.0],
        "Low": [99.0, 100.0, 101.0],
        "Close": [103.0, 104.0, 105.0],
        "Volume": [1000000, 1100000, 1200000],
    }
    index = pd.date_range("2024-01-01", periods=3, freq="D")
    return pd.DataFrame(data, index=index)


class TestTimeframeUtils:
    """時間軸ユーティリティのテスト."""

    def test_validate_interval_valid_with_valid_interval_returns_true(self):
        """有効な時間軸の検証."""
        # Arrange (準備)
        # 有効な時間軸を準備

        # Act (実行)
        # 検証関数を実行

        # Assert (検証)
        assert validate_interval("1d") is True
        assert validate_interval("1h") is True
        assert validate_interval("1m") is True

    def test_validate_interval_invalid_with_invalid_interval_returns_false(
        self,
    ):
        """無効な時間軸の検証."""
        # Arrange (準備)
        # 無効な時間軸を準備

        # Act (実行)
        # 検証関数を実行

        # Assert (検証)
        assert validate_interval("invalid") is False
        assert validate_interval("") is False

    def test_get_model_for_interval_with_valid_interval_returns_model(self):
        """時間軸に対応するモデルの取得."""
        # Arrange (準備)
        from app.models import Stocks1d, Stocks1h, Stocks1m

        # Act (実行)
        # モデル取得関数を実行
        # Assert (検証)
        assert get_model_for_interval("1d") == Stocks1d
        assert get_model_for_interval("1h") == Stocks1h
        assert get_model_for_interval("1m") == Stocks1m

    def test_get_model_for_interval_invalid_with_invalid_interval_raises_error(
        self,
    ):
        """無効な時間軸でエラー."""
        # Arrange (準備)
        # 無効な時間軸を準備

        # Act & Assert (実行と検証)
        with pytest.raises(ValueError):
            get_model_for_interval("invalid")

    def test_get_all_intervals_with_valid_config_returns_all_intervals(self):
        """全時間軸の取得."""
        # Arrange (準備)
        # 時間軸設定を準備

        # Act (実行)
        intervals = get_all_intervals()

        # Assert (検証)
        assert "1m" in intervals
        assert "1d" in intervals
        assert "1wk" in intervals
        assert len(intervals) == 8


class TestStockDataFetcher:
    """StockDataFetcherのテスト."""

    @pytest.fixture
    def fetcher(self):
        """フェッチャーインスタンス."""
        return StockDataFetcher()

    @patch("app.services.stock_data.fetcher.yf.Ticker")
    def test_fetch_stock_data_success_with_valid_symbol_returns_data(
        self, mock_ticker, fetcher, mock_yfinance_data
    ):
        """データ取得成功."""
        # Arrange (準備)
        mock_ticker.return_value.history.return_value = mock_yfinance_data

        # Act (実行)
        df = fetcher.fetch_stock_data("7203.T", "1d", period="3d")

        # Assert (検証)
        assert len(df) == 3
        assert not df.empty
        mock_ticker.return_value.history.assert_called_once()

    @patch("app.services.stock_data.fetcher.yf.Ticker")
    def test_fetch_stock_data_empty_with_invalid_symbol_raises_error(
        self, mock_ticker, fetcher
    ):
        """空データの場合エラー."""
        # Arrange (準備)
        mock_ticker.return_value.history.return_value = pd.DataFrame()

        # Act & Assert (実行と検証)
        with pytest.raises(StockDataFetchError):
            fetcher.fetch_stock_data("INVALID", "1d", period="1d")

    @patch("app.services.stock_data.fetcher.yf.Ticker")
    def test_fetch_stock_data_invalid_interval_with_invalid_interval_raises_error(
        self, mock_ticker, fetcher
    ):
        """無効な時間軸でエラー."""
        # Arrange (準備)
        # 無効な時間軸を準備

        # Act & Assert (実行と検証)
        with pytest.raises(StockDataFetchError):
            fetcher.fetch_stock_data("7203.T", "invalid")

    def test_convert_to_dict_daily_with_valid_dataframe_returns_dict(
        self, fetcher, mock_yfinance_data
    ):
        """DataFrameから辞書への変換（日足）."""
        # Arrange (準備)
        from app.services.stock_data.converter import StockDataConverter

        converter = StockDataConverter()

        # Act (実行)
        records = converter.convert_to_dict(mock_yfinance_data, "1d")

        # Assert (検証)
        assert len(records) == 3
        assert "date" in records[0]
        assert "open" in records[0]
        assert "close" in records[0]
        assert records[0]["open"] == 100.0

    def test_convert_to_dict_intraday_with_valid_dataframe_returns_dict(
        self, fetcher
    ):
        """DataFrameから辞書への変換（分足）."""
        # Arrange (準備)
        from app.services.stock_data.converter import StockDataConverter

        converter = StockDataConverter()
        data = {
            "Open": [100.0],
            "High": [105.0],
            "Low": [99.0],
            "Close": [103.0],
            "Volume": [1000000],
        }
        index = pd.date_range("2024-01-01 09:00", periods=1, freq="1min")
        df = pd.DataFrame(data, index=index)

        # Act (実行)
        records = converter.convert_to_dict(df, "1m")

        # Assert (検証)
        assert len(records) == 1
        assert "datetime" in records[0]
        assert isinstance(records[0]["datetime"], datetime)


class TestStockDataSaver:
    """StockDataSaverのテスト."""

    @pytest.fixture
    def saver(self):
        """セーバーインスタンス."""
        return StockDataSaver()

    @pytest.fixture
    def sample_data_list(self):
        """サンプルデータ."""
        return [
            {
                "date": date(2024, 1, 1),
                "open": 100.0,
                "high": 105.0,
                "low": 99.0,
                "close": 103.0,
                "volume": 1000000,
            },
            {
                "date": date(2024, 1, 2),
                "open": 103.0,
                "high": 108.0,
                "low": 102.0,
                "close": 106.0,
                "volume": 1100000,
            },
        ]

    def test_save_stock_data_invalid_interval_with_invalid_interval_raises_error(
        self, saver, sample_data_list
    ):
        """無効な時間軸でエラー."""
        # Arrange (準備)
        # saverとsample_data_listフィクスチャを使用

        # Act & Assert (実行と検証)
        with pytest.raises(ValueError):
            saver.save_stock_data("7203.T", "invalid", sample_data_list)

    @patch("app.services.stock_data.saver.get_db_session")
    def test_stock_data_service_save_data_with_valid_data_returns_success(
        self, mock_session, saver, sample_data_list
    ):
        """データ保存成功."""
        # Arrange (準備)
        mock_sess = MagicMock()
        mock_session.return_value.__enter__.return_value = mock_sess

        # Act (実行)
        result = saver.save_stock_data("7203.T", "1d", sample_data_list)

        # Assert (検証)
        assert result["symbol"] == "7203.T"
        assert result["interval"] == "1d"
        assert result["total"] == 2

    @patch("app.services.stock_data.saver.get_db_session")
    def test_stock_data_service_validation_with_invalid_data_raises_validation_error(
        self, mock_session, saver, sample_data_list
    ):
        """データ保存成功."""
        # Arrange (準備)
        mock_sess = MagicMock()
        mock_session.return_value.__enter__.return_value = mock_sess

        # Act (実行)
        result = saver.save_stock_data("7203.T", "1d", sample_data_list)

        # Assert (検証)
        assert result["symbol"] == "7203.T"
        assert result["interval"] == "1d"
        assert result["total"] == 2


class TestStockDataOrchestrator:
    """StockDataOrchestratorのテスト."""

    @pytest.fixture
    def orchestrator(self):
        """オーケストレーターインスタンス."""
        return StockDataOrchestrator()

    @patch.object(StockDataFetcher, "fetch_stock_data")
    @patch.object(StockDataConverter, "convert_to_dict")
    @patch.object(StockDataSaver, "save_stock_data")
    @patch.object(StockDataOrchestrator, "check_data_integrity")
    def test_fetch_and_save_success_with_valid_data_returns_success(
        self, mock_integrity, mock_save, mock_convert, mock_fetch, orchestrator
    ):
        """取得・保存の統合処理成功."""
        # Arrange (準備)
        mock_fetch.return_value = pd.DataFrame(
            {
                "Open": [100.0],
                "High": [105.0],
                "Low": [99.0],
                "Close": [103.0],
                "Volume": [1000000],
            },
            index=pd.date_range("2024-01-01", periods=1),
        )
        mock_convert.return_value = [
            {
                "date": date(2024, 1, 1),
                "open": 100.0,
                "high": 105.0,
                "low": 99.0,
                "close": 103.0,
                "volume": 1000000,
            }
        ]
        mock_save.return_value = {
            "symbol": "7203.T",
            "interval": "1d",
            "total": 1,
            "saved": 1,
            "skipped": 0,
            "errors": 0,
        }
        mock_integrity.return_value = {"valid": True, "record_count": 1}

        # Act (実行)
        result = orchestrator.fetch_and_save("7203.T", "1d", period="1d")

        # Assert (検証)
        assert result["success"] is True
        assert result["symbol"] == "7203.T"
        assert result["interval"] == "1d"
        assert "save_result" in result
        assert "integrity_check" in result

    def test_check_data_integrity_with_valid_data_returns_integrity_result(
        self, orchestrator
    ):
        """整合性チェック."""
        # Arrange (準備)
        # orchestratorフィクスチャを使用

        # Act (実行)
        with patch.object(
            orchestrator.saver, "count_records", return_value=10
        ), patch.object(
            orchestrator.saver,
            "get_latest_date",
            return_value=date(2024, 1, 1),
        ):
            result = orchestrator.check_data_integrity("7203.T", "1d")

        # Assert (検証)
        assert result["valid"] is True
        assert result["record_count"] == 10
        assert result["latest_date"] is not None

    def test_stock_data_service_initialization_with_valid_config_returns_service_instance(
        self,
    ):
        """有効な時間軸の検証."""
        # Arrange (準備)
        # 有効な時間軸を準備

        # Act (実行)
        # 検証関数を実行

        # Assert (検証)
        assert validate_interval("1d") is True
        assert validate_interval("1h") is True
        assert validate_interval("1m") is True

    def test_stock_data_service_fetch_data_with_valid_symbol_returns_stock_data(
        self, mock_yfinance_data
    ):
        """DataFrameから辞書への変換（日足）."""
        # Arrange (準備)
        from app.services.stock_data.converter import StockDataConverter

        converter = StockDataConverter()

        # Act (実行)
        records = converter.convert_to_dict(mock_yfinance_data, "1d")

        # Assert (検証)
        assert len(records) == 3
        assert "date" in records[0]
        assert "open" in records[0]
        assert "close" in records[0]
        assert records[0]["open"] == 100.0

    def test_stock_data_service_fetch_data_with_invalid_symbol_raises_error(
        self,
    ):
        """DataFrameから辞書への変換（分足）."""
        # Arrange (準備)
        from app.services.stock_data.converter import StockDataConverter

        converter = StockDataConverter()
        data = {
            "Open": [100.0],
            "High": [105.0],
            "Low": [99.0],
            "Close": [103.0],
            "Volume": [1000000],
        }
        index = pd.date_range("2024-01-01 09:00", periods=1, freq="1min")
        df = pd.DataFrame(data, index=index)

        # Act (実行)
        records = converter.convert_to_dict(df, "1m")

        # Assert (検証)
        assert len(records) == 1
        assert "datetime" in records[0]
        assert isinstance(records[0]["datetime"], datetime)
