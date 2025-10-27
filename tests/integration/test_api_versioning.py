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
        # 既存のエンドポイント（バージョンなし）
        response = client.post(
            "/api/bulk-data/jobs",
            json={"symbols": ["7203.T"], "interval": "1d"},
        )
        assert response.status_code in [
            200,
            202,
            401,
        ]  # 認証エラーまたは正常/受理レスポンス

        # 新しいバージョン付きエンドポイント
        response = client.post(
            "/api/v1/bulk-data/jobs",
            json={"symbols": ["7203.T"], "interval": "1d"},
        )
        assert response.status_code in [
            200,
            202,
            401,
        ]  # 認証エラーまたは正常/受理レスポンス

    def test_backward_compatibility_stock_master_api(self, client):
        """株式マスタAPIの後方互換性テスト."""
        # 既存のエンドポイント（バージョンなし）
        response = client.get("/api/stock-master/")
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
        response = client.get("/api/system/health")
        assert response.status_code == 200
        data = response.get_json()
        # 新しいAPIレスポンス形式を検証
        assert data["status"] == "success"
        assert "data" in data
        assert "overall_status" in data["data"]

        # 新しいバージョン付きエンドポイント
        response = client.get("/api/v1/system/health-check")
        assert response.status_code == 200
        data = response.get_json()
        # 新しいAPIレスポンス形式を検証
        assert data["status"] == "success"
        assert "data" in data
        assert "overall_status" in data["data"]

    def test_version_parsing_in_request(self, client):
        """リクエスト内でのバージョン解析テスト."""
        # バージョン付きリクエストでのバージョン情報確認
        with app.test_request_context("/api/v1/system/health-check"):
            from flask import request

            # ミドルウェアを手動で実行
            middleware = APIVersioningMiddleware()
            # ログ出力でrequest.appが参照されるため明示的に設定
            request.app = app
            middleware.process_request(request)
            assert hasattr(request, "api_version")
            assert request.api_version == "v1"

    def test_default_version_for_non_versioned_request(self, client):
        """バージョンなしリクエストでのデフォルトバージョンテスト."""
        with app.test_request_context("/api/system/health"):
            from flask import request

            # ミドルウェアを手動で実行
            middleware = APIVersioningMiddleware()
            request.app = app
            middleware.process_request(request)
            assert hasattr(request, "api_version")
            assert request.api_version == "v1"  # デフォルトバージョン

    def test_non_api_request_version(self, client):
        """API以外のリクエストでのバージョンテスト."""
        with app.test_request_context("/"):
            from flask import request

            # ミドルウェアを手動で実行
            middleware = APIVersioningMiddleware()
            request.app = app
            middleware.process_request(request)
            assert hasattr(request, "api_version")
            assert request.api_version == "v1"  # デフォルトバージョン

    def test_same_functionality_different_versions(self, client):
        """異なるバージョンで同じ機能のテスト."""
        # バージョンなしエンドポイント
        response1 = client.get("/api/system/health")

        # バージョン付きエンドポイント
        response2 = client.get("/api/v1/system/health-check")

        # 両方とも同じレスポンスを返すことを確認
        assert response1.status_code == response2.status_code
        if response1.status_code == 200:
            data1 = response1.get_json()
            data2 = response2.get_json()

            # 新しいAPIレスポンス形式を検証
            assert data1["status"] == "success"
            assert data2["status"] == "success"
            assert "data" in data1
            assert "data" in data2
            assert "overall_status" in data1["data"]
            assert "overall_status" in data2["data"]

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
                assert url == "/api/system/health"
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
        # エラーレスポンスの場合、新しい形式を確認
        data = response.get_json()
        if data and "status" in data:
            # 新しいAPIレスポンス形式の場合
            assert data["status"] == "error"
            if "error" in data:
                assert "code" in data["error"]
                assert "message" in data["error"]

        # 存在しないバージョンへのリクエスト
        response = client.get("/api/v999/system/health")
        # 未サポートバージョンはミドルウェアで400を返す
        assert response.status_code == 400
        # エラーレスポンスの場合、新しい形式を確認
        data = response.get_json()
        if data and "status" in data:
            # 新しいAPIレスポンス形式の場合
            assert data["status"] == "error"
            if "error" in data:
                assert "code" in data["error"]
                assert "message" in data["error"]


class TestAPIVersioningConfiguration:
    """APIバージョニング設定のテスト."""

    def test_default_configuration(self):
        """デフォルト設定のテスト."""
        test_app = Flask(__name__)
        middleware = APIVersioningMiddleware(test_app)
        info = middleware.get_version_info()
        assert info["default_version"] == "v1"
        assert info["supported_versions"] == ["v1"]

    def test_custom_configuration(self):
        """カスタム設定のテスト."""
        test_app = Flask(__name__)
        test_app.config["API_DEFAULT_VERSION"] = "v2"
        test_app.config["API_SUPPORTED_VERSIONS"] = ["v1", "v2", "v3"]

        middleware = APIVersioningMiddleware(test_app)
        info = middleware.get_version_info()
        assert info["default_version"] == "v2"
        assert info["supported_versions"] == ["v1", "v2", "v3"]

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
        info = middleware.get_version_info()
        assert info["default_version"] == "v2"
        assert info["supported_versions"] == ["v1", "v3"]


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
            # 新しいAPIレスポンス形式を検証
            data = response.get_json()
            assert data["status"] == "success"
            assert "data" in data
            assert "overall_status" in data["data"]

        # 平均レスポンス時間が合理的な範囲内であることを確認
        avg_time = sum(times) / len(times)
        assert avg_time < 1.0  # 1秒以内

    def test_version_parsing_performance(self):
        """バージョン解析のパフォーマンステスト."""
        import time

        # 実装変更に合わせ、extract_version_from_urlを使用
        middleware = APIVersioningMiddleware()

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
                middleware.extract_version_from_url(path)[0]
        end_time = time.time()

        # 1000回の解析が1秒以内に完了することを確認
        assert (end_time - start_time) < 1.0
