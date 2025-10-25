"""bulk_data_serviceのテスト."""

from datetime import datetime
from unittest.mock import MagicMock, Mock, mock_open, patch

import pandas as pd
import pytest

from services.bulk.bulk_service import (
    BulkDataService,
    BulkDataServiceError,
    ProgressTracker,
)
from services.stock_data.fetcher import StockDataFetchError
from services.stock_data.saver import StockDataSaveError


class TestProgressTracker:
    """ProgressTrackerクラスのテスト."""

    def test_init(self):
        """初期化のテスト."""
        tracker = ProgressTracker(total=100)

        assert tracker.total == 100
        assert tracker.processed == 0
        assert tracker.successful == 0
        assert tracker.failed == 0
        assert tracker.current_symbol is None
        assert isinstance(tracker.start_time, datetime)
        assert tracker.error_details == []

    def test_update_success(self):
        """成功時の更新テスト."""
        tracker = ProgressTracker(total=10)

        tracker.update(symbol="7203.T", success=True)

        assert tracker.processed == 1
        assert tracker.successful == 1
        assert tracker.failed == 0
        assert tracker.current_symbol == "7203.T"
        assert len(tracker.error_details) == 0

    def test_update_failure(self):
        """失敗時の更新テスト."""
        tracker = ProgressTracker(total=10)

        tracker.update(
            symbol="INVALID.T", success=False, error_message="データ取得エラー"
        )

        assert tracker.processed == 1
        assert tracker.successful == 0
        assert tracker.failed == 1
        assert tracker.current_symbol == "INVALID.T"
        assert len(tracker.error_details) == 1
        assert tracker.error_details[0]["symbol"] == "INVALID.T"
        assert tracker.error_details[0]["error"] == "データ取得エラー"

    def test_get_progress(self):
        """進捗情報取得のテスト."""
        tracker = ProgressTracker(total=100)

        for i in range(50):
            tracker.update(symbol=f"{i}.T", success=True)

        progress = tracker.get_progress()

        assert progress["total"] == 100
        assert progress["processed"] == 50
        assert progress["successful"] == 50
        assert progress["failed"] == 0
        assert progress["progress_percentage"] == 50.0
        assert (
            progress["stocks_per_second"] >= 0
        )  # 高速実行時は0になる可能性がある
        assert "estimated_completion" in progress

    def test_get_summary(self):
        """サマリー取得のテスト."""
        tracker = ProgressTracker(total=10)

        for i in range(8):
            tracker.update(symbol=f"{i}.T", success=True)

        for i in range(2):
            tracker.update(
                symbol=f"ERR{i}.T", success=False, error_message=f"エラー{i}"
            )

        summary = tracker.get_summary()

        assert summary["total"] == 10
        assert summary["processed"] == 10
        assert summary["successful"] == 8
        assert summary["failed"] == 2
        assert summary["status"] == "completed"
        assert "end_time" in summary
        assert len(summary["error_details"]) == 2


class TestBulkDataService:
    """BulkDataServiceクラスのテスト."""

    @pytest.fixture
    def service(self):
        """テスト用サービスインスタンス."""
        return BulkDataService(max_workers=2, retry_count=2)

    @pytest.fixture
    def mock_fetcher(self):
        """モックFetcher."""
        with patch("services.bulk.bulk_service.StockDataFetcher") as mock:
            yield mock

    @pytest.fixture
    def mock_saver(self):
        """モックSaver."""
        with patch("services.bulk.bulk_service.StockDataSaver") as mock:
            yield mock

    def test_init(self, service):
        """初期化のテスト."""
        assert service.max_workers == 2
        assert service.retry_count == 2
        assert service.fetcher is not None
        assert service.saver is not None

    def test_fetch_single_stock_success(self, service):
        """単一銘柄取得成功のテスト."""
        # モックの設定
        mock_df = pd.DataFrame(
            {
                "Open": [100.0],
                "High": [105.0],
                "Low": [99.0],
                "Close": [103.0],
                "Volume": [1000000],
            },
            index=[pd.Timestamp("2024-01-01")],
        )

        service.fetcher.fetch_stock_data = Mock(return_value=mock_df)
        service.saver.save_stock_data = Mock(
            return_value={"saved": 1, "skipped": 0}
        )

        # テスト実行
        result = service.fetch_single_stock(symbol="7203.T", interval="1d")

        # 検証
        assert result["success"] is True
        assert result["symbol"] == "7203.T"
        assert result["records_fetched"] == 1
        assert result["records_saved"] == 1
        service.fetcher.fetch_stock_data.assert_called_once()
        service.saver.save_stock_data.assert_called_once()

    def test_fetch_single_stock_with_retry(self, service):
        """リトライ機能のテスト."""
        # 1回目は失敗、2回目は成功
        mock_df = pd.DataFrame(
            {
                "Open": [100.0],
                "High": [105.0],
                "Low": [99.0],
                "Close": [103.0],
                "Volume": [1000000],
            },
            index=[pd.Timestamp("2024-01-01")],
        )

        service.fetcher.fetch_stock_data = Mock(
            side_effect=[StockDataFetchError("一時的なエラー"), mock_df]
        )
        service.saver.save_stock_data = Mock(return_value={"saved": 1})

        # テスト実行
        result = service.fetch_single_stock(symbol="7203.T")

        # 検証
        assert result["success"] is True
        assert result["attempt"] == 2
        assert service.fetcher.fetch_stock_data.call_count == 2

    def test_fetch_single_stock_all_retries_failed(self, service):
        """全リトライ失敗のテスト."""
        service.fetcher.fetch_stock_data = Mock(
            side_effect=StockDataFetchError("永続的なエラー")
        )

        # テスト実行
        result = service.fetch_single_stock(symbol="INVALID.T")

        # 検証
        assert result["success"] is False
        assert result["error"] == "永続的なエラー"
        assert result["attempts"] == 2  # retry_count=2なので2回試行
        assert (
            service.fetcher.fetch_stock_data.call_count == 2
        )  # 実際の呼び出し回数は2回

    def test_fetch_multiple_stocks(self, service):
        """複数銘柄取得のテスト."""
        symbols = ["7203.T", "6758.T", "9984.T"]

        # モックの設定
        service.fetch_single_stock = Mock(
            side_effect=[
                {"success": True, "symbol": "7203.T", "records_saved": 10},
                {"success": True, "symbol": "6758.T", "records_saved": 10},
                {"success": False, "symbol": "9984.T", "error": "エラー"},
            ]
        )

        # テスト実行
        summary = service.fetch_multiple_stocks(
            symbols=symbols, use_batch=False
        )

        # 検証
        assert summary["total"] == 3
        assert summary["processed"] == 3
        assert summary["successful"] == 2
        assert summary["failed"] == 1
        assert len(summary["results"]) == 3
        assert service.fetch_single_stock.call_count == 3

    def test_fetch_multiple_stocks_with_progress_callback(self, service):
        """進捗コールバック付き複数銘柄取得のテスト."""
        symbols = ["7203.T", "6758.T"]
        progress_updates = []

        def progress_callback(progress):
            progress_updates.append(progress)

        service.fetch_single_stock = Mock(
            side_effect=[
                {"success": True, "symbol": "7203.T"},
                {"success": True, "symbol": "6758.T"},
            ]
        )

        # テスト実行
        service.fetch_multiple_stocks(
            symbols=symbols,
            progress_callback=progress_callback,
            use_batch=False,
        )

        # 検証
        assert len(progress_updates) >= 2  # 最低2回は呼ばれる

    def test_fetch_all_stocks_from_list_file(self, service):
        """ファイルから銘柄リスト読み込みのテスト."""
        file_content = "7203.T\n6758.T\n9984.T\n"

        with patch("builtins.open", mock_open(read_data=file_content)):
            service.fetch_multiple_stocks = Mock(return_value={"total": 3})

            # テスト実行
            result = service.fetch_all_stocks_from_list_file("test.txt")

            # 検証
            assert result["total"] == 3
            service.fetch_multiple_stocks.assert_called_once()
            call_args = service.fetch_multiple_stocks.call_args
            assert call_args[1]["symbols"] == ["7203.T", "6758.T", "9984.T"]

    def test_fetch_all_stocks_from_list_file_not_found(self, service):
        """ファイルが見つからない場合のテスト."""
        with pytest.raises(BulkDataServiceError) as exc_info:
            service.fetch_all_stocks_from_list_file("nonexistent.txt")

        assert "見つかりません" in str(exc_info.value)

    def test_estimate_completion_time(self, service):
        """完了時間推定のテスト."""
        service.fetch_single_stock = Mock(return_value={"success": True})

        # テスト実行
        estimation = service.estimate_completion_time(symbol_count=100)

        # 検証
        assert estimation["symbol_count"] == 100
        assert "sample_time_per_stock" in estimation
        assert "estimated_total_seconds" in estimation
        assert "estimated_total_minutes" in estimation
        assert estimation["max_workers"] == 2

    def test_estimate_completion_time_error(self, service):
        """完了時間推定エラーのテスト."""
        service.fetch_single_stock = Mock(
            side_effect=StockDataFetchError("エラー")
        )

        # テスト実行
        estimation = service.estimate_completion_time(symbol_count=100)

        # 検証
        assert estimation["symbol_count"] == 100
        assert "error" in estimation
