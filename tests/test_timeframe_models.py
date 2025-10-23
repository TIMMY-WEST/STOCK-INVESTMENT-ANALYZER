"""
時間軸（足データ）対応 - モデルテスト.

このテストファイルは以下をテストします：
- 8つの時間軸テーブルのモデル作成
- データ挿入・取得
- 制約の動作確認
- インデックスの効果確認
- パフォーマンステスト。
"""

from datetime import date, datetime, timedelta
from decimal import Decimal
import os
from pathlib import Path
import sys

import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import sessionmaker


# プロジェクトルートをパスに追加
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.models import (
    Base,
    Stocks1d,
    Stocks1h,
    Stocks1m,
    Stocks1mo,
    Stocks1wk,
    Stocks5m,
    Stocks15m,
    Stocks30m,
)


# テスト用データベース設定
TEST_DATABASE_URL = "sqlite:///test_timeframe.db"


@pytest.fixture(scope="module")
def engine():
    """テスト用データベースエンジン."""
    engine = create_engine(TEST_DATABASE_URL, echo=False)
    Base.metadata.create_all(engine)
    yield engine
    Base.metadata.drop_all(engine)
    engine.dispose()  # エンジンを明示的に閉じる

    # テストファイルを削除（エラーハンドリング付き）
    import time

    db_file = "test_timeframe.db"
    if os.path.exists(db_file):
        try:
            # 少し待ってからファイル削除を試行
            time.sleep(0.1)
            os.remove(db_file)
        except PermissionError:
            # Windowsでファイルが使用中の場合は警告のみ出力
            import warnings

            warnings.warn(
                f"テストデータベースファイル {db_file} を削除できませんでした。手動で削除してください。"
            )


@pytest.fixture(scope="function")
def session(engine):
    """テスト用セッション."""
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.rollback()
    # 全テーブルのデータをクリア
    for table in reversed(Base.metadata.sorted_tables):
        session.execute(table.delete())
    session.commit()
    session.close()


class TestTimeframeModels:
    """時間軸モデルのテストクラス."""

    def test_stocks_1m_model(self, session):
        """1分足モデルのテスト."""
        # テストデータ作成
        stock_data = Stocks1m(
            symbol="AAPL",
            datetime=datetime(2024, 1, 1, 9, 30, 0),
            open=Decimal("150.00"),
            high=Decimal("151.00"),
            low=Decimal("149.50"),
            close=Decimal("150.75"),
            volume=1000000,
        )

        # データ挿入
        session.add(stock_data)
        session.commit()

        # データ取得確認
        retrieved = session.query(Stocks1m).filter_by(symbol="AAPL").first()
        assert retrieved is not None
        assert retrieved.symbol == "AAPL"
        assert retrieved.close == Decimal("150.75")
        assert retrieved.volume == 1000000

    def test_stocks_5m_model(self, session):
        """5分足モデルのテスト."""
        stock_data = Stocks5m(
            symbol="GOOGL",
            datetime=datetime(2024, 1, 1, 9, 35, 0),
            open=Decimal("2800.00"),
            high=Decimal("2810.00"),
            low=Decimal("2795.00"),
            close=Decimal("2805.50"),
            volume=500000,
        )

        session.add(stock_data)
        session.commit()

        retrieved = session.query(Stocks5m).filter_by(symbol="GOOGL").first()
        assert retrieved is not None
        assert retrieved.symbol == "GOOGL"
        assert retrieved.close == Decimal("2805.50")

    def test_stocks_15m_model(self, session):
        """15分足モデルのテスト."""
        stock_data = Stocks15m(
            symbol="MSFT",
            datetime=datetime(2024, 1, 1, 9, 45, 0),
            open=Decimal("380.00"),
            high=Decimal("382.00"),
            low=Decimal("379.00"),
            close=Decimal("381.25"),
            volume=750000,
        )

        session.add(stock_data)
        session.commit()

        retrieved = session.query(Stocks15m).filter_by(symbol="MSFT").first()
        assert retrieved is not None
        assert retrieved.symbol == "MSFT"
        assert retrieved.close == Decimal("381.25")

    def test_stocks_30m_model(self, session):
        """30分足モデルのテスト."""
        stock_data = Stocks30m(
            symbol="TSLA",
            datetime=datetime(2024, 1, 1, 10, 0, 0),
            open=Decimal("250.00"),
            high=Decimal("255.00"),
            low=Decimal("248.00"),
            close=Decimal("252.75"),
            volume=2000000,
        )

        session.add(stock_data)
        session.commit()

        retrieved = session.query(Stocks30m).filter_by(symbol="TSLA").first()
        assert retrieved is not None
        assert retrieved.symbol == "TSLA"
        assert retrieved.close == Decimal("252.75")

    def test_stocks_1h_model(self, session):
        """1時間足モデルのテスト."""
        stock_data = Stocks1h(
            symbol="NVDA",
            datetime=datetime(2024, 1, 1, 10, 0, 0),
            open=Decimal("500.00"),
            high=Decimal("510.00"),
            low=Decimal("495.00"),
            close=Decimal("505.25"),
            volume=1500000,
        )

        session.add(stock_data)
        session.commit()

        retrieved = session.query(Stocks1h).filter_by(symbol="NVDA").first()
        assert retrieved is not None
        assert retrieved.symbol == "NVDA"
        assert retrieved.close == Decimal("505.25")

    def test_stocks_1d_model(self, session):
        """日足モデルのテスト."""
        stock_data = Stocks1d(
            symbol="AMZN",
            date=date(2024, 1, 1),
            open=Decimal("3200.00"),
            high=Decimal("3250.00"),
            low=Decimal("3180.00"),
            close=Decimal("3225.75"),
            volume=5000000,
        )

        session.add(stock_data)
        session.commit()

        retrieved = session.query(Stocks1d).filter_by(symbol="AMZN").first()
        assert retrieved is not None
        assert retrieved.symbol == "AMZN"
        assert retrieved.close == Decimal("3225.75")

    def test_stocks_1wk_model(self, session):
        """週足モデルのテスト."""
        stock_data = Stocks1wk(
            symbol="META",
            date=date(2024, 1, 1),
            open=Decimal("350.00"),
            high=Decimal("365.00"),
            low=Decimal("345.00"),
            close=Decimal("360.50"),
            volume=10000000,
        )

        session.add(stock_data)
        session.commit()

        retrieved = session.query(Stocks1wk).filter_by(symbol="META").first()
        assert retrieved is not None
        assert retrieved.symbol == "META"
        assert retrieved.close == Decimal("360.50")

    def test_stocks_1mo_model(self, session):
        """月足モデルのテスト."""
        stock_data = Stocks1mo(
            symbol="NFLX",
            date=date(2024, 1, 1),
            open=Decimal("450.00"),
            high=Decimal("480.00"),
            low=Decimal("440.00"),
            close=Decimal("470.25"),
            volume=20000000,
        )

        session.add(stock_data)
        session.commit()

        retrieved = session.query(Stocks1mo).filter_by(symbol="NFLX").first()
        assert retrieved is not None
        assert retrieved.symbol == "NFLX"
        assert retrieved.close == Decimal("470.25")


class TestConstraints:
    """制約のテストクラス."""

    def test_unique_constraint_datetime(self, session):
        """datetime系テーブルのユニーク制約テスト."""
        # 同じsymbolとdatetimeのデータを2回挿入
        stock1 = Stocks1m(
            symbol="AAPL",
            datetime=datetime(2024, 1, 1, 9, 30, 0),
            open=Decimal("150.00"),
            high=Decimal("151.00"),
            low=Decimal("149.50"),
            close=Decimal("150.75"),
            volume=1000000,
        )

        stock2 = Stocks1m(
            symbol="AAPL",
            datetime=datetime(2024, 1, 1, 9, 30, 0),  # 同じdatetime
            open=Decimal("151.00"),
            high=Decimal("152.00"),
            low=Decimal("150.50"),
            close=Decimal("151.75"),
            volume=1100000,
        )

        session.add(stock1)
        session.commit()

        session.add(stock2)
        with pytest.raises(IntegrityError):
            session.commit()

    def test_unique_constraint_date(self, session):
        """date系テーブルのユニーク制約テスト."""
        # 同じsymbolとdateのデータを2回挿入
        stock1 = Stocks1d(
            symbol="AAPL",
            date=date(2024, 1, 1),
            open=Decimal("150.00"),
            high=Decimal("151.00"),
            low=Decimal("149.50"),
            close=Decimal("150.75"),
            volume=1000000,
        )

        stock2 = Stocks1d(
            symbol="AAPL",
            date=date(2024, 1, 1),  # 同じdate
            open=Decimal("151.00"),
            high=Decimal("152.00"),
            low=Decimal("150.50"),
            close=Decimal("151.75"),
            volume=1100000,
        )

        session.add(stock1)
        session.commit()

        session.add(stock2)
        with pytest.raises(IntegrityError):
            session.commit()

    def test_price_check_constraints(self, session):
        """価格チェック制約のテスト."""
        # 負の価格でテスト
        with pytest.raises(IntegrityError):
            stock = Stocks1d(
                symbol="AAPL",
                date=date(2024, 1, 1),
                open=Decimal("-150.00"),  # 負の値
                high=Decimal("151.00"),
                low=Decimal("149.50"),
                close=Decimal("150.75"),
                volume=1000000,
            )
            session.add(stock)
            session.commit()

    def test_volume_check_constraint(self, session):
        """ボリュームチェック制約のテスト."""
        # 負のボリュームでテスト
        with pytest.raises(IntegrityError):
            stock = Stocks1d(
                symbol="AAPL",
                date=date(2024, 1, 1),
                open=Decimal("150.00"),
                high=Decimal("151.00"),
                low=Decimal("149.50"),
                close=Decimal("150.75"),
                volume=-1000000,  # 負の値
            )
            session.add(stock)
            session.commit()


class TestToDict:
    """to_dictメソッドのテストクラス."""

    def test_stocks_1m_to_dict(self, session):
        """1分足のto_dictテスト."""
        stock_data = Stocks1m(
            symbol="AAPL",
            datetime=datetime(2024, 1, 1, 9, 30, 0),
            open=Decimal("150.00"),
            high=Decimal("151.00"),
            low=Decimal("149.50"),
            close=Decimal("150.75"),
            volume=1000000,
        )

        session.add(stock_data)
        session.commit()

        result_dict = stock_data.to_dict()

        assert result_dict["symbol"] == "AAPL"
        assert result_dict["open"] == 150.00
        assert result_dict["high"] == 151.00
        assert result_dict["low"] == 149.50
        assert result_dict["close"] == 150.75
        assert result_dict["volume"] == 1000000
        assert "datetime" in result_dict
        assert "created_at" in result_dict
        assert "updated_at" in result_dict

    def test_stocks_1d_to_dict(self, session):
        """日足のto_dictテスト."""
        stock_data = Stocks1d(
            symbol="AAPL",
            date=date(2024, 1, 1),
            open=Decimal("150.00"),
            high=Decimal("151.00"),
            low=Decimal("149.50"),
            close=Decimal("150.75"),
            volume=1000000,
        )

        session.add(stock_data)
        session.commit()

        result_dict = stock_data.to_dict()

        assert result_dict["symbol"] == "AAPL"
        assert result_dict["open"] == 150.00
        assert result_dict["high"] == 151.00
        assert result_dict["low"] == 149.50
        assert result_dict["close"] == 150.75
        assert result_dict["volume"] == 1000000
        assert "date" in result_dict
        assert "created_at" in result_dict
        assert "updated_at" in result_dict


class TestPerformance:
    """パフォーマンステストクラス."""

    def test_bulk_insert_performance(self, session):
        """大量データ挿入のパフォーマンステスト."""
        import time

        # 1000件のテストデータを作成
        test_data = []
        base_datetime = datetime(2024, 1, 1, 9, 30, 0)

        for i in range(1000):
            stock_data = Stocks1m(
                symbol=f"TEST{i % 10}",  # 10種類のシンボル
                datetime=base_datetime + timedelta(minutes=i),
                open=Decimal("150.00") + Decimal(str(i * 0.01)),
                high=Decimal("151.00") + Decimal(str(i * 0.01)),
                low=Decimal("149.50") + Decimal(str(i * 0.01)),
                close=Decimal("150.75") + Decimal(str(i * 0.01)),
                volume=1000000 + i * 1000,
            )
            test_data.append(stock_data)

        # 挿入時間を測定
        start_time = time.time()
        session.add_all(test_data)
        session.commit()
        end_time = time.time()

        insert_time = end_time - start_time
        print(f"1000件の挿入時間: {insert_time:.3f}秒")

        # 挿入されたデータ数を確認
        count = session.query(Stocks1m).count()
        assert count >= 1000  # 他のテストからのデータも含む可能性があるため

        # 検索パフォーマンステスト
        start_time = time.time()
        results = session.query(Stocks1m).filter_by(symbol="TEST0").all()
        end_time = time.time()

        search_time = end_time - start_time
        print(f"シンボル検索時間: {search_time:.3f}秒")

        assert len(results) >= 100  # TEST0は100件以上


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
