"""株価データ取得サービス.

このモジュールは株価データのAPI通信機能を提供します。
"""

import logging
from typing import Optional

import pandas as pd
import yfinance as yf

from services.stock_data_validator import StockDataValidator


logger = logging.getLogger(__name__)


class StockDataFetchError(Exception):
    """株価データ取得エラー."""

    pass


class StockDataFetcher:
    """株価データ取得クラス（API通信専用）."""

    def __init__(self):
        """初期化."""
        self.logger = logger
        self.validator = StockDataValidator()

    def fetch_stock_data(
        self,
        symbol: str,
        interval: str = "1d",
        period: Optional[str] = None,
    ) -> pd.DataFrame:
        """株価データを取得.

        Args:
            symbol: 銘柄コード
            interval: 時間軸（1d, 1h, 5m等）
            period: 取得期間（1y, 6mo等）

        Returns:
            株価データのDataFrame

        Raises:
            StockDataFetchError: データ取得エラーの場合
        """
        # 入力検証（バリデーターを使用）
        try:
            formatted_symbol = self.validator.validate_symbol_input(symbol)
        except Exception as e:
            raise StockDataFetchError(str(e)) from e

        # 時間軸の検証（バリデーターを使用）
        try:
            self.validator.validate_interval(interval)
        except Exception as e:
            raise StockDataFetchError(str(e)) from e

        self.logger.info(
            f"株価データ取得開始: {formatted_symbol} ({interval})"
        )

        try:
            # データ取得
            df = self._download_from_yahoo(formatted_symbol, interval, period)

            # データの検証（バリデーターを使用）
            self.validator.validate_dataframe_structure(df, formatted_symbol)

            self.logger.info(
                f"株価データ取得完了: {formatted_symbol} - {len(df)}件"
            )

            return df

        except StockDataFetchError:
            raise
        except Exception as e:
            error_msg = f"株価データ取得エラー: {formatted_symbol} - {str(e)}"
            self.logger.error(error_msg)
            raise StockDataFetchError(error_msg) from e

    def _download_from_yahoo(
        self,
        symbol: str,
        interval: str,
        period: Optional[str] = None,
    ) -> pd.DataFrame:
        """Yahoo Financeからデータをダウンロード.

        Args:
            symbol: 銘柄コード
            interval: 時間軸
            period: 取得期間

        Returns:
            ダウンロードしたDataFrame

        Raises:
            StockDataFetchError: ダウンロードエラーの場合
        """
        try:
            ticker = yf.Ticker(symbol)

            # 期間の設定
            if period:
                df = ticker.history(period=period, interval=interval)
            else:
                # デフォルト期間の設定
                default_periods = {
                    "1m": "7d",
                    "2m": "60d",
                    "5m": "60d",
                    "15m": "60d",
                    "30m": "60d",
                    "60m": "730d",
                    "90m": "60d",
                    "1h": "730d",
                    "1d": "max",
                    "5d": "max",
                    "1wk": "max",
                    "1mo": "max",
                    "3mo": "max",
                }
                period = default_periods.get(interval, "1y")
                df = ticker.history(period=period, interval=interval)

            return df

        except Exception as e:
            raise StockDataFetchError(
                f"Yahoo Financeからのデータダウンロードに失敗しました: {e}"
            ) from e
