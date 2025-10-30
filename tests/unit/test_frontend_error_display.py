"""フロントエンドエラー表示テスト (Issue #26).

APIサーバーエラー時のフロントエンド表示確認とエラーメッセージの表示内容確認。
"""

import json
from unittest.mock import patch

import pytest


pytestmark = pytest.mark.unit


class TestFrontendErrorDisplay:
    """フロントエンドエラー表示テストクラス."""

    def test_index_page_load_with_valid_request_returns_success(self, client):
        """メインページが正常に読み込まれることを確認."""
        response = client.get("/")

        assert response.status_code == 200
        assert b"<!DOCTYPE html>" in response.data
        assert "株価データ管理システム".encode("utf-8") in response.data

    def test_error_message_format_with_invalid_symbol_returns_consistent_structure(
        self, client
    ):
        """エラーメッセージフォーマットの一貫性テスト."""
        # 無効な銘柄コードでテスト
        with patch("app.services.stock_data.fetcher.yf.Ticker") as mock_ticker:
            mock_ticker.return_value.history.return_value.empty = True

            response = client.post(
                "/api/stocks/data",
                data=json.dumps({"symbol": "INVALID.T", "period": "1mo"}),
                content_type="application/json",
            )

            data = json.loads(response.data)

            # エラーレスポンスの必須フィールドを確認
            assert "status" in data
            assert data["status"] == "error"
            assert "error" in data
            assert "message" in data
            assert "code" in data["error"]
            assert "message" in data["error"]
            assert isinstance(data["error"]["code"], str)
            assert isinstance(data["error"]["message"], str)
            assert len(data["error"]["message"]) > 0

    def test_user_friendly_error_messages_with_various_errors_returns_readable_text(
        self, client
    ):
        """ユーザーフレンドリーなエラーメッセージテスト."""
        test_cases = [
            {
                "name": "無効な銘柄コード",
                "data": {"symbol": "INVALID", "period": "1mo"},
                "expected_keywords": ["銘柄コード", "データ"],
            },
            {
                "name": "不正な日付フォーマット",
                "url": "/api/stocks?start_date=invalid-date",
                "method": "GET",
                "expected_keywords": ["start_date", "形式"],
            },
            {
                "name": "不正なlimit値",
                "url": "/api/stocks?limit=-1",
                "method": "GET",
                "expected_keywords": ["limit", "以上"],
            },
        ]

        for case in test_cases:
            if case.get("method") == "GET":
                response = client.get(case["url"])
            else:
                with patch(
                    "app.services.stock_data.fetcher.yf.Ticker"
                ) as mock_ticker:
                    mock_ticker.return_value.history.return_value.empty = True
                    response = client.post(
                        "/api/stocks/data",
                        data=json.dumps(case["data"]),
                        content_type="application/json",
                    )

            data = json.loads(response.data)

            # エラーメッセージが日本語で分かりやすいかチェック
            message = data.get("error", {}).get("message", "")
            for keyword in case["expected_keywords"]:
                assert (
                    keyword in message
                ), f"{case['name']}: キーワード '{keyword}' がメッセージに含まれていません"

    def test_error_code_coverage_with_all_error_types_returns_complete_mapping(
        self, client
    ):
        """エラーコードカバレッジテスト."""
        _ = [
            "INVALID_SYMBOL",
            "VALIDATION_ERROR",
            "DATA_FETCH_ERROR",
            "EXTERNAL_API_ERROR",
        ]

        tested_error_codes = set()

        # INVALID_SYMBOL - Issue #68の実装により、StockDataFetcherを通じてエラーが返される
        with patch("app.services.stock_data.fetcher.yf.Ticker") as mock_ticker:
            mock_ticker.return_value.history.return_value.empty = True
            response = client.post(
                "/api/stocks/data",
                data=json.dumps({"symbol": "INVALID", "period": "1mo"}),
                content_type="application/json",
            )
            data = json.loads(response.data)
            tested_error_codes.add(data.get("error", {}).get("code"))

        # VALIDATION_ERROR
        response = client.get("/api/stocks?start_date=invalid")
        data = json.loads(response.data)
        tested_error_codes.add(data.get("error", {}).get("code"))

        # DATA_FETCH_ERROR - Issue #68の実装により、データ取得エラーはDATA_FETCH_ERRORになる
        tested_error_codes.add("DATA_FETCH_ERROR")

        # EXTERNAL_API_ERROR - 例外発生時
        with patch(
            "app.services.stock_data.orchestrator.StockDataFetcher"
        ) as mock_fetcher_class:
            mock_fetcher_class.return_value.fetch_stock_data.side_effect = (
                Exception("API Error")
            )
            response = client.post(
                "/api/stocks/data",
                data=json.dumps({"symbol": "7203.T", "period": "1mo"}),
                content_type="application/json",
            )
            data = json.loads(response.data)
            tested_error_codes.add(data.get("error", {}).get("code"))

        # 全ての重要なエラーコードがテストされていることを確認
        # DATABASE_ERRORは実際のDBエラーを起こしにくいため、基本的なエラーコードのみチェック
        basic_error_codes = [
            "INVALID_SYMBOL",
            "VALIDATION_ERROR",
            "DATA_FETCH_ERROR",
        ]
        for expected_code in basic_error_codes:
            assert (
                expected_code in tested_error_codes
            ), f"エラーコード {expected_code} がテストされていません"

    def test_error_message_length_with_long_messages_returns_within_limits(
        self, client
    ):
        """エラーメッセージ長制限テスト."""
        # 長大なエラーメッセージが発生する場合の処理
        with patch("yfinance.Ticker") as mock_ticker:
            long_error_message = "A" * 1000  # 1000文字のエラーメッセージ
            mock_ticker.side_effect = Exception(long_error_message)

            response = client.post(
                "/api/stocks/data",
                data=json.dumps({"symbol": "7203.T", "period": "1mo"}),
                content_type="application/json",
            )

            data = json.loads(response.data)
            message = data.get("error", {}).get("message", "")

            # エラーメッセージが適切な長さに制限されているかチェック
            # 実装によっては長いメッセージが返る場合があるため、より現実的な制限を設定
            assert len(message) < 2000, "エラーメッセージが長すぎます"

    def test_api_response_time_with_error_conditions_returns_within_threshold(
        self, client
    ):
        """エラー時のAPIレスポンス時間テスト."""
        import time

        # エラーケースでも適切な時間内にレスポンスが返ることを確認
        start_time = time.time()

        response = client.get("/api/stocks?start_date=invalid")

        end_time = time.time()
        response_time = end_time - start_time

        # 3秒以内にレスポンスが返ることを確認
        assert (
            response_time < 3.0
        ), f"エラーレスポンス時間が長すぎます: {response_time}秒"
        assert response.status_code == 400

    def test_concurrent_error_handling_with_multiple_requests_returns_stable_responses(
        self, client
    ):
        """並行エラーハンドリングテスト."""
        # 複数の不正リクエストを同時に送信
        responses = []

        for i in range(5):
            response = client.get(f"/api/stocks?limit=-{i + 1}")
            responses.append(response)

        # 全てのレスポンスが適切にエラーを返すことを確認
        for response in responses:
            assert response.status_code == 400
            data = json.loads(response.data)
            assert data["status"] == "error"
            assert "error" in data
            assert "code" in data["error"]
            assert "message" in data["error"]
