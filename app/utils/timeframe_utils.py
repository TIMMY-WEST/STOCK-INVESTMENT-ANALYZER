"""時間軸ユーティリティ

yfinanceの時間軸(interval)とデータベースモデルのマッピングを提供します。
"""

from typing import Dict, Type, Literal
from models import (
    Stocks1m, Stocks5m, Stocks15m, Stocks30m,
    Stocks1h, Stocks1d, Stocks1wk, Stocks1mo,
    StockDataBase
)

# 時間軸の型定義
TimeframeInterval = Literal['1m', '5m', '15m', '30m', '1h', '1d', '1wk', '1mo']

# yfinance interval と データベースモデルのマッピング
TIMEFRAME_MODEL_MAP: Dict[str, Type[StockDataBase]] = {
    '1m': Stocks1m,
    '5m': Stocks5m,
    '15m': Stocks15m,
    '30m': Stocks30m,
    '1h': Stocks1h,
    '1d': Stocks1d,
    '1wk': Stocks1wk,
    '1mo': Stocks1mo,
}

# 時間軸の表示名マッピング
TIMEFRAME_DISPLAY_NAME: Dict[str, str] = {
    '1m': '1分足',
    '5m': '5分足',
    '15m': '15分足',
    '30m': '30分足',
    '1h': '1時間足',
    '1d': '日足',
    '1wk': '週足',
    '1mo': '月足',
}

# 時間軸の優先順位（データ量が多い順）
TIMEFRAME_PRIORITY: Dict[str, int] = {
    '1m': 1,   # 最優先（データ量が最大）
    '5m': 2,
    '15m': 3,
    '30m': 4,
    '1h': 5,
    '1d': 6,
    '1wk': 7,
    '1mo': 8,  # 最低優先（データ量が最小）
}

# 時間軸の推奨取得期間（yfinance period）
TIMEFRAME_RECOMMENDED_PERIOD: Dict[str, str] = {
    '1m': '7d',    # 1分足: 過去7日間
    '5m': '60d',   # 5分足: 過去60日間
    '15m': '60d',  # 15分足: 過去60日間
    '30m': '60d',  # 30分足: 過去60日間
    '1h': '730d',  # 1時間足: 過去730日間（2年）
    '1d': 'max',   # 日足: 全期間
    '1wk': 'max',  # 週足: 全期間
    '1mo': 'max',  # 月足: 全期間
}


def get_model_for_interval(interval: str) -> Type[StockDataBase]:
    """
    yfinance intervalに対応するデータベースモデルを取得

    Args:
        interval: yfinance interval ('1m', '5m', '15m', '30m', '1h', '1d', '1wk', '1mo')

    Returns:
        対応するデータベースモデルクラス

    Raises:
        ValueError: サポートされていないintervalの場合
    """
    if interval not in TIMEFRAME_MODEL_MAP:
        raise ValueError(
            f"サポートされていない時間軸: {interval}. "
            f"サポート時間軸: {list(TIMEFRAME_MODEL_MAP.keys())}"
        )
    return TIMEFRAME_MODEL_MAP[interval]


def get_display_name(interval: str) -> str:
    """
    時間軸の表示名を取得

    Args:
        interval: yfinance interval

    Returns:
        時間軸の日本語表示名
    """
    return TIMEFRAME_DISPLAY_NAME.get(interval, interval)


def get_recommended_period(interval: str) -> str:
    """
    時間軸の推奨取得期間を取得

    Args:
        interval: yfinance interval

    Returns:
        推奨取得期間（yfinance period）
    """
    return TIMEFRAME_RECOMMENDED_PERIOD.get(interval, '1y')


def is_intraday_interval(interval: str) -> bool:
    """
    分足・時間足（日内）の時間軸かどうかを判定

    Args:
        interval: yfinance interval

    Returns:
        True: 分足・時間足（datetime使用）
        False: 日足・週足・月足（date使用）
    """
    return interval in ['1m', '5m', '15m', '30m', '1h']


def get_all_intervals() -> list[str]:
    """
    サポートされている全ての時間軸を取得

    Returns:
        時間軸のリスト
    """
    return list(TIMEFRAME_MODEL_MAP.keys())


def validate_interval(interval: str) -> bool:
    """
    時間軸が有効かどうかを検証

    Args:
        interval: 検証する時間軸

    Returns:
        True: 有効な時間軸
        False: 無効な時間軸
    """
    return interval in TIMEFRAME_MODEL_MAP
