"""APIバージョニングミドルウェア.

URLパスベースのAPIバージョニングを提供するミドルウェア。
"""

import re
from typing import Optional, Tuple

import flask
from flask import Flask


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
        # インスタンス属性（テストが参照）
        self.default_version = "v1"
        self.supported_versions = ["v1"]
        if app is not None:
            self.init_app(app)

    def init_app(self, app: Flask) -> None:
        """Flaskアプリケーションにミドルウェアを登録.

        Args:
            app: Flaskアプリケーションインスタンス
        """
        self.app = app
        # Flaskのrequestを直接使用するようにする
        app.before_request(lambda: self.process_request(flask.request))
        app.config.setdefault("API_DEFAULT_VERSION", "v1")
        app.config.setdefault("API_SUPPORTED_VERSIONS", ["v1"])
        # インスタンス属性を設定
        self.default_version = app.config.get("API_DEFAULT_VERSION", "v1")
        self.supported_versions = app.config.get(
            "API_SUPPORTED_VERSIONS", ["v1"]
        )

    def before_request(self):
        """テスト用に直接呼び出せるbefore_requestラッパー."""
        # テストでモックできるように、RequestProxyを使用
        return self.process_request(request)

    def process_request(self, request):
        """リクエスト処理時にバージョン情報を設定.

        Args:
            request: Flaskリクエストオブジェクト
        """
        # URLからバージョン情報を抽出
        version, is_versioned = self.extract_version_from_url(request.path)

        # バージョンが指定されていない場合はデフォルトバージョンを設定
        if not version:
            version = self.default_version

        # リクエストオブジェクトにバージョン情報を追加
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
        return version in self.supported_versions

    def get_version_info(self) -> dict:
        """現在のバージョン設定情報を取得.

        Returns:
            dict: バージョン設定情報
        """
        return {
            "default_version": self.default_version,
            "supported_versions": self.supported_versions,
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
    if original_prefix == "/api":
        # /api -> /api/v1
        return f"/api/{version}"
    if original_prefix in ("/", ""):
        # ルートや空文字 -> /v1
        return f"/{version}"
    # その他の場合はそのまま
    return original_prefix


def parse_api_version(url_path: str) -> Optional[str]:
    """URLパスからAPIバージョンを解析して返す.

    Args:
        url_path: リクエストのURLパス

    Returns:
        Optional[str]: 解析されたバージョン（例: 'v1'）。見つからない場合はNone。
    """
    if not url_path:
        return None
    match = re.match(r"^/api/(v\d+)/", url_path)
    return match.group(1) if match else None


class RequestProxy:
    """Flaskの`request`をモックしやすくするための軽量プロキシ.

    - ユニットテストの`@patch('app.middleware.versioning.request')`が
      元のLocalProxyにアクセスしようとして失敗しないよう、
      特殊属性アクセス（例: '__func__'）は存在しないものとして扱う。
    - 実運用では`flask.request`へフォワードする。
    """

    def __getattr__(self, name):
        """属性アクセスをflask.requestにフォワード."""
        # unittest.mockやinspectの内部チェックで参照されるプライベート属性は未定義扱い
        if name.startswith("_"):
            raise AttributeError(name)
        return getattr(flask.request, name)


# モジュール公開名として`request`をプロキシに差し替え
request = RequestProxy()
