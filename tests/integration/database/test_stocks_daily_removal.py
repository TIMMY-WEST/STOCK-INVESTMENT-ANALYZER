"""stocks_daily テーブル削除に関するテストコード.

Issue #65: Remove stocks_daily table after migration

このテストは以下を検証します:
1. データ移行の完了確認
2. アプリケーションコードの正常動作
3. stocks_1d テーブルの正常性
4. 削除前後の整合性確認。
"""
# flake8: noqa

from datetime import date, datetime
from decimal import Decimal
import os

from dotenv import load_dotenv  # noqa: E402
import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import sessionmaker

from app.models import (  # noqa: E402
    Base,
    DatabaseError,
    StockDaily,
    StockDailyCRUD,
    StockDataError,
    Stocks1d,
    Stocks1h,
    Stocks1m,
    get_db_session,
)


# プロジェクトルートをパスに追加
# sys.path.append(os.path.join(os.path.dirname(__file__), "..", "..", "app"))

# legacy: removed import from models (now using app.models)
# legacy names were: Base, DatabaseError, StockDaily, StockDailyCRUD, StockDataError, Stocks1d, get_db_session


load_dotenv(os.path.join(os.path.dirname(__file__), "..", "..", ".env"))


# module-level marker so pytest -m integration picks these up
pytestmark = pytest.mark.integration


@pytest.fixture(scope="class")
def engine():
    """クラススコープのエンジンを提供するfixture."""
    test_db_url = f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
    eng = create_engine(test_db_url)
    yield eng
    try:
        eng.dispose()
    except Exception:
        pass


@pytest.fixture()
def session(engine):  # noqa: C901
    """テストごとのセッションを提供し、前後でクリーンアップを行う."""
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    sess = SessionLocal()
    symbols = ["TEST.T", "CRUD.T", "CONSTRAINT.T", "COUNT.T", "LATEST.T"]
    try:
        sess.query(Stocks1d).filter(Stocks1d.symbol.in_(symbols)).delete(
            synchronize_session=False
        )
        sess.commit()
    except Exception:
        sess.rollback()
    yield sess
    try:
        sess.rollback()
        sess.query(Stocks1d).filter(Stocks1d.symbol.in_(symbols)).delete(
            synchronize_session=False
        )
        sess.commit()
    except Exception:
        sess.rollback()
    finally:
        sess.close()

    def test_stocks_1d_table_exists(self, engine):
        """stocks_1d テーブルが存在することを確認."""
        # Arrange (準備)
        # データベース接続を使用

        # Act (実行)

    with engine.connect() as conn:
        result = conn.execute(
            text(
                """
                SELECT COUNT(*)
                FROM information_schema.tables
                WHERE table_name = 'stocks_1d'
            """
            )
        )
        table_count = result.scalar()

    # Assert (検証)
    assert table_count == 1, "stocks_1d テーブルが存在しません"

    def test_stock_daily_alias_works(self, session):
        """Verify that StockDaily エイリアスが正常に動作することを確認."""
        # Arrange (準備)
        # テストデータを使用

        # Act & Assert (実行と検証)
        alias_check = StockDaily == Stocks1d
        assert alias_check, "StockDaily は Stocks1d のエイリアスである必要があります"

        stock_data = StockDailyCRUD.create(
            session,
            **{
                "symbol": "TEST.T",
                "date": datetime(2024, 1, 15).date(),
                "open": Decimal("1000.00"),
                "high": Decimal("1100.00"),
                "low": Decimal("950.00"),
                "close": Decimal("1050.00"),
                "volume": 100000,
            },
        )

        assert stock_data is not None, "StockDaily を使用したデータ作成に失敗しました"
        assert stock_data.symbol == "TEST.T"

    def test_stocks_1d_crud_operations(self, session):
        """stocks_1d テーブルに対するCRUD操作が正常に動作することを確認."""
        # Arrange (準備)
        test_data = self.test_data.copy()
        test_data["symbol"] = "CRUD.T"

        with get_db_session() as session:
            # Act (実行) - Create
            created_stock = StockDailyCRUD.create(session, **test_data)

            # Assert (検証) - Create
            assert created_stock is not None
            assert created_stock.symbol == test_data["symbol"]

            # Act (実行) - Read by ID
            retrieved_stock = StockDailyCRUD.get_by_id(
                session, created_stock.id
            )
            assert retrieved_stock is not None
            assert retrieved_stock.symbol == test_data["symbol"]

            # Act (実行) - Read by symbol and date
            retrieved_by_date = StockDailyCRUD.get_by_symbol_and_date(
                session, test_data["symbol"], test_data["date"]
            )
            assert retrieved_by_date is not None
            assert retrieved_by_date.id == created_stock.id

            # Act (実行) - Update
            updated_stock = StockDailyCRUD.update(
                session, created_stock.id, close=Decimal("1080.00")
            )
            assert updated_stock is not None
            assert updated_stock.close == Decimal("1080.00")

            # Act (実行) - Delete
            delete_result = StockDailyCRUD.delete(session, created_stock.id)
            assert delete_result

            # Act (実行) - Verify deletion
            deleted_stock = StockDailyCRUD.get_by_id(session, created_stock.id)
            assert deleted_stock is None

    @pytest.mark.skip(reason="制約テストは一時的にスキップ")
    def test_stocks_1d_constraints(self, session):
        """stocks_1d テーブルの制約が正常に動作することを確認."""
        # Arrange (準備)
        test_data = self.test_data.copy()
        test_data["symbol"] = "CONSTRAINT.T"

        with get_db_session() as session:
            # Act (実行) - 正常なデータの作成
            stock_data = StockDailyCRUD.create(session, **test_data)
            assert stock_data is not None

            # 重複データの作成を試行
            import pytest as _pytest

            with _pytest.raises(
                (DatabaseError, StockDataError, SQLAlchemyError)
            ):
                StockDailyCRUD.create(session, **test_data)

    def test_stocks_1d_indexes(self):
        """stocks_1d テーブルのインデックスが存在することを確認."""
        # Arrange (準備)
        expected_indexes = [
            "idx_stocks_1d_date",
            "idx_stocks_1d_symbol",
            "idx_stocks_1d_symbol_date_desc",
        ]

        # Act (実行)
        with self.engine.connect() as conn:
            result = conn.execute(
                text(
                    """
                SELECT indexname
                FROM pg_indexes
                WHERE tablename = 'stocks_1d'
                ORDER BY indexname
            """
                )
            )
            indexes = [row[0] for row in result]

        # Assert (検証)
        for expected_index in expected_indexes:
            assert (
                expected_index in indexes
            ), f"インデックス {expected_index} が存在しません"

    def test_data_migration_validation(self, engine):
        """データ移行の検証（stocks_daily が存在する場合）."""
        # Arrange (準備)
        # データベース接続を使用

        # Act (実行)
        with self.engine.connect() as conn:
            result = conn.execute(
                text(
                    """
                SELECT COUNT(*)
                FROM information_schema.tables
                WHERE table_name = 'stocks_daily'
            """
                )
            )
            stocks_daily_exists = result.scalar() > 0

            # Assert (検証)
            if stocks_daily_exists:
                stocks_daily_count = conn.execute(
                    text("SELECT COUNT(*) FROM stocks_daily")
                ).scalar()
                stocks_1d_count = conn.execute(
                    text("SELECT COUNT(*) FROM stocks_1d")
                ).scalar()

                assert (
                    stocks_1d_count >= stocks_daily_count
                ), "stocks_1d のレコード数が stocks_daily より少ないです"

                if stocks_daily_count > 0:
                    sample_data = conn.execute(
                        text(
                            """
                        SELECT symbol, date, open, high, low, close, volume
                        FROM stocks_daily
                        LIMIT 5
                    """
                        )
                    ).fetchall()

                    for row in sample_data:
                        (
                            symbol,
                            date_val,
                            open_val,
                            high_val,
                            low_val,
                            close_val,
                            volume_val,
                        ) = row

                        stocks_1d_data = conn.execute(
                            text(
                                """
                            SELECT COUNT(*)
                            FROM stocks_1d
                            WHERE symbol = :symbol
                            AND date = :date
                            AND open = :open
                            AND high = :high
                            AND low = :low
                            AND close = :close
                            AND volume = :volume
                        """
                            ),
                            {
                                "symbol": symbol,
                                "date": date_val,
                                "open": open_val,
                                "high": high_val,
                                "low": low_val,
                                "close": close_val,
                                "volume": volume_val,
                            },
                        ).scalar()

                        assert (
                            stocks_1d_data == 1
                        ), f"stocks_daily のデータ ({symbol}, {date_val}) が stocks_1d に存在しません"

    def test_bulk_operations(self, session):
        """一括操作が正常に動作することを確認."""
        # Arrange (準備)
        test_data_list = [
            {
                "symbol": "BULK1.T",
                "date": date(2024, 1, 10),
                "open": Decimal("1000.00"),
                "high": Decimal("1100.00"),
                "low": Decimal("950.00"),
                "close": Decimal("1050.00"),
                "volume": 100000,
            },
            {
                "symbol": "BULK2.T",
                "date": date(2024, 1, 11),
                "open": Decimal("2000.00"),
                "high": Decimal("2100.00"),
                "low": Decimal("1950.00"),
                "close": Decimal("2050.00"),
                "volume": 200000,
            },
        ]

        try:
            # Act (実行)
            with get_db_session() as session:
                created_stocks = StockDailyCRUD.bulk_create(
                    session, test_data_list
                )
                assert len(created_stocks) == 2
                for i, stock in enumerate(created_stocks):
                    assert stock.symbol == test_data_list[i]["symbol"]
                    assert stock.date == test_data_list[i]["date"]

        finally:
            with get_db_session() as cleanup_session:
                for test_data in test_data_list:
                    cleanup_session.query(Stocks1d).filter(
                        Stocks1d.symbol == test_data["symbol"]
                    ).delete()
                cleanup_session.commit()

    def test_count_operations(self, session):
        """カウント操作が正常に動作することを確認."""
        # Arrange (準備)
        test_data = self.test_data.copy()
        test_data["symbol"] = "COUNT.T"

        with get_db_session() as session:
            # Act (実行) - テストデータ作成
            _ = StockDailyCRUD.create(session, **test_data)
            total_count = StockDailyCRUD.count_all(session)
            assert total_count > 0
            symbol_count = StockDailyCRUD.count_by_symbol(
                session, test_data["symbol"]
            )
            assert symbol_count == 1
            filtered_count = StockDailyCRUD.count_with_filters(
                session, symbol=test_data["symbol"]
            )
            assert filtered_count == 1

    def test_latest_date_retrieval(self, session):
        """最新日付取得が正常に動作することを確認."""
        # Arrange (準備)
        test_data = self.test_data.copy()
        test_data["symbol"] = "LATEST.T"

        with get_db_session() as session:
            # Act (実行) - テストデータ作成
            _ = StockDailyCRUD.create(session, **test_data)
            latest_date = StockDailyCRUD.get_latest_date_by_symbol(
                session, test_data["symbol"]
            )
            assert latest_date == test_data["date"]


class TestDatabaseConnection:
    """データベース接続テスト."""

    def test_database_connection(self):
        """データベース接続が正常に動作することを確認."""
        try:
            with get_db_session() as session:
                result = session.execute(text("SELECT 1")).scalar()
            assert result == 1
        except Exception as e:
            pytest.fail(f"データベース接続に失敗しました: {str(e)}")

    def test_required_tables_exist(self):
        """必要なテーブルが存在することを確認."""
        required_tables = [
            "stocks_1d",
            "stocks_1m",
            "stocks_5m",
            "stocks_15m",
            "stocks_30m",
            "stocks_1h",
            "stocks_1wk",
            "stocks_1mo",
        ]

        with get_db_session() as session:
            for table_name in required_tables:
                result = session.execute(
                    text(
                        f"""
                    SELECT COUNT(*)
                    FROM information_schema.tables
                    WHERE table_name = '{table_name}'
                """
                    )
                ).scalar()
                assert result == 1, f"テーブル {table_name} が存在しません"
