"""stocks_daily テーブル削除に関するテストコード.

Issue #65: Remove stocks_daily table after migration

このテストは以下を検証します:
1. データ移行の完了確認
2. アプリケーションコードの正常動作
3. stocks_1d テーブルの正常性
4. 削除前後の整合性確認。
"""

from datetime import date, datetime
from decimal import Decimal
import os
import sys
import unittest

from dotenv import load_dotenv  # noqa: E402
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


class TestStocksDailyRemoval(unittest.TestCase):
    """stocks_daily テーブル削除に関するテストクラス."""

    @classmethod
    def setUpClass(cls):
        """テストクラス全体の初期化."""
        cls.test_db_url = f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
        cls.engine = create_engine(cls.test_db_url)
        cls.SessionLocal = sessionmaker(
            autocommit=False, autoflush=False, bind=cls.engine
        )

        # テストデータの作成（価格制約を満たすように修正）
        cls.test_data = {
            "symbol": "TEST.T",
            "date": datetime(2024, 1, 15).date(),
            "open": Decimal("1000.00"),
            "high": Decimal("1100.00"),
            "low": Decimal("950.00"),
            "close": Decimal("1050.00"),
            "volume": 100000,
        }

    def setUp(self):
        """各テストメソッドの初期化."""
        self.session = self.SessionLocal()

        # テスト用データをクリーンアップ
        try:
            # 既存のテストデータを削除（複数のシンボルに対応）
            self.session.query(Stocks1d).filter(
                Stocks1d.symbol.in_(
                    ["TEST.T", "CRUD.T", "CONSTRAINT.T", "COUNT.T", "LATEST.T"]
                )
            ).delete(synchronize_session=False)
            self.session.commit()
        except Exception:
            self.session.rollback()

    def tearDown(self):
        """各テストメソッドの後処理."""
        try:
            # セッションの状態をリセット
            self.session.rollback()
            # テスト用データをクリーンアップ（複数のシンボルに対応）
            self.session.query(Stocks1d).filter(
                Stocks1d.symbol.in_(
                    ["TEST.T", "CRUD.T", "CONSTRAINT.T", "COUNT.T", "LATEST.T"]
                )
            ).delete(synchronize_session=False)
            self.session.commit()
        except Exception:
            self.session.rollback()
        finally:
            self.session.close()

    def test_stocks_1d_table_exists(self):
        """stocks_1d テーブルが存在することを確認."""
        # Arrange (準備)
        # データベース接続を使用

        # Act (実行)
        with self.engine.connect() as conn:
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
        self.assertEqual(table_count, 1, "stocks_1d テーブルが存在しません")

    def test_stock_daily_alias_works(self):
        """Verify that StockDaily エイリアスが正常に動作することを確認."""
        # Arrange (準備)
        # テストデータを使用

        # Act & Assert (実行と検証)
        alias_check = StockDaily == Stocks1d
        self.assertTrue(
            alias_check,
            "StockDaily は Stocks1d のエイリアスである必要があります",
        )

        with get_db_session() as session:
            stock_data = StockDailyCRUD.create(session, **self.test_data)

            # Assert (検証)
            self.assertIsNotNone(stock_data, "StockDaily を使用したデータ作成に失敗しました")
            self.assertEqual(stock_data.symbol, self.test_data["symbol"])

    def test_stocks_1d_crud_operations(self):
        """stocks_1d テーブルに対するCRUD操作が正常に動作することを確認."""
        # Arrange (準備)
        test_data = self.test_data.copy()
        test_data["symbol"] = "CRUD.T"

        with get_db_session() as session:
            # Act (実行) - Create
            created_stock = StockDailyCRUD.create(session, **test_data)

            # Assert (検証) - Create
            self.assertIsNotNone(created_stock)
            self.assertEqual(created_stock.symbol, test_data["symbol"])

            # Act (実行) - Read by ID
            retrieved_stock = StockDailyCRUD.get_by_id(
                session, created_stock.id
            )

            # Assert (検証) - Read by ID
            self.assertIsNotNone(retrieved_stock)
            self.assertEqual(retrieved_stock.symbol, test_data["symbol"])

            # Act (実行) - Read by symbol and date
            retrieved_by_date = StockDailyCRUD.get_by_symbol_and_date(
                session, test_data["symbol"], test_data["date"]
            )

            # Assert (検証) - Read by symbol and date
            self.assertIsNotNone(retrieved_by_date)
            self.assertEqual(retrieved_by_date.id, created_stock.id)

            # Act (実行) - Update
            updated_stock = StockDailyCRUD.update(
                session, created_stock.id, close=Decimal("1080.00")
            )

            # Assert (検証) - Update
            self.assertIsNotNone(updated_stock)
            self.assertEqual(updated_stock.close, Decimal("1080.00"))

            # Act (実行) - Delete
            delete_result = StockDailyCRUD.delete(session, created_stock.id)

            # Assert (検証) - Delete
            self.assertTrue(delete_result)

            # Act (実行) - Verify deletion
            deleted_stock = StockDailyCRUD.get_by_id(session, created_stock.id)

            # Assert (検証) - Verify deletion
            self.assertIsNone(deleted_stock)

    @unittest.skip("制約テストは一時的にスキップ")
    def test_stocks_1d_constraints(self):
        """stocks_1d テーブルの制約が正常に動作することを確認."""
        # Arrange (準備)
        test_data = self.test_data.copy()
        test_data["symbol"] = "CONSTRAINT.T"

        with get_db_session() as session:
            # Act (実行) - 正常なデータの作成
            stock_data = StockDailyCRUD.create(session, **test_data)

            # Assert (検証) - 正常なデータの作成
            self.assertIsNotNone(stock_data)

            # Act & Assert (実行と検証) - 重複データの作成を試行
            try:
                StockDailyCRUD.create(session, **test_data)
                self.fail("重複データの作成が成功してしまいました")
            except (DatabaseError, StockDataError, SQLAlchemyError):
                pass

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
            self.assertIn(
                expected_index,
                indexes,
                f"インデックス {expected_index} が存在しません",
            )

    def test_data_migration_validation(self):
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

                self.assertGreaterEqual(
                    stocks_1d_count,
                    stocks_daily_count,
                    "stocks_1d のレコード数が stocks_daily より少ないです",
                )

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

                        self.assertEqual(
                            stocks_1d_data,
                            1,
                            f"stocks_daily のデータ ({symbol}, {date_val}) が stocks_1d に存在しません",
                        )

    def test_bulk_operations(self):
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

                # Assert (検証)
                self.assertEqual(len(created_stocks), 2)

                for i, stock in enumerate(created_stocks):
                    self.assertEqual(stock.symbol, test_data_list[i]["symbol"])
                    self.assertEqual(stock.date, test_data_list[i]["date"])

        finally:
            with get_db_session() as session:
                for test_data in test_data_list:
                    session.query(Stocks1d).filter(
                        Stocks1d.symbol == test_data["symbol"]
                    ).delete()
                session.commit()

    def test_count_operations(self):
        """カウント操作が正常に動作することを確認."""
        # Arrange (準備)
        test_data = self.test_data.copy()
        test_data["symbol"] = "COUNT.T"

        with get_db_session() as session:
            # Act (実行) - テストデータ作成
            _ = StockDailyCRUD.create(session, **test_data)

            # Act (実行) - 全件数取得
            total_count = StockDailyCRUD.count_all(session)

            # Assert (検証) - 全件数取得
            self.assertGreater(total_count, 0)

            # Act (実行) - 銘柄別件数取得
            symbol_count = StockDailyCRUD.count_by_symbol(
                session, test_data["symbol"]
            )

            # Assert (検証) - 銘柄別件数取得
            self.assertEqual(symbol_count, 1)

            # Act (実行) - フィルタ条件での件数取得
            filtered_count = StockDailyCRUD.count_with_filters(
                session, symbol=test_data["symbol"]
            )

            # Assert (検証) - フィルタ条件での件数取得
            self.assertEqual(filtered_count, 1)

    def test_latest_date_retrieval(self):
        """最新日付取得が正常に動作することを確認."""
        # Arrange (準備)
        test_data = self.test_data.copy()
        test_data["symbol"] = "LATEST.T"

        with get_db_session() as session:
            # Act (実行) - テストデータ作成
            _ = StockDailyCRUD.create(session, **test_data)

            # Act (実行) - 最新日付取得
            latest_date = StockDailyCRUD.get_latest_date_by_symbol(
                session, test_data["symbol"]
            )

            # Assert (検証)
            self.assertEqual(latest_date, test_data["date"])


class TestDatabaseConnection(unittest.TestCase):
    """データベース接続テスト."""

    def test_database_connection(self):
        """データベース接続が正常に動作することを確認."""
        # Arrange (準備)
        # データベースセッションを使用

        # Act (実行)
        try:
            with get_db_session() as session:
                result = session.execute(text("SELECT 1")).scalar()

            # Assert (検証)
            self.assertEqual(result, 1)
        except Exception as e:
            self.fail(f"データベース接続に失敗しました: {str(e)}")

    def test_required_tables_exist(self):
        """必要なテーブルが存在することを確認."""
        # Arrange (準備)
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

        # Act (実行) & Assert (検証)
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
                self.assertEqual(result, 1, f"テーブル {table_name} が存在しません")


if __name__ == "__main__":
    # テスト実行前の環境確認
    print("=== stocks_daily テーブル削除テスト開始 ===")
    print(f"データベース: {os.getenv('DB_NAME')}")
    print(f"ユーザー: {os.getenv('DB_USER')}")
    print(f"ホスト: {os.getenv('DB_HOST')}")
    print("=" * 50)

    # テスト実行
    unittest.main(verbosity=2)
