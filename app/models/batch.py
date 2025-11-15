"""バッチ実行管理モデル定義.

バッチ実行情報と詳細のモデルを定義します。
"""

from datetime import datetime
from typing import Any, Dict, Optional

from sqlalchemy import DateTime, Index, Integer, String
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from app.models.base import Base


# バッチ実行情報テーブル (Phase 2)
class BatchExecution(Base):
    """バッチ実行情報テーブル - バッチ処理の実行状況を管理.

    株価データ取得バッチの実行状況を記録し、
    処理進捗、成功・失敗統計、実行時間などを管理します。
    """

    __tablename__ = "batch_executions"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True
    )
    batch_type: Mapped[str] = mapped_column(
        String(50), nullable=False
    )  # 'all_stocks', 'partial', etc.
    status: Mapped[str] = mapped_column(
        String(20), nullable=False
    )  # 'running', 'completed', 'failed', 'paused'
    total_stocks: Mapped[int] = mapped_column(Integer, nullable=False)  # 総銘柄数
    processed_stocks: Mapped[Optional[int]] = mapped_column(
        Integer, default=0
    )  # 処理済み銘柄数
    successful_stocks: Mapped[Optional[int]] = mapped_column(
        Integer, default=0
    )  # 成功銘柄数
    failed_stocks: Mapped[Optional[int]] = mapped_column(
        Integer, default=0
    )  # 失敗銘柄数
    start_time: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    end_time: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True)
    )
    error_message: Mapped[Optional[str]] = mapped_column(String)  # エラーメッセージ
    created_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    __table_args__ = (
        Index("idx_batch_executions_status", "status"),
        Index("idx_batch_executions_batch_type", "batch_type"),
        Index("idx_batch_executions_start_time", "start_time"),
    )

    def __repr__(self):
        """オブジェクトの文字列表現を返す.

        Returns:
            str: オブジェクトの文字列表現
        """
        return (
            f"<BatchExecution(id={self.id}, batch_type='{self.batch_type}', "
            f"status='{self.status}')>"
        )

    def to_dict(self) -> Dict[str, Any]:
        """モデルインスタンスを辞書形式に変換.

        Returns:
            Dict[str, Any]: モデルの辞書表現
        """
        return {
            "id": self.id,
            "batch_type": self.batch_type,
            "status": self.status,
            "total_stocks": self.total_stocks,
            "processed_stocks": self.processed_stocks,
            "successful_stocks": self.successful_stocks,
            "failed_stocks": self.failed_stocks,
            "start_time": (
                self.start_time.isoformat() if self.start_time else None
            ),
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "error_message": self.error_message,
            "created_at": (
                self.created_at.isoformat() if self.created_at else None
            ),
        }

    @property
    def progress_percentage(self) -> float:
        """進捗率を計算.

        Returns:
            float: 進捗率(0.0-100.0)
        """
        if self.total_stocks == 0:
            return 0.0
        processed = self.processed_stocks or 0
        return (processed / self.total_stocks) * 100.0

    @property
    def duration_seconds(self) -> Optional[float]:
        """実行時間を秒で計算.

        Returns:
            Optional[float]: 実行時間(秒)、開始時間が未設定の場合はNone
        """
        if not self.start_time:
            return None
        end_time = self.end_time or datetime.now(self.start_time.tzinfo)
        return (end_time - self.start_time).total_seconds()


# バッチ実行詳細テーブル (Phase 2)
class BatchExecutionDetail(Base):
    """バッチ実行詳細テーブル - 個別銘柄の処理状況を管理.

    バッチ処理における個別銘柄の処理状況を記録し、
    処理ステータス、実行時間、エラー情報などを管理します。
    """

    __tablename__ = "batch_execution_details"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True
    )
    batch_execution_id: Mapped[int] = mapped_column(
        Integer, nullable=False
    )  # batch_executionsテーブルへの外部キー
    stock_code: Mapped[str] = mapped_column(
        String(10), nullable=False
    )  # 銘柄コード
    status: Mapped[str] = mapped_column(
        String(20), nullable=False
    )  # 'pending', 'processing', 'completed', 'failed'
    start_time: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True)
    )
    end_time: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True)
    )
    error_message: Mapped[Optional[str]] = mapped_column(String)  # エラーメッセージ
    records_inserted: Mapped[Optional[int]] = mapped_column(
        Integer, default=0
    )  # 挿入されたレコード数
    created_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    __table_args__ = (
        Index("idx_batch_execution_details_batch_id", "batch_execution_id"),
        Index("idx_batch_execution_details_status", "status"),
        Index("idx_batch_execution_details_stock_code", "stock_code"),
        Index(
            "idx_batch_execution_details_batch_stock",
            "batch_execution_id",
            "stock_code",
        ),
    )

    def __repr__(self):
        """オブジェクトの文字列表現を返す.

        Returns:
            str: オブジェクトの文字列表現
        """
        return (
            f"<BatchExecutionDetail(id={self.id}, "
            f"batch_execution_id={self.batch_execution_id}, "
            f"stock_code='{self.stock_code}', status='{self.status}')>"
        )

    def to_dict(self) -> Dict[str, Any]:
        """モデルインスタンスを辞書形式に変換.

        Returns:
            Dict[str, Any]: モデルの辞書表現
        """
        return {
            "id": self.id,
            "batch_execution_id": self.batch_execution_id,
            "stock_code": self.stock_code,
            "status": self.status,
            "start_time": (
                self.start_time.isoformat() if self.start_time else None
            ),
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "error_message": self.error_message,
            "records_inserted": self.records_inserted,
            "created_at": (
                self.created_at.isoformat() if self.created_at else None
            ),
        }

    @property
    def duration_seconds(self) -> Optional[float]:
        """処理時間を秒で計算.

        Returns:
            Optional[float]: 処理時間(秒)、開始時間が未設定の場合はNone
        """
        if not self.start_time:
            return None
        end_time = self.end_time or datetime.now(self.start_time.tzinfo)
        return (end_time - self.start_time).total_seconds()


__all__ = [
    "BatchExecution",
    "BatchExecutionDetail",
]
