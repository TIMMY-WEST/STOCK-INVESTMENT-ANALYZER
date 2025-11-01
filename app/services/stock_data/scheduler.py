"""Schedules periodic data fetching using APScheduler."""

from datetime import datetime
import logging
from typing import Callable, List, Optional

from apscheduler.events import EVENT_JOB_ERROR, EVENT_JOB_EXECUTED
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

from app.services.stock_data.orchestrator import StockDataOrchestrator


logger = logging.getLogger(__name__)


class StockDataScheduler:
    """株価データ取得スケジューラークラス."""

    def __init__(self):
        """初期化."""
        self.scheduler = BackgroundScheduler()
        self.orchestrator = StockDataOrchestrator()
        self.logger = logger
        self._setup_event_listeners()

    def _setup_event_listeners(self):
        """イベントリスナーの設定."""
        self.scheduler.add_listener(
            self._job_executed_listener, EVENT_JOB_EXECUTED
        )
        self.scheduler.add_listener(self._job_error_listener, EVENT_JOB_ERROR)

    def _job_executed_listener(self, event):
        """ジョブ実行成功時のリスナー."""
        self.logger.info(f"ジョブ実行成功: {event.job_id}")

    def _job_error_listener(self, event):
        """ジョブ実行エラー時のリスナー."""
        self.logger.error(f"ジョブ実行エラー: {event.job_id} - {event.exception}")

    def add_daily_update_job(
        self,
        symbol: str,
        intervals: Optional[List[str]] = None,
        hour: int = 18,
        minute: int = 0,
        job_id: Optional[str] = None,
    ):
        """日次更新ジョブを追加.

        Args:
            symbol: 銘柄コード
            intervals: 時間軸のリスト
            hour: 実行時刻（時）
            minute: 実行時刻（分）
            job_id: ジョブID（Noneの場合は自動生成）。
        """
        if job_id is None:
            job_id = f"daily_update_{symbol}_{datetime.now().timestamp()}"

        trigger = CronTrigger(hour=hour, minute=minute, timezone="Asia/Tokyo")

        self.scheduler.add_job(
            func=self._update_job,
            trigger=trigger,
            args=[symbol, intervals],
            id=job_id,
            name=f"日次更新: {symbol}",
            replace_existing=True,
        )

        self.logger.info(
            f"日次更新ジョブ追加: {symbol} " f"(実行時刻: {hour:02d}:{minute:02d})"
        )

    def add_intraday_update_job(
        self,
        symbol: str,
        intervals: List[str],
        interval_minutes: int = 5,
        start_hour: int = 9,
        end_hour: int = 15,
        job_id: Optional[str] = None,
    ):
        """日中更新ジョブを追加（分足・時間足データ用）.

        Args:
            symbol: 銘柄コード
            intervals: 時間軸のリスト（分足・時間足のみ）
            interval_minutes: 更新間隔（分）
            start_hour: 開始時刻（時）
            end_hour: 終了時刻（時）
            job_id: ジョブID（Noneの場合は自動生成）。
        """
        if job_id is None:
            job_id = f"intraday_update_{symbol}_{datetime.now().timestamp()}"

        # 営業日の指定時間帯のみ実行
        trigger = CronTrigger(
            day_of_week="mon-fri",
            hour=f"{start_hour}-{end_hour}",
            minute=f"*/{interval_minutes}",
            timezone="Asia/Tokyo",
        )

        self.scheduler.add_job(
            func=self._update_job,
            trigger=trigger,
            args=[symbol, intervals],
            id=job_id,
            name=f"日中更新: {symbol}",
            replace_existing=True,
        )

        self.logger.info(
            f"日中更新ジョブ追加: {symbol} "
            f"({interval_minutes}分間隔, {start_hour}:00-{end_hour}:00)"
        )

    def add_custom_job(
        self, func: Callable, trigger, job_id: str, name: str, **kwargs
    ):
        """カスタムジョブを追加.

        Args:
            func: 実行する関数
            trigger: APSchedulerトリガー
            job_id: ジョブID
            name: ジョブ名
            **kwargs: その他のAPSchedulerパラメータ。
        """
        self.scheduler.add_job(
            func=func,
            trigger=trigger,
            id=job_id,
            name=name,
            replace_existing=True,
            **kwargs,
        )

        self.logger.info(f"カスタムジョブ追加: {name} (ID: {job_id})")

    def _update_job(self, symbol: str, intervals: Optional[List[str]] = None):
        """更新ジョブの実行（内部メソッド）.

        Args:
            symbol: 銘柄コード
            intervals: 時間軸のリスト。
        """
        try:
            self.logger.info(f"更新ジョブ開始: {symbol}")

            result = self.orchestrator.update_all_timeframes(
                symbol=symbol, intervals=intervals
            )

            self.logger.info(
                f"更新ジョブ完了: {symbol} - "
                f"成功: {result['success_count']}/{result['total_intervals']}"
            )

        except Exception as e:
            self.logger.error(f"更新ジョブエラー: {symbol}: {e}")

    def remove_job(self, job_id: str):
        """ジョブを削除.

        Args:
            job_id: ジョブID。
        """
        try:
            self.scheduler.remove_job(job_id)
            self.logger.info(f"ジョブ削除: {job_id}")
        except Exception as e:
            self.logger.warning(f"ジョブ削除失敗: {job_id}: {e}")

    def start(self):
        """スケジューラーを開始."""
        if not self.scheduler.running:
            self.scheduler.start()
            self.logger.info("スケジューラー開始")

    def shutdown(self, wait: bool = True):
        """スケジューラーを停止.

        Args:
            wait: True の場合、実行中のジョブが完了するまで待機。
        """
        if self.scheduler.running:
            self.scheduler.shutdown(wait=wait)
            self.logger.info("スケジューラー停止")

    def get_jobs(self):
        """登録されているジョブのリストを取得.

        Returns:
            ジョブのリスト。
        """
        return self.scheduler.get_jobs()

    def print_jobs(self):
        """登録されているジョブを表示."""
        jobs = self.get_jobs()
        if not jobs:
            print("登録されているジョブはありません")
            return

        print(f"\n登録されているジョブ: {len(jobs)}件")
        print("-" * 80)
        for job in jobs:
            print(f"ID: {job.id}")
            print(f"名前: {job.name}")
            print(f"次回実行: {job.next_run_time}")
            print("-" * 80)


# グローバルスケジューラーインスタンス（オプション）
_global_scheduler: Optional[StockDataScheduler] = None


def get_scheduler() -> StockDataScheduler:
    """グローバルスケジューラーインスタンスを取得.

    Returns:
        StockDataSchedulerインスタンス。
    """
    global _global_scheduler
    if _global_scheduler is None:
        _global_scheduler = StockDataScheduler()
    return _global_scheduler
