"""株価データモデル定義.

様々な時間間隔の株価データテーブルを定義します。
"""

from datetime import date, datetime

from sqlalchemy import CheckConstraint, Date, DateTime, Index, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, StockDataBase


# 1分足データテーブル
class Stocks1m(Base, StockDataBase):
    """1分足株価データモデル.

    1分間隔の株価データを格納するテーブルです。
    """

    __tablename__ = "stocks_1m"

    datetime: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )

    __table_args__ = (
        UniqueConstraint(
            "symbol", "datetime", name="uk_stocks_1m_symbol_datetime"
        ),
        CheckConstraint(
            "open >= 0 AND high >= 0 AND low >= 0 AND close >= 0",
            name="ck_stocks_1m_prices",
        ),
        CheckConstraint("volume >= 0", name="ck_stocks_1m_volume"),
        CheckConstraint(
            "high >= low AND high >= open AND high >= close "
            "AND low <= open AND low <= close",
            name="ck_stocks_1m_price_logic",
        ),
        Index("idx_stocks_1m_symbol", "symbol"),
        Index("idx_stocks_1m_datetime", "datetime"),
        Index("idx_stocks_1m_symbol_datetime_desc", "symbol", "datetime"),
    )

    def __repr__(self):
        """オブジェクトの文字列表現を返す.

        Returns:
            str: オブジェクトの文字列表現
        """
        return (
            f"<Stocks1m(symbol='{self.symbol}', "
            f"datetime='{self.datetime}', close={self.close})>"
        )


# 5分足データテーブル
class Stocks5m(Base, StockDataBase):
    """5分足株価データモデル.

    5分間隔の株価データを格納するテーブルです。
    """

    __tablename__ = "stocks_5m"

    datetime: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )

    __table_args__ = (
        UniqueConstraint(
            "symbol", "datetime", name="uk_stocks_5m_symbol_datetime"
        ),
        CheckConstraint(
            "open >= 0 AND high >= 0 AND low >= 0 AND close >= 0",
            name="ck_stocks_5m_prices",
        ),
        CheckConstraint("volume >= 0", name="ck_stocks_5m_volume"),
        CheckConstraint(
            "high >= low AND high >= open AND high >= close "
            "AND low <= open AND low <= close",
            name="ck_stocks_5m_price_logic",
        ),
        Index("idx_stocks_5m_symbol", "symbol"),
        Index("idx_stocks_5m_datetime", "datetime"),
        Index("idx_stocks_5m_symbol_datetime_desc", "symbol", "datetime"),
    )

    def __repr__(self):
        """オブジェクトの文字列表現を返す.

        Returns:
            str: オブジェクトの文字列表現
        """
        return (
            f"<Stocks5m(symbol='{self.symbol}', "
            f"datetime='{self.datetime}', close={self.close})>"
        )


# 15分足データテーブル
class Stocks15m(Base, StockDataBase):
    """15分足株価データモデル.

    15分間隔の株価データを格納するテーブルです。
    """

    __tablename__ = "stocks_15m"

    datetime: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )

    __table_args__ = (
        UniqueConstraint(
            "symbol", "datetime", name="uk_stocks_15m_symbol_datetime"
        ),
        CheckConstraint(
            "open >= 0 AND high >= 0 AND low >= 0 AND close >= 0",
            name="ck_stocks_15m_prices",
        ),
        CheckConstraint("volume >= 0", name="ck_stocks_15m_volume"),
        CheckConstraint(
            "high >= low AND high >= open AND high >= close "
            "AND low <= open AND low <= close",
            name="ck_stocks_15m_price_logic",
        ),
        Index("idx_stocks_15m_symbol", "symbol"),
        Index("idx_stocks_15m_datetime", "datetime"),
        Index("idx_stocks_15m_symbol_datetime_desc", "symbol", "datetime"),
    )

    def __repr__(self):
        """オブジェクトの文字列表現を返す.

        Returns:
            str: オブジェクトの文字列表現
        """
        return (
            f"<Stocks15m(symbol='{self.symbol}', "
            f"datetime='{self.datetime}', close={self.close})>"
        )


# 30分足データテーブル
class Stocks30m(Base, StockDataBase):
    """30分足株価データモデル.

    30分間隔の株価データを格納するテーブルです。
    """

    __tablename__ = "stocks_30m"

    datetime: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )

    __table_args__ = (
        UniqueConstraint(
            "symbol", "datetime", name="uk_stocks_30m_symbol_datetime"
        ),
        CheckConstraint(
            "open >= 0 AND high >= 0 AND low >= 0 AND close >= 0",
            name="ck_stocks_30m_prices",
        ),
        CheckConstraint("volume >= 0", name="ck_stocks_30m_volume"),
        CheckConstraint(
            "high >= low AND high >= open AND high >= close "
            "AND low <= open AND low <= close",
            name="ck_stocks_30m_price_logic",
        ),
        Index("idx_stocks_30m_symbol", "symbol"),
        Index("idx_stocks_30m_datetime", "datetime"),
        Index("idx_stocks_30m_symbol_datetime_desc", "symbol", "datetime"),
    )

    def __repr__(self):
        """オブジェクトの文字列表現を返す.

        Returns:
            str: オブジェクトの文字列表現
        """
        return (
            f"<Stocks30m(symbol='{self.symbol}', "
            f"datetime='{self.datetime}', close={self.close})>"
        )


# 1時間足データテーブル
class Stocks1h(Base, StockDataBase):
    """1時間足株価データモデル.

    1時間間隔の株価データを格納するテーブルです。
    """

    __tablename__ = "stocks_1h"

    datetime: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )

    __table_args__ = (
        UniqueConstraint(
            "symbol", "datetime", name="uk_stocks_1h_symbol_datetime"
        ),
        CheckConstraint(
            "open >= 0 AND high >= 0 AND low >= 0 AND close >= 0",
            name="ck_stocks_1h_prices",
        ),
        CheckConstraint("volume >= 0", name="ck_stocks_1h_volume"),
        CheckConstraint(
            "high >= low AND high >= open AND high >= close "
            "AND low <= open AND low <= close",
            name="ck_stocks_1h_price_logic",
        ),
        Index("idx_stocks_1h_symbol", "symbol"),
        Index("idx_stocks_1h_datetime", "datetime"),
        Index("idx_stocks_1h_symbol_datetime_desc", "symbol", "datetime"),
    )

    def __repr__(self):
        """オブジェクトの文字列表現を返す.

        Returns:
            str: オブジェクトの文字列表現
        """
        return (
            f"<Stocks1h(symbol='{self.symbol}', "
            f"datetime='{self.datetime}', close={self.close})>"
        )


# 日足データテーブル(既存のstocks_dailyをstocks_1dに変更)
class Stocks1d(Base, StockDataBase):
    """日足株価データモデル.

    日次の株価データを格納するテーブルです。
    """

    __tablename__ = "stocks_1d"

    date: Mapped[date] = mapped_column(Date, nullable=False)

    __table_args__ = (
        UniqueConstraint("symbol", "date", name="uk_stocks_1d_symbol_date"),
        CheckConstraint(
            "open >= 0 AND high >= 0 AND low >= 0 AND close >= 0",
            name="ck_stocks_1d_prices",
        ),
        CheckConstraint("volume >= 0", name="ck_stocks_1d_volume"),
        CheckConstraint(
            "high >= low AND high >= open AND high >= close "
            "AND low <= open AND low <= close",
            name="ck_stocks_1d_price_logic",
        ),
        Index("idx_stocks_1d_symbol", "symbol"),
        Index("idx_stocks_1d_date", "date"),
        Index("idx_stocks_1d_symbol_date_desc", "symbol", "date"),
    )

    def __repr__(self):
        """オブジェクトの文字列表現を返す.

        Returns:
            str: オブジェクトの文字列表現
        """
        return (
            f"<Stocks1d(symbol='{self.symbol}', "
            f"date='{self.date}', close={self.close})>"
        )


# 週足データテーブル
class Stocks1wk(Base, StockDataBase):
    """週足株価データモデル.

    週次の株価データを格納するテーブルです。
    """

    __tablename__ = "stocks_1wk"

    date: Mapped[date] = mapped_column(Date, nullable=False)

    __table_args__ = (
        UniqueConstraint("symbol", "date", name="uk_stocks_1wk_symbol_date"),
        CheckConstraint(
            "open >= 0 AND high >= 0 AND low >= 0 AND close >= 0",
            name="ck_stocks_1wk_prices",
        ),
        CheckConstraint("volume >= 0", name="ck_stocks_1wk_volume"),
        CheckConstraint(
            "high >= low AND high >= open AND high >= close "
            "AND low <= open AND low <= close",
            name="ck_stocks_1wk_price_logic",
        ),
        Index("idx_stocks_1wk_symbol", "symbol"),
        Index("idx_stocks_1wk_date", "date"),
        Index("idx_stocks_1wk_symbol_date_desc", "symbol", "date"),
    )

    def __repr__(self):
        """オブジェクトの文字列表現を返す.

        Returns:
            str: オブジェクトの文字列表現
        """
        return (
            f"<Stocks1wk(symbol='{self.symbol}', "
            f"date='{self.date}', close={self.close})>"
        )


# 月足データテーブル
class Stocks1mo(Base, StockDataBase):
    """月足株価データモデル.

    月次の株価データを格納するテーブルです。
    """

    __tablename__ = "stocks_1mo"

    date: Mapped[date] = mapped_column(Date, nullable=False)

    __table_args__ = (
        UniqueConstraint("symbol", "date", name="uk_stocks_1mo_symbol_date"),
        CheckConstraint(
            "open >= 0 AND high >= 0 AND low >= 0 AND close >= 0",
            name="ck_stocks_1mo_prices",
        ),
        CheckConstraint("volume >= 0", name="ck_stocks_1mo_volume"),
        CheckConstraint(
            "high >= low AND high >= open AND high >= close "
            "AND low <= open AND low <= close",
            name="ck_stocks_1mo_price_logic",
        ),
        Index("idx_stocks_1mo_symbol", "symbol"),
        Index("idx_stocks_1mo_date", "date"),
        Index("idx_stocks_1mo_symbol_date_desc", "symbol", "date"),
    )

    def __repr__(self):
        """オブジェクトの文字列表現を返す.

        Returns:
            str: オブジェクトの文字列表現
        """
        return (
            f"<Stocks1mo(symbol='{self.symbol}', "
            f"date='{self.date}', close={self.close})>"
        )


# 既存のStockDailyクラスは後方互換性のためにStocks1dのエイリアスとして残す
StockDaily = Stocks1d


__all__ = [
    "Stocks1m",
    "Stocks5m",
    "Stocks15m",
    "Stocks30m",
    "Stocks1h",
    "Stocks1d",
    "Stocks1wk",
    "Stocks1mo",
    "StockDaily",
]
