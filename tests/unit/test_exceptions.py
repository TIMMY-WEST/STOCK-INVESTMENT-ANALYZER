"""例外クラスのテスト."""

import pytest

from app.exceptions import (  # 後方互換性のための例外クラス
    APIException,
    BaseStockAnalyzerException,
    BatchProcessingException,
    BatchServiceError,
    BulkDataServiceError,
    BusinessLogicException,
    DatabaseError,
    DatabaseException,
    ErrorCode,
    JPXStockServiceError,
    StockBatchProcessingError,
    StockDataConversionError,
    StockDataError,
    StockDataException,
    StockDataFetchError,
    StockDataOrchestrationError,
    StockDataSaveError,
    StockDataValidationError,
    SystemException,
    ValidationException,
)


class TestErrorCode:
    """ErrorCodeのテスト."""

    def test_error_code_values(self):
        """エラーコードの値が正しく設定されていることを確認."""
        assert ErrorCode.SYSTEM_ERROR.value == "SYS001"
        assert ErrorCode.DATABASE_CONNECTION.value == "DB001"
        assert ErrorCode.API_TIMEOUT.value == "API001"
        assert ErrorCode.STOCK_DATA_FETCH.value == "STK001"
        assert ErrorCode.BATCH_TIMEOUT.value == "BAT001"
        assert ErrorCode.VALIDATION_REQUIRED_FIELD.value == "VAL001"
        assert ErrorCode.BUSINESS_LOGIC_INVALID_OPERATION.value == "BIZ001"


class TestBaseStockAnalyzerException:
    """BaseStockAnalyzerExceptionのテスト."""

    def test_basic_creation(self):
        """基本的な例外作成のテスト."""
        error = BaseStockAnalyzerException(
            message="テストエラー", error_code=ErrorCode.SYSTEM_ERROR
        )
        assert str(error) == "テストエラー"
        assert error.error_code == ErrorCode.SYSTEM_ERROR
        assert error.details is None

    def test_creation_with_details(self):
        """詳細情報付きの例外作成のテスト."""
        details = {"stock_code": "1234", "retry_count": 3}
        error = BaseStockAnalyzerException(
            message="詳細付きエラー",
            error_code=ErrorCode.SYSTEM_ERROR,
            details=details,
        )
        assert str(error) == "詳細付きエラー"
        assert error.error_code == ErrorCode.SYSTEM_ERROR
        assert error.details == details

    def test_inheritance(self):
        """Exceptionクラスの継承を確認."""
        error = BaseStockAnalyzerException(
            message="継承テスト", error_code=ErrorCode.SYSTEM_ERROR
        )
        assert isinstance(error, Exception)


class TestSystemException:
    """SystemExceptionのテスト."""

    def test_creation(self):
        """SystemException作成のテスト."""
        error = SystemException("システムエラー")
        assert str(error) == "システムエラー"
        assert error.error_code == ErrorCode.SYSTEM_ERROR
        assert isinstance(error, BaseStockAnalyzerException)


class TestDatabaseException:
    """DatabaseExceptionのテスト."""

    def test_connection_error(self):
        """データベース接続エラーのテスト."""
        error = DatabaseException(
            message="接続エラー", error_code=ErrorCode.DATABASE_CONNECTION
        )
        assert str(error) == "接続エラー"
        assert error.error_code == ErrorCode.DATABASE_CONNECTION

    def test_timeout_error(self):
        """データベースタイムアウトエラーのテスト."""
        error = DatabaseException(
            message="タイムアウト", error_code=ErrorCode.DATABASE_TIMEOUT
        )
        assert str(error) == "タイムアウト"
        assert error.error_code == ErrorCode.DATABASE_TIMEOUT


class TestAPIException:
    """APIExceptionのテスト."""

    def test_timeout_error(self):
        """APIタイムアウトエラーのテスト."""
        error = APIException(
            message="APIタイムアウト", error_code=ErrorCode.API_TIMEOUT
        )
        assert str(error) == "APIタイムアウト"
        assert error.error_code == ErrorCode.API_TIMEOUT

    def test_rate_limit_error(self):
        """APIレート制限エラーのテスト."""
        error = APIException(
            message="レート制限", error_code=ErrorCode.API_RATE_LIMIT
        )
        assert str(error) == "レート制限"
        assert error.error_code == ErrorCode.API_RATE_LIMIT


class TestStockDataException:
    """StockDataExceptionのテスト."""

    def test_fetch_error(self):
        """株価データ取得エラーのテスト."""
        error = StockDataException(
            message="データ取得失敗", error_code=ErrorCode.STOCK_DATA_FETCH
        )
        assert str(error) == "データ取得失敗"
        assert error.error_code == ErrorCode.STOCK_DATA_FETCH

    def test_validation_error(self):
        """株価データバリデーションエラーのテスト."""
        error = StockDataException(
            message="データ検証失敗",
            error_code=ErrorCode.STOCK_DATA_VALIDATION,
        )
        assert str(error) == "データ検証失敗"
        assert error.error_code == ErrorCode.STOCK_DATA_VALIDATION


class TestBatchProcessingException:
    """BatchProcessingExceptionのテスト."""

    def test_timeout_error(self):
        """バッチ処理タイムアウトエラーのテスト."""
        error = BatchProcessingException(
            message="バッチタイムアウト", error_code=ErrorCode.BATCH_TIMEOUT
        )
        assert str(error) == "バッチタイムアウト"
        assert error.error_code == ErrorCode.BATCH_TIMEOUT

    def test_resource_error(self):
        """バッチ処理リソースエラーのテスト."""
        error = BatchProcessingException(
            message="リソース不足", error_code=ErrorCode.BATCH_RESOURCE
        )
        assert str(error) == "リソース不足"
        assert error.error_code == ErrorCode.BATCH_RESOURCE


class TestValidationException:
    """ValidationExceptionのテスト."""

    def test_required_field_error(self):
        """必須フィールドエラーのテスト."""
        error = ValidationException(
            message="必須フィールドが不足",
            error_code=ErrorCode.VALIDATION_REQUIRED_FIELD,
        )
        assert str(error) == "必須フィールドが不足"
        assert error.error_code == ErrorCode.VALIDATION_REQUIRED_FIELD

    def test_invalid_format_error(self):
        """無効フォーマットエラーのテスト."""
        error = ValidationException(
            message="フォーマットが無効",
            error_code=ErrorCode.VALIDATION_INVALID_FORMAT,
        )
        assert str(error) == "フォーマットが無効"
        assert error.error_code == ErrorCode.VALIDATION_INVALID_FORMAT


class TestBusinessLogicException:
    """BusinessLogicExceptionのテスト."""

    def test_invalid_operation_error(self):
        """無効操作エラーのテスト."""
        error = BusinessLogicException(
            message="無効な操作",
            error_code=ErrorCode.BUSINESS_LOGIC_INVALID_OPERATION,
        )
        assert str(error) == "無効な操作"
        assert error.error_code == ErrorCode.BUSINESS_LOGIC_INVALID_OPERATION


class TestBackwardCompatibility:
    """後方互換性のテスト."""

    def test_database_error_compatibility(self):
        """DatabaseErrorの後方互換性テスト."""
        error = DatabaseError("データベースエラー")
        assert str(error) == "データベースエラー"
        assert isinstance(error, DatabaseException)
        assert isinstance(error, BaseStockAnalyzerException)
        assert isinstance(error, Exception)

    def test_stock_data_error_compatibility(self):
        """StockDataErrorの後方互換性テスト."""
        error = StockDataError("株価データエラー")
        assert str(error) == "株価データエラー"
        assert isinstance(error, StockDataException)
        assert isinstance(error, BaseStockAnalyzerException)

    def test_stock_data_fetch_error_compatibility(self):
        """StockDataFetchErrorの後方互換性テスト."""
        error = StockDataFetchError("データ取得エラー")
        assert str(error) == "データ取得エラー"
        assert isinstance(error, StockDataException)
        assert error.error_code == ErrorCode.STOCK_DATA_FETCH

    def test_stock_data_save_error_compatibility(self):
        """StockDataSaveErrorの後方互換性テスト."""
        error = StockDataSaveError("データ保存エラー")
        assert str(error) == "データ保存エラー"
        assert isinstance(error, DatabaseException)
        assert error.error_code == ErrorCode.DATABASE_SAVE

    def test_batch_service_error_compatibility(self):
        """BatchServiceErrorの後方互換性テスト."""
        error = BatchServiceError("バッチサービスエラー")
        assert str(error) == "バッチサービスエラー"
        assert isinstance(error, BatchProcessingException)
        assert error.error_code == ErrorCode.BATCH_PROCESSING

    def test_validation_error_compatibility(self):
        """StockDataValidationErrorの後方互換性テスト."""
        error = StockDataValidationError("バリデーションエラー")
        assert str(error) == "バリデーションエラー"
        assert isinstance(error, ValidationException)
        assert error.error_code == ErrorCode.VALIDATION_INVALID_FORMAT


class TestExceptionDetails:
    """例外詳細情報のテスト."""

    def test_exception_with_stock_code_details(self):
        """銘柄コード付き例外のテスト."""
        details = {"stock_code": "1234", "market": "TSE"}
        error = StockDataException(
            message="銘柄データエラー",
            error_code=ErrorCode.STOCK_DATA_FETCH,
            details=details,
        )
        assert error.details["stock_code"] == "1234"
        assert error.details["market"] == "TSE"

    def test_exception_with_retry_details(self):
        """リトライ情報付き例外のテスト."""
        details = {"retry_count": 3, "max_retries": 5}
        error = APIException(
            message="API呼び出し失敗",
            error_code=ErrorCode.API_TIMEOUT,
            details=details,
        )
        assert error.details["retry_count"] == 3
        assert error.details["max_retries"] == 5

    def test_exception_with_complex_details(self):
        """複雑な詳細情報付き例外のテスト."""
        details = {
            "operation": "bulk_insert",
            "affected_records": 1000,
            "failed_records": 50,
            "error_records": [
                {"id": 1, "reason": "duplicate"},
                {"id": 2, "reason": "invalid_format"},
            ],
        }
        error = BatchProcessingException(
            message="バッチ処理部分失敗",
            error_code=ErrorCode.BATCH_PROCESSING,
            details=details,
        )
        assert error.details["operation"] == "bulk_insert"
        assert error.details["affected_records"] == 1000
        assert len(error.details["error_records"]) == 2
