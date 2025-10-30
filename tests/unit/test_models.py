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

    def test_create_success_with_valid_data_returns_created_instance(self):
        """正常なデータ作成のテスト."""
        # モックセッションの設定
        mock_session = Mock(spec=Session)

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

        result = StockDailyCRUD.create(mock_session, **data)

        # セッションのメソッドが呼ばれたことを確認
        mock_session.add.assert_called_once()
        mock_session.flush.assert_called_once()
        assert result is not None

    def test_create_integrity_error_with_duplicate_data_raises_database_error(
        self,
    ):
        """重複データでのIntegrityErrorテスト."""
        # モックセッションの設定
        mock_session = Mock(spec=Session)
        mock_session.flush.side_effect = IntegrityError(
            "uk_stocks_daily_symbol_date", "", ""
        )

        data = {
            "symbol": "7203",
            "date": date(2024, 1, 15),
        }

        # ユニーク制約エラーはStockDataErrorを送出
        with pytest.raises(StockDataError):
            StockDailyCRUD.create(mock_session, **data)

    def test_get_by_id_found_with_existing_id_returns_instance(self):
        """IDによる検索（見つかった場合）のテスト."""
        # モックセッションの設定
        mock_session = Mock(spec=Session)
        mock_stock = Mock(spec=StockDaily)
        mock_session.query.return_value.filter.return_value.first.return_value = (
            mock_stock
        )

        result = StockDailyCRUD.get_by_id(mock_session, 1)

        assert result == mock_stock
        mock_session.query.assert_called_once_with(StockDaily)

    def test_get_by_id_not_found_with_nonexistent_id_returns_none(self):
        """IDによる検索（見つからなかった場合）のテスト."""
        # モックセッションの設定
        mock_session = Mock(spec=Session)
        mock_session.query.return_value.filter.return_value.first.return_value = (
            None
        )

        result = StockDailyCRUD.get_by_id(mock_session, 999)

        assert result is None

    def test_get_by_symbol_and_date_with_valid_params_returns_instance(self):
        """シンボルと日付による検索のテスト."""
        # モックセッションの設定
        mock_session = Mock(spec=Session)
        mock_stock = Mock(spec=StockDaily)
        mock_session.query.return_value.filter.return_value.first.return_value = (
            mock_stock
        )

        result = StockDailyCRUD.get_by_symbol_and_date(
            mock_session, "7203", date(2024, 1, 15)
        )

        assert result == mock_stock

    def test_update_success_with_valid_data_returns_updated_instance(self):
        """正常な更新のテスト."""
        # モックセッション・インスタンスの設定
        mock_session = Mock(spec=Session)
        mock_instance = Mock()
        mock_session.query.return_value.filter.return_value.first.return_value = (
            mock_instance
        )

        data = {"close": 1600.00}
        result = StockDailyCRUD.update(mock_session, 1, **data)

        # 属性が更新されたことを確認
        assert mock_instance.close == 1600.00
        mock_session.flush.assert_called_once()
        assert result == mock_instance

    def test_update_not_found_with_nonexistent_id_returns_none(self):
        """存在しないIDでの更新テスト."""
        # モックセッションの設定
        mock_session = Mock(spec=Session)
        mock_session.query.return_value.filter.return_value.first.return_value = (
            None
        )

        result = StockDailyCRUD.update(mock_session, 999, close=1600.00)

        assert result is None

    def test_delete_success_with_existing_id_returns_true(self):
        """正常な削除のテスト."""
        # モックセッションの設定
        mock_session = Mock(spec=Session)
        mock_stock = Mock(spec=StockDaily)
        mock_session.query.return_value.filter.return_value.first.return_value = (
            mock_stock
        )

        result = StockDailyCRUD.delete(mock_session, 1)

        mock_session.delete.assert_called_once_with(mock_stock)
        mock_session.flush.assert_called_once()
        assert result is True

    def test_delete_not_found_with_nonexistent_id_returns_false(self):
        """存在しないIDでの削除テスト."""
        # モックセッションの設定
        mock_session = Mock(spec=Session)
        mock_session.query.return_value.filter.return_value.first.return_value = (
            None
        )

        result = StockDailyCRUD.delete(mock_session, 999)

        assert result is False

    def test_count_by_symbol_with_existing_symbol_returns_count(self):
        """シンボル別カウントのテスト."""
        # モックセッションの設定
        mock_session = Mock(spec=Session)
        mock_session.query.return_value.filter.return_value.count.return_value = (
            5
        )

        result = StockDailyCRUD.count_by_symbol(mock_session, "7203")

        assert result == 5

    def test_get_latest_date_by_symbol_with_existing_data_returns_date(self):
        """シンボル別最新日付取得のテスト."""
        # モックセッションの設定
        mock_session = Mock(spec=Session)
        mock_session.query.return_value.filter.return_value.order_by.return_value.first.return_value = (
            date(2024, 1, 15),
        )

        result = StockDailyCRUD.get_latest_date_by_symbol(mock_session, "7203")

        assert result == date(2024, 1, 15)

    def test_get_latest_date_by_symbol_not_found_with_nonexistent_symbol_returns_none(
        self,
    ):
        """存在しないシンボルでの最新日付取得テスト."""
        # モックセッションの設定
        mock_session = Mock(spec=Session)
        mock_session.query.return_value.filter.return_value.order_by.return_value.first.return_value = (
            None
        )

        result = StockDailyCRUD.get_latest_date_by_symbol(
            mock_session, "INVALID"
        )

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

    def test_stock_master_basic_definition_returns_valid_table_name(self):
        """StockMasterモデルの基本定義テスト."""
        assert StockMaster is not None
        assert StockMaster.__tablename__ == "stock_master"

    def test_stock_master_repr_with_valid_data_returns_formatted_string(self):
        """StockMasterの文字列表現テスト."""
        stock = StockMaster()
        stock.stock_code = "7203"
        stock.stock_name = "トヨタ自動車"
        stock.is_active = 1

        expected = "<StockMaster(stock_code='7203', stock_name='トヨタ自動車', is_active=1)>"
        assert repr(stock) == expected
