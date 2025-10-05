"""全銘柄一括取得サービス

全銘柄の株価データを並列処理で効率的に一括取得します。
"""

import asyncio
import logging
from typing import List, Dict, Any, Optional, Callable
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
import time

from services.stock_data_fetcher import StockDataFetcher, StockDataFetchError
from services.stock_data_saver import StockDataSaver, StockDataSaveError

logger = logging.getLogger(__name__)


class BulkDataServiceError(Exception):
    """一括データ取得エラー"""
    pass


class ProgressTracker:
    """進捗トラッカー"""

    def __init__(self, total: int):
        """
        初期化

        Args:
            total: 処理対象の総数
        """
        self.total = total
        self.processed = 0
        self.successful = 0
        self.failed = 0
        self.start_time = datetime.now()
        self.current_symbol = None
        self.error_details: List[Dict[str, Any]] = []

    def update(self, symbol: str, success: bool, error_message: Optional[str] = None):
        """
        進捗を更新

        Args:
            symbol: 処理した銘柄コード
            success: 成功したかどうか
            error_message: エラーメッセージ（失敗時）
        """
        self.processed += 1
        self.current_symbol = symbol

        if success:
            self.successful += 1
        else:
            self.failed += 1
            if error_message:
                self.error_details.append({
                    'symbol': symbol,
                    'error': error_message,
                    'timestamp': datetime.now().isoformat()
                })

    def get_progress(self) -> Dict[str, Any]:
        """
        現在の進捗情報を取得

        Returns:
            進捗情報の辞書
        """
        elapsed_time = (datetime.now() - self.start_time).total_seconds()
        progress_percentage = (self.processed / self.total * 100) if self.total > 0 else 0

        # 処理速度の計算
        stocks_per_second = self.processed / elapsed_time if elapsed_time > 0 else 0

        # 完了予測時刻の計算
        remaining = self.total - self.processed
        eta_seconds = remaining / stocks_per_second if stocks_per_second > 0 else 0
        eta = datetime.now().timestamp() + eta_seconds

        return {
            'total': self.total,
            'processed': self.processed,
            'successful': self.successful,
            'failed': self.failed,
            'progress_percentage': round(progress_percentage, 2),
            'current_symbol': self.current_symbol,
            'elapsed_time': round(elapsed_time, 2),
            'stocks_per_second': round(stocks_per_second, 2),
            'estimated_completion': datetime.fromtimestamp(eta).isoformat() if eta_seconds > 0 else None,
            'error_count': len(self.error_details)
        }

    def get_summary(self) -> Dict[str, Any]:
        """
        処理完了後のサマリーを取得

        Returns:
            サマリー情報の辞書
        """
        progress = self.get_progress()
        return {
            **progress,
            'status': 'completed',
            'end_time': datetime.now().isoformat(),
            'error_details': self.error_details[:100]  # 最大100件のエラー詳細
        }


class BulkDataService:
    """全銘柄一括取得サービスクラス"""

    def __init__(self, max_workers: int = 10, retry_count: int = 3):
        """
        初期化

        Args:
            max_workers: 最大並列ワーカー数
            retry_count: リトライ回数
        """
        self.fetcher = StockDataFetcher()
        self.saver = StockDataSaver()
        self.max_workers = max_workers
        self.retry_count = retry_count
        self.logger = logger

    def fetch_single_stock(
        self,
        symbol: str,
        interval: str = '1d',
        period: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        単一銘柄のデータを取得・保存（リトライ機能付き）

        Args:
            symbol: 銘柄コード
            interval: 時間軸
            period: 取得期間

        Returns:
            処理結果
        """
        last_error = None

        for attempt in range(self.retry_count):
            try:
                # データ取得
                df = self.fetcher.fetch_stock_data(
                    symbol=symbol,
                    interval=interval,
                    period=period
                )

                # データ変換
                data_list = self.fetcher.convert_to_dict(df, interval)

                # データ保存
                save_result = self.saver.save_stock_data(
                    symbol=symbol,
                    interval=interval,
                    data_list=data_list
                )

                return {
                    'success': True,
                    'symbol': symbol,
                    'interval': interval,
                    'records_fetched': len(data_list),
                    'records_saved': save_result.get('saved', 0),
                    'attempt': attempt + 1
                }

            except (StockDataFetchError, StockDataSaveError) as e:
                last_error = str(e)
                self.logger.warning(
                    f"銘柄 {symbol} の取得失敗 (試行 {attempt + 1}/{self.retry_count}): {e}"
                )

                # 最終試行でない場合は待機
                if attempt < self.retry_count - 1:
                    time.sleep(2 ** attempt)  # 指数バックオフ

            except Exception as e:
                last_error = str(e)
                self.logger.error(f"予期しないエラー: {symbol}: {e}")
                break  # 予期しないエラーの場合はリトライしない

        return {
            'success': False,
            'symbol': symbol,
            'interval': interval,
            'error': last_error,
            'attempts': self.retry_count
        }

    def fetch_multiple_stocks(
        self,
        symbols: List[str],
        interval: str = '1d',
        period: Optional[str] = None,
        progress_callback: Optional[Callable[[Dict[str, Any]], None]] = None
    ) -> Dict[str, Any]:
        """
        複数銘柄のデータを並列取得・保存

        Args:
            symbols: 銘柄コードのリスト
            interval: 時間軸
            period: 取得期間
            progress_callback: 進捗通知用コールバック関数

        Returns:
            処理結果のサマリー
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
                    self.fetch_single_stock,
                    symbol,
                    interval,
                    period
                ): symbol
                for symbol in symbols
            }

            # 完了したタスクから順次処理
            for future in as_completed(future_to_symbol):
                symbol = future_to_symbol[future]

                try:
                    result = future.result()
                    results.append(result)

                    # 進捗更新
                    tracker.update(
                        symbol=symbol,
                        success=result.get('success', False),
                        error_message=result.get('error')
                    )

                    # 進捗コールバック実行
                    if progress_callback:
                        try:
                            progress_callback(tracker.get_progress())
                        except Exception as e:
                            self.logger.error(f"進捗コールバックエラー: {e}")

                    # 進捗ログ出力（10件ごと）
                    if tracker.processed % 10 == 0 or tracker.processed == tracker.total:
                        progress = tracker.get_progress()
                        self.logger.info(
                            f"進捗: {progress['processed']}/{progress['total']} "
                            f"({progress['progress_percentage']}%) - "
                            f"成功: {progress['successful']}, "
                            f"失敗: {progress['failed']}, "
                            f"速度: {progress['stocks_per_second']}銘柄/秒"
                        )

                except Exception as e:
                    self.logger.error(f"タスク実行エラー ({symbol}): {e}")
                    tracker.update(symbol=symbol, success=False, error_message=str(e))
                    results.append({
                        'success': False,
                        'symbol': symbol,
                        'error': str(e)
                    })

        # サマリー作成
        summary = tracker.get_summary()
        summary['results'] = results

        self.logger.info(
            f"全銘柄一括取得完了: "
            f"成功 {summary['successful']}/{summary['total']}, "
            f"失敗 {summary['failed']}, "
            f"処理時間 {summary['elapsed_time']}秒"
        )

        return summary

    def fetch_all_stocks_from_list_file(
        self,
        file_path: str,
        interval: str = '1d',
        period: Optional[str] = None,
        progress_callback: Optional[Callable[[Dict[str, Any]], None]] = None
    ) -> Dict[str, Any]:
        """
        ファイルから銘柄リストを読み込んで一括取得

        Args:
            file_path: 銘柄コードリストファイルのパス（1行1銘柄）
            interval: 時間軸
            period: 取得期間
            progress_callback: 進捗通知用コールバック関数

        Returns:
            処理結果のサマリー
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                symbols = [line.strip() for line in f if line.strip()]

            self.logger.info(f"銘柄リストファイル読み込み: {file_path} ({len(symbols)}銘柄)")

            return self.fetch_multiple_stocks(
                symbols=symbols,
                interval=interval,
                period=period,
                progress_callback=progress_callback
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
        self,
        symbol_count: int,
        interval: str = '1d'
    ) -> Dict[str, Any]:
        """
        処理完了時間を推定

        Args:
            symbol_count: 銘柄数
            interval: 時間軸

        Returns:
            推定情報
        """
        # サンプル銘柄で処理時間を計測
        sample_symbol = '7203.T'  # トヨタ

        try:
            start_time = time.time()
            self.fetch_single_stock(sample_symbol, interval)
            sample_time = time.time() - start_time

            # 並列処理を考慮した推定時間
            estimated_total_seconds = (symbol_count * sample_time) / self.max_workers

            return {
                'symbol_count': symbol_count,
                'sample_time_per_stock': round(sample_time, 2),
                'estimated_total_seconds': round(estimated_total_seconds, 2),
                'estimated_total_minutes': round(estimated_total_seconds / 60, 2),
                'max_workers': self.max_workers
            }

        except Exception as e:
            self.logger.warning(f"処理時間推定エラー: {e}")
            return {
                'symbol_count': symbol_count,
                'error': str(e)
            }
