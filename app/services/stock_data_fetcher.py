"""yfinanceを使用して各時間軸の株価データを取得します.

このモジュールは株価データの取得、検証、変換機能を提供します。
"""

from datetime import date, datetime
import logging
from typing import Any, Dict, Optional

import pandas as pd
import yfinance as yf

from utils.timeframe_utils import (
    get_display_name,
    get_recommended_period,
    is_intraday_interval,
    validate_interval,
)


logger = logging.getLogger(__name__)


class StockDataFetchError(Exception):
    """データ取得エラー."""

    pass


class StockDataFetcher:
    """株価データ取得クラス."""

    def __init__(self):
        """初期化."""
        self.logger = logger

    def _is_valid_stock_code(self, symbol: str) -> bool:
        """有効な銘柄コードかチェック.

        Args:
            symbol: 銘柄コード

        Returns:
            有効な場合True。
        """
        if not symbol or not isinstance(symbol, str):
            return False

        # .T サフィックスを除去
        code = symbol.replace(".T", "")

        # 数字のみ（4桁）が日本株の標準形式
        if code.isdigit() and len(code) == 4:
            return True

        # その他の有効なフォーマット（米国株など）
        # アルファベットのみ、または数字+アルファベットの組み合わせ
        if code.replace(".", "").replace("-", "").isalnum():
            # 無効なパターン（数字+A形式）を除外
            if code[-1] == "A" and code[:-1].isdigit():
                return False
            return True

        return False

    def _format_symbol_for_yahoo(self, symbol: str) -> str:
        """Yahoo Finance用に銘柄コードをフォーマット.

        Args:
            symbol: 元の銘柄コード（例: '1301', '7203.T'）

        Returns:
            Yahoo Finance用の銘柄コード（例: '1301.T', '7203.T'）。
        """
        # symbolがNoneまたは空文字列の場合はそのまま返す
        if not symbol:
            return symbol or ""

        # 既に.Tサフィックスが付いている場合はそのまま返す
        if symbol.endswith(".T"):
            return symbol

        # 数字のみの銘柄コード（日本株）の場合は.Tを追加
        if symbol.isdigit():
            return f"{symbol}.T"

        # その他の場合（海外株等）はそのまま返す
        return symbol

    def fetch_stock_data(
        self,
        symbol: str,
        interval: str = "1d",
        period: Optional[str] = None,
        start: Optional[str] = None,
        end: Optional[str] = None,
    ) -> pd.DataFrame:
        """株価データを取得.

        Args:
            symbol: 銘柄コード（例: '7203.T'）
            interval: 時間軸（'1m', '5m', '15m', '30m', '1h', '1d', '1wk', '1mo'）
            period: 取得期間（'1d', '5d', '1mo', '3mo', '6mo', '1y', '2y', '5y', '10y', 'ytd', 'max'）
            start: 開始日（YYYY-MM-DD形式、periodと排他）
            end: 終了日（YYYY-MM-DD形式、periodと排他）

        Returns:
            株価データのDataFrame

        Raises:
            StockDataFetchError: データ取得失敗時。
        """
        try:
            # symbolの検証
            if not symbol:
                raise StockDataFetchError(f"無効な銘柄コードです: {symbol}")

            # 時間軸の検証
            if not validate_interval(interval):
                raise ValueError(f"サポートされていない時間軸: {interval}")

            # 期間の設定
            if period is None and start is None and end is None:
                period = get_recommended_period(interval)
                self.logger.info(
                    f"期間未指定のため推奨期間を使用: {period} (時間軸: {get_display_name(interval)})"
                )

            # 日本株の場合、Yahoo Finance用に.Tサフィックスを追加
            yahoo_symbol = self._format_symbol_for_yahoo(symbol)

            # yfinanceでデータ取得
            self.logger.info(
                f"株価データ取得開始: {symbol} -> {yahoo_symbol} (時間軸: {get_display_name(interval)}, "
                f"期間: {period or f'{start}~{end}'})"
            )

            ticker = yf.Ticker(yahoo_symbol)

            # データ取得（タイムアウト設定を追加）
            if period:
                df = ticker.history(
                    period=period, interval=interval, timeout=30
                )
            else:
                df = ticker.history(
                    start=start, end=end, interval=interval, timeout=30
                )

            # データの検証
            if df.empty:
                raise StockDataFetchError(
                    f"データが取得できませんでした: {symbol} (Yahoo: {yahoo_symbol}) "
                    f"(時間軸: {get_display_name(interval)})"
                )

            self.logger.info(
                f"株価データ取得成功: {symbol} (Yahoo: {yahoo_symbol}) - {len(df)}件 "
                f"(時間軸: {get_display_name(interval)})"
            )

            return df

        except Exception as e:
            # yahoo_symbolが定義されていない場合の対応
            yahoo_symbol_str = (
                yahoo_symbol if "yahoo_symbol" in locals() else symbol
            )
            error_msg = (
                f"株価データ取得エラー: {symbol} (Yahoo: {yahoo_symbol_str}) "
                f"(時間軸: {get_display_name(interval)}): {str(e)}"
            )
            self.logger.error(error_msg)
            raise StockDataFetchError(error_msg) from e

    def fetch_multiple_timeframes(
        self, symbol: str, intervals: list[str], period: Optional[str] = None
    ) -> Dict[str, pd.DataFrame]:
        """複数時間軸のデータを一度に取得.

        Args:
            symbol: 銘柄コード
            intervals: 時間軸のリスト
            period: 取得期間（各時間軸で共通、Noneの場合は推奨期間を使用）

        Returns:
            {interval: DataFrame} の辞書

        Raises:
            StockDataFetchError: データ取得失敗時。
        """
        results = {}
        errors = []

        for interval in intervals:
            try:
                df = self.fetch_stock_data(
                    symbol=symbol, interval=interval, period=period
                )
                results[interval] = df
            except StockDataFetchError as e:
                errors.append(str(e))
                self.logger.warning(
                    f"時間軸 {interval} のデータ取得をスキップ: {e}"
                )

        if not results and errors:
            raise StockDataFetchError(
                f"全ての時間軸でデータ取得に失敗しました: {symbol}\n"
                + "\n".join(errors)
            )

        return results

    def fetch_batch_stock_data(
        self,
        symbols: list[str],
        interval: str = "1d",
        period: Optional[str] = None,
        start: Optional[str] = None,
        end: Optional[str] = None,
    ) -> Dict[str, pd.DataFrame]:
        """複数銘柄の株価データを一括取得（バッチダウンロード）.

        Args:
            symbols: 銘柄コードのリスト（例: ['7203.T', '6758.T', '9984.T']）
            interval: 時間軸（'1m', '5m', '15m', '30m', '1h', '1d', '1wk', '1mo'）
            period: 取得期間（'1d', '5d', '1mo', '3mo', '6mo', '1y', '2y', '5y', '10y', 'ytd', 'max'）
            start: 開始日（YYYY-MM-DD形式、periodと排他）
            end: 終了日（YYYY-MM-DD形式、periodと排他）

        Returns:
            {銘柄コード: DataFrame} の辞書

        Raises:
            StockDataFetchError: データ取得失敗時。
        """
        try:
            # 時間軸の検証
            if not validate_interval(interval):
                raise ValueError(f"サポートされていない時間軸: {interval}")

            # 無効な銘柄コードをフィルタリング
            valid_symbols = []
            invalid_symbols = []
            for symbol in symbols:
                if self._is_valid_stock_code(symbol):
                    valid_symbols.append(symbol)
                else:
                    invalid_symbols.append(symbol)

            if invalid_symbols:
                self.logger.warning(
                    f"無効な銘柄コードをスキップ: {len(invalid_symbols)}件 - {invalid_symbols[:10]}"
                    + ("..." if len(invalid_symbols) > 10 else "")
                )

            if not valid_symbols:
                self.logger.warning("有効な銘柄コードがありません")
                return {}

            # 期間の設定
            if period is None and start is None and end is None:
                period = get_recommended_period(interval)
                self.logger.info(
                    f"期間未指定のため推奨期間を使用: {period} (時間軸: {get_display_name(interval)})"
                )

            # 日本株の場合、Yahoo Finance用に.Tサフィックスを追加
            yahoo_symbols = [
                self._format_symbol_for_yahoo(s) for s in valid_symbols
            ]

            # yfinanceでバッチダウンロード
            self.logger.info(
                f"株価データバッチ取得開始: {len(valid_symbols)}銘柄 (時間軸: {get_display_name(interval)}, "
                f"期間: {period or f'{start}~{end}'})"
            )

            # yf.download()でバッチダウンロード
            if period:
                df_multi = yf.download(
                    tickers=yahoo_symbols,
                    period=period,
                    interval=interval,
                    group_by="ticker",
                    threads=True,
                    timeout=60,
                    progress=False,
                )
            else:
                df_multi = yf.download(
                    tickers=yahoo_symbols,
                    start=start,
                    end=end,
                    interval=interval,
                    group_by="ticker",
                    threads=True,
                    timeout=60,
                    progress=False,
                )

            # 結果を銘柄ごとに分割
            result = {}
            success_count = 0

            for original_symbol, yahoo_symbol in zip(
                valid_symbols, yahoo_symbols
            ):
                try:
                    # 複数銘柄の場合はdf_multi[yahoo_symbol]、単一銘柄の場合はdf_multi
                    if len(yahoo_symbols) > 1:
                        df = (
                            df_multi[yahoo_symbol]
                            if yahoo_symbol in df_multi.columns.levels[0]
                            else pd.DataFrame()
                        )
                    else:
                        df = df_multi

                    if not df.empty:
                        result[original_symbol] = df
                        success_count += 1
                    else:
                        self.logger.warning(
                            f"データが取得できませんでした: {original_symbol} (Yahoo: {yahoo_symbol})"
                        )
                except Exception as e:
                    self.logger.error(
                        f"銘柄データ抽出エラー: {original_symbol} (Yahoo: {yahoo_symbol}): {e}"
                    )

            self.logger.info(
                f"株価データバッチ取得完了: {success_count}/{len(valid_symbols)}銘柄成功 "
                f"(時間軸: {get_display_name(interval)})"
            )

            return result

        except Exception as e:
            error_msg = (
                f"株価データバッチ取得エラー: {len(symbols)}銘柄 "
                f"(時間軸: {get_display_name(interval)}): {str(e)}"
            )
            self.logger.error(error_msg)
            raise StockDataFetchError(error_msg) from e

    def convert_to_dict(
        self, df: pd.DataFrame, interval: str
    ) -> list[Dict[str, Any]]:
        """DataFrameを辞書リストに変換（データベース保存用）.

        Args:
            df: yfinanceから取得したDataFrame
            interval: 時間軸

        Returns:
            データベース保存用の辞書リスト。
        """
        records = []
        is_intraday = is_intraday_interval(interval)
        skipped_count = 0  # スキップされたレコード数をカウント

        for index, row in df.iterrows():
            # NaN値チェック - 主要フィールドがすべてNaNの場合はスキップ
            if (
                pd.isna(row["Open"])
                and pd.isna(row["High"])
                and pd.isna(row["Low"])
                and pd.isna(row["Close"])
            ):
                skipped_count += 1
                self.logger.debug(
                    f"データスキップ: すべての価格フィールドがNaN ({index})"
                )
                continue

            try:
                # 価格データの取得と検証
                open_price = (
                    float(row["Open"]) if pd.notna(row["Open"]) else None
                )
                high_price = (
                    float(row["High"]) if pd.notna(row["High"]) else None
                )
                low_price = float(row["Low"]) if pd.notna(row["Low"]) else None
                close_price = (
                    float(row["Close"]) if pd.notna(row["Close"]) else None
                )
                volume = int(row["Volume"]) if pd.notna(row["Volume"]) else 0

                # 無効な価格データをスキップ（NaNまたは0以下の値）
                if (
                    open_price is None
                    or open_price <= 0
                    or high_price is None
                    or high_price <= 0
                    or low_price is None
                    or low_price <= 0
                    or close_price is None
                    or close_price <= 0
                ):
                    skipped_count += 1
                    self.logger.debug(
                        f"データスキップ: 無効な価格データ ({index}) - "
                        f"Open:{open_price}, High:{high_price}, Low:{low_price}, Close:{close_price}"
                    )
                    continue

                # 価格ロジック制約の検証
                if not (
                    high_price >= low_price
                    and high_price >= open_price
                    and high_price >= close_price
                    and low_price <= open_price
                    and low_price <= close_price
                ):
                    skipped_count += 1
                    self.logger.debug(
                        f"データスキップ: 価格ロジック制約違反 ({index}) - "
                        f"Open:{open_price}, High:{high_price}, Low:{low_price}, Close:{close_price}"
                    )
                    continue

                record = {
                    "open": open_price,
                    "high": high_price,
                    "low": low_price,
                    "close": close_price,
                    "volume": volume,
                }

                # 日付・日時フィールドの設定
                if is_intraday:
                    # 分足・時間足: datetime使用
                    if isinstance(index, pd.Timestamp):
                        record["datetime"] = index.to_pydatetime()
                    else:
                        record["datetime"] = datetime.fromisoformat(str(index))
                else:
                    # 日足・週足・月足: date使用
                    if isinstance(index, pd.Timestamp):
                        record["date"] = index.date()
                    else:
                        record["date"] = date.fromisoformat(
                            str(index).split()[0]
                        )

                records.append(record)

            except (ValueError, TypeError) as e:
                skipped_count += 1
                self.logger.warning(f"データ変換エラー: {index}: {e}")
                continue

        # フィルタリング結果をログ出力
        if skipped_count > 0:
            self.logger.info(
                f"データ変換完了: 元データ {len(df)}件 → 有効データ {len(records)}件 "
                f"(無効データ {skipped_count}件をスキップ)"
            )

        return records

    def get_latest_data_date(
        self, symbol: str, interval: str = "1d"
    ) -> Optional[datetime]:
        """最新データの日時を取得（データベース更新判定用）.

        Args:
            symbol: 銘柄コード
            interval: 時間軸

        Returns:
            最新データの日時、データがない場合はNone。
        """
        try:
            df = self.fetch_stock_data(symbol, interval, period="1d")
            if not df.empty:
                return df.index[-1].to_pydatetime()
            return None
        except StockDataFetchError:
            return None
