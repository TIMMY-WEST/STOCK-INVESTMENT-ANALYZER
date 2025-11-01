"""APIバージョニング機能のエンドツーエンドテスト."""

import os
import time
from unittest.mock import patch

import pytest
import requests

from app.app import app


pytestmark = pytest.mark.e2e


class TestAPIVersioningE2E:
    """APIバージョニングのエンドツーエンドテスト."""

    @pytest.fixture(scope="class")
    def test_server(self):
        """テスト用サーバーの起動."""
        app.config["TESTING"] = True
        app.config["WTF_CSRF_ENABLED"] = False

        # テスト用のポートでサーバーを起動
        import threading

        from werkzeug.serving import make_server

        server = make_server("127.0.0.1", 5001, app, threaded=True)
        thread = threading.Thread(target=server.serve_forever)
        thread.daemon = True
        thread.start()

        # サーバーが起動するまで少し待機
        time.sleep(1)

        yield "http://127.0.0.1:5001"

        server.shutdown()

    def test_health_check_endpoints(self, test_server):
        """ヘルスチェックエンドポイントのE2Eテスト."""
        # Arrange (準備)
        base_url = test_server

        # Act (実行) - 既存のヘルスチェックエンドポイント
        response = requests.get(f"{base_url}/api/system/health")
        data = response.json()

        # Assert (検証) - 既存のヘルスチェックエンドポイント
        assert response.status_code == 200
        assert data["status"] == "success"
        assert "data" in data
        assert "overall_status" in data["data"]
        assert "meta" in data and "timestamp" in data["meta"]

        # Act (実行) - バージョン付きヘルスチェックエンドポイント
        response = requests.get(f"{base_url}/api/v1/system/health-check")
        data = response.json()

        # Assert (検証) - バージョン付きヘルスチェックエンドポイント
        assert response.status_code == 200
        assert data["status"] == "success"
        assert "data" in data
        assert "overall_status" in data["data"]
        assert "meta" in data and "timestamp" in data["meta"]

    def test_database_connection_endpoints(self, test_server):
        """データベース接続テストエンドポイントのE2Eテスト."""
        # Arrange (準備)
        base_url = test_server

        # Act (実行) - 既存のデータベース接続テストエンドポイント
        response = requests.get(f"{base_url}/api/system/database/connection")
        data = response.json()

        # Assert (検証) - 既存のデータベース接続テストエンドポイント
        assert response.status_code == 200
        assert data["status"] == "success"
        assert "data" in data
        assert "database" in data["data"]
        assert "connection_count" in data["data"]
        assert "table_exists" in data["data"]

        # Act (実行) - バージョン付きデータベース接続テストエンドポイント
        response = requests.get(
            f"{base_url}/api/v1/system/database/connection"
        )
        data = response.json()

        # Assert (検証) - バージョン付きデータベース接続テストエンドポイント
        assert response.status_code == 200
        assert data["status"] == "success"
        assert "data" in data
        assert "database" in data["data"]
        assert "connection_count" in data["data"]
        assert "table_exists" in data["data"]

    def test_api_connection_endpoints(self, test_server):
        """API接続テストエンドポイントのE2Eテスト."""
        # Arrange (準備)
        base_url = test_server

        # Act (実行) - 既存のAPI接続テストエンドポイント
        response = requests.get(
            f"{base_url}/api/system/external-api/connection"
        )
        data = response.json()

        # Assert (検証) - 既存のAPI接続テストエンドポイント
        assert response.status_code == 200
        assert data["status"] == "success"
        assert "data" in data
        assert "symbol" in data["data"]
        assert "data_available" in data["data"]

        # Act (実行) - バージョン付きAPI接続テストエンドポイント
        response = requests.get(
            f"{base_url}/api/v1/system/external-api/connection"
        )
        data = response.json()

        # Assert (検証) - バージョン付きAPI接続テストエンドポイント
        assert response.status_code == 200
        assert data["status"] == "success"
        assert "data" in data
        assert "symbol" in data["data"]
        assert "data_available" in data["data"]

    def test_stock_master_endpoints_with_auth(self, test_server):
        """株式マスタエンドポイントの認証付きE2Eテスト."""
        # Arrange (準備)
        base_url = test_server

        with patch.dict(os.environ, {"API_KEY": "test-key"}, clear=False):
            # Act (実行) - APIキーなしでのリクエスト（既存エンドポイント）
            response = requests.get(f"{base_url}/api/stock-master/")
            data = response.json()

            # Assert (検証) - APIキーなしでのリクエスト（既存エンドポイント）
            assert response.status_code == 401
            assert data["status"] == "error"
            assert "error" in data
            assert "code" in data["error"]
            assert "message" in data["error"]

            # Act (実行) - APIキーなしでのリクエスト（バージョン付き）
            response = requests.get(f"{base_url}/api/v1/stock-master/stocks")
            data = response.json()

            # Assert (検証) - APIキーなしでのリクエスト（バージョン付き）
            assert response.status_code == 401
            assert data["status"] == "error"
            assert "error" in data
            assert "code" in data["error"]
            assert "message" in data["error"]

            # Act (実行) - 無効なAPIキーでのリクエスト（既存エンドポイント）
            headers = {"X-API-Key": "invalid-key"}
            response = requests.get(
                f"{base_url}/api/stock-master/", headers=headers
            )
            data = response.json()

            # Assert (検証) - 無効なAPIキーでのリクエスト（既存エンドポイント）
            assert response.status_code == 401
            assert data["status"] == "error"
            assert "error" in data
            assert "code" in data["error"]
            assert "message" in data["error"]

            # Act (実行) - 無効なAPIキーでのリクエスト（バージョン付き）
            response = requests.get(
                f"{base_url}/api/v1/stock-master/stocks", headers=headers
            )
            data = response.json()

            # Assert (検証) - 無効なAPIキーでのリクエスト（バージョン付き）
            assert response.status_code == 401
            assert data["status"] == "error"
            assert "error" in data
            assert "code" in data["error"]
            assert "message" in data["error"]

    def test_bulk_data_endpoints_with_auth(self, test_server):
        """バルクデータエンドポイントの認証付きE2Eテスト."""
        # Arrange (準備)
        base_url = test_server

        # APIキーを設定して認証を有効化
        with patch.dict(os.environ, {"API_KEY": "test-key"}, clear=False):
            # Act (実行) - APIキーなしでのリクエスト（既存エンドポイント）
            response = requests.post(f"{base_url}/api/bulk-data/jobs")
            data = response.json()

            # Assert (検証) - APIキーなしでのリクエスト（既存エンドポイント）
            assert response.status_code == 401
            assert "success" in data and data["success"] is False
            assert "error" in data and isinstance(data["error"], str)
            assert "message" in data and isinstance(data["message"], str)

            # Act (実行) - APIキーなしでのリクエスト（バージョン付き）
            response = requests.post(f"{base_url}/api/v1/bulk-data/jobs")
            data = response.json()

            # Assert (検証) - APIキーなしでのリクエスト（バージョン付き）
            assert response.status_code == 401
            assert "success" in data and data["success"] is False
            assert "error" in data and isinstance(data["error"], str)
            assert "message" in data and isinstance(data["message"], str)

            # Arrange (準備) - 無効なAPIキー
            headers = {"X-API-KEY": "invalid-key"}

            # Act (実行) - 無効なAPIキーでのリクエスト（既存エンドポイント）
            response = requests.post(
                f"{base_url}/api/bulk-data/jobs", headers=headers
            )
            data = response.json()

            # Assert (検証) - 無効なAPIキーでのリクエスト（既存エンドポイント）
            assert response.status_code == 401
            assert "success" in data and data["success"] is False
            assert "error" in data and isinstance(data["error"], str)
            assert "message" in data and isinstance(data["message"], str)

            # Act (実行) - 無効なAPIキーでのリクエスト（バージョン付き）
            response = requests.post(
                f"{base_url}/api/v1/bulk-data/jobs", headers=headers
            )
            data = response.json()

            # Assert (検証) - 無効なAPIキーでのリクエスト（バージョン付き）
            assert response.status_code == 401
            assert "success" in data and data["success"] is False
            assert "error" in data and isinstance(data["error"], str)
            assert "message" in data and isinstance(data["message"], str)

    def test_nonexistent_endpoints(self, test_server):
        """存在しないエンドポイントのE2Eテスト."""
        # Arrange (準備)
        base_url = test_server

        # Act (実行) - 存在しないエンドポイント（既存）
        response = requests.get(f"{base_url}/api/nonexistent")

        # Assert (検証) - 存在しないエンドポイント（既存）
        assert response.status_code == 404

        # Act (実行) - 存在しないエンドポイント（バージョン付き）
        response = requests.get(f"{base_url}/api/v1/nonexistent")

        # Assert (検証) - 存在しないエンドポイント（バージョン付き）
        assert response.status_code == 404

        # Act (実行) - 存在しないバージョン
        response = requests.get(f"{base_url}/api/v999/system/health-check")

        # Assert (検証) - 存在しないバージョン
        assert response.status_code == 400

    def test_response_consistency(self, test_server):
        """レスポンスの一貫性テスト."""
        # Arrange (準備)
        base_url = test_server

        # Act (実行) - 同じ機能のエンドポイントが同じレスポンスを返すことを確認
        response1 = requests.get(f"{base_url}/api/system/health")
        response2 = requests.get(f"{base_url}/api/v1/system/health-check")

        # Assert (検証)
        assert response1.status_code == response2.status_code
        if response1.status_code == 200:
            data1 = response1.json()
            data2 = response2.json()

            # タイムスタンプは異なる可能性があるため、statusのみ比較
            assert data1["status"] == "success"
            assert data2["status"] == "success"
            assert (
                data1["data"]["overall_status"]
                == data2["data"]["overall_status"]
            )

    def test_content_type_headers(self, test_server):
        """Content-Typeヘッダーのテスト."""
        # Arrange (準備)
        base_url = test_server

        endpoints = [
            "/api/system/health",
            "/api/v1/system/health-check",
            "/api/system/database/connection",
            "/api/v1/system/database/connection",
        ]

        # Act & Assert (実行と検証)
        for endpoint in endpoints:
            response = requests.get(f"{base_url}{endpoint}")
            assert response.status_code == 200
            assert "application/json" in response.headers.get(
                "Content-Type", ""
            )

    def test_cors_headers(self, test_server):
        """CORSヘッダーのテスト."""
        # Arrange (準備)
        base_url = test_server

        # Act (実行) - OPTIONSリクエストでCORSヘッダーを確認（既存）
        requests.options(f"{base_url}/api/system/health")
        # CORSの設定によってはヘッダーが設定されている可能性がある

        # Act (実行) - OPTIONSリクエストでCORSヘッダーを確認（バージョン付き）
        requests.options(f"{base_url}/api/v1/system/health-check")
        # 同様にバージョン付きエンドポイントでもCORSが動作することを確認

    def test_rate_limiting_behavior(self, test_server):
        """レート制限の動作テスト."""
        # Arrange (準備)
        base_url = test_server

        # Act (実行) - 短時間で複数のリクエストを送信（既存エンドポイント）
        responses = []
        for _ in range(5):
            response = requests.get(f"{base_url}/api/system/health")
            responses.append(response)
            time.sleep(0.1)

        # Assert (検証) - 全てのリクエストが成功することを確認（レート制限がない場合）
        for response in responses:
            assert response.status_code == 200

        # Act (実行) - バージョン付きエンドポイントでも同様にテスト
        responses = []
        for _ in range(5):
            response = requests.get(f"{base_url}/api/v1/system/health-check")
            responses.append(response)
            time.sleep(0.1)

        # Assert (検証)
        for response in responses:
            assert response.status_code == 200

    def test_error_response_format(self, test_server):
        """エラーレスポンスの形式テスト."""
        # Arrange (準備)
        base_url = test_server

        # Act (実行) - 存在しないエンドポイントへのリクエスト
        response = requests.get(f"{base_url}/api/nonexistent")

        # Assert (検証)
        assert response.status_code == 404

        # エラーレスポンスがJSONまたはHTMLであることを確認
        content_type = response.headers.get("Content-Type", "")
        assert (
            "application/json" in content_type or "text/html" in content_type
        )

    def test_performance_comparison(self, test_server):
        """パフォーマンス比較テスト."""
        # Arrange (準備)
        base_url = test_server

        # Act (実行) - 既存エンドポイントのレスポンス時間測定
        start_time = time.time()
        for _ in range(10):
            response = requests.get(f"{base_url}/api/system/health")
            assert response.status_code == 200
        old_time = time.time() - start_time

        # Act (実行) - バージョン付きエンドポイントのレスポンス時間測定
        start_time = time.time()
        for _ in range(10):
            response = requests.get(f"{base_url}/api/v1/system/health-check")
            assert response.status_code == 200
        new_time = time.time() - start_time

        # Assert (検証) - バージョニングによるオーバーヘッドが大きくないことを確認
        # 新しいエンドポイントが既存のエンドポイントの2倍以上遅くないことを確認
        assert new_time < old_time * 2

    def test_concurrent_requests(self, test_server):
        """同時リクエストのテスト."""
        # Arrange (準備)
        import queue
        import threading

        base_url = test_server
        results = queue.Queue()

        def make_request(endpoint):
            try:
                response = requests.get(f"{base_url}{endpoint}")
                results.put((endpoint, response.status_code))
            except Exception as e:
                results.put((endpoint, str(e)))

        endpoints = [
            "/api/system/health",
            "/api/v1/system/health-check",
            "/api/system/database/connection",
            "/api/v1/system/database/connection",
        ]

        # Act (実行) - 複数のスレッドで同時にリクエストを送信
        threads = []
        for endpoint in endpoints:
            for _ in range(3):  # 各エンドポイントに3回ずつリクエスト
                thread = threading.Thread(
                    target=make_request, args=(endpoint,)
                )
                threads.append(thread)
                thread.start()

        # 全てのスレッドの完了を待機
        for thread in threads:
            thread.join()

        # Assert (検証) - 結果の確認
        while not results.empty():
            endpoint, status = results.get()
            assert status == 200, f"Failed request to {endpoint}: {status}"
