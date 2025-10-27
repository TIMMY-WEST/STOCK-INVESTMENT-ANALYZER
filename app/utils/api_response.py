"""APIレスポンス形式の統一ユーティリティ.

このモジュールは、全APIエンドポイントで統一されたJSONレスポンス形式を提供します。
JSON API仕様とRESTful APIベストプラクティスに準拠した構造を採用しています。
"""

from typing import Any, Dict, List, Optional, Union

from flask import jsonify


class APIResponse:
    """統一されたAPIレスポンス形式を提供するクラス."""

    @staticmethod
    def success(
        data: Optional[Union[Dict[str, Any], List[Any]]] = None,
        message: Optional[str] = None,
        meta: Optional[Dict[str, Any]] = None,
        status_code: int = 200,
    ) -> tuple:
        """成功レスポンスを生成.

        Args:
            data: レスポンスデータ
            message: 成功メッセージ（オプション）
            meta: メタデータ（オプション）
            status_code: HTTPステータスコード（デフォルト: 200）

        Returns:
            tuple: (jsonifyされたレスポンス, ステータスコード)
        """
        response: Dict[str, Any] = {"status": "success"}

        if message:
            response["message"] = message

        if data is not None:
            response["data"] = data

        if meta:
            response["meta"] = meta

        return jsonify(response), status_code

    @staticmethod
    def error(
        error_code: str,
        message: str,
        details: Optional[Dict[str, Any]] = None,
        status_code: int = 400,
    ) -> tuple:
        """エラーレスポンスを生成.

        Args:
            error_code: エラーコード（例: "INVALID_SYMBOL"）
            message: エラーメッセージ
            details: エラー詳細情報（オプション）
            status_code: HTTPステータスコード（デフォルト: 400）

        Returns:
            tuple: (jsonifyされたレスポンス, ステータスコード)
        """
        error_obj: Dict[str, Any] = {"code": error_code, "message": message}

        if details:
            error_obj["details"] = details

        response: Dict[str, Any] = {
            "status": "error",
            "message": message,  # トップレベルにもmessageを追加（後方互換性）
            "error": error_obj,
        }

        return jsonify(response), status_code

    @staticmethod
    def paginated(
        data: List[Any],
        total: int,
        limit: int,
        offset: int,
        meta: Optional[Dict[str, Any]] = None,
        message: Optional[str] = None,
    ) -> tuple:
        """ページネーション付き成功レスポンスを生成.

        Args:
            data: レスポンスデータのリスト
            total: 総件数
            limit: 1ページあたりの件数
            offset: オフセット
            meta: 追加のメタデータ（オプション）
            message: 成功メッセージ（オプション）

        Returns:
            tuple: (jsonifyされたレスポンス, ステータスコード)
        """
        response: Dict[str, Any] = {"status": "success"}

        if message:
            response["message"] = message

        response["data"] = data

        # ページネーション情報を構築
        pagination: Dict[str, Any] = {
            "total": total,
            "limit": limit,
            "offset": offset,
            "count": len(data),
            "has_next": (offset + len(data)) < total,
            "has_prev": offset > 0,
        }

        # メタデータを構築
        response_meta: Dict[str, Any] = {"pagination": pagination}
        if meta:
            response_meta.update(meta)

        response["meta"] = response_meta

        return jsonify(response), 200


class ErrorCode:
    """標準エラーコード定数."""

    # バリデーションエラー (400)
    VALIDATION_ERROR = "VALIDATION_ERROR"
    INVALID_SYMBOL = "INVALID_SYMBOL"
    INVALID_PERIOD = "INVALID_PERIOD"
    INVALID_INTERVAL = "INVALID_INTERVAL"
    INVALID_DATETIME_RANGE = "INVALID_DATETIME_RANGE"
    INVALID_PARAMETER = "INVALID_PARAMETER"

    # 認証・認可エラー (401, 403)
    UNAUTHORIZED = "UNAUTHORIZED"
    FORBIDDEN = "FORBIDDEN"

    # リソースエラー (404)
    NOT_FOUND = "NOT_FOUND"
    DATA_NOT_FOUND = "DATA_NOT_FOUND"

    # タイムアウト (408)
    TIMEOUT = "TIMEOUT"
    MAX_PERIOD_TIMEOUT = "MAX_PERIOD_TIMEOUT"

    # レート制限 (429)
    RATE_LIMIT_EXCEEDED = "RATE_LIMIT_EXCEEDED"

    # サーバーエラー (500)
    INTERNAL_SERVER_ERROR = "INTERNAL_SERVER_ERROR"
    DATABASE_ERROR = "DATABASE_ERROR"
    DATA_FETCH_ERROR = "DATA_FETCH_ERROR"

    # 外部APIエラー (502)
    EXTERNAL_API_ERROR = "EXTERNAL_API_ERROR"


# 後方互換性のためのエイリアス（既存コードとの互換性を維持）
def success_response(
    data: Optional[Union[Dict[str, Any], List[Any]]] = None,
    message: Optional[str] = None,
    meta: Optional[Dict[str, Any]] = None,
    status_code: int = 200,
) -> tuple:
    """成功レスポンスを生成（後方互換性のための関数）.

    Args:
        data: レスポンスデータ
        message: 成功メッセージ
        meta: メタデータ
        status_code: HTTPステータスコード

    Returns:
        tuple: (jsonifyされたレスポンス, ステータスコード)
    """
    return APIResponse.success(data, message, meta, status_code)


def error_response(
    error_code: str,
    message: str,
    details: Optional[Dict[str, Any]] = None,
    status_code: int = 400,
) -> tuple:
    """エラーレスポンスを生成（後方互換性のための関数）.

    Args:
        error_code: エラーコード
        message: エラーメッセージ
        details: エラー詳細情報
        status_code: HTTPステータスコード

    Returns:
        tuple: (jsonifyされたレスポンス, ステータスコード)
    """
    return APIResponse.error(error_code, message, details, status_code)


def paginated_response(
    data: List[Any],
    total: int,
    limit: int,
    offset: int,
    meta: Optional[Dict[str, Any]] = None,
    message: Optional[str] = None,
) -> tuple:
    """ページネーション付きレスポンスを生成（後方互換性のための関数）.

    Args:
        data: レスポンスデータのリスト
        total: 総件数
        limit: 1ページあたりの件数
        offset: オフセット
        meta: 追加のメタデータ
        message: 成功メッセージ

    Returns:
        tuple: (jsonifyされたレスポンス, ステータスコード)
    """
    return APIResponse.paginated(data, total, limit, offset, meta, message)
