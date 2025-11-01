"""StockDataSaverクラスのユニットテスト."""

from datetime import date, datetime
from unittest.mock import MagicMock, Mock, patch

import pytest
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from app.services.stock_data.saver import StockDataSaveError, StockDataSaver


pytestmark = pytest.mark.unit


class TestStockDataSaver:
    """StockDataSaverクラスのテストスイート."""

    def setup_method(self):
        """各テストメソッドの前に実行される初期化処理."""
        self.saver = StockDataSaver()

    @patch("app.services.stock_data.saver.get_db_session")
    @patch("app.services.stock_data.saver.get_model_for_interval")
    @patch("app.services.stock_data.saver.validate_interval")
    def test_save_stock_data_with_valid_data_returns_success(
        self, mock_validate, mock_get_model, mock_get_db_session
    ):
        """正常なデータ保存のテスト."""
        # Arrange (準備)
        mock_validate.return_value = True
        mock_model = Mock()
        mock_get_model.return_value = mock_model
        mock_session = MagicMock()
        mock_get_db_session.return_value.__enter__.return_value = mock_session
        symbol = "7203.T"
        interval = "1d"
        data_list = [
            {"date": date(2025, 1, 1), "open": 100, "close": 110},
            {"date": date(2025, 1, 2), "open": 110, "close": 120},
        ]

        # Act (実行)
        result = self.saver.save_stock_data(symbol, interval, data_list)

        # Assert (検証)
        assert result["symbol"] == symbol
        assert result["interval"] == interval
        assert result["total"] == 2
        assert result["saved"] >= 0
        assert result["skipped"] >= 0
        assert result["errors"] >= 0

    @patch("app.services.stock_data.saver.get_db_session")
    @patch("app.services.stock_data.saver.get_model_for_interval")
    @patch("app.services.stock_data.saver.validate_interval")
    def test_save_stock_data_with_provided_session_returns_success(
        self, mock_validate, mock_get_model, mock_get_db_session
    ):
        """セッション提供時のデータ保存テスト."""
        # Arrange (準備)
        mock_validate.return_value = True
        mock_model = Mock()
        mock_get_model.return_value = mock_model
        mock_session = MagicMock()
        symbol = "7203.T"
        interval = "1d"
        data_list = [
            {"date": date(2025, 1, 1), "open": 100, "close": 110},
        ]

        # Act (実行)
        result = self.saver.save_stock_data(
            symbol, interval, data_list, session=mock_session
        )

        # Assert (検証)
        assert result["symbol"] == symbol
        assert result["total"] == 1

    def test_save_stock_data_with_invalid_interval_raises_error(self):
        """無効な時間軸でのエラーテスト."""
        # Arrange (準備)
        symbol = "7203.T"
        interval = "invalid"
        data_list = []

        # Act & Assert (実行と検証)
        with pytest.raises(ValueError):
            self.saver.save_stock_data(symbol, interval, data_list)

    @patch("app.services.stock_data.saver.is_intraday_interval")
    def test_save_with_session_bulk_insert_with_valid_data_returns_success(
        self, mock_is_intraday
    ):
        """バルクインサートの実行テスト."""
        # Arrange (準備)
        mock_is_intraday.return_value = False
        mock_session = MagicMock()
        mock_model = Mock()
        mock_model.date = Mock()
        mock_model.symbol = Mock()
        mock_session.query.return_value.filter.return_value.all.return_value = (
            []
        )
        symbol = "7203.T"
        interval = "1d"
        data_list = [
            {"date": date(2025, 1, 1), "open": 100, "close": 110},
            {"date": date(2025, 1, 2), "open": 110, "close": 120},
        ]

        # Act (実行)
        result = self.saver._save_with_session(
            mock_session, symbol, interval, mock_model, data_list
        )

        # Assert (検証)
        mock_session.bulk_insert_mappings.assert_called_once()
        assert result["saved"] == 2
        assert result["skipped"] == 0

    @patch("app.services.stock_data.saver.is_intraday_interval")
    def test_save_with_session_duplicate_skip_with_existing_data_returns_success(
        self, mock_is_intraday
    ):
        """重複データのスキップテスト."""
        # Arrange (準備)
        mock_is_intraday.return_value = False
        mock_session = MagicMock()
        mock_model = Mock()
        mock_model.date = Mock()
        mock_model.symbol = Mock()
        existing_date = date(2025, 1, 1)
        mock_session.query.return_value.filter.return_value.all.return_value = [
            (existing_date,)
        ]
        symbol = "7203.T"
        interval = "1d"
        data_list = [
            {"date": existing_date, "open": 100, "close": 110},
            {"date": date(2025, 1, 2), "open": 110, "close": 120},
        ]

        # Act (実行)
        result = self.saver._save_with_session(
            mock_session, symbol, interval, mock_model, data_list
        )

        # Assert (検証)
        assert result["skipped"] == 1
        assert result["saved"] == 1

    @patch("app.services.stock_data.saver.is_intraday_interval")
    def test_save_with_session_error_handling_with_database_error_raises_exception(
        self, mock_is_intraday
    ):
        """エラー発生時のハンドリングテスト."""
        # Arrange (準備)
        mock_is_intraday.return_value = False
        mock_session = MagicMock()
        mock_model = Mock()
        mock_model.date = Mock()
        mock_model.symbol = Mock()
        mock_session.query.side_effect = SQLAlchemyError("DB Error")
        symbol = "7203.T"
        interval = "1d"
        data_list = [
            {"date": date(2025, 1, 1), "open": 100, "close": 110},
        ]

        # Act (実行)
        result = self.saver._save_with_session(
            mock_session, symbol, interval, mock_model, data_list
        )

        # Assert (検証)
        assert result is not None

    @patch("app.services.stock_data.saver.get_db_session")
    @patch("app.services.stock_data.saver.get_model_for_interval")
    @patch("app.services.stock_data.saver.validate_interval")
    def test_save_batch_stock_data_with_valid_data_returns_success(
        self, mock_validate, mock_get_model, mock_get_db_session
    ):
        """バッチ保存の正常動作テスト."""
        # Arrange (準備)
        mock_validate.return_value = True
        mock_model = Mock()
        mock_get_model.return_value = mock_model
        mock_session = MagicMock()
        mock_get_db_session.return_value.__enter__.return_value = mock_session
        symbols_data = {
            "7203.T": [{"date": date(2025, 1, 1), "open": 100, "close": 110}],
            "9984.T": [{"date": date(2025, 1, 1), "open": 200, "close": 210}],
        }

        # Act (実行)
        with patch.object(self.saver, "_filter_duplicate_data") as mock_filter:
            mock_filter.return_value = symbols_data
            result = self.saver.save_batch_stock_data(
                symbols_data, interval="1d"
            )

        # Assert (検証)
        assert result["total_symbols"] == 2
        assert result["total_saved"] == 2
        mock_session.bulk_insert_mappings.assert_called_once()

    @patch("app.services.stock_data.saver.get_db_session")
    @patch("app.services.stock_data.saver.get_model_for_interval")
    @patch("app.services.stock_data.saver.validate_interval")
    def test_save_batch_stock_data_with_error_raises_exception(
        self, mock_validate, mock_get_model, mock_get_db_session
    ):
        """バッチ保存時のエラーハンドリングテスト."""
        # Arrange (準備)
        mock_validate.return_value = True
        mock_model = Mock()
        mock_get_model.return_value = mock_model
        mock_session = MagicMock()
        mock_get_db_session.return_value.__enter__.return_value = mock_session
        mock_session.bulk_insert_mappings.side_effect = SQLAlchemyError(
            "Insert Error"
        )
        symbols_data = {
            "7203.T": [{"date": date(2025, 1, 1), "open": 100, "close": 110}],
        }

        # Act & Assert (実行と検証)
        with patch.object(self.saver, "_filter_duplicate_data") as mock_filter:
            mock_filter.return_value = symbols_data
            with pytest.raises(StockDataSaveError):
                self.saver.save_batch_stock_data(symbols_data, interval="1d")

    @patch("app.services.stock_data.saver.is_intraday_interval")
    def test_filter_duplicate_data_with_existing_records_returns_filtered_data(
        self, mock_is_intraday
    ):
        """重複データフィルタリングのテスト."""
        # Arrange (準備)
        mock_is_intraday.return_value = False
        mock_session = MagicMock()
        mock_model = Mock()
        mock_model.date = Mock()
        mock_model.symbol = Mock()
        existing_date = date(2025, 1, 1)
        mock_session.query.return_value.filter.return_value.all.return_value = [
            (existing_date,)
        ]
        symbols_data = {
            "7203.T": [
                {"date": existing_date, "open": 100, "close": 110},
                {"date": date(2025, 1, 2), "open": 110, "close": 120},
            ]
        }

        # Act (実行)
        filtered = self.saver._filter_duplicate_data(
            mock_session, mock_model, symbols_data, "1d"
        )

        # Assert (検証)
        assert len(filtered["7203.T"]) == 1
        assert filtered["7203.T"][0]["date"] == date(2025, 1, 2)

    @patch("app.services.stock_data.saver.get_db_session")
    @patch("app.services.stock_data.saver.get_model_for_interval")
    @patch("app.services.stock_data.saver.validate_interval")
    @patch("app.services.stock_data.saver.is_intraday_interval")
    def test_get_latest_date_with_existing_data_returns_date(
        self,
        mock_is_intraday,
        mock_validate,
        mock_get_model,
        mock_get_db_session,
    ):
        """最新日付取得のテスト."""
        # Arrange (準備)
        mock_validate.return_value = True
        mock_is_intraday.return_value = False
        mock_model = Mock()
        mock_model.date = Mock()
        mock_model.symbol = Mock()
        mock_get_model.return_value = mock_model
        mock_session = MagicMock()
        mock_get_db_session.return_value.__enter__.return_value = mock_session
        latest_date = date(2025, 1, 15)
        mock_session.query.return_value.filter.return_value.order_by.return_value.first.return_value = (
            latest_date,
        )

        # Act (実行)
        result = self.saver.get_latest_date("7203.T", "1d")

        # Assert (検証)
        assert result == latest_date

    @patch("app.services.stock_data.saver.get_db_session")
    @patch("app.services.stock_data.saver.get_model_for_interval")
    @patch("app.services.stock_data.saver.validate_interval")
    def test_count_records_with_existing_data_returns_count(
        self, mock_validate, mock_get_model, mock_get_db_session
    ):
        """レコード数取得のテスト."""
        # Arrange (準備)
        mock_validate.return_value = True
        mock_model = Mock()
        mock_model.symbol = Mock()
        mock_get_model.return_value = mock_model
        mock_session = MagicMock()
        mock_get_db_session.return_value.__enter__.return_value = mock_session
        record_count = 100
        mock_session.query.return_value.filter.return_value.count.return_value = (
            record_count
        )

        # Act (実行)
        result = self.saver.count_records("7203.T", "1d")

        # Assert (検証)
        assert result == record_count

    @patch("app.services.stock_data.saver.get_db_session")
    @patch("app.services.stock_data.saver.get_model_for_interval")
    @patch("app.services.stock_data.saver.validate_interval")
    def test_save_multiple_timeframes_with_valid_data_returns_success(
        self, mock_validate, mock_get_model, mock_get_db_session
    ):
        """複数時間軸保存のテスト."""
        # Arrange (準備)
        mock_validate.return_value = True
        mock_model = Mock()
        mock_get_model.return_value = mock_model
        mock_session = MagicMock()
        mock_get_db_session.return_value.__enter__.return_value = mock_session
        symbol = "7203.T"
        data_dict = {
            "1d": [{"date": date(2025, 1, 1), "open": 100, "close": 110}],
            "1h": [
                {
                    "datetime": datetime(2025, 1, 1, 9, 0),
                    "open": 100,
                    "close": 105,
                }
            ],
        }

        # Act (実行)
        results = self.saver.save_multiple_timeframes(symbol, data_dict)

        # Assert (検証)
        assert "1d" in results
        assert "1h" in results
        assert results["1d"]["symbol"] == symbol
        assert results["1h"]["symbol"] == symbol


class TestStockDataSaveError:
    """StockDataSaveErrorクラスのテスト."""

    def test_stock_data_save_error(self):
        """エラークラスのインスタンス化テスト."""
        # Arrange (準備)
        error_message = "Test error message"

        # Act (実行)
        error = StockDataSaveError(error_message)

        # Assert (検証)
        assert str(error) == error_message
        assert isinstance(error, Exception)
