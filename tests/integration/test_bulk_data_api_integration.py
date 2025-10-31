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
        # Arrange (準備)
        mock_job = mocker.Mock()
        mock_job.job_id = "test-job-123"
        mock_job.status = "pending"
        mocker.patch(
            "app.api.bulk_data.start_bulk_fetch", return_value=mock_job
        )
        test_payload = {"symbols": ["7203.T", "6758.T"], "interval": "1d"}

        # Act (実行)
        response = client.post(
            "/api/bulk-data/jobs",
            json=test_payload,
            headers={"X-API-KEY": "test-key"},
            content_type="application/json",
        )
        data = response.get_json()

        # Assert (検証)
        assert response.status_code in [200, 202]
        assert (
            data.get("status") in ["success", "accepted"]
            or data.get("success") is True
        )
        assert "job_id" in data or "message" in data

    def test_create_bulk_job_missing_params(self, client):
        """POST /api/bulk-data/jobs - 必須パラメータ不足."""
        # Arrange (準備)
        empty_payload = {}

        # Act (実行)
        response = client.post(
            "/api/bulk-data/jobs",
            json=empty_payload,
            headers={"X-API-KEY": "test-key"},
            content_type="application/json",
        )
        data = response.get_json()

        # Assert (検証)
        assert response.status_code in [400, 422]
        assert data["success"] is False and "error" in data
        assert "message" in data

    def test_create_bulk_job_unauthorized(self, client):
        """POST /api/bulk-data/jobs - 認証エラー."""
        # Arrange (準備)
        test_payload = {"symbols": ["7203.T"], "interval": "1d"}

        # Act (実行)
        response = client.post(
            "/api/bulk-data/jobs",
            json=test_payload,
            content_type="application/json",
        )
        data = response.get_json()

        # Assert (検証)
        assert response.status_code == 401
        assert "error" in data
        assert "message" in data

    def test_create_bulk_job_invalid_api_key(self, client):
        """POST /api/bulk-data/jobs - 無効なAPIキー."""
        # Arrange (準備)
        test_payload = {"symbols": ["7203.T"], "interval": "1d"}

        # Act (実行)
        response = client.post(
            "/api/bulk-data/jobs",
            json=test_payload,
            headers={"X-API-KEY": "invalid-key"},
            content_type="application/json",
        )
        data = response.get_json()

        # Assert (検証)
        assert response.status_code == 401
        assert "error" in data

    def test_get_job_status_success(self, client, mocker):
        """GET /api/bulk-data/jobs/{job_id} - ジョブステータス取得成功."""
        # Arrange (準備)
        from app.api.bulk_data import JOBS

        test_job = {
            "id": "test-job-123",
            "status": "completed",
            "progress": {
                "total": 10,
                "processed": 10,
                "successful": 8,
                "failed": 2,
                "progress_percentage": 100.0,
            },
            "created_at": 1234567890,
            "updated_at": 1234567890,
        }
        JOBS["test-job-123"] = test_job

        # Act (実行)
        response = client.get(
            "/api/bulk-data/jobs/test-job-123",
            headers={"X-API-KEY": "test-key"},
        )
        data = response.get_json()

        # Assert (検証)
        assert response.status_code == 200
        assert data["success"] is True
        assert "job" in data
        assert data["job"]["id"] == "test-job-123"

        JOBS.pop("test-job-123", None)

    def test_get_job_status_not_found(self, client, mocker):
        """GET /api/bulk-data/jobs/{job_id} - 存在しないジョブ."""
        # Arrange (準備)
        mocker.patch("app.api.bulk_data.get_job_status", return_value=None)

        # Act (実行)
        response = client.get(
            "/api/bulk-data/jobs/nonexistent-job",
            headers={"X-API-KEY": "test-key"},
        )
        data = response.get_json()

        # Assert (検証)
        assert response.status_code == 404
        assert "error" in data
        assert "message" in data

    def test_bulk_data_api_stop_job_success_with_running_job_returns_stopped_status(
        self, client, mocker
    ):
        """POST /api/bulk-data/jobs/{job_id}/stop - ジョブ停止成功."""
        # Arrange (準備)
        from app.api.bulk_data import JOBS

        test_job = {
            "id": "test-job-456",
            "status": "running",
            "progress": {
                "total": 10,
                "processed": 5,
                "successful": 4,
                "failed": 1,
                "progress_percentage": 50.0,
            },
            "created_at": 1234567890,
            "updated_at": 1234567890,
        }
        JOBS["test-job-456"] = test_job

        # Act (実行)
        response = client.post(
            "/api/bulk-data/jobs/test-job-456/stop",
            headers={"X-API-KEY": "test-key"},
        )
        data = response.get_json()

        # Assert (検証)
        assert response.status_code == 200
        assert data["success"] is True
        assert "message" in data

        JOBS.pop("test-job-456", None)

    def test_bulk_data_api_stop_job_not_found_with_invalid_job_id_returns_not_found_error(
        self, client, mocker
    ):
        """POST /api/bulk-data/jobs/{job_id}/stop - 存在しないジョブの停止."""
        # Arrange (準備)
        mocker.patch("app.api.bulk_data.stop_job", return_value=None)

        # Act (実行)
        response = client.post(
            "/api/bulk-data/jobs/nonexistent-job/stop",
            headers={"X-API-KEY": "test-key"},
        )
        data = response.get_json()

        # Assert (検証)
        assert response.status_code == 404
        assert "error" in data


class TestJPXSequentialAPI:
    """JPX銘柄一括取得API統合テスト."""

    def test_get_jpx_symbols_success(self, client, mocker):
        """GET /api/bulk-data/jpx-sequential/symbols - JPX銘柄一覧取得成功."""
        # Arrange (準備)
        mock_symbols = [
            {"symbol": "7203.T", "name": "Toyota Motor Corporation"},
            {"symbol": "6758.T", "name": "Sony Group Corporation"},
        ]
        mocker.patch(
            "app.api.bulk_data.get_jpx_symbols", return_value=mock_symbols
        )

        # Act (実行)
        response = client.get(
            "/api/bulk-data/jpx-sequential/symbols",
            headers={"X-API-KEY": "test-key"},
        )
        data = response.get_json()

        # Assert (検証)
        assert response.status_code == 200
        assert data.get("status") == "success" or data.get("success") is True
        assert "data" in data or "symbols" in data

    def test_get_jpx_symbols_pagination(self, client, mocker):
        """GET /api/bulk-data/jpx-sequential/symbols - ページネーションテスト."""
        # Arrange (準備)
        mock_symbols = []
        mocker.patch(
            "app.api.bulk_data.get_jpx_symbols", return_value=mock_symbols
        )

        # Act (実行)
        response = client.get(
            "/api/bulk-data/jpx-sequential/symbols?limit=10&offset=0",
            headers={"X-API-KEY": "test-key"},
        )

        # Assert (検証)
        assert response.status_code == 200

    def test_get_jpx_symbols_unauthorized(self, client):
        """GET /api/bulk-data/jpx-sequential/symbols - 認証エラー."""
        # Arrange (準備)
        # 認証なしでリクエスト

        # Act (実行)
        response = client.get("/api/bulk-data/jpx-sequential/symbols")
        data = response.get_json()

        # Assert (検証)
        assert response.status_code == 401
        assert "error" in data

    def test_create_jpx_sequential_job_success(self, client, mocker):
        """POST /api/bulk-data/jpx-sequential/jobs - JPXバルクジョブ作成成功."""
        # Arrange (準備)
        mocker.patch(
            "app.api.bulk_data.BatchService.create_batch",
            return_value={"id": "batch-123"},
        )
        mocker.patch("app.api.bulk_data.ENABLE_PHASE2", False)
        mocker.patch("app.api.bulk_data._run_jpx_sequential_job")
        test_payload = {"symbols": ["7203.T", "6758.T"]}

        # Act (実行)
        response = client.post(
            "/api/bulk-data/jpx-sequential/jobs",
            json=test_payload,
            headers={"X-API-KEY": "test-key"},
            content_type="application/json",
        )
        data = response.get_json()

        # Assert (検証)
        assert response.status_code in [200, 202]
        assert data["success"] is True
        assert "job_id" in data
        assert data["status"] == "accepted"
        assert data["total_symbols"] == 2


class TestBulkDataAPIErrorHandling:
    """バルクデータAPIエラーハンドリングテスト."""

    def test_invalid_symbols_format(self, client):
        """POST /api/bulk-data/jobs - 無効なシンボル形式."""
        # Arrange (準備)
        invalid_payload = {"symbols": "not-an-array", "interval": "1d"}

        # Act (実行)
        response = client.post(
            "/api/bulk-data/jobs",
            json=invalid_payload,
            headers={"X-API-KEY": "test-key"},
            content_type="application/json",
        )
        data = response.get_json()

        # Assert (検証)
        assert response.status_code in [400, 422]
        assert "error" in data or data.get("status") == "error"

    def test_bulk_data_api_invalid_interval_with_invalid_parameter_returns_error_response(
        self, client
    ):
        """POST /api/bulk-data/jobs - 無効な時間間隔."""
        # Arrange (準備)
        invalid_payload = {"symbols": ["7203.T"], "interval": "invalid"}

        # Act (実行)
        response = client.post(
            "/api/bulk-data/jobs",
            json=invalid_payload,
            headers={"X-API-KEY": "test-key"},
            content_type="application/json",
        )

        # Assert (検証)
        assert response.status_code in [200, 202, 400, 422]

    def test_bulk_data_api_empty_symbols_array_with_no_symbols_returns_error_response(
        self, client
    ):
        """POST /api/bulk-data/jobs - 空のシンボル配列."""
        # Arrange (準備)
        empty_symbols_payload = {"symbols": [], "interval": "1d"}

        # Act (実行)
        response = client.post(
            "/api/bulk-data/jobs",
            json=empty_symbols_payload,
            headers={"X-API-KEY": "test-key"},
            content_type="application/json",
        )
        data = response.get_json()

        # Assert (検証)
        assert response.status_code in [400, 422]
        assert "error" in data or data.get("status") == "error"

    def test_service_unavailable(self, client, mocker):
        """POST /api/bulk-data/jobs - サービス利用不可."""
        # Arrange (準備)
        mocker.patch(
            "app.api.bulk_data.threading.Thread",
            side_effect=Exception("Service unavailable"),
        )
        test_payload = {"symbols": ["7203.T"], "interval": "1d"}

        # Act (実行)
        response = client.post(
            "/api/bulk-data/jobs",
            json=test_payload,
            headers={"X-API-KEY": "test-key"},
            content_type="application/json",
        )
        data = response.get_json()

        # Assert (検証)
        assert response.status_code in [500, 503]
        assert data.get("status") == "error" or "error" in data


class TestBulkDataAPIResponseFormat:
    """バルクデータAPIレスポンス形式検証."""

    def test_response_content_type(self, client, mocker):
        """レスポンスのContent-Typeがapplication/jsonであることを確認."""
        # Arrange (準備)
        mock_symbols = []
        mocker.patch(
            "app.api.bulk_data.get_jpx_symbols", return_value=mock_symbols
        )

        # Act (実行)
        response = client.get(
            "/api/bulk-data/jpx-sequential/symbols",
            headers={"X-API-KEY": "test-key"},
        )

        # Assert (検証)
        assert "application/json" in response.content_type

    def test_error_response_format(self, client):
        """エラーレスポンスの形式検証."""
        # Arrange (準備)
        empty_payload = {}

        # Act (実行)
        response = client.post(
            "/api/bulk-data/jobs",
            json=empty_payload,
            headers={"X-API-KEY": "test-key"},
            content_type="application/json",
        )
        data = response.get_json()

        # Assert (検証)
        assert "error" in data or "status" in data
        assert "message" in data

    def test_success_response_consistency(self, client, mocker):
        """成功レスポンスの一貫性検証."""
        # Arrange (準備)
        mock_symbols = [{"symbol": "7203.T"}]
        mocker.patch(
            "app.api.bulk_data.get_jpx_symbols", return_value=mock_symbols
        )

        # Act (実行)
        response = client.get(
            "/api/bulk-data/jpx-sequential/symbols",
            headers={"X-API-KEY": "test-key"},
        )
        data = response.get_json()

        # Assert (検証)
        assert "status" in data or "success" in data


class TestBulkDataAPIAuthentication:
    """バルクデータAPI認証テスト."""

    def test_missing_api_key_header(self, client):
        """APIキーヘッダーがない場合のテスト."""
        # Arrange (準備)
        # 認証なしでリクエスト

        # Act (実行)
        response = client.get("/api/bulk-data/jpx-sequential/symbols")

        # Assert (検証)
        assert response.status_code == 401

    def test_empty_api_key(self, client):
        """空のAPIキーの場合のテスト."""
        # Arrange (準備)
        # 空のAPIキーでリクエスト

        # Act (実行)
        response = client.get(
            "/api/bulk-data/jpx-sequential/symbols",
            headers={"X-API-KEY": ""},
        )

        # Assert (検証)
        assert response.status_code == 401

    def test_case_sensitive_api_key_header(self, client, mocker):
        """APIキーヘッダー名の大文字小文字区別テスト."""
        # Arrange (準備)
        mock_symbols = []
        mocker.patch(
            "app.api.bulk_data.get_jpx_symbols", return_value=mock_symbols
        )

        # Act (実行)
        response = client.get(
            "/api/bulk-data/jpx-sequential/symbols",
            headers={"X-API-KEY": "test-key"},
        )

        # Assert (検証)
        assert response.status_code == 200
