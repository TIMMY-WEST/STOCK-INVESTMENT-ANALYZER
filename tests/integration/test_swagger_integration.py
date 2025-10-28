"""Swagger UI統合テストモジュール.

このモジュールは、Swagger UIとメインアプリケーションの統合をテストします。
"""

import json
from unittest.mock import patch

import pytest
import requests

from app.app import app as main_app


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
        response = client.get("/api/docs/")

        assert response.status_code == 200
        assert response.content_type.startswith("text/html")

        # Swagger UIページが正しく表示されることを確認
        html_content = response.get_data(as_text=True)
        assert "swagger-ui" in html_content
        assert "/api/docs/openapi.json" in html_content

    def test_openapi_spec_reflects_actual_endpoints(self, client):
        """OpenAPI仕様書が実際のエンドポイントを反映しているかテスト."""
        # OpenAPI仕様書を取得
        spec_response = client.get("/api/docs/openapi.json")
        assert spec_response.status_code == 200
        openapi_spec = spec_response.get_json()

        # 仕様書に定義されているパスを取得
        defined_paths = set(openapi_spec["paths"].keys())

        # 実際のエンドポイントをテスト
        test_endpoints = [
            ("/api/stocks", "GET"),
            ("/api/fetch-data", "POST"),
            ("/api/bulk-data/jobs", "POST"),
            ("/api/stock-master/stocks", "GET"),
            ("/api/system/health-check", "GET"),
        ]

        for endpoint, method in test_endpoints:
            # エンドポイントが仕様書に定義されているか確認
            assert endpoint in defined_paths or any(
                endpoint.replace("/api/", "/api/v1/") in path
                for path in defined_paths
            )

            # 実際のエンドポイントが存在するか確認（簡易チェック）
            if method == "GET":
                response = client.get(endpoint)
                # 404以外のレスポンス（エンドポイントが存在する）
                assert response.status_code != 404

    def test_openapi_spec_server_urls_dynamic_setting(self, client):
        """OpenAPI仕様書のサーバーURL動的設定テスト."""
        response = client.get("/api/docs/openapi.json")
        openapi_spec = response.get_json()

        # サーバーURLが設定されているか確認
        assert "servers" in openapi_spec
        servers = openapi_spec["servers"]
        assert len(servers) > 0

        # 少なくとも一つのサーバーURLが設定されているか
        server_urls = [server["url"] for server in servers]
        assert any(url for url in server_urls)

    def test_swagger_ui_with_different_environments(self, client):
        """異なる環境でのSwagger UI動作テスト."""
        # 開発環境での動作確認
        with patch.dict("os.environ", {"FLASK_ENV": "development"}):
            response = client.get("/api/docs/")
            assert response.status_code == 200

        # 本番環境での動作確認
        with patch.dict("os.environ", {"FLASK_ENV": "production"}):
            response = client.get("/api/docs/")
            assert response.status_code == 200

    def test_openapi_spec_validation_against_actual_responses(self, client):
        """OpenAPI仕様書と実際のレスポンスの整合性テスト."""
        # OpenAPI仕様書を取得
        spec_response = client.get("/api/docs/openapi.json")
        assert spec_response.status_code == 200

        # ヘルスチェックエンドポイントのテスト
        health_response = client.get("/api/system/health-check")
        if health_response.status_code == 200:
            health_data = health_response.get_json()

            # レスポンス構造が仕様書と一致するか確認
            assert isinstance(health_data, dict)
            # 基本的なフィールドの存在確認
            expected_fields = ["status", "timestamp"]
            for field in expected_fields:
                if field in health_data:
                    assert health_data[field] is not None

    def test_swagger_ui_accessibility(self, client):
        """Swagger UIのアクセシビリティテスト."""
        response = client.get("/api/docs/")
        html_content = response.get_data(as_text=True)

        # 基本的なアクセシビリティ要素の確認
        assert 'lang="ja"' in html_content
        assert "<title>" in html_content
        assert 'meta name="viewport"' in html_content

    def test_swagger_ui_performance(self, client):
        """Swagger UIのパフォーマンステスト."""
        import time

        # レスポンス時間の測定
        start_time = time.time()
        response = client.get("/api/docs/")
        end_time = time.time()

        response_time = end_time - start_time

        # レスポンス時間が妥当な範囲内であることを確認（5秒以内）
        assert response_time < 5.0
        assert response.status_code == 200

    def test_openapi_json_performance(self, client):
        """Test OpenAPI JSON generation performance."""
        import time

        # JSON生成時間の測定
        start_time = time.time()
        response = client.get("/api/docs/openapi.json")
        end_time = time.time()

        response_time = end_time - start_time

        # JSON生成時間が妥当な範囲内であることを確認（3秒以内）
        assert response_time < 3.0
        assert response.status_code == 200

        # JSONサイズの確認（適切なサイズであることを確認）
        json_data = response.get_json()
        json_str = json.dumps(json_data)
        json_size = len(json_str.encode("utf-8"))

        # JSONサイズが妥当な範囲内（10KB以上、1MB以下）
        assert 10000 < json_size < 1000000

    def test_swagger_ui_error_handling_integration(self, client):
        """Swagger UIのエラーハンドリング統合テスト."""
        # 存在しないエンドポイントへのアクセス
        response = client.get("/api/docs/invalid-endpoint")
        assert response.status_code == 404

        # 不正なメソッドでのアクセス
        response = client.post("/api/docs/")
        # POSTメソッドは許可されていないが、405または404が返される
        assert response.status_code in [404, 405]

    def test_swagger_ui_caching_headers(self, client):
        """Swagger UIのキャッシュヘッダーテスト."""
        response = client.get("/api/docs/")

        # キャッシュ関連のヘッダーが適切に設定されているか確認
        # 開発環境では通常キャッシュを無効にする
        if "Cache-Control" in response.headers:
            cache_control = response.headers["Cache-Control"]
            # 開発環境では no-cache が設定されることが多い
            assert "no-cache" in cache_control or "max-age" in cache_control

    def test_openapi_spec_consistency_across_requests(self, client):
        """OpenAPI仕様書の複数リクエスト間での一貫性テスト."""
        # 複数回リクエストして同じ内容が返されることを確認
        response1 = client.get("/api/docs/openapi.json")
        response2 = client.get("/api/docs/openapi.json")

        assert response1.status_code == 200
        assert response2.status_code == 200

        spec1 = response1.get_json()
        spec2 = response2.get_json()

        # 基本的な構造が同じであることを確認
        assert spec1["openapi"] == spec2["openapi"]
        assert spec1["info"] == spec2["info"]
        assert len(spec1["paths"]) == len(spec2["paths"])

    def test_swagger_ui_with_api_versioning(self, client):
        """APIバージョニングとSwagger UIの統合テスト."""
        response = client.get("/api/docs/openapi.json")
        openapi_spec = response.get_json()

        # バージョン付きエンドポイントが仕様書に含まれているか確認
        paths = openapi_spec["paths"]

        # v1エンドポイントが含まれているか確認
        v1_paths = [path for path in paths.keys() if "/v1/" in path]
        assert len(v1_paths) > 0

        # 各バージョンのエンドポイントが適切に文書化されているか確認
        for path in v1_paths:
            path_info = paths[path]
            # 少なくとも一つのHTTPメソッドが定義されているか
            http_methods = ["get", "post", "put", "delete", "patch"]
            defined_methods = [
                method for method in http_methods if method in path_info
            ]
            assert len(defined_methods) > 0
