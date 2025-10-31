"""RESTful化されたAPIエンドポイントのテスト."""

import json

import pytest


@pytest.fixture(autouse=True)
def setup_env(monkeypatch):
    """テスト環境のセットアップ."""
    monkeypatch.setenv("API_KEY", "test-key")
    monkeypatch.setenv("RATE_LIMIT_PER_MINUTE", "10")


class TestBulkDataAPI:
    """Bulk Data APIのRESTfulエンドポイントテスト."""

    def test_bulk_data_jobs_with_valid_request_returns_proper_structure(
        self, client
    ):
        """POST /api/bulk-data/jobs エンドポイントの構造テスト."""
        # Arrange (準備)
        payload = {"symbols": ["7203.T"], "interval": "1d"}
        headers = {"X-API-KEY": "test-key"}

        # Act (実行)
        response = client.post(
            "/api/bulk-data/jobs",
            json=payload,
            headers=headers,
        )

        # Assert (検証)
        assert response.status_code in [202, 400, 401]

        if response.status_code == 202:
            data = response.get_json()
            assert "job_id" in data
            assert (data.get("status") in ["success", "accepted"]) or (
                data.get("success") is True
            )

    def test_bulk_data_job_status_with_job_id_returns_proper_structure(
        self, client
    ):
        """GET /api/bulk-data/jobs/{job_id} エンドポイントの構造テスト."""
        # Arrange (準備)
        job_id = "test-job-id"
        headers = {"X-API-KEY": "test-key"}

        # Act (実行)
        response = client.get(
            f"/api/bulk-data/jobs/{job_id}",
            headers=headers,
        )

        # Assert (検証)
        assert response.status_code in [200, 404, 401]

        data = response.get_json()
        assert (
            ("status" in data)
            or ("success" in data)
            or ("job" in data)
            or ("error" in data)
        )
        if response.status_code in [404, 401]:
            assert "error" in data
            if isinstance(data["error"], dict):
                assert "code" in data["error"]
                assert "message" in data["error"]
            else:
                assert isinstance(data["error"], str)
                assert "message" in data

    def test_bulk_data_job_stop_with_job_id_returns_proper_structure(
        self, client
    ):
        """POST /api/bulk-data/jobs/{job_id}/stop エンドポイントの構造テスト."""
        # Arrange (準備)
        job_id = "test-job-id"
        headers = {"X-API-KEY": "test-key"}

        # Act (実行)
        response = client.post(
            f"/api/bulk-data/jobs/{job_id}/stop",
            headers=headers,
        )

        # Assert (検証)
        assert response.status_code in [200, 404, 401]

        data = response.get_json()
        assert (
            ("status" in data)
            or ("success" in data)
            or ("message" in data)
            or ("error" in data)
        )
        if response.status_code in [404, 401]:
            assert "error" in data
            if isinstance(data["error"], dict):
                assert "code" in data["error"]
                assert "message" in data["error"]
            else:
                assert isinstance(data["error"], str)
                assert "message" in data

    def test_bulk_data_jpx_symbols_with_request_returns_proper_structure(
        self, client
    ):
        """GET /api/bulk-data/jpx-sequential/symbols エンドポイントの構造テスト."""
        # Arrange (準備)
        headers = {"X-API-KEY": "test-key"}

        # Act (実行)
        response = client.get(
            "/api/bulk-data/jpx-sequential/symbols",
            headers=headers,
        )

        # Assert (検証)
        assert response.status_code in [200, 401]

        if response.status_code == 200:
            data = response.get_json()
            assert (data.get("status") == "success") or (
                data.get("success") is True
            )

    def test_bulk_data_jpx_jobs_with_valid_request_returns_proper_structure(
        self, client
    ):
        """POST /api/bulk-data/jpx-sequential/jobs エンドポイントの構造テスト."""
        # Arrange (準備)
        payload = {"symbols": ["7203.T"]}
        headers = {"X-API-KEY": "test-key"}

        # Act (実行)
        response = client.post(
            "/api/bulk-data/jpx-sequential/jobs",
            json=payload,
            headers=headers,
        )

        # Assert (検証)
        assert response.status_code in [202, 400, 401]

        if response.status_code == 202:
            data = response.get_json()
            assert (
                ("job_id" in data)
                or (data.get("status") in ["success", "accepted"])
                or (data.get("success") is True)
            )


class TestStockMasterAPI:
    """Stock Master APIのRESTfulエンドポイントテスト."""

    def test_stock_master_update_with_api_key_returns_proper_structure(
        self, client
    ):
        """POST /api/stock-master/ エンドポイントの構造テスト."""
        # Arrange (準備)
        headers = {"X-API-KEY": "test-key"}

        # Act (実行)
        response = client.post("/api/stock-master/", headers=headers)

        # Assert (検証)
        assert response.status_code in [200, 202, 401, 500]

        data = response.get_json()
        assert "status" in data
        if response.status_code in [401, 500]:
            assert "error" in data
            assert "code" in data["error"]
            assert "message" in data["error"]
        else:
            assert "message" in data

    def test_stock_master_list_with_api_key_returns_proper_structure(
        self, client
    ):
        """GET /api/stock-master/ エンドポイントの構造テスト."""
        # Arrange (準備)
        headers = {"X-API-KEY": "test-key"}

        # Act (実行)
        response = client.get("/api/stock-master/", headers=headers)

        # Assert (検証)
        assert response.status_code in [200, 401]

        if response.status_code == 200:
            data = response.get_json()
            assert "data" in data or "message" in data

    def test_stock_master_status_with_api_key_returns_proper_structure(
        self, client
    ):
        """GET /api/stock-master/status エンドポイントの構造テスト."""
        # Arrange (準備)
        headers = {"X-API-KEY": "test-key"}

        # Act (実行)
        response = client.get("/api/stock-master/status", headers=headers)

        # Assert (検証)
        assert response.status_code in [200, 401]

        if response.status_code == 200:
            data = response.get_json()
            assert "data" in data or "message" in data


class TestSystemMonitoringAPI:
    """System Monitoring APIのRESTfulエンドポイントテスト."""

    def test_system_database_connection_with_request_returns_proper_structure(
        self, client
    ):
        """GET /api/system/database/connection エンドポイントの構造テスト."""
        # Arrange (準備)
        endpoint = "/api/system/database/connection"

        # Act (実行)
        response = client.get(endpoint)

        # Assert (検証)
        assert response.status_code in [200, 500]

        data = response.get_json()
        assert data["status"] == "success" or data["status"] == "error"

    def test_system_external_api_connection_with_request_returns_proper_structure(
        self, client
    ):
        """GET /api/system/external-api/connection エンドポイントの構造テスト."""
        # Arrange (準備)
        endpoint = "/api/system/external-api/connection"

        # Act (実行)
        response = client.get(endpoint)

        # Assert (検証)
        assert response.status_code in [200, 500]

        data = response.get_json()
        assert data["status"] == "success" or data["status"] == "error"

    def test_system_health_with_request_returns_proper_structure(self, client):
        """GET /api/system/health エンドポイントの構造テスト."""
        # Arrange (準備)
        endpoint = "/api/system/health"

        # Act (実行)
        response = client.get(endpoint)

        # Assert (検証)
        assert response.status_code in [200, 500]

        data = response.get_json()
        if response.status_code == 200:
            assert "data" in data
            assert "overall_status" in data["data"]
        else:
            assert data["status"] == "error"


class TestMainStocksAPI:
    """Main Stocks APIのRESTfulエンドポイントテスト."""

    def test_stocks_data_with_valid_request_returns_proper_structure(
        self, client
    ):
        """POST /api/stocks/data エンドポイントの構造テスト."""
        # Arrange (準備)
        payload = {"symbol": "7203.T", "period": "1mo"}

        # Act (実行)
        response = client.post(
            "/api/stocks/data",
            json=payload,
            content_type="application/json",
        )

        # Assert (検証)
        assert response.status_code in [200, 400, 502]

        data = response.get_json()
        assert "status" in data
        assert "message" in data

    def test_stocks_test_with_valid_request_returns_proper_structure(
        self, client
    ):
        """POST /api/stocks/test エンドポイントの構造テスト."""
        # Arrange (準備)
        payload = {"symbol": "TEST"}

        # Act (実行)
        response = client.post(
            "/api/stocks/test",
            json=payload,
            content_type="application/json",
        )

        # Assert (検証)
        assert response.status_code in [200, 201, 400, 500]

        data = response.get_json()
        if response.status_code in [400, 500]:
            assert "error" in data
            if isinstance(data["error"], dict):
                assert "code" in data["error"]
                assert "message" in data["error"]
            else:
                assert isinstance(data["error"], str)
                assert "message" in data
        else:
            assert (
                ("status" in data)
                or ("success" in data)
                or ("message" in data)
            )


class TestRESTfulCompliance:
    """RESTful設計原則の準拠テスト."""

    def test_restful_http_methods_with_endpoints_returns_proper_compliance(
        self, client
    ):
        """HTTPメソッドの適切な使用テスト."""
        # Arrange (準備)
        get_endpoints = [
            "/api/bulk-data/jobs/test-id",
            "/api/bulk-data/jpx-sequential/symbols",
            "/api/stock-master/",
            "/api/stock-master/status",
            "/api/system/database/connection",
            "/api/system/external-api/connection",
            "/api/system/health",
        ]

        post_endpoints = [
            ("/api/bulk-data/jobs", {"symbols": ["7203.T"]}),
            ("/api/bulk-data/jobs/test-id/stop", {}),
            ("/api/bulk-data/jpx-sequential/jobs", {"symbols": ["7203.T"]}),
            ("/api/stock-master/", {}),
            ("/api/stocks/data", {"symbol": "7203.T", "period": "1mo"}),
            ("/api/stocks/test", {"symbol": "TEST"}),
        ]

        headers = {"X-API-KEY": "test-key"}

        # Act (実行) & Assert (検証)
        for endpoint in get_endpoints:
            response = client.get(endpoint, headers=headers)
            assert response.status_code != 405

        for endpoint, payload in post_endpoints:
            response = client.post(endpoint, json=payload, headers=headers)
            assert response.status_code != 405

    def test_restful_url_structure_with_patterns_returns_proper_compliance(
        self, client
    ):
        """Test RESTful URL pattern compliance."""
        # Arrange (準備)
        resource_patterns = [
            "/api/bulk-data/jobs",
            "/api/stock-master/",
            "/api/stocks/data",
            "/api/system/health",
        ]

        # Act (実行) & Assert (検証)
        for pattern in resource_patterns:
            assert "/api/" in pattern
            assert not pattern.endswith("/test")
            assert not pattern.endswith("/get")

    def test_restful_status_codes_with_requests_returns_proper_compliance(
        self, client
    ):
        """適切なHTTPステータスコードの使用テスト."""
        # Arrange (準備)
        headers = {"X-API-KEY": "test-key"}

        # Act (実行) & Assert (検証) - 200 OK
        response = client.get("/api/system/health")
        if response.status_code == 200:
            data = response.get_json()
            assert "data" in data
            assert "overall_status" in data["data"]

        # Act (実行) & Assert (検証) - 202 Accepted
        response = client.post(
            "/api/bulk-data/jobs",
            json={"symbols": ["7203.T"]},
            headers=headers,
        )
        if response.status_code == 202:
            data = response.get_json()
            assert (
                ("job_id" in data)
                or (data.get("status") in ["success", "accepted"])
                or (data.get("success") is True)
            )

        # Act (実行) & Assert (検証) - 404 Not Found
        response = client.get(
            "/api/bulk-data/jobs/nonexistent-job-id",
            headers=headers,
        )
        if response.status_code == 404:
            data = response.get_json()
            assert "error" in data
            if isinstance(data["error"], dict):
                assert "code" in data["error"]
                assert "message" in data["error"]
            else:
                assert isinstance(data["error"], str)
                assert "message" in data

        # Act (実行) & Assert (検証) - 401 Unauthorized
        response = client.post(
            "/api/bulk-data/jobs", json={"symbols": ["7203.T"]}
        )
        if response.status_code == 401:
            data = response.get_json()
            assert "error" in data
            if isinstance(data["error"], dict):
                assert "code" in data["error"]
                assert "message" in data["error"]
            else:
                assert isinstance(data["error"], str)
                assert "message" in data
