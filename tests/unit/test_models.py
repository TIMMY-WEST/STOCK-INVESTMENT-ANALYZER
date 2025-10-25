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

    def test_stock_daily_import(self):
        """StockDailyのインポートテスト."""
        assert StockDaily is not None
        assert StockDaily == Stocks1d

    def test_stock_daily_repr(self):
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

    def test_stock_daily_tablename(self):
        """StockDailyのテーブル名テスト."""
        assert StockDaily.__tablename__ == "stocks_1d"

    def test_stock_daily_inheritance(self):
        """StockDailyの継承関係テスト."""
        assert issubclass(StockDaily, Base)
        assert issubclass(StockDaily, StockDataBase)


class TestStockDataBase:
    """StockDataBaseクラスのテスト."""

    def test_to_dict_method(self):
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

    def test_to_dict_with_none_values(self):
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

    def test_database_error_creation(self):
        """DatabaseErrorの作成テスト."""
        error = DatabaseError("テストエラー")
        assert str(error) == "テストエラー"
        assert isinstance(error, Exception)

    def test_database_error_inheritance(self):
        """DatabaseErrorの継承関係テスト."""
        assert issubclass(DatabaseError, Exception)


class TestStockDataError:
    """StockDataErrorクラスのテスト."""

    def test_stock_data_error_creation(self):
        """StockDataErrorの作成テスト."""
        error = StockDataError("株価データエラー")
        assert str(error) == "株価データエラー"
        assert isinstance(error, Exception)

    def test_stock_data_error_inheritance(self):
        """StockDataErrorの継承関係テスト."""
        assert issubclass(StockDataError, Exception)


class TestStockDailyCRUD:
    """StockDailyCRUDクラスのテスト."""

    def setup_method(self):
        """各テストメソッドの前に実行される設定."""
        self.mock_session = Mock(spec=Session)

    def test_create_success(self):
        """正常なデータ作成のテスト."""
        # テストデータ
        test_data = {
            "symbol": "7203",
            "date": date(2024, 1, 15),
            "open": Decimal("1400.00"),
            "high": Decimal("1600.00"),
            "low": Decimal("1350.00"),
            "close": Decimal("1500.00"),
            "volume": 1000000,
        }

        # モックの設定
        mock_stock = Mock(spec=StockDaily)
        with patch("app.models.StockDaily", return_value=mock_stock):
            result = StockDailyCRUD.create(self.mock_session, **test_data)

        # 検証
        self.mock_session.add.assert_called_once_with(mock_stock)
        self.mock_session.flush.assert_called_once()
        assert result == mock_stock

    def test_create_integrity_error(self):
        """重複データ作成時のエラーテスト."""
        test_data = {
            "symbol": "7203",
            "date": date(2024, 1, 15),
            "open": Decimal("1400.00"),
            "high": Decimal("1600.00"),
            "low": Decimal("1350.00"),
            "close": Decimal("1500.00"),
            "volume": 1000000,
        }

        # IntegrityErrorをシミュレート
        self.mock_session.flush.side_effect = IntegrityError(
            "duplicate key", None, None
        )

        with patch("app.models.StockDaily"):
            with pytest.raises(DatabaseError):
                StockDailyCRUD.create(self.mock_session, **test_data)

    def test_get_by_id_found(self):
        """IDによる検索（見つかった場合）のテスト."""
        mock_stock = Mock(spec=StockDaily)
        mock_query = Mock()
        mock_query.filter.return_value.first.return_value = mock_stock
        self.mock_session.query.return_value = mock_query

        result = StockDailyCRUD.get_by_id(self.mock_session, 1)

        assert result == mock_stock
        self.mock_session.query.assert_called_once_with(StockDaily)

    def test_get_by_id_not_found(self):
        """IDによる検索（見つからない場合）のテスト."""
        mock_query = Mock()
        mock_query.filter.return_value.first.return_value = None
        self.mock_session.query.return_value = mock_query

        result = StockDailyCRUD.get_by_id(self.mock_session, 999)

        assert result is None

    def test_get_by_symbol_and_date(self):
        """シンボルと日付による検索のテスト."""
        mock_stock = Mock(spec=StockDaily)
        mock_query = Mock()
        mock_query.filter.return_value.first.return_value = mock_stock
        self.mock_session.query.return_value = mock_query

        result = StockDailyCRUD.get_by_symbol_and_date(
            self.mock_session, "7203", date(2024, 1, 15)
        )

        assert result == mock_stock

    @patch("app.models.StockDaily")
    def test_update_success(self, mock_stock_daily_class):
        """正常な更新のテスト."""
        mock_stock = Mock()
        mock_filter = Mock()
        mock_filter.first.return_value = mock_stock
        mock_query = Mock()
        mock_query.filter.return_value = mock_filter
        self.mock_session.query.return_value = mock_query

        # hasattrをモック
        with patch("builtins.hasattr", return_value=True):
            result = StockDailyCRUD.update(
                self.mock_session, 1, close=Decimal("1600.00")
            )

        assert result == mock_stock
        self.mock_session.flush.assert_called_once()

    @patch("app.models.StockDaily")
    def test_update_not_found(self, mock_stock_daily_class):
        """存在しないIDの更新のテスト."""
        mock_filter = Mock()
        mock_filter.first.return_value = None
        mock_query = Mock()
        mock_query.filter.return_value = mock_filter
        self.mock_session.query.return_value = mock_query

        result = StockDailyCRUD.update(
            self.mock_session, 999, close=Decimal("1600.00")
        )

        assert result is None

    def test_delete_success(self):
        """正常な削除のテスト."""
        mock_stock = Mock(spec=StockDaily)
        mock_query = Mock()
        mock_query.filter.return_value.first.return_value = mock_stock
        self.mock_session.query.return_value = mock_query

        result = StockDailyCRUD.delete(self.mock_session, 1)

        assert result is True
        self.mock_session.delete.assert_called_once_with(mock_stock)
        self.mock_session.flush.assert_called_once()

    def test_delete_not_found(self):
        """存在しないデータの削除テスト."""
        mock_query = Mock()
        mock_query.filter.return_value.first.return_value = None
        self.mock_session.query.return_value = mock_query

        result = StockDailyCRUD.delete(self.mock_session, 999)

        assert result is False

    def test_count_by_symbol(self):
        """シンボル別カウントのテスト."""
        mock_query = Mock()
        mock_query.filter.return_value.count.return_value = 100
        self.mock_session.query.return_value = mock_query

        result = StockDailyCRUD.count_by_symbol(self.mock_session, "7203")

        assert result == 100

    def test_get_latest_date_by_symbol(self):
        """シンボル別最新日付取得のテスト."""
        expected_date = date(2024, 1, 15)
        mock_query = Mock()
        mock_query.filter.return_value.order_by.return_value.first.return_value = (
            expected_date,
        )
        self.mock_session.query.return_value = mock_query

        result = StockDailyCRUD.get_latest_date_by_symbol(
            self.mock_session, "7203"
        )

        assert result == expected_date

    def test_get_latest_date_by_symbol_not_found(self):
        """データが存在しない場合の最新日付取得テスト."""
        mock_query = Mock()
        mock_query.filter.return_value.order_by.return_value.first.return_value = (
            None
        )
        self.mock_session.query.return_value = mock_query

        result = StockDailyCRUD.get_latest_date_by_symbol(
            self.mock_session, "9999"
        )

        assert result is None


class TestDatabaseSession:
    """データベースセッション関連のテスト."""

    def test_get_db_session(self):
        """get_db_sessionのテスト."""
        with patch("app.models.SessionLocal") as mock_session_local:
            mock_session = Mock()
            mock_session_local.return_value = mock_session

            # コンテキストマネージャーとしてテスト
            with get_db_session() as session:
                assert session == mock_session

            # セッションがクローズされることを確認
            mock_session.close.assert_called_once()
            mock_session.commit.assert_called_once()

    def test_get_db_session_exception_handling(self):
        """get_db_sessionの例外処理テスト."""
        with patch("app.models.SessionLocal") as mock_session_local:
            mock_session = Mock()
            mock_session_local.return_value = mock_session

            # 例外が発生した場合のテスト
            try:
                with get_db_session() as session:
                    assert session == mock_session
                    raise Exception("テストエラー")
            except Exception:
                pass

            # セッションがロールバックされクローズされることを確認
            mock_session.rollback.assert_called_once()
            mock_session.close.assert_called_once()
