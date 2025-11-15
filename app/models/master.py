"""マスタデータモデル定義.

銘柄マスタと銘柄一覧更新履歴のモデルを定義します。
"""

from datetime import datetime
from typing import Any, Dict, Optional

from sqlalchemy import DateTime, Index, Integer, String
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from app.models.base import Base


# 銘柄マスタテーブル (Phase 2)
class StockMaster(Base):
    """銘柄マスタテーブル - JPX銘柄一覧を管理(全項目対応版).

    JPXから取得した銘柄一覧データを格納し、
    銘柄コード、銘柄名、市場区分、業種情報などを管理します。
    """

    __tablename__ = "stock_master"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True
    )

    # 基本情報
    stock_code: Mapped[str] = mapped_column(
        String(10), unique=True, nullable=False
    )  # 銘柄コード(例: "7203")
    stock_name: Mapped[str] = mapped_column(
        String(100), nullable=False
    )  # 銘柄名(例: "トヨタ自動車")
    market_category: Mapped[Optional[str]] = mapped_column(
        String(50)
    )  # 市場区分(例: "プライム(内国株式)")

    # 業種情報
    sector_code_33: Mapped[Optional[str]] = mapped_column(
        String(10)
    )  # 33業種コード
    sector_name_33: Mapped[Optional[str]] = mapped_column(
        String(100)
    )  # 33業種区分
    sector_code_17: Mapped[Optional[str]] = mapped_column(
        String(10)
    )  # 17業種コード
    sector_name_17: Mapped[Optional[str]] = mapped_column(
        String(100)
    )  # 17業種区分

    # 規模情報
    scale_code: Mapped[Optional[str]] = mapped_column(String(10))  # 規模コード
    scale_category: Mapped[Optional[str]] = mapped_column(
        String(50)
    )  # 規模区分(TOPIX分類)

    # データ管理
    data_date: Mapped[Optional[str]] = mapped_column(
        String(8)
    )  # データ取得日(YYYYMMDD形式)
    is_active: Mapped[Optional[int]] = mapped_column(
        Integer, default=1, nullable=False
    )  # 有効フラグ(1=有効, 0=無効)
    created_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    __table_args__ = (
        Index("idx_stock_master_code", "stock_code"),
        Index("idx_stock_master_active", "is_active"),
        Index("idx_stock_master_market", "market_category"),
        Index("idx_stock_master_sector_33", "sector_code_33"),
    )

    def __repr__(self):
        """オブジェクトの文字列表現を返す.

        Returns:
            str: オブジェクトの文字列表現
        """
        return (
            f"<StockMaster(stock_code='{self.stock_code}', "
            f"stock_name='{self.stock_name}', is_active={self.is_active})>"
        )

    def to_dict(self) -> Dict[str, Any]:
        """モデルインスタンスを辞書形式に変換.

        Returns:
            Dict[str, Any]: モデルの辞書表現
        """
        return {
            "id": self.id,
            "stock_code": self.stock_code,
            "stock_name": self.stock_name,
            "market_category": self.market_category,
            "sector_code_33": self.sector_code_33,
            "sector_name_33": self.sector_name_33,
            "sector_code_17": self.sector_code_17,
            "sector_name_17": self.sector_name_17,
            "scale_code": self.scale_code,
            "scale_category": self.scale_category,
            "data_date": self.data_date,
            "is_active": bool(self.is_active),
            "created_at": (
                self.created_at.isoformat() if self.created_at else None
            ),
            "updated_at": (
                self.updated_at.isoformat() if self.updated_at else None
            ),
        }


# 銘柄一覧更新履歴テーブル (Phase 2)
class StockMasterUpdate(Base):
    """銘柄一覧更新履歴テーブル - 銘柄マスタの更新履歴を管理.

    銘柄マスタテーブルの更新処理の履歴を記録し、
    更新タイプ、処理結果、統計情報などを管理します。
    """

    __tablename__ = "stock_master_updates"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True
    )
    update_type: Mapped[str] = mapped_column(
        String(20), nullable=False
    )  # 'manual', 'scheduled'
    total_stocks: Mapped[int] = mapped_column(Integer, nullable=False)  # 総銘柄数
    added_stocks: Mapped[Optional[int]] = mapped_column(
        Integer, default=0
    )  # 新規追加銘柄数
    updated_stocks: Mapped[Optional[int]] = mapped_column(
        Integer, default=0
    )  # 更新銘柄数
    removed_stocks: Mapped[Optional[int]] = mapped_column(
        Integer, default=0
    )  # 削除(無効化)銘柄数
    status: Mapped[str] = mapped_column(
        String(20), nullable=False
    )  # 'success', 'failed'
    error_message: Mapped[Optional[str]] = mapped_column(String)  # エラーメッセージ
    started_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    completed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True)
    )

    def __repr__(self):
        """オブジェクトの文字列表現を返す.

        Returns:
            str: オブジェクトの文字列表現
        """
        return (
            f"<StockMasterUpdate(id={self.id}, "
            f"update_type='{self.update_type}', status='{self.status}')>"
        )

    def to_dict(self) -> Dict[str, Any]:
        """モデルインスタンスを辞書形式に変換.

        Returns:
            Dict[str, Any]: モデルの辞書表現
        """
        return {
            "id": self.id,
            "update_type": self.update_type,
            "total_stocks": self.total_stocks,
            "added_stocks": self.added_stocks,
            "updated_stocks": self.updated_stocks,
            "removed_stocks": self.removed_stocks,
            "status": self.status,
            "error_message": self.error_message,
            "started_at": (
                self.started_at.isoformat() if self.started_at else None
            ),
            "completed_at": (
                self.completed_at.isoformat() if self.completed_at else None
            ),
        }


__all__ = [
    "StockMaster",
    "StockMasterUpdate",
]
