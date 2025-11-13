"""全銘柄一括取得サービス.

全銘柄の株価データを並列処理で効率的に一括取得します。
"""

from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
import logging
import time
from typing import Any, Callable, Dict, List, Optional

from app.services.bulk.stock_batch_processor import StockBatchProcessor
from app.services.common.error_handler import ErrorAction, ErrorHandler
from app.services.stock_data.converter import StockDataConverter
from app.services.stock_data.fetcher import StockDataFetcher
from app.services.stock_data.saver import StockDataSaver
from app.utils.structured_logger import (
    get_batch_logger,
    setup_structured_logging,
)
from app.utils.timeframe_utils import normalize_interval


logger = logging.getLogger(__name__)

# 構造化ログ設定（アプリケーション起動時に一度だけ実行）
try:
    setup_structured_logging(
        log_dir="logs",
        log_level=logging.INFO,
        enable_console=True,
        enable_file=True,
    )
except Exception as e:
    logger.warning(f"構造化ログ設定に失敗しました: {e}")


class BulkDataServiceError(Exception):
    """一括データ取得エラー."""

    pass


class ProgressTracker:
    """進捗トラッカー.

    Phase 2要件: メトリクス収集機能（スループット、成功率、平均処理時間等）
    仕様書: docs/api_bulk_fetch.md (790-796行目)。
    """

    def __init__(self, total: int):
        """初期化.

        Args:
            total: 処理対象の総数。
        """
        self.total = total
        self.processed = 0
        self.successful = 0
        self.failed = 0
        self.start_time = datetime.now()
        self.current_symbol: Optional[str] = None
        self.error_details: List[Dict[str, Any]] = []
        # メトリクス収集用
        self.processing_times: List[float] = []  # 各銘柄の処理時間（ミリ秒）
        self.records_fetched_list: List[int] = []  # 各銘柄の取得レコード数
        self.records_saved_list: List[int] = []  # 各銘柄の保存レコード数

    def update(
        self,
        symbol: str,
        success: bool,
        error_message: Optional[str] = None,
        duration_ms: Optional[int] = None,
        records_fetched: int = 0,
        records_saved: int = 0,
    ):
        """進捗を更新.

        Args:
            symbol: 処理した銘柄コード
            success: 成功したかどうか
            error_message: エラーメッセージ（失敗時）
            duration_ms: 処理時間（ミリ秒）
            records_fetched: 取得したレコード数
            records_saved: 保存したレコード数。
        """
        self.processed += 1
        self.current_symbol = symbol

        if success:
            self.successful += 1
            # メトリクス記録
            if duration_ms is not None:
                self.processing_times.append(duration_ms)
            self.records_fetched_list.append(records_fetched)
            self.records_saved_list.append(records_saved)
        else:
            self.failed += 1
            if error_message:
                self.error_details.append(
                    {
                        "symbol": symbol,
                        "error": error_message,
                        "timestamp": datetime.now().isoformat(),
                    }
                )

    def get_progress(self) -> Dict[str, Any]:
        """現在の進捗情報を取得.

        Returns:
            進捗情報の辞書（メトリクス含む）。
        """
        elapsed_time = (datetime.now() - self.start_time).total_seconds()
        progress_percentage = (
            (self.processed / self.total * 100) if self.total > 0 else 0
        )

        # 処理速度の計算
        stocks_per_second = (
            self.processed / elapsed_time if elapsed_time > 0 else 0
        )
        stocks_per_minute = stocks_per_second * 60

        # 完了予測時刻の計算（ETA）
        remaining = self.total - self.processed
        eta_seconds = (
            remaining / stocks_per_second if stocks_per_second > 0 else 0
        )
        eta = datetime.now().timestamp() + eta_seconds

        # メトリクス計算
        avg_processing_time = (
            sum(self.processing_times) / len(self.processing_times)
            if self.processing_times
            else 0
        )
        total_records_fetched = sum(self.records_fetched_list)
        total_records_saved = sum(self.records_saved_list)
        records_per_minute = (
            (total_records_saved / elapsed_time * 60)
            if elapsed_time > 0
            else 0
        )

        # 成功率の計算
        success_rate = (
            (self.successful / self.processed * 100)
            if self.processed > 0
            else 0
        )

        return {
            "total": self.total,
            "processed": self.processed,
            "successful": self.successful,
            "failed": self.failed,
            "progress_percentage": round(progress_percentage, 2),
            "current_symbol": self.current_symbol,
            "elapsed_time": round(elapsed_time, 2),
            "stocks_per_second": round(stocks_per_second, 2),
            "estimated_completion": (
                datetime.fromtimestamp(eta).isoformat()
                if eta_seconds > 0
                else None
            ),
            "error_count": len(self.error_details),
            # Phase 2メトリクス
            "throughput": {
                "stocks_per_minute": round(stocks_per_minute, 2),
                "records_per_minute": round(records_per_minute, 2),
            },
            "performance": {
                "success_rate": round(success_rate, 2),
                "avg_processing_time_ms": round(avg_processing_time, 2),
                "total_records_fetched": total_records_fetched,
                "total_records_saved": total_records_saved,
            },
        }

    def get_summary(self) -> Dict[str, Any]:
        """処理完了後のサマリーを取得.

        Returns:
            サマリー情報の辞書。
        """
        progress = self.get_progress()
        return {
            **progress,
            "status": "completed",
            "end_time": datetime.now().isoformat(),
            "error_details": self.error_details[:100],  # 最大100件のエラー詳細
        }


class BulkDataService:
    """全銘柄一括取得サービスクラス."""

    def __init__(
        self,
        max_workers: int = 3,
        retry_count: int = 5,
        batch_id: Optional[str] = None,
    ):
        """初期化.

        Args:
            max_workers: 最大並列ワーカー数（レート制限対策で3に削減）
            retry_count: リトライ回数（デフォルト5回に増加）
            batch_id: バッチID（構造化ログ用）。
        """
        self.fetcher = StockDataFetcher()
        self.batch_processor = StockBatchProcessor()
        self.saver = StockDataSaver()
        self.converter = StockDataConverter()
        self.max_workers = max_workers
        self.retry_count = retry_count
        self.logger = logger
        # 構造化ログ用ロガー
        self.batch_logger = get_batch_logger(batch_id=batch_id)
        # ErrorHandlerを初期化（リトライ設定を強化）
        self.error_handler = ErrorHandler(
            max_retries=retry_count,
            retry_delay=5,  # 初期遅延を5秒に増加（レート制限対策）
            backoff_multiplier=3,  # バックオフ倍率を3に増加
        )

    def _fetch_and_convert_data(
        self, symbol: str, interval: str, period: Optional[str]
    ) -> tuple[bool, list, int]:
        """データの取得と変換.

        Args:
            symbol: 銘柄コード
            interval: 時間軸
            period: 取得期間

        Returns:
            (成功フラグ, 変換済みデータリスト, 処理時間(ms))
        """
        fetch_start = time.time()
        df = self.fetcher.fetch_stock_data(
            symbol=symbol, interval=interval, period=period
        )
        fetch_duration = int((time.time() - fetch_start) * 1000)

        # 構造化ログ: データ取得成功
        self.batch_logger.log_batch_action(
            action="data_fetch",
            stock_code=symbol,
            status="success",
            duration_ms=fetch_duration,
            records_count=len(df),
        )

        # データ変換
        try:
            data_list = self.converter.convert_to_dict(df, interval)
            if not data_list:
                self.logger.warning(f"変換後のデータが空です: {symbol}")
                return False, [], fetch_duration

            return True, data_list, fetch_duration

        except Exception as e:
            self.logger.error(f"データ変換エラー: {symbol}: {e}")
            return False, [], fetch_duration

    def _handle_retry_action(
        self,
        action: "ErrorAction",
        symbol: str,
        error: Exception,
        retry_count: int,
    ) -> bool:
        """リトライアクションの処理.

        Args:
            action: エラーアクション
            symbol: 銘柄コード
            error: エラー
            retry_count: 現在のリトライ回数

        Returns:
            継続フラグ（Trueなら継続、Falseなら終了）
        """
        if action == ErrorAction.RETRY:
            if retry_count < self.retry_count - 1:
                self.logger.info(
                    f"リトライ {retry_count + 1}/{self.retry_count}: {symbol}"
                )
                return True
            else:
                self.logger.error(f"最大リトライ回数に達しました: {symbol}")
                return False
        elif action == ErrorAction.SKIP:
            return False
        elif action == ErrorAction.ABORT:
            raise BulkDataServiceError(
                f"システムエラー: {symbol}: {error}"
            ) from error

    def fetch_single_stock(
        self, symbol: str, interval: str = "1d", period: Optional[str] = None
    ) -> Dict[str, Any]:
        """単一銘柄のデータを取得・保存（ErrorHandlerによるリトライ機能付き).

        Args:
            symbol: 銘柄コード
            interval: 時間軸
            period: 取得期間

        Returns:
            処理結果。
        """
        last_error = None
        start_time = time.time()
        retry_count_for_handler = 0

        for _ in range(self.retry_count):
            try:
                # データ取得と変換
                (
                    success,
                    data_list,
                    fetch_duration,
                ) = self._fetch_and_convert_data(symbol, interval, period)

                if not success:
                    continue

                # データ保存 (内部では Interval 型を要求するため正規化する)
                interval_norm = normalize_interval(interval)
                save_result = self.saver.save_stock_data(
                    symbol, interval_norm, data_list
                )

                # 成功ログ
                self.logger.info(
                    f"データ保存完了: {symbol} ({interval}) - "
                    f"有効データ: {len(data_list)}件, 保存: {save_result.get('saved', 0)}件"
                )

                # 成功時の結果を返す
                total_duration = int((time.time() - start_time) * 1000)
                return {
                    "success": True,
                    "symbol": symbol,
                    "interval": interval,
                    "records_fetched": len(data_list),
                    "records_saved": save_result.get("saved", 0),
                    "duration_ms": total_duration,
                    "attempt": retry_count_for_handler + 1,
                }

            except Exception as e:
                last_error = e
                self.logger.error(f"データ処理エラー: {symbol}: {e}")

                # エラーハンドラーでアクションを決定
                action = self.error_handler.handle_error(
                    e, symbol, {"retry_count": retry_count_for_handler}
                )

                # リトライカウントをインクリメント（ブレイク前に実行）
                retry_count_for_handler += 1

                # アクション処理
                should_continue = self._handle_retry_action(
                    action, symbol, e, retry_count_for_handler - 1
                )
                if not should_continue:
                    break

        # 構造化ログ: エラー発生
        total_duration = int((time.time() - start_time) * 1000)
        self.batch_logger.log_batch_action(
            action="error_occurred",
            stock_code=symbol,
            status="failed",
            error_message=str(last_error),
            retry_count=retry_count_for_handler - 1,
            duration_ms=total_duration,
        )

        return {
            "success": False,
            "symbol": symbol,
            "interval": interval,
            "error": str(last_error),
            "attempts": retry_count_for_handler,
            "retry_count": retry_count_for_handler - 1,
            "duration_ms": total_duration,
        }

    def fetch_multiple_stocks(
        self,
        symbols: List[str],
        interval: str = "1d",
        period: Optional[str] = None,
        progress_callback: Optional[Callable[[Dict[str, Any]], None]] = None,
        use_batch: bool = True,
        batch_size: int = 100,
    ) -> Dict[str, Any]:
        """複数銘柄のデータを取得・保存（バッチ処理対応）.

        Args:
            symbols: 銘柄コードのリスト
            interval: 時間軸
            period: 取得期間
            progress_callback: 進捗通知用コールバック関数
            use_batch: バッチ処理を使用するか（デフォルト: True）
            batch_size: バッチサイズ（デフォルト: 100銘柄）

        Returns:
            処理結果のサマリー。
        """
        if use_batch:
            return self._fetch_multiple_stocks_batch(
                symbols, interval, period, progress_callback, batch_size
            )
        else:
            return self._fetch_multiple_stocks_parallel(
                symbols, interval, period, progress_callback
            )

    def _process_batch_data_conversion(
        self, batch_data: dict, interval: str
    ) -> tuple[dict, list]:
        """バッチデータの変換処理.

        Args:
            batch_data: バッチデータ（StockBatchProcessorから返された結果）
            interval: 時間軸

        Returns:
            (変換済みデータ辞書, エラーリスト)
        """
        symbols_data = {}
        conversion_errors = []

        for symbol, result in batch_data.items():
            try:
                # StockBatchProcessorから返された結果の構造を確認
                if isinstance(result, dict):
                    if result.get("success", False):
                        # 成功した場合、既に変換済みのデータを取得
                        data_list = result.get("data", [])
                        if data_list:
                            symbols_data[symbol] = data_list
                        else:
                            self.logger.warning(f"データ変換後が空: {symbol}")
                    else:
                        # 失敗した場合、エラーメッセージを記録
                        error_msg = result.get("error", "不明なエラー")
                        conversion_errors.append(f"{symbol}: {error_msg}")
                        self.logger.error(f"データ変換エラー: {symbol}: {error_msg}")
                else:
                    # 予期しない形式の場合
                    conversion_errors.append(f"{symbol}: 予期しないデータ形式")
                    self.logger.error(f"データ変換エラー: {symbol}: 予期しないデータ形式")
            except Exception as e:
                conversion_errors.append(f"{symbol}: {e}")
                self.logger.error(f"データ変換エラー: {symbol}: {e}")

        if conversion_errors:
            self.logger.warning(
                f"データ変換エラー: {len(conversion_errors)}件 - "
                f"{', '.join(conversion_errors[:5])}"
                + ("..." if len(conversion_errors) > 5 else "")
            )

        return symbols_data, conversion_errors

    def _save_batch_if_data_exists(
        self, symbols_data: dict, interval: str, batch_index: int
    ) -> tuple[dict, int]:
        """データが存在する場合の保存処理.

        Args:
            symbols_data: 変換済みデータ
            interval: 時間軸
            batch_index: バッチインデックス

        Returns:
            (保存結果辞書, 処理時間(ms))
        """
        if not symbols_data:
            self.logger.warning(f"保存可能なデータなし: バッチ {batch_index}")
            return {
                "total_symbols": 0,
                "total_saved": 0,
                "results_by_symbol": {},
            }, 0

        save_start = time.time()
        interval_norm = normalize_interval(interval)
        save_result = self.saver.save_batch_stock_data(
            symbols_data=symbols_data, interval=interval_norm
        )
        save_duration = int((time.time() - save_start) * 1000)
        self.logger.debug(
            f"バッチ保存完了: {len(symbols_data)}銘柄 - {save_duration}ms"
        )
        return save_result, save_duration

    def _record_batch_result(
        self,
        symbol: str,
        interval: str,
        symbols_data: dict,
        save_result: dict,
        batch_duration: int,
        batch_size: int,
        tracker,
        all_results: list,
    ) -> None:
        """バッチ処理結果の記録.

        Args:
            symbol: 銘柄コード
            interval: 時間軸
            symbols_data: 変換済みデータ
            save_result: 保存結果
            batch_duration: バッチ処理時間(ms)
            batch_size: バッチサイズ
            tracker: 進捗トラッカー
            all_results: 全結果リスト
        """
        if symbol in symbols_data and len(symbols_data[symbol]) > 0:
            data_list = symbols_data[symbol]
            symbol_save_result = save_result.get("results_by_symbol", {}).get(
                symbol, {}
            )

            self.logger.info(
                f"バッチ保存完了: {symbol} ({interval}) - "
                f"有効データ: {len(data_list)}件, 保存: {symbol_save_result.get('saved', 0)}件"
            )

            result = {
                "success": True,
                "symbol": symbol,
                "interval": interval,
                "records_fetched": len(data_list),
                "records_saved": symbol_save_result.get("saved", 0),
                "duration_ms": batch_duration // batch_size,
            }
            all_results.append(result)

            tracker.update(
                symbol=symbol,
                success=True,
                duration_ms=batch_duration // batch_size,
                records_fetched=len(data_list),
                records_saved=symbol_save_result.get("saved", 0),
            )
        else:
            # データ取得失敗
            result = {
                "success": False,
                "symbol": symbol,
                "interval": interval,
                "error": "データ取得失敗",
            }
            all_results.append(result)
            tracker.update(
                symbol=symbol,
                success=False,
                error_message="データ取得失敗",
            )

    def _fetch_multiple_stocks_batch(
        self,
        symbols: List[str],
        interval: str = "1d",
        period: Optional[str] = None,
        progress_callback: Optional[Callable[[Dict[str, Any]], None]] = None,
        batch_size: int = 100,
    ) -> Dict[str, Any]:
        """複数銘柄のデータをバッチ処理で取得・保存.

        Args:
            symbols: 銘柄コードのリスト
            interval: 時間軸
            period: 取得期間
            progress_callback: 進捗通知用コールバック関数
            batch_size: バッチサイズ

        Returns:
            処理結果のサマリー。
        """
        self.logger.info(
            f"全銘柄バッチ取得開始: {len(symbols)}銘柄 "
            f"(時間軸: {interval}, バッチサイズ: {batch_size})"
        )

        tracker = ProgressTracker(total=len(symbols))
        all_results: List[Dict[str, Any]] = []

        # 銘柄をバッチサイズごとに分割
        for i in range(0, len(symbols), batch_size):
            batch_symbols = symbols[i : i + batch_size]
            batch_start_time = time.time()
            batch_index = i // batch_size + 1

            self.logger.info(
                f"バッチ {batch_index}/{(len(symbols) + batch_size - 1) // batch_size} 処理開始: "
                f"{len(batch_symbols)}銘柄"
            )

            try:
                # バッチダウンロード
                fetch_start = time.time()
                batch_data = self.batch_processor.fetch_batch_stock_data(
                    symbols=batch_symbols, interval=interval, period=period
                )
                fetch_duration = int((time.time() - fetch_start) * 1000)
                self.logger.debug(
                    f"バッチフェッチ完了: {len(batch_symbols)}銘柄 - {fetch_duration}ms"
                )

                # データ変換
                symbols_data, _ = self._process_batch_data_conversion(
                    batch_data, interval
                )

                # バッチ保存
                save_result, _ = self._save_batch_if_data_exists(
                    symbols_data, interval, batch_index
                )

                batch_duration = int((time.time() - batch_start_time) * 1000)

                # 結果を記録
                for symbol in batch_symbols:
                    self._record_batch_result(
                        symbol,
                        interval,
                        symbols_data,
                        save_result,
                        batch_duration,
                        len(batch_symbols),
                        tracker,
                        all_results,
                    )

                # 進捗コールバック実行
                if progress_callback:
                    try:
                        progress_callback(tracker.get_progress())
                    except Exception as e:
                        self.logger.error(f"進捗コールバックエラー: {e}")

                # 進捗ログ出力
                progress = tracker.get_progress()
                self.logger.info(
                    f"バッチ処理完了: {progress['processed']}/{progress['total']} "
                    f"({progress['progress_percentage']}%) - "
                    f"成功: {progress['successful']}, 失敗: {progress['failed']}"
                )

            except Exception as e:
                self.logger.error(f"バッチ処理エラー: {e}")
                # バッチ全体が失敗した場合
                for symbol in batch_symbols:
                    result = {
                        "success": False,
                        "symbol": symbol,
                        "interval": interval,
                        "error": str(e),
                    }
                    all_results.append(result)
                    tracker.update(
                        symbol=symbol, success=False, error_message=str(e)
                    )

        # サマリー作成
        summary = tracker.get_summary()
        summary["results"] = all_results

        # 詳細統計情報を集計
        total_downloaded = sum(
            int(r.get("records_fetched", 0))
            for r in all_results
            if r.get("success")
        )
        total_saved = sum(
            int(r.get("records_saved", 0))
            for r in all_results
            if r.get("success")
        )
        total_skipped = total_downloaded - total_saved

        summary["total_downloaded"] = total_downloaded
        summary["total_saved"] = total_saved
        summary["total_skipped"] = total_skipped
        summary["errors"] = tracker.error_details[:100]

        self.logger.info(
            f"全銘柄バッチ取得完了: "
            f"成功 {summary['successful']}/{summary['total']}, "
            f"失敗 {summary['failed']}, "
            f"ダウンロード {total_downloaded}件, "
            f"DB格納 {total_saved}件, "
            f"処理時間 {summary['elapsed_time']}秒"
        )

        return summary

    def _fetch_multiple_stocks_parallel(
        self,
        symbols: List[str],
        interval: str = "1d",
        period: Optional[str] = None,
        progress_callback: Optional[Callable[[Dict[str, Any]], None]] = None,
    ) -> Dict[str, Any]:
        """複数銘柄のデータを並列取得・保存（旧実装）.

        Args:
            symbols: 銘柄コードのリスト
            interval: 時間軸
            period: 取得期間
            progress_callback: 進捗通知用コールバック関数

        Returns:
            処理結果のサマリー。
        """
        self.logger.info(
            f"全銘柄一括取得開始: {len(symbols)}銘柄 "
            f"(時間軸: {interval}, 並列数: {self.max_workers})"
        )

        # 進捗トラッカー初期化
        tracker = ProgressTracker(total=len(symbols))
        results = []

        # ThreadPoolExecutorで並列処理
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # 全銘柄のタスクを送信
            future_to_symbol = {
                executor.submit(
                    self.fetch_single_stock, symbol, interval, period
                ): symbol
                for symbol in symbols
            }

            # 完了したタスクから順次処理
            for future in as_completed(future_to_symbol):
                symbol = future_to_symbol[future]

                try:
                    result = future.result()
                    results.append(result)

                    # 進捗更新（メトリクス含む）
                    tracker.update(
                        symbol=symbol,
                        success=result.get("success", False),
                        error_message=result.get("error"),
                        duration_ms=result.get("duration_ms"),
                        records_fetched=result.get("records_fetched", 0),
                        records_saved=result.get("records_saved", 0),
                    )

                    # 進捗コールバック実行
                    if progress_callback:
                        try:
                            progress_callback(tracker.get_progress())
                        except Exception as e:
                            self.logger.error(f"進捗コールバックエラー: {e}")

                    # 進捗ログ出力（10件ごと）
                    if (
                        tracker.processed % 10 == 0
                        or tracker.processed == tracker.total
                    ):
                        progress = tracker.get_progress()
                        self.logger.info(
                            f"進捗: {progress['processed']}/{progress['total']} "
                            f"({progress['progress_percentage']}%) - "
                            f"成功: {progress['successful']}, "
                            f"失敗: {progress['failed']}, "
                            f"速度: {progress['stocks_per_second']}銘柄/秒"
                        )

                    # レート制限対策：リクエスト間隔制御
                    if tracker.processed < tracker.total:
                        time.sleep(1.0)  # 1秒間隔でリクエスト制御

                except Exception as e:
                    self.logger.error(f"タスク実行エラー ({symbol}): {e}")
                    tracker.update(
                        symbol=symbol, success=False, error_message=str(e)
                    )
                    results.append(
                        {"success": False, "symbol": symbol, "error": str(e)}
                    )

        # サマリー作成
        summary = tracker.get_summary()
        summary["results"] = results

        # 詳細統計情報を集計
        total_downloaded = sum(
            r.get("records_fetched", 0) for r in results if r.get("success")
        )
        total_saved = sum(
            r.get("records_saved", 0) for r in results if r.get("success")
        )
        total_skipped = total_downloaded - total_saved

        summary["total_downloaded"] = total_downloaded
        summary["total_saved"] = total_saved
        summary["total_skipped"] = total_skipped
        summary["errors"] = tracker.error_details[:100]  # エラー詳細（最大100件）

        # エラーハンドラーからエラーレポートを生成
        error_report = self.error_handler.generate_error_report()
        summary["error_report"] = error_report

        self.logger.info(
            f"全銘柄一括取得完了: "
            f"成功 {summary['successful']}/{summary['total']}, "
            f"失敗 {summary['failed']}, "
            f"ダウンロード {total_downloaded}件, "
            f"DB格納 {total_saved}件, "
            f"スキップ {total_skipped}件, "
            f"処理時間 {summary['elapsed_time']}秒, "
            f"エラー統計: {error_report['summary']['error_by_type']}"
        )

        return summary

    def fetch_all_stocks_from_list_file(
        self,
        file_path: str,
        interval: str = "1d",
        period: Optional[str] = None,
        progress_callback: Optional[Callable[[Dict[str, Any]], None]] = None,
    ) -> Dict[str, Any]:
        """ファイルから銘柄リストを読み込んで一括取得.

        Args:
            file_path: 銘柄コードリストファイルのパス（1行1銘柄）
            interval: 時間軸
            period: 取得期間
            progress_callback: 進捗通知用コールバック関数

        Returns:
            処理結果のサマリー。
        """
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                symbols = [line.strip() for line in f if line.strip()]

            self.logger.info(f"銘柄リストファイル読み込み: {file_path} ({len(symbols)}銘柄)")

            return self.fetch_multiple_stocks(
                symbols=symbols,
                interval=interval,
                period=period,
                progress_callback=progress_callback,
            )

        except FileNotFoundError:
            error_msg = f"銘柄リストファイルが見つかりません: {file_path}"
            self.logger.error(error_msg)
            raise BulkDataServiceError(error_msg)
        except Exception as e:
            error_msg = f"銘柄リストファイル読み込みエラー: {e}"
            self.logger.error(error_msg)
            raise BulkDataServiceError(error_msg) from e

    def estimate_completion_time(
        self, symbol_count: int, interval: str = "1d"
    ) -> Dict[str, Any]:
        """処理完了時間を推定.

        Args:
            symbol_count: 銘柄数
            interval: 時間軸

        Returns:
            推定情報。
        """  # サンプル銘柄で処理時間を計測
        sample_symbol = "7203.T"  # トヨタ

        try:
            start_time = time.time()
            self.fetch_single_stock(sample_symbol, interval)
            sample_time = time.time() - start_time

            # 並列処理を考慮した推定時間
            estimated_total_seconds = (
                symbol_count * sample_time
            ) / self.max_workers

            return {
                "symbol_count": symbol_count,
                "sample_time_per_stock": round(sample_time, 2),
                "estimated_total_seconds": round(estimated_total_seconds, 2),
                "estimated_total_minutes": round(
                    estimated_total_seconds / 60, 2
                ),
                "max_workers": self.max_workers,
            }

        except Exception as e:
            self.logger.warning(f"処理時間推定エラー: {e}")
            return {"symbol_count": symbol_count, "error": str(e)}
