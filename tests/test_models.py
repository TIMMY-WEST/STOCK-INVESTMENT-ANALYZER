import pytest
from datetime import date
from decimal import Decimal

def test_stock_daily_model_import():
    """StockDailyモデルのインポートテスト"""
    from models import StockDaily, Base

    # モデルクラスの基本チェック
    assert StockDaily.__tablename__ == 'stocks_daily'
    assert hasattr(StockDaily, 'id')
    assert hasattr(StockDaily, 'symbol')
    assert hasattr(StockDaily, 'date')
    assert hasattr(StockDaily, 'open')
    assert hasattr(StockDaily, 'high')
    assert hasattr(StockDaily, 'low')
    assert hasattr(StockDaily, 'close')
    assert hasattr(StockDaily, 'volume')


def test_stock_daily_repr():
    """StockDailyモデルの文字列表現テスト"""
    from models import StockDaily

    stock = StockDaily()
    stock.symbol = "7203.T"
    stock.date = date(2024, 9, 13)
    stock.close = Decimal("2500.00")

    expected = "<StockDaily(symbol='7203.T', date='2024-09-13', close=2500.00)>"
    assert str(stock) == expected