"""Mixin classes for database models.

このモジュールは、複数のモデルで共通利用されるMixinクラスを提供します。
"""

from datetime import datetime
from decimal import Decimal
import math
from typing import Any, Dict, Optional

from sqlalchemy import Boolean, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func


class TimestampMixin:
    """タイムスタンプフィールドを提供するMixin.

    全てのモデルで使用する作成日時と更新日時のカラムを提供します。

    Attributes:
        created_at: レコードの作成日時（タイムゾーン付き）
        updated_at: レコードの更新日時（タイムゾーン付き、更新時に自動更新）
    """

    created_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        comment="作成日時",
    )
    updated_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
        comment="更新日時",
    )


class SoftDeleteMixin:
    """論理削除機能を提供するMixin.

    物理削除ではなく論理削除を行うためのフラグを提供します。

    Attributes:
        is_deleted: 削除フラグ（True=削除済み、False=有効）
        deleted_at: 削除日時（削除時に設定）
    """

    is_deleted: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        index=True,
        comment="削除フラグ（True=削除済み）",
    )
    deleted_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True, comment="削除日時"
    )


class DictSerializableMixin:
    """辞書型への変換機能を提供するMixin.

    モデルインスタンスをJSON互換の辞書形式に変換するメソッドを提供します。

    Note:
        このMixinはSQLAlchemyのBaseクラスと組み合わせて使用されます。
        __table__属性は実行時にSQLAlchemyによって自動的に提供されます。
    """

    def to_dict(self) -> Dict[str, Any]:
        """モデルインスタンスを辞書形式に変換.

        Returns:
            モデルの全カラムを含む辞書

        Note:
            - Decimal型はfloatに変換されます
            - NaN/Inf値はNoneに変換されます
            - datetime型はISO8601形式の文字列に変換されます
            - date型はYYYY-MM-DD形式の文字列に変換されます
        """

        def safe_float_conversion(value):
            """Decimal値を安全にfloatに変換し、NaN値をNoneに変換する."""
            if value is None:
                return None
            try:
                float_val = float(value)
                # NaN/Inf値をチェックしてNoneに変換
                if math.isnan(float_val) or math.isinf(float_val):
                    return None
                return float_val
            except (ValueError, TypeError, OverflowError):
                return None

        result: Dict[str, Any] = {}

        # 全カラムを走査して辞書に追加
        for column in self.__table__.columns:  # type: ignore[attr-defined]
            value = getattr(self, column.name)

            # Decimal型の変換
            if isinstance(value, Decimal):
                value = safe_float_conversion(value)
            # datetime型の変換
            elif isinstance(value, datetime):
                value = value.isoformat()
            # date型の変換
            elif hasattr(value, "isoformat"):
                value = value.isoformat()

            result[column.name] = value

        return result


__all__ = [
    "TimestampMixin",
    "SoftDeleteMixin",
    "DictSerializableMixin",
]
