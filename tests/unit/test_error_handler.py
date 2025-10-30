"""ErrorHandlerクラスのテスト."""

from unittest.mock import Mock, patch

import pytest
from requests.exceptions import ConnectionError, HTTPError, Timeout

from app.exceptions import (
    APIException,
    BaseStockAnalyzerException,
    BatchProcessingException,
    BusinessLogicException,
    DatabaseException,
    ErrorCode,
    StockDataException,
    SystemException,
    ValidationException,
)
from app.services.common.error_handler import (
    ErrorAction,
    ErrorHandler,
    ErrorRecord,
    ErrorType,
)


class TestErrorHandler:
    """ErrorHandlerクラスのテストケース."""

    @pytest.fixture
    def error_handler(self):
        """ErrorHandlerインスタンスを作成."""
        return ErrorHandler(max_retries=3, retry_delay=1, backoff_multiplier=2)

    # ===== エラー分類テスト =====

    def test_classify_timeout_error_with_timeout_exception_returns_temporary(
        self, error_handler
    ):
        """タイムアウトエラーを一時的エラーとして分類."""
        error = Timeout("Request timed out")
        error_type = error_handler.classify_error(error)
        assert error_type == ErrorType.TEMPORARY

    def test_classify_connection_error_with_connection_exception_returns_temporary(
        self, error_handler
    ):
        """接続エラーを一時的エラーとして分類."""
        error = ConnectionError("Failed to connect")
        error_type = error_handler.classify_error(error)
        assert error_type == ErrorType.TEMPORARY

    def test_classify_429_with_rate_limit_returns_temporary(
        self, error_handler
    ):
        """429エラー（Rate Limit）を一時的エラーとして分類."""
        # HTTPErrorのモック作成
        response_mock = Mock()
        response_mock.status_code = 429
        error = HTTPError()
        error.response = response_mock

        error_type = error_handler.classify_error(error)
        assert error_type == ErrorType.TEMPORARY

    def test_classify_503_with_service_unavailable_returns_temporary(
        self, error_handler
    ):
        """503エラー（Service Unavailable）を一時的エラーとして分類."""
        response_mock = Mock()
        response_mock.status_code = 503
        error = HTTPError()
        error.response = response_mock

        error_type = error_handler.classify_error(error)
        assert error_type == ErrorType.TEMPORARY

    def test_classify_404_with_not_found_returns_permanent(
        self, error_handler
    ):
        """404エラーを永続的エラーとして分類."""
        response_mock = Mock()
        response_mock.status_code = 404
        error = HTTPError()
        error.response = response_mock

        error_type = error_handler.classify_error(error)
        assert error_type == ErrorType.PERMANENT

    def test_classify_value_error_as_permanent(self, error_handler):
        """ValueErrorを永続的エラーとして分類."""
        error = ValueError("Invalid data format")
        error_type = error_handler.classify_error(error)
        assert error_type == ErrorType.PERMANENT

    # ===== エラー処理テスト =====

    def test_handle_temporary_error_returns_retry(self, error_handler):
        """一時的エラーの場合、RETRYアクションを返す."""
        error = Timeout("Request timed out")
        action = error_handler.handle_error(
            error, "7203.T", {"retry_count": 0}
        )
        assert action == ErrorAction.RETRY

    def test_handle_temporary_error_max_retries_returns_skip(
        self, error_handler
    ):
        """最大リトライ回数到達時、SKIPアクションを返す."""
        error = Timeout("Request timed out")
        action = error_handler.handle_error(
            error, "7203.T", {"retry_count": 3}
        )
        assert action == ErrorAction.SKIP

    def test_handle_permanent_error_returns_skip(self, error_handler):
        """永続的エラーの場合、SKIPアクションを返す."""
        error = ValueError("Invalid data")
        action = error_handler.handle_error(
            error, "7203.T", {"retry_count": 0}
        )
        assert action == ErrorAction.SKIP

    # ===== リトライバックオフテスト =====

    @patch("time.sleep")
    def test_retry_with_backoff_delays_correctly(
        self, mock_sleep, error_handler
    ):
        """指数バックオフで正しい待機時間を計算."""
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
        """エラー記録が保存される."""
        error = ValueError("Test error")
        error_handler.handle_error(error, "7203.T", {"retry_count": 0})

        assert len(error_handler.error_records) == 1
        record = error_handler.error_records[0]
        assert record.stock_code == "7203.T"
        assert record.error_type == "permanent"
        assert record.exception_class == "ValueError"

    def test_error_statistics_are_updated(self, error_handler):
        """エラー統計が更新される."""
        error_handler.handle_error(
            Timeout("timeout"), "7203.T", {"retry_count": 0}
        )
        error_handler.handle_error(
            ValueError("value error"), "6758.T", {"retry_count": 0}
        )

        stats = error_handler.get_error_statistics()
        assert stats["total_errors"] == 2
        assert stats["error_stats"]["temporary"] == 1
        assert stats["error_stats"]["permanent"] == 1

    # ===== エラーレポート生成テスト =====

    def test_generate_error_report(self, error_handler):
        """エラーレポートが正しく生成される."""
        # 複数のエラーを記録
        error_handler.handle_error(
            Timeout("timeout"), "7203.T", {"retry_count": 0}
        )
        error_handler.handle_error(
            ValueError("value error"), "7203.T", {"retry_count": 0}
        )
        error_handler.handle_error(
            Timeout("timeout"), "6758.T", {"retry_count": 0}
        )

        report = error_handler.generate_error_report()

        # サマリー確認
        assert report["summary"]["total_errors"] == 3
        assert report["summary"]["error_by_type"]["temporary"] == 2
        assert report["summary"]["error_by_type"]["permanent"] == 1

        # トップエラー銘柄の確認
        assert len(report["top_error_stocks"]) > 0
        top_stock = report["top_error_stocks"][0]
        assert top_stock["stock_code"] == "7203.T"
        assert top_stock["error_count"] == 2

        # 統計の確認
        assert report["statistics"]["temporary_errors"] == 2
        assert report["statistics"]["permanent_errors"] == 1

    def test_error_handler_clear_error_records_with_existing_records_returns_empty_state(
        self, error_handler
    ):
        """エラー記録がクリアされる."""
        error_handler.handle_error(
            Timeout("timeout"), "7203.T", {"retry_count": 0}
        )
        assert len(error_handler.error_records) == 1

        error_handler.clear_error_records()
        assert len(error_handler.error_records) == 0
        assert len(error_handler.error_stats) == 0

    # ===== 統合テスト =====

    def test_full_error_handling_workflow(self, error_handler):
        """エラーハンドリングの全体フローをテスト."""
        # シナリオ: 一時的エラーが2回発生し、3回目に成功
        errors = [Timeout("timeout 1"), Timeout("timeout 2")]

        for i, error in enumerate(errors):
            action = error_handler.handle_error(
                error, "7203.T", {"retry_count": i}
            )
            assert action == ErrorAction.RETRY

        # エラー記録の確認
        assert len(error_handler.error_records) == 2

        # レポート生成
        report = error_handler.generate_error_report()
        assert report["summary"]["total_errors"] == 2
        assert report["summary"]["error_by_type"]["temporary"] == 2


class TestErrorRecord:
    """ErrorRecordクラスのテスト."""

    def test_error_record_creation(self):
        """ErrorRecordが正しく作成される."""
        record = ErrorRecord(
            timestamp="2024-01-01T00:00:00",
            error_type="temporary",
            stock_code="7203.T",
            error_message="Test error",
            exception_class="TimeoutError",
            retry_count=1,
            action_taken="retry",
            context={"interval": "1d"},
        )

        assert record.timestamp == "2024-01-01T00:00:00"
        assert record.error_type == "temporary"
        assert record.stock_code == "7203.T"
        assert record.error_message == "Test error"
        assert record.exception_class == "TimeoutError"
        assert record.retry_count == 1
        assert record.action_taken == "retry"
        assert record.context["interval"] == "1d"


class TestCustomExceptionIntegration:
    """カスタム例外クラスとエラーハンドラーの統合テスト."""

    @pytest.fixture
    def error_handler(self):
        """ErrorHandlerインスタンスを作成."""
        return ErrorHandler(max_retries=3, retry_delay=1, backoff_multiplier=2)

    # ===== システム例外の分類テスト =====

    def test_classify_system_exception_as_system(self, error_handler):
        """SystemExceptionをシステムエラーとして分類."""
        error = SystemException("システムエラー")
        error_type = error_handler.classify_error(error)
        assert error_type == ErrorType.SYSTEM

    # ===== データベース例外の分類テスト =====

    def test_classify_database_connection_error_as_temporary(
        self, error_handler
    ):
        """データベース接続エラーを一時的エラーとして分類."""
        error = DatabaseException(
            message="接続エラー", error_code=ErrorCode.DATABASE_CONNECTION
        )
        error_type = error_handler.classify_error(error)
        assert error_type == ErrorType.TEMPORARY

    def test_classify_database_timeout_error_as_temporary(self, error_handler):
        """データベースタイムアウトエラーを一時的エラーとして分類."""
        error = DatabaseException(
            message="タイムアウト", error_code=ErrorCode.DATABASE_TIMEOUT
        )
        error_type = error_handler.classify_error(error)
        assert error_type == ErrorType.TEMPORARY

    def test_classify_database_save_error_as_permanent(self, error_handler):
        """データベース保存エラーを永続的エラーとして分類."""
        error = DatabaseException(
            message="保存エラー", error_code=ErrorCode.DATABASE_SAVE
        )
        error_type = error_handler.classify_error(error)
        assert error_type == ErrorType.PERMANENT

    # ===== API例外の分類テスト =====

    def test_classify_api_timeout_error_as_temporary(self, error_handler):
        """APIタイムアウトエラーを一時的エラーとして分類."""
        error = APIException(
            message="APIタイムアウト", error_code=ErrorCode.API_TIMEOUT
        )
        error_type = error_handler.classify_error(error)
        assert error_type == ErrorType.TEMPORARY

    def test_classify_api_rate_limit_error_as_temporary(self, error_handler):
        """APIレート制限エラーを一時的エラーとして分類."""
        error = APIException(
            message="レート制限", error_code=ErrorCode.API_RATE_LIMIT
        )
        error_type = error_handler.classify_error(error)
        assert error_type == ErrorType.TEMPORARY

    def test_classify_api_authentication_error_as_permanent(
        self, error_handler
    ):
        """API認証エラーを永続的エラーとして分類."""
        error = APIException(
            message="認証エラー", error_code=ErrorCode.API_AUTHENTICATION
        )
        error_type = error_handler.classify_error(error)
        assert error_type == ErrorType.PERMANENT

    # ===== 株価データ例外の分類テスト =====

    def test_classify_stock_data_fetch_error_as_temporary(self, error_handler):
        """株価データ取得エラーを一時的エラーとして分類."""
        error = StockDataException(
            message="データ取得失敗", error_code=ErrorCode.STOCK_DATA_FETCH
        )
        error_type = error_handler.classify_error(error)
        assert error_type == ErrorType.TEMPORARY

    def test_classify_stock_data_validation_error_as_permanent(
        self, error_handler
    ):
        """株価データバリデーションエラーを永続的エラーとして分類."""
        error = StockDataException(
            message="データ検証失敗",
            error_code=ErrorCode.STOCK_DATA_VALIDATION,
        )
        error_type = error_handler.classify_error(error)
        assert error_type == ErrorType.PERMANENT

    # ===== バッチ処理例外の分類テスト =====

    def test_classify_batch_timeout_error_as_temporary(self, error_handler):
        """バッチ処理タイムアウトエラーを一時的エラーとして分類."""
        error = BatchProcessingException(
            message="バッチタイムアウト", error_code=ErrorCode.BATCH_TIMEOUT
        )
        error_type = error_handler.classify_error(error)
        assert error_type == ErrorType.TEMPORARY

    def test_classify_batch_resource_error_as_temporary(self, error_handler):
        """バッチ処理リソースエラーを一時的エラーとして分類."""
        error = BatchProcessingException(
            message="リソース不足", error_code=ErrorCode.BATCH_RESOURCE
        )
        error_type = error_handler.classify_error(error)
        assert error_type == ErrorType.TEMPORARY

    def test_classify_batch_processing_error_as_permanent(self, error_handler):
        """バッチ処理エラーを永続的エラーとして分類."""
        error = BatchProcessingException(
            message="処理エラー", error_code=ErrorCode.BATCH_PROCESSING
        )
        error_type = error_handler.classify_error(error)
        assert error_type == ErrorType.PERMANENT

    # ===== バリデーション例外の分類テスト =====

    def test_classify_validation_error_as_permanent(self, error_handler):
        """バリデーションエラーを永続的エラーとして分類."""
        error = ValidationException(
            message="バリデーションエラー",
            error_code=ErrorCode.VALIDATION_REQUIRED_FIELD,
        )
        error_type = error_handler.classify_error(error)
        assert error_type == ErrorType.PERMANENT

    # ===== ビジネスロジック例外の分類テスト =====

    def test_classify_business_logic_error_as_permanent(self, error_handler):
        """ビジネスロジックエラーを永続的エラーとして分類."""
        error = BusinessLogicException(
            message="ビジネスロジックエラー",
            error_code=ErrorCode.BUSINESS_LOGIC_INVALID_OPERATION,
        )
        error_type = error_handler.classify_error(error)
        assert error_type == ErrorType.PERMANENT

    # ===== エラー記録の詳細情報テスト =====

    def test_custom_exception_error_record_includes_error_code(
        self, error_handler
    ):
        """カスタム例外のエラー記録にエラーコードが含まれる."""
        error = StockDataException(
            message="データ取得失敗", error_code=ErrorCode.STOCK_DATA_FETCH
        )

        error_handler.handle_error(error, "7203.T")

        # エラー記録を確認
        assert len(error_handler.error_records) == 1
        record = error_handler.error_records[0]
        assert record.error_code == ErrorCode.STOCK_DATA_FETCH.value
        assert record.details is None

    def test_custom_exception_error_record_includes_details(
        self, error_handler
    ):
        """カスタム例外のエラー記録に詳細情報が含まれる."""
        details = {"stock_code": "7203.T", "retry_count": 2}
        error = APIException(
            message="APIエラー",
            error_code=ErrorCode.API_TIMEOUT,
            details=details,
        )

        error_handler.handle_error(error, "7203.T")

        # エラー記録を確認
        assert len(error_handler.error_records) == 1
        record = error_handler.error_records[0]
        assert record.error_code == ErrorCode.API_TIMEOUT.value
        assert record.details == details

    # ===== 統合ワークフローテスト =====

    def test_custom_exception_full_workflow(self, error_handler):
        """カスタム例外の完全なワークフローテスト."""
        # 一時的エラー（リトライ対象）
        temp_error = APIException(
            message="APIタイムアウト",
            error_code=ErrorCode.API_TIMEOUT,
            details={"endpoint": "/api/stocks", "timeout": 30},
        )

        # 永続的エラー（スキップ対象）
        perm_error = ValidationException(
            message="必須フィールド不足",
            error_code=ErrorCode.VALIDATION_REQUIRED_FIELD,
            details={"missing_fields": ["stock_code", "date"]},
        )

        # 一時的エラーの処理
        action1 = error_handler.handle_error(temp_error, "7203.T")
        assert action1 == ErrorAction.RETRY

        # 永続的エラーの処理
        action2 = error_handler.handle_error(perm_error, "9984.T")
        assert action2 == ErrorAction.SKIP

        # エラー記録の確認
        assert len(error_handler.error_records) == 2

        # 統計の確認
        stats = error_handler.get_error_statistics()
        assert stats["temporary"] == 1
        assert stats["permanent"] == 1

        # レポート生成
        report = error_handler.generate_error_report()
        assert report["summary"]["total_errors"] == 2
        assert report["summary"]["error_by_type"]["temporary"] == 1
        assert report["summary"]["error_by_type"]["permanent"] == 1

        # エラーコードが記録されていることを確認
        temp_record = next(
            r for r in error_handler.error_records if r.stock_code == "7203.T"
        )
        perm_record = next(
            r for r in error_handler.error_records if r.stock_code == "9984.T"
        )

        assert temp_record.error_code == ErrorCode.API_TIMEOUT.value
        assert temp_record.details["endpoint"] == "/api/stocks"

        assert (
            perm_record.error_code == ErrorCode.VALIDATION_REQUIRED_FIELD.value
        )
        assert "stock_code" in perm_record.details["missing_fields"]
