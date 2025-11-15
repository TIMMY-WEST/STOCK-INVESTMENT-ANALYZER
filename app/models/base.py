"""SQLAlchemyのベースクラスと株価データ共通クラス."""

from decimal import Decimal

from sqlalchemy import BigInteger, Integer, Numeric, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from app.models.mixins import DictSerializableMixin, TimestampMixin


class Base(DeclarativeBase):
    """全てのモデルクラスの基底クラス.

    SQLAlchemyの宣言的マッピングの基底クラス。
    全てのORMモデルはこのクラスを継承します。

    Example:
        >>> class MyModel(Base):
        ...     __tablename__ = "my_table"
        ...     id: Mapped[int] = mapped_column(primary_key=True)
    """

    pass


class StockDataBase(TimestampMixin, DictSerializableMixin):
    """株価データの共通カラムと制約を定義するベースクラス.

    全ての株価データテーブルで共通して使用されるカラムと
    辞書変換メソッドを提供します。

    Attributes:
        id: レコードID（主キー、自動採番）
        symbol: 銘柄コード（例: "7203.T"）
        open: 始値
        high: 高値
        low: 安値
        close: 終値
        volume: 出来高
        created_at: 作成日時（TimestampMixinより）
        updated_at: 更新日時（TimestampMixinより）
    """

    # 共通カラム
    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True, comment="レコードID"
    )
    symbol: Mapped[str] = mapped_column(
        String(20), nullable=False, index=True, comment="銘柄コード"
    )
    open: Mapped[Decimal] = mapped_column(
        Numeric(10, 2), nullable=False, comment="始値"
    )
    high: Mapped[Decimal] = mapped_column(
        Numeric(10, 2), nullable=False, comment="高値"
    )
    low: Mapped[Decimal] = mapped_column(
        Numeric(10, 2), nullable=False, comment="安値"
    )
    close: Mapped[Decimal] = mapped_column(
        Numeric(10, 2), nullable=False, comment="終値"
    )
    volume: Mapped[int] = mapped_column(
        BigInteger, nullable=False, comment="出来高"
    )


__all__ = [
    "Base",
    "StockDataBase",
]
