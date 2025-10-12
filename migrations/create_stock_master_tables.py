"""
銘柄マスタテーブル作成マイグレーションスクリプト (Phase 2)

作成日: 2025-10-12
説明: JPX銘柄一覧を管理する銘柄マスタテーブルと更新履歴テーブルを作成

実行方法:
    python migrations/create_stock_master_tables.py
"""

import sys
import os
from pathlib import Path

# UTF-8エンコーディング設定
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# プロジェクトルートをPythonパスに追加
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# 環境変数を読み込み
load_dotenv()

# データベース接続情報
DATABASE_URL = f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"


def create_stock_master_tables():
    """銘柄マスタテーブルと更新履歴テーブルを作成"""

    print("=" * 80)
    print("銘柄マスタテーブル作成マイグレーション開始")
    print("=" * 80)

    engine = create_engine(DATABASE_URL)

    try:
        with engine.begin() as conn:
            # 1. stock_master テーブル作成（JPX全項目対応版）
            print("\n[1/4] stock_master テーブルを作成中...")
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS stock_master (
                    id SERIAL PRIMARY KEY,

                    -- 基本情報
                    stock_code VARCHAR(10) UNIQUE NOT NULL,
                    stock_name VARCHAR(100) NOT NULL,
                    market_category VARCHAR(50),

                    -- 業種情報
                    sector_code_33 VARCHAR(10),
                    sector_name_33 VARCHAR(100),
                    sector_code_17 VARCHAR(10),
                    sector_name_17 VARCHAR(100),

                    -- 規模情報
                    scale_code VARCHAR(10),
                    scale_category VARCHAR(50),

                    -- データ管理
                    data_date VARCHAR(8),
                    is_active INTEGER DEFAULT 1 NOT NULL,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                )
            """))
            print("✓ stock_master テーブルを作成しました（JPX全項目対応版）")

            # 2. stock_master インデックス作成
            print("\n[2/4] stock_master インデックスを作成中...")
            conn.execute(text("CREATE INDEX IF NOT EXISTS idx_stock_master_code ON stock_master(stock_code)"))
            conn.execute(text("CREATE INDEX IF NOT EXISTS idx_stock_master_active ON stock_master(is_active)"))
            conn.execute(text("CREATE INDEX IF NOT EXISTS idx_stock_master_market ON stock_master(market_category)"))
            conn.execute(text("CREATE INDEX IF NOT EXISTS idx_stock_master_sector_33 ON stock_master(sector_code_33)"))
            print("✓ stock_master インデックスを作成しました")

            # 3. stock_master_updates テーブル作成
            print("\n[3/4] stock_master_updates テーブルを作成中...")
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS stock_master_updates (
                    id SERIAL PRIMARY KEY,
                    update_type VARCHAR(20) NOT NULL,
                    total_stocks INTEGER NOT NULL,
                    added_stocks INTEGER DEFAULT 0,
                    updated_stocks INTEGER DEFAULT 0,
                    removed_stocks INTEGER DEFAULT 0,
                    status VARCHAR(20) NOT NULL,
                    error_message TEXT,
                    started_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                    completed_at TIMESTAMP WITH TIME ZONE
                )
            """))
            print("✓ stock_master_updates テーブルを作成しました")

            # 4. テーブル作成確認
            print("\n[4/4] テーブル作成を確認中...")
            result = conn.execute(text("""
                SELECT table_name
                FROM information_schema.tables
                WHERE table_schema = 'public'
                AND table_name IN ('stock_master', 'stock_master_updates')
                ORDER BY table_name
            """))

            created_tables = [row[0] for row in result]
            print(f"✓ 作成されたテーブル: {', '.join(created_tables)}")

            # インデックス確認
            print("\n[確認] インデックスを確認中...")
            result = conn.execute(text("""
                SELECT tablename, indexname
                FROM pg_indexes
                WHERE schemaname = 'public'
                AND tablename IN ('stock_master', 'stock_master_updates')
                ORDER BY tablename, indexname
            """))

            for row in result:
                print(f"  - {row[0]}.{row[1]}")

        print("\n" + "=" * 80)
        print("✅ マイグレーション完了")
        print("=" * 80)

    except Exception as e:
        print("\n" + "=" * 80)
        print("❌ マイグレーション失敗")
        print("=" * 80)
        print(f"エラー: {e}")
        sys.exit(1)

    finally:
        engine.dispose()


def verify_tables():
    """テーブル構造を検証"""

    print("\n" + "=" * 80)
    print("テーブル構造検証")
    print("=" * 80)

    engine = create_engine(DATABASE_URL)

    try:
        with engine.begin() as conn:
            # stock_master のカラム確認
            print("\n[stock_master テーブル構造]")
            result = conn.execute(text("""
                SELECT column_name, data_type, is_nullable, column_default
                FROM information_schema.columns
                WHERE table_schema = 'public'
                AND table_name = 'stock_master'
                ORDER BY ordinal_position
            """))

            print(f"{'カラム名':<20} {'データ型':<20} {'NULL許可':<10} {'デフォルト値':<30}")
            print("-" * 80)
            for row in result:
                print(f"{row[0]:<20} {row[1]:<20} {row[2]:<10} {str(row[3])[:30]:<30}")

            # stock_master_updates のカラム確認
            print("\n[stock_master_updates テーブル構造]")
            result = conn.execute(text("""
                SELECT column_name, data_type, is_nullable, column_default
                FROM information_schema.columns
                WHERE table_schema = 'public'
                AND table_name = 'stock_master_updates'
                ORDER BY ordinal_position
            """))

            print(f"{'カラム名':<20} {'データ型':<20} {'NULL許可':<10} {'デフォルト値':<30}")
            print("-" * 80)
            for row in result:
                print(f"{row[0]:<20} {row[1]:<20} {row[2]:<10} {str(row[3])[:30]:<30}")

        print("\n✅ 検証完了")

    except Exception as e:
        print(f"\n❌ 検証失敗: {e}")
        sys.exit(1)

    finally:
        engine.dispose()


if __name__ == "__main__":
    print("\n銘柄マスタテーブル作成マイグレーション")
    print(f"データベース: {os.getenv('DB_NAME')}")
    print(f"ホスト: {os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}")

    # マイグレーション実行
    create_stock_master_tables()

    # テーブル構造検証
    verify_tables()

    print("\n✅ すべての処理が正常に完了しました")
