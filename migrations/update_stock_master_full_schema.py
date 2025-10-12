"""
銘柄マスタテーブル更新マイグレーションスクリプト
JPXデータの全項目を格納可能な拡張版に更新

作成日: 2025-10-12
説明: 既存のstock_masterテーブルを削除し、全項目対応版で再作成

実行方法:
    python migrations/update_stock_master_full_schema.py
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


def update_stock_master_schema():
    """stock_masterテーブルを全項目対応版に更新"""

    print("=" * 80)
    print("銘柄マスタテーブル拡張マイグレーション開始")
    print("=" * 80)

    engine = create_engine(DATABASE_URL)

    try:
        with engine.begin() as conn:
            # 1. 既存テーブルの削除
            print("\n[1/3] 既存のstock_masterテーブルを削除中...")
            conn.execute(text("DROP TABLE IF EXISTS stock_master CASCADE"))
            print("✓ 既存テーブルを削除しました")

            # 2. 新しいテーブル作成
            print("\n[2/3] JPX全項目対応のstock_masterテーブルを作成中...")
            conn.execute(text("""
                CREATE TABLE stock_master (
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
            print("✓ 新しいテーブルを作成しました")

            # 3. インデックス作成
            print("\n[3/3] インデックスを作成中...")
            conn.execute(text("CREATE INDEX idx_stock_master_code ON stock_master(stock_code)"))
            conn.execute(text("CREATE INDEX idx_stock_master_active ON stock_master(is_active)"))
            conn.execute(text("CREATE INDEX idx_stock_master_market ON stock_master(market_category)"))
            conn.execute(text("CREATE INDEX idx_stock_master_sector_33 ON stock_master(sector_code_33)"))
            print("✓ インデックスを作成しました")

            # 4. テーブル構造確認
            print("\n[確認] テーブル構造を確認中...")
            result = conn.execute(text("""
                SELECT column_name, data_type, character_maximum_length
                FROM information_schema.columns
                WHERE table_schema = 'public'
                AND table_name = 'stock_master'
                ORDER BY ordinal_position
            """))

            print(f"{'カラム名':<25} {'データ型':<20} {'最大長':<10}")
            print("-" * 60)
            for row in result:
                max_len = row[2] if row[2] is not None else "-"
                print(f"{row[0]:<25} {row[1]:<20} {max_len:<10}")

        print("\n" + "=" * 80)
        print("✅ マイグレーション完了")
        print("=" * 80)
        print("\n📊 拡張されたカラム:")
        print("  - sector_code_33: 33業種コード")
        print("  - sector_name_33: 33業種区分")
        print("  - sector_code_17: 17業種コード")
        print("  - sector_name_17: 17業種区分")
        print("  - scale_code: 規模コード")
        print("  - scale_category: 規模区分（TOPIX分類）")
        print("  - data_date: データ取得日（YYYYMMDD形式）")

    except Exception as e:
        print("\n" + "=" * 80)
        print("❌ マイグレーション失敗")
        print("=" * 80)
        print(f"エラー: {e}")
        sys.exit(1)

    finally:
        engine.dispose()


if __name__ == "__main__":
    print("\n銘柄マスタテーブル拡張マイグレーション")
    print(f"データベース: {os.getenv('DB_NAME')}")
    print(f"ホスト: {os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}")
    print("\n⚠ 注意: 既存のstock_masterテーブルは削除されます")

    # マイグレーション実行
    update_stock_master_schema()

    print("\n✅ すべての処理が正常に完了しました")
