"""APIバージョニングミドルウェアの単体テスト."""

from unittest.mock import Mock, patch

from flask import Flask, request
import pytest

from app.middleware.versioning import (
    APIVersioningMiddleware,
    create_versioned_blueprint_name,
    create_versioned_url_prefix,
    parse_api_version,
)


class TestAPIVersioningMiddleware:
    """APIVersioningMiddlewareクラスのテスト."""

    def test_init_with_app_with_valid_app_returns_initialized_middleware(self):
        """アプリケーションとの初期化テスト."""
        app = Flask(__name__)
        middleware = APIVersioningMiddleware(app)

        assert middleware.app == app
        assert middleware.default_version == "v1"
        assert middleware.supported_versions == ["v1"]

    def test_init_with_custom_config_with_valid_config_returns_configured_middleware(
        self,
    ):
        """カスタム設定での初期化テスト."""
        app = Flask(__name__)
        app.config["API_DEFAULT_VERSION"] = "v2"
        app.config["API_SUPPORTED_VERSIONS"] = ["v1", "v2", "v3"]

        middleware = APIVersioningMiddleware(app)

        assert middleware.default_version == "v2"
        assert middleware.supported_versions == ["v1", "v2", "v3"]

    def test_versioning_middleware_init_without_app_with_no_parameters_returns_default_configuration(
        self,
    ):
        """アプリケーションなしでの初期化テスト."""
        middleware = APIVersioningMiddleware()

        assert middleware.app is None
        assert middleware.default_version == "v1"
        assert middleware.supported_versions == ["v1"]

    def test_versioning_middleware_init_app_method_with_configured_app_returns_initialized_middleware(
        self,
    ):
        """init_appメソッドのテスト."""
        app = Flask(__name__)
        app.config["API_DEFAULT_VERSION"] = "v2"
        app.config["API_SUPPORTED_VERSIONS"] = ["v1", "v2"]

        middleware = APIVersioningMiddleware()
        middleware.init_app(app)

        assert middleware.app == app
        assert middleware.default_version == "v2"
        assert middleware.supported_versions == ["v1", "v2"]

    @patch("app.middleware.versioning.request")
    def test_before_request_with_versioned_path_with_valid_version_returns_processed_request(
        self, mock_request
    ):
        """バージョン付きパスでのbefore_requestテスト."""
        app = Flask(__name__)
        middleware = APIVersioningMiddleware(app)

        mock_request.path = "/api/v2/stocks"

        with app.app_context():
            middleware.before_request()
            assert mock_request.api_version == "v2"

    @patch("app.middleware.versioning.request")
    def test_before_request_with_non_versioned_path_with_default_path_returns_unmodified_request(
        self, mock_request
    ):
        """バージョンなしパスでのbefore_requestテスト."""
        app = Flask(__name__)
        middleware = APIVersioningMiddleware(app)

        mock_request.path = "/api/stocks"

        with app.app_context():
            middleware.before_request()
            assert mock_request.api_version == "v1"  # デフォルトバージョン

    @patch("app.middleware.versioning.request")
    def test_before_request_with_non_api_path_with_static_path_returns_unmodified_request(
        self, mock_request
    ):
        """API以外のパスでのbefore_requestテスト."""
        app = Flask(__name__)
        middleware = APIVersioningMiddleware(app)

        mock_request.path = "/home"

        with app.app_context():
            middleware.before_request()
            assert mock_request.api_version == "v1"  # デフォルトバージョン


class TestParseApiVersion:
    """parse_api_version関数のテスト."""

    def test_parse_api_version_from_path_with_valid_versioned_paths_returns_correct_version(
        self,
    ):
        """パスからのバージョン解析テスト."""
        assert parse_api_version("/api/v1/stocks") == "v1"
        assert parse_api_version("/api/v2/bulk-data") == "v2"
        assert parse_api_version("/api/v10/system") == "v10"

    def test_parse_api_version_without_version_with_unversioned_paths_returns_none(
        self,
    ):
        """バージョンなしパスの解析テスト."""
        assert parse_api_version("/api/stocks") is None
        assert parse_api_version("/api/bulk-data") is None
        assert parse_api_version("/api/system") is None

    def test_parse_api_version_non_api_path_with_static_paths_returns_none(
        self,
    ):
        """API以外のパスの解析テスト."""
        assert parse_api_version("/home") is None
        assert parse_api_version("/about") is None
        assert parse_api_version("/") is None

    def test_parse_api_version_invalid_format_with_malformed_paths_returns_none(
        self,
    ):
        """無効なフォーマットのテスト."""
        assert parse_api_version("/api/version1/stocks") is None
        assert parse_api_version("/api/1/stocks") is None
        assert parse_api_version("/api/v/stocks") is None

    def test_parse_api_version_edge_cases_with_empty_paths_returns_none(self):
        """エッジケースのテスト."""
        assert parse_api_version("") is None
        assert parse_api_version("/") is None
        assert parse_api_version("/api") is None
        assert parse_api_version("/api/") is None


class TestVersioningHelpers:
    """バージョニングヘルパー関数のテスト."""

    def test_versioning_create_versioned_blueprint_name_with_valid_inputs_returns_formatted_name(
        self,
    ):
        """バージョン付きBlueprint名作成のテスト."""
        assert create_versioned_blueprint_name("api", "v1") == "api_v1"
        assert (
            create_versioned_blueprint_name("bulk_api", "v2") == "bulk_api_v2"
        )
        assert (
            create_versioned_blueprint_name("stock_master", "v10")
            == "stock_master_v10"
        )

    def test_versioning_create_versioned_url_prefix_with_valid_paths_returns_formatted_prefix(
        self,
    ):
        """バージョン付きURL prefix作成のテスト."""
        assert (
            create_versioned_url_prefix("/api/stocks", "v1")
            == "/api/v1/stocks"
        )
        assert (
            create_versioned_url_prefix("/api/bulk-data", "v2")
            == "/api/v2/bulk-data"
        )
        assert (
            create_versioned_url_prefix("/api/system", "v10")
            == "/api/v10/system"
        )

    def test_versioning_create_versioned_url_prefix_with_trailing_slash_returns_formatted_prefix(
        self,
    ):
        """末尾スラッシュ付きURL prefixのテスト."""
        assert (
            create_versioned_url_prefix("/api/stocks/", "v1")
            == "/api/v1/stocks/"
        )
        assert (
            create_versioned_url_prefix("/api/bulk-data/", "v2")
            == "/api/v2/bulk-data/"
        )

    def test_versioning_create_versioned_url_prefix_edge_cases_with_minimal_paths_returns_formatted_prefix(
        self,
    ):
        """URL prefix作成のエッジケースのテスト."""
        assert create_versioned_url_prefix("/api", "v1") == "/api/v1"
        assert create_versioned_url_prefix("/", "v1") == "/v1"
        assert create_versioned_url_prefix("", "v1") == "/v1"


@pytest.fixture
def app():
    """テスト用Flaskアプリケーション."""
    app = Flask(__name__)
    app.config["TESTING"] = True
    return app


@pytest.fixture
def client(app):
    """テスト用クライアント."""
    return app.test_client()


class TestAPIVersioningIntegration:
    """APIバージョニングの統合テスト."""

    def test_versioning_middleware_integration_with_versioned_endpoints_returns_correct_version(
        self, app, client
    ):
        """ミドルウェア統合テスト."""
        APIVersioningMiddleware(app)

        @app.route("/api/v1/test")
        def test_v1():
            from flask import request

            return {"version": request.api_version}

        @app.route("/api/test")
        def test_default():
            from flask import request

            return {"version": request.api_version}

        # バージョン付きエンドポイントのテスト
        response = client.get("/api/v1/test")
        assert response.status_code == 200
        data = response.get_json()
        assert data["version"] == "v1"

        # デフォルトエンドポイントのテスト
        response = client.get("/api/test")
        assert response.status_code == 200
        data = response.get_json()
        assert data["version"] == "v1"

    def test_versioning_multiple_versions_with_different_endpoints_returns_correct_version_data(
        self, app, client
    ):
        """複数バージョンのテスト."""
        app.config["API_SUPPORTED_VERSIONS"] = ["v1", "v2"]
        APIVersioningMiddleware(app)

        @app.route("/api/v1/test")
        def test_v1():
            from flask import request

            return {"version": request.api_version, "endpoint": "v1"}

        @app.route("/api/v2/test")
        def test_v2():
            from flask import request

            return {"version": request.api_version, "endpoint": "v2"}

        # v1エンドポイントのテスト
        response = client.get("/api/v1/test")
        assert response.status_code == 200
        data = response.get_json()
        assert data["version"] == "v1"
        assert data["endpoint"] == "v1"

        # v2エンドポイントのテスト
        response = client.get("/api/v2/test")
        assert response.status_code == 200
        data = response.get_json()
        assert data["version"] == "v2"
        assert data["endpoint"] == "v2"
