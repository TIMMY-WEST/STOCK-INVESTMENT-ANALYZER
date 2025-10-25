"""進捗トラッカーとメトリクス収集のテスト.

Phase 2要件: メトリクス収集機能のテスト。
"""

import time

import pytest

from app.services.bulk.bulk_service import ProgressTracker


class TestProgressTracker:
    """進捗トラッカーのテスト."""

    def test_initialization(self):
        """初期化のテスト."""
        tracker = ProgressTracker(total=100)

        assert tracker.total == 100
        assert tracker.processed == 0
        assert tracker.successful == 0
        assert tracker.failed == 0
        assert tracker.current_symbol is None
        assert len(tracker.error_details) == 0

    def test_update_success(self):
        """成功時の更新テスト."""
        tracker = ProgressTracker(total=10)

        tracker.update(
            symbol="7203.T",
            success=True,
            duration_ms=1500,
            records_fetched=50,
            records_saved=50,
        )

        assert tracker.processed == 1
        assert tracker.successful == 1
        assert tracker.failed == 0
        assert tracker.current_symbol == "7203.T"
        assert len(tracker.processing_times) == 1
        assert tracker.processing_times[0] == 1500
        assert sum(tracker.records_fetched_list) == 50
        assert sum(tracker.records_saved_list) == 50

    def test_update_failed(self):
        """失敗時の更新テスト."""
        tracker = ProgressTracker(total=10)

        tracker.update(
            symbol="9999.T", success=False, error_message="Connection timeout"
        )

        assert tracker.processed == 1
        assert tracker.successful == 0
        assert tracker.failed == 1
        assert tracker.current_symbol == "9999.T"
        assert len(tracker.error_details) == 1
        assert tracker.error_details[0]["symbol"] == "9999.T"
        assert "Connection timeout" in tracker.error_details[0]["error"]

    def test_get_progress(self):
        """進捗情報取得のテスト."""
        tracker = ProgressTracker(total=10)

        # 複数の銘柄を処理
        for i in range(5):
            tracker.update(
                symbol=f"stock{i}.T",
                success=True,
                duration_ms=1000,
                records_fetched=50,
                records_saved=45,
            )

        time.sleep(0.1)  # わずかに時間経過

        progress = tracker.get_progress()

        assert progress["total"] == 10
        assert progress["processed"] == 5
        assert progress["successful"] == 5
        assert progress["failed"] == 0
        assert progress["progress_percentage"] == 50.0
        assert progress["elapsed_time"] > 0
        assert progress["stocks_per_second"] > 0
        assert progress["estimated_completion"] is not None

        # Phase 2メトリクス
        assert "throughput" in progress
        assert progress["throughput"]["stocks_per_minute"] > 0
        assert progress["throughput"]["records_per_minute"] > 0

        assert "performance" in progress
        assert progress["performance"]["success_rate"] == 100.0
        assert progress["performance"]["avg_processing_time_ms"] == 1000.0
        assert progress["performance"]["total_records_fetched"] == 250
        assert progress["performance"]["total_records_saved"] == 225

    def test_metrics_calculation(self):
        """メトリクス計算のテスト."""
        tracker = ProgressTracker(total=20)

        # 成功: 15件、失敗: 5件
        for i in range(15):
            tracker.update(
                symbol=f"stock{i}.T",
                success=True,
                duration_ms=1000 + i * 100,  # 処理時間を変化させる
                records_fetched=50,
                records_saved=48,
            )

        for i in range(5):
            tracker.update(
                symbol=f"fail{i}.T", success=False, error_message="Test error"
            )

        progress = tracker.get_progress()

        # 成功率の確認
        assert progress["performance"]["success_rate"] == 75.0  # 15/20 = 75%

        # 平均処理時間の確認
        expected_avg = sum(1000 + i * 100 for i in range(15)) / 15
        assert (
            abs(
                progress["performance"]["avg_processing_time_ms"]
                - expected_avg
            )
            < 0.1
        )

        # レコード数の確認
        assert (
            progress["performance"]["total_records_fetched"] == 750
        )  # 15 * 50
        assert progress["performance"]["total_records_saved"] == 720  # 15 * 48

    def test_get_summary(self):
        """サマリー取得のテスト."""
        tracker = ProgressTracker(total=5)

        for i in range(5):
            tracker.update(
                symbol=f"stock{i}.T",
                success=True,
                duration_ms=1000,
                records_fetched=50,
                records_saved=50,
            )

        summary = tracker.get_summary()

        assert summary["status"] == "completed"
        assert summary["total"] == 5
        assert summary["processed"] == 5
        assert summary["successful"] == 5
        assert "end_time" in summary
        assert "throughput" in summary
        assert "performance" in summary

    def test_empty_metrics(self):
        """空のメトリクスのテスト."""
        tracker = ProgressTracker(total=10)

        progress = tracker.get_progress()

        # 処理が0件の場合でもエラーにならないこと
        assert progress["throughput"]["stocks_per_minute"] == 0
        assert progress["performance"]["success_rate"] == 0
        assert progress["performance"]["avg_processing_time_ms"] == 0
        assert progress["performance"]["total_records_fetched"] == 0
        assert progress["performance"]["total_records_saved"] == 0

    def test_eta_calculation(self):
        """ETA計算のテスト."""
        tracker = ProgressTracker(total=10)

        # 5件処理
        for i in range(5):
            tracker.update(
                symbol=f"stock{i}.T",
                success=True,
                duration_ms=1000,
                records_fetched=50,
                records_saved=50,
            )

        time.sleep(0.5)  # 0.5秒待機

        progress = tracker.get_progress()

        # ETAが計算されていることを確認
        assert progress["estimated_completion"] is not None

        # 残り5件なので、ETAは現在時刻より未来であること
        from datetime import datetime

        eta = datetime.fromisoformat(progress["estimated_completion"])
        assert eta > datetime.now()
