"""
銘柄マスタテーブルのモデルテスト.

テスト対象:
- StockMaster モデル
- StockMasterUpdate モデル
- テーブル作成
- CRUD操作
- インデックス検証。
"""

from datetime import datetime
import os
from pathlib import Path
import sys

from dotenv import load_dotenv
import pytest
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import sessionmaker


# プロジェクトルートをPythonパスに追加
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "app"))

from models import Base, StockMaster, StockMasterUpdate


load_dotenv()

# テスト用データベース接続
DATABASE_URL = f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"


@pytest.fixture(scope="module")
def engine():
    """テスト用データベースエンジン."""
    engine = create_engine(DATABASE_URL)
    yield engine
    engine.dispose()


@pytest.fixture(scope="module")
def session(engine):
    """テスト用セッション."""
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()


@pytest.fixture(scope="function")
def clean_stock_master_tables(session):
    """各テスト前に銘柄マスタテーブルをクリーンアップ."""
    session.execute(text("DELETE FROM stock_master_updates"))
    session.execute(text("DELETE FROM stock_master"))
    session.commit()
    yield
    session.execute(text("DELETE FROM stock_master_updates"))
    session.execute(text("DELETE FROM stock_master"))
    session.commit()


class TestStockMasterTableStructure:
    """銘柄マスタテーブル構造のテスト."""

    def test_stock_master_table_exists(self, engine):
        """stock_master テーブルが存在することを確認."""
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        assert "stock_master" in tables, "stock_master テーブルが存在しません"

    def test_stock_master_updates_table_exists(self, engine):
        """stock_master_updates テーブルが存在することを確認."""
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        assert (
            "stock_master_updates" in tables
        ), "stock_master_updates テーブルが存在しません"

    def test_stock_master_columns(self, engine):
        """stock_master テーブルのカラムを検証."""
        inspector = inspect(engine)
        columns = {
            col["name"]: col for col in inspector.get_columns("stock_master")
        }

        expected_columns = [
            "id",
            "stock_code",
            "stock_name",
            "market_category",
            "sector_code_33",
            "sector_name_33",
            "sector_code_17",
            "sector_name_17",
            "scale_code",
            "scale_category",
            "data_date",
            "is_active",
            "created_at",
            "updated_at",
        ]

        for col_name in expected_columns:
            assert col_name in columns, f"カラム {col_name} が存在しません"

        # stock_code のユニーク制約を確認
        unique_constraints = inspector.get_unique_constraints("stock_master")
        stock_code_unique = any(
            "stock_code" in uc["column_names"] for uc in unique_constraints
        )
        assert (
            stock_code_unique
        ), "stock_code にユニーク制約が設定されていません"

    def test_stock_master_indexes(self, engine):
        """stock_master テーブルのインデックスを検証."""
        inspector = inspect(engine)
        indexes = {
            idx["name"]: idx for idx in inspector.get_indexes("stock_master")
        }

        expected_indexes = ["idx_stock_master_code", "idx_stock_master_active"]

        for idx_name in expected_indexes:
            assert (
                idx_name in indexes
            ), f"インデックス {idx_name} が存在しません"


class TestStockMasterCRUD:
    """StockMaster モデルのCRUD操作テスト."""

    def test_create_stock_master(self, session, clean_stock_master_tables):
        """銘柄マスタの作成テスト."""
        stock = StockMaster(
            stock_code="7203",
            stock_name="トヨタ自動車",
            market_category="プライム（内国株式）",
            sector_name_33="輸送用機器",
            sector_code_33="5050",
            is_active=1,
        )
        session.add(stock)
        session.commit()

        # 作成確認
        result = (
            session.query(StockMaster).filter_by(stock_code="7203").first()
        )
        assert result is not None
        assert result.stock_name == "トヨタ自動車"
        assert result.market_category == "プライム（内国株式）"
        assert result.sector_name_33 == "輸送用機器"
        assert result.is_active == 1

    def test_unique_stock_code_constraint(
        self, session, clean_stock_master_tables
    ):
        """銘柄コードのユニーク制約テスト."""
        stock1 = StockMaster(
            stock_code="7203", stock_name="トヨタ自動車", is_active=1
        )
        session.add(stock1)
        session.commit()

        # 同じ銘柄コードで2つ目を作成（エラーが発生するはず）
        stock2 = StockMaster(
            stock_code="7203", stock_name="重複銘柄", is_active=1
        )
        session.add(stock2)

        with pytest.raises(Exception):  # IntegrityError が発生
            session.commit()

        session.rollback()

    def test_update_stock_master(self, session, clean_stock_master_tables):
        """銘柄マスタの更新テスト."""
        stock = StockMaster(
            stock_code="7203", stock_name="トヨタ自動車", is_active=1
        )
        session.add(stock)
        session.commit()

        # 更新
        stock.stock_name = "トヨタ自動車株式会社"
        stock.market_category = "プライム"
        session.commit()

        # 更新確認
        result = (
            session.query(StockMaster).filter_by(stock_code="7203").first()
        )
        assert result.stock_name == "トヨタ自動車株式会社"
        assert result.market_category == "プライム"

    def test_deactivate_stock(self, session, clean_stock_master_tables):
        """銘柄の無効化テスト."""
        stock = StockMaster(
            stock_code="7203", stock_name="トヨタ自動車", is_active=1
        )
        session.add(stock)
        session.commit()

        # 無効化
        stock.is_active = 0
        session.commit()

        # 確認
        result = (
            session.query(StockMaster).filter_by(stock_code="7203").first()
        )
        assert result.is_active == 0

    def test_to_dict_method(self, session, clean_stock_master_tables):
        """to_dict メソッドのテスト."""
        stock = StockMaster(
            stock_code="7203",
            stock_name="トヨタ自動車",
            market_category="プライム（内国株式）",
            sector_name_33="輸送用機器",
            sector_code_33="5050",
            is_active=1,
        )
        session.add(stock)
        session.commit()

        stock_dict = stock.to_dict()

        assert stock_dict["stock_code"] == "7203"
        assert stock_dict["stock_name"] == "トヨタ自動車"
        assert stock_dict["market_category"] == "プライム（内国株式）"
        assert stock_dict["sector_name_33"] == "輸送用機器"
        assert stock_dict["is_active"] is True  # Integer から Boolean に変換
        assert "created_at" in stock_dict
        assert "updated_at" in stock_dict


class TestStockMasterUpdateCRUD:
    """StockMasterUpdate モデルのCRUD操作テスト."""

    def test_create_update_record(self, session, clean_stock_master_tables):
        """更新履歴レコードの作成テスト."""
        update_record = StockMasterUpdate(
            update_type="manual",
            total_stocks=3800,
            added_stocks=15,
            updated_stocks=120,
            removed_stocks=5,
            status="success",
        )
        session.add(update_record)
        session.commit()

        # 確認
        result = session.query(StockMasterUpdate).first()
        assert result is not None
        assert result.update_type == "manual"
        assert result.total_stocks == 3800
        assert result.added_stocks == 15
        assert result.updated_stocks == 120
        assert result.removed_stocks == 5
        assert result.status == "success"

    def test_failed_update_record(self, session, clean_stock_master_tables):
        """失敗した更新履歴レコードのテスト."""
        update_record = StockMasterUpdate(
            update_type="scheduled",
            total_stocks=0,
            status="failed",
            error_message="接続エラー: タイムアウト",
        )
        session.add(update_record)
        session.commit()

        # 確認
        result = session.query(StockMasterUpdate).first()
        assert result.status == "failed"
        assert result.error_message == "接続エラー: タイムアウト"

    def test_update_record_to_dict(self, session, clean_stock_master_tables):
        """更新履歴レコードの to_dict メソッドテスト."""
        update_record = StockMasterUpdate(
            update_type="manual",
            total_stocks=3800,
            added_stocks=15,
            updated_stocks=120,
            removed_stocks=5,
            status="success",
        )
        session.add(update_record)
        session.commit()

        record_dict = update_record.to_dict()

        assert record_dict["update_type"] == "manual"
        assert record_dict["total_stocks"] == 3800
        assert record_dict["added_stocks"] == 15
        assert record_dict["status"] == "success"
        assert "started_at" in record_dict


class TestStockMasterIntegration:
    """銘柄マスタの統合テスト."""

    def test_bulk_insert_and_query(self, session, clean_stock_master_tables):
        """一括登録とクエリのテスト."""
        stocks = [
            StockMaster(
                stock_code="7203",
                stock_name="トヨタ自動車",
                market_category="プライム",
                is_active=1,
            ),
            StockMaster(
                stock_code="6758",
                stock_name="ソニーグループ",
                market_category="プライム",
                is_active=1,
            ),
            StockMaster(
                stock_code="9984",
                stock_name="ソフトバンクグループ",
                market_category="プライム",
                is_active=1,
            ),
            StockMaster(
                stock_code="8306",
                stock_name="三菱UFJフィナンシャル・グループ",
                market_category="プライム",
                is_active=1,
            ),
            StockMaster(
                stock_code="9999",
                stock_name="上場廃止銘柄",
                market_category="",
                is_active=0,
            ),
        ]

        session.add_all(stocks)
        session.commit()

        # 全銘柄数確認
        total_count = session.query(StockMaster).count()
        assert total_count == 5

        # 有効な銘柄のみ取得
        active_stocks = session.query(StockMaster).filter_by(is_active=1).all()
        assert len(active_stocks) == 4

        # 無効な銘柄のみ取得
        inactive_stocks = (
            session.query(StockMaster).filter_by(is_active=0).all()
        )
        assert len(inactive_stocks) == 1
        assert inactive_stocks[0].stock_code == "9999"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
