"""
時間軸（足データ）対応 - データベーステーブル作成マイグレーション

このスクリプトは以下の8つの時間軸テーブルを作成します：
- stocks_1m (1分足)
- stocks_5m (5分足)
- stocks_15m (15分足)
- stocks_30m (30分足)
- stocks_1h (1時間足)
- stocks_1d (日足) - 既存のstocks_dailyから移行
- stocks_1wk (週足)
- stocks_1mo (月足)

実行方法:
python migrations/create_timeframe_tables.py
"""

import sys
import os
from pathlib import Path

# プロジェクトルートをパスに追加
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from sqlalchemy import create_engine, text, inspect
from sqlalchemy.exc import SQLAlchemyError
from app.models import Base, Stocks1m, Stocks5m, Stocks15m, Stocks30m, Stocks1h, Stocks1d, Stocks1wk, Stocks1mo
from dotenv import load_dotenv
import logging

# ログ設定
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# 環境変数読み込み
load_dotenv()

def get_database_url():
    """データベースURLを取得"""
    return f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"

def check_table_exists(engine, table_name):
    """テーブルの存在確認"""
    inspector = inspect(engine)
    return table_name in inspector.get_table_names()

def migrate_stocks_daily_to_stocks_1d(engine):
    """既存のstocks_dailyテーブルをstocks_1dに移行"""
    try:
        with engine.connect() as conn:
            # stocks_dailyテーブルが存在するかチェック
            if check_table_exists(engine, 'stocks_daily'):
                logger.info("stocks_dailyテーブルが存在します。stocks_1dへの移行を開始します。")
                
                # stocks_1dテーブルが存在しない場合のみ移行
                if not check_table_exists(engine, 'stocks_1d'):
                    # stocks_dailyをstocks_1dにリネーム
                    conn.execute(text("ALTER TABLE stocks_daily RENAME TO stocks_1d;"))
                    
                    # 制約名を更新
                    conn.execute(text("ALTER TABLE stocks_1d RENAME CONSTRAINT uk_stocks_daily_symbol_date TO uk_stocks_1d_symbol_date;"))
                    conn.execute(text("ALTER TABLE stocks_1d RENAME CONSTRAINT ck_stocks_daily_prices TO ck_stocks_1d_prices;"))
                    conn.execute(text("ALTER TABLE stocks_1d RENAME CONSTRAINT ck_stocks_daily_volume TO ck_stocks_1d_volume;"))
                    conn.execute(text("ALTER TABLE stocks_1d RENAME CONSTRAINT ck_stocks_daily_price_logic TO ck_stocks_1d_price_logic;"))
                    
                    # インデックス名を更新
                    conn.execute(text("ALTER INDEX idx_stocks_daily_symbol RENAME TO idx_stocks_1d_symbol;"))
                    conn.execute(text("ALTER INDEX idx_stocks_daily_date RENAME TO idx_stocks_1d_date;"))
                    conn.execute(text("ALTER INDEX idx_stocks_daily_symbol_date_desc RENAME TO idx_stocks_1d_symbol_date_desc;"))
                    
                    conn.commit()
                    logger.info("stocks_dailyテーブルをstocks_1dに正常に移行しました。")
                else:
                    logger.info("stocks_1dテーブルが既に存在します。移行をスキップします。")
            else:
                logger.info("stocks_dailyテーブルが存在しません。新規でstocks_1dテーブルを作成します。")
                
    except SQLAlchemyError as e:
        logger.error(f"stocks_dailyからstocks_1dへの移行中にエラーが発生しました: {str(e)}")
        raise

def create_timeframe_tables(engine):
    """時間軸テーブルを作成"""
    try:
        # 作成するテーブルのリスト
        tables_to_create = [
            ('stocks_1m', Stocks1m),
            ('stocks_5m', Stocks5m),
            ('stocks_15m', Stocks15m),
            ('stocks_30m', Stocks30m),
            ('stocks_1h', Stocks1h),
            ('stocks_1d', Stocks1d),
            ('stocks_1wk', Stocks1wk),
            ('stocks_1mo', Stocks1mo),
        ]
        
        for table_name, model_class in tables_to_create:
            if not check_table_exists(engine, table_name):
                logger.info(f"{table_name}テーブルを作成中...")
                model_class.__table__.create(engine)
                logger.info(f"{table_name}テーブルを正常に作成しました。")
            else:
                logger.info(f"{table_name}テーブルは既に存在します。スキップします。")
                
    except SQLAlchemyError as e:
        logger.error(f"テーブル作成中にエラーが発生しました: {str(e)}")
        raise

def verify_tables(engine):
    """作成されたテーブルの検証"""
    try:
        inspector = inspect(engine)
        existing_tables = inspector.get_table_names()
        
        expected_tables = [
            'stocks_1m', 'stocks_5m', 'stocks_15m', 'stocks_30m',
            'stocks_1h', 'stocks_1d', 'stocks_1wk', 'stocks_1mo'
        ]
        
        logger.info("テーブル作成結果の検証:")
        for table in expected_tables:
            if table in existing_tables:
                logger.info(f"✓ {table}テーブル: 作成済み")
                
                # インデックスの確認
                indexes = inspector.get_indexes(table)
                logger.info(f"  インデックス数: {len(indexes)}")
                
                # 制約の確認
                constraints = inspector.get_check_constraints(table)
                logger.info(f"  チェック制約数: {len(constraints)}")
                
            else:
                logger.error(f"✗ {table}テーブル: 作成されていません")
                
    except SQLAlchemyError as e:
        logger.error(f"テーブル検証中にエラーが発生しました: {str(e)}")
        raise

def main():
    """メイン実行関数"""
    try:
        logger.info("時間軸テーブル作成マイグレーションを開始します。")
        
        # データベース接続
        database_url = get_database_url()
        engine = create_engine(database_url)
        
        logger.info("データベースに接続しました。")
        
        # 1. 既存のstocks_dailyテーブルをstocks_1dに移行
        migrate_stocks_daily_to_stocks_1d(engine)
        
        # 2. 時間軸テーブルを作成
        create_timeframe_tables(engine)
        
        # 3. 作成されたテーブルの検証
        verify_tables(engine)
        
        logger.info("時間軸テーブル作成マイグレーションが正常に完了しました。")
        
    except Exception as e:
        logger.error(f"マイグレーション実行中にエラーが発生しました: {str(e)}")
        sys.exit(1)
    finally:
        if 'engine' in locals():
            engine.dispose()

if __name__ == "__main__":
    main()