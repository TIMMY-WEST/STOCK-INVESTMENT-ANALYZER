from sqlalchemy import Column, Integer, String, Date, Numeric, BigInteger, DateTime, UniqueConstraint, CheckConstraint, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func

Base = declarative_base()

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

    # 制約定義
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