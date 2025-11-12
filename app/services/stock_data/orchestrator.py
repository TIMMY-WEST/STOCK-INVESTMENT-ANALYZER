"""Orchestrates data fetching, saving, and integrity checks."""

from datetime import datetime
import logging
from typing import Any, Dict, List, Optional

from app.services.bulk.stock_batch_processor import StockBatchProcessor
from app.services.stock_data.converter import StockDataConverter
from app.services.stock_data.fetcher import (
    StockDataFetcher,
    StockDataFetchError,
)
from app.services.stock_data.saver import StockDataSaveError, StockDataSaver
from app.types import Interval
from app.utils.timeframe_utils import get_all_intervals, get_display_name


logger = logging.getLogger(__name__)


class StockDataOrchestrationError(Exception):
    """オーケストレーションエラー."""

    pass


class StockDataOrchestrator:
    """株価データ取得・保存オーケストレータークラス."""

    def __init__(self):
        """初期化."""
        self.fetcher = StockDataFetcher()
        self.saver = StockDataSaver()
        self.converter = StockDataConverter()
        self.batch_processor = StockBatchProcessor()
        self.logger = logger

    def _build_success_result(
        self,
        symbol: str,
        interval: Interval,
        data_list: List[Dict],
        save_result: Dict[str, Any],
        integrity_check: Dict[str, Any],
    ) -> Dict[str, Any]:
        """成功時の結果オブジェクトを構築.

        Args:
            symbol: 銘柄コード
            interval: 時間軸
            data_list: 取得したデータリスト
            save_result: 保存結果
            integrity_check: 整合性チェック結果

        Returns:
            成功結果の辞書。
        """
        return {
            "success": True,
            "symbol": symbol,
            "interval": interval,
            "fetch_count": len(data_list),
            "save_result": save_result,
            "integrity_check": integrity_check,
            "timestamp": datetime.now().isoformat(),
        }

    def _build_error_result(
        self, symbol: str, interval: Interval, error: Exception
    ) -> Dict[str, Any]:
        """エラー時の結果オブジェクトを構築.

        Args:
            symbol: 銘柄コード
            interval: 時間軸
            error: 発生したエラー

        Returns:
            エラー結果の辞書。
        """
        return {
            "success": False,
            "symbol": symbol,
            "interval": interval,
            "error": str(error),
            "timestamp": datetime.now().isoformat(),
        }

    def _process_single_timeframe(
        self, symbol: str, interval: Interval, df: Any
    ) -> Dict[str, Any]:
        """単一時間軸のデータを処理（変換・保存・チェック）.

        Args:
            symbol: 銘柄コード
            interval: 時間軸
            df: 取得したDataFrame

        Returns:
            処理結果。

        Raises:
            StockDataSaveError: 保存時のエラー
        """
        # データ変換
        data_list = self.converter.convert_to_dict(df, interval)

        # データ保存
        save_result = self.saver.save_stock_data(
            symbol=symbol, interval=interval, data_list=data_list
        )

        # 整合性チェック
        integrity_check = self.check_data_integrity(
            symbol=symbol, interval=interval
        )

        return self._build_success_result(
            symbol=symbol,
            interval=interval,
            data_list=data_list,
            save_result=save_result,
            integrity_check=integrity_check,
        )

    def fetch_and_save(
        self,
        symbol: str,
        interval: Interval = "1d",
        period: Optional[str] = None,
        force_update: bool = False,
    ) -> Dict[str, Any]:
        """株価データの取得と保存を実行.

        Args:
            symbol: 銘柄コード
            interval: 時間軸
            period: 取得期間
            force_update: True の場合、既存データを無視して全て取得

        Returns:
            実行結果の詳細情報。
        """
        try:
            self.logger.info(
                "データ取得・保存開始: %s (時間軸: %s)",
                symbol,
                get_display_name(interval),
            )

            # データ取得
            df = self.fetcher.fetch_stock_data(
                symbol=symbol, interval=interval, period=period
            )

            # データ処理（変換・保存・チェック）
            result = self._process_single_timeframe(symbol, interval, df)

            self.logger.info(
                "データ取得・保存完了: %s (時間軸: %s) - " "取得: %d件, 保存: %d件",
                symbol,
                get_display_name(interval),
                result["fetch_count"],
                result["save_result"]["saved"],
            )

            return result

        except (StockDataFetchError, StockDataSaveError) as e:
            self.logger.error("データ取得・保存エラー: %s (%s): %s", symbol, interval, e)
            return self._build_error_result(symbol, interval, e)

    def fetch_and_save_multiple_timeframes(
        self,
        symbol: str,
        intervals: Optional[List[Interval]] = None,
        period: Optional[str] = None,
    ) -> Dict[Interval, Dict[str, Any]]:
        """複数時間軸のデータを取得・保存.

        Args:
            symbol: 銘柄コード
            intervals: 時間軸のリスト（Noneの場合は全時間軸）
            period: 取得期間

        Returns:
            {interval: 実行結果} の辞書。
        """
        if intervals is None:
            intervals = get_all_intervals()

        self.logger.info(
            "複数時間軸データ取得・保存開始: %s (時間軸: %d種類)",
            symbol,
            len(intervals),
        )

        # バッチ取得を試行し、結果を処理
        results = self._fetch_and_process_batch(symbol, intervals, period)

        # サマリーログ出力
        success_count = sum(1 for r in results.values() if r.get("success"))
        self.logger.info(
            "複数時間軸データ取得・保存完了: %s - 成功: %d/%d",
            symbol,
            success_count,
            len(intervals),
        )

        return results

    def _fetch_and_process_batch(
        self, symbol: str, intervals: List[Interval], period: Optional[str]
    ) -> Dict[Interval, Dict[str, Any]]:
        """バッチ取得と各時間軸の処理を実行.

        Args:
            symbol: 銘柄コード
            intervals: 時間軸のリスト
            period: 取得期間

        Returns:
            {interval: 実行結果} の辞書。
        """
        try:
            # BatchProcessorを使用して複数時間軸のデータを取得
            batch_results = self.batch_processor.fetch_multiple_timeframes(
                symbol=symbol, intervals=intervals, period=period
            )
            # 各時間軸のデータを処理
            return self._process_batch_results(symbol, batch_results)

        except Exception as e:
            # バッチ取得全体でエラーが発生した場合
            self.logger.error("複数時間軸データ取得エラー: %s: %s", symbol, e)
            return {
                interval: self._build_error_result(symbol, interval, e)
                for interval in intervals
            }

    def _process_batch_results(
        self, symbol: str, batch_results: Dict[Interval, Any]
    ) -> Dict[Interval, Dict[str, Any]]:
        """バッチ取得結果の各時間軸データを処理.

        Args:
            symbol: 銘柄コード
            batch_results: {interval: DataFrame} の辞書

        Returns:
            {interval: 実行結果} の辞書。
        """
        results = {}
        for interval, df in batch_results.items():
            try:
                results[interval] = self._process_single_timeframe(
                    symbol, interval, df
                )
            except (StockDataSaveError, Exception) as e:
                self.logger.error("データ保存エラー: %s (%s): %s", symbol, interval, e)
                results[interval] = self._build_error_result(
                    symbol, interval, e
                )
        return results

    def check_data_integrity(
        self, symbol: str, interval: Interval
    ) -> Dict[str, Any]:
        """データ整合性をチェック.

        Args:
            symbol: 銘柄コード
            interval: 時間軸

        Returns:
            整合性チェック結果。
        """
        try:
            # データベース内のレコード数
            record_count = self.saver.count_records(symbol, interval)

            # 最新データ日時
            latest_date = self.saver.get_latest_date(symbol, interval)

            # 基本的な整合性チェック
            is_valid = record_count > 0

            result = {
                "valid": is_valid,
                "record_count": record_count,
                "latest_date": (
                    latest_date.isoformat() if latest_date else None
                ),
                "checks": {
                    "has_data": record_count > 0,
                },
            }

            if is_valid:
                self.logger.debug(
                    "整合性チェック OK: %s (%s) - %d件",
                    symbol,
                    interval,
                    record_count,
                )
            else:
                self.logger.warning(
                    "整合性チェック NG: %s (%s) - データがありません",
                    symbol,
                    interval,
                )

            return result

        except Exception as e:
            self.logger.error("整合性チェックエラー: %s (%s): %s", symbol, interval, e)
            return {"valid": False, "error": str(e)}

    def get_status(
        self, symbol: str, intervals: Optional[List[Interval]] = None
    ) -> Dict[Interval, Dict[str, Any]]:
        """各時間軸のデータ状態を取得.

        Args:
            symbol: 銘柄コード
            intervals: 時間軸のリスト（Noneの場合は全時間軸）

        Returns:
            {interval: ステータス情報} の辞書。
        """
        if intervals is None:
            intervals = get_all_intervals()

        status = {}

        for interval in intervals:
            try:
                record_count = self.saver.count_records(symbol, interval)
                latest_date = self.saver.get_latest_date(symbol, interval)

                status[interval] = {
                    "interval": interval,
                    "display_name": get_display_name(interval),
                    "record_count": record_count,
                    "latest_date": (
                        latest_date.isoformat() if latest_date else None
                    ),
                    "has_data": record_count > 0,
                }

            except Exception as e:
                status[interval] = {
                    "interval": interval,
                    "display_name": get_display_name(interval),
                    "error": str(e),
                }

        return status

    def update_all_timeframes(
        self, symbol: str, intervals: Optional[List[Interval]] = None
    ) -> Dict[str, Any]:
        """全時間軸のデータを更新（差分更新）.

        Args:
            symbol: 銘柄コード
            intervals: 時間軸のリスト（Noneの場合は全時間軸）

        Returns:
            更新結果のサマリー。
        """
        if intervals is None:
            intervals = get_all_intervals()

        self.logger.info("全時間軸データ更新開始: %s", symbol)

        results = self.fetch_and_save_multiple_timeframes(
            symbol=symbol, intervals=intervals, period=None  # 推奨期間を使用
        )

        # サマリー作成
        success_count = sum(1 for r in results.values() if r.get("success"))
        total_saved = sum(
            r.get("save_result", {}).get("saved", 0)
            for r in results.values()
            if r.get("success")
        )

        summary = {
            "symbol": symbol,
            "total_intervals": len(intervals),
            "success_count": success_count,
            "failed_count": len(intervals) - success_count,
            "total_saved_records": total_saved,
            "results": results,
            "timestamp": datetime.now().isoformat(),
        }

        self.logger.info(
            "全時間軸データ更新完了: %s - 成功: %d/%d, 保存: %d件",
            symbol,
            success_count,
            len(intervals),
            total_saved,
        )

        return summary
