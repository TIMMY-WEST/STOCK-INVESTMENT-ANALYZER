from sqlalchemy import Column, Integer, String, Date, Numeric, BigInteger, DateTime, UniqueConstraint, CheckConstraint, Index, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.sql import func
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from typing import List, Optional, Dict, Any, Union
from datetime import date, datetime
from contextlib import contextmanager
import os
from dotenv import load_dotenv

load_dotenv()

Base = declarative_base()

class DatabaseError(Exception):
    """データベース操作エラーの基底クラス"""
    pass

class StockDataError(DatabaseError):
    """株価データ関連エラー"""
    pass

# =============================================================================
# 時間軸対応モデルクラス
# =============================================================================

class StockDaily(Base):
    """1日足株価データモデル（stocks_1dテーブル）"""
    __tablename__ = 'stocks_1d'

    # カラム定義
    id = Column(Integer, primary_key=True, autoincrement=True)
    symbol = Column(String(20), nullable=False)
    date = Column(Date, nullable=False)
    open = Column(Numeric(10, 2), nullable=False)
    high = Column(Numeric(10, 2), nullable=False)
    low = Column(Numeric(10, 2), nullable=False)
    close = Column(Numeric(10, 2), nullable=False)
    volume = Column(BigInteger, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # 制約定義
    __table_args__ = (
        UniqueConstraint('symbol', 'date', name='uk_stocks_1d_symbol_date'),
        CheckConstraint('open >= 0 AND high >= 0 AND low >= 0 AND close >= 0', name='ck_stocks_1d_prices'),
        CheckConstraint('volume >= 0', name='ck_stocks_1d_volume'),
        CheckConstraint('high >= low AND high >= open AND high >= close AND low <= open AND low <= close', name='ck_stocks_1d_price_logic'),
        Index('idx_stocks_1d_symbol', 'symbol'),
        Index('idx_stocks_1d_date', 'date'),
        Index('idx_stocks_1d_symbol_date_desc', 'symbol', 'date'),
    )

    def __repr__(self):
        return f"<StockDaily(symbol='{self.symbol}', date='{self.date}', close={self.close})>"

    def to_dict(self) -> Dict[str, Any]:
        """モデルインスタンスを辞書形式に変換"""
        return {
            'id': self.id,
            'symbol': self.symbol,
            'date': self.date.isoformat() if self.date else None,
            'open': float(self.open) if self.open else None,
            'high': float(self.high) if self.high else None,
            'low': float(self.low) if self.low else None,
            'close': float(self.close) if self.close else None,
            'volume': self.volume,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class Stock1m(Base):
    """1分足株価データモデル"""
    __tablename__ = 'stocks_1m'

    id = Column(Integer, primary_key=True, autoincrement=True)
    symbol = Column(String(20), nullable=False)
    datetime = Column(DateTime(timezone=True), nullable=False)
    open = Column(Numeric(10, 2), nullable=False)
    high = Column(Numeric(10, 2), nullable=False)
    low = Column(Numeric(10, 2), nullable=False)
    close = Column(Numeric(10, 2), nullable=False)
    volume = Column(BigInteger, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    __table_args__ = (
        UniqueConstraint('symbol', 'datetime', name='uk_stocks_1m_symbol_datetime'),
        CheckConstraint('open >= 0 AND high >= 0 AND low >= 0 AND close >= 0', name='ck_stocks_1m_prices'),
        CheckConstraint('volume >= 0', name='ck_stocks_1m_volume'),
        CheckConstraint('high >= low AND high >= open AND high >= close AND low <= open AND low <= close', name='ck_stocks_1m_price_logic'),
    )

    def __repr__(self):
        return f"<Stock1m(symbol='{self.symbol}', datetime='{self.datetime}', close={self.close})>"

    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'symbol': self.symbol,
            'datetime': self.datetime.isoformat() if self.datetime else None,
            'open': float(self.open) if self.open else None,
            'high': float(self.high) if self.high else None,
            'low': float(self.low) if self.low else None,
            'close': float(self.close) if self.close else None,
            'volume': self.volume,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class Stock5m(Base):
    """5分足株価データモデル"""
    __tablename__ = 'stocks_5m'

    id = Column(Integer, primary_key=True, autoincrement=True)
    symbol = Column(String(20), nullable=False)
    datetime = Column(DateTime(timezone=True), nullable=False)
    open = Column(Numeric(10, 2), nullable=False)
    high = Column(Numeric(10, 2), nullable=False)
    low = Column(Numeric(10, 2), nullable=False)
    close = Column(Numeric(10, 2), nullable=False)
    volume = Column(BigInteger, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    __table_args__ = (
        UniqueConstraint('symbol', 'datetime', name='uk_stocks_5m_symbol_datetime'),
        CheckConstraint('open >= 0 AND high >= 0 AND low >= 0 AND close >= 0', name='ck_stocks_5m_prices'),
        CheckConstraint('volume >= 0', name='ck_stocks_5m_volume'),
        CheckConstraint('high >= low AND high >= open AND high >= close AND low <= open AND low <= close', name='ck_stocks_5m_price_logic'),
    )

    def __repr__(self):
        return f"<Stock5m(symbol='{self.symbol}', datetime='{self.datetime}', close={self.close})>"

    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'symbol': self.symbol,
            'datetime': self.datetime.isoformat() if self.datetime else None,
            'open': float(self.open) if self.open else None,
            'high': float(self.high) if self.high else None,
            'low': float(self.low) if self.low else None,
            'close': float(self.close) if self.close else None,
            'volume': self.volume,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class Stock15m(Base):
    """15分足株価データモデル"""
    __tablename__ = 'stocks_15m'

    id = Column(Integer, primary_key=True, autoincrement=True)
    symbol = Column(String(20), nullable=False)
    datetime = Column(DateTime(timezone=True), nullable=False)
    open = Column(Numeric(10, 2), nullable=False)
    high = Column(Numeric(10, 2), nullable=False)
    low = Column(Numeric(10, 2), nullable=False)
    close = Column(Numeric(10, 2), nullable=False)
    volume = Column(BigInteger, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    __table_args__ = (
        UniqueConstraint('symbol', 'datetime', name='uk_stocks_15m_symbol_datetime'),
        CheckConstraint('open >= 0 AND high >= 0 AND low >= 0 AND close >= 0', name='ck_stocks_15m_prices'),
        CheckConstraint('volume >= 0', name='ck_stocks_15m_volume'),
        CheckConstraint('high >= low AND high >= open AND high >= close AND low <= open AND low <= close', name='ck_stocks_15m_price_logic'),
    )

    def __repr__(self):
        return f"<Stock15m(symbol='{self.symbol}', datetime='{self.datetime}', close={self.close})>"

    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'symbol': self.symbol,
            'datetime': self.datetime.isoformat() if self.datetime else None,
            'open': float(self.open) if self.open else None,
            'high': float(self.high) if self.high else None,
            'low': float(self.low) if self.low else None,
            'close': float(self.close) if self.close else None,
            'volume': self.volume,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class Stock30m(Base):
    """30分足株価データモデル"""
    __tablename__ = 'stocks_30m'

    id = Column(Integer, primary_key=True, autoincrement=True)
    symbol = Column(String(20), nullable=False)
    datetime = Column(DateTime(timezone=True), nullable=False)
    open = Column(Numeric(10, 2), nullable=False)
    high = Column(Numeric(10, 2), nullable=False)
    low = Column(Numeric(10, 2), nullable=False)
    close = Column(Numeric(10, 2), nullable=False)
    volume = Column(BigInteger, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    __table_args__ = (
        UniqueConstraint('symbol', 'datetime', name='uk_stocks_30m_symbol_datetime'),
        CheckConstraint('open >= 0 AND high >= 0 AND low >= 0 AND close >= 0', name='ck_stocks_30m_prices'),
        CheckConstraint('volume >= 0', name='ck_stocks_30m_volume'),
        CheckConstraint('high >= low AND high >= open AND high >= close AND low <= open AND low <= close', name='ck_stocks_30m_price_logic'),
    )

    def __repr__(self):
        return f"<Stock30m(symbol='{self.symbol}', datetime='{self.datetime}', close={self.close})>"

    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'symbol': self.symbol,
            'datetime': self.datetime.isoformat() if self.datetime else None,
            'open': float(self.open) if self.open else None,
            'high': float(self.high) if self.high else None,
            'low': float(self.low) if self.low else None,
            'close': float(self.close) if self.close else None,
            'volume': self.volume,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class Stock1h(Base):
    """1時間足株価データモデル"""
    __tablename__ = 'stocks_1h'

    id = Column(Integer, primary_key=True, autoincrement=True)
    symbol = Column(String(20), nullable=False)
    datetime = Column(DateTime(timezone=True), nullable=False)
    open = Column(Numeric(10, 2), nullable=False)
    high = Column(Numeric(10, 2), nullable=False)
    low = Column(Numeric(10, 2), nullable=False)
    close = Column(Numeric(10, 2), nullable=False)
    volume = Column(BigInteger, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    __table_args__ = (
        UniqueConstraint('symbol', 'datetime', name='uk_stocks_1h_symbol_datetime'),
        CheckConstraint('open >= 0 AND high >= 0 AND low >= 0 AND close >= 0', name='ck_stocks_1h_prices'),
        CheckConstraint('volume >= 0', name='ck_stocks_1h_volume'),
        CheckConstraint('high >= low AND high >= open AND high >= close AND low <= open AND low <= close', name='ck_stocks_1h_price_logic'),
    )

    def __repr__(self):
        return f"<Stock1h(symbol='{self.symbol}', datetime='{self.datetime}', close={self.close})>"

    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'symbol': self.symbol,
            'datetime': self.datetime.isoformat() if self.datetime else None,
            'open': float(self.open) if self.open else None,
            'high': float(self.high) if self.high else None,
            'low': float(self.low) if self.low else None,
            'close': float(self.close) if self.close else None,
            'volume': self.volume,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class Stock1wk(Base):
    """1週間足株価データモデル"""
    __tablename__ = 'stocks_1wk'

    id = Column(Integer, primary_key=True, autoincrement=True)
    symbol = Column(String(20), nullable=False)
    week_start_date = Column(Date, nullable=False)
    open = Column(Numeric(10, 2), nullable=False)
    high = Column(Numeric(10, 2), nullable=False)
    low = Column(Numeric(10, 2), nullable=False)
    close = Column(Numeric(10, 2), nullable=False)
    volume = Column(BigInteger, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    __table_args__ = (
        UniqueConstraint('symbol', 'week_start_date', name='uk_stocks_1wk_symbol_week'),
        CheckConstraint('open >= 0 AND high >= 0 AND low >= 0 AND close >= 0', name='ck_stocks_1wk_prices'),
        CheckConstraint('volume >= 0', name='ck_stocks_1wk_volume'),
        CheckConstraint('high >= low AND high >= open AND high >= close AND low <= open AND low <= close', name='ck_stocks_1wk_price_logic'),
    )

    def __repr__(self):
        return f"<Stock1wk(symbol='{self.symbol}', week_start_date='{self.week_start_date}', close={self.close})>"

    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'symbol': self.symbol,
            'week_start_date': self.week_start_date.isoformat() if self.week_start_date else None,
            'open': float(self.open) if self.open else None,
            'high': float(self.high) if self.high else None,
            'low': float(self.low) if self.low else None,
            'close': float(self.close) if self.close else None,
            'volume': self.volume,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class Stock1mo(Base):
    """1ヶ月足株価データモデル"""
    __tablename__ = 'stocks_1mo'

    id = Column(Integer, primary_key=True, autoincrement=True)
    symbol = Column(String(20), nullable=False)
    year = Column(Integer, nullable=False)
    month = Column(Integer, nullable=False)
    open = Column(Numeric(10, 2), nullable=False)
    high = Column(Numeric(10, 2), nullable=False)
    low = Column(Numeric(10, 2), nullable=False)
    close = Column(Numeric(10, 2), nullable=False)
    volume = Column(BigInteger, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    __table_args__ = (
        UniqueConstraint('symbol', 'year', 'month', name='uk_stocks_1mo_symbol_year_month'),
        CheckConstraint('open >= 0 AND high >= 0 AND low >= 0 AND close >= 0', name='ck_stocks_1mo_prices'),
        CheckConstraint('volume >= 0', name='ck_stocks_1mo_volume'),
        CheckConstraint('year >= 1900 AND year <= 2100', name='ck_stocks_1mo_year'),
        CheckConstraint('month >= 1 AND month <= 12', name='ck_stocks_1mo_month'),
        CheckConstraint('high >= low AND high >= open AND high >= close AND low <= open AND low <= close', name='ck_stocks_1mo_price_logic'),
    )

    def __repr__(self):
        return f"<Stock1mo(symbol='{self.symbol}', year={self.year}, month={self.month}, close={self.close})>"

    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'symbol': self.symbol,
            'year': self.year,
            'month': self.month,
            'open': float(self.open) if self.open else None,
            'high': float(self.high) if self.high else None,
            'low': float(self.low) if self.low else None,
            'close': float(self.close) if self.close else None,
            'volume': self.volume,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

# =============================================================================
# 時間軸モデルマッピング
# =============================================================================

TIMEFRAME_MODELS = {
    '1m': Stock1m,
    '5m': Stock5m,
    '15m': Stock15m,
    '30m': Stock30m,
    '1h': Stock1h,
    '1d': StockDaily,
    '1wk': Stock1wk,
    '1mo': Stock1mo,
}

def get_model_by_timeframe(timeframe: str):
    """時間軸文字列からモデルクラスを取得"""
    return TIMEFRAME_MODELS.get(timeframe)

def get_table_name_by_timeframe(timeframe: str) -> str:
    """時間軸文字列からテーブル名を取得"""
    model = get_model_by_timeframe(timeframe)
    return model.__tablename__ if model else None

# =============================================================================
# データベース設定
# =============================================================================

DATABASE_URL = f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@contextmanager
def get_db_session():
    """データベースセッションのコンテキストマネージャー"""
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()

# =============================================================================
# 汎用CRUDクラス
# =============================================================================

class TimeframeCRUD:
    """時間軸対応の汎用CRUDクラス"""

    @staticmethod
    def create(session: Session, timeframe: str, **kwargs):
        """新しい株価データを作成"""
        model_class = get_model_by_timeframe(timeframe)
        if not model_class:
            raise ValueError(f"サポートされていない時間軸: {timeframe}")
        
        try:
            stock_data = model_class(**kwargs)
            session.add(stock_data)
            session.flush()
            return stock_data
        except IntegrityError as e:
            constraint_name = f"uk_stocks_{timeframe.replace('wk', '1wk').replace('mo', '1mo')}_symbol"
            if constraint_name in str(e):
                raise StockDataError(f"銘柄 {kwargs.get('symbol')} の指定時刻のデータは既に存在します")
            raise DatabaseError(f"データベース制約違反: {str(e)}")
        except SQLAlchemyError as e:
            raise DatabaseError(f"データベースエラー: {str(e)}")

    @staticmethod
    def bulk_create(session: Session, timeframe: str, stock_data_list: List[Dict[str, Any]]):
        """複数の株価データを一括作成"""
        model_class = get_model_by_timeframe(timeframe)
        if not model_class:
            raise ValueError(f"サポートされていない時間軸: {timeframe}")
        
        try:
            stock_objects = []
            for data in stock_data_list:
                stock_data = model_class(**data)
                stock_objects.append(stock_data)

            session.add_all(stock_objects)
            session.flush()
            return stock_objects
        except IntegrityError as e:
            raise StockDataError("一括作成中に重複データが検出されました")
        except SQLAlchemyError as e:
            raise DatabaseError(f"データベースエラー: {str(e)}")

    @staticmethod
    def get_by_symbol(session: Session, timeframe: str, symbol: str, 
                     limit: Optional[int] = None, offset: Optional[int] = None,
                     start_date: Optional[Union[date, datetime]] = None, 
                     end_date: Optional[Union[date, datetime]] = None):
        """銘柄コードで株価データを取得"""
        model_class = get_model_by_timeframe(timeframe)
        if not model_class:
            raise ValueError(f"サポートされていない時間軸: {timeframe}")
        
        try:
            query = session.query(model_class).filter(model_class.symbol == symbol)

            # 時間軸に応じた日時フィルタリング
            if timeframe in ['1m', '5m', '15m', '30m', '1h']:
                # 分足・時間足の場合はdatetimeカラムを使用
                if start_date:
                    query = query.filter(model_class.datetime >= start_date)
                if end_date:
                    query = query.filter(model_class.datetime <= end_date)
                query = query.order_by(model_class.datetime.desc())
            elif timeframe == '1d':
                # 日足の場合はdateカラムを使用
                if start_date:
                    query = query.filter(model_class.date >= start_date)
                if end_date:
                    query = query.filter(model_class.date <= end_date)
                query = query.order_by(model_class.date.desc())
            elif timeframe == '1wk':
                # 週足の場合はweek_start_dateカラムを使用
                if start_date:
                    query = query.filter(model_class.week_start_date >= start_date)
                if end_date:
                    query = query.filter(model_class.week_start_date <= end_date)
                query = query.order_by(model_class.week_start_date.desc())
            elif timeframe == '1mo':
                # 月足の場合は年月で比較
                if start_date:
                    if isinstance(start_date, datetime):
                        start_date = start_date.date()
                    query = query.filter(
                        (model_class.year > start_date.year) |
                        ((model_class.year == start_date.year) & (model_class.month >= start_date.month))
                    )
                if end_date:
                    if isinstance(end_date, datetime):
                        end_date = end_date.date()
                    query = query.filter(
                        (model_class.year < end_date.year) |
                        ((model_class.year == end_date.year) & (model_class.month <= end_date.month))
                    )
                query = query.order_by(model_class.year.desc(), model_class.month.desc())

            if offset:
                query = query.offset(offset)
            if limit:
                query = query.limit(limit)

            return query.all()
        except SQLAlchemyError as e:
            raise DatabaseError(f"データベースエラー: {str(e)}")

    @staticmethod
    def check_existing_data(session: Session, timeframe: str, symbol: str, 
                           datetime_value: Union[date, datetime]) -> bool:
        """指定された時刻のデータが既に存在するかチェック"""
        model_class = get_model_by_timeframe(timeframe)
        if not model_class:
            raise ValueError(f"サポートされていない時間軸: {timeframe}")
        
        try:
            if timeframe in ['1m', '5m', '15m', '30m', '1h']:
                # 分足・時間足の場合
                existing = session.query(model_class).filter(
                    model_class.symbol == symbol,
                    model_class.datetime == datetime_value
                ).first()
            elif timeframe == '1d':
                # 日足の場合
                existing = session.query(model_class).filter(
                    model_class.symbol == symbol,
                    model_class.date == datetime_value
                ).first()
            elif timeframe == '1wk':
                # 週足の場合
                existing = session.query(model_class).filter(
                    model_class.symbol == symbol,
                    model_class.week_start_date == datetime_value
                ).first()
            elif timeframe == '1mo':
                # 月足の場合
                if isinstance(datetime_value, datetime):
                    datetime_value = datetime_value.date()
                existing = session.query(model_class).filter(
                    model_class.symbol == symbol,
                    model_class.year == datetime_value.year,
                    model_class.month == datetime_value.month
                ).first()
            
            return existing is not None
        except SQLAlchemyError as e:
            raise DatabaseError(f"データベースエラー: {str(e)}")

# =============================================================================
# 既存のStockDailyCRUDクラス（後方互換性のため保持）
# =============================================================================

class StockDailyCRUD:
    """StockDailyモデルのCRUD操作クラス"""

    @staticmethod
    def create(session: Session, **kwargs) -> StockDaily:
        """新しい株価データを作成"""
        try:
            stock_data = StockDaily(**kwargs)
            session.add(stock_data)
            session.flush()
            return stock_data
        except IntegrityError as e:
            if "uk_stocks_daily_symbol_date" in str(e):
                raise StockDataError(f"銘柄 {kwargs.get('symbol')} の日付 {kwargs.get('date')} のデータは既に存在します")
            raise DatabaseError(f"データベース制約違反: {str(e)}")
        except SQLAlchemyError as e:
            raise DatabaseError(f"データベースエラー: {str(e)}")

    @staticmethod
    def get_by_id(session: Session, stock_id: int) -> Optional[StockDaily]:
        """IDで株価データを取得"""
        try:
            return session.query(StockDaily).filter(StockDaily.id == stock_id).first()
        except SQLAlchemyError as e:
            raise DatabaseError(f"データベースエラー: {str(e)}")

    @staticmethod
    def get_by_symbol_and_date(session: Session, symbol: str, date: date) -> Optional[StockDaily]:
        """銘柄コードと日付で株価データを取得"""
        try:
            return session.query(StockDaily).filter(
                StockDaily.symbol == symbol,
                StockDaily.date == date
            ).first()
        except SQLAlchemyError as e:
            raise DatabaseError(f"データベースエラー: {str(e)}")

    @staticmethod
    def get_by_symbol(session: Session, symbol: str, limit: Optional[int] = None, offset: Optional[int] = None,
                     start_date: Optional[date] = None, end_date: Optional[date] = None) -> List[StockDaily]:
        """銘柄コードで株価データを取得（日付降順）"""
        try:
            query = session.query(StockDaily).filter(StockDaily.symbol == symbol)

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
    def get_with_filters(session: Session, symbol: Optional[str] = None, limit: Optional[int] = None, 
                        offset: Optional[int] = None, start_date: Optional[date] = None, 
                        end_date: Optional[date] = None) -> List[StockDaily]:
        """フィルタ条件に基づく株価データを取得（日付降順）"""
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
    def get_all(session: Session, limit: Optional[int] = None, offset: Optional[int] = None) -> List[StockDaily]:
        """全ての株価データを取得（日付降順）"""
        try:
            query = session.query(StockDaily).order_by(StockDaily.date.desc(), StockDaily.symbol)

            if offset:
                query = query.offset(offset)
            if limit:
                query = query.limit(limit)

            return query.all()
        except SQLAlchemyError as e:
            raise DatabaseError(f"データベースエラー: {str(e)}")

    @staticmethod
    def update(session: Session, stock_id: int, **kwargs) -> Optional[StockDaily]:
        """株価データを更新"""
        try:
            stock_data = session.query(StockDaily).filter(StockDaily.id == stock_id).first()
            if not stock_data:
                return None

            for key, value in kwargs.items():
                if hasattr(stock_data, key):
                    setattr(stock_data, key, value)

            stock_data.updated_at = datetime.utcnow()
            session.flush()
            return stock_data
        except IntegrityError as e:
            if "uk_stocks_daily_symbol_date" in str(e):
                raise StockDataError(f"銘柄コードと日付の組み合わせが既に存在します")
            raise DatabaseError(f"データベース制約違反: {str(e)}")
        except SQLAlchemyError as e:
            raise DatabaseError(f"データベースエラー: {str(e)}")

    @staticmethod
    def delete(session: Session, stock_id: int) -> bool:
        """株価データを削除"""
        try:
            stock_data = session.query(StockDaily).filter(StockDaily.id == stock_id).first()
            if not stock_data:
                return False

            session.delete(stock_data)
            session.flush()
            return True
        except SQLAlchemyError as e:
            raise DatabaseError(f"データベースエラー: {str(e)}")

    @staticmethod
    def bulk_create(session: Session, stock_data_list: List[Dict[str, Any]]) -> List[StockDaily]:
        """複数の株価データを一括作成"""
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
        """銘柄のデータ件数を取得"""
        try:
            return session.query(StockDaily).filter(StockDaily.symbol == symbol).count()
        except SQLAlchemyError as e:
            raise DatabaseError(f"データベースエラー: {str(e)}")

    @staticmethod
    def get_latest_date_by_symbol(session: Session, symbol: str) -> Optional[date]:
        """銘柄の最新データ日付を取得"""
        try:
            result = session.query(StockDaily.date).filter(
                StockDaily.symbol == symbol
            ).order_by(StockDaily.date.desc()).first()
            return result[0] if result else None
        except SQLAlchemyError as e:
            raise DatabaseError(f"データベースエラー: {str(e)}")

    @staticmethod
    def count_all(session: Session) -> int:
        """全ての株価データ件数を取得"""
        try:
            return session.query(StockDaily).count()
        except SQLAlchemyError as e:
            raise DatabaseError(f"データベースエラー: {str(e)}")

    @staticmethod
    def count_with_filters(session: Session, symbol: Optional[str] = None,
                          start_date: Optional[date] = None, end_date: Optional[date] = None) -> int:
        """フィルタ条件に基づく株価データ件数を取得"""
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
