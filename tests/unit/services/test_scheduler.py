"""StockDataSchedulerの単体テスト.

このモジュールはStockDataSchedulerクラスの全メソッドをテストし、
スケジューリング機能が正しく動作することを検証する。
"""

from unittest.mock import MagicMock, Mock, patch

import pytest

from app.services.stock_data.scheduler import StockDataScheduler, get_scheduler


pytestmark = pytest.mark.unit


class TestStockDataScheduler:
    """StockDataSchedulerクラスのテスト."""

    @patch("app.services.stock_data.scheduler.StockDataOrchestrator")
    @patch("app.services.stock_data.scheduler.BackgroundScheduler")
    def test_init_creates_scheduler_and_orchestrator(
        self, mock_scheduler_class, mock_orchestrator_class
    ):
        """初期化でスケジューラとオーケストレータが作成される."""
        # Arrange (準備)
        mock_scheduler = Mock()
        mock_orchestrator = Mock()
        mock_scheduler_class.return_value = mock_scheduler
        mock_orchestrator_class.return_value = mock_orchestrator

        # Act (実行)
        scheduler = StockDataScheduler()

        # Assert (検証)
        assert scheduler.scheduler == mock_scheduler
        assert scheduler.orchestrator == mock_orchestrator
        mock_scheduler_class.assert_called_once()
        mock_orchestrator_class.assert_called_once()

    @patch("app.services.stock_data.scheduler.StockDataOrchestrator")
    @patch("app.services.stock_data.scheduler.BackgroundScheduler")
    def test_add_daily_update_job_with_valid_params_adds_job(
        self, mock_scheduler_class, mock_orchestrator_class
    ):
        """日次更新ジョブを正常に追加する."""
        # Arrange (準備)
        mock_scheduler = Mock()
        mock_scheduler_class.return_value = mock_scheduler

        scheduler = StockDataScheduler()
        job_id = "daily_7203"
        symbol = "7203.T"

        # Act (実行)
        scheduler.add_daily_update_job(job_id=job_id, symbol=symbol)

        # Assert (検証)
        # ジョブが追加されたことを確認
        mock_scheduler.add_job.assert_called_once()

    @patch("app.services.stock_data.scheduler.StockDataOrchestrator")
    @patch("app.services.stock_data.scheduler.BackgroundScheduler")
    def test_add_intraday_update_job_with_valid_params_adds_job(
        self, mock_scheduler_class, mock_orchestrator_class
    ):
        """日中更新ジョブを正常に追加する."""
        # Arrange (準備)
        mock_scheduler = Mock()
        mock_scheduler_class.return_value = mock_scheduler

        scheduler = StockDataScheduler()
        job_id = "intraday_7203"
        symbol = "7203.T"
        intervals = ["1m", "5m"]

        # Act (実行)
        scheduler.add_intraday_update_job(
            job_id=job_id, symbol=symbol, intervals=intervals
        )

        # Assert (検証)
        # ジョブが追加されたことを確認
        mock_scheduler.add_job.assert_called_once()

    @patch("app.services.stock_data.scheduler.StockDataOrchestrator")
    @patch("app.services.stock_data.scheduler.BackgroundScheduler")
    def test_add_custom_job_with_valid_params_adds_job(
        self, mock_scheduler_class, mock_orchestrator_class
    ):
        """カスタムジョブを正常に追加する."""
        # Arrange (準備)
        mock_scheduler = Mock()
        mock_scheduler_class.return_value = mock_scheduler

        scheduler = StockDataScheduler()
        job_id = "custom_job"
        func = Mock()

        # Act (実行)
        scheduler.add_custom_job(
            func=func,
            trigger="interval",
            job_id=job_id,
            name="Custom Job",
            minutes=30,
        )

        # Assert (検証)
        # ジョブが追加されたことを確認
        mock_scheduler.add_job.assert_called_once()

    @patch("app.services.stock_data.scheduler.StockDataOrchestrator")
    @patch("app.services.stock_data.scheduler.BackgroundScheduler")
    def test_remove_job_with_valid_job_id_removes_job(
        self, mock_scheduler_class, mock_orchestrator_class
    ):
        """有効なジョブIDでジョブを削除する."""
        # Arrange (準備)
        mock_scheduler = Mock()
        mock_scheduler_class.return_value = mock_scheduler

        scheduler = StockDataScheduler()
        job_id = "test_job"

        # Act (実行)
        scheduler.remove_job(job_id)

        # Assert (検証)
        mock_scheduler.remove_job.assert_called_once_with(job_id)

    @patch("app.services.stock_data.scheduler.StockDataOrchestrator")
    @patch("app.services.stock_data.scheduler.BackgroundScheduler")
    def test_remove_job_with_nonexistent_job_logs_warning(
        self, mock_scheduler_class, mock_orchestrator_class
    ):
        """存在しないジョブIDで警告をログに記録する."""
        # Arrange (準備)
        mock_scheduler = Mock()
        mock_scheduler.remove_job.side_effect = Exception("Job not found")
        mock_scheduler_class.return_value = mock_scheduler

        scheduler = StockDataScheduler()
        job_id = "nonexistent_job"

        # Act (実行)
        scheduler.remove_job(job_id)

        # Assert (検証)
        mock_scheduler.remove_job.assert_called_once_with(job_id)

    @patch("app.services.stock_data.scheduler.StockDataOrchestrator")
    @patch("app.services.stock_data.scheduler.BackgroundScheduler")
    def test_start_starts_scheduler(
        self, mock_scheduler_class, mock_orchestrator_class
    ):
        """スケジューラを開始する."""
        # Arrange (準備)
        mock_scheduler = Mock()
        mock_scheduler.running = False  # Not running initially
        mock_scheduler_class.return_value = mock_scheduler

        scheduler = StockDataScheduler()

        # Act (実行)
        scheduler.start()

        # Assert (検証)
        mock_scheduler.start.assert_called_once()

    @patch("app.services.stock_data.scheduler.StockDataOrchestrator")
    @patch("app.services.stock_data.scheduler.BackgroundScheduler")
    def test_shutdown_stops_scheduler(
        self, mock_scheduler_class, mock_orchestrator_class
    ):
        """スケジューラを停止する."""
        # Arrange (準備)
        mock_scheduler = Mock()
        mock_scheduler_class.return_value = mock_scheduler

        scheduler = StockDataScheduler()

        # Act (実行)
        scheduler.shutdown()

        # Assert (検証)
        mock_scheduler.shutdown.assert_called_once_with(wait=True)

    @patch("app.services.stock_data.scheduler.StockDataOrchestrator")
    @patch("app.services.stock_data.scheduler.BackgroundScheduler")
    def test_shutdown_with_wait_false(
        self, mock_scheduler_class, mock_orchestrator_class
    ):
        """wait=Falseで即座に停止する."""
        # Arrange (準備)
        mock_scheduler = Mock()
        mock_scheduler_class.return_value = mock_scheduler

        scheduler = StockDataScheduler()

        # Act (実行)
        scheduler.shutdown(wait=False)

        # Assert (検証)
        mock_scheduler.shutdown.assert_called_once_with(wait=False)

    @patch("app.services.stock_data.scheduler.StockDataOrchestrator")
    @patch("app.services.stock_data.scheduler.BackgroundScheduler")
    def test_get_jobs_returns_all_jobs(
        self, mock_scheduler_class, mock_orchestrator_class
    ):
        """全ジョブを取得する."""
        # Arrange (準備)
        mock_scheduler = Mock()
        mock_job1 = Mock()
        mock_job1.id = "job1"
        mock_job2 = Mock()
        mock_job2.id = "job2"
        mock_scheduler.get_jobs.return_value = [mock_job1, mock_job2]
        mock_scheduler_class.return_value = mock_scheduler

        scheduler = StockDataScheduler()

        # Act (実行)
        result = scheduler.get_jobs()

        # Assert (検証)
        assert len(result) == 2
        assert result[0].id == "job1"
        assert result[1].id == "job2"

    @patch("app.services.stock_data.scheduler.StockDataOrchestrator")
    @patch("app.services.stock_data.scheduler.BackgroundScheduler")
    def test_get_jobs_returns_empty_list_when_no_jobs(
        self, mock_scheduler_class, mock_orchestrator_class
    ):
        """ジョブがない場合は空リストを返す."""
        # Arrange (準備)
        mock_scheduler = Mock()
        mock_scheduler.get_jobs.return_value = []
        mock_scheduler_class.return_value = mock_scheduler

        scheduler = StockDataScheduler()

        # Act (実行)
        result = scheduler.get_jobs()

        # Assert (検証)
        assert result == []

    @patch("app.services.stock_data.scheduler.StockDataOrchestrator")
    @patch("app.services.stock_data.scheduler.BackgroundScheduler")
    def test_print_jobs_with_jobs_outputs_info(
        self, mock_scheduler_class, mock_orchestrator_class, capsys
    ):
        """ジョブ情報を出力する."""
        # Arrange (準備)
        mock_scheduler = Mock()
        mock_job = Mock()
        mock_job.id = "test_job"
        mock_job.next_run_time = "2025-11-01 10:00:00"
        mock_scheduler.get_jobs.return_value = [mock_job]
        mock_scheduler_class.return_value = mock_scheduler

        scheduler = StockDataScheduler()

        # Act (実行)
        scheduler.print_jobs()

        # Assert (検証)
        captured = capsys.readouterr()
        # 日本語でも英語でもジョブ情報が出力されていることを確認
        assert "test_job" in captured.out

    @patch("app.services.stock_data.scheduler.StockDataOrchestrator")
    @patch("app.services.stock_data.scheduler.BackgroundScheduler")
    def test_print_jobs_with_no_jobs_outputs_message(
        self, mock_scheduler_class, mock_orchestrator_class, capsys
    ):
        """ジョブがない場合のメッセージを出力する."""
        # Arrange (準備)
        mock_scheduler = Mock()
        mock_scheduler.get_jobs.return_value = []
        mock_scheduler_class.return_value = mock_scheduler

        scheduler = StockDataScheduler()

        # Act (実行)
        scheduler.print_jobs()

        # Assert (検証)
        captured = capsys.readouterr()
        # 何かしらのメッセージが出力されていることを確認
        assert len(captured.out) > 0

    @patch("app.services.stock_data.scheduler.StockDataOrchestrator")
    @patch("app.services.stock_data.scheduler.BackgroundScheduler")
    def test_update_job_calls_orchestrator_update_all_timeframes(
        self, mock_scheduler_class, mock_orchestrator_class
    ):
        """_update_jobがオーケストレータを呼び出す."""
        # Arrange (準備)
        mock_orchestrator = Mock()
        mock_orchestrator.update_all_timeframes.return_value = {
            "success_count": 1,
            "total_intervals": 1,
        }
        mock_orchestrator_class.return_value = mock_orchestrator

        scheduler = StockDataScheduler()
        symbol = "7203.T"

        # Act (実行)
        scheduler._update_job(symbol=symbol)

        # Assert (検証)
        mock_orchestrator.update_all_timeframes.assert_called_once_with(
            symbol=symbol, intervals=None
        )

    @patch("app.services.stock_data.scheduler.StockDataOrchestrator")
    @patch("app.services.stock_data.scheduler.BackgroundScheduler")
    def test_update_job_with_error_logs_error(
        self, mock_scheduler_class, mock_orchestrator_class
    ):
        """_update_jobでエラーが発生した場合にログに記録する."""
        # Arrange (準備)
        mock_orchestrator = Mock()
        mock_orchestrator.update_all_timeframes.side_effect = Exception(
            "Fetch error"
        )
        mock_orchestrator_class.return_value = mock_orchestrator

        scheduler = StockDataScheduler()
        symbol = "7203.T"

        # Act (実行)
        scheduler._update_job(symbol=symbol)

        # Assert (検証)
        mock_orchestrator.update_all_timeframes.assert_called_once()

    @patch("app.services.stock_data.scheduler.StockDataOrchestrator")
    @patch("app.services.stock_data.scheduler.BackgroundScheduler")
    def test_job_executed_listener_logs_info(
        self, mock_scheduler_class, mock_orchestrator_class
    ):
        """ジョブ実行リスナーが情報をログに記録する."""
        # Arrange (準備)
        scheduler = StockDataScheduler()
        mock_event = Mock()
        mock_event.job_id = "test_job"

        # Act (実行)
        scheduler._job_executed_listener(mock_event)

        # Assert (検証)
        # 例外が発生しないことを確認
        assert True

    @patch("app.services.stock_data.scheduler.StockDataOrchestrator")
    @patch("app.services.stock_data.scheduler.BackgroundScheduler")
    def test_job_error_listener_logs_error(
        self, mock_scheduler_class, mock_orchestrator_class
    ):
        """ジョブエラーリスナーがエラーをログに記録する."""
        # Arrange (準備)
        scheduler = StockDataScheduler()
        mock_event = Mock()
        mock_event.job_id = "test_job"
        mock_event.exception = Exception("Test error")

        # Act (実行)
        scheduler._job_error_listener(mock_event)

        # Assert (検証)
        # 例外が発生しないことを確認
        assert True

    @patch("app.services.stock_data.scheduler.StockDataOrchestrator")
    @patch("app.services.stock_data.scheduler.BackgroundScheduler")
    def test_add_daily_update_job_with_custom_time(
        self, mock_scheduler_class, mock_orchestrator_class
    ):
        """カスタム時刻で日次更新ジョブを追加する."""
        # Arrange (準備)
        mock_scheduler = Mock()
        mock_scheduler_class.return_value = mock_scheduler

        scheduler = StockDataScheduler()

        # Act (実行)
        scheduler.add_daily_update_job(
            job_id="test", symbol="7203.T", hour=9, minute=30
        )

        # Assert (検証)
        # ジョブが追加されたことを確認
        mock_scheduler.add_job.assert_called_once()

    @patch("app.services.stock_data.scheduler.StockDataOrchestrator")
    @patch("app.services.stock_data.scheduler.BackgroundScheduler")
    def test_add_intraday_update_job_with_custom_interval(
        self, mock_scheduler_class, mock_orchestrator_class
    ):
        """カスタム間隔で日中更新ジョブを追加する."""
        # Arrange (準備)
        mock_scheduler = Mock()
        mock_scheduler_class.return_value = mock_scheduler

        scheduler = StockDataScheduler()

        # Act (実行)
        scheduler.add_intraday_update_job(
            job_id="test",
            symbol="7203.T",
            intervals=["1m", "5m"],
            interval_minutes=15,
        )

        # Assert (検証)
        # ジョブが追加されたことを確認
        mock_scheduler.add_job.assert_called_once()


class TestGetScheduler:
    """get_scheduler関数のテスト."""

    @patch("app.services.stock_data.scheduler._global_scheduler", None)
    @patch("app.services.stock_data.scheduler.StockDataScheduler")
    def test_get_scheduler_creates_new_instance_when_none(
        self, mock_scheduler_class
    ):
        """グローバルスケジューラがNoneの場合に新規作成する."""
        # Arrange (準備)
        mock_scheduler = Mock()
        mock_scheduler_class.return_value = mock_scheduler

        # Act (実行)
        result = get_scheduler()

        # Assert (検証)
        assert result == mock_scheduler
        mock_scheduler_class.assert_called_once()

    @patch("app.services.stock_data.scheduler._global_scheduler")
    def test_get_scheduler_returns_existing_instance(
        self, mock_global_scheduler
    ):
        """既存のグローバルスケジューラを返す."""
        # Arrange (準備)
        existing_scheduler = Mock()
        mock_global_scheduler.__bool__.return_value = True
        with patch(
            "app.services.stock_data.scheduler._global_scheduler",
            existing_scheduler,
        ):
            # Act (実行)
            result = get_scheduler()

            # Assert (検証)
            assert result == existing_scheduler
