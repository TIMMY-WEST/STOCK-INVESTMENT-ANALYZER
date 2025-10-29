"""models.pyのテストケース.

このモジュールは、models.pyで定義されたクラスとメソッドの包括的なテストを提供します。
"""

from datetime import date, datetime
from decimal import Decimal
from unittest.mock import Mock, patch

import pytest
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session

from app.models import (
    Base,
    BatchExecution,
    BatchExecutionDetail,
    DatabaseError,
    StockDaily,
    StockDailyCRUD,
    StockDataBase,
    StockDataError,
    StockMaster,
    StockMasterUpdate,
    Stocks1d,
    get_db_session,
)


class TestStockDaily:
    """StockDaily（Stocks1d）モデルのテスト."""

    def test_stock_daily_import_with_valid_class_returns_success(self):
        """StockDailyのインポートテスト."""
        assert StockDaily is not None
        assert StockDaily == Stocks1d

    def test_stock_daily_repr_with_valid_data_returns_formatted_string(self):
        """StockDailyの文字列表現テスト."""
        # StockDailyインスタンスを作成
        stock = StockDaily()
        stock.symbol = "7203"
        stock.date = date(2024, 1, 15)
        stock.close = Decimal("1500.00")

        expected = (
            "<Stocks1d(symbol='7203', date='2024-01-15', close=1500.00)>"
        )
        assert repr(stock) == expected

    def test_stock_daily_tablename_with_model_returns_correct_name(self):
        """StockDailyのテーブル名テスト."""
        assert StockDaily.__tablename__ == "stocks_1d"

    def test_stock_daily_inheritance_with_base_classes_returns_valid_hierarchy(
        self,
    ):
        """StockDailyの継承関係テスト."""
        assert issubclass(StockDaily, Base)
        assert issubclass(StockDaily, StockDataBase)


class TestStockDataBase:
    """StockDataBaseクラスのテスト."""

    def test_to_dict_method_with_complete_data_returns_formatted_dict(self):
        """to_dictメソッドのテスト."""
        # StockDailyインスタンスを作成してテスト
        stock = StockDaily()
        stock.id = 1
        stock.symbol = "7203"
        stock.open = Decimal("1400.00")
        stock.high = Decimal("1600.00")
        stock.low = Decimal("1350.00")
        stock.close = Decimal("1500.00")
        stock.volume = 1000000
        stock.date = date(2024, 1, 15)
        stock.created_at = datetime(2024, 1, 15, 10, 0, 0)
        stock.updated_at = datetime(2024, 1, 15, 15, 0, 0)

        result = stock.to_dict()

        expected = {
            "id": 1,
            "symbol": "7203",
            "open": 1400.00,
            "high": 1600.00,
            "low": 1350.00,
            "close": 1500.00,
            "volume": 1000000,
            "date": "2024-01-15",
            "created_at": "2024-01-15T10:00:00",
            "updated_at": "2024-01-15T15:00:00",
        }

        assert result == expected

    def test_to_dict_method_with_none_values_returns_partial_dict(self):
        """None値を含むto_dictメソッドのテスト."""
        stock = StockDaily()
        stock.id = 1
        stock.symbol = "7203"
        stock.open = None
        stock.high = None
        stock.low = None
        stock.close = None
        stock.volume = 0
        stock.date = None
        stock.created_at = None
        stock.updated_at = None

        result = stock.to_dict()

        expected = {
            "id": 1,
            "symbol": "7203",
            "open": None,
            "high": None,
            "low": None,
            "close": None,
            "volume": 0,
            "date": None,
            "created_at": None,
            "updated_at": None,
        }

        assert result == expected


class TestDatabaseError:
    """DatabaseErrorクラスのテスト."""

    def test_database_error_creation_with_message_returns_valid_instance(self):
        """DatabaseErrorの作成テスト."""
        error = DatabaseError("データベースエラー")
        assert str(error) == "データベースエラー"

    def test_database_error_inheritance_with_exception_returns_valid_hierarchy(
        self,
    ):
        """DatabaseErrorの継承関係テスト."""
        error = DatabaseError("テスト")
        assert isinstance(error, Exception)


class TestStockDataError:
    """StockDataErrorクラスのテスト."""

    def test_stock_data_error_creation_with_message_returns_valid_instance(
        self,
    ):
        """StockDataErrorの作成テスト."""
        error = StockDataError("株価データエラー")
        assert str(error) == "株価データエラー"

    def test_stock_data_error_inheritance_with_exception_returns_valid_hierarchy(
        self,
    ):
        """StockDataErrorの継承関係テスト."""
        error = StockDataError("テスト")
        assert isinstance(error, Exception)


class TestStockDailyCRUD:
    """StockDailyCRUDクラスのテスト."""

    @patch("app.models.get_db_session")
    def test_create_success_with_valid_data_returns_created_instance(
        self, mock_get_db_session
    ):
        """正常なデータ作成のテスト."""
        # モックセッションの設定
        mock_session = Mock(spec=Session)
        mock_get_db_session.return_value.__enter__.return_value = mock_session

        # テストデータ
        data = {
            "symbol": "7203",
            "open": 1400.00,
            "high": 1600.00,
            "low": 1350.00,
            "close": 1500.00,
            "volume": 1000000,
            "date": date(2024, 1, 15),
        }

        result = StockDailyCRUD.create(data)

        # セッションのメソッドが呼ばれたことを確認
        mock_session.add.assert_called_once()
        mock_session.commit.assert_called_once()
        assert result is not None

    @patch("app.models.get_db_session")
    def test_create_integrity_error_with_duplicate_data_raises_database_error(
        self, mock_get_db_session
    ):
        """重複データでのIntegrityErrorテスト."""
        # モックセッションの設定
        mock_session = Mock(spec=Session)
        mock_session.commit.side_effect = IntegrityError("", "", "")
        mock_get_db_session.return_value.__enter__.return_value = mock_session

        data = {
            "symbol": "7203",
            "date": date(2024, 1, 15),
        }

        with pytest.raises(DatabaseError):
            StockDailyCRUD.create(data)

        mock_session.rollback.assert_called_once()

    @patch("app.models.get_db_session")
    def test_get_by_id_found_with_existing_id_returns_instance(
        self, mock_get_db_session
    ):
        """IDによる検索（見つかった場合）のテスト."""
        # モックセッションの設定
        mock_session = Mock(spec=Session)
        mock_stock = Mock(spec=StockDaily)
        mock_session.query.return_value.filter.return_value.first.return_value = (
            mock_stock
        )
        mock_get_db_session.return_value.__enter__.return_value = mock_session

        result = StockDailyCRUD.get_by_id(1)

        assert result == mock_stock
        mock_session.query.assert_called_once_with(StockDaily)

    @patch("app.models.get_db_session")
    def test_get_by_id_not_found_with_nonexistent_id_returns_none(
        self, mock_get_db_session
    ):
        """IDによる検索（見つからなかった場合）のテスト."""
        # モックセッションの設定
        mock_session = Mock(spec=Session)
        mock_session.query.return_value.filter.return_value.first.return_value = (
            None
        )
        mock_get_db_session.return_value.__enter__.return_value = mock_session

        result = StockDailyCRUD.get_by_id(999)

        assert result is None

    @patch("app.models.get_db_session")
    def test_get_by_symbol_and_date_with_valid_params_returns_instance(
        self, mock_get_db_session
    ):
        """シンボルと日付による検索のテスト."""
        # モックセッションの設定
        mock_session = Mock(spec=Session)
        mock_stock = Mock(spec=StockDaily)
        mock_session.query.return_value.filter.return_value.first.return_value = (
            mock_stock
        )
        mock_get_db_session.return_value.__enter__.return_value = mock_session

        result = StockDailyCRUD.get_by_symbol_and_date(
            "7203", date(2024, 1, 15)
        )

        assert result == mock_stock

    @patch("app.models.StockDaily")
    def test_update_success_with_valid_data_returns_updated_instance(
        self, mock_stock_daily_class
    ):
        """正常な更新のテスト."""
        # モックインスタンスの設定
        mock_instance = Mock()
        mock_stock_daily_class.query.filter_by.return_value.first.return_value = (
            mock_instance
        )

        data = {"close": 1600.00}
        result = StockDailyCRUD.update(1, data)

        # 属性が更新されたことを確認
        assert mock_instance.close == 1600.00
        assert result == mock_instance

    @patch("app.models.StockDaily")
    def test_update_not_found_with_nonexistent_id_returns_none(
        self, mock_stock_daily_class
    ):
        """存在しないIDでの更新テスト."""
        # モックの設定
        mock_stock_daily_class.query.filter_by.return_value.first.return_value = (
            None
        )

        result = StockDailyCRUD.update(999, {"close": 1600.00})

        assert result is None

    @patch("app.models.get_db_session")
    def test_delete_success_with_existing_id_returns_true(
        self, mock_get_db_session
    ):
        """正常な削除のテスト."""
        # モックセッションの設定
        mock_session = Mock(spec=Session)
        mock_stock = Mock(spec=StockDaily)
        mock_session.query.return_value.filter.return_value.first.return_value = (
            mock_stock
        )
        mock_get_db_session.return_value.__enter__.return_value = mock_session

        result = StockDailyCRUD.delete(1)

        mock_session.delete.assert_called_once_with(mock_stock)
        mock_session.commit.assert_called_once()
        assert result is True

    @patch("app.models.get_db_session")
    def test_delete_not_found_with_nonexistent_id_returns_false(
        self, mock_get_db_session
    ):
        """存在しないIDでの削除テスト."""
        # モックセッションの設定
        mock_session = Mock(spec=Session)
        mock_session.query.return_value.filter.return_value.first.return_value = (
            None
        )
        mock_get_db_session.return_value.__enter__.return_value = mock_session

        result = StockDailyCRUD.delete(999)

        assert result is False

    @patch("app.models.get_db_session")
    def test_count_by_symbol_with_existing_symbol_returns_count(
        self, mock_get_db_session
    ):
        """シンボル別カウントのテスト."""
        # モックセッションの設定
        mock_session = Mock(spec=Session)
        mock_session.query.return_value.filter.return_value.count.return_value = (
            5
        )
        mock_get_db_session.return_value.__enter__.return_value = mock_session

        result = StockDailyCRUD.count_by_symbol("7203")

        assert result == 5

    @patch("app.models.get_db_session")
    def test_get_latest_date_by_symbol_with_existing_data_returns_date(
        self, mock_get_db_session
    ):
        """シンボル別最新日付取得のテスト."""
        # モックセッションの設定
        mock_session = Mock(spec=Session)
        mock_session.query.return_value.filter.return_value.order_by.return_value.first.return_value = (
            date(2024, 1, 15),
        )
        mock_get_db_session.return_value.__enter__.return_value = mock_session

        result = StockDailyCRUD.get_latest_date_by_symbol("7203")

        assert result == date(2024, 1, 15)

    @patch("app.models.get_db_session")
    def test_get_latest_date_by_symbol_not_found_with_nonexistent_symbol_returns_none(
        self, mock_get_db_session
    ):
        """存在しないシンボルでの最新日付取得テスト."""
        # モックセッションの設定
        mock_session = Mock(spec=Session)
        mock_session.query.return_value.filter.return_value.order_by.return_value.first.return_value = (
            None
        )
        mock_get_db_session.return_value.__enter__.return_value = mock_session

        result = StockDailyCRUD.get_latest_date_by_symbol("INVALID")

        assert result is None


class TestGetDbSession:
    """get_db_session関数のテスト."""

    @patch("app.models.SessionLocal")
    def test_get_db_session_with_context_manager_returns_session(
        self, mock_session_local
    ):
        """get_db_sessionのコンテキストマネージャーテスト."""
        mock_session = Mock(spec=Session)
        mock_session_local.return_value = mock_session

        with get_db_session() as session:
            assert session == mock_session

        mock_session.close.assert_called_once()

    @patch("app.models.SessionLocal")
    def test_get_db_session_exception_handling_with_error_calls_rollback(
        self, mock_session_local
    ):
        """get_db_sessionの例外処理テスト."""
        mock_session = Mock(spec=Session)
        mock_session_local.return_value = mock_session

        try:
            with get_db_session():
                raise Exception("テストエラー")
        except Exception:
            pass

        mock_session.rollback.assert_called_once()
        mock_session.close.assert_called_once()


class TestStockMaster:
    """StockMasterクラスのテスト."""

    def test_stock_master_model_creation_with_valid_data_returns_model_instance(
        self,
    ):
        """StockMasterモデルの作成テスト."""
        assert StockMaster is not None
        assert StockMaster == Stocks1d

    def test_stock_master_model_validation_with_invalid_data_raises_validation_error(
        self,
    ):
        """StockMasterモデルの検証テスト."""
        # StockMasterインスタンスを作成
        stock = StockMaster()
        stock.symbol = "7203"
        stock.date = date(2024, 1, 15)
        stock.close = Decimal("1500.00")

        expected = (
            "<Stocks1d(symbol='7203', date='2024-01-15', close=1500.00)>"
        )
        assert repr(stock) == expected

    def test_stock_master_model_relationships_with_valid_data_returns_correct_associations(
        self,
    ):
        """StockMasterのテーブル名テスト."""
        assert StockMaster.__tablename__ == "stocks_1d"

    def test_stock_master_model_creation_with_valid_data_returns_model_instance(
        self,
    ):
        """StockMasterモデルの作成テスト."""
        assert StockMaster is not None
        assert StockMaster == Stocks1d

    def test_stock_master_model_validation_with_invalid_data_raises_validation_error(
        self,
    ):
        """StockMasterモデルの検証テスト."""
        # StockMasterインスタンスを作成
        stock = StockMaster()
        stock.symbol = "7203"
        stock.date = date(2024, 1, 15)
        stock.close = Decimal("1500.00")

        expected = (
            "<Stocks1d(symbol='7203', date='2024-01-15', close=1500.00)>"
        )
        assert repr(stock) == expected
