"""株価投資分析システムのデータベースモデル定義.

このモジュールは、株価データ、銘柄マスタ、バッチ実行履歴などの
データベースモデルとCRUD操作を提供します。
"""

from contextlib import contextmanager
from datetime import date, datetime
from decimal import Decimal
import os
from typing import Any, Dict, Iterator, List, Optional

from dotenv import load_dotenv
from sqlalchemy import (
    BigInteger,
    CheckConstraint,
    Date,
    DateTime,
    Index,
    Integer,
    Numeric,
    String,
    UniqueConstraint,
    create_engine,
)
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    Session,
    mapped_column,
    sessionmaker,
)
from sqlalchemy.sql import func


load_dotenv()


class Base(DeclarativeBase):
    """全てのモデルクラスの基底クラス."""

    pass


class DatabaseError(Exception):
    """データベース操作エラーの基底クラス."""

    pass


class StockDataError(DatabaseError):
    """株価データ関連エラー."""

    pass


# ベースクラス：共通のカラムと制約を定義
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

        def safe_float_conversion(value: Any) -> Optional[float]:
            """Decimal値を安全にfloatに変換し、NaN値をNoneに変換する.

            Args:
                value: Decimal もしくは数値/None を想定

            Returns:
                Optional[float]: 変換後の float、変換不可や NaN/Inf は None
            """
            if value is None:
                return None
            try:
                float_val = float(value)
                # NaN値をチェックしてNoneに変換
                import math

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
            "high >= low AND high >= open AND high >= close AND low <= open AND low <= close",
            name="ck_stocks_1m_price_logic",
        ),
        Index("idx_stocks_1m_symbol", "symbol"),
        Index("idx_stocks_1m_datetime", "datetime"),
        Index("idx_stocks_1m_symbol_datetime_desc", "symbol", "datetime"),
    )

    def __repr__(self) -> str:
        """オブジェクトの文字列表現を返す.

        Returns:
            str: オブジェクトの文字列表現
        """
        return f"<Stocks1m(symbol='{self.symbol}', datetime='{self.datetime}', close={self.close})>"


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
            "high >= low AND high >= open AND high >= close AND low <= open AND low <= close",
            name="ck_stocks_5m_price_logic",
        ),
        Index("idx_stocks_5m_symbol", "symbol"),
        Index("idx_stocks_5m_datetime", "datetime"),
        Index("idx_stocks_5m_symbol_datetime_desc", "symbol", "datetime"),
    )

    def __repr__(self) -> str:
        """オブジェクトの文字列表現を返す.

        Returns:
            str: オブジェクトの文字列表現
        """
        return f"<Stocks5m(symbol='{self.symbol}', datetime='{self.datetime}', close={self.close})>"


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
            "high >= low AND high >= open AND high >= close AND low <= open AND low <= close",
            name="ck_stocks_15m_price_logic",
        ),
        Index("idx_stocks_15m_symbol", "symbol"),
        Index("idx_stocks_15m_datetime", "datetime"),
        Index("idx_stocks_15m_symbol_datetime_desc", "symbol", "datetime"),
    )

    def __repr__(self) -> str:
        """オブジェクトの文字列表現を返す.

        Returns:
            str: オブジェクトの文字列表現
        """
        return f"<Stocks15m(symbol='{self.symbol}', datetime='{self.datetime}', close={self.close})>"


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
            "high >= low AND high >= open AND high >= close AND low <= open AND low <= close",
            name="ck_stocks_30m_price_logic",
        ),
        Index("idx_stocks_30m_symbol", "symbol"),
        Index("idx_stocks_30m_datetime", "datetime"),
        Index("idx_stocks_30m_symbol_datetime_desc", "symbol", "datetime"),
    )

    def __repr__(self) -> str:
        """オブジェクトの文字列表現を返す.

        Returns:
            str: オブジェクトの文字列表現
        """
        return f"<Stocks30m(symbol='{self.symbol}', datetime='{self.datetime}', close={self.close})>"


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
            "high >= low AND high >= open AND high >= close AND low <= open AND low <= close",
            name="ck_stocks_1h_price_logic",
        ),
        Index("idx_stocks_1h_symbol", "symbol"),
        Index("idx_stocks_1h_datetime", "datetime"),
        Index("idx_stocks_1h_symbol_datetime_desc", "symbol", "datetime"),
    )

    def __repr__(self) -> str:
        """オブジェクトの文字列表現を返す.

        Returns:
            str: オブジェクトの文字列表現
        """
        return f"<Stocks1h(symbol='{self.symbol}', datetime='{self.datetime}', close={self.close})>"


# 日足データテーブル（既存のstocks_dailyをstocks_1dに変更）
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
            "high >= low AND high >= open AND high >= close AND low <= open AND low <= close",
            name="ck_stocks_1d_price_logic",
        ),
        Index("idx_stocks_1d_symbol", "symbol"),
        Index("idx_stocks_1d_date", "date"),
        Index("idx_stocks_1d_symbol_date_desc", "symbol", "date"),
    )

    def __repr__(self) -> str:
        """オブジェクトの文字列表現を返す.

        Returns:
            str: オブジェクトの文字列表現
        """
        return f"<Stocks1d(symbol='{self.symbol}', date='{self.date}', close={self.close})>"


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
            "high >= low AND high >= open AND high >= close AND low <= open AND low <= close",
            name="ck_stocks_1wk_price_logic",
        ),
        Index("idx_stocks_1wk_symbol", "symbol"),
        Index("idx_stocks_1wk_date", "date"),
        Index("idx_stocks_1wk_symbol_date_desc", "symbol", "date"),
    )

    def __repr__(self) -> str:
        """オブジェクトの文字列表現を返す.

        Returns:
            str: オブジェクトの文字列表現
        """
        return f"<Stocks1wk(symbol='{self.symbol}', date='{self.date}', close={self.close})>"


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
            "high >= low AND high >= open AND high >= close AND low <= open AND low <= close",
            name="ck_stocks_1mo_price_logic",
        ),
        Index("idx_stocks_1mo_symbol", "symbol"),
        Index("idx_stocks_1mo_date", "date"),
        Index("idx_stocks_1mo_symbol_date_desc", "symbol", "date"),
    )

    def __repr__(self) -> str:
        """オブジェクトの文字列表現を返す.

        Returns:
            str: オブジェクトの文字列表現
        """
        return f"<Stocks1mo(symbol='{self.symbol}', date='{self.date}', close={self.close})>"


# 既存のStockDailyクラスは後方互換性のためにStocks1dのエイリアスとして残す
StockDaily = Stocks1d


# 銘柄マスタテーブル (Phase 2)
class StockMaster(Base):
    """銘柄マスタテーブル - JPX銘柄一覧を管理（全項目対応版）.

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
    )  # 銘柄コード（例: "7203"）
    stock_name: Mapped[str] = mapped_column(
        String(100), nullable=False
    )  # 銘柄名（例: "トヨタ自動車"）
    market_category: Mapped[Optional[str]] = mapped_column(
        String(50)
    )  # 市場区分（例: "プライム（内国株式）"）

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
    )  # 規模区分（TOPIX分類）

    # データ管理
    data_date: Mapped[Optional[str]] = mapped_column(
        String(8)
    )  # データ取得日（YYYYMMDD形式）
    is_active: Mapped[Optional[int]] = mapped_column(
        Integer, default=1, nullable=False
    )  # 有効フラグ（1=有効, 0=無効）
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

    def __repr__(self) -> str:
        """オブジェクトの文字列表現を返す.

        Returns:
            str: オブジェクトの文字列表現
        """
        return f"<StockMaster(stock_code='{self.stock_code}', stock_name='{self.stock_name}', is_active={self.is_active})>"

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
    )  # 削除（無効化）銘柄数
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

    def __repr__(self) -> str:
        """オブジェクトの文字列表現を返す.

        Returns:
            str: オブジェクトの文字列表現
        """
        return f"<StockMasterUpdate(id={self.id}, update_type='{self.update_type}', status='{self.status}')>"

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
        return f"<BatchExecution(id={self.id}, batch_type='{self.batch_type}', status='{self.status}')>"

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
            float: 進捗率（0.0-100.0）
        """
        if self.total_stocks == 0:
            return 0.0
        processed = self.processed_stocks or 0
        return (processed / self.total_stocks) * 100.0

    @property
    def duration_seconds(self) -> Optional[float]:
        """実行時間を秒で計算.

        Returns:
            Optional[float]: 実行時間（秒）、開始時間が未設定の場合はNone
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
        return f"<BatchExecutionDetail(id={self.id}, batch_execution_id={self.batch_execution_id}, stock_code='{self.stock_code}', status='{self.status}')>"

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
            Optional[float]: 処理時間（秒）、開始時間が未設定の場合はNone
        """
        if not self.start_time:
            return None
        end_time = self.end_time or datetime.now(self.start_time.tzinfo)
        return (end_time - self.start_time).total_seconds()


# データベース設定
DATABASE_URL = f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"

# コネクションプール設定
# - pool_size: 通常時に保持する接続数（デフォルト5→10に変更）
# - max_overflow: pool_sizeを超えて作成可能な追加接続数
# - pool_pre_ping: 接続を使用前にpingして有効性を確認（接続切れ防止）
# - pool_recycle: 接続を再利用する最大秒数（-1=無制限、3600=1時間）
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
def get_db_session() -> Iterator[Session]:
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


class StockDailyCRUD:
    """StockDailyモデルのCRUD操作クラス.

    日足株価データに対する作成、読み取り、更新、削除操作を提供します。
    """

    @staticmethod
    def create(session: Session, **kwargs) -> StockDaily:
        """新しい株価データを作成.

        Args:
            session: データベースセッション
            **kwargs: 株価データの属性

        Returns:
            StockDaily: 作成された株価データ

        Raises:
            StockDataError: データが既に存在する場合
            DatabaseError: データベースエラーが発生した場合
        """
        try:
            stock_data = StockDaily(**kwargs)
            session.add(stock_data)
            session.flush()
            return stock_data
        except IntegrityError as e:
            if "uk_stocks_daily_symbol_date" in str(e):
                raise StockDataError(
                    f"銘柄 {kwargs.get('symbol')} の日付 {kwargs.get('date')} のデータは既に存在します"
                )
            raise DatabaseError(f"データベース制約違反: {str(e)}")
        except SQLAlchemyError as e:
            raise DatabaseError(f"データベースエラー: {str(e)}")

    @staticmethod
    def get_by_id(session: Session, stock_id: int) -> Optional[StockDaily]:
        """IDで株価データを取得.

        Args:
            session: データベースセッション
            stock_id: 株価データのID

        Returns:
            Optional[StockDaily]: 見つかった株価データ、存在しない場合はNone

        Raises:
            DatabaseError: データベースエラーが発生した場合
        """
        try:
            return (
                session.query(StockDaily)
                .filter(StockDaily.id == stock_id)
                .first()
            )
        except SQLAlchemyError as e:
            raise DatabaseError(f"データベースエラー: {str(e)}")

    @staticmethod
    def get_by_symbol_and_date(
        session: Session, symbol: str, date: date
    ) -> Optional[StockDaily]:
        """銘柄コードと日付で株価データを取得.

        Args:
            session: データベースセッション
            symbol: 銘柄コード
            date: 日付

        Returns:
            Optional[StockDaily]: 見つかった株価データ、存在しない場合はNone

        Raises:
            DatabaseError: データベースエラーが発生した場合
        """
        try:
            return (
                session.query(StockDaily)
                .filter(StockDaily.symbol == symbol, StockDaily.date == date)
                .first()
            )
        except SQLAlchemyError as e:
            raise DatabaseError(f"データベースエラー: {str(e)}")

    @staticmethod
    def get_by_symbol(
        session: Session,
        symbol: str,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
    ) -> List[StockDaily]:
        """銘柄コードで株価データを取得（日付降順）.

        Args:
            session: データベースセッション
            symbol: 銘柄コード
            limit: 取得件数の上限
            offset: 取得開始位置のオフセット
            start_date: 開始日付（この日付以降）
            end_date: 終了日付（この日付以前）

        Returns:
            List[StockDaily]: 株価データのリスト

        Raises:
            DatabaseError: データベースエラーが発生した場合
        """
        try:
            query = session.query(StockDaily).filter(
                StockDaily.symbol == symbol
            )

            if start_date:
                query = query.filter(StockDaily.date >= start_date)
            if end_date:
                query = query.filter(StockDaily.date <= end_date)

            query = query.order_by(StockDaily.date.desc())

            if offset:
                query = query.offset(offset)
            if limit:
                query = query.limit(limit)

            return query.all()
        except SQLAlchemyError as e:
            raise DatabaseError(f"データベースエラー: {str(e)}")

    @staticmethod
    def get_with_filters(
        session: Session,
        symbol: Optional[str] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
    ) -> List[StockDaily]:
        """フィルタ条件に基づく株価データを取得（日付降順）.

        Args:
            session: データベースセッション
            symbol: 銘柄コード（指定時のみフィルタ）
            limit: 取得件数の上限
            offset: 取得開始位置のオフセット
            start_date: 開始日付（この日付以降）
            end_date: 終了日付（この日付以前）

        Returns:
            List[StockDaily]: 株価データのリスト

        Raises:
            DatabaseError: データベースエラーが発生した場合
        """
        try:
            query = session.query(StockDaily)

            if symbol:
                query = query.filter(StockDaily.symbol == symbol)
            if start_date:
                query = query.filter(StockDaily.date >= start_date)
            if end_date:
                query = query.filter(StockDaily.date <= end_date)

            query = query.order_by(StockDaily.date.desc(), StockDaily.symbol)

            if offset:
                query = query.offset(offset)
            if limit:
                query = query.limit(limit)

            return query.all()
        except SQLAlchemyError as e:
            raise DatabaseError(f"データベースエラー: {str(e)}")

    @staticmethod
    def get_all(
        session: Session,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
    ) -> List[StockDaily]:
        """全ての株価データを取得（日付降順）.

        Args:
            session: データベースセッション
            limit: 取得件数の上限
            offset: 取得開始位置のオフセット

        Returns:
            List[StockDaily]: 株価データのリスト

        Raises:
            DatabaseError: データベースエラーが発生した場合
        """
        try:
            query = session.query(StockDaily).order_by(
                StockDaily.date.desc(), StockDaily.symbol
            )

            if offset:
                query = query.offset(offset)
            if limit:
                query = query.limit(limit)

            return query.all()
        except SQLAlchemyError as e:
            raise DatabaseError(f"データベースエラー: {str(e)}")

    @staticmethod
    def update(
        session: Session, stock_id: int, **kwargs
    ) -> Optional[StockDaily]:
        """株価データを更新.

        Args:
            session: データベースセッション
            stock_id: 更新対象の株価データID
            **kwargs: 更新するフィールドと値

        Returns:
            Optional[StockDaily]: 更新された株価データ（見つからない場合はNone）

        Raises:
            StockDataError: 銘柄コードと日付の組み合わせが重複した場合
            DatabaseError: データベースエラーが発生した場合
        """
        try:
            stock_data = (
                session.query(StockDaily)
                .filter(StockDaily.id == stock_id)
                .first()
            )
            if not stock_data:
                return None

            for key, value in kwargs.items():
                if hasattr(stock_data, key):
                    setattr(stock_data, key, value)

            # updated_atはonupdateで自動更新されるため、明示的な設定は不要
            session.flush()
            return stock_data
        except IntegrityError as e:
            if "uk_stocks_daily_symbol_date" in str(e):
                raise StockDataError("銘柄コードと日付の組み合わせが既に存在します")
            raise DatabaseError(f"データベース制約違反: {str(e)}")
        except SQLAlchemyError as e:
            raise DatabaseError(f"データベースエラー: {str(e)}")

    @staticmethod
    def delete(session: Session, stock_id: int) -> bool:
        """株価データを削除.

        Args:
            session: データベースセッション
            stock_id: 削除対象の株価データID

        Returns:
            bool: 削除が成功した場合True、対象が見つからない場合False

        Raises:
            DatabaseError: データベースエラーが発生した場合
        """
        try:
            stock_data = (
                session.query(StockDaily)
                .filter(StockDaily.id == stock_id)
                .first()
            )
            if not stock_data:
                return False

            session.delete(stock_data)
            session.flush()
            return True
        except SQLAlchemyError as e:
            raise DatabaseError(f"データベースエラー: {str(e)}")

    @staticmethod
    def bulk_create(
        session: Session, stock_data_list: List[Dict[str, Any]]
    ) -> List[StockDaily]:
        """複数の株価データを一括作成.

        Args:
            session: データベースセッション
            stock_data_list: 作成する株価データのリスト

        Returns:
            List[StockDaily]: 作成された株価データのリスト

        Raises:
            StockDataError: 重複データが検出された場合
            DatabaseError: データベースエラーが発生した場合
        """
        try:
            stock_objects = []
            for data in stock_data_list:
                stock_data = StockDaily(**data)
                stock_objects.append(stock_data)

            session.add_all(stock_objects)
            session.flush()
            return stock_objects
        except IntegrityError as e:
            if "uk_stocks_daily_symbol_date" in str(e):
                raise StockDataError("一括作成中に重複データが検出されました")
            raise DatabaseError(f"データベース制約違反: {str(e)}")
        except SQLAlchemyError as e:
            raise DatabaseError(f"データベースエラー: {str(e)}")

    @staticmethod
    def count_by_symbol(session: Session, symbol: str) -> int:
        """銘柄のデータ件数を取得.

        Args:
            session: データベースセッション
            symbol: 銘柄コード

        Returns:
            int: 指定銘柄のデータ件数

        Raises:
            DatabaseError: データベースエラーが発生した場合
        """
        try:
            return (
                session.query(StockDaily)
                .filter(StockDaily.symbol == symbol)
                .count()
            )
        except SQLAlchemyError as e:
            raise DatabaseError(f"データベースエラー: {str(e)}")

    @staticmethod
    def get_latest_date_by_symbol(
        session: Session, symbol: str
    ) -> Optional[date]:
        """銘柄の最新データ日付を取得.

        Args:
            session: データベースセッション
            symbol: 銘柄コード

        Returns:
            Optional[date]: 最新データの日付（データがない場合はNone）

        Raises:
            DatabaseError: データベースエラーが発生した場合
        """
        try:
            result = (
                session.query(StockDaily.date)
                .filter(StockDaily.symbol == symbol)
                .order_by(StockDaily.date.desc())
                .first()
            )
            return result[0] if result else None
        except SQLAlchemyError as e:
            raise DatabaseError(f"データベースエラー: {str(e)}")

    @staticmethod
    def count_all(session: Session) -> int:
        """全ての株価データ件数を取得.

        Args:
            session: データベースセッション

        Returns:
            int: 全ての株価データの件数

        Raises:
            DatabaseError: データベースエラーが発生した場合
        """
        try:
            return session.query(StockDaily).count()
        except SQLAlchemyError as e:
            raise DatabaseError(f"データベースエラー: {str(e)}")

    @staticmethod
    def count_with_filters(
        session: Session,
        symbol: Optional[str] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
    ) -> int:
        """フィルタ条件に基づく株価データ件数を取得.

        Args:
            session: データベースセッション
            symbol: 銘柄コード（指定時のみフィルタ）
            start_date: 開始日付（この日付以降）
            end_date: 終了日付（この日付以前）

        Returns:
            int: フィルタ条件に一致するデータの件数

        Raises:
            DatabaseError: データベースエラーが発生した場合
        """
        try:
            query = session.query(StockDaily)

            if symbol:
                query = query.filter(StockDaily.symbol == symbol)
            if start_date:
                query = query.filter(StockDaily.date >= start_date)
            if end_date:
                query = query.filter(StockDaily.date <= end_date)

            return query.count()
        except SQLAlchemyError as e:
            raise DatabaseError(f"データベースエラー: {str(e)}")
