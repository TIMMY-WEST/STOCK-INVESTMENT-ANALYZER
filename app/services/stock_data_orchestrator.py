"""株価データ取得・保存オーケストレーター.

データ取得から保存、整合性チェックまでを統合的に管理します。
"""

from datetime import datetime
import logging
from typing import Any, Dict, List, Optional

from services.stock_data_fetcher import StockDataFetcher, StockDataFetchError
from services.stock_data_saver import StockDataSaveError, StockDataSaver
from utils.timeframe_utils import (
    get_all_intervals,
    get_display_name,
    validate_interval,
)


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
        self.logger = logger

    def fetch_and_save(
        self,
        symbol: str,
        interval: str = "1d",
        period: Optional[str] = None,
        force_update: bool = False,
    ) -> Dict[str, Any]:
        """
        株価データの取得と保存を実行.

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
                f"データ取得・保存開始: {symbol} "
                f"(時間軸: {get_display_name(interval)})"
            )

            # データ取得
            df = self.fetcher.fetch_stock_data(
                symbol=symbol, interval=interval, period=period
            )

            # データ変換
            data_list = self.fetcher.convert_to_dict(df, interval)

            # データ保存
            save_result = self.saver.save_stock_data(
                symbol=symbol, interval=interval, data_list=data_list
            )

            # 整合性チェック
            integrity_check = self.check_data_integrity(
                symbol=symbol, interval=interval
            )

            result = {
                "success": True,
                "symbol": symbol,
                "interval": interval,
                "fetch_count": len(data_list),
                "save_result": save_result,
                "integrity_check": integrity_check,
                "timestamp": datetime.now().isoformat(),
            }

            self.logger.info(
                f"データ取得・保存完了: {symbol} "
                f"(時間軸: {get_display_name(interval)}) - "
                f"取得: {len(data_list)}件, 保存: {save_result['saved']}件"
            )

            return result

        except (StockDataFetchError, StockDataSaveError) as e:
            error_msg = f"データ取得・保存エラー: {symbol} ({interval}): {e}"
            self.logger.error(error_msg)
            return {
                "success": False,
                "symbol": symbol,
                "interval": interval,
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
            }

    def fetch_and_save_multiple_timeframes(
        self,
        symbol: str,
        intervals: Optional[List[str]] = None,
        period: Optional[str] = None,
    ) -> Dict[str, Dict[str, Any]]:
        """
        複数時間軸のデータを取得・保存.

        Args:
            symbol: 銘柄コード
            intervals: 時間軸のリスト（Noneの場合は全時間軸）
            period: 取得期間

        Returns:
            {interval: 実行結果} の辞書。
        """
        if intervals is None:
            intervals = get_all_intervals()

        results = {}

        self.logger.info(
            f"複数時間軸データ取得・保存開始: {symbol} "
            f"(時間軸: {len(intervals)}種類)"
        )

        for interval in intervals:
            results[interval] = self.fetch_and_save(
                symbol=symbol, interval=interval, period=period
            )

        success_count = sum(1 for r in results.values() if r.get("success"))
        self.logger.info(
            f"複数時間軸データ取得・保存完了: {symbol} - "
            f"成功: {success_count}/{len(intervals)}"
        )

        return results

    def check_data_integrity(
        self, symbol: str, interval: str
    ) -> Dict[str, Any]:
        """
        データ整合性をチェック.

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
                    f"整合性チェック OK: {symbol} ({interval}) - "
                    f"{record_count}件"
                )
            else:
                self.logger.warning(
                    f"整合性チェック NG: {symbol} ({interval}) - "
                    f"データがありません"
                )

            return result

        except Exception as e:
            self.logger.error(
                f"整合性チェックエラー: {symbol} ({interval}): {e}"
            )
            return {"valid": False, "error": str(e)}

    def get_status(
        self, symbol: str, intervals: Optional[List[str]] = None
    ) -> Dict[str, Dict[str, Any]]:
        """
        各時間軸のデータ状態を取得.

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
        self, symbol: str, intervals: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        全時間軸のデータを更新（差分更新）.

        Args:
            symbol: 銘柄コード
            intervals: 時間軸のリスト（Noneの場合は全時間軸）

        Returns:
            更新結果のサマリー。
        """
        if intervals is None:
            intervals = get_all_intervals()

        self.logger.info(f"全時間軸データ更新開始: {symbol}")

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
            f"全時間軸データ更新完了: {symbol} - "
            f"成功: {success_count}/{len(intervals)}, "
            f"保存: {total_saved}件"
        )

        return summary
