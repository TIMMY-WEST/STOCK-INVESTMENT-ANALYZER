"""app.utils.api_response モジュールの単体テスト."""

import json

from flask import Flask
import pytest

from app.utils.api_response import APIResponse, ErrorCode


# Note: conftest.py にも app フィクスチャがありますが、
# このテストは最小限のアプリケーションコンテキストのみが必要なため、
# 軽量な専用フィクスチャを保持します
pytestmark = pytest.mark.unit


@pytest.fixture
def app():
    """Flaskアプリケーションのフィクスチャ（最小限）."""
    app = Flask(__name__)
    return app


class TestAPIResponse:
    """APIResponseクラスのテスト."""

    @pytest.mark.parametrize(
        "kwargs,expected_fields",
        [
            # 最小限の成功レスポンス
            ({}, {"status": "success"}),
            # データ付き成功レスポンス
            (
                {"data": {"key": "value", "number": 123}},
                {"status": "success", "data": {"key": "value", "number": 123}},
            ),
            # メッセージ付き成功レスポンス
            (
                {"message": "操作が成功しました"},
                {"status": "success", "message": "操作が成功しました"},
            ),
            # メタデータ付き成功レスポンス
            (
                {"meta": {"total": 100, "timestamp": "2024-01-01T00:00:00Z"}},
                {
                    "status": "success",
                    "meta": {
                        "total": 100,
                        "timestamp": "2024-01-01T00:00:00Z",
                    },
                },
            ),
        ],
    )
    def test_success_response_variations(self, app, kwargs, expected_fields):
        """成功レスポンスのパラメータ化テスト.

        様々なパラメータでの成功レスポンスをテストします。
        """
        with app.app_context():
            # Arrange & Act (準備・実行)
            response, status_code = APIResponse.success(**kwargs)

            # Assert (検証)
            assert status_code == 200
            data = json.loads(response.data)

            # expected_fields に含まれるフィールドを検証
            for key, value in expected_fields.items():
                assert data[key] == value

            # data, message, meta が kwargs にない場合は、レスポンスにも含まれないことを確認
            if "data" not in kwargs:
                assert "data" not in data or data.get("data") is None
            if "message" not in kwargs:
                assert "message" not in data or data.get("message") is None
            if "meta" not in kwargs:
                assert "meta" not in data or data.get("meta") is None

    def test_error_response_basic(self, app):
        """基本的なエラーレスポンスのテスト."""
        with app.app_context():
            # Arrange (準備)
            error_code = ErrorCode.INVALID_PARAMETER
            message = "パラメータが無効です"

            # Act (実行)
            response, status_code = APIResponse.error(error_code, message)

            # Assert (検証)
            assert status_code == 400
            data = json.loads(response.data)
            assert data["status"] == "error"
            assert data["error"]["code"] == error_code
            assert data["error"]["message"] == message
            assert "details" not in data["error"]

    def test_error_response_with_details(self, app):
        """詳細情報付きエラーレスポンスのテスト."""
        with app.app_context():
            # Arrange (準備)
            error_code = ErrorCode.VALIDATION_ERROR
            message = "バリデーションエラー"
            details = {"field": "email", "reason": "無効な形式"}

            # Act (実行)
            response, status_code = APIResponse.error(
                error_code, message, details, status_code=422
            )

            # Assert (検証)
            assert status_code == 422
            data = json.loads(response.data)
            assert data["status"] == "error"
            assert data["error"]["code"] == error_code
            assert data["error"]["message"] == message
            assert data["error"]["details"] == details

    def test_paginated_response(self, app):
        """ページネーション付きレスポンスのテスト."""
        with app.app_context():
            # Arrange (準備)
            test_data = [{"id": 1}, {"id": 2}, {"id": 3}]
            total = 10
            limit = 3
            offset = 0

            # Act (実行)
            response, status_code = APIResponse.paginated(
                data=test_data, total=total, limit=limit, offset=offset
            )

            # Assert (検証)
            assert status_code == 200
            data = json.loads(response.data)
            assert data["status"] == "success"
            assert data["data"] == test_data
            assert "meta" in data
            assert "pagination" in data["meta"]

            pagination = data["meta"]["pagination"]
            assert pagination["total"] == total
            assert pagination["limit"] == limit
            assert pagination["offset"] == offset
            assert pagination["count"] == len(test_data)
            assert pagination["has_next"] is True
            assert pagination["has_prev"] is False

    def test_paginated_response_last_page(self, app):
        """最終ページのページネーションレスポンスのテスト."""
        with app.app_context():
            # Arrange (準備)
            test_data = [{"id": 8}, {"id": 9}, {"id": 10}]
            total = 10
            limit = 3
            offset = 7

            # Act (実行)
            response, status_code = APIResponse.paginated(
                data=test_data, total=total, limit=limit, offset=offset
            )

            # Assert (検証)
            assert status_code == 200
            data = json.loads(response.data)
            pagination = data["meta"]["pagination"]
            assert pagination["has_next"] is False
            assert pagination["has_prev"] is True

    def test_paginated_response_with_meta(self, app):
        """追加メタデータ付きページネーションレスポンスのテスト."""
        with app.app_context():
            # Arrange (準備)
            test_data = [{"id": 1}]
            meta = {"interval": "1d", "table_name": "stocks_1d"}

            # Act (実行)
            response, status_code = APIResponse.paginated(
                data=test_data, total=1, limit=10, offset=0, meta=meta
            )

            # Assert (検証)
            assert status_code == 200
            data = json.loads(response.data)
            assert "pagination" in data["meta"]
            assert data["meta"]["interval"] == "1d"
            assert data["meta"]["table_name"] == "stocks_1d"


class TestErrorCode:
    """ErrorCodeクラスのテスト."""

    def test_error_codes_exist(self):
        """主要なエラーコードが定義されているかテスト."""
        # Arrange (準備)
        # ErrorCodeクラスの属性チェックを準備

        # Act (実行)
        # 各エラーコードの属性存在をチェック

        # Assert (検証)
        assert hasattr(ErrorCode, "VALIDATION_ERROR")
        assert hasattr(ErrorCode, "INVALID_SYMBOL")
        assert hasattr(ErrorCode, "DATABASE_ERROR")
        assert hasattr(ErrorCode, "EXTERNAL_API_ERROR")
        assert hasattr(ErrorCode, "NOT_FOUND")
        assert hasattr(ErrorCode, "UNAUTHORIZED")
        assert hasattr(ErrorCode, "INTERNAL_SERVER_ERROR")

    def test_error_code_values(self):
        """エラーコードの値が正しいかテスト."""
        # Arrange (準備)
        # ErrorCodeクラスの値チェックを準備

        # Act (実行)
        # 各エラーコードの値を取得

        # Assert (検証)
        assert ErrorCode.VALIDATION_ERROR == "VALIDATION_ERROR"
        assert ErrorCode.INVALID_SYMBOL == "INVALID_SYMBOL"
        assert ErrorCode.DATABASE_ERROR == "DATABASE_ERROR"
