"""株価データ変換クラス.

このモジュールは株価データの変換・フォーマット機能を提供します。
"""

from datetime import datetime
import logging
from typing import Any, Dict, List, cast

import pandas as pd

from app.types import Interval


logger = logging.getLogger(__name__)


class StockDataConversionError(Exception):
    """データ変換エラー."""

    pass


class StockDataConverter:
    """株価データ変換クラス."""

    def __init__(self):
        """初期化."""
        self.logger = logger

    def convert_to_dict(
        self, df: pd.DataFrame, interval: Interval
    ) -> List[Dict[str, Any]]:
        """DataFrameを辞書リストに変換（データベース保存用）.

        Args:
            df: yfinanceから取得したDataFrame
            interval: 時間軸

        Returns:
            データベース保存用の辞書リスト。

        Raises:
            StockDataConversionError: 変換エラーの場合
        """
        try:
            if df.empty:
                return []

            records = []
            skipped_count = 0

            for index, row in df.iterrows():
                # 価格データの妥当性をチェック
                if not self._is_valid_price_data(row):
                    skipped_count += 1
                    self.logger.debug(
                        f"データスキップ: 無効な価格データ "
                        f"(Open:{row['Open']}, High:{row['High']}, "
                        f"Low:{row['Low']}, Close:{row['Close']})"
                    )
                    continue

                index_ts = cast(pd.Timestamp, index)
                record = self._create_record_from_row(index_ts, row, interval)
                records.append(record)

            if skipped_count > 0:
                self.logger.info(f"無効なデータをスキップ: {skipped_count}件")

            self.logger.debug(f"データ変換完了: {len(records)}件 ({interval})")
            return records

        except Exception as e:
            raise StockDataConversionError(f"データ変換エラー: {e}") from e

    def _is_valid_price_data(self, row: pd.Series) -> bool:
        """価格データの妥当性をチェック.

        データベース制約に準拠した価格データかどうかを検証します:
        - high >= low AND high >= open AND high >= close AND low <= open AND low <= close

        Args:
            row: 価格データの行

        Returns:
            妥当な場合True
        """
        try:
            open_price = float(row["Open"])
            high_price = float(row["High"])
            low_price = float(row["Low"])
            close_price = float(row["Close"])

            # 基本的な妥当性チェック
            if any(
                price <= 0
                for price in [open_price, high_price, low_price, close_price]
            ):
                return False

            # データベース制約チェック
            if not (
                high_price >= low_price
                and high_price >= open_price
                and high_price >= close_price
                and low_price <= open_price
                and low_price <= close_price
            ):
                return False

            return True

        except (ValueError, TypeError, KeyError):
            return False

    def _create_record_from_row(
        self, index: pd.Timestamp, row: pd.Series, interval: Interval
    ) -> Dict[str, Any]:
        """陦後ョ繝ｼ繧ｿ縺九ｉ繝ｬ繧ｳ繝ｼ繝芽ｾ樊嶌繧剃ｽ懈・.

        Args:
            index: 譌･譎ゅう繝ｳ繝・ャ繧ｯ繧ｹ
            row: 陦後ョ繝ｼ繧ｿ
            interval: 譎る俣霆ｸ

        Returns:
            繝ｬ繧ｳ繝ｼ繝芽ｾ樊嶌
        """
        try:
            record: Dict[str, Any] = {
                "open": float(row["Open"]),
                "high": float(row["High"]),
                "low": float(row["Low"]),
                "close": float(row["Close"]),
                "volume": int(row["Volume"]) if pd.notna(row["Volume"]) else 0,
            }

            # 時系列インターバルに応じて日付/日時を設定
            if interval in ["1d", "1wk", "1mo"]:
                record["date"] = index.date()
            else:
                record["datetime"] = index.to_pydatetime()

            return record
        except (AttributeError, TypeError, ValueError) as e:
            raise StockDataConversionError(
                f"繝ｬ繧ｳ繝ｼ繝我ｽ懈・繧ｨ繝ｩ繝ｼ: 繧､繝ｳ繝・ャ繧ｯ繧ｹ={index}, 繧ｨ繝ｩ繝ｼ={str(e)}"
            )

    def extract_price_data(self, df: pd.DataFrame) -> Dict[str, Any]:
        """価格データを抽出.

        Args:
            df: yfinanceから取得したDataFrame

        Returns:
            価格データの辞書
        """
        if df.empty:
            return {}

        latest_row = df.iloc[-1]
        latest_date = df.index[-1]

        return {
            "symbol": getattr(df, "symbol", None),
            "latest_date": latest_date.to_pydatetime(),
            "latest_close": float(latest_row["Close"]),
            "latest_volume": (
                int(latest_row["Volume"])
                if pd.notna(latest_row["Volume"])
                else 0
            ),
            "record_count": len(df),
            "date_range": {
                "start": df.index[0].to_pydatetime(),
                "end": latest_date.to_pydatetime(),
            },
        }

    def get_latest_data_date(self, df: pd.DataFrame) -> datetime:
        """最新データの日時を取得.

        Args:
            df: yfinanceから取得したDataFrame

        Returns:
            最新データの日時

        Raises:
            StockDataConversionError: データが空の場合
        """
        if df.empty:
            raise StockDataConversionError("データが空です")

        return df.index[-1].to_pydatetime()

    def split_multi_symbol_result(
        self, df: pd.DataFrame, symbols: List[str]
    ) -> Dict[str, pd.DataFrame]:
        """複数銘柄のダウンロード結果を個別の銘柄データに分割."""
        result: Dict[str, pd.DataFrame] = {}

        # マルチインデックス列の場合は銘柄ごとに抽出
        if isinstance(df.columns, pd.MultiIndex):
            for symbol in symbols:
                try:
                    symbol_data = df.xs(symbol, level=1, axis=1)
                    if isinstance(symbol_data, pd.Series):
                        symbol_data = symbol_data.to_frame()
                    result[symbol] = symbol_data
                except KeyError:
                    result[symbol] = pd.DataFrame()
        else:
            if len(symbols) == 1:
                result[symbols[0]] = df
            else:
                result = {symbol: pd.DataFrame() for symbol in symbols}

        return result

    def format_summary_data(
        self, results: Dict[str, Any], symbol: str, interval: Interval
    ) -> Dict[str, Any]:
        """サマリーデータをフォーマット.

        Args:
            results: 処理結果
            symbol: 銘柄コード
            interval: 時間軸

        Returns:
            フォーマットされたサマリーデータ
        """
        return {
            "symbol": symbol,
            "interval": interval,
            "success": results.get("success", False),
            "record_count": results.get("record_count", 0),
            "latest_date": results.get("latest_date"),
            "error": results.get("error"),
            "timestamp": datetime.now().isoformat(),
        }
