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


# module-level marker so pytest -m unit picks these up
pytestmark = pytest.mark.unit


class TestAPIVersioningMiddleware:
    """APIVersioningMiddlewareクラスのテスト."""

    def test_init_with_app_with_valid_app_returns_initialized_middleware(self):
        """アプリケーションとの初期化テスト."""
        # Arrange (準備)
        app = Flask(__name__)

        # Act (実行)
        middleware = APIVersioningMiddleware(app)

        # Assert (検証)
        assert middleware.app == app
        assert middleware.default_version == "v1"
        assert middleware.supported_versions == ["v1"]

    def test_init_with_custom_config_with_valid_config_returns_configured_middleware(
        self,
    ):
        """カスタム設定での初期化テスト."""
        # Arrange (準備)
        app = Flask(__name__)
        app.config["API_DEFAULT_VERSION"] = "v2"
        app.config["API_SUPPORTED_VERSIONS"] = ["v1", "v2", "v3"]

        # Act (実行)
        middleware = APIVersioningMiddleware(app)

        # Assert (検証)
        assert middleware.default_version == "v2"
        assert middleware.supported_versions == ["v1", "v2", "v3"]

    def test_versioning_middleware_init_without_app_with_no_parameters_returns_default_configuration(
        self,
    ):
        """アプリケーションなしでの初期化テスト."""
        # Arrange (準備)
        # パラメータなしでミドルウェアを作成

        # Act (実行)
        middleware = APIVersioningMiddleware()

        # Assert (検証)
        assert middleware.app is None
        assert middleware.default_version == "v1"
        assert middleware.supported_versions == ["v1"]

    def test_versioning_middleware_init_app_method_with_configured_app_returns_initialized_middleware(
        self,
    ):
        """init_appメソッドのテスト."""
        # Arrange (準備)
        app = Flask(__name__)
        app.config["API_DEFAULT_VERSION"] = "v2"
        app.config["API_SUPPORTED_VERSIONS"] = ["v1", "v2"]
        middleware = APIVersioningMiddleware()

        # Act (実行)
        middleware.init_app(app)

        # Assert (検証)
        assert middleware.app == app
        assert middleware.default_version == "v2"
        assert middleware.supported_versions == ["v1", "v2"]

    @patch("app.middleware.versioning.request")
    def test_before_request_with_versioned_path_with_valid_version_returns_processed_request(
        self, mock_request
    ):
        """バージョン付きパスでのbefore_requestテスト."""
        # Arrange (準備)
        app = Flask(__name__)
        middleware = APIVersioningMiddleware(app)
        mock_request.path = "/api/v2/stocks"

        # Act (実行)
        with app.app_context():
            middleware.before_request()

        # Assert (検証)
        assert mock_request.api_version == "v2"

    @patch("app.middleware.versioning.request")
    def test_before_request_with_non_versioned_path_with_default_path_returns_unmodified_request(
        self, mock_request
    ):
        """バージョンなしパスでのbefore_requestテスト."""
        # Arrange (準備)
        app = Flask(__name__)
        middleware = APIVersioningMiddleware(app)
        mock_request.path = "/api/stocks"

        # Act (実行)
        with app.app_context():
            middleware.before_request()

        # Assert (検証)
        assert mock_request.api_version == "v1"  # デフォルトバージョン

    @patch("app.middleware.versioning.request")
    def test_before_request_with_non_api_path_with_static_path_returns_unmodified_request(
        self, mock_request
    ):
        """API以外のパスでのbefore_requestテスト."""
        # Arrange (準備)
        app = Flask(__name__)
        middleware = APIVersioningMiddleware(app)
        mock_request.path = "/home"

        # Act (実行)
        with app.app_context():
            middleware.before_request()

        # Assert (検証)
        assert mock_request.api_version == "v1"  # デフォルトバージョン


class TestParseApiVersion:
    """parse_api_version関数のテスト."""

    def test_parse_api_version_from_path_with_valid_versioned_paths_returns_correct_version(
        self,
    ):
        """パスからのバージョン解析テスト."""
        # Arrange (準備)
        # テスト対象のパスを準備

        # Act (実行)
        result1 = parse_api_version("/api/v1/stocks")
        result2 = parse_api_version("/api/v2/bulk-data")
        result3 = parse_api_version("/api/v10/system")

        # Assert (検証)
        assert result1 == "v1"
        assert result2 == "v2"
        assert result3 == "v10"

    def test_parse_api_version_without_version_with_unversioned_paths_returns_none(
        self,
    ):
        """バージョンなしパスの解析テスト."""
        # Arrange (準備)
        # テスト対象のパスを準備

        # Act (実行)
        result1 = parse_api_version("/api/stocks")
        result2 = parse_api_version("/api/bulk-data")
        result3 = parse_api_version("/api/system")

        # Assert (検証)
        assert result1 is None
        assert result2 is None
        assert result3 is None

    def test_parse_api_version_non_api_path_with_static_paths_returns_none(
        self,
    ):
        """API以外のパスの解析テスト."""
        # Arrange (準備)
        # テスト対象のパスを準備

        # Act (実行)
        result1 = parse_api_version("/home")
        result2 = parse_api_version("/about")
        result3 = parse_api_version("/")

        # Assert (検証)
        assert result1 is None
        assert result2 is None
        assert result3 is None

    def test_parse_api_version_invalid_format_with_malformed_paths_returns_none(
        self,
    ):
        """無効なフォーマットのテスト."""
        # Arrange (準備)
        # テスト対象のパスを準備

        # Act (実行)
        result1 = parse_api_version("/api/version1/stocks")
        result2 = parse_api_version("/api/1/stocks")
        result3 = parse_api_version("/api/v/stocks")

        # Assert (検証)
        assert result1 is None
        assert result2 is None
        assert result3 is None

    def test_parse_api_version_edge_cases_with_empty_paths_returns_none(self):
        """エッジケースのテスト."""
        # Arrange (準備)
        # テスト対象のパスを準備

        # Act (実行)
        result1 = parse_api_version("")
        result2 = parse_api_version("/")
        result3 = parse_api_version("/api")
        result4 = parse_api_version("/api/")

        # Assert (検証)
        assert result1 is None
        assert result2 is None
        assert result3 is None
        assert result4 is None


class TestVersioningHelpers:
    """バージョニングヘルパー関数のテスト."""

    def test_versioning_create_versioned_blueprint_name_with_valid_inputs_returns_formatted_name(
        self,
    ):
        """バージョン付きBlueprint名作成のテスト."""
        # Arrange (準備)
        # テスト対象のパラメータを準備

        # Act (実行)
        result1 = create_versioned_blueprint_name("api", "v1")
        result2 = create_versioned_blueprint_name("bulk_api", "v2")
        result3 = create_versioned_blueprint_name("stock_master", "v10")

        # Assert (検証)
        assert result1 == "api_v1"
        assert result2 == "bulk_api_v2"
        assert result3 == "stock_master_v10"

    def test_versioning_create_versioned_url_prefix_with_valid_paths_returns_formatted_prefix(
        self,
    ):
        """バージョン付きURL prefix作成のテスト."""
        # Arrange (準備)
        # テスト対象のパラメータを準備

        # Act (実行)
        result1 = create_versioned_url_prefix("/api/stocks", "v1")
        result2 = create_versioned_url_prefix("/api/bulk-data", "v2")
        result3 = create_versioned_url_prefix("/api/system", "v10")

        # Assert (検証)
        assert result1 == "/api/v1/stocks"
        assert result2 == "/api/v2/bulk-data"
        assert result3 == "/api/v10/system"

    def test_versioning_create_versioned_url_prefix_with_trailing_slash_returns_formatted_prefix(
        self,
    ):
        """末尾スラッシュ付きURL prefixのテスト."""
        # Arrange (準備)
        # テスト対象のパラメータを準備

        # Act (実行)
        result1 = create_versioned_url_prefix("/api/stocks/", "v1")
        result2 = create_versioned_url_prefix("/api/bulk-data/", "v2")

        # Assert (検証)
        assert result1 == "/api/v1/stocks/"
        assert result2 == "/api/v2/bulk-data/"

    def test_versioning_create_versioned_url_prefix_edge_cases_with_minimal_paths_returns_formatted_prefix(
        self,
    ):
        """URL prefix作成のエッジケースのテスト."""
        # Arrange (準備)
        # テスト対象のパラメータを準備

        # Act (実行)
        result1 = create_versioned_url_prefix("/api", "v1")
        result2 = create_versioned_url_prefix("/", "v1")
        result3 = create_versioned_url_prefix("", "v1")

        # Assert (検証)
        assert result1 == "/api/v1"
        assert result2 == "/v1"
        assert result3 == "/v1"


# Note: app と client フィクスチャは tests/conftest.py で定義されています
# ただし、このテストはミドルウェアテスト専用の独自のアプリが必要なため、
# 専用フィクスチャを保持します


@pytest.fixture
def app():
    """テスト用Flaskアプリケーション（バージョニングミドルウェアテスト専用）."""
    app = Flask(__name__)
    app.config["TESTING"] = True
    return app


@pytest.fixture
def client(app):
    """テスト用クライアント（バージョニングミドルウェアテスト専用）."""
    return app.test_client()


class TestAPIVersioningIntegration:
    """APIバージョニングの統合テスト."""

    def test_versioning_middleware_integration_with_versioned_endpoints_returns_correct_version(
        self, app, client
    ):
        """ミドルウェア統合テスト."""
        # Arrange (準備)
        APIVersioningMiddleware(app)

        @app.route("/api/v1/test")
        def test_v1():
            from flask import request

            return {"version": request.api_version}

        @app.route("/api/test")
        def test_default():
            from flask import request

            return {"version": request.api_version}

        # Act (実行)
        response_v1 = client.get("/api/v1/test")
        data_v1 = response_v1.get_json()
        response_default = client.get("/api/test")
        data_default = response_default.get_json()

        # Assert (検証)
        assert response_v1.status_code == 200
        assert data_v1["version"] == "v1"
        assert response_default.status_code == 200
        assert data_default["version"] == "v1"

    def test_versioning_multiple_versions_with_different_endpoints_returns_correct_version_data(
        self, app, client
    ):
        """複数バージョンのテスト."""
        # Arrange (準備)
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

        # Act (実行)
        response_v1 = client.get("/api/v1/test")
        data_v1 = response_v1.get_json()
        response_v2 = client.get("/api/v2/test")
        data_v2 = response_v2.get_json()

        # Assert (検証)
        assert response_v1.status_code == 200
        assert data_v1["version"] == "v1"
        assert data_v1["endpoint"] == "v1"
        assert response_v2.status_code == 200
        assert data_v2["version"] == "v2"
        assert data_v2["endpoint"] == "v2"
