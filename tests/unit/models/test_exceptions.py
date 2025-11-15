"""app.models.exceptions モジュールのユニットテスト.

このテストモジュールでは、データアクセス層のカスタム例外クラスが
正しく動作することを検証します。
"""

from __future__ import annotations

import pytest

from app.models.exceptions import (
    BaseModelException,
    CRUDOperationError,
    DatabaseError,
    ModelNotFoundError,
    ValidationError,
)


class TestBaseModelException:
    """BaseModelException クラスのテスト."""

    def test_basic_initialization(self) -> None:
        """基本的な初期化のテスト."""
        exc = BaseModelException("Test error")
        assert exc.message == "Test error"
        assert exc.context == {}

    def test_initialization_with_context(self) -> None:
        """コンテキスト付き初期化のテスト."""
        context = {"key1": "value1", "key2": 42}
        exc = BaseModelException("Test error", context=context)
        assert exc.message == "Test error"
        assert exc.context == context

    def test_str_representation_without_context(self) -> None:
        """コンテキストなしの文字列表現のテスト."""
        exc = BaseModelException("Test error")
        assert str(exc) == "Test error"

    def test_str_representation_with_context(self) -> None:
        """コンテキスト付き文字列表現のテスト."""
        context = {"symbol": "7203.T", "date": "2025-01-01"}
        exc = BaseModelException("Test error", context=context)
        exc_str = str(exc)
        assert "Test error" in exc_str
        assert "context:" in exc_str
        assert "symbol=7203.T" in exc_str
        assert "date=2025-01-01" in exc_str

    def test_repr_representation(self) -> None:
        """repr表現のテスト."""
        context = {"key": "value"}
        exc = BaseModelException("Test error", context=context)
        repr_str = repr(exc)
        assert "BaseModelException" in repr_str
        assert "message='Test error'" in repr_str
        assert "context={'key': 'value'}" in repr_str

    def test_can_be_raised(self) -> None:
        """例外として送出できることのテスト."""
        with pytest.raises(BaseModelException) as exc_info:
            raise BaseModelException("Test error")
        assert exc_info.value.message == "Test error"


class TestDatabaseError:
    """DatabaseError クラスのテスト."""

    def test_inherits_from_base_model_exception(self) -> None:
        """BaseModelException を継承していることのテスト."""
        exc = DatabaseError("DB error")
        assert isinstance(exc, BaseModelException)
        assert isinstance(exc, DatabaseError)

    def test_basic_initialization(self) -> None:
        """基本的な初期化のテスト."""
        exc = DatabaseError("Connection failed")
        assert exc.message == "Connection failed"
        assert exc.context == {}

    def test_initialization_with_context(self) -> None:
        """コンテキスト付き初期化のテスト."""
        context = {"error": "Timeout", "retry_count": 3}
        exc = DatabaseError("Connection failed", context=context)
        assert exc.message == "Connection failed"
        assert exc.context == context

    def test_can_be_caught_as_base_exception(self) -> None:
        """BaseModelException としてキャッチできることのテスト."""
        with pytest.raises(BaseModelException):
            raise DatabaseError("Test error")


class TestCRUDOperationError:
    """CRUDOperationError クラスのテスト."""

    def test_inherits_from_database_error(self) -> None:
        """DatabaseError を継承していることのテスト."""
        exc = CRUDOperationError("CRUD failed")
        assert isinstance(exc, DatabaseError)
        assert isinstance(exc, BaseModelException)

    def test_basic_initialization(self) -> None:
        """基本的な初期化のテスト."""
        exc = CRUDOperationError("Create failed")
        assert exc.message == "Create failed"
        assert exc.context == {}

    def test_initialization_with_operation(self) -> None:
        """operation 引数付き初期化のテスト."""
        exc = CRUDOperationError("Create failed", operation="create")
        assert exc.message == "Create failed"
        assert exc.context["operation"] == "create"

    def test_initialization_with_model_name(self) -> None:
        """model_name 引数付き初期化のテスト."""
        exc = CRUDOperationError("Create failed", model_name="Stocks1d")
        assert exc.message == "Create failed"
        assert exc.context["model_name"] == "Stocks1d"

    def test_initialization_with_all_parameters(self) -> None:
        """すべてのパラメータを指定した初期化のテスト."""
        context = {"symbol": "7203.T", "error": "Duplicate key"}
        exc = CRUDOperationError(
            "Create failed",
            operation="create",
            model_name="Stocks1d",
            context=context,
        )
        assert exc.message == "Create failed"
        assert exc.context["operation"] == "create"
        assert exc.context["model_name"] == "Stocks1d"
        assert exc.context["symbol"] == "7203.T"
        assert exc.context["error"] == "Duplicate key"

    def test_str_representation(self) -> None:
        """文字列表現のテスト."""
        exc = CRUDOperationError(
            "Update failed",
            operation="update",
            model_name="StockMaster",
        )
        exc_str = str(exc)
        assert "Update failed" in exc_str
        assert "operation=update" in exc_str
        assert "model_name=StockMaster" in exc_str


class TestModelNotFoundError:
    """ModelNotFoundError クラスのテスト."""

    def test_inherits_from_base_model_exception(self) -> None:
        """BaseModelException を継承していることのテスト."""
        exc = ModelNotFoundError("TestModel")
        assert isinstance(exc, BaseModelException)
        assert not isinstance(exc, DatabaseError)

    def test_basic_initialization(self) -> None:
        """基本的な初期化のテスト."""
        exc = ModelNotFoundError("Stocks1d")
        assert exc.message == "Stocks1d not found"
        assert exc.context == {}

    def test_initialization_with_search_criteria(self) -> None:
        """検索条件付き初期化のテスト."""
        exc = ModelNotFoundError(
            "Stocks1d",
            symbol="7203.T",
            date="2025-01-01",
        )
        assert exc.message == "Stocks1d not found"
        assert exc.context["symbol"] == "7203.T"
        assert exc.context["date"] == "2025-01-01"

    def test_initialization_with_multiple_criteria(self) -> None:
        """複数の検索条件での初期化のテスト."""
        exc = ModelNotFoundError(
            "StockMaster",
            stock_code="7203",
            is_active=True,
            market_category="プライム",
        )
        assert exc.context["stock_code"] == "7203"
        assert exc.context["is_active"] is True
        assert exc.context["market_category"] == "プライム"

    def test_str_representation(self) -> None:
        """文字列表現のテスト."""
        exc = ModelNotFoundError("Stocks1d", symbol="7203.T")
        exc_str = str(exc)
        assert "Stocks1d not found" in exc_str
        assert "symbol=7203.T" in exc_str


class TestValidationError:
    """ValidationError クラスのテスト."""

    def test_inherits_from_base_model_exception(self) -> None:
        """BaseModelException を継承していることのテスト."""
        exc = ValidationError("Invalid value")
        assert isinstance(exc, BaseModelException)
        assert not isinstance(exc, DatabaseError)

    def test_basic_initialization(self) -> None:
        """基本的な初期化のテスト."""
        exc = ValidationError("Price must be positive")
        assert exc.message == "Price must be positive"
        assert exc.context == {}

    def test_initialization_with_field_name(self) -> None:
        """field_name 引数付き初期化のテスト."""
        exc = ValidationError(
            "Price must be positive",
            field_name="close",
        )
        assert exc.message == "Price must be positive"
        assert exc.context["field_name"] == "close"

    def test_initialization_with_invalid_value(self) -> None:
        """invalid_value 引数付き初期化のテスト."""
        exc = ValidationError(
            "Price must be positive",
            invalid_value=-100,
        )
        assert exc.message == "Price must be positive"
        assert exc.context["invalid_value"] == -100

    def test_initialization_with_all_parameters(self) -> None:
        """すべてのパラメータを指定した初期化のテスト."""
        context = {"constraint": "CHECK (close >= 0)"}
        exc = ValidationError(
            "Price must be positive",
            field_name="close",
            invalid_value=-100,
            context=context,
        )
        assert exc.message == "Price must be positive"
        assert exc.context["field_name"] == "close"
        assert exc.context["invalid_value"] == -100
        assert exc.context["constraint"] == "CHECK (close >= 0)"

    def test_initialization_with_zero_value(self) -> None:
        """invalid_value が 0 の場合のテスト."""
        exc = ValidationError(
            "Value cannot be zero",
            field_name="volume",
            invalid_value=0,
        )
        # 0 も invalid_value として正しく設定されることを確認
        assert exc.context["invalid_value"] == 0

    def test_str_representation(self) -> None:
        """文字列表現のテスト."""
        exc = ValidationError(
            "Invalid symbol format",
            field_name="symbol",
            invalid_value="INVALID",
        )
        exc_str = str(exc)
        assert "Invalid symbol format" in exc_str
        assert "field_name=symbol" in exc_str
        assert "invalid_value=INVALID" in exc_str


class TestExceptionHierarchy:
    """例外階層のテスト."""

    def test_database_error_hierarchy(self) -> None:
        """DatabaseError 系の階層構造のテスト."""
        crud_error = CRUDOperationError("CRUD failed")
        assert isinstance(crud_error, CRUDOperationError)
        assert isinstance(crud_error, DatabaseError)
        assert isinstance(crud_error, BaseModelException)
        assert isinstance(crud_error, Exception)

    def test_validation_error_hierarchy(self) -> None:
        """ValidationError の階層構造のテスト."""
        validation_error = ValidationError("Invalid data")
        assert isinstance(validation_error, ValidationError)
        assert isinstance(validation_error, BaseModelException)
        assert isinstance(validation_error, Exception)
        assert not isinstance(validation_error, DatabaseError)

    def test_model_not_found_error_hierarchy(self) -> None:
        """ModelNotFoundError の階層構造のテスト."""
        not_found_error = ModelNotFoundError("TestModel")
        assert isinstance(not_found_error, ModelNotFoundError)
        assert isinstance(not_found_error, BaseModelException)
        assert isinstance(not_found_error, Exception)
        assert not isinstance(not_found_error, DatabaseError)

    def test_can_catch_all_with_base_exception(self) -> None:
        """BaseModelException ですべての例外をキャッチできることのテスト."""
        exceptions = [
            DatabaseError("DB error"),
            CRUDOperationError("CRUD error"),
            ModelNotFoundError("Model"),
            ValidationError("Validation error"),
        ]
        for exc in exceptions:
            with pytest.raises(BaseModelException):
                raise exc


class TestExceptionUsageScenarios:
    """実際の使用シナリオのテスト."""

    def test_database_connection_error_scenario(self) -> None:
        """データベース接続エラーのシナリオ."""
        with pytest.raises(DatabaseError) as exc_info:
            raise DatabaseError(
                "Failed to connect to database",
                context={"host": "localhost", "port": 5432},
            )
        exc = exc_info.value
        assert "Failed to connect to database" in str(exc)
        assert exc.context["host"] == "localhost"
        assert exc.context["port"] == 5432

    def test_crud_create_duplicate_error_scenario(self) -> None:
        """CRUD作成時の重複エラーのシナリオ."""
        with pytest.raises(CRUDOperationError) as exc_info:
            raise CRUDOperationError(
                "Duplicate key violation",
                operation="create",
                model_name="Stocks1d",
                context={"symbol": "7203.T", "date": "2025-01-01"},
            )
        exc = exc_info.value
        assert exc.context["operation"] == "create"
        assert exc.context["model_name"] == "Stocks1d"

    def test_model_not_found_scenario(self) -> None:
        """モデル未発見のシナリオ."""
        with pytest.raises(ModelNotFoundError) as exc_info:
            raise ModelNotFoundError(
                "Stocks1d",
                symbol="7203.T",
                date="2025-01-01",
            )
        exc = exc_info.value
        assert "Stocks1d not found" in str(exc)

    def test_validation_price_error_scenario(self) -> None:
        """価格バリデーションエラーのシナリオ."""
        with pytest.raises(ValidationError) as exc_info:
            raise ValidationError(
                "Price must be non-negative",
                field_name="close",
                invalid_value=-100.50,
            )
        exc = exc_info.value
        assert exc.context["field_name"] == "close"
        assert exc.context["invalid_value"] == -100.50
