"""エラーハンドリング・リカバリ機能.

バッチ処理におけるエラー分類、リトライ処理、エラーログ記録、
エラーレポート生成を提供します。
"""

from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import logging
import time
from typing import Any, Dict, List, Optional

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


logger = logging.getLogger(__name__)


class ErrorType(Enum):
    """エラー種別."""

    TEMPORARY = "temporary"  # 一時的エラー（リトライ対象）
    PERMANENT = "permanent"  # 永続的エラー（スキップ対象）
    SYSTEM = "system"  # システムエラー（バッチ停止）


class ErrorAction(Enum):
    """エラー処理アクション."""

    RETRY = "retry"  # リトライを実行
    SKIP = "skip"  # スキップして継続
    ABORT = "abort"  # バッチ停止


@dataclass
class ErrorRecord:
    """エラー記録."""

    timestamp: str
    error_type: str
    stock_code: str
    error_message: str
    exception_class: str
    retry_count: int = 0
    action_taken: str = ""
    context: Dict[str, Any] = field(default_factory=dict)
    error_code: Optional[str] = None
    details: Optional[Dict[str, Any]] = None


class ErrorHandler:
    """エラーハンドリングクラス.

    エラー分類、リトライ処理、ログ記録、レポート生成を行います。
    """

    def __init__(
        self,
        max_retries: int = 3,
        retry_delay: int = 2,
        backoff_multiplier: int = 2,
    ):
        """初期化.

        Args:
            max_retries: 最大リトライ回数
            retry_delay: 初回リトライ待機時間（秒）
            backoff_multiplier: 指数バックオフの係数。
        """
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.backoff_multiplier = backoff_multiplier

        # エラー統計
        self.error_stats: Dict[str, int] = defaultdict(int)

        # エラー記録リスト
        self.error_records: List[ErrorRecord] = []

        self.logger = logger

    def classify_error(self, error: Exception) -> ErrorType:
        """エラーを分類.

        Args:
            error: 発生した例外

        Returns:
            ErrorType: エラー種別。
        """
        error_class = error.__class__.__name__
        error_message = str(error).lower()

        # 新しい例外クラス体系による分類
        if isinstance(error, BaseStockAnalyzerException):
            return self._classify_custom_exception(error)

        # 従来の例外クラスによる分類（後方互換性）
        # 一時的エラー（ネットワーク関連）
        # Timeout, ConnectionError, TimeoutError, StockDataFetchError など
        if error_class in [
            "Timeout",
            "TimeoutError",
            "ConnectionError",
            "HTTPError",
            "StockDataFetchError",
        ]:
            # HTTPエラーの場合はステータスコードで判定
            if hasattr(error, "response") and error.response:
                status_code = error.response.status_code
                # 429 (Too Many Requests), 503 (Service Unavailable) など
                if status_code in [429, 503, 504]:
                    return ErrorType.TEMPORARY
                # 401, 403, 404 などは永続的エラー
                if status_code in [401, 403, 404]:
                    return ErrorType.PERMANENT
            # その他のHTTPエラー、StockDataFetchErrorは一時的と判定
            return ErrorType.TEMPORARY

        # タイムアウト・接続エラー（メッセージベース）
        if "timeout" in error_message or "connection" in error_message:
            return ErrorType.TEMPORARY

        # レート制限エラー
        if "rate limit" in error_message or "429" in error_message:
            return ErrorType.TEMPORARY

        # データベースエラー
        if error_class in [
            "DatabaseError",
            "OperationalError",
            "IntegrityError",
        ]:
            return ErrorType.SYSTEM

        # データ形式エラー
        if error_class in ["ValueError", "KeyError", "AttributeError"]:
            return ErrorType.PERMANENT

        # デフォルトは永続的エラー
        return ErrorType.PERMANENT

    def _classify_custom_exception(
        self, error: BaseStockAnalyzerException
    ) -> ErrorType:
        """カスタム例外クラスを分類.

        Args:
            error: カスタム例外

        Returns:
            ErrorType: エラー種別。
        """
        # システムエラー
        if isinstance(error, SystemException):
            return ErrorType.SYSTEM

        # データベースエラー
        if isinstance(error, DatabaseException):
            return self._classify_database_exception(error)

        # API/ネットワークエラー
        if isinstance(error, APIException):
            return self._classify_api_exception(error)

        # 株価データエラー
        if isinstance(error, StockDataException):
            return self._classify_stock_data_exception(error)

        # バッチ処理エラー
        if isinstance(error, BatchProcessingException):
            return self._classify_batch_exception(error)

        # バリデーションエラーは永続的
        if isinstance(error, ValidationException):
            return ErrorType.PERMANENT

        # ビジネスロジックエラーは永続的
        if isinstance(error, BusinessLogicException):
            return ErrorType.PERMANENT

        # デフォルトは永続的
        return ErrorType.PERMANENT

    def _classify_database_exception(
        self, error: DatabaseException
    ) -> ErrorType:
        """データベース例外を分類."""
        # 接続エラーやタイムアウトは一時的
        if error.error_code in [
            ErrorCode.DATABASE_CONNECTION,
            ErrorCode.DATABASE_TIMEOUT,
        ]:
            return ErrorType.TEMPORARY
        # 整合性制約違反などは永続的
        return ErrorType.PERMANENT

    def _classify_api_exception(self, error: APIException) -> ErrorType:
        """API例外を分類."""
        # タイムアウトやレート制限は一時的
        if error.error_code in [
            ErrorCode.API_TIMEOUT,
            ErrorCode.API_RATE_LIMIT,
        ]:
            return ErrorType.TEMPORARY
        # 認証エラーは永続的
        if error.error_code == ErrorCode.API_AUTHENTICATION:
            return ErrorType.PERMANENT
        # その他のAPI接続エラーは一時的
        return ErrorType.TEMPORARY

    def _classify_stock_data_exception(
        self, error: StockDataException
    ) -> ErrorType:
        """株価データ例外を分類."""
        # 取得エラーは一時的
        if error.error_code == ErrorCode.STOCK_DATA_FETCH:
            return ErrorType.TEMPORARY
        # バリデーションエラーは永続的
        if error.error_code == ErrorCode.STOCK_DATA_VALIDATION:
            return ErrorType.PERMANENT
        # その他は一時的
        return ErrorType.TEMPORARY

    def _classify_batch_exception(
        self, error: BatchProcessingException
    ) -> ErrorType:
        """バッチ処理例外を分類."""
        # タイムアウトやリソース不足は一時的
        if error.error_code in [
            ErrorCode.BATCH_TIMEOUT,
            ErrorCode.BATCH_RESOURCE,
        ]:
            return ErrorType.TEMPORARY
        # その他は永続的
        return ErrorType.PERMANENT

    def handle_error(
        self,
        error: Exception,
        stock_code: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> ErrorAction:
        """エラー処理を判定.

        Args:
            error: 発生した例外
            stock_code: 銘柄コード
            context: エラー発生時のコンテキスト情報

        Returns:
            ErrorAction: 実行すべきアクション。
        """
        error_type = self.classify_error(error)
        context = context or {}

        # エラー統計を更新
        self.error_stats[error_type.value] += 1

        # エラー記録を作成
        error_code = None
        details = None
        if isinstance(error, BaseStockAnalyzerException):
            error_code = error.error_code.value
            details = error.details

        error_record = ErrorRecord(
            timestamp=datetime.now().isoformat(),
            error_type=error_type.value,
            stock_code=stock_code,
            error_message=str(error),
            exception_class=error.__class__.__name__,
            retry_count=context.get("retry_count", 0),
            context=context,
            error_code=error_code,
            details=details,
        )

        # エラー種別に応じた処理判定
        if error_type == ErrorType.TEMPORARY:
            action = self._handle_temporary_error(error, stock_code, context)
        elif error_type == ErrorType.PERMANENT:
            action = self._handle_permanent_error(error, stock_code, context)
        else:  # SYSTEM
            action = self._handle_system_error(error, stock_code, context)

        # アクションを記録
        error_record.action_taken = action.value
        self.error_records.append(error_record)

        # ログ出力
        self._log_error(error_record, action)

        return action

    def _handle_temporary_error(
        self, error: Exception, stock_code: str, context: Dict[str, Any]
    ) -> ErrorAction:
        """一時的エラーの処理.

        Args:
            error: 発生した例外
            stock_code: 銘柄コード
            context: コンテキスト情報

        Returns:
            ErrorAction: 実行すべきアクション。
        """
        retry_count = context.get("retry_count", 0)

        if retry_count < self.max_retries:
            self.logger.info(
                f"一時的エラー検出: {stock_code} - リトライします "
                f"({retry_count + 1}/{self.max_retries})"
            )
            return ErrorAction.RETRY
        else:
            self.logger.warning(
                f"最大リトライ回数到達: {stock_code} - スキップします"
            )
            return ErrorAction.SKIP

    def _handle_permanent_error(
        self, error: Exception, stock_code: str, context: Dict[str, Any]
    ) -> ErrorAction:
        """永続的エラーの処理.

        Args:
            error: 発生した例外
            stock_code: 銘柄コード
            context: コンテキスト情報

        Returns:
            ErrorAction: 実行すべきアクション。
        """
        self.logger.warning(
            f"永続的エラー検出: {stock_code} - スキップします: {error}"
        )
        return ErrorAction.SKIP

    def _handle_system_error(
        self, error: Exception, stock_code: str, context: Dict[str, Any]
    ) -> ErrorAction:
        """システムエラーの処理.

        Args:
            error: 発生した例外
            stock_code: 銘柄コード
            context: コンテキスト情報

        Returns:
            ErrorAction: 実行すべきアクション。
        """
        self.logger.error(
            f"システムエラー検出: {stock_code} - バッチを停止します: {error}"
        )
        return ErrorAction.ABORT

    def retry_with_backoff(self, retry_count: int) -> float:
        """指数バックオフでリトライ待機時間を計算.

        Args:
            retry_count: 現在のリトライ回数

        Returns:
            float: 待機時間（秒）。
        """
        delay = self.retry_delay * (self.backoff_multiplier**retry_count)
        self.logger.debug(f"リトライ待機: {delay}秒")
        time.sleep(delay)
        return delay

    def _log_error(self, error_record: ErrorRecord, action: ErrorAction):
        """エラーログを記録.

        Args:
            error_record: エラー記録
            action: 実行アクション。
        """
        log_message = (
            f"[エラーハンドリング] "
            f"銘柄={error_record.stock_code}, "
            f"種別={error_record.error_type}, "
            f"例外={error_record.exception_class}, "
            f"アクション={action.value}, "
            f"リトライ回数={error_record.retry_count}, "
            f"メッセージ={error_record.error_message}"
        )

        if action == ErrorAction.ABORT:
            self.logger.error(log_message)
        elif action == ErrorAction.RETRY:
            self.logger.warning(log_message)
        else:
            self.logger.info(log_message)

    def generate_error_report(self) -> Dict[str, Any]:
        """エラーレポートを生成.

        Returns:
            Dict[str, Any]: エラーレポート。
        """
        # エラー種別ごとの集計
        error_by_type: defaultdict[str, int] = defaultdict(int)
        error_by_stock: defaultdict[str, int] = defaultdict(int)

        for record in self.error_records:
            error_by_type[record.error_type] += 1
            error_by_stock[record.stock_code] += 1

        # 最も多くエラーが発生した銘柄トップ10
        top_error_stocks = sorted(
            error_by_stock.items(), key=lambda x: x[1], reverse=True
        )[:10]

        # 最近のエラー詳細（最大50件）
        recent_errors = [
            {
                "timestamp": rec.timestamp,
                "stock_code": rec.stock_code,
                "error_type": rec.error_type,
                "error_message": rec.error_message,
                "exception_class": rec.exception_class,
                "retry_count": rec.retry_count,
                "action_taken": rec.action_taken,
            }
            for rec in self.error_records[-50:]
        ]

        report = {
            "summary": {
                "total_errors": len(self.error_records),
                "error_by_type": dict(error_by_type),
                "unique_stocks_with_errors": len(error_by_stock),
                "generated_at": datetime.now().isoformat(),
            },
            "top_error_stocks": [
                {"stock_code": code, "error_count": count}
                for code, count in top_error_stocks
            ],
            "recent_errors": recent_errors,
            "statistics": {
                "temporary_errors": error_by_type.get("temporary", 0),
                "permanent_errors": error_by_type.get("permanent", 0),
                "system_errors": error_by_type.get("system", 0),
            },
        }

        return report

    def get_error_statistics(self) -> Dict[str, Any]:
        """エラー統計情報を取得.

        Returns:
            Dict[str, Any]: エラー統計。
        """
        return {
            "total_errors": len(self.error_records),
            "error_stats": dict(self.error_stats),
            "error_records_count": len(self.error_records),
            "temporary": self.error_stats.get("temporary", 0),
            "permanent": self.error_stats.get("permanent", 0),
            "system": self.error_stats.get("system", 0),
        }

    def clear_error_records(self):
        """エラー記録をクリア."""
        self.error_records.clear()
        self.error_stats.clear()
        self.logger.info("エラー記録をクリアしました")
