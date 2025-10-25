"""Phase 2バッチ実行テーブル作成マイグレーション.

バッチ実行情報とバッチ実行詳細のテーブルを作成します。
Phase 1からPhase 2への移行実装（Issue #85）に対応。

参照仕様書: docs/api_bulk_fetch.md (Phase 2データ構造)
"""

from contextlib import contextmanager
import logging
import os
from pathlib import Path
import sys

from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker


# プロジェクトルートをパスに追加
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "app"))


# .envを読み込み
load_dotenv()

# データベース接続設定
DATABASE_URL = f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@contextmanager
def get_db_session():
    """データベースセッションのコンテキストマネージャー."""
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


logger = logging.getLogger(__name__)


def upgrade():
    """batch_executionsとbatch_execution_detailsテーブルを作成."""
    logger.info("Phase 2バッチ実行テーブルの作成を開始します...")

    try:
        with get_db_session() as session:
            # テーブルが既に存在するか確認
            check_batch_executions = text(
                """
                SELECT EXISTS (
                    SELECT FROM information_schema.tables
                    WHERE table_name = 'batch_executions'
                )
            """
            )

            check_batch_execution_details = text(
                """
                SELECT EXISTS (
                    SELECT FROM information_schema.tables
                    WHERE table_name = 'batch_execution_details'
                )
            """
            )

            batch_executions_exists = session.execute(
                check_batch_executions
            ).scalar()
            batch_execution_details_exists = session.execute(
                check_batch_execution_details
            ).scalar()

            if batch_executions_exists and batch_execution_details_exists:
                logger.info(
                    "batch_executionsとbatch_execution_detailsテーブルは既に存在します。"
                )
                return

            # batch_executionsテーブル作成
            if not batch_executions_exists:
                logger.info("batch_executionsテーブルを作成中...")
                create_batch_executions = text(
                    """
                    CREATE TABLE batch_executions (
                        id SERIAL PRIMARY KEY,
                        batch_type VARCHAR(50) NOT NULL,
                        status VARCHAR(20) NOT NULL,
                        total_stocks INTEGER NOT NULL,
                        processed_stocks INTEGER DEFAULT 0,
                        successful_stocks INTEGER DEFAULT 0,
                        failed_stocks INTEGER DEFAULT 0,
                        start_time TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                        end_time TIMESTAMP WITH TIME ZONE,
                        error_message TEXT,
                        created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                    )
                """
                )
                session.execute(create_batch_executions)

                # インデックス作成
                session.execute(
                    text(
                        "CREATE INDEX idx_batch_executions_status ON batch_executions(status)"
                    )
                )
                session.execute(
                    text(
                        "CREATE INDEX idx_batch_executions_batch_type ON batch_executions(batch_type)"
                    )
                )
                session.execute(
                    text(
                        "CREATE INDEX idx_batch_executions_start_time ON batch_executions(start_time)"
                    )
                )
                logger.info("batch_executionsテーブルの作成が完了しました。")

            # batch_execution_detailsテーブル作成
            if not batch_execution_details_exists:
                logger.info("batch_execution_detailsテーブルを作成中...")
                create_batch_execution_details = text(
                    """
                    CREATE TABLE batch_execution_details (
                        id SERIAL PRIMARY KEY,
                        batch_execution_id INTEGER NOT NULL,
                        stock_code VARCHAR(10) NOT NULL,
                        status VARCHAR(20) NOT NULL,
                        start_time TIMESTAMP WITH TIME ZONE,
                        end_time TIMESTAMP WITH TIME ZONE,
                        error_message TEXT,
                        records_inserted INTEGER DEFAULT 0,
                        created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (batch_execution_id) REFERENCES batch_executions(id) ON DELETE CASCADE
                    )
                """
                )
                session.execute(create_batch_execution_details)

                # インデックス作成
                session.execute(
                    text(
                        "CREATE INDEX idx_batch_execution_details_batch_id ON batch_execution_details(batch_execution_id)"
                    )
                )
                session.execute(
                    text(
                        "CREATE INDEX idx_batch_execution_details_status ON batch_execution_details(status)"
                    )
                )
                session.execute(
                    text(
                        "CREATE INDEX idx_batch_execution_details_stock_code ON batch_execution_details(stock_code)"
                    )
                )
                session.execute(
                    text(
                        "CREATE INDEX idx_batch_execution_details_batch_stock ON batch_execution_details(batch_execution_id, stock_code)"
                    )
                )
                logger.info(
                    "batch_execution_detailsテーブルの作成が完了しました。"
                )

            logger.info("Phase 2バッチ実行テーブルの作成が完了しました。")

    except Exception as e:
        logger.error(f"マイグレーションエラー: {e}")
        raise


def downgrade():
    """batch_executionsとbatch_execution_detailsテーブルを削除."""
    logger.info("Phase 2バッチ実行テーブルの削除を開始します...")

    try:
        with get_db_session() as session:
            # テーブルを削除（外部キー制約のため、詳細テーブルから削除）
            session.execute(
                text("DROP TABLE IF EXISTS batch_execution_details CASCADE")
            )
            logger.info("batch_execution_detailsテーブルを削除しました。")

            session.execute(
                text("DROP TABLE IF EXISTS batch_executions CASCADE")
            )
            logger.info("batch_executionsテーブルを削除しました。")

            logger.info("Phase 2バッチ実行テーブルの削除が完了しました。")

    except Exception as e:
        logger.error(f"マイグレーションのダウングレードエラー: {e}")
        raise


if __name__ == "__main__":
    import sys

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    if len(sys.argv) < 2:
        print(
            "使用法: python create_batch_execution_tables.py [upgrade|downgrade]"
        )
        sys.exit(1)

    command = sys.argv[1].lower()

    if command == "upgrade":
        upgrade()
    elif command == "downgrade":
        downgrade()
    else:
        print(f"不明なコマンド: {command}")
        print(
            "使用法: python create_batch_execution_tables.py [upgrade|downgrade]"
        )
        sys.exit(1)
