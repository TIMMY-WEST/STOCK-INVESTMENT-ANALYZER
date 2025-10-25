"""株価投資分析システムのカスタム例外クラス定義.

このモジュールは、システム全体で使用される例外クラスの階層構造と
エラーコード体系を提供します。
"""

from enum import Enum
from typing import Any, Dict, Optional


class ErrorCode(Enum):
    """エラーコード定義.

    各エラーに一意のコードを割り当て、ログ分析とトラブルシューティングを支援します。
    """

    # システムエラー (1000番台)
    SYSTEM_UNKNOWN = "SYS_1000"
    SYSTEM_CONFIG = "SYS_1001"
    SYSTEM_RESOURCE = "SYS_1002"

    # データベースエラー (2000番台)
    DATABASE_CONNECTION = "DB_2000"
    DATABASE_QUERY = "DB_2001"
    DATABASE_INTEGRITY = "DB_2002"
    DATABASE_TRANSACTION = "DB_2003"
    DATABASE_TIMEOUT = "DB_2004"

    # 株価データエラー (3000番台)
    STOCK_DATA_FETCH = "STK_3000"
    STOCK_DATA_VALIDATION = "STK_3001"
    STOCK_DATA_CONVERSION = "STK_3002"
    STOCK_DATA_SAVE = "STK_3003"
    STOCK_DATA_NOT_FOUND = "STK_3004"

    # バッチ処理エラー (4000番台)
    BATCH_EXECUTION = "BCH_4000"
    BATCH_PROCESSING = "BCH_4001"
    BATCH_TIMEOUT = "BCH_4002"
    BATCH_RESOURCE = "BCH_4003"

    # API/ネットワークエラー (5000番台)
    API_CONNECTION = "API_5000"
    API_TIMEOUT = "API_5001"
    API_RATE_LIMIT = "API_5002"
    API_AUTHENTICATION = "API_5003"
    API_RESPONSE = "API_5004"

    # バリデーションエラー (6000番台)
    VALIDATION_REQUIRED = "VAL_6000"
    VALIDATION_FORMAT = "VAL_6001"
    VALIDATION_RANGE = "VAL_6002"
    VALIDATION_TYPE = "VAL_6003"

    # ビジネスロジックエラー (7000番台)
    BUSINESS_RULE = "BIZ_7000"
    BUSINESS_STATE = "BIZ_7001"
    BUSINESS_PERMISSION = "BIZ_7002"


class BaseStockAnalyzerException(Exception):
    """株価投資分析システムの基底例外クラス.

    全てのカスタム例外の基底クラスとして、共通の機能を提供します。
    """

    def __init__(
        self,
        message: str,
        error_code: ErrorCode,
        details: Optional[Dict[str, Any]] = None,
        original_exception: Optional[Exception] = None,
    ):
        """例外の初期化.

        Args:
            message: エラーメッセージ
            error_code: エラーコード
            details: 追加の詳細情報
            original_exception: 元の例外（ラップする場合）
        """
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.details = details or {}
        self.original_exception = original_exception

    def to_dict(self) -> Dict[str, Any]:
        """例外情報を辞書形式で返す.

        Returns:
            Dict[str, Any]: 例外情報の辞書
        """
        return {
            "error_code": self.error_code.value,
            "message": self.message,
            "details": self.details,
            "exception_type": self.__class__.__name__,
            "original_exception": (
                str(self.original_exception)
                if self.original_exception
                else None
            ),
        }

    def __str__(self) -> str:
        """文字列表現を返す."""
        return f"[{self.error_code.value}] {self.message}"


class SystemException(BaseStockAnalyzerException):
    """システム関連例外.

    システム設定、リソース不足、予期しないエラーなど、
    システムレベルの問題を表す例外です。
    """

    pass


class DatabaseException(BaseStockAnalyzerException):
    """データベース関連例外.

    データベース接続、クエリ実行、整合性制約違反など、
    データベース操作に関する例外です。
    """

    pass


class StockDataException(BaseStockAnalyzerException):
    """株価データ関連例外.

    株価データの取得、変換、保存、バリデーションなど、
    株価データ処理に関する例外です。
    """

    pass


class BatchProcessingException(BaseStockAnalyzerException):
    """バッチ処理関連例外.

    バッチ実行、処理タイムアウト、リソース不足など、
    バッチ処理に関する例外です。
    """

    pass


class APIException(BaseStockAnalyzerException):
    """API/ネットワーク関連例外.

    外部API接続、タイムアウト、レート制限、認証エラーなど、
    ネットワーク通信に関する例外です。
    """

    pass


class ValidationException(BaseStockAnalyzerException):
    """バリデーション関連例外.

    入力値検証、フォーマットエラー、範囲チェックなど、
    データバリデーションに関する例外です。
    """

    pass


class BusinessLogicException(BaseStockAnalyzerException):
    """ビジネスロジック関連例外.

    業務ルール違反、状態不整合、権限エラーなど、
    ビジネスロジックに関する例外です。
    """

    pass


# 具体的な例外クラス（既存コードとの互換性を保つため）
class DatabaseError(DatabaseException):
    """データベースエラー（既存コードとの互換性用）."""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        """データベースエラーを初期化します."""
        super().__init__(
            message=message,
            error_code=ErrorCode.DATABASE_CONNECTION,
            details=details,
        )


class StockDataError(StockDataException):
    """株価データエラー（既存コードとの互換性用）."""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        """株価データエラーを初期化します."""
        super().__init__(
            message=message,
            error_code=ErrorCode.STOCK_DATA_FETCH,
            details=details,
        )


class StockDataFetchError(StockDataException):
    """株価データ取得エラー."""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        """株価データ取得エラーを初期化します."""
        super().__init__(
            message=message,
            error_code=ErrorCode.STOCK_DATA_FETCH,
            details=details,
        )


class StockDataValidationError(StockDataException):
    """株価データバリデーションエラー."""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        """株価データバリデーションエラーを初期化します."""
        super().__init__(
            message=message,
            error_code=ErrorCode.STOCK_DATA_VALIDATION,
            details=details,
        )


class StockDataConversionError(StockDataException):
    """株価データ変換エラー."""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        """株価データ変換エラーを初期化します."""
        super().__init__(
            message=message,
            error_code=ErrorCode.STOCK_DATA_CONVERSION,
            details=details,
        )


class StockDataSaveError(StockDataException):
    """株価データ保存エラー."""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        """株価データ保存エラーを初期化します."""
        super().__init__(
            message=message,
            error_code=ErrorCode.STOCK_DATA_SAVE,
            details=details,
        )


class BatchServiceError(BatchProcessingException):
    """バッチサービスエラー."""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        """バッチサービスエラーを初期化します."""
        super().__init__(
            message=message,
            error_code=ErrorCode.BATCH_EXECUTION,
            details=details,
        )


class StockBatchProcessingError(BatchProcessingException):
    """株価バッチ処理エラー."""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        """株価バッチ処理エラーを初期化します."""
        super().__init__(
            message=message,
            error_code=ErrorCode.BATCH_PROCESSING,
            details=details,
        )


class BulkDataServiceError(APIException):
    """一括データサービスエラー."""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        """一括データサービスエラーを初期化します."""
        super().__init__(
            message=message,
            error_code=ErrorCode.API_CONNECTION,
            details=details,
        )


class JPXStockServiceError(APIException):
    """JPX株価サービスエラー."""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        """JPX株価サービスエラーを初期化します."""
        super().__init__(
            message=message,
            error_code=ErrorCode.API_CONNECTION,
            details=details,
        )


class StockDataOrchestrationError(SystemException):
    """株価データオーケストレーションエラー."""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        """株価データオーケストレーションエラーを初期化します."""
        super().__init__(
            message=message,
            error_code=ErrorCode.SYSTEM_UNKNOWN,
            details=details,
        )
