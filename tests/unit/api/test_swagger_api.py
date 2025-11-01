"""Swagger UI APIのテストモジュール.

このモジュールは、Swagger UIとOpenAPI仕様書の提供機能をテストします。
"""

import json

from flask import Flask
import pytest
import yaml

from app.api.swagger import swagger_bp


# module-level marker so pytest -m unit picks these up
pytestmark = pytest.mark.unit


class TestSwaggerAPI:
    """Swagger UI APIのテストクラス."""

    def test_swagger_ui_page_with_request_returns_html_content(self, client):
        """Swagger UIページのテスト."""
        # Arrange (準備)

        # Act (実行)
        response = client.get("/api/docs/")

        # Assert (検証)
        assert response.status_code == 200
        assert response.content_type.startswith("text/html")

        html_content = response.get_data(as_text=True)
        assert "swagger-ui" in html_content
        assert "Stock Investment Analyzer API Documentation" in html_content
        assert "SwaggerUIBundle" in html_content

    def test_swagger_openapi_json_with_request_returns_valid_spec(
        self, client
    ):
        """OpenAPI仕様書JSONエンドポイントのテスト."""
        # Arrange (準備)

        # Act (実行)
        response = client.get("/api/docs/openapi.json")

        # Assert (検証)
        assert response.status_code == 200
        assert response.content_type == "application/json"

        openapi_spec = response.get_json()
        assert openapi_spec is not None

        assert "openapi" in openapi_spec
        assert "info" in openapi_spec
        assert "paths" in openapi_spec
        assert "components" in openapi_spec

        assert openapi_spec["openapi"] == "3.0.3"
        assert openapi_spec["info"]["title"] == "Stock Investment Analyzer API"
        assert openapi_spec["info"]["version"] == "1.0.0"

    def test_swagger_openapi_yaml_with_request_returns_valid_spec(
        self, client
    ):
        """OpenAPI仕様書YAMLエンドポイントのテスト."""
        # Arrange (準備)

        # Act (実行)
        response = client.get("/api/docs/openapi.yaml")

        # Assert (検証)
        assert response.status_code == 200
        assert response.content_type == "application/x-yaml"

        yaml_content = response.get_data(as_text=True)
        openapi_spec = yaml.safe_load(yaml_content)

        assert "openapi" in openapi_spec
        assert "info" in openapi_spec
        assert "paths" in openapi_spec
        assert "components" in openapi_spec

    def test_swagger_redoc_page_with_request_returns_html_content(
        self, client
    ):
        """ReDocページのテスト."""
        # Arrange (準備)

        # Act (実行)
        response = client.get("/api/docs/redoc/")

        # Assert (検証)
        assert response.status_code == 200
        assert response.content_type.startswith("text/html")

        html_content = response.get_data(as_text=True)
        assert "redoc" in html_content
        assert (
            "Stock Investment Analyzer API Documentation - ReDoc"
            in html_content
        )
        assert "redoc.standalone.js" in html_content

    def test_swagger_docs_health_with_request_returns_healthy_status(
        self, client
    ):
        """ドキュメントサービスヘルスチェックエンドポイントのテスト."""
        # Arrange (準備)

        # Act (実行)
        response = client.get("/api/docs/health")

        # Assert (検証)
        assert response.status_code == 200
        assert response.content_type == "application/json"

        health_data = response.get_json()
        assert health_data["status"] == "success"
        assert health_data["data"]["service"] == "swagger-docs"
        assert health_data["data"]["status"] == "healthy"

    def test_swagger_openapi_spec_content_with_validation_returns_proper_structure(
        self, client
    ):
        """OpenAPI仕様書の内容詳細検証."""
        # Arrange (準備)

        # Act (実行)
        response = client.get("/api/docs/openapi.json")
        openapi_spec = response.get_json()

        # Assert (検証)
        assert "servers" in openapi_spec
        assert len(openapi_spec["servers"]) > 0

        paths = openapi_spec["paths"]

        assert "/api/stocks" in paths
        assert "/api/stocks/{stock_id}" in paths
        assert "/api/fetch-data" in paths

        assert "/api/bulk-data/jobs" in paths
        assert "/api/bulk-data/jobs/{job_id}" in paths

        assert "/api/stock-master/stocks" in paths

        assert "/api/system/health-check" in paths
        assert "/api/system/database/connection" in paths

    def test_swagger_openapi_spec_components_with_validation_returns_proper_schemas(
        self, client
    ):
        """OpenAPI仕様書のコンポーネント検証."""
        # Arrange (準備)

        # Act (実行)
        response = client.get("/api/docs/openapi.json")
        openapi_spec = response.get_json()

        # Assert (検証)
        components = openapi_spec["components"]

        assert "schemas" in components
        schemas = components["schemas"]

        assert "StockData" in schemas
        assert "StockMaster" in schemas
        assert "BulkJobStatus" in schemas
        assert "APIResponse" in schemas
        assert "ErrorResponse" in schemas
        assert "PaginatedResponse" in schemas

        assert "responses" in components
        responses = components["responses"]

        assert "Success" in responses
        assert "BadRequest" in responses
        assert "NotFound" in responses
        assert "InternalServerError" in responses

    def test_swagger_blueprint_registration_with_app_returns_proper_registration(
        self, app
    ):
        """Swagger UIブループリントの登録確認."""
        # Arrange (準備)

        # Act (実行)
        blueprint_names = [bp.name for bp in app.blueprints.values()]

        # Assert (検証)
        assert "swagger" in blueprint_names

    def test_swagger_error_handling_with_nonexistent_endpoint_returns_not_found(
        self, client
    ):
        """Swagger UIのエラーハンドリングテスト."""
        # Arrange (準備)

        # Act (実行)
        response = client.get("/api/docs/nonexistent")

        # Assert (検証)
        assert response.status_code == 404

    def test_swagger_openapi_spec_security_with_definitions_returns_proper_schemes(
        self, client
    ):
        """OpenAPI仕様書のセキュリティ定義検証."""
        # Arrange (準備)

        # Act (実行)
        response = client.get("/api/docs/openapi.json")
        openapi_spec = response.get_json()

        # Assert (検証)
        if (
            "components" in openapi_spec
            and "securitySchemes" in openapi_spec["components"]
        ):
            security_schemes = openapi_spec["components"]["securitySchemes"]
            assert isinstance(security_schemes, dict)

    def test_swagger_openapi_spec_tags_with_validation_returns_proper_tags(
        self, client
    ):
        """OpenAPI仕様書のタグ検証."""
        # Arrange (準備)

        # Act (実行)
        response = client.get("/api/docs/openapi.json")
        openapi_spec = response.get_json()

        # Assert (検証)
        assert "tags" in openapi_spec
        tags = openapi_spec["tags"]

        tag_names = [tag["name"] for tag in tags]
        assert "株価データ" in tag_names
        assert "バルクデータ" in tag_names
        assert "銘柄マスター" in tag_names
        assert "システム監視" in tag_names

    def test_swagger_content_type_headers_with_requests_returns_proper_headers(
        self, client
    ):
        """レスポンスのContent-Typeヘッダー検証."""
        # Arrange (準備)

        # Act (実行)
        response_swagger = client.get("/api/docs/")
        response_json = client.get("/api/docs/openapi.json")
        response_yaml = client.get("/api/docs/openapi.yaml")
        response_redoc = client.get("/api/docs/redoc")

        # Assert (検証)
        assert "text/html" in response_swagger.content_type
        assert response_json.content_type == "application/json"
        assert response_yaml.content_type == "application/x-yaml"
        assert "text/html" in response_redoc.content_type

    def test_swagger_openapi_spec_examples_with_validation_returns_proper_samples(
        self, client
    ):
        """OpenAPI仕様書のサンプルデータ検証."""
        # Arrange (準備)

        # Act (実行)
        response = client.get("/api/docs/openapi.json")
        openapi_spec = response.get_json()

        # Assert (検証)
        if (
            "components" in openapi_spec
            and "responses" in openapi_spec["components"]
        ):
            responses = openapi_spec["components"]["responses"]

            for _response_name, response_def in responses.items():
                if "content" in response_def:
                    for _content_type, content_def in response_def[
                        "content"
                    ].items():
                        assert (
                            "example" in content_def or "schema" in content_def
                        )


# Note: app と client フィクスチャは tests/conftest.py で定義されています
# ただし、このテストは swagger_bp のみを登録する独自のアプリが必要なため、
# 専用フィクスチャを保持します


@pytest.fixture
def app():
    """テスト用Flaskアプリケーションの作成（Swagger専用）."""
    app = Flask(__name__)
    app.config["TESTING"] = True
    app.register_blueprint(swagger_bp)
    return app


@pytest.fixture
def client(app):
    """テスト用クライアントの作成（Swagger専用アプリ用）."""
    return app.test_client()
