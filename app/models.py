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
    """データベース操作エラーの基底クラス"""
    pass

class StockDataError(DatabaseError):
    """株価データ関連エラー"""
    pass

# ベースクラス：共通のカラムと制約を定義
class StockDataBase:
    """株価データの共通カラムと制約を定義するベースクラス"""
    
    # 共通カラム
    id = Column(Integer, primary_key=True, autoincrement=True)
    symbol = Column(String(20), nullable=False)
    open = Column(Numeric(10, 2), nullable=False)
    high = Column(Numeric(10, 2), nullable=False)
    low = Column(Numeric(10, 2), nullable=False)
    close = Column(Numeric(10, 2), nullable=False)
    volume = Column(BigInteger, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    def to_dict(self) -> Dict[str, Any]:
        """モデルインスタンスを辞書形式に変換"""
        result = {
            'id': self.id,
            'symbol': self.symbol,
            'open': float(self.open) if self.open else None,
            'high': float(self.high) if self.high else None,
            'low': float(self.low) if self.low else None,
            'close': float(self.close) if self.close else None,
            'volume': self.volume,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
        
        # 日付またはdatetimeフィールドを追加
        if hasattr(self, 'date'):
            result['date'] = self.date.isoformat() if self.date else None
        if hasattr(self, 'datetime'):
            result['datetime'] = self.datetime.isoformat() if self.datetime else None
            
        return result

# 1分足データテーブル
class Stocks1m(Base, StockDataBase):
    __tablename__ = 'stocks_1m'
    
    datetime = Column(DateTime(timezone=True), nullable=False)
    
    __table_args__ = (
        UniqueConstraint('symbol', 'datetime', name='uk_stocks_1m_symbol_datetime'),
        CheckConstraint('open >= 0 AND high >= 0 AND low >= 0 AND close >= 0', name='ck_stocks_1m_prices'),
        CheckConstraint('volume >= 0', name='ck_stocks_1m_volume'),
        CheckConstraint('high >= low AND high >= open AND high >= close AND low <= open AND low <= close', name='ck_stocks_1m_price_logic'),
        Index('idx_stocks_1m_symbol', 'symbol'),
        Index('idx_stocks_1m_datetime', 'datetime'),
        Index('idx_stocks_1m_symbol_datetime_desc', 'symbol', 'datetime'),
    )

    def __repr__(self):
        return f"<Stocks1m(symbol='{self.symbol}', datetime='{self.datetime}', close={self.close})>"

# 5分足データテーブル
class Stocks5m(Base, StockDataBase):
    __tablename__ = 'stocks_5m'
    
    datetime = Column(DateTime(timezone=True), nullable=False)
    
    __table_args__ = (
        UniqueConstraint('symbol', 'datetime', name='uk_stocks_5m_symbol_datetime'),
        CheckConstraint('open >= 0 AND high >= 0 AND low >= 0 AND close >= 0', name='ck_stocks_5m_prices'),
        CheckConstraint('volume >= 0', name='ck_stocks_5m_volume'),
        CheckConstraint('high >= low AND high >= open AND high >= close AND low <= open AND low <= close', name='ck_stocks_5m_price_logic'),
        Index('idx_stocks_5m_symbol', 'symbol'),
        Index('idx_stocks_5m_datetime', 'datetime'),
        Index('idx_stocks_5m_symbol_datetime_desc', 'symbol', 'datetime'),
    )

    def __repr__(self):
        return f"<Stocks5m(symbol='{self.symbol}', datetime='{self.datetime}', close={self.close})>"

# 15分足データテーブル
class Stocks15m(Base, StockDataBase):
    __tablename__ = 'stocks_15m'
    
    datetime = Column(DateTime(timezone=True), nullable=False)
    
    __table_args__ = (
        UniqueConstraint('symbol', 'datetime', name='uk_stocks_15m_symbol_datetime'),
        CheckConstraint('open >= 0 AND high >= 0 AND low >= 0 AND close >= 0', name='ck_stocks_15m_prices'),
        CheckConstraint('volume >= 0', name='ck_stocks_15m_volume'),
        CheckConstraint('high >= low AND high >= open AND high >= close AND low <= open AND low <= close', name='ck_stocks_15m_price_logic'),
        Index('idx_stocks_15m_symbol', 'symbol'),
        Index('idx_stocks_15m_datetime', 'datetime'),
        Index('idx_stocks_15m_symbol_datetime_desc', 'symbol', 'datetime'),
    )

    def __repr__(self):
        return f"<Stocks15m(symbol='{self.symbol}', datetime='{self.datetime}', close={self.close})>"

# 30分足データテーブル
class Stocks30m(Base, StockDataBase):
    __tablename__ = 'stocks_30m'
    
    datetime = Column(DateTime(timezone=True), nullable=False)
    
    __table_args__ = (
        UniqueConstraint('symbol', 'datetime', name='uk_stocks_30m_symbol_datetime'),
        CheckConstraint('open >= 0 AND high >= 0 AND low >= 0 AND close >= 0', name='ck_stocks_30m_prices'),
        CheckConstraint('volume >= 0', name='ck_stocks_30m_volume'),
        CheckConstraint('high >= low AND high >= open AND high >= close AND low <= open AND low <= close', name='ck_stocks_30m_price_logic'),
        Index('idx_stocks_30m_symbol', 'symbol'),
        Index('idx_stocks_30m_datetime', 'datetime'),
        Index('idx_stocks_30m_symbol_datetime_desc', 'symbol', 'datetime'),
    )

    def __repr__(self):
        return f"<Stocks30m(symbol='{self.symbol}', datetime='{self.datetime}', close={self.close})>"

# 1時間足データテーブル
class Stocks1h(Base, StockDataBase):
    __tablename__ = 'stocks_1h'
    
    datetime = Column(DateTime(timezone=True), nullable=False)
    
    __table_args__ = (
        UniqueConstraint('symbol', 'datetime', name='uk_stocks_1h_symbol_datetime'),
        CheckConstraint('open >= 0 AND high >= 0 AND low >= 0 AND close >= 0', name='ck_stocks_1h_prices'),
        CheckConstraint('volume >= 0', name='ck_stocks_1h_volume'),
        CheckConstraint('high >= low AND high >= open AND high >= close AND low <= open AND low <= close', name='ck_stocks_1h_price_logic'),
        Index('idx_stocks_1h_symbol', 'symbol'),
        Index('idx_stocks_1h_datetime', 'datetime'),
        Index('idx_stocks_1h_symbol_datetime_desc', 'symbol', 'datetime'),
    )

    def __repr__(self):
        return f"<Stocks1h(symbol='{self.symbol}', datetime='{self.datetime}', close={self.close})>"

# 日足データテーブル（既存のstocks_dailyをstocks_1dに変更）
class Stocks1d(Base, StockDataBase):
    __tablename__ = 'stocks_1d'
    
    date = Column(Date, nullable=False)
    
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
        return f"<Stocks1d(symbol='{self.symbol}', date='{self.date}', close={self.close})>"

# 週足データテーブル
class Stocks1wk(Base, StockDataBase):
    __tablename__ = 'stocks_1wk'
    
    date = Column(Date, nullable=False)
    
    __table_args__ = (
        UniqueConstraint('symbol', 'date', name='uk_stocks_1wk_symbol_date'),
        CheckConstraint('open >= 0 AND high >= 0 AND low >= 0 AND close >= 0', name='ck_stocks_1wk_prices'),
        CheckConstraint('volume >= 0', name='ck_stocks_1wk_volume'),
        CheckConstraint('high >= low AND high >= open AND high >= close AND low <= open AND low <= close', name='ck_stocks_1wk_price_logic'),
        Index('idx_stocks_1wk_symbol', 'symbol'),
        Index('idx_stocks_1wk_date', 'date'),
        Index('idx_stocks_1wk_symbol_date_desc', 'symbol', 'date'),
    )

    def __repr__(self):
        return f"<Stocks1wk(symbol='{self.symbol}', date='{self.date}', close={self.close})>"

# 月足データテーブル
class Stocks1mo(Base, StockDataBase):
    __tablename__ = 'stocks_1mo'
    
    date = Column(Date, nullable=False)
    
    __table_args__ = (
        UniqueConstraint('symbol', 'date', name='uk_stocks_1mo_symbol_date'),
        CheckConstraint('open >= 0 AND high >= 0 AND low >= 0 AND close >= 0', name='ck_stocks_1mo_prices'),
        CheckConstraint('volume >= 0', name='ck_stocks_1mo_volume'),
        CheckConstraint('high >= low AND high >= open AND high >= close AND low <= open AND low <= close', name='ck_stocks_1mo_price_logic'),
        Index('idx_stocks_1mo_symbol', 'symbol'),
        Index('idx_stocks_1mo_date', 'date'),
        Index('idx_stocks_1mo_symbol_date_desc', 'symbol', 'date'),
    )

    def __repr__(self):
        return f"<Stocks1mo(symbol='{self.symbol}', date='{self.date}', close={self.close})>"

# 既存のStockDailyクラスは後方互換性のためにStocks1dのエイリアスとして残す
StockDaily = Stocks1d

# 銘柄マスタテーブル (Phase 2)
class StockMaster(Base):
    """銘柄マスタテーブル - JPX銘柄一覧を管理（全項目対応版）"""
    __tablename__ = 'stock_master'

    id = Column(Integer, primary_key=True, autoincrement=True)

    # 基本情報
    stock_code = Column(String(10), unique=True, nullable=False)  # 銘柄コード（例: "7203"）
    stock_name = Column(String(100), nullable=False)              # 銘柄名（例: "トヨタ自動車"）
    market_category = Column(String(50))                          # 市場区分（例: "プライム（内国株式）"）

    # 業種情報
    sector_code_33 = Column(String(10))                           # 33業種コード
    sector_name_33 = Column(String(100))                          # 33業種区分
    sector_code_17 = Column(String(10))                           # 17業種コード
    sector_name_17 = Column(String(100))                          # 17業種区分

    # 規模情報
    scale_code = Column(String(10))                               # 規模コード
    scale_category = Column(String(50))                           # 規模区分（TOPIX分類）

    # データ管理
    data_date = Column(String(8))                                 # データ取得日（YYYYMMDD形式）
    is_active = Column(Integer, default=1, nullable=False)        # 有効フラグ（1=有効, 0=無効）
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    __table_args__ = (
        Index('idx_stock_master_code', 'stock_code'),
        Index('idx_stock_master_active', 'is_active'),
        Index('idx_stock_master_market', 'market_category'),
        Index('idx_stock_master_sector_33', 'sector_code_33'),
    )

    def __repr__(self):
        return f"<StockMaster(stock_code='{self.stock_code}', stock_name='{self.stock_name}', is_active={self.is_active})>"

    def to_dict(self) -> Dict[str, Any]:
        """モデルインスタンスを辞書形式に変換"""
        return {
            'id': self.id,
            'stock_code': self.stock_code,
            'stock_name': self.stock_name,
            'market_category': self.market_category,
            'sector_code_33': self.sector_code_33,
            'sector_name_33': self.sector_name_33,
            'sector_code_17': self.sector_code_17,
            'sector_name_17': self.sector_name_17,
            'scale_code': self.scale_code,
            'scale_category': self.scale_category,
            'data_date': self.data_date,
            'is_active': bool(self.is_active),
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

# 銘柄一覧更新履歴テーブル (Phase 2)
class StockMasterUpdate(Base):
    """銘柄一覧更新履歴テーブル - 銘柄マスタの更新履歴を管理"""
    __tablename__ = 'stock_master_updates'

    id = Column(Integer, primary_key=True, autoincrement=True)
    update_type = Column(String(20), nullable=False)              # 'manual', 'scheduled'
    total_stocks = Column(Integer, nullable=False)                # 総銘柄数
    added_stocks = Column(Integer, default=0)                     # 新規追加銘柄数
    updated_stocks = Column(Integer, default=0)                   # 更新銘柄数
    removed_stocks = Column(Integer, default=0)                   # 削除（無効化）銘柄数
    status = Column(String(20), nullable=False)                   # 'success', 'failed'
    error_message = Column(String)                                # エラーメッセージ
    started_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True))

    def __repr__(self):
        return f"<StockMasterUpdate(id={self.id}, update_type='{self.update_type}', status='{self.status}')>"

    def to_dict(self) -> Dict[str, Any]:
        """モデルインスタンスを辞書形式に変換"""
        return {
            'id': self.id,
            'update_type': self.update_type,
            'total_stocks': self.total_stocks,
            'added_stocks': self.added_stocks,
            'updated_stocks': self.updated_stocks,
            'removed_stocks': self.removed_stocks,
            'status': self.status,
            'error_message': self.error_message,
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None
        }

# データベース設定
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
