"""SQLAlchemyのベースクラスと株価データ共通クラス."""

from datetime import datetime
from decimal import Decimal
import math
from typing import Any, Dict, Optional

from sqlalchemy import BigInteger, DateTime, Integer, Numeric, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.sql import func


class Base(DeclarativeBase):
    """全てのモデルクラスの基底クラス."""

    pass


class StockDataBase:
    """株価データの共通カラムと制約を定義するベースクラス.

    全ての株価データテーブルで共通して使用されるカラムと
    辞書変換メソッドを提供します。
    """

    # 共通カラム
    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True
    )
    symbol: Mapped[str] = mapped_column(String(20), nullable=False)
    open: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    high: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    low: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    close: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    volume: Mapped[int] = mapped_column(BigInteger, nullable=False)
    created_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    def to_dict(self) -> Dict[str, Any]:
        """モデルインスタンスを辞書形式に変換.

        Returns:
            Dict[str, Any]: モデルの辞書表現
        """

        def safe_float_conversion(value):
            """Decimal値を安全にfloatに変換し、NaN値をNoneに変換する."""
            if value is None:
                return None
            try:
                float_val = float(value)
                # NaN値をチェックしてNoneに変換
                if math.isnan(float_val) or math.isinf(float_val):
                    return None
                return float_val
            except (ValueError, TypeError, OverflowError):
                return None

        result = {
            "id": self.id,
            "symbol": self.symbol,
            "open": safe_float_conversion(self.open),
            "high": safe_float_conversion(self.high),
            "low": safe_float_conversion(self.low),
            "close": safe_float_conversion(self.close),
            "volume": self.volume,
            "created_at": (
                self.created_at.isoformat() if self.created_at else None
            ),
            "updated_at": (
                self.updated_at.isoformat() if self.updated_at else None
            ),
        }

        # 日付またはdatetimeフィールドを追加
        if hasattr(self, "date"):
            result["date"] = self.date.isoformat() if self.date else None
        if hasattr(self, "datetime"):
            result["datetime"] = (
                self.datetime.isoformat() if self.datetime else None
            )

        return result


__all__ = [
    "Base",
    "StockDataBase",
]
