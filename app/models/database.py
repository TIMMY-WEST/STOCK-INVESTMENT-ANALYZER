"""データベース接続とセッション管理."""

from contextlib import contextmanager
import os

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


load_dotenv()

# データベース設定
DATABASE_URL = (
    f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}"
    f"@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
)

# コネクションプール設定
# - pool_size: 通常時に保持する接続数(デフォルト5→10に変更)
# - max_overflow: pool_sizeを超えて作成可能な追加接続数
# - pool_pre_ping: 接続を使用前にpingして有効性を確認(接続切れ防止)
# - pool_recycle: 接続を再利用する最大秒数(-1=無制限、3600=1時間)
# - pool_timeout: 接続取得時の最大待機秒数
engine = create_engine(
    DATABASE_URL,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True,
    pool_recycle=3600,
    pool_timeout=30,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@contextmanager
def get_db_session():
    """データベースセッションのコンテキストマネージャー.

    データベースセッションを安全に管理し、
    自動的にコミット・ロールバック・クローズを行います。

    Yields:
        Session: SQLAlchemyセッション
    """
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


__all__ = [
    "DATABASE_URL",
    "engine",
    "SessionLocal",
    "get_db_session",
]
