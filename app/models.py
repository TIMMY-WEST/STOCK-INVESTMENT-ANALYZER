from sqlalchemy import Column, Integer, String, Date, Numeric, BigInteger, DateTime, UniqueConstraint, CheckConstraint, Index, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.sql import func
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from typing import List, Optional, Dict, Any
from datetime import date, datetime
from contextlib import contextmanager
import os
from dotenv import load_dotenv

load_dotenv()

Base = declarative_base()


class DatabaseError(Exception):
    """データベース関連のエラー"""
    pass


class StockDataError(DatabaseError):
    """株価データ関連のエラー"""
    pass


class StockDaily(Base):
    __tablename__ = 'stocks_daily'

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

    # テーブル制約とインデックス
    __table_args__ = (
        UniqueConstraint('symbol', 'date', name='uk_stocks_daily_symbol_date'),
        CheckConstraint('open >= 0 AND high >= 0 AND low >= 0 AND close >= 0', name='ck_stocks_daily_prices'),
        CheckConstraint('volume >= 0', name='ck_stocks_daily_volume'),
        CheckConstraint('high >= low AND high >= open AND high >= close AND low <= open AND low <= close', name='ck_stocks_daily_price_logic'),
        Index('idx_stocks_daily_symbol', 'symbol'),
        Index('idx_stocks_daily_date', 'date'),
        Index('idx_stocks_daily_symbol_date_desc', 'symbol', 'date'),
    )

    def __repr__(self):
        return f"<StockDaily(symbol='{self.symbol}', date='{self.date}', close={self.close})>"

    def to_dict(self) -> Dict[str, Any]:
        """オブジェクトを辞書形式に変換"""
        return {
            'id': self.id,
            'symbol': self.symbol,
            'date': self.date.isoformat() if self.date else None,
            'open': float(self.open) if self.open else None,
            'high': float(self.high) if self.high else None,
            'low': float(self.low) if self.low else None,
            'close': float(self.close) if self.close else None,
            'volume': int(self.volume) if self.volume else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class StockIntraday(Base):
    """分足・時間足データ用のベースモデル"""
    __tablename__ = 'stocks_intraday'

    # カラム定義
    id = Column(Integer, primary_key=True, autoincrement=True)
    symbol = Column(String(20), nullable=False)
    datetime = Column(DateTime(timezone=True), nullable=False)
    interval = Column(String(10), nullable=False)  # 1m, 5m, 15m, 30m, 1h
    open = Column(Numeric(10, 2), nullable=False)
    high = Column(Numeric(10, 2), nullable=False)
    low = Column(Numeric(10, 2), nullable=False)
    close = Column(Numeric(10, 2), nullable=False)
    volume = Column(BigInteger, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # テーブル制約とインデックス
    __table_args__ = (
        UniqueConstraint('symbol', 'datetime', 'interval', name='uk_stocks_intraday_symbol_datetime_interval'),
        CheckConstraint('open >= 0 AND high >= 0 AND low >= 0 AND close >= 0', name='ck_stocks_intraday_prices'),
        CheckConstraint('volume >= 0', name='ck_stocks_intraday_volume'),
        CheckConstraint('high >= low AND high >= open AND high >= close AND low <= open AND low <= close', name='ck_stocks_intraday_price_logic'),
        CheckConstraint("interval IN ('1m', '5m', '15m', '30m', '1h')", name='ck_stocks_intraday_interval'),
        Index('idx_stocks_intraday_symbol', 'symbol'),
        Index('idx_stocks_intraday_datetime', 'datetime'),
        Index('idx_stocks_intraday_interval', 'interval'),
        Index('idx_stocks_intraday_symbol_interval_datetime_desc', 'symbol', 'interval', 'datetime'),
    )

    def __repr__(self):
        return f"<StockIntraday(symbol='{self.symbol}', datetime='{self.datetime}', interval='{self.interval}', close={self.close})>"

    def to_dict(self) -> Dict[str, Any]:
        """オブジェクトを辞書形式に変換"""
        return {
            'id': self.id,
            'symbol': self.symbol,
            'datetime': self.datetime.isoformat() if self.datetime else None,
            'interval': self.interval,
            'open': float(self.open) if self.open else None,
            'high': float(self.high) if self.high else None,
            'low': float(self.low) if self.low else None,
            'close': float(self.close) if self.close else None,
            'volume': int(self.volume) if self.volume else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class StockWeekly(Base):
    """週足データ用のモデル"""
    __tablename__ = 'stocks_weekly'

    # カラム定義
    id = Column(Integer, primary_key=True, autoincrement=True)
    symbol = Column(String(20), nullable=False)
    week_start_date = Column(Date, nullable=False)  # 週の開始日
    open = Column(Numeric(10, 2), nullable=False)
    high = Column(Numeric(10, 2), nullable=False)
    low = Column(Numeric(10, 2), nullable=False)
    close = Column(Numeric(10, 2), nullable=False)
    volume = Column(BigInteger, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # テーブル制約とインデックス
    __table_args__ = (
        UniqueConstraint('symbol', 'week_start_date', name='uk_stocks_weekly_symbol_week'),
        CheckConstraint('open >= 0 AND high >= 0 AND low >= 0 AND close >= 0', name='ck_stocks_weekly_prices'),
        CheckConstraint('volume >= 0', name='ck_stocks_weekly_volume'),
        CheckConstraint('high >= low AND high >= open AND high >= close AND low <= open AND low <= close', name='ck_stocks_weekly_price_logic'),
        Index('idx_stocks_weekly_symbol', 'symbol'),
        Index('idx_stocks_weekly_week_start_date', 'week_start_date'),
        Index('idx_stocks_weekly_symbol_week_desc', 'symbol', 'week_start_date'),
    )

    def __repr__(self):
        return f"<StockWeekly(symbol='{self.symbol}', week_start_date='{self.week_start_date}', close={self.close})>"

    def to_dict(self) -> Dict[str, Any]:
        """オブジェクトを辞書形式に変換"""
        return {
            'id': self.id,
            'symbol': self.symbol,
            'week_start_date': self.week_start_date.isoformat() if self.week_start_date else None,
            'open': float(self.open) if self.open else None,
            'high': float(self.high) if self.high else None,
            'low': float(self.low) if self.low else None,
            'close': float(self.close) if self.close else None,
            'volume': int(self.volume) if self.volume else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class StockMonthly(Base):
    """月足データ用のモデル"""
    __tablename__ = 'stocks_monthly'

    # カラム定義
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

    # テーブル制約とインデックス
    __table_args__ = (
        UniqueConstraint('symbol', 'year', 'month', name='uk_stocks_monthly_symbol_year_month'),
        CheckConstraint('open >= 0 AND high >= 0 AND low >= 0 AND close >= 0', name='ck_stocks_monthly_prices'),
        CheckConstraint('volume >= 0', name='ck_stocks_monthly_volume'),
        CheckConstraint('high >= low AND high >= open AND high >= close AND low <= open AND low <= close', name='ck_stocks_monthly_price_logic'),
        CheckConstraint('month >= 1 AND month <= 12', name='ck_stocks_monthly_month'),
        CheckConstraint('year >= 1900', name='ck_stocks_monthly_year'),
        Index('idx_stocks_monthly_symbol', 'symbol'),
        Index('idx_stocks_monthly_year_month', 'year', 'month'),
        Index('idx_stocks_monthly_symbol_year_month_desc', 'symbol', 'year', 'month'),
    )

    def __repr__(self):
        return f"<StockMonthly(symbol='{self.symbol}', year={self.year}, month={self.month}, close={self.close})>"

    def to_dict(self) -> Dict[str, Any]:
        """オブジェクトを辞書形式に変換"""
        return {
            'id': self.id,
            'symbol': self.symbol,
            'year': self.year,
            'month': self.month,
            'open': float(self.open) if self.open else None,
            'high': float(self.high) if self.high else None,
            'low': float(self.low) if self.low else None,
            'close': float(self.close) if self.close else None,
            'volume': int(self.volume) if self.volume else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


# データベース接続設定
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


class StockIntradayCRUD:
    """StockIntradayモデルのCRUD操作クラス"""

    @staticmethod
    def create(session: Session, **kwargs) -> StockIntraday:
        """分足・時間足データを作成"""
        try:
            stock_data = StockIntraday(**kwargs)
            session.add(stock_data)
            session.flush()
            return stock_data
        except IntegrityError as e:
            if "uk_stocks_intraday_symbol_datetime_interval" in str(e):
                raise StockDataError(f"銘柄コード、日時、時間軸の組み合わせが既に存在します")
            raise DatabaseError(f"データベース制約違反: {str(e)}")
        except SQLAlchemyError as e:
            raise DatabaseError(f"データベースエラー: {str(e)}")

    @staticmethod
    def get_by_symbol_and_datetime(session: Session, symbol: str, datetime: datetime, interval: str) -> Optional[StockIntraday]:
        """銘柄コード、日時、時間軸で分足・時間足データを取得"""
        try:
            return session.query(StockIntraday).filter(
                StockIntraday.symbol == symbol,
                StockIntraday.datetime == datetime,
                StockIntraday.interval == interval
            ).first()
        except SQLAlchemyError as e:
            raise DatabaseError(f"データベースエラー: {str(e)}")

    @staticmethod
    def get_by_symbol_and_interval(session: Session, symbol: str, interval: str, limit: Optional[int] = None, 
                                  offset: Optional[int] = None, start_datetime: Optional[datetime] = None, 
                                  end_datetime: Optional[datetime] = None) -> List[StockIntraday]:
        """銘柄コードと時間軸で分足・時間足データを取得（日時降順）"""
        try:
            query = session.query(StockIntraday).filter(
                StockIntraday.symbol == symbol,
                StockIntraday.interval == interval
            )

            if start_datetime:
                query = query.filter(StockIntraday.datetime >= start_datetime)
            if end_datetime:
                query = query.filter(StockIntraday.datetime <= end_datetime)

            query = query.order_by(StockIntraday.datetime.desc())

            if offset:
                query = query.offset(offset)
            if limit:
                query = query.limit(limit)

            return query.all()
        except SQLAlchemyError as e:
            raise DatabaseError(f"データベースエラー: {str(e)}")

    @staticmethod
    def bulk_create(session: Session, stock_data_list: List[Dict[str, Any]]) -> List[StockIntraday]:
        """複数の分足・時間足データを一括作成"""
        try:
            stock_objects = []
            for data in stock_data_list:
                stock_data = StockIntraday(**data)
                stock_objects.append(stock_data)

            session.add_all(stock_objects)
            session.flush()
            return stock_objects
        except IntegrityError as e:
            if "uk_stocks_intraday_symbol_datetime_interval" in str(e):
                raise StockDataError("一括作成中に重複データが検出されました")
            raise DatabaseError(f"データベース制約違反: {str(e)}")
        except SQLAlchemyError as e:
            raise DatabaseError(f"データベースエラー: {str(e)}")

    @staticmethod
    def get_latest_datetime_by_symbol_and_interval(session: Session, symbol: str, interval: str) -> Optional[datetime]:
        """銘柄と時間軸の最新データ日時を取得"""
        try:
            result = session.query(StockIntraday.datetime).filter(
                StockIntraday.symbol == symbol,
                StockIntraday.interval == interval
            ).order_by(StockIntraday.datetime.desc()).first()
            return result[0] if result else None
        except SQLAlchemyError as e:
            raise DatabaseError(f"データベースエラー: {str(e)}")


class StockWeeklyCRUD:
    """StockWeeklyモデルのCRUD操作クラス"""

    @staticmethod
    def create(session: Session, **kwargs) -> StockWeekly:
        """週足データを作成"""
        try:
            stock_data = StockWeekly(**kwargs)
            session.add(stock_data)
            session.flush()
            return stock_data
        except IntegrityError as e:
            if "uk_stocks_weekly_symbol_week" in str(e):
                raise StockDataError(f"銘柄コードと週の組み合わせが既に存在します")
            raise DatabaseError(f"データベース制約違反: {str(e)}")
        except SQLAlchemyError as e:
            raise DatabaseError(f"データベースエラー: {str(e)}")

    @staticmethod
    def get_by_symbol_and_week(session: Session, symbol: str, week_start_date: date) -> Optional[StockWeekly]:
        """銘柄コードと週開始日で週足データを取得"""
        try:
            return session.query(StockWeekly).filter(
                StockWeekly.symbol == symbol,
                StockWeekly.week_start_date == week_start_date
            ).first()
        except SQLAlchemyError as e:
            raise DatabaseError(f"データベースエラー: {str(e)}")

    @staticmethod
    def get_by_symbol(session: Session, symbol: str, limit: Optional[int] = None, offset: Optional[int] = None,
                     start_date: Optional[date] = None, end_date: Optional[date] = None) -> List[StockWeekly]:
        """銘柄コードで週足データを取得（週開始日降順）"""
        try:
            query = session.query(StockWeekly).filter(StockWeekly.symbol == symbol)

            if start_date:
                query = query.filter(StockWeekly.week_start_date >= start_date)
            if end_date:
                query = query.filter(StockWeekly.week_start_date <= end_date)

            query = query.order_by(StockWeekly.week_start_date.desc())

            if offset:
                query = query.offset(offset)
            if limit:
                query = query.limit(limit)

            return query.all()
        except SQLAlchemyError as e:
            raise DatabaseError(f"データベースエラー: {str(e)}")

    @staticmethod
    def bulk_create(session: Session, stock_data_list: List[Dict[str, Any]]) -> List[StockWeekly]:
        """複数の週足データを一括作成"""
        try:
            stock_objects = []
            for data in stock_data_list:
                stock_data = StockWeekly(**data)
                stock_objects.append(stock_data)

            session.add_all(stock_objects)
            session.flush()
            return stock_objects
        except IntegrityError as e:
            if "uk_stocks_weekly_symbol_week" in str(e):
                raise StockDataError("一括作成中に重複データが検出されました")
            raise DatabaseError(f"データベース制約違反: {str(e)}")
        except SQLAlchemyError as e:
            raise DatabaseError(f"データベースエラー: {str(e)}")


class StockMonthlyCRUD:
    """StockMonthlyモデルのCRUD操作クラス"""

    @staticmethod
    def create(session: Session, **kwargs) -> StockMonthly:
        """月足データを作成"""
        try:
            stock_data = StockMonthly(**kwargs)
            session.add(stock_data)
            session.flush()
            return stock_data
        except IntegrityError as e:
            if "uk_stocks_monthly_symbol_year_month" in str(e):
                raise StockDataError(f"銘柄コード、年、月の組み合わせが既に存在します")
            raise DatabaseError(f"データベース制約違反: {str(e)}")
        except SQLAlchemyError as e:
            raise DatabaseError(f"データベースエラー: {str(e)}")

    @staticmethod
    def get_by_symbol_and_month(session: Session, symbol: str, year: int, month: int) -> Optional[StockMonthly]:
        """銘柄コード、年、月で月足データを取得"""
        try:
            return session.query(StockMonthly).filter(
                StockMonthly.symbol == symbol,
                StockMonthly.year == year,
                StockMonthly.month == month
            ).first()
        except SQLAlchemyError as e:
            raise DatabaseError(f"データベースエラー: {str(e)}")

    @staticmethod
    def get_by_symbol(session: Session, symbol: str, limit: Optional[int] = None, offset: Optional[int] = None,
                     start_year: Optional[int] = None, start_month: Optional[int] = None,
                     end_year: Optional[int] = None, end_month: Optional[int] = None) -> List[StockMonthly]:
        """銘柄コードで月足データを取得（年月降順）"""
        try:
            query = session.query(StockMonthly).filter(StockMonthly.symbol == symbol)

            if start_year and start_month:
                query = query.filter(
                    (StockMonthly.year > start_year) | 
                    ((StockMonthly.year == start_year) & (StockMonthly.month >= start_month))
                )
            if end_year and end_month:
                query = query.filter(
                    (StockMonthly.year < end_year) | 
                    ((StockMonthly.year == end_year) & (StockMonthly.month <= end_month))
                )

            query = query.order_by(StockMonthly.year.desc(), StockMonthly.month.desc())

            if offset:
                query = query.offset(offset)
            if limit:
                query = query.limit(limit)

            return query.all()
        except SQLAlchemyError as e:
            raise DatabaseError(f"データベースエラー: {str(e)}")

    @staticmethod
    def bulk_create(session: Session, stock_data_list: List[Dict[str, Any]]) -> List[StockMonthly]:
        """複数の月足データを一括作成"""
        try:
            stock_objects = []
            for data in stock_data_list:
                stock_data = StockMonthly(**data)
                stock_objects.append(stock_data)

            session.add_all(stock_objects)
            session.flush()
            return stock_objects
        except IntegrityError as e:
            if "uk_stocks_monthly_symbol_year_month" in str(e):
                raise StockDataError("一括作成中に重複データが検出されました")
            raise DatabaseError(f"データベース制約違反: {str(e)}")
        except SQLAlchemyError as e:
            raise DatabaseError(f"データベースエラー: {str(e)}")


# 時間軸とモデル・CRUDクラスのマッピング
TIMEFRAME_MODELS = {
    '1d': {'model': StockDaily, 'crud': StockDailyCRUD},
    '1wk': {'model': StockWeekly, 'crud': StockWeeklyCRUD},
    '1mo': {'model': StockMonthly, 'crud': StockMonthlyCRUD},
    '1m': {'model': StockIntraday, 'crud': StockIntradayCRUD},
    '5m': {'model': StockIntraday, 'crud': StockIntradayCRUD},
    '15m': {'model': StockIntraday, 'crud': StockIntradayCRUD},
    '30m': {'model': StockIntraday, 'crud': StockIntradayCRUD},
    '1h': {'model': StockIntraday, 'crud': StockIntradayCRUD},
}
