"""データアクセス層で使用するカスタム例外クラス定義.

このモジュールでは、モデル層における統一されたエラーハンドリング戦略を
実現するための例外クラスを提供します。

例外階層:
    BaseModelException (基底クラス)
    ├── DatabaseError (データベース操作エラー)
    │   └── CRUDOperationError (CRUD操作固有エラー)
    ├── ModelNotFoundError (モデル/レコード未発見エラー)
    └── ValidationError (データ検証エラー)

使用例:
    >>> from app.models.exceptions import ModelNotFoundError
    >>> if not stock_data:
    ...     raise ModelNotFoundError("Stock", symbol="7203.T")
"""

from __future__ import annotations

from typing import Any, Dict, Optional


class BaseModelException(Exception):
    """データアクセス層の例外基底クラス.

    すべてのモデル層の例外はこのクラスを継承します。
    エラーメッセージとコンテキスト情報を保持できます。

    Attributes:
        message: エラーメッセージ
        context: エラー発生時のコンテキスト情報（任意）
    """

    def __init__(
        self,
        message: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> None:
        """例外を初期化する.

        Args:
            message: エラーメッセージ
            context: エラー発生時のコンテキスト情報（任意）
        """
        self.message = message
        self.context = context or {}
        super().__init__(self.message)

    def __str__(self) -> str:
        """例外の文字列表現を返す.

        Returns:
            エラーメッセージとコンテキスト情報を含む文字列
        """
        if self.context:
            context_str = ", ".join(
                f"{key}={value}" for key, value in self.context.items()
            )
            return f"{self.message} (context: {context_str})"
        return self.message

    def __repr__(self) -> str:
        """例外のデバッグ用文字列表現を返す.

        Returns:
            クラス名、メッセージ、コンテキストを含む文字列
        """
        return (
            f"{self.__class__.__name__}"
            f"(message={self.message!r}, context={self.context!r})"
        )


class DatabaseError(BaseModelException):
    """データベース操作エラー.

    データベース接続、トランザクション、SQL実行などの
    データベース操作全般に関するエラーを表します。

    使用例:
        >>> try:
        ...     session.commit()
        ... except SQLAlchemyError as e:
        ...     raise DatabaseError(
        ...         "Failed to commit transaction",
        ...         context={"error": str(e)}
        ...     )
    """

    pass


class CRUDOperationError(DatabaseError):
    """CRUD操作固有エラー.

    Create, Read, Update, Delete操作における
    具体的なエラーを表します。

    Attributes:
        operation: 実行しようとしたCRUD操作 ("create", "read", "update",
            "delete")
        model_name: 操作対象のモデル名

    使用例:
        >>> raise CRUDOperationError(
        ...     "Failed to create stock data",
        ...     context={
        ...         "operation": "create",
        ...         "model_name": "Stocks1d",
        ...         "symbol": "7203.T",
        ...         "error": "Duplicate key violation"
        ...     }
        ... )
    """

    def __init__(
        self,
        message: str,
        operation: Optional[str] = None,
        model_name: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
    ) -> None:
        """CRUD操作エラーを初期化する.

        Args:
            message: エラーメッセージ
            operation: CRUD操作の種類 (例: "create", "read", "update",
                "delete")
            model_name: 操作対象のモデル名 (例: "Stocks1d")
            context: 追加のコンテキスト情報
        """
        context = context or {}
        if operation:
            context["operation"] = operation
        if model_name:
            context["model_name"] = model_name
        super().__init__(message, context)


class ModelNotFoundError(BaseModelException):
    """モデル/レコード未発見エラー.

    指定された条件でデータベースからレコードが見つからない場合に
    発生します。

    使用例:
        >>> stock_data = session.query(Stocks1d).filter_by(
        ...     symbol="7203.T", date="2025-01-01"
        ... ).first()
        >>> if not stock_data:
        ...     raise ModelNotFoundError(
        ...         "Stocks1d",
        ...         symbol="7203.T",
        ...         date="2025-01-01"
        ...     )
    """

    def __init__(
        self,
        model_name: str,
        **search_criteria: Any,
    ) -> None:
        """モデル未発見エラーを初期化する.

        Args:
            model_name: 検索対象のモデル名
            **search_criteria: 検索条件（キーワード引数）
        """
        message = f"{model_name} not found"
        super().__init__(message, context=search_criteria)


class ValidationError(BaseModelException):
    """データ検証エラー.

    データベースへの保存前のバリデーションで検出された
    不正なデータに関するエラーを表します。

    Attributes:
        field_name: 検証に失敗したフィールド名
        invalid_value: 不正な値

    使用例:
        >>> if price < 0:
        ...     raise ValidationError(
        ...         "Price must be non-negative",
        ...         field_name="close",
        ...         invalid_value=price
        ...     )
    """

    def __init__(
        self,
        message: str,
        field_name: Optional[str] = None,
        invalid_value: Optional[Any] = None,
        context: Optional[Dict[str, Any]] = None,
    ) -> None:
        """検証エラーを初期化する.

        Args:
            message: エラーメッセージ
            field_name: 検証に失敗したフィールド名
            invalid_value: 不正な値
            context: 追加のコンテキスト情報
        """
        context = context or {}
        if field_name:
            context["field_name"] = field_name
        if invalid_value is not None:
            context["invalid_value"] = invalid_value
        super().__init__(message, context)


__all__ = [
    "BaseModelException",
    "DatabaseError",
    "CRUDOperationError",
    "ModelNotFoundError",
    "ValidationError",
]
