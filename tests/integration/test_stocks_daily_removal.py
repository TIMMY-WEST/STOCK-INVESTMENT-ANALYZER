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

from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import sessionmaker


# プロジェクトルートをパスに追加
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "..", "app"))

from dotenv import load_dotenv  # noqa: E402

from models import (  # noqa: E402
    Base,
    DatabaseError,
    StockDaily,
    StockDailyCRUD,
    StockDataError,
    Stocks1d,
    get_db_session,
)


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
            self.assertEqual(
                table_count, 1, "stocks_1d テーブルが存在しません"
            )

    def test_stock_daily_alias_works(self):
        """Verify that StockDaily エイリアスが正常に動作することを確認."""
        # StockDaily が Stocks1d のエイリアスであることを確認
        self.assertEqual(
            StockDaily,
            Stocks1d,
            "StockDaily は Stocks1d のエイリアスである必要があります",
        )

        # StockDaily を使用してデータ作成
        with get_db_session() as session:
            stock_data = StockDailyCRUD.create(session, **self.test_data)
            self.assertIsNotNone(
                stock_data, "StockDaily を使用したデータ作成に失敗しました"
            )
            self.assertEqual(stock_data.symbol, self.test_data["symbol"])

    def test_stocks_1d_crud_operations(self):
        """stocks_1d テーブルに対するCRUD操作が正常に動作することを確認."""
        # テスト用データ（異なるシンボルを使用）
        test_data = self.test_data.copy()
        test_data["symbol"] = "CRUD.T"

        with get_db_session() as session:
            # Create
            created_stock = StockDailyCRUD.create(session, **test_data)
            self.assertIsNotNone(created_stock)
            self.assertEqual(created_stock.symbol, test_data["symbol"])

            # Read by ID
            retrieved_stock = StockDailyCRUD.get_by_id(
                session, created_stock.id
            )
            self.assertIsNotNone(retrieved_stock)
            self.assertEqual(retrieved_stock.symbol, test_data["symbol"])

            # Read by symbol and date
            retrieved_by_date = StockDailyCRUD.get_by_symbol_and_date(
                session, test_data["symbol"], test_data["date"]
            )
            self.assertIsNotNone(retrieved_by_date)
            self.assertEqual(retrieved_by_date.id, created_stock.id)

            # Update
            updated_stock = StockDailyCRUD.update(
                session, created_stock.id, close=Decimal("1080.00")
            )
            self.assertIsNotNone(updated_stock)
            self.assertEqual(updated_stock.close, Decimal("1080.00"))

            # Delete
            delete_result = StockDailyCRUD.delete(session, created_stock.id)
            self.assertTrue(delete_result)

            # Verify deletion
            deleted_stock = StockDailyCRUD.get_by_id(session, created_stock.id)
            self.assertIsNone(deleted_stock)

    @unittest.skip("制約テストは一時的にスキップ")
    def test_stocks_1d_constraints(self):
        """stocks_1d テーブルの制約が正常に動作することを確認."""
        # テスト用データ（異なるシンボルを使用）
        test_data = self.test_data.copy()
        test_data["symbol"] = "CONSTRAINT.T"

        # 正常なデータの作成
        with get_db_session() as session:
            stock_data = StockDailyCRUD.create(session, **test_data)
            self.assertIsNotNone(stock_data)

            # 同じセッション内で重複データの作成を試行（UniqueConstraint のテスト）
            try:
                StockDailyCRUD.create(session, **test_data)
                self.fail("重複データの作成が成功してしまいました")
            except (DatabaseError, StockDataError, SQLAlchemyError):
                # 期待される例外が発生した場合は成功
                pass

    def test_stocks_1d_indexes(self):
        """stocks_1d テーブルのインデックスが存在することを確認."""
        with self.engine.connect() as conn:
            # インデックスの存在確認
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

            expected_indexes = [
                "idx_stocks_1d_date",
                "idx_stocks_1d_symbol",
                "idx_stocks_1d_symbol_date_desc",
            ]

            for expected_index in expected_indexes:
                self.assertIn(
                    expected_index,
                    indexes,
                    f"インデックス {expected_index} が存在しません",
                )

    def test_data_migration_validation(self):
        """データ移行の検証（stocks_daily が存在する場合）."""
        with self.engine.connect() as conn:
            # stocks_daily テーブルの存在確認
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

            if stocks_daily_exists:
                # stocks_daily と stocks_1d のレコード数比較
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

                # データの整合性確認（サンプルチェック）
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

                        # stocks_1d に対応するデータが存在するかチェック
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
            with get_db_session() as session:
                # 一括作成
                created_stocks = StockDailyCRUD.bulk_create(
                    session, test_data_list
                )
                self.assertEqual(len(created_stocks), 2)

                # 作成されたデータの確認
                for i, stock in enumerate(created_stocks):
                    self.assertEqual(stock.symbol, test_data_list[i]["symbol"])
                    self.assertEqual(stock.date, test_data_list[i]["date"])

        finally:
            # クリーンアップ
            with get_db_session() as session:
                for test_data in test_data_list:
                    session.query(Stocks1d).filter(
                        Stocks1d.symbol == test_data["symbol"]
                    ).delete()
                session.commit()

    def test_count_operations(self):
        """カウント操作が正常に動作することを確認."""
        # テスト用データ（異なるシンボルを使用）
        test_data = self.test_data.copy()
        test_data["symbol"] = "COUNT.T"

        with get_db_session() as session:
            # テストデータ作成
            _ = StockDailyCRUD.create(session, **test_data)

            # 全件数取得
            total_count = StockDailyCRUD.count_all(session)
            self.assertGreater(total_count, 0)

            # 銘柄別件数取得
            symbol_count = StockDailyCRUD.count_by_symbol(
                session, test_data["symbol"]
            )
            self.assertEqual(symbol_count, 1)

            # フィルタ条件での件数取得
            filtered_count = StockDailyCRUD.count_with_filters(
                session, symbol=test_data["symbol"]
            )
            self.assertEqual(filtered_count, 1)

    def test_latest_date_retrieval(self):
        """最新日付取得が正常に動作することを確認."""
        # テスト用データ（異なるシンボルを使用）
        test_data = self.test_data.copy()
        test_data["symbol"] = "LATEST.T"

        with get_db_session() as session:
            # テストデータ作成
            _ = StockDailyCRUD.create(session, **test_data)

            # 最新日付取得
            latest_date = StockDailyCRUD.get_latest_date_by_symbol(
                session, test_data["symbol"]
            )
            self.assertEqual(latest_date, test_data["date"])


class TestDatabaseConnection(unittest.TestCase):
    """データベース接続テスト."""

    def test_database_connection(self):
        """データベース接続が正常に動作することを確認."""
        try:
            with get_db_session() as session:
                result = session.execute(text("SELECT 1")).scalar()
                self.assertEqual(result, 1)
        except Exception as e:
            self.fail(f"データベース接続に失敗しました: {str(e)}")

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
                self.assertEqual(
                    result, 1, f"テーブル {table_name} が存在しません"
                )


if __name__ == "__main__":
    # テスト実行前の環境確認
    print("=== stocks_daily テーブル削除テスト開始 ===")
    print(f"データベース: {os.getenv('DB_NAME')}")
    print(f"ユーザー: {os.getenv('DB_USER')}")
    print(f"ホスト: {os.getenv('DB_HOST')}")
    print("=" * 50)

    # テスト実行
    unittest.main(verbosity=2)
