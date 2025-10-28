"""バルクデータAPI統合テスト.

このモジュールはバルクデータ処理関連APIエンドポイントの統合テストを提供します。
- バルクジョブの作成・取得・停止
- JPX銘柄一括取得
- エラーハンドリング
- 認証テスト
"""

import json

import pytest

from app.app import app as flask_app


@pytest.fixture
def client():
    """テスト用のFlaskクライアント."""
    flask_app.config["TESTING"] = True
    with flask_app.test_client() as client:
        yield client


@pytest.fixture(autouse=True)
def setup_env(monkeypatch):
    """テスト環境のセットアップ."""
    monkeypatch.setenv("API_KEY", "test-key")
    monkeypatch.setenv("RATE_LIMIT_PER_MINUTE", "10")


class TestBulkDataJobsAPI:
    """バルクデータジョブAPI統合テスト."""

    def test_create_bulk_job_success(self, client, mocker):
        """POST /api/bulk-data/jobs - バルクジョブ作成成功."""
        # バルクジョブサービスのモック
        mock_job = mocker.Mock()
        mock_job.job_id = "test-job-123"
        mock_job.status = "pending"

        mocker.patch(
            "app.api.bulk_data.start_bulk_fetch", return_value=mock_job
        )

        response = client.post(
            "/api/bulk-data/jobs",
            json={"symbols": ["7203.T", "6758.T"], "interval": "1d"},
            headers={"X-API-KEY": "test-key"},
            content_type="application/json",
        )

        # ステータスコードの検証（202 Accepted または 200 OK）
        assert response.status_code in [200, 202]
        data = response.get_json()

        # レスポンス形式の検証
        assert (
            data.get("status") in ["success", "accepted"]
            or data.get("success") is True
        )
        assert "job_id" in data or "message" in data

    def test_create_bulk_job_missing_params(self, client):
        """POST /api/bulk-data/jobs - 必須パラメータ不足."""
        response = client.post(
            "/api/bulk-data/jobs",
            json={},
            headers={"X-API-KEY": "test-key"},
            content_type="application/json",
        )

        assert response.status_code in [400, 422]
        data = response.get_json()

        assert data["status"] == "error" or "error" in data
        assert "message" in data

    def test_create_bulk_job_unauthorized(self, client):
        """POST /api/bulk-data/jobs - 認証エラー."""
        response = client.post(
            "/api/bulk-data/jobs",
            json={"symbols": ["7203.T"], "interval": "1d"},
            content_type="application/json",
        )

        assert response.status_code == 401
        data = response.get_json()

        assert "error" in data
        assert "message" in data

    def test_create_bulk_job_invalid_api_key(self, client):
        """POST /api/bulk-data/jobs - 無効なAPIキー."""
        response = client.post(
            "/api/bulk-data/jobs",
            json={"symbols": ["7203.T"], "interval": "1d"},
            headers={"X-API-KEY": "invalid-key"},
            content_type="application/json",
        )

        assert response.status_code == 401
        data = response.get_json()

        assert "error" in data

    def test_get_job_status_success(self, client, mocker):
        """GET /api/bulk-data/jobs/{job_id} - ジョブステータス取得成功."""
        mock_job = mocker.Mock()
        mock_job.job_id = "test-job-123"
        mock_job.status = "completed"
        mock_job.total = 10
        mock_job.processed = 10

        mocker.patch("app.api.bulk_data.get_job_status", return_value=mock_job)

        response = client.get(
            "/api/bulk-data/jobs/test-job-123",
            headers={"X-API-KEY": "test-key"},
        )

        assert response.status_code == 200
        data = response.get_json()

        # レスポンス形式の検証
        assert "status" in data or "success" in data or "job" in data

    def test_get_job_status_not_found(self, client, mocker):
        """GET /api/bulk-data/jobs/{job_id} - 存在しないジョブ."""
        mocker.patch("app.api.bulk_data.get_job_status", return_value=None)

        response = client.get(
            "/api/bulk-data/jobs/nonexistent-job",
            headers={"X-API-KEY": "test-key"},
        )

        assert response.status_code == 404
        data = response.get_json()

        assert "error" in data
        assert "message" in data

    def test_stop_job_success(self, client, mocker):
        """POST /api/bulk-data/jobs/{job_id}/stop - ジョブ停止成功."""
        mock_result = {"status": "stopped", "job_id": "test-job-123"}

        mocker.patch("app.api.bulk_data.stop_job", return_value=mock_result)

        response = client.post(
            "/api/bulk-data/jobs/test-job-123/stop",
            headers={"X-API-KEY": "test-key"},
        )

        assert response.status_code == 200
        data = response.get_json()

        assert (
            data.get("status") in ["success", "stopped"]
            or data.get("success") is True
        )
        assert "message" in data or "status" in data

    def test_stop_job_not_found(self, client, mocker):
        """POST /api/bulk-data/jobs/{job_id}/stop - 存在しないジョブの停止."""
        mocker.patch("app.api.bulk_data.stop_job", return_value=None)

        response = client.post(
            "/api/bulk-data/jobs/nonexistent-job/stop",
            headers={"X-API-KEY": "test-key"},
        )

        assert response.status_code == 404
        data = response.get_json()

        assert "error" in data


class TestJPXSequentialAPI:
    """JPX銘柄一括取得API統合テスト."""

    def test_get_jpx_symbols_success(self, client, mocker):
        """GET /api/bulk-data/jpx-sequential/symbols - JPX銘柄一覧取得成功."""
        mock_symbols = [
            {"symbol": "7203.T", "name": "Toyota Motor Corporation"},
            {"symbol": "6758.T", "name": "Sony Group Corporation"},
        ]

        mocker.patch(
            "app.api.bulk_data.get_jpx_symbols", return_value=mock_symbols
        )

        response = client.get(
            "/api/bulk-data/jpx-sequential/symbols",
            headers={"X-API-KEY": "test-key"},
        )

        assert response.status_code == 200
        data = response.get_json()

        assert data.get("status") == "success" or data.get("success") is True
        assert "data" in data or "symbols" in data

    def test_get_jpx_symbols_pagination(self, client, mocker):
        """GET /api/bulk-data/jpx-sequential/symbols - ページネーションテスト."""
        mock_symbols = []

        mocker.patch(
            "app.api.bulk_data.get_jpx_symbols", return_value=mock_symbols
        )

        response = client.get(
            "/api/bulk-data/jpx-sequential/symbols?limit=10&offset=0",
            headers={"X-API-KEY": "test-key"},
        )

        assert response.status_code == 200

    def test_get_jpx_symbols_unauthorized(self, client):
        """GET /api/bulk-data/jpx-sequential/symbols - 認証エラー."""
        response = client.get("/api/bulk-data/jpx-sequential/symbols")

        assert response.status_code == 401
        data = response.get_json()

        assert "error" in data

    def test_create_jpx_sequential_job_success(self, client, mocker):
        """POST /api/bulk-data/jpx-sequential/jobs - JPXバルクジョブ作成成功."""
        mock_job = mocker.Mock()
        mock_job.job_id = "jpx-job-123"
        mock_job.status = "pending"

        mocker.patch(
            "app.api.bulk_data.start_jpx_sequential_job",
            return_value=mock_job,
        )

        response = client.post(
            "/api/bulk-data/jpx-sequential/jobs",
            json={"symbols": ["7203.T", "6758.T"]},
            headers={"X-API-KEY": "test-key"},
            content_type="application/json",
        )

        assert response.status_code in [200, 202]
        data = response.get_json()

        assert (
            data.get("status") in ["success", "accepted"]
            or data.get("success") is True
            or "job_id" in data
        )


class TestBulkDataAPIErrorHandling:
    """バルクデータAPIエラーハンドリングテスト."""

    def test_invalid_symbols_format(self, client):
        """POST /api/bulk-data/jobs - 無効なシンボル形式."""
        response = client.post(
            "/api/bulk-data/jobs",
            json={"symbols": "not-an-array", "interval": "1d"},
            headers={"X-API-KEY": "test-key"},
            content_type="application/json",
        )

        assert response.status_code in [400, 422]
        data = response.get_json()

        assert "error" in data or data.get("status") == "error"

    def test_invalid_interval(self, client):
        """POST /api/bulk-data/jobs - 無効な時間間隔."""
        response = client.post(
            "/api/bulk-data/jobs",
            json={"symbols": ["7203.T"], "interval": "invalid"},
            headers={"X-API-KEY": "test-key"},
            content_type="application/json",
        )

        # 無効な間隔は拒否またはデフォルト値が使用される
        assert response.status_code in [200, 202, 400, 422]

    def test_empty_symbols_array(self, client):
        """POST /api/bulk-data/jobs - 空のシンボル配列."""
        response = client.post(
            "/api/bulk-data/jobs",
            json={"symbols": [], "interval": "1d"},
            headers={"X-API-KEY": "test-key"},
            content_type="application/json",
        )

        assert response.status_code in [400, 422]
        data = response.get_json()

        assert "error" in data or data.get("status") == "error"

    def test_service_unavailable(self, client, mocker):
        """POST /api/bulk-data/jobs - サービス利用不可."""
        mocker.patch(
            "app.api.bulk_data.start_bulk_fetch",
            side_effect=Exception("Service unavailable"),
        )

        response = client.post(
            "/api/bulk-data/jobs",
            json={"symbols": ["7203.T"], "interval": "1d"},
            headers={"X-API-KEY": "test-key"},
            content_type="application/json",
        )

        assert response.status_code in [500, 503]
        data = response.get_json()

        assert data.get("status") == "error" or "error" in data


class TestBulkDataAPIResponseFormat:
    """バルクデータAPIレスポンス形式検証."""

    def test_response_content_type(self, client, mocker):
        """レスポンスのContent-Typeがapplication/jsonであることを確認."""
        mock_symbols = []
        mocker.patch(
            "app.api.bulk_data.get_jpx_symbols", return_value=mock_symbols
        )

        response = client.get(
            "/api/bulk-data/jpx-sequential/symbols",
            headers={"X-API-KEY": "test-key"},
        )

        assert "application/json" in response.content_type

    def test_error_response_format(self, client):
        """エラーレスポンスの形式検証."""
        response = client.post(
            "/api/bulk-data/jobs",
            json={},
            headers={"X-API-KEY": "test-key"},
            content_type="application/json",
        )

        data = response.get_json()

        # エラーレスポンスには error または status フィールドが必要
        assert "error" in data or "status" in data
        assert "message" in data

    def test_success_response_consistency(self, client, mocker):
        """成功レスポンスの一貫性検証."""
        mock_symbols = [{"symbol": "7203.T"}]
        mocker.patch(
            "app.api.bulk_data.get_jpx_symbols", return_value=mock_symbols
        )

        response = client.get(
            "/api/bulk-data/jpx-sequential/symbols",
            headers={"X-API-KEY": "test-key"},
        )

        data = response.get_json()

        # 成功レスポンスには status または success フィールドが必要
        assert "status" in data or "success" in data


class TestBulkDataAPIAuthentication:
    """バルクデータAPI認証テスト."""

    def test_missing_api_key_header(self, client):
        """APIキーヘッダーがない場合のテスト."""
        response = client.get("/api/bulk-data/jpx-sequential/symbols")

        assert response.status_code == 401

    def test_empty_api_key(self, client):
        """空のAPIキーの場合のテスト."""
        response = client.get(
            "/api/bulk-data/jpx-sequential/symbols",
            headers={"X-API-KEY": ""},
        )

        assert response.status_code == 401

    def test_case_sensitive_api_key_header(self, client, mocker):
        """APIキーヘッダー名の大文字小文字区別テスト."""
        mock_symbols = []
        mocker.patch(
            "app.api.bulk_data.get_jpx_symbols", return_value=mock_symbols
        )

        # 正しいヘッダー名
        response = client.get(
            "/api/bulk-data/jpx-sequential/symbols",
            headers={"X-API-KEY": "test-key"},
        )

        # ヘッダー名は通常大文字小文字を区別しない
        assert response.status_code == 200
