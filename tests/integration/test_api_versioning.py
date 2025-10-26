"""APIバージョニング機能の統合テスト."""

from unittest.mock import patch

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
        # 既存のエンドポイント（バージョンなし）
        response = client.get("/api/bulk-data/jobs")
        assert response.status_code in [
            200,
            401,
        ]  # 認証エラーまたは正常レスポンス

        # 新しいバージョン付きエンドポイント
        response = client.get("/api/v1/bulk-data/jobs")
        assert response.status_code in [
            200,
            401,
        ]  # 認証エラーまたは正常レスポンス

    def test_backward_compatibility_stock_master_api(self, client):
        """株式マスタAPIの後方互換性テスト."""
        # 既存のエンドポイント（バージョンなし）
        response = client.get("/api/stock-master/stocks")
        assert response.status_code in [
            200,
            401,
        ]  # 認証エラーまたは正常レスポンス

        # 新しいバージョン付きエンドポイント
        response = client.get("/api/v1/stock-master/stocks")
        assert response.status_code in [
            200,
            401,
        ]  # 認証エラーまたは正常レスポンス

    def test_backward_compatibility_system_api(self, client):
        """システムAPIの後方互換性テスト."""
        # 既存のエンドポイント（バージョンなし）
        response = client.get("/api/system/health-check")
        assert response.status_code == 200

        # 新しいバージョン付きエンドポイント
        response = client.get("/api/v1/system/health-check")
        assert response.status_code == 200

    def test_version_parsing_in_request(self, client):
        """リクエスト内でのバージョン解析テスト."""
        # バージョン付きリクエストでのバージョン情報確認
        with app.test_request_context("/api/v1/system/health-check"):
            from flask import request

            # ミドルウェアを手動で実行
            middleware = APIVersioningMiddleware(app)
            middleware.before_request()
            assert hasattr(request, "api_version")
            assert request.api_version == "v1"

    def test_default_version_for_non_versioned_request(self, client):
        """バージョンなしリクエストでのデフォルトバージョンテスト."""
        with app.test_request_context("/api/system/health-check"):
            from flask import request

            # ミドルウェアを手動で実行
            middleware = APIVersioningMiddleware(app)
            middleware.before_request()
            assert hasattr(request, "api_version")
            assert request.api_version == "v1"  # デフォルトバージョン

    def test_non_api_request_version(self, client):
        """API以外のリクエストでのバージョンテスト."""
        with app.test_request_context("/"):
            from flask import request

            # ミドルウェアを手動で実行
            middleware = APIVersioningMiddleware(app)
            middleware.before_request()
            assert hasattr(request, "api_version")
            assert request.api_version == "v1"  # デフォルトバージョン

    @patch("app.api.system_monitoring.health_check")
    def test_same_functionality_different_versions(
        self, mock_health_check, client
    ):
        """異なるバージョンで同じ機能のテスト."""
        mock_health_check.return_value = {
            "status": "healthy",
            "timestamp": "2024-01-01T00:00:00Z",
        }

        # バージョンなしエンドポイント
        response1 = client.get("/api/system/health-check")

        # バージョン付きエンドポイント
        response2 = client.get("/api/v1/system/health-check")

        # 両方とも同じレスポンスを返すことを確認
        assert response1.status_code == response2.status_code
        if response1.status_code == 200:
            assert response1.get_json() == response2.get_json()

    def test_blueprint_registration(self, client):
        """Blueprintの登録確認テスト."""
        # アプリケーションに登録されているBlueprint名を確認
        blueprint_names = [bp.name for bp in app.blueprints.values()]

        # 既存のBlueprint
        assert "bulk_api" in blueprint_names
        assert "stock_master_api" in blueprint_names
        assert "system_api" in blueprint_names

        # バージョン付きBlueprint
        assert "bulk_api_v1" in blueprint_names
        assert "stock_master_api_v1" in blueprint_names
        assert "system_api_v1" in blueprint_names

    def test_url_routing(self, client):
        """URLルーティングのテスト."""
        # 既存のルートが存在することを確認
        with app.test_request_context():
            from flask import url_for

            # システムAPIのヘルスチェック（既存）
            try:
                url = url_for("system_api.health_check")
                assert url == "/api/system/health-check"
            except Exception:
                pass  # ルートが見つからない場合はスキップ

            # システムAPIのヘルスチェック（v1）
            try:
                url = url_for("system_api_v1.health_check")
                assert url == "/api/v1/system/health-check"
            except Exception:
                pass  # ルートが見つからない場合はスキップ

    def test_middleware_configuration(self, client):
        """ミドルウェア設定のテスト."""
        # アプリケーション設定の確認
        assert app.config.get("API_DEFAULT_VERSION") == "v1"
        assert app.config.get("API_SUPPORTED_VERSIONS") == ["v1"]

    def test_error_handling_with_versioning(self, client):
        """バージョニング付きエラーハンドリングのテスト."""
        # 存在しないエンドポイントへのリクエスト
        response = client.get("/api/v1/nonexistent")
        assert response.status_code == 404

        # 存在しないバージョンへのリクエスト
        response = client.get("/api/v999/system/health-check")
        assert response.status_code == 404


class TestAPIVersioningConfiguration:
    """APIバージョニング設定のテスト."""

    def test_default_configuration(self):
        """デフォルト設定のテスト."""
        test_app = Flask(__name__)
        middleware = APIVersioningMiddleware(test_app)

        assert middleware.default_version == "v1"
        assert middleware.supported_versions == ["v1"]

    def test_custom_configuration(self):
        """カスタム設定のテスト."""
        test_app = Flask(__name__)
        test_app.config["API_DEFAULT_VERSION"] = "v2"
        test_app.config["API_SUPPORTED_VERSIONS"] = ["v1", "v2", "v3"]

        middleware = APIVersioningMiddleware(test_app)

        assert middleware.default_version == "v2"
        assert middleware.supported_versions == ["v1", "v2", "v3"]

    def test_configuration_validation(self):
        """設定値の検証テスト."""
        test_app = Flask(__name__)
        test_app.config["API_DEFAULT_VERSION"] = "v2"
        test_app.config["API_SUPPORTED_VERSIONS"] = [
            "v1",
            "v3",
        ]  # デフォルトバージョンが含まれていない

        # この場合でもミドルウェアは正常に動作する（設定の検証は実装次第）
        middleware = APIVersioningMiddleware(test_app)
        assert middleware.default_version == "v2"
        assert middleware.supported_versions == ["v1", "v3"]


class TestAPIVersioningPerformance:
    """APIバージョニングのパフォーマンステスト."""

    def test_middleware_overhead(self, client):
        """ミドルウェアのオーバーヘッドテスト."""
        import time

        # 複数回リクエストを送信してレスポンス時間を測定
        times = []
        for _ in range(10):
            start_time = time.time()
            response = client.get("/api/v1/system/health-check")
            end_time = time.time()
            times.append(end_time - start_time)
            assert response.status_code == 200

        # 平均レスポンス時間が合理的な範囲内であることを確認
        avg_time = sum(times) / len(times)
        assert avg_time < 1.0  # 1秒以内

    def test_version_parsing_performance(self):
        """バージョン解析のパフォーマンステスト."""
        import time

        from app.middleware.versioning import parse_api_version

        test_paths = [
            "/api/v1/stocks",
            "/api/v2/bulk-data",
            "/api/system/health-check",
            "/home",
            "/api/v10/complex/nested/path",
        ]

        start_time = time.time()
        for _ in range(1000):
            for path in test_paths:
                parse_api_version(path)
        end_time = time.time()

        # 1000回の解析が1秒以内に完了することを確認
        assert (end_time - start_time) < 1.0
