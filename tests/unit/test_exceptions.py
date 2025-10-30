"""exceptions.pyのテストケース.

このモジュールは、exceptions.pyで定義された例外クラスの包括的なテストを提供します。
"""

import pytest

from app.exceptions import (
    APIException,
    BatchServiceError,
    BulkDataServiceError,
    DatabaseError,
    ErrorCode,
    JPXStockServiceError,
    StockBatchProcessingError,
    StockDataError,
    StockDataOrchestrationError,
    StockDataValidationError,
    ValidationException,
)


class TestErrorCode:
    """ErrorCodeクラスのテスト."""

    def test_error_code_values_with_enum_returns_correct_codes(self):
        """ErrorCodeの値が正しく設定されていることのテスト."""
        # Arrange (準備)
        # テストデータの準備は不要（Enumを直接使用）

        # Act (実行)
        # 実行処理は不要（値の検証のみ）

        # Assert (検証)
        assert ErrorCode.SYSTEM_ERROR.value == "SYS001"
        assert ErrorCode.DATABASE_CONNECTION.value == "DB001"
        assert ErrorCode.API_TIMEOUT.value == "API001"
        assert ErrorCode.VALIDATION_REQUIRED_FIELD.value == "VAL001"

    def test_error_code_string_representation_with_enum_returns_formatted_string(
        self,
    ):
        """ErrorCodeの文字列表現のテスト."""
        # Arrange (準備)
        # テストデータの準備は不要（Enumを直接使用）

        # Act (実行)
        # 実行処理は不要（文字列表現の検証のみ）

        # Assert (検証)
        assert str(ErrorCode.SYSTEM_ERROR) == "ErrorCode.SYSTEM_ERROR"
        assert (
            repr(ErrorCode.DATABASE_CONNECTION)
            == "<ErrorCode.DATABASE_CONNECTION: 'DB001'>"
        )

    def test_error_code_comparison_with_same_values_returns_equal(self):
        """ErrorCodeの比較のテスト."""
        # Arrange (準備)
        # テストデータの準備は不要（Enumを直接使用）

        # Act (実行)
        # 実行処理は不要（比較演算の検証のみ）

        # Assert (検証)
        assert ErrorCode.SYSTEM_ERROR == ErrorCode.SYSTEM_ERROR
        assert ErrorCode.DATABASE_CONNECTION != ErrorCode.API_TIMEOUT


class TestStockDataError:
    """StockDataErrorクラスのテスト."""

    def test_exception_creation_with_basic_params_returns_valid_instance(self):
        """基本的な例外作成のテスト."""
        # Arrange (準備)
        message = "データエラー"
        error_code = ErrorCode.STOCK_DATA_FETCH

        # Act (実行)
        error = StockDataError(message, error_code)

        # Assert (検証)
        assert str(error) == "データエラー"
        assert error.error_code == ErrorCode.STOCK_DATA_FETCH

    def test_exception_creation_with_custom_error_code_returns_valid_instance(
        self,
    ):
        """カスタムエラーコード付きの例外作成のテスト."""
        # Arrange (準備)
        message = "カスタムエラー"

        # Act (実行)
        error = StockDataError(message)

        # Assert (検証)
        assert str(error) == "カスタムエラー"
        assert error.error_code == ErrorCode.STOCK_DATA_FETCH

    def test_exception_creation_with_details_returns_valid_instance(self):
        """詳細情報付きの例外作成のテスト."""
        # Arrange (準備)
        message = "詳細エラー"
        details = {"symbol": "7203", "market": "TSE"}

        # Act (実行)
        error = StockDataError(message, details)

        # Assert (検証)
        assert str(error) == "詳細エラー"
        assert error.error_code == ErrorCode.STOCK_DATA_FETCH
        assert error.details == details

    def test_exception_inheritance_with_base_exception_returns_valid_hierarchy(
        self,
    ):
        """継承関係のテスト."""
        # Arrange (準備)
        message = "テスト"

        # Act (実行)
        error = StockDataError(message)

        # Assert (検証)
        assert isinstance(error, Exception)


class TestDatabaseError:
    """DatabaseErrorクラスのテスト."""

    def test_exception_creation_with_basic_params_returns_valid_instance(self):
        """基本的な例外作成のテスト."""
        # Arrange (準備)
        message = "データベースエラー"
        error_code = ErrorCode.DATABASE_CONNECTION

        # Act (実行)
        error = DatabaseError(message, error_code)

        # Assert (検証)
        assert str(error) == "データベースエラー"
        assert error.error_code == ErrorCode.DATABASE_CONNECTION

    def test_exception_creation_with_custom_error_code_returns_valid_instance(
        self,
    ):
        """カスタムエラーコード付きの例外作成のテスト."""
        # Arrange (準備)
        message = "カスタムエラー"

        # Act (実行)
        error = DatabaseError(message)

        # Assert (検証)
        assert str(error) == "カスタムエラー"
        assert error.error_code == ErrorCode.DATABASE_CONNECTION


class TestAPIException:
    """APIExceptionクラスのテスト."""

    def test_exception_creation_with_basic_params_returns_valid_instance(self):
        """基本的な例外作成のテスト."""
        # Arrange (準備)
        message = "API エラー"
        error_code = ErrorCode.API_TIMEOUT

        # Act (実行)
        error = APIException(message, error_code)

        # Assert (検証)
        assert str(error) == "API エラー"
        assert error.error_code == ErrorCode.API_TIMEOUT

    def test_exception_creation_with_status_code_returns_valid_instance(self):
        """ステータスコード付きの例外作成のテスト."""
        # Arrange (準備)
        message = "API エラー"
        error_code = ErrorCode.API_CONNECTION
        details = {"status_code": 404}

        # Act (実行)
        error = APIException(message, error_code, details=details)

        # Assert (検証)
        assert str(error) == "API エラー"
        assert error.details["status_code"] == 404


class TestValidationException:
    """ValidationExceptionクラスのテスト."""

    def test_exception_creation_with_basic_params_returns_valid_instance(self):
        """基本的な例外作成のテスト."""
        # Arrange (準備)
        message = "バリデーションエラー"
        error_code = ErrorCode.VALIDATION_INVALID_FORMAT

        # Act (実行)
        error = ValidationException(message, error_code)

        # Assert (検証)
        assert str(error) == "バリデーションエラー"
        assert error.error_code == ErrorCode.VALIDATION_INVALID_FORMAT

    def test_exception_creation_with_field_details_returns_valid_instance(
        self,
    ):
        """フィールド詳細付きの例外作成のテスト."""
        # Arrange (準備)
        message = "無効な値"
        error_code = ErrorCode.VALIDATION_INVALID_FORMAT
        details = {"field": "symbol", "value": "invalid"}

        # Act (実行)
        error = ValidationException(message, error_code, details=details)

        # Assert (検証)
        assert str(error) == "無効な値"
        assert error.details == details


class TestStockDataValidationError:
    """StockDataValidationErrorクラスのテスト."""

    def test_exception_creation_with_basic_params_returns_valid_instance(self):
        """基本的な例外作成のテスト."""
        # Arrange (準備)
        message = "株式データ検証エラー"
        error_code = ErrorCode.VALIDATION_INVALID_FORMAT

        # Act (実行)
        error = StockDataValidationError(message, error_code)

        # Assert (検証)
        assert str(error) == "株式データ検証エラー"
        assert error.error_code == ErrorCode.VALIDATION_INVALID_FORMAT

    def test_exception_creation_with_validation_details_returns_valid_instance(
        self,
    ):
        """バリデーション詳細付きの例外作成のテスト."""
        # Arrange (準備)
        message = "価格は正の値である必要があります"
        validation_details = {
            "field": "price",
            "value": -100,
            "constraint": "positive",
        }

        # Act (実行)
        error = StockDataValidationError(message, details=validation_details)

        # Assert (検証)
        assert str(error) == "価格は正の値である必要があります"
        assert error.details == validation_details


class TestBatchServiceError:
    """BatchServiceErrorクラスのテスト."""

    def test_exception_creation_with_basic_params_returns_valid_instance(self):
        """基本的な例外作成のテスト."""
        # Arrange (準備)
        message = "バッチ処理エラー"
        error_code = ErrorCode.BATCH_PROCESSING

        # Act (実行)
        error = BatchServiceError(message, error_code)

        # Assert (検証)
        assert str(error) == "バッチ処理エラー"
        assert error.error_code == ErrorCode.BATCH_PROCESSING


class TestJPXStockServiceError:
    """JPXStockServiceErrorクラスのテスト."""

    def test_exception_creation_with_basic_params_returns_valid_instance(self):
        """基本的な例外作成のテスト."""
        # Arrange (準備)
        message = "JPX サービスエラー"
        error_code = ErrorCode.API_CONNECTION

        # Act (実行)
        error = JPXStockServiceError(message, error_code)

        # Assert (検証)
        assert str(error) == "JPX サービスエラー"
        assert error.error_code == ErrorCode.API_CONNECTION


class TestExceptionHierarchy:
    """例外クラスの継承関係テスト."""

    def test_all_exceptions_inherit_from_exception_with_base_class_returns_valid_hierarchy(
        self,
    ):
        """全ての例外クラスがExceptionを継承していることのテスト."""
        # Arrange (準備)
        exception_classes = [
            StockDataError,
            DatabaseError,
            StockDataValidationError,
            BatchServiceError,
            JPXStockServiceError,
        ]

        # Act (実行)
        # 実行処理は不要（継承関係の検証のみ）

        # Assert (検証)
        for exception_class in exception_classes:
            assert issubclass(exception_class, Exception)

    def test_exception_instantiation_with_all_classes_returns_valid_instances(
        self,
    ):
        """全ての例外クラスがインスタンス化可能であることのテスト."""
        # Arrange (準備)
        basic_exception_classes = [
            StockDataError,
            DatabaseError,
        ]
        error_code_exception_classes = [
            (BatchServiceError, ErrorCode.BATCH_PROCESSING),
            (JPXStockServiceError, ErrorCode.API_CONNECTION),
        ]
        test_message = "テストメッセージ"
        validation_message = "バリデーションエラー"

        # Act (実行)
        # 基本的な例外クラスのテスト
        for exception_class in basic_exception_classes:
            error = exception_class(test_message)
            assert isinstance(error, Exception)
            assert str(error) == "テストメッセージ"

        # エラーコードが必要な例外クラスのテスト
        for exception_class, error_code in error_code_exception_classes:
            error = exception_class(test_message, error_code)
            assert isinstance(error, Exception)
            assert str(error) == "テストメッセージ"

        # StockDataValidationErrorは特別な処理が必要
        validation_error = StockDataValidationError(validation_message)

        # Assert (検証)
        assert isinstance(validation_error, Exception)
        assert (
            validation_error.error_code == ErrorCode.VALIDATION_INVALID_FORMAT
        )
