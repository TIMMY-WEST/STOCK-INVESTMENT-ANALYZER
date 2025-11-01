"""Swagger UI統合テストモジュール.

このモジュールは、Swagger UIとメインアプリケーションの統合をテストします。
"""

import json
from unittest.mock import patch

import pytest
import requests

from app.app import app as main_app


pytestmark = pytest.mark.integration


class TestSwaggerIntegration:
    """Swagger UI統合テストクラス."""

    @pytest.fixture
    def app(self):
        """メインアプリケーションのテスト設定."""
        main_app.config["TESTING"] = True
        return main_app

    @pytest.fixture
    def client(self, app):
        """テスト用クライアント."""
        return app.test_client()

    def test_swagger_ui_integration_with_main_app(self, client):
        """メインアプリケーションとのSwagger UI統合テスト."""
        # Arrange (準備)
        # テストクライアントを使用

        # Act (実行)
        response = client.get("/api/docs/")
        html_content = response.get_data(as_text=True)

        # Assert (検証)
        assert response.status_code == 200
        assert response.content_type.startswith("text/html")
        assert "swagger-ui" in html_content
        assert "/api/docs/openapi.json" in html_content

    def test_openapi_spec_reflects_actual_endpoints(self, client):
        """OpenAPI仕様書が実際のエンドポイントを反映しているかテスト."""
        # Arrange (準備)
        test_endpoints = [
            ("/api/stocks", "GET"),
            ("/api/fetch-data", "POST"),
            ("/api/bulk-data/jobs", "POST"),
            ("/api/stock-master/stocks", "GET"),
            ("/api/system/health-check", "GET"),
        ]

        # Act (実行)
        spec_response = client.get("/api/docs/openapi.json")
        openapi_spec = spec_response.get_json()
        defined_paths = set(openapi_spec["paths"].keys())

        # Assert (検証)
        assert spec_response.status_code == 200

        for endpoint, method in test_endpoints:
            assert endpoint in defined_paths or any(
                endpoint.replace("/api/", "/api/v1/") in path
                for path in defined_paths
            )

            if method == "GET":
                response = client.get(endpoint)
                assert response.status_code != 404

    def test_openapi_spec_server_urls_dynamic_setting(self, client):
        """OpenAPI仕様書のサーバーURL動的設定テスト."""
        # Arrange (準備)
        # テストクライアントを使用

        # Act (実行)
        response = client.get("/api/docs/openapi.json")
        openapi_spec = response.get_json()
        servers = openapi_spec["servers"]
        server_urls = [server["url"] for server in servers]

        # Assert (検証)
        assert "servers" in openapi_spec
        assert len(servers) > 0
        assert any(url for url in server_urls)

    def test_swagger_ui_with_different_environments(self, client):
        """異なる環境でのSwagger UI動作テスト."""
        # Arrange (準備)
        # テストクライアントを使用

        # Act (実行) & Assert (検証) - 開発環境
        with patch.dict("os.environ", {"FLASK_ENV": "development"}):
            response = client.get("/api/docs/")
            assert response.status_code == 200

        # Act (実行) & Assert (検証) - 本番環境
        with patch.dict("os.environ", {"FLASK_ENV": "production"}):
            response = client.get("/api/docs/")
            assert response.status_code == 200

    def test_openapi_spec_validation_against_actual_responses(self, client):
        """OpenAPI仕様書と実際のレスポンスの整合性テスト."""
        # Arrange (準備)
        expected_fields = ["status", "timestamp"]

        # Act (実行)
        spec_response = client.get("/api/docs/openapi.json")
        health_response = client.get("/api/system/health-check")

        # Assert (検証)
        assert spec_response.status_code == 200

        if health_response.status_code == 200:
            health_data = health_response.get_json()
            assert isinstance(health_data, dict)

            for field in expected_fields:
                if field in health_data:
                    assert health_data[field] is not None

    def test_swagger_ui_accessibility(self, client):
        """Swagger UIのアクセシビリティテスト."""
        # Arrange (準備)
        # テストクライアントを使用

        # Act (実行)
        response = client.get("/api/docs/")
        html_content = response.get_data(as_text=True)

        # Assert (検証)
        assert 'lang="ja"' in html_content
        assert "<title>" in html_content
        assert 'meta name="viewport"' in html_content

    def test_swagger_ui_performance(self, client):
        """Swagger UIのパフォーマンステスト."""
        # Arrange (準備)
        import time

        # Act (実行)
        start_time = time.time()
        response = client.get("/api/docs/")
        end_time = time.time()
        response_time = end_time - start_time

        # Assert (検証)
        assert response_time < 5.0
        assert response.status_code == 200

    def test_openapi_json_performance(self, client):
        """Test OpenAPI JSON generation performance."""
        # Arrange (準備)
        import time

        # Act (実行)
        start_time = time.time()
        response = client.get("/api/docs/openapi.json")
        end_time = time.time()
        response_time = end_time - start_time
        json_data = response.get_json()
        json_str = json.dumps(json_data)
        json_size = len(json_str.encode("utf-8"))

        # Assert (検証)
        assert response_time < 3.0
        assert response.status_code == 200
        assert 10000 < json_size < 1000000

    def test_swagger_ui_error_handling_integration(self, client):
        """Swagger UIのエラーハンドリング統合テスト."""
        # Arrange (準備)
        # テストクライアントを使用

        # Act (実行) & Assert (検証) - 存在しないエンドポイント
        response = client.get("/api/docs/invalid-endpoint")
        assert response.status_code == 404

        # Act (実行) & Assert (検証) - 不正なメソッド
        response = client.post("/api/docs/")
        assert response.status_code in [404, 405]

    def test_swagger_ui_caching_headers(self, client):
        """Swagger UIのキャッシュヘッダーテスト."""
        # Arrange (準備)
        # テストクライアントを使用

        # Act (実行)
        response = client.get("/api/docs/")

        # Assert (検証)
        if "Cache-Control" in response.headers:
            cache_control = response.headers["Cache-Control"]
            assert "no-cache" in cache_control or "max-age" in cache_control

    def test_openapi_spec_consistency_across_requests(self, client):
        """OpenAPI仕様書の複数リクエスト間での一貫性テスト."""
        # Arrange (準備)
        # テストクライアントを使用

        # Act (実行)
        response1 = client.get("/api/docs/openapi.json")
        response2 = client.get("/api/docs/openapi.json")
        spec1 = response1.get_json()
        spec2 = response2.get_json()

        # Assert (検証)
        assert response1.status_code == 200
        assert response2.status_code == 200
        assert spec1["openapi"] == spec2["openapi"]
        assert spec1["info"] == spec2["info"]
        assert len(spec1["paths"]) == len(spec2["paths"])

    def test_swagger_ui_with_api_versioning(self, client):
        """APIバージョニングとSwagger UIの統合テスト."""
        # Arrange (準備)
        http_methods = ["get", "post", "put", "delete", "patch"]

        # Act (実行)
        response = client.get("/api/docs/openapi.json")
        openapi_spec = response.get_json()
        paths = openapi_spec["paths"]
        v1_paths = [path for path in paths.keys() if "/v1/" in path]

        # Assert (検証)
        assert len(v1_paths) > 0

        for path in v1_paths:
            path_info = paths[path]
            defined_methods = [
                method for method in http_methods if method in path_info
            ]
            assert len(defined_methods) > 0
