"""株価データ取得サービス

yfinanceを使用して各時間軸の株価データを取得します。
"""

import yfinance as yf
import pandas as pd
from typing import Optional, Dict, Any
from datetime import datetime, date
import logging
from app.utils.timeframe_utils import (
    validate_interval,
    get_display_name,
    get_recommended_period,
    is_intraday_interval
)

logger = logging.getLogger(__name__)


class StockDataFetchError(Exception):
    """データ取得エラー"""
    pass


class StockDataFetcher:
    """株価データ取得クラス"""

    def __init__(self):
        """初期化"""
        self.logger = logger

    def fetch_stock_data(
        self,
        symbol: str,
        interval: str = '1d',
        period: Optional[str] = None,
        start: Optional[str] = None,
        end: Optional[str] = None
    ) -> pd.DataFrame:
        """
        株価データを取得

        Args:
            symbol: 銘柄コード（例: '7203.T'）
            interval: 時間軸（'1m', '5m', '15m', '30m', '1h', '1d', '1wk', '1mo'）
            period: 取得期間（'1d', '5d', '1mo', '3mo', '6mo', '1y', '2y', '5y', '10y', 'ytd', 'max'）
            start: 開始日（YYYY-MM-DD形式、periodと排他）
            end: 終了日（YYYY-MM-DD形式、periodと排他）

        Returns:
            株価データのDataFrame

        Raises:
            StockDataFetchError: データ取得失敗時
        """
        try:
            # 時間軸の検証
            if not validate_interval(interval):
                raise ValueError(f"サポートされていない時間軸: {interval}")

            # 期間の設定
            if period is None and start is None and end is None:
                period = get_recommended_period(interval)
                self.logger.info(
                    f"期間未指定のため推奨期間を使用: {period} (時間軸: {get_display_name(interval)})"
                )

            # yfinanceでデータ取得
            self.logger.info(
                f"株価データ取得開始: {symbol} (時間軸: {get_display_name(interval)}, "
                f"期間: {period or f'{start}~{end}'})"
            )

            ticker = yf.Ticker(symbol)

            # データ取得
            if period:
                df = ticker.history(period=period, interval=interval)
            else:
                df = ticker.history(start=start, end=end, interval=interval)

            # データの検証
            if df.empty:
                raise StockDataFetchError(
                    f"データが取得できませんでした: {symbol} "
                    f"(時間軸: {get_display_name(interval)})"
                )

            self.logger.info(
                f"株価データ取得成功: {symbol} - {len(df)}件 "
                f"(時間軸: {get_display_name(interval)})"
            )

            return df

        except Exception as e:
            error_msg = (
                f"株価データ取得エラー: {symbol} "
                f"(時間軸: {get_display_name(interval)}): {str(e)}"
            )
            self.logger.error(error_msg)
            raise StockDataFetchError(error_msg) from e

    def fetch_multiple_timeframes(
        self,
        symbol: str,
        intervals: list[str],
        period: Optional[str] = None
    ) -> Dict[str, pd.DataFrame]:
        """
        複数時間軸のデータを一度に取得

        Args:
            symbol: 銘柄コード
            intervals: 時間軸のリスト
            period: 取得期間（各時間軸で共通、Noneの場合は推奨期間を使用）

        Returns:
            {interval: DataFrame} の辞書

        Raises:
            StockDataFetchError: データ取得失敗時
        """
        results = {}
        errors = []

        for interval in intervals:
            try:
                df = self.fetch_stock_data(
                    symbol=symbol,
                    interval=interval,
                    period=period
                )
                results[interval] = df
            except StockDataFetchError as e:
                errors.append(str(e))
                self.logger.warning(f"時間軸 {interval} のデータ取得をスキップ: {e}")

        if not results and errors:
            raise StockDataFetchError(
                f"全ての時間軸でデータ取得に失敗しました: {symbol}\n"
                + "\n".join(errors)
            )

        return results

    def convert_to_dict(self, df: pd.DataFrame, interval: str) -> list[Dict[str, Any]]:
        """
        DataFrameを辞書リストに変換（データベース保存用）

        Args:
            df: yfinanceから取得したDataFrame
            interval: 時間軸

        Returns:
            データベース保存用の辞書リスト
        """
        records = []
        is_intraday = is_intraday_interval(interval)

        for index, row in df.iterrows():
            record = {
                'open': float(row['Open']),
                'high': float(row['High']),
                'low': float(row['Low']),
                'close': float(row['Close']),
                'volume': int(row['Volume'])
            }

            # 日付・日時フィールドの設定
            if is_intraday:
                # 分足・時間足: datetime使用
                if isinstance(index, pd.Timestamp):
                    record['datetime'] = index.to_pydatetime()
                else:
                    record['datetime'] = datetime.fromisoformat(str(index))
            else:
                # 日足・週足・月足: date使用
                if isinstance(index, pd.Timestamp):
                    record['date'] = index.date()
                else:
                    record['date'] = date.fromisoformat(str(index).split()[0])

            records.append(record)

        return records

    def get_latest_data_date(
        self,
        symbol: str,
        interval: str = '1d'
    ) -> Optional[datetime]:
        """
        最新データの日時を取得（データベース更新判定用）

        Args:
            symbol: 銘柄コード
            interval: 時間軸

        Returns:
            最新データの日時、データがない場合はNone
        """
        try:
            df = self.fetch_stock_data(symbol, interval, period='1d')
            if not df.empty:
                return df.index[-1].to_pydatetime()
            return None
        except StockDataFetchError:
            return None
