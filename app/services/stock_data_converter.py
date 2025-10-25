"""株価データ変換クラス.

このモジュールは株価データの変換・フォーマット機能を提供します。
"""

from datetime import datetime
import logging
from typing import Any, Dict, List

import pandas as pd


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
        self, df: pd.DataFrame, interval: str
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
            for index, row in df.iterrows():
                record = self._create_record_from_row(index, row, interval)
                records.append(record)

            self.logger.debug(f"データ変換完了: {len(records)}件 ({interval})")
            return records

        except Exception as e:
            raise StockDataConversionError(f"データ変換エラー: {e}") from e

    def _create_record_from_row(
        self, index: pd.Timestamp, row: pd.Series, interval: str
    ) -> Dict[str, Any]:
        """行データからレコード辞書を作成.

        Args:
            index: 日時インデックス
            row: 価格データの行
            interval: 時間軸

        Returns:
            レコード辞書
        """
        record = {
            "open": float(row["Open"]),
            "high": float(row["High"]),
            "low": float(row["Low"]),
            "close": float(row["Close"]),
            "volume": int(row["Volume"]) if pd.notna(row["Volume"]) else 0,
        }

        # 時間軸に応じて日時フィールドを設定
        if interval in ["1d", "1wk", "1mo"]:
            # 日足以上は日付のみ
            record["date"] = index.date()
        else:
            # 分足・時間足は日時
            record["datetime"] = index.to_pydatetime()

        return record

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
        """複数銘柄のダウンロード結果を個別の銘柄データに分割.

        Args:
            df: 複数銘柄のDataFrame
            symbols: 銘柄コードのリスト

        Returns:
            {銘柄コード: DataFrame} の辞書
        """
        result = {}

        if df.empty:
            return {symbol: pd.DataFrame() for symbol in symbols}

        # マルチレベルカラムの場合
        if isinstance(df.columns, pd.MultiIndex):
            for symbol in symbols:
                try:
                    # 銘柄ごとのデータを抽出
                    symbol_data = df.xs(symbol, level=1, axis=1)
                    result[symbol] = symbol_data
                except KeyError:
                    # 該当銘柄のデータがない場合は空のDataFrame
                    result[symbol] = pd.DataFrame()
        else:
            # 単一銘柄の場合
            if len(symbols) == 1:
                result[symbols[0]] = df
            else:
                # 複数銘柄だがマルチレベルでない場合は空を返す
                result = {symbol: pd.DataFrame() for symbol in symbols}

        return result

    def format_summary_data(
        self, results: Dict[str, Any], symbol: str, interval: str
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
