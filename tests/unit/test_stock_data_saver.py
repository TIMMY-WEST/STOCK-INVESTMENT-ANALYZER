"""StockDataSaverクラスのユニットテスト."""

from datetime import date, datetime
from unittest.mock import MagicMock, Mock, patch

import pytest
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from services.stock_data.saver import StockDataSaveError, StockDataSaver


class TestStockDataSaver:
    """StockDataSaverクラスのテストスイート."""

    def setup_method(self):
        """各テストメソッドの前に実行される初期化処理."""
        self.saver = StockDataSaver()

    @patch("services.stock_data.saver.get_db_session")
    @patch("services.stock_data.saver.get_model_for_interval")
    @patch("services.stock_data.saver.validate_interval")
    def test_save_stock_data_success(
        self, mock_validate, mock_get_model, mock_get_db_session
    ):
        """正常なデータ保存のテスト."""
        # モックの設定
        mock_validate.return_value = True
        mock_model = Mock()
        mock_get_model.return_value = mock_model

        mock_session = MagicMock()
        mock_get_db_session.return_value.__enter__.return_value = mock_session

        # テストデータ
        symbol = "7203.T"
        interval = "1d"
        data_list = [
            {"date": date(2025, 1, 1), "open": 100, "close": 110},
            {"date": date(2025, 1, 2), "open": 110, "close": 120},
        ]

        # 実行
        result = self.saver.save_stock_data(symbol, interval, data_list)

        # 検証
        assert result["symbol"] == symbol
        assert result["interval"] == interval
        assert result["total"] == 2
        assert result["saved"] >= 0
        assert result["skipped"] >= 0
        assert result["errors"] >= 0

    @patch("services.stock_data.saver.get_db_session")
    @patch("services.stock_data.saver.get_model_for_interval")
    @patch("services.stock_data.saver.validate_interval")
    def test_save_stock_data_with_session(
        self, mock_validate, mock_get_model, mock_get_db_session
    ):
        """セッション提供時のデータ保存テスト."""
        # モックの設定
        mock_validate.return_value = True
        mock_model = Mock()
        mock_get_model.return_value = mock_model

        mock_session = MagicMock()

        # テストデータ
        symbol = "7203.T"
        interval = "1d"
        data_list = [
            {"date": date(2025, 1, 1), "open": 100, "close": 110},
        ]

        # 実行
        result = self.saver.save_stock_data(
            symbol, interval, data_list, session=mock_session
        )

        # 検証
        assert result["symbol"] == symbol
        assert result["total"] == 1

    def test_save_stock_data_invalid_interval(self):
        """無効な時間軸でのエラーテスト."""
        symbol = "7203.T"
        interval = "invalid"
        data_list = []

        with pytest.raises(ValueError):
            self.saver.save_stock_data(symbol, interval, data_list)

    @patch("services.stock_data.saver.is_intraday_interval")
    def test_save_with_session_bulk_insert(self, mock_is_intraday):
        """バルクインサートの実行テスト."""
        # モックの設定
        mock_is_intraday.return_value = False
        mock_session = MagicMock()
        mock_model = Mock()
        mock_model.date = Mock()
        mock_model.symbol = Mock()

        # 既存データなし
        mock_session.query.return_value.filter.return_value.all.return_value = (
            []
        )

        # テストデータ
        symbol = "7203.T"
        interval = "1d"
        data_list = [
            {"date": date(2025, 1, 1), "open": 100, "close": 110},
            {"date": date(2025, 1, 2), "open": 110, "close": 120},
        ]

        # 実行
        result = self.saver._save_with_session(
            mock_session, symbol, interval, mock_model, data_list
        )

        # 検証: bulk_insert_mappingsが呼ばれたか
        mock_session.bulk_insert_mappings.assert_called_once()
        assert result["saved"] == 2
        assert result["skipped"] == 0

    @patch("services.stock_data.saver.is_intraday_interval")
    def test_save_with_session_duplicate_skip(self, mock_is_intraday):
        """重複データのスキップテスト."""
        # モックの設定
        mock_is_intraday.return_value = False
        mock_session = MagicMock()
        mock_model = Mock()
        mock_model.date = Mock()
        mock_model.symbol = Mock()

        # 既存データあり
        existing_date = date(2025, 1, 1)
        mock_session.query.return_value.filter.return_value.all.return_value = [
            (existing_date,)
        ]

        # テストデータ(重複を含む)
        symbol = "7203.T"
        interval = "1d"
        data_list = [
            {"date": existing_date, "open": 100, "close": 110},
            {"date": date(2025, 1, 2), "open": 110, "close": 120},
        ]

        # 実行
        result = self.saver._save_with_session(
            mock_session, symbol, interval, mock_model, data_list
        )

        # 検証: 重複がスキップされたか
        assert result["skipped"] == 1
        assert result["saved"] == 1

    @patch("services.stock_data.saver.is_intraday_interval")
    def test_save_with_session_error_handling(self, mock_is_intraday):
        """エラー発生時のハンドリングテスト."""
        # モックの設定
        mock_is_intraday.return_value = False
        mock_session = MagicMock()
        mock_model = Mock()
        mock_model.date = Mock()
        mock_model.symbol = Mock()

        # 既存データ取得時のエラー
        mock_session.query.side_effect = SQLAlchemyError("DB Error")

        # テストデータ
        symbol = "7203.T"
        interval = "1d"
        data_list = [
            {"date": date(2025, 1, 1), "open": 100, "close": 110},
        ]

        # 実行と検証: エラーが発生してもデータ保存は試みられる
        # (既存データ取得エラーは警告のみ)
        result = self.saver._save_with_session(
            mock_session, symbol, interval, mock_model, data_list
        )
        assert result is not None

    @patch("services.stock_data.saver.get_db_session")
    @patch("services.stock_data.saver.get_model_for_interval")
    @patch("services.stock_data.saver.validate_interval")
    def test_save_batch_stock_data_success(
        self, mock_validate, mock_get_model, mock_get_db_session
    ):
        """バッチ保存の正常動作テスト."""
        # モックの設定
        mock_validate.return_value = True
        mock_model = Mock()
        mock_get_model.return_value = mock_model

        mock_session = MagicMock()
        mock_get_db_session.return_value.__enter__.return_value = mock_session

        # 重複フィルタのモック
        with patch.object(self.saver, "_filter_duplicate_data") as mock_filter:
            symbols_data = {
                "7203.T": [
                    {"date": date(2025, 1, 1), "open": 100, "close": 110}
                ],
                "9984.T": [
                    {"date": date(2025, 1, 1), "open": 200, "close": 210}
                ],
            }
            mock_filter.return_value = symbols_data

            # 実行
            result = self.saver.save_batch_stock_data(
                symbols_data, interval="1d"
            )

            # 検証
            assert result["total_symbols"] == 2
            assert result["total_saved"] == 2
            mock_session.bulk_insert_mappings.assert_called_once()

    @patch("services.stock_data.saver.get_db_session")
    @patch("services.stock_data.saver.get_model_for_interval")
    @patch("services.stock_data.saver.validate_interval")
    def test_save_batch_stock_data_error(
        self, mock_validate, mock_get_model, mock_get_db_session
    ):
        """バッチ保存時のエラーハンドリングテスト."""
        # モックの設定
        mock_validate.return_value = True
        mock_model = Mock()
        mock_get_model.return_value = mock_model

        mock_session = MagicMock()
        mock_get_db_session.return_value.__enter__.return_value = mock_session

        # bulk_insert_mappingsでエラー発生
        mock_session.bulk_insert_mappings.side_effect = SQLAlchemyError(
            "Insert Error"
        )

        with patch.object(self.saver, "_filter_duplicate_data") as mock_filter:
            symbols_data = {
                "7203.T": [
                    {"date": date(2025, 1, 1), "open": 100, "close": 110}
                ],
            }
            mock_filter.return_value = symbols_data

            # 実行と検証: エラーが発生
            with pytest.raises(StockDataSaveError):
                self.saver.save_batch_stock_data(symbols_data, interval="1d")

    @patch("services.stock_data.saver.is_intraday_interval")
    def test_filter_duplicate_data(self, mock_is_intraday):
        """重複データフィルタリングのテスト."""
        # モックの設定
        mock_is_intraday.return_value = False
        mock_session = MagicMock()
        mock_model = Mock()
        mock_model.date = Mock()
        mock_model.symbol = Mock()

        # 既存データあり
        existing_date = date(2025, 1, 1)
        mock_session.query.return_value.filter.return_value.all.return_value = [
            (existing_date,)
        ]

        # テストデータ
        symbols_data = {
            "7203.T": [
                {"date": existing_date, "open": 100, "close": 110},
                {"date": date(2025, 1, 2), "open": 110, "close": 120},
            ]
        }

        # 実行
        filtered = self.saver._filter_duplicate_data(
            mock_session, mock_model, symbols_data, "1d"
        )

        # 検証: 重複が除外された
        assert len(filtered["7203.T"]) == 1
        assert filtered["7203.T"][0]["date"] == date(2025, 1, 2)

    @patch("services.stock_data.saver.get_db_session")
    @patch("services.stock_data.saver.get_model_for_interval")
    @patch("services.stock_data.saver.validate_interval")
    @patch("services.stock_data.saver.is_intraday_interval")
    def test_get_latest_date(
        self,
        mock_is_intraday,
        mock_validate,
        mock_get_model,
        mock_get_db_session,
    ):
        """最新日付取得のテスト."""
        # モックの設定
        mock_validate.return_value = True
        mock_is_intraday.return_value = False
        mock_model = Mock()
        mock_model.date = Mock()
        mock_model.symbol = Mock()
        mock_get_model.return_value = mock_model

        mock_session = MagicMock()
        mock_get_db_session.return_value.__enter__.return_value = mock_session

        # 最新日付を返す
        latest_date = date(2025, 1, 15)
        mock_session.query.return_value.filter.return_value.order_by.return_value.first.return_value = (
            latest_date,
        )

        # 実行
        result = self.saver.get_latest_date("7203.T", "1d")

        # 検証
        assert result == latest_date

    @patch("services.stock_data.saver.get_db_session")
    @patch("services.stock_data.saver.get_model_for_interval")
    @patch("services.stock_data.saver.validate_interval")
    def test_count_records(
        self, mock_validate, mock_get_model, mock_get_db_session
    ):
        """レコード数取得のテスト."""
        # モックの設定
        mock_validate.return_value = True
        mock_model = Mock()
        mock_model.symbol = Mock()
        mock_get_model.return_value = mock_model

        mock_session = MagicMock()
        mock_get_db_session.return_value.__enter__.return_value = mock_session

        # レコード数を返す
        record_count = 100
        mock_session.query.return_value.filter.return_value.count.return_value = (
            record_count
        )

        # 実行
        result = self.saver.count_records("7203.T", "1d")

        # 検証
        assert result == record_count

    @patch("services.stock_data.saver.get_db_session")
    @patch("services.stock_data.saver.get_model_for_interval")
    @patch("services.stock_data.saver.validate_interval")
    def test_save_multiple_timeframes(
        self, mock_validate, mock_get_model, mock_get_db_session
    ):
        """複数時間軸保存のテスト."""
        # モックの設定
        mock_validate.return_value = True
        mock_model = Mock()
        mock_get_model.return_value = mock_model

        mock_session = MagicMock()
        mock_get_db_session.return_value.__enter__.return_value = mock_session

        # テストデータ
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

        # 実行
        results = self.saver.save_multiple_timeframes(symbol, data_dict)

        # 検証
        assert "1d" in results
        assert "1h" in results
        assert results["1d"]["symbol"] == symbol
        assert results["1h"]["symbol"] == symbol


class TestStockDataSaveError:
    """StockDataSaveErrorクラスのテスト."""

    def test_stock_data_save_error(self):
        """エラークラスのインスタンス化テスト."""
        error_message = "Test error message"
        error = StockDataSaveError(error_message)

        assert str(error) == error_message
        assert isinstance(error, Exception)
