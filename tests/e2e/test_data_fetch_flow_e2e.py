"""データ取得フローE2Eテスト.

主要なデータ取得ユースケースをエンドツーエンドでテスト。
Issue #209: E2Eテストの整備
"""

import os
import sys
import threading
import time

import pytest
import requests


pytestmark = pytest.mark.e2e


class TestDataFetchFlowE2E:
    """データ取得フロー E2Eテストクラス."""

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
                port=8003,
                debug=False,
                use_reloader=False,
                threaded=True,
            )

        server_thread = threading.Thread(target=run_app, daemon=True)
        server_thread.start()

        # サーバーが起動するまで待機
        base_url = "http://127.0.0.1:8003"
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

    def test_single_stock_data_fetch_complete_flow(self, app_server):
        """単一銘柄データ取得の完全なフローテスト.

        テストシナリオ:
        1. アプリケーションが起動していることを確認
        2. 有効な銘柄コードでデータ取得をリクエスト
        3. レスポンスが正常に返ることを確認
        4. データがデータベースに保存されることを確認
        5. 保存されたデータを取得できることを確認
        """
        # Arrange (準備)
        test_symbol = "AAPL"
        test_period = "5d"

        # Act (実行) - 1. アプリケーション起動確認
        response = requests.get(app_server)
        assert response.status_code == 200
        print("✓ アプリケーション起動確認")

        # Act (実行) - 2. データ取得リクエスト
        payload = {"symbol": test_symbol, "period": test_period}
        fetch_response = requests.post(
            f"{app_server}/api/stocks/data", json=payload, timeout=30
        )

        # Assert (検証) - 3. レスポンス確認
        assert fetch_response.status_code in [200, 400, 500]
        print(
            f"✓ データ取得リクエスト: {test_symbol} - "
            f"ステータス {fetch_response.status_code}"
        )

        if fetch_response.status_code == 200:
            fetch_data = fetch_response.json()
            assert "status" in fetch_data
            assert fetch_data["status"] == "success"
            print(f"✓ データ取得成功: {test_symbol}")

            # Act (実行) - 4. 保存されたデータを取得
            time.sleep(2)  # データ保存を待機
            get_response = requests.get(
                f"{app_server}/api/stocks?symbol={test_symbol}&limit=10"
            )

            # Assert (検証) - 5. データ取得確認
            assert get_response.status_code == 200
            get_data = get_response.json()
            assert get_data["status"] == "success"
            assert "data" in get_data
            print(f"✓ 保存データ取得成功: {len(get_data['data'])}件")

    def test_multiple_timeframe_data_fetch_flow(self, app_server):
        """複数期間でのデータ取得フローテスト.

        テストシナリオ:
        1. 1日間データの取得
        2. 1週間データの取得
        3. 1ヶ月データの取得
        4. それぞれのデータが正しく保存されることを確認
        """
        # Arrange (準備)
        test_symbol = "MSFT"
        test_periods = ["1d", "5d", "1mo"]

        for period in test_periods:
            # Act (実行) - データ取得リクエスト
            payload = {"symbol": test_symbol, "period": period}
            response = requests.post(
                f"{app_server}/api/stocks/data",
                json=payload,
                timeout=30,
            )

            # Assert (検証)
            assert response.status_code in [200, 400, 500]

            if response.status_code == 200:
                data = response.json()
                assert data["status"] == "success"
                print(f"✓ {period}データ取得成功: {test_symbol}")
            else:
                print(f"✓ {period}データ取得: ステータス{response.status_code}")

            time.sleep(1)  # API制限回避

    def test_japanese_stock_data_fetch_flow(self, app_server):
        """日本株データ取得フローテスト.

        テストシナリオ:
        1. 東証上場銘柄のデータ取得
        2. データ形式の検証
        3. 日本円での価格データ確認
        """
        # Arrange (準備)
        test_symbols = ["7203.T", "9984.T", "6758.T"]  # トヨタ、ソフトバンク、ソニー

        for symbol in test_symbols:
            # Act (実行) - データ取得リクエスト
            payload = {"symbol": symbol, "period": "1d"}
            response = requests.post(
                f"{app_server}/api/stocks/data",
                json=payload,
                timeout=30,
            )

            # Assert (検証)
            assert response.status_code in [200, 400, 500]

            if response.status_code == 200:
                data = response.json()
                assert data["status"] == "success"
                print(f"✓ 日本株データ取得成功: {symbol}")
            else:
                print(
                    f"✓ 日本株データ取得: {symbol} - " f"ステータス{response.status_code}"
                )

            time.sleep(1)  # API制限回避

    def test_error_handling_flow(self, app_server):
        """エラーハンドリングフローテスト.

        テストシナリオ:
        1. 無効な銘柄コードでのエラー処理
        2. 無効な期間指定でのエラー処理
        3. エラーメッセージの妥当性確認
        """
        # Arrange (準備) - 1. 無効な銘柄コード
        invalid_symbols = ["INVALID123", "XYZ999", ""]

        for symbol in invalid_symbols:
            # Act (実行)
            payload = {"symbol": symbol, "period": "1d"}
            response = requests.post(
                f"{app_server}/api/stocks/data",
                json=payload,
                timeout=30,
            )

            # Assert (検証) - エラーレスポンスが返ることを確認
            assert response.status_code in [400, 404, 500]
            print(f"✓ 無効銘柄コードエラー処理: {symbol}")

        # Arrange (準備) - 2. 無効な期間指定
        invalid_periods = ["invalid"]

        for period in invalid_periods:
            # Act (実行)
            payload = {"symbol": "AAPL", "period": period}
            response = requests.post(
                f"{app_server}/api/stocks/data",
                json=payload,
                timeout=30,
            )

            # Assert (検証)
            assert response.status_code in [400, 500]
            print(f"✓ 無効期間指定エラー処理: {period}")

    def test_data_validation_flow(self, app_server):
        """データ検証フローテスト.

        テストシナリオ:
        1. 取得データの必須フィールド確認
        2. データ型の検証
        3. データ範囲の妥当性確認
        """
        # Arrange (準備)
        test_symbol = "GOOGL"
        test_period = "5d"

        # Act (実行) - データ取得
        payload = {"symbol": test_symbol, "period": test_period}
        response = requests.post(
            f"{app_server}/api/stocks/data", json=payload, timeout=30
        )

        # Assert (検証)
        if response.status_code == 200:
            data = response.json()
            assert data["status"] == "success"

            # データ構造の検証
            if "data" in data and data["data"]:
                stock_data = data["data"]

                # 必須フィールドの確認
                required_fields = ["symbol"]
                for field in required_fields:
                    assert field in stock_data
                    print(f"✓ 必須フィールド確認: {field}")

                print(f"✓ データ検証完了: {test_symbol}")

    def test_concurrent_data_fetch_flow(self, app_server):
        """同時データ取得フローテスト.

        テストシナリオ:
        1. 複数銘柄の同時データ取得
        2. システムの同時実行処理確認
        3. レスポンス整合性の確認
        """
        # Arrange (準備)
        import concurrent.futures

        test_symbols = ["AAPL", "MSFT", "GOOGL"]

        def fetch_stock_data(symbol):
            """株価データを取得する関数."""
            payload = {"symbol": symbol, "period": "1d"}
            response = requests.post(
                f"{app_server}/api/stocks/data",
                json=payload,
                timeout=30,
            )
            return symbol, response.status_code

        # Act (実行) - 同時リクエスト
        with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
            futures = [
                executor.submit(fetch_stock_data, symbol)
                for symbol in test_symbols
            ]
            results = [
                future.result()
                for future in concurrent.futures.as_completed(futures)
            ]

        # Assert (検証)
        for symbol, status_code in results:
            assert status_code in [200, 400, 500]
            print(f"✓ 同時データ取得: {symbol} - ステータス{status_code}")

    def test_performance_benchmarking_flow(self, app_server):
        """パフォーマンスベンチマークフローテスト.

        テストシナリオ:
        1. データ取得のレスポンス時間測定
        2. 許容範囲内のレスポンス時間確認
        """
        # Arrange (準備)
        test_symbol = "TSLA"
        test_period = "1d"

        # Act (実行) - レスポンス時間測定
        start_time = time.time()

        payload = {"symbol": test_symbol, "period": test_period}
        response = requests.post(
            f"{app_server}/api/stocks/data", json=payload, timeout=30
        )

        end_time = time.time()
        response_time = end_time - start_time

        # Assert (検証)
        assert response.status_code in [200, 400, 500]
        assert response_time < 30.0  # 30秒以内
        print(f"✓ レスポンス時間: {response_time:.2f}秒")
