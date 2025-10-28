"""Swagger UI APIのテストモジュール.

このモジュールは、Swagger UIとOpenAPI仕様書の提供機能をテストします。
"""

import json

from flask import Flask
import pytest
import yaml

from app.api.swagger import swagger_bp


class TestSwaggerAPI:
    """Swagger UI APIのテストクラス."""

    def test_swagger_ui_page(self, client):
        """Swagger UIページのテスト."""
        response = client.get("/api/docs/")

        assert response.status_code == 200
        assert response.content_type.startswith("text/html")

        # HTMLコンテンツの基本的な検証
        html_content = response.get_data(as_text=True)
        assert "swagger-ui" in html_content
        assert "Stock Investment Analyzer API Documentation" in html_content
        assert "SwaggerUIBundle" in html_content

    def test_openapi_json_endpoint(self, client):
        """OpenAPI仕様書JSONエンドポイントのテスト."""
        response = client.get("/api/docs/openapi.json")

        assert response.status_code == 200
        assert response.content_type == "application/json"

        # JSONの妥当性検証
        openapi_spec = response.get_json()
        assert openapi_spec is not None

        # OpenAPI仕様書の基本構造検証
        assert "openapi" in openapi_spec
        assert "info" in openapi_spec
        assert "paths" in openapi_spec
        assert "components" in openapi_spec

        # バージョン情報の検証
        assert openapi_spec["openapi"] == "3.0.3"
        assert openapi_spec["info"]["title"] == "Stock Investment Analyzer API"
        assert openapi_spec["info"]["version"] == "1.0.0"

    def test_openapi_yaml_endpoint(self, client):
        """OpenAPI仕様書YAMLエンドポイントのテスト."""
        response = client.get("/api/docs/openapi.yaml")

        assert response.status_code == 200
        assert response.content_type == "application/x-yaml"

        # YAMLの妥当性検証
        yaml_content = response.get_data(as_text=True)
        openapi_spec = yaml.safe_load(yaml_content)

        # OpenAPI仕様書の基本構造検証
        assert "openapi" in openapi_spec
        assert "info" in openapi_spec
        assert "paths" in openapi_spec
        assert "components" in openapi_spec

    def test_redoc_page(self, client):
        """ReDocページのテスト."""
        response = client.get("/api/docs/redoc/")

        assert response.status_code == 200
        assert response.content_type.startswith("text/html")

        # HTMLコンテンツの基本的な検証
        html_content = response.get_data(as_text=True)
        assert "redoc" in html_content
        assert (
            "Stock Investment Analyzer API Documentation - ReDoc"
            in html_content
        )
        assert "redoc.standalone.js" in html_content

    def test_docs_health_endpoint(self, client):
        """ドキュメントサービスヘルスチェックエンドポイントのテスト."""
        response = client.get("/api/docs/health")

        assert response.status_code == 200
        assert response.content_type == "application/json"

        health_data = response.get_json()
        assert health_data["status"] == "success"
        assert health_data["data"]["service"] == "swagger-docs"
        assert health_data["data"]["status"] == "healthy"

    def test_openapi_spec_content_validation(self, client):
        """OpenAPI仕様書の内容詳細検証."""
        response = client.get("/api/docs/openapi.json")
        openapi_spec = response.get_json()

        # サーバー情報の検証
        assert "servers" in openapi_spec
        assert len(openapi_spec["servers"]) > 0

        # パス情報の検証（主要なエンドポイントが含まれているか）
        paths = openapi_spec["paths"]

        # 株価データAPI
        assert "/api/stocks" in paths
        assert "/api/stocks/{stock_id}" in paths
        assert "/api/fetch-data" in paths

        # バルクデータAPI
        assert "/api/bulk-data/jobs" in paths
        assert "/api/bulk-data/jobs/{job_id}" in paths

        # 銘柄マスターAPI
        assert "/api/stock-master/stocks" in paths

        # システム監視API
        assert "/api/system/health-check" in paths
        assert "/api/system/database/connection" in paths

    def test_openapi_spec_components_validation(self, client):
        """OpenAPI仕様書のコンポーネント検証."""
        response = client.get("/api/docs/openapi.json")
        openapi_spec = response.get_json()

        components = openapi_spec["components"]

        # スキーマの検証
        assert "schemas" in components
        schemas = components["schemas"]

        # 主要なスキーマが定義されているか
        assert "StockData" in schemas
        assert "StockMaster" in schemas
        assert "BulkJobStatus" in schemas
        assert "APIResponse" in schemas
        assert "ErrorResponse" in schemas
        assert "PaginatedResponse" in schemas

        # レスポンスの検証
        assert "responses" in components
        responses = components["responses"]

        # 共通レスポンスが定義されているか
        assert "Success" in responses
        assert "BadRequest" in responses
        assert "NotFound" in responses
        assert "InternalServerError" in responses

    def test_swagger_blueprint_registration(self, app):
        """Swagger UIブループリントの登録確認."""
        # ブループリントが正しく登録されているか確認
        blueprint_names = [bp.name for bp in app.blueprints.values()]
        assert "swagger" in blueprint_names

    def test_swagger_error_handling(self, client):
        """Swagger UIのエラーハンドリングテスト."""
        # 存在しないエンドポイントへのアクセス
        response = client.get("/api/docs/nonexistent")
        assert response.status_code == 404

    def test_openapi_spec_security_definitions(self, client):
        """OpenAPI仕様書のセキュリティ定義検証."""
        response = client.get("/api/docs/openapi.json")
        openapi_spec = response.get_json()

        # セキュリティスキームが定義されているか（将来の拡張のため）
        if (
            "components" in openapi_spec
            and "securitySchemes" in openapi_spec["components"]
        ):
            security_schemes = openapi_spec["components"]["securitySchemes"]
            # 現在は認証なしだが、将来的にAPIキーやJWTが追加される可能性
            assert isinstance(security_schemes, dict)

    def test_openapi_spec_tags_validation(self, client):
        """OpenAPI仕様書のタグ検証."""
        response = client.get("/api/docs/openapi.json")
        openapi_spec = response.get_json()

        # タグが定義されているか
        assert "tags" in openapi_spec
        tags = openapi_spec["tags"]

        # 主要なタグが定義されているか
        tag_names = [tag["name"] for tag in tags]
        assert "株価データ" in tag_names
        assert "バルクデータ" in tag_names
        assert "銘柄マスター" in tag_names
        assert "システム監視" in tag_names

    def test_content_type_headers(self, client):
        """レスポンスのContent-Typeヘッダー検証."""
        # Swagger UIページ
        response = client.get("/api/docs/")
        assert "text/html" in response.content_type

        # OpenAPI JSON
        response = client.get("/api/docs/openapi.json")
        assert response.content_type == "application/json"

        # OpenAPI YAML
        response = client.get("/api/docs/openapi.yaml")
        assert response.content_type == "application/x-yaml"

        # ReDoc
        response = client.get("/api/docs/redoc")
        assert "text/html" in response.content_type

    def test_openapi_spec_examples_validation(self, client):
        """OpenAPI仕様書のサンプルデータ検証."""
        response = client.get("/api/docs/openapi.json")
        openapi_spec = response.get_json()

        # レスポンスにサンプルデータが含まれているか確認
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
                        # サンプルまたはスキーマが定義されているか
                        assert (
                            "example" in content_def or "schema" in content_def
                        )


@pytest.fixture
def app():
    """テスト用Flaskアプリケーションの作成."""
    app = Flask(__name__)
    app.config["TESTING"] = True
    app.register_blueprint(swagger_bp)
    return app


@pytest.fixture
def client(app):
    """テスト用クライアントの作成."""
    return app.test_client()
