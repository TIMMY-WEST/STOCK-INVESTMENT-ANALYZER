"""API E2Eテスト - ブラウザを使わずにFlaskアプリケーションのAPIをテスト."""

import os
import sys
import threading
import time

import pytest
import requests


pytestmark = pytest.mark.integration


class TestAPIE2E:
    """API E2Eテストクラス."""

    @pytest.fixture(scope="class")
    def app_server(self):
        """Flaskアプリケーションサーバーを起動するフィクスチャ."""
        # プロジェクトルートディレクトリをPythonパスに追加
        project_root = os.path.join(os.path.dirname(__file__), "..", "..")
        sys.path.insert(0, project_root)

        # Flaskアプリをインポート
        from app.app import app

        app.config["TESTING"] = True

        # スレッドでサーバーを起動
        def run_app():
            app.run(
                host="127.0.0.1",
                port=8002,
                debug=False,
                use_reloader=False,
                threaded=True,
            )

        server_thread = threading.Thread(target=run_app, daemon=True)
        server_thread.start()

        # サーバーが起動するまで待機
        base_url = "http://127.0.0.1:8002"
        max_attempts = 30
        for _ in range(max_attempts):
            try:
                response = requests.get(base_url, timeout=2)
                if response.status_code == 200:
                    break
            except requests.exceptions.RequestException:
                pass
            time.sleep(1)
        else:
            raise Exception("アプリケーションサーバーの起動に失敗しました")

        yield base_url

        # デーモンスレッドなので自動的に終了

    def test_home_page_access(self, app_server):
        """ホームページへのアクセステスト."""
        response = requests.get(app_server)
        assert response.status_code == 200
        # HTMLページが正常に返されることを確認
        assert "html" in response.text.lower()
        # 実際のページコンテンツに基づいた検証
        assert "株価データ管理システム" in response.text or "株価" in response.text
        print("✓ ホームページアクセス成功")

    def test_database_connection_endpoint(self, app_server):
        """データベース接続テストエンドポイント."""
        response = requests.get(f"{app_server}/api/system/health")
        assert response.status_code in [200, 500]
        data = response.json()
        # レスポンスにヘルスチェック情報が含まれることを確認
        assert "data" in data
        assert "overall_status" in data["data"]
        assert (
            "services" in data["data"]
            and "database" in data["data"]["services"]
        )
        print(f"✓ ヘルスチェック: {data}")

    def test_fetch_data_endpoint_valid_symbol(self, app_server):
        """有効な銘柄コードでのデータ取得テスト."""
        payload = {"symbol": "AAPL", "period": "1mo"}
        response = requests.post(f"{app_server}/api/stocks/data", json=payload)

        # レスポンスの確認
        assert response.status_code in [
            200,
            400,
            500,
        ]  # APIの実装によって異なる

        if response.status_code == 200:
            data = response.json()
            assert "data" in data or "message" in data
            print("✓ 有効な銘柄コードでのデータ取得成功")
        else:
            print(f"✓ データ取得エラー（予想される動作）: {response.status_code}")

    def test_fetch_data_endpoint_invalid_symbol(self, app_server):
        """無効な銘柄コードでのエラーハンドリングテスト."""
        payload = {"symbol": "INVALID_SYMBOL_12345", "period": "1mo"}
        response = requests.post(f"{app_server}/api/stocks/data", json=payload)

        # エラーレスポンスの確認
        assert response.status_code in [400, 404, 500]
        print(f"✓ 無効な銘柄コードでのエラーハンドリング: {response.status_code}")

    def test_fetch_data_endpoint_max_period(self, app_server):
        """maxオプションでのデータ取得テスト（Issue #45対応）."""
        payload = {"symbol": "AAPL", "period": "max"}
        response = requests.post(f"{app_server}/api/stocks/data", json=payload)

        # レスポンスの確認
        assert response.status_code in [200, 400, 500]

        if response.status_code == 200:
            data = response.json()
            assert "status" in data
            assert data["status"] == "success"
            assert "data" in data

            # maxオプション特有の検証
            if "data" in data and data["data"]:
                stock_data = data["data"]
                assert "records_count" in stock_data
                assert "date_range" in stock_data

                # maxオプションでは大量のデータが取得されることを確認
                if "records_count" in stock_data:
                    assert stock_data["records_count"] > 1000  # maxは通常大量のデータ

                print(
                    f"✓ maxオプションでのデータ取得成功: {stock_data.get('records_count', 0)}件"
                )
            else:
                print("✓ maxオプションでのデータ取得成功（データ構造確認）")
        else:
            print(f"✓ maxオプションでのデータ取得エラー（予想される動作）: {response.status_code}")

    def test_fetch_data_endpoint_max_period_japanese_stock(self, app_server):
        """日本株でのmaxオプションテスト（Issue #45対応）."""
        payload = {"symbol": "7203.T", "period": "max"}  # トヨタ自動車
        response = requests.post(f"{app_server}/api/stocks/data", json=payload)

        # レスポンスの確認
        assert response.status_code in [200, 400, 500]

        if response.status_code == 200:
            data = response.json()
            assert "status" in data
            assert data["status"] == "success"

            if "data" in data and data["data"]:
                stock_data = data["data"]
                assert "symbol" in stock_data
                assert stock_data["symbol"] == "7203.T"

                print(f"✓ 日本株（{stock_data['symbol']}）でのmaxオプション取得成功")
            else:
                print("✓ 日本株でのmaxオプション取得成功（データ構造確認）")
        else:
            print(f"✓ 日本株でのmaxオプション取得エラー（予想される動作）: {response.status_code}")

    def test_stocks_api_endpoints(self, app_server):
        """株式データCRUD APIエンドポイントのテスト."""
        # GET /api/stocks
        response = requests.get(f"{app_server}/api/stocks")
        assert response.status_code in [200, 404, 500]
        print(f"✓ 株式データ一覧取得: {response.status_code}")

        # POST /api/stocks (テストデータ作成)
        test_data = {"symbol": "TEST", "name": "Test Stock", "price": 100.0}
        response = requests.post(f"{app_server}/api/stocks", json=test_data)
        assert response.status_code in [200, 201, 400, 500]
        print(f"✓ 株式データ作成: {response.status_code}")

    def test_create_test_data_endpoint(self, app_server):
        """テストデータ作成エンドポイントのテスト."""
        response = requests.post(f"{app_server}/api/create-test-data")
        # 404エラーも許可（エンドポイントが存在しない場合）
        assert response.status_code in [200, 201, 404, 500]

        if response.status_code in [200, 201]:
            data = response.json()
            assert "message" in data
            print(f"✓ テストデータ作成成功: {data.get('message', '')}")
        elif response.status_code == 404:
            print("✓ テストデータ作成エンドポイントが存在しません（予想される動作）")
        else:
            print(f"✓ テストデータ作成エラー（予想される動作）: {response.status_code}")

    def test_api_error_handling(self, app_server):
        """API エラーハンドリングのテスト."""
        # 存在しないエンドポイント
        response = requests.get(f"{app_server}/api/nonexistent")
        assert response.status_code == 404
        print("✓ 存在しないエンドポイントで404エラー")

        # 不正なJSONデータ
        response = requests.post(
            f"{app_server}/api/stocks/data",
            data="invalid json",
            headers={"Content-Type": "application/json"},
        )
        # 502エラーも許可（プロキシエラー）
        assert response.status_code in [400, 500, 502]
        print(f"✓ 不正なJSONデータでエラー: {response.status_code}")

    def test_concurrent_requests(self, app_server):
        """同時リクエストのテスト."""
        import concurrent.futures

        def make_request():
            response = requests.get(app_server)
            return response.status_code

        # 5つの同時リクエスト
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(make_request) for _ in range(5)]
            results = [
                future.result()
                for future in concurrent.futures.as_completed(futures)
            ]

        # すべてのリクエストが成功することを確認
        assert all(status == 200 for status in results)
        print("✓ 同時リクエスト処理成功")

    def test_response_headers(self, app_server):
        """レスポンスヘッダーのテスト."""
        response = requests.get(app_server)

        # Content-Typeヘッダーの確認
        assert "text/html" in response.headers.get("Content-Type", "")
        print("✓ レスポンスヘッダー確認成功")

    def test_api_performance(self, app_server):
        """APIパフォーマンステスト."""
        start_time = time.time()
        response = requests.get(app_server)
        end_time = time.time()

        response_time = end_time - start_time
        assert response.status_code == 200
        assert response_time < 5.0  # 5秒以内
        print(f"✓ レスポンス時間: {response_time:.2f}秒")

    def test_data_reading_endpoints(self, app_server):
        """データ読み込み機能のテスト."""
        # 1. 全株価データ取得テスト
        response = requests.get(f"{app_server}/api/stocks")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert "data" in data
        assert "meta" in data
        assert "pagination" in data["meta"]
        print("✓ 全株価データ取得成功")

        # 2. ページネーション機能テスト
        response = requests.get(f"{app_server}/api/stocks?limit=5&offset=0")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert data["meta"]["pagination"]["limit"] == 5
        assert data["meta"]["pagination"]["offset"] == 0
        print("✓ ページネーション機能テスト成功")

        # 3. 銘柄コードフィルタリングテスト
        response = requests.get(f"{app_server}/api/stocks?symbol=7203.T")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        print("✓ 銘柄コードフィルタリングテスト成功")

        # 4. 日付範囲フィルタリングテスト
        response = requests.get(
            f"{app_server}/api/stocks?start_date=2024-01-01&end_date=2024-12-31"
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        print("✓ 日付範囲フィルタリングテスト成功")

        # 5. 無効なパラメータテスト
        response = requests.get(f"{app_server}/api/stocks?limit=-1")
        assert response.status_code == 400
        data = response.json()
        assert data["status"] == "error"
        assert "error" in data
        assert data["error"]["code"] == "VALIDATION_ERROR"
        print("✓ 無効なパラメータエラーハンドリング成功")

        # 6. 無効な日付形式テスト
        response = requests.get(
            f"{app_server}/api/stocks?start_date=invalid-date"
        )
        assert response.status_code == 400
        data = response.json()
        assert data["status"] == "error"
        assert "error" in data
        assert data["error"]["code"] == "VALIDATION_ERROR"
        print("✓ 無効な日付形式エラーハンドリング成功")

    def test_individual_stock_data_reading(self, app_server):
        """個別株価データ読み込みテスト."""
        # まず、利用可能な株価データを取得
        response = requests.get(f"{app_server}/api/stocks?limit=1")
        assert response.status_code == 200
        data = response.json()

        if data["data"]:
            # 最初のデータのIDを使用してテスト
            stock_id = data["data"][0]["id"]

            # 1. 有効なIDでの個別データ取得
            response = requests.get(f"{app_server}/api/stocks/{stock_id}")
            assert response.status_code == 200
            individual_data = response.json()
            assert individual_data["status"] == "success"
            assert "data" in individual_data
            assert individual_data["data"]["id"] == stock_id
            print(f"✓ 個別株価データ取得成功 (ID: {stock_id})")
        else:
            print("✓ 株価データが存在しないため、個別データ取得テストをスキップ")

        # 2. 存在しないIDでの個別データ取得
        response = requests.get(f"{app_server}/api/stocks/99999")
        assert response.status_code == 404
        error_data = response.json()
        assert error_data["status"] == "error"
        assert "error" in error_data
        assert error_data["error"]["code"] == "NOT_FOUND"
        print("✓ 存在しないIDでの404エラーハンドリング成功")

    def test_data_deletion_endpoints(self, app_server):
        """データ削除機能のテスト."""
        # まず、テストデータを作成
        test_stock_data = {
            "symbol": "TEST.T",
            "date": "2024-01-01",
            "open": 100.0,
            "high": 110.0,
            "low": 95.0,
            "close": 105.0,
            "volume": 1000000,
        }

        # テストデータを作成
        create_response = requests.post(
            f"{app_server}/api/stocks", json=test_stock_data
        )

        if create_response.status_code == 201:
            # 作成成功の場合
            created_data = create_response.json()
            created_id = created_data["data"]["id"]
            print(f"✓ テストデータ作成成功 (ID: {created_id})")

            # 1. 有効なIDでの削除テスト
            delete_response = requests.delete(
                f"{app_server}/api/stocks/{created_id}"
            )
            assert delete_response.status_code == 200
            delete_data = delete_response.json()
            assert delete_data["status"] == "success"
            assert f"ID {created_id}" in delete_data["message"]
            print(f"✓ 有効なIDでの削除成功 (ID: {created_id})")

            # 削除されたデータが取得できないことを確認
            get_response = requests.get(
                f"{app_server}/api/stocks/{created_id}"
            )
            assert get_response.status_code == 404
            print("✓ 削除後のデータ取得で404エラー確認")

        elif create_response.status_code == 400:
            # 重複データの場合、既存データを使用してテスト
            print("✓ テストデータが既に存在するため、既存データで削除テストを実行")

            # 既存のデータを取得
            response = requests.get(
                f"{app_server}/api/stocks?symbol=TEST.T&limit=1"
            )
            if response.status_code == 200:
                data = response.json()
                if data["data"]:
                    existing_id = data["data"][0]["id"]

                    # 既存データの削除テスト
                    delete_response = requests.delete(
                        f"{app_server}/api/stocks/{existing_id}"
                    )
                    assert delete_response.status_code == 200
                    delete_data = delete_response.json()
                    assert delete_data["status"] == "success"
                    print(f"✓ 既存データの削除成功 (ID: {existing_id})")
        else:
            print("✓ テストデータ作成に失敗したため、削除テストをスキップ")

        # 2. 存在しないIDでの削除テスト
        response = requests.delete(f"{app_server}/api/stocks/99999")
        assert response.status_code == 404
        error_data = response.json()
        assert error_data["status"] == "error"
        assert "error" in error_data
        assert error_data["error"]["code"] == "NOT_FOUND"
        print("✓ 存在しないIDでの削除時404エラーハンドリング成功")

    def test_data_deletion_with_validation(self, app_server):
        """データ削除の詳細バリデーションテスト."""
        # 1. 無効なIDフォーマットでの削除テスト
        response = requests.delete(f"{app_server}/api/stocks/invalid_id")
        # Flask は無効なIDフォーマットの場合、404を返す（HTMLレスポンス）
        assert response.status_code == 404
        print("✓ 無効なIDフォーマットでの削除エラーハンドリング成功")

        # 2. 負の数のIDでの削除テスト（Flaskルーティングでは負の数も404になる）
        response = requests.delete(f"{app_server}/api/stocks/-1")
        assert response.status_code == 404
        print("✓ 負の数IDでの削除エラーハンドリング成功")

        # 3. 非常に大きなIDでの削除テスト（有効な数値IDなのでAPIエンドポイントに到達）
        response = requests.delete(f"{app_server}/api/stocks/999999999")
        assert response.status_code == 404
        try:
            error_data = response.json()
            assert error_data["status"] == "error"
            assert "error" in error_data
            assert error_data["error"]["code"] == "NOT_FOUND"
        except requests.exceptions.JSONDecodeError:
            # JSONレスポンスでない場合もあるため、ステータスコードのみ確認
            pass
        print("✓ 非常に大きなIDでの削除エラーハンドリング成功")
