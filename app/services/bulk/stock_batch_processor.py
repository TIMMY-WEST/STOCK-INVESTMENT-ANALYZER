"""株価データ一括処理クラス.

このモジュールは複数銘柄の株価データ一括処理機能を提供します。
"""

import logging
from typing import Any, Dict, List, Optional

import pandas as pd
import yfinance as yf

from services.stock_data.converter import StockDataConverter
from services.stock_data.fetcher import StockDataFetcher
from services.stock_data.validator import StockDataValidator


logger = logging.getLogger(__name__)


class StockBatchProcessingError(Exception):
    """一括処理エラー."""

    pass


class StockBatchProcessor:
    """株価データ一括処理クラス."""

    def __init__(self):
        """初期化."""
        self.logger = logger
        self.validator = StockDataValidator()
        self.converter = StockDataConverter()

    def fetch_multiple_timeframes(
        self,
        symbol: str,
        intervals: List[str],
        period: Optional[str] = None,
    ) -> Dict[str, Dict[str, Any]]:
        """複数時間軸のデータを取得.

        Args:
            symbol: 銘柄コード
            intervals: 時間軸のリスト
            period: 取得期間

        Returns:
            {時間軸: 結果} の辞書
        """
        # 銘柄コードの検証
        try:
            formatted_symbol = self.validator.validate_symbol_input(symbol)
        except Exception as e:
            error_result = {
                "success": False,
                "error": str(e),
                "symbol": symbol,
            }
            return {interval: error_result for interval in intervals}

        results = {}
        errors = []

        self.logger.info(
            f"複数時間軸データ取得開始: {symbol} ({len(intervals)}種類)"
        )

        for interval in intervals:
            try:
                # 個別の時間軸でデータ取得（外部のfetch_stock_dataを使用）
                fetcher = StockDataFetcher()
                df = fetcher.fetch_stock_data(
                    symbol=formatted_symbol, interval=interval, period=period
                )

                # データ変換
                data_list = self.converter.convert_to_dict(df, interval)
                price_data = self.converter.extract_price_data(df)

                results[interval] = {
                    "success": True,
                    "data": data_list,
                    "price_data": price_data,
                    "record_count": len(data_list),
                }

                self.logger.debug(
                    f"時間軸データ取得成功: {symbol} ({interval}) - {len(data_list)}件"
                )

            except Exception as e:
                error_msg = f"{interval}: {str(e)}"
                errors.append(error_msg)
                results[interval] = {
                    "success": False,
                    "error": str(e),
                    "symbol": symbol,
                    "interval": interval,
                }

                self.logger.warning(
                    f"時間軸データ取得失敗: {symbol} ({interval}): {e}"
                )

        # 全て失敗した場合はエラー
        if not results or all(not r.get("success") for r in results.values()):
            raise StockBatchProcessingError(
                f"全ての時間軸でデータ取得に失敗しました: {symbol}\n"
                + "\n".join(errors)
            )

        success_count = sum(1 for r in results.values() if r.get("success"))
        self.logger.info(
            f"複数時間軸データ取得完了: {symbol} - 成功: {success_count}/{len(intervals)}"
        )

        return results

    def fetch_batch_stock_data(
        self,
        symbols: List[str],
        interval: str = "1d",
        period: Optional[str] = None,
    ) -> Dict[str, Dict[str, Any]]:
        """複数銘柄の株価データを一括取得.

        Args:
            symbols: 銘柄コードのリスト
            interval: 時間軸
            period: 取得期間

        Returns:
            {銘柄コード: 結果} の辞書
        """
        if not symbols:
            return {}

        # 銘柄コードの検証とフィルタリング
        valid_symbols, invalid_symbols = self._validate_symbols(symbols)

        # 結果辞書の初期化
        results = self._initialize_results(invalid_symbols)

        self.logger.info(
            f"一括データ取得開始: {len(valid_symbols)}銘柄 ({interval})"
        )

        # 有効な銘柄のデータを処理
        self._process_valid_symbols(valid_symbols, interval, period, results)

        # 結果をログ出力
        self._log_batch_results(results, len(symbols))

        return results

    def _validate_symbols(
        self, symbols: List[str]
    ) -> tuple[List[str], List[str]]:
        """銘柄コードの検証とフィルタリング."""
        valid_symbols, invalid_symbols = (
            self.validator.validate_and_filter_symbols(symbols)
        )

        if invalid_symbols:
            self.logger.warning(f"無効な銘柄コード: {invalid_symbols}")

        if not valid_symbols:
            raise StockBatchProcessingError("有効な銘柄コードがありません")

        return valid_symbols, invalid_symbols

    def _initialize_results(
        self, invalid_symbols: List[str]
    ) -> Dict[str, Dict[str, Any]]:
        """結果辞書を初期化し、無効な銘柄の結果を設定."""
        results = {}
        for symbol in invalid_symbols:
            results[symbol] = {
                "success": False,
                "error": f"無効な銘柄コード: {symbol}",
                "symbol": symbol,
            }
        return results

    def _process_valid_symbols(
        self,
        valid_symbols: List[str],
        interval: str,
        period: Optional[str],
        results: Dict[str, Dict[str, Any]],
    ) -> None:
        """有効な銘柄のデータを処理."""
        try:
            # 一括ダウンロード
            batch_df = self._download_batch_from_yahoo(
                valid_symbols, interval, period
            )

            # 銘柄ごとに分割
            symbol_dataframes = self.converter.split_multi_symbol_result(
                batch_df, valid_symbols
            )

            # 各銘柄のデータを処理
            self._process_individual_symbols(
                symbol_dataframes, valid_symbols, interval, results
            )

        except Exception as e:
            # 一括ダウンロード失敗時は全銘柄をエラーとする
            self._handle_batch_download_error(valid_symbols, e, results)

    def _process_individual_symbols(
        self,
        symbol_dataframes: Dict[str, pd.DataFrame],
        valid_symbols: List[str],
        interval: str,
        results: Dict[str, Dict[str, Any]],
    ) -> None:
        """個別銘柄のデータを処理."""
        for symbol in valid_symbols:
            try:
                df = symbol_dataframes.get(symbol, pd.DataFrame())

                if df.empty:
                    results[symbol] = {
                        "success": False,
                        "error": f"データが取得できませんでした: {symbol}",
                        "symbol": symbol,
                    }
                    continue

                # データ検証と変換
                self._validate_and_convert_data(df, symbol, interval, results)

            except Exception as e:
                results[symbol] = {
                    "success": False,
                    "error": str(e),
                    "symbol": symbol,
                }
                self.logger.warning(f"銘柄データ処理失敗: {symbol}: {e}")

    def _validate_and_convert_data(
        self,
        df: pd.DataFrame,
        symbol: str,
        interval: str,
        results: Dict[str, Dict[str, Any]],
    ) -> None:
        """データの検証と変換を実行."""
        # データ検証
        self.validator.validate_dataframe_structure(df, symbol)

        # データ変換
        data_list = self.converter.convert_to_dict(df, interval)
        price_data = self.converter.extract_price_data(df)

        results[symbol] = {
            "success": True,
            "data": data_list,
            "price_data": price_data,
            "record_count": len(data_list),
        }

        self.logger.debug(f"銘柄データ処理完了: {symbol} - {len(data_list)}件")

    def _handle_batch_download_error(
        self,
        valid_symbols: List[str],
        error: Exception,
        results: Dict[str, Dict[str, Any]],
    ) -> None:
        """一括ダウンロードエラーを処理."""
        error_msg = f"一括ダウンロードエラー: {str(error)}"
        for symbol in valid_symbols:
            results[symbol] = {
                "success": False,
                "error": error_msg,
                "symbol": symbol,
            }
        self.logger.error(f"一括データ取得失敗: {error}")

    def _log_batch_results(
        self, results: Dict[str, Dict[str, Any]], total_symbols: int
    ) -> None:
        """一括処理の結果をログ出力."""
        success_count = sum(1 for r in results.values() if r.get("success"))
        self.logger.info(
            f"一括データ取得完了: 成功: {success_count}/{total_symbols}"
        )

    def _download_batch_from_yahoo(
        self,
        symbols: List[str],
        interval: str,
        period: Optional[str] = None,
    ) -> pd.DataFrame:
        """Yahoo Financeから一括ダウンロード.

        Args:
            symbols: 銘柄コードのリスト
            interval: 時間軸
            period: 取得期間

        Returns:
            ダウンロードしたDataFrame

        Raises:
            StockBatchProcessingError: ダウンロードエラーの場合
        """
        try:
            # 複数銘柄を一括ダウンロード
            tickers = yf.Tickers(" ".join(symbols))

            # 期間の設定
            if period:
                df = tickers.history(period=period, interval=interval)
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
                df = tickers.history(period=period, interval=interval)

            return df

        except Exception as e:
            raise StockBatchProcessingError(
                f"Yahoo Financeからのデータダウンロードに失敗しました: {e}"
            ) from e
