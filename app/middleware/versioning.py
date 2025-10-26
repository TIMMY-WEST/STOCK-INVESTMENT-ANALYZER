"""APIバージョニングミドルウェア.

URLパスベースのAPIバージョニングを提供するミドルウェア。
"""

import re
from typing import Optional, Tuple

from flask import Flask, request


class APIVersioningMiddleware:
    """APIバージョニングミドルウェア.

    リクエストURLからAPIバージョンを解析し、適切なルーティングを行います。
    """

    def __init__(self, app: Optional[Flask] = None):
        """ミドルウェアを初期化.

        Args:
            app: Flaskアプリケーションインスタンス
        """
        self.app = app
        if app is not None:
            self.init_app(app)

    def init_app(self, app: Flask) -> None:
        """Flaskアプリケーションにミドルウェアを登録.

        Args:
            app: Flaskアプリケーションインスタンス
        """
        self.app = app
        app.before_request(lambda: self.process_request(request))
        app.config.setdefault("API_DEFAULT_VERSION", "v1")
        app.config.setdefault("API_SUPPORTED_VERSIONS", ["v1"])

    def process_request(self, request):
        """リクエスト処理時にバージョン情報を設定.

        Args:
            request: Flaskリクエストオブジェクト
        """
        # URLからバージョン情報を抽出
        version, is_versioned = self.extract_version_from_url(request.path)

        # バージョンが指定されていない場合はデフォルトを使用
        # デフォルトバージョンを設定
        if not version:
            version = "v1"
            if self.app:
                version = self.app.config.get("API_DEFAULT_VERSION", "v1")

        # リクエストオブジェクトにバージョン情報を追加
        if hasattr(request, "__dict__"):
            request.api_version = version
            request.is_versioned_api = is_versioned

            # アプリケーションオブジェクトも追加（必要に応じて）
            if self.app:
                request.app = self.app

        # サポートされていないバージョンの場合はエラー
        if not self.is_supported_version(version):
            from flask import jsonify

            return (
                jsonify(
                    {
                        "error": "Unsupported API version",
                        "version": version,
                        "supported_versions": self.get_version_info()[
                            "supported_versions"
                        ],
                    }
                ),
                400,
            )

        # バージョン情報をログに記録（デバッグ用）
        if hasattr(request, "api_version"):
            app = self.app or request.app
            app.logger.debug(
                f"API Version: {request.api_version}, Versioned: {request.is_versioned_api}"
            )

    def extract_version_from_url(
        self, url_path: str
    ) -> Tuple[Optional[str], bool]:
        """URLパスからAPIバージョンを抽出する.

        Args:
            url_path: リクエストのURLパス

        Returns:
            Tuple[Optional[str], bool]: (抽出されたバージョン, バージョン付きAPIかどうか)
        """
        # /api/v1/... の形式からバージョンを抽出
        match = re.match(r"^/api/(v\d+)/", url_path)
        if match is not None:
            return match.group(1), True
        return None, False

    def is_supported_version(self, version: str) -> bool:
        """指定されたバージョンがサポートされているかチェック.

        Args:
            version: チェックするバージョン文字列

        Returns:
            bool: サポートされている場合True
        """
        if not self.app:
            return version == "v1"  # デフォルト

        supported_versions = self.app.config.get(
            "API_SUPPORTED_VERSIONS", ["v1"]
        )
        return version in supported_versions

    def get_version_info(self) -> dict:
        """現在のバージョン設定情報を取得.

        Returns:
            dict: バージョン設定情報
        """
        if not self.app:
            return {"default_version": "v1", "supported_versions": ["v1"]}

        return {
            "default_version": self.app.config.get(
                "API_DEFAULT_VERSION", "v1"
            ),
            "supported_versions": self.app.config.get(
                "API_SUPPORTED_VERSIONS", ["v1"]
            ),
        }


def create_versioned_blueprint_name(original_name: str, version: str) -> str:
    """バージョン付きBlueprint名を生成.

    Args:
        original_name: 元のBlueprint名
        version: バージョン文字列

    Returns:
        str: バージョン付きBlueprint名

    Examples:
        create_versioned_blueprint_name('bulk_api', 'v1') -> 'bulk_api_v1'
    """
    return f"{original_name}_{version}"


def create_versioned_url_prefix(original_prefix: str, version: str) -> str:
    """バージョン付きURL prefixを生成.

    Args:
        original_prefix: 元のURL prefix
        version: バージョン文字列

    Returns:
        str: バージョン付きURL prefix

    Examples:
        create_versioned_url_prefix('/api/bulk-data', 'v1') -> '/api/v1/bulk-data'
    """
    if original_prefix.startswith("/api/"):
        # /api/bulk-data -> /api/v1/bulk-data
        return original_prefix.replace("/api/", f"/api/{version}/")
    elif original_prefix.startswith("/api"):
        # /api -> /api/v1
        return f"/api/{version}"
    else:
        # その他の場合はそのまま
        return original_prefix
