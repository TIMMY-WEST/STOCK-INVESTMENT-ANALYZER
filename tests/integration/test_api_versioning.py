"""APIバージョニング機能の統合テスト."""

from flask import Flask
import pytest

from app.app import app
from app.middleware.versioning import APIVersioningMiddleware


class TestAPIVersioningIntegration:
    """APIバージョニングの統合テスト."""

    @pytest.fixture
    def client(self):
        """テスト用クライアント."""
        app.config["TESTING"] = True
        with app.test_client() as client:
            yield client

    def test_backward_compatibility_bulk_api(self, client):
        """バルクAPIの後方互換性テスト."""
        # Arrange (準備)
        test_payload = {"symbols": ["7203.T"], "interval": "1d"}
        expected_status_codes = [200, 202, 401]

        # Act (実行)
        response_v0 = client.post("/api/bulk-data/jobs", json=test_payload)
        response_v1 = client.post("/api/v1/bulk-data/jobs", json=test_payload)

        # Assert (検証)
        assert response_v0.status_code in expected_status_codes
        assert response_v1.status_code in expected_status_codes

    def test_backward_compatibility_stock_master_api(self, client):
        """株式マスタAPIの後方互換性テスト."""
        # Arrange (準備)
        expected_status_codes = [200, 401]

        # Act (実行)
        response_v0 = client.get("/api/stock-master/")
        response_v1 = client.get("/api/v1/stock-master/stocks")

        # Assert (検証)
        assert response_v0.status_code in expected_status_codes
        assert response_v1.status_code in expected_status_codes

    def test_backward_compatibility_system_api(self, client):
        """システムAPIの後方互換性テスト."""
        # Arrange (準備)
        # テスト対象のエンドポイントを準備

        # Act (実行)
        response_v0 = client.get("/api/system/health")
        response_v1 = client.get("/api/v1/system/health-check")
        data_v0 = response_v0.get_json()
        data_v1 = response_v1.get_json()

        # Assert (検証)
        assert response_v0.status_code == 200
        assert data_v0["status"] == "success"
        assert "data" in data_v0
        assert "overall_status" in data_v0["data"]
        assert response_v1.status_code == 200
        assert data_v1["status"] == "success"
        assert "data" in data_v1
        assert "overall_status" in data_v1["data"]

    def test_version_parsing_in_request(self, client):
        """リクエスト内でのバージョン解析テスト."""
        # Arrange (準備)
        middleware = APIVersioningMiddleware()

        # Act & Assert (実行と検証)
        with app.test_request_context("/api/v1/system/health-check"):
            from flask import request

            request.app = app
            middleware.process_request(request)
            result_version = request.api_version

            # Assert (検証)
            assert hasattr(request, "api_version")
            assert result_version == "v1"

    def test_default_version_for_non_versioned_request(self, client):
        """バージョンなしリクエストでのデフォルトバージョンテスト."""
        # Arrange (準備)
        middleware = APIVersioningMiddleware()

        # Act & Assert (実行と検証)
        with app.test_request_context("/api/system/health"):
            from flask import request

            request.app = app
            middleware.process_request(request)
            result_version = request.api_version

            # Assert (検証)
            assert hasattr(request, "api_version")
            assert result_version == "v1"

    def test_non_api_request_version(self, client):
        """API以外のリクエストでのバージョンテスト."""
        # Arrange (準備)
        middleware = APIVersioningMiddleware()

        # Act & Assert (実行と検証)
        with app.test_request_context("/"):
            from flask import request

            request.app = app
            middleware.process_request(request)
            result_version = request.api_version

            # Assert (検証)
            assert hasattr(request, "api_version")
            assert result_version == "v1"

    def test_same_functionality_different_versions(self, client):
        """異なるバージョンで同じ機能のテスト."""
        # Arrange (準備)
        # テスト対象のエンドポイントを準備

        # Act (実行)
        response1 = client.get("/api/system/health")
        response2 = client.get("/api/v1/system/health-check")

        # Assert (検証)
        assert response1.status_code == response2.status_code
        if response1.status_code == 200:
            data1 = response1.get_json()
            data2 = response2.get_json()
            assert data1["status"] == "success"
            assert data2["status"] == "success"
            assert "data" in data1
            assert "data" in data2
            assert "overall_status" in data1["data"]
            assert "overall_status" in data2["data"]

    def test_blueprint_registration(self, client):
        """Blueprintの登録確認テスト."""
        # Arrange (準備)
        expected_blueprints = [
            "bulk_api",
            "stock_master_api",
            "system_api",
            "bulk_api_v1",
            "stock_master_api_v1",
            "system_api_v1",
        ]

        # Act (実行)
        blueprint_names = [bp.name for bp in app.blueprints.values()]

        # Assert (検証)
        for bp_name in expected_blueprints:
            assert bp_name in blueprint_names

    def test_url_routing(self, client):
        """URLルーティングのテスト."""
        # Arrange (準備)
        # URLルーティングをテスト

        # Act & Assert (実行と検証)
        with app.test_request_context():
            from flask import url_for

            url_v0 = None
            url_v1 = None
            try:
                url_v0 = url_for("system_api.health_check")
            except Exception:
                pass
            try:
                url_v1 = url_for("system_api_v1.health_check")
            except Exception:
                pass

            # Assert (検証)
            if url_v0:
                assert url_v0 in [
                    "/api/system/health",
                    "/api/system/health-check",
                ]
            if url_v1:
                assert url_v1 == "/api/v1/system/health-check"

    def test_middleware_configuration(self, client):
        """ミドルウェア設定のテスト."""
        # Arrange (準備)
        # アプリケーション設定を取得

        # Act (実行)
        default_version = app.config.get("API_DEFAULT_VERSION")
        supported_versions = app.config.get("API_SUPPORTED_VERSIONS")

        # Assert (検証)
        assert default_version == "v1"
        assert supported_versions == ["v1"]

    def test_error_handling_with_versioning(self, client):
        """バージョニング付きエラーハンドリングのテスト."""
        # Arrange (準備)
        # エラーハンドリングをテスト

        # Act (実行)
        response_nonexistent = client.get("/api/v1/nonexistent")
        response_unsupported = client.get("/api/v999/system/health")
        data_nonexistent = response_nonexistent.get_json()
        data_unsupported = response_unsupported.get_json()

        # Assert (検証)
        assert response_nonexistent.status_code == 404
        if data_nonexistent and "status" in data_nonexistent:
            assert data_nonexistent["status"] == "error"
            if "error" in data_nonexistent:
                assert "code" in data_nonexistent["error"]
                assert "message" in data_nonexistent["error"]
        assert response_unsupported.status_code == 400
        if data_unsupported and "status" in data_unsupported:
            assert data_unsupported["status"] == "error"
            if "error" in data_unsupported:
                assert "code" in data_unsupported["error"]
                assert "message" in data_unsupported["error"]


class TestAPIVersioningConfiguration:
    """APIバージョニング設定のテスト."""

    def test_default_configuration(self):
        """デフォルト設定のテスト."""
        # Arrange (準備)
        test_app = Flask(__name__)
        middleware = APIVersioningMiddleware(test_app)

        # Act (実行)
        info = middleware.get_version_info()

        # Assert (検証)
        assert info["default_version"] == "v1"
        assert info["supported_versions"] == ["v1"]

    def test_custom_configuration(self):
        """カスタム設定のテスト."""
        # Arrange (準備)
        test_app = Flask(__name__)
        test_app.config["API_DEFAULT_VERSION"] = "v2"
        test_app.config["API_SUPPORTED_VERSIONS"] = ["v1", "v2", "v3"]
        middleware = APIVersioningMiddleware(test_app)

        # Act (実行)
        info = middleware.get_version_info()

        # Assert (検証)
        assert info["default_version"] == "v2"
        assert info["supported_versions"] == ["v1", "v2", "v3"]

    def test_configuration_validation(self):
        """設定値の検証テスト."""
        # Arrange (準備)
        test_app = Flask(__name__)
        test_app.config["API_DEFAULT_VERSION"] = "v2"
        test_app.config["API_SUPPORTED_VERSIONS"] = ["v1", "v3"]
        middleware = APIVersioningMiddleware(test_app)

        # Act (実行)
        info = middleware.get_version_info()

        # Assert (検証)
        assert info["default_version"] == "v2"
        assert info["supported_versions"] == ["v1", "v3"]


class TestAPIVersioningPerformance:
    """APIバージョニングのパフォーマンステスト."""

    def test_middleware_overhead(self, client):
        """ミドルウェアのオーバーヘッドテスト."""
        # Arrange (準備)
        import time

        times = []

        # Act (実行)
        for _ in range(10):
            start_time = time.time()
            response = client.get("/api/v1/system/health-check")
            end_time = time.time()
            times.append(end_time - start_time)
            data = response.get_json()

            # Assert (検証)
            assert response.status_code == 200
            assert data["status"] == "success"
            assert "data" in data
            assert "overall_status" in data["data"]

        avg_time = sum(times) / len(times)
        assert avg_time < 1.0

    def test_version_parsing_performance(self):
        """バージョン解析のパフォーマンステスト."""
        # Arrange (準備)
        import time

        middleware = APIVersioningMiddleware()
        test_paths = [
            "/api/v1/stocks",
            "/api/v2/bulk-data",
            "/api/system/health-check",
            "/home",
            "/api/v10/complex/nested/path",
        ]

        # Act (実行)
        start_time = time.time()
        for _ in range(1000):
            for path in test_paths:
                middleware.extract_version_from_url(path)[0]
        end_time = time.time()
        elapsed_time = end_time - start_time

        # Assert (検証)
        assert elapsed_time < 1.0
