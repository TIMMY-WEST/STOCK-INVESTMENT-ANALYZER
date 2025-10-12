"""ErrorHandlerクラスのテスト"""

import pytest
from unittest.mock import Mock, patch
from requests.exceptions import HTTPError, Timeout, ConnectionError

from services.error_handler import (
    ErrorHandler,
    ErrorType,
    ErrorAction,
    ErrorRecord
)


class TestErrorHandler:
    """ErrorHandlerクラスのテストケース"""

    @pytest.fixture
    def error_handler(self):
        """ErrorHandlerインスタンスを作成"""
        return ErrorHandler(max_retries=3, retry_delay=1, backoff_multiplier=2)

    # ===== エラー分類テスト =====

    def test_classify_timeout_error_as_temporary(self, error_handler):
        """タイムアウトエラーを一時的エラーとして分類"""
        error = Timeout("Request timed out")
        error_type = error_handler.classify_error(error)
        assert error_type == ErrorType.TEMPORARY

    def test_classify_connection_error_as_temporary(self, error_handler):
        """接続エラーを一時的エラーとして分類"""
        error = ConnectionError("Failed to connect")
        error_type = error_handler.classify_error(error)
        assert error_type == ErrorType.TEMPORARY

    def test_classify_429_as_temporary(self, error_handler):
        """429エラー（Rate Limit）を一時的エラーとして分類"""
        # HTTPErrorのモック作成
        response_mock = Mock()
        response_mock.status_code = 429
        error = HTTPError()
        error.response = response_mock

        error_type = error_handler.classify_error(error)
        assert error_type == ErrorType.TEMPORARY

    def test_classify_503_as_temporary(self, error_handler):
        """503エラー（Service Unavailable）を一時的エラーとして分類"""
        response_mock = Mock()
        response_mock.status_code = 503
        error = HTTPError()
        error.response = response_mock

        error_type = error_handler.classify_error(error)
        assert error_type == ErrorType.TEMPORARY

    def test_classify_404_as_permanent(self, error_handler):
        """404エラーを永続的エラーとして分類"""
        response_mock = Mock()
        response_mock.status_code = 404
        error = HTTPError()
        error.response = response_mock

        error_type = error_handler.classify_error(error)
        assert error_type == ErrorType.PERMANENT

    def test_classify_value_error_as_permanent(self, error_handler):
        """ValueErrorを永続的エラーとして分類"""
        error = ValueError("Invalid data format")
        error_type = error_handler.classify_error(error)
        assert error_type == ErrorType.PERMANENT

    # ===== エラー処理テスト =====

    def test_handle_temporary_error_returns_retry(self, error_handler):
        """一時的エラーの場合、RETRYアクションを返す"""
        error = Timeout("Request timed out")
        action = error_handler.handle_error(error, "7203.T", {'retry_count': 0})
        assert action == ErrorAction.RETRY

    def test_handle_temporary_error_max_retries_returns_skip(self, error_handler):
        """最大リトライ回数到達時、SKIPアクションを返す"""
        error = Timeout("Request timed out")
        action = error_handler.handle_error(error, "7203.T", {'retry_count': 3})
        assert action == ErrorAction.SKIP

    def test_handle_permanent_error_returns_skip(self, error_handler):
        """永続的エラーの場合、SKIPアクションを返す"""
        error = ValueError("Invalid data")
        action = error_handler.handle_error(error, "7203.T", {'retry_count': 0})
        assert action == ErrorAction.SKIP

    # ===== リトライバックオフテスト =====

    @patch('time.sleep')
    def test_retry_with_backoff_delays_correctly(self, mock_sleep, error_handler):
        """指数バックオフで正しい待機時間を計算"""
        # 1回目のリトライ: 1 * (2 ^ 0) = 1秒
        error_handler.retry_with_backoff(0)
        mock_sleep.assert_called_with(1)

        # 2回目のリトライ: 1 * (2 ^ 1) = 2秒
        error_handler.retry_with_backoff(1)
        mock_sleep.assert_called_with(2)

        # 3回目のリトライ: 1 * (2 ^ 2) = 4秒
        error_handler.retry_with_backoff(2)
        mock_sleep.assert_called_with(4)

    # ===== エラー記録テスト =====

    def test_error_records_are_saved(self, error_handler):
        """エラー記録が保存される"""
        error = ValueError("Test error")
        error_handler.handle_error(error, "7203.T", {'retry_count': 0})

        assert len(error_handler.error_records) == 1
        record = error_handler.error_records[0]
        assert record.stock_code == "7203.T"
        assert record.error_type == "permanent"
        assert record.exception_class == "ValueError"

    def test_error_statistics_are_updated(self, error_handler):
        """エラー統計が更新される"""
        error_handler.handle_error(Timeout("timeout"), "7203.T", {'retry_count': 0})
        error_handler.handle_error(ValueError("value error"), "6758.T", {'retry_count': 0})

        stats = error_handler.get_error_statistics()
        assert stats['total_errors'] == 2
        assert stats['error_stats']['temporary'] == 1
        assert stats['error_stats']['permanent'] == 1

    # ===== エラーレポート生成テスト =====

    def test_generate_error_report(self, error_handler):
        """エラーレポートが正しく生成される"""
        # 複数のエラーを記録
        error_handler.handle_error(Timeout("timeout"), "7203.T", {'retry_count': 0})
        error_handler.handle_error(ValueError("value error"), "7203.T", {'retry_count': 0})
        error_handler.handle_error(Timeout("timeout"), "6758.T", {'retry_count': 0})

        report = error_handler.generate_error_report()

        # サマリー確認
        assert report['summary']['total_errors'] == 3
        assert report['summary']['error_by_type']['temporary'] == 2
        assert report['summary']['error_by_type']['permanent'] == 1

        # トップエラー銘柄の確認
        assert len(report['top_error_stocks']) > 0
        top_stock = report['top_error_stocks'][0]
        assert top_stock['stock_code'] == "7203.T"
        assert top_stock['error_count'] == 2

        # 統計の確認
        assert report['statistics']['temporary_errors'] == 2
        assert report['statistics']['permanent_errors'] == 1

    def test_clear_error_records(self, error_handler):
        """エラー記録がクリアされる"""
        error_handler.handle_error(Timeout("timeout"), "7203.T", {'retry_count': 0})
        assert len(error_handler.error_records) == 1

        error_handler.clear_error_records()
        assert len(error_handler.error_records) == 0
        assert len(error_handler.error_stats) == 0

    # ===== 統合テスト =====

    def test_full_error_handling_workflow(self, error_handler):
        """エラーハンドリングの全体フローをテスト"""
        # シナリオ: 一時的エラーが2回発生し、3回目に成功
        errors = [Timeout("timeout 1"), Timeout("timeout 2")]

        for i, error in enumerate(errors):
            action = error_handler.handle_error(error, "7203.T", {'retry_count': i})
            assert action == ErrorAction.RETRY

        # エラー記録の確認
        assert len(error_handler.error_records) == 2

        # レポート生成
        report = error_handler.generate_error_report()
        assert report['summary']['total_errors'] == 2
        assert report['summary']['error_by_type']['temporary'] == 2


class TestErrorRecord:
    """ErrorRecordクラスのテスト"""

    def test_error_record_creation(self):
        """ErrorRecordが正しく作成される"""
        record = ErrorRecord(
            timestamp="2024-01-01T00:00:00",
            error_type="temporary",
            stock_code="7203.T",
            error_message="Test error",
            exception_class="TimeoutError",
            retry_count=1,
            action_taken="retry",
            context={'interval': '1d'}
        )

        assert record.timestamp == "2024-01-01T00:00:00"
        assert record.error_type == "temporary"
        assert record.stock_code == "7203.T"
        assert record.retry_count == 1
        assert record.action_taken == "retry"
        assert record.context['interval'] == '1d'
