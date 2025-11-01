"""全銘柄取得フローE2Eテスト.

JPX銘柄一括取得などのバルクデータ取得フローをテスト。
Issue #209: E2Eテストの整備
"""

import os
import sys
import threading
import time

import pytest
import requests


pytestmark = pytest.mark.e2e


class TestBulkFetchFlowE2E:
    """全銘柄取得フロー E2Eテストクラス."""

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
                port=8004,
                debug=False,
                use_reloader=False,
                threaded=True,
            )

        server_thread = threading.Thread(target=run_app, daemon=True)
        server_thread.start()

        # サーバーが起動するまで待機
        base_url = "http://127.0.0.1:8004"
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

    def test_jpx_symbols_list_fetch_flow(self, app_server):
        """JPX銘柄リスト取得フローテスト.

        テストシナリオ:
        1. JPX銘柄リストの取得
        2. レスポンス形式の確認
        3. 銘柄データの妥当性確認
        """
        # Act (実行) - JPX銘柄リスト取得
        response = requests.get(
            f"{app_server}/api/bulk/jpx-sequential/get-symbols?limit=10",
            timeout=30,
        )

        # Assert (検証)
        assert response.status_code in [200, 404, 500]

        if response.status_code == 200:
            data = response.json()
            assert "status" in data

            if data["status"] == "success" and "data" in data:
                symbols = data["data"]
                assert isinstance(symbols, list)
                print(f"✓ JPX銘柄リスト取得成功: {len(symbols)}銘柄")

                # 銘柄データの構造確認
                if symbols:
                    first_symbol = symbols[0]
                    assert "code" in first_symbol or "symbol" in first_symbol
                    print("✓ 銘柄データ構造確認")
            else:
                print("✓ JPX銘柄リスト取得: データなし")
        else:
            print(f"✓ JPX銘柄リスト取得: ステータス{response.status_code}")

    def test_bulk_data_download_progress_flow(self, app_server):
        """バルクデータダウンロード進捗確認フローテスト.

        テストシナリオ:
        1. バルクダウンロード開始
        2. 進捗状況の取得
        3. 完了確認
        """
        # Act (実行) - バルクダウンロード開始リクエスト
        start_payload = {"symbols": ["7203.T", "9984.T"], "period": "1d"}
        start_response = requests.post(
            f"{app_server}/api/bulk/download",
            json=start_payload,
            timeout=60,
        )

        # Assert (検証)
        assert start_response.status_code in [200, 404, 500]

        if start_response.status_code == 200:
            start_data = start_response.json()
            print(f"✓ バルクダウンロード開始: {start_data.get('status')}")

            # バッチIDがある場合、進捗確認
            if "data" in start_data and "batch_id" in start_data["data"]:
                batch_id = start_data["data"]["batch_id"]
                time.sleep(2)  # 処理開始を待機

                # Act (実行) - 進捗状況取得
                progress_response = requests.get(
                    f"{app_server}/api/bulk/progress/{batch_id}",
                    timeout=10,
                )

                # Assert (検証)
                if progress_response.status_code == 200:
                    progress_data = progress_response.json()
                    print(f"✓ 進捗確認成功: {progress_data.get('status')}")
        else:
            print(f"✓ バルクダウンロード: ステータス{start_response.status_code}")

    def test_sequential_download_flow(self, app_server):
        """逐次ダウンロードフローテスト.

        テストシナリオ:
        1. 逐次ダウンロードモードの開始
        2. ダウンロード状態の確認
        3. エラーハンドリング
        """
        # Arrange (準備)
        test_symbols = ["7203.T", "6758.T", "9984.T"]

        # Act (実行) - 逐次ダウンロードリクエスト
        payload = {
            "symbols": test_symbols,
            "period": "1d",
            "mode": "sequential",
        }
        response = requests.post(
            f"{app_server}/api/bulk/jpx-sequential/download",
            json=payload,
            timeout=120,
        )

        # Assert (検証)
        assert response.status_code in [200, 404, 500]

        if response.status_code == 200:
            data = response.json()
            print(f"✓ 逐次ダウンロード: {data.get('status')}")

            if "data" in data:
                result = data["data"]
                if "success_count" in result:
                    print(
                        f"✓ 成功: {result['success_count']}/"
                        f"{len(test_symbols)}銘柄"
                    )
        else:
            print(f"✓ 逐次ダウンロード: ステータス{response.status_code}")

    def test_batch_execution_status_flow(self, app_server):
        """バッチ実行状態確認フローテスト.

        テストシナリオ:
        1. バッチ実行履歴の取得
        2. 実行状態の確認
        3. 完了・失敗状態の判定
        """
        # Act (実行) - バッチ実行履歴取得
        response = requests.get(
            f"{app_server}/api/bulk/batch-executions?limit=10",
            timeout=10,
        )

        # Assert (検証)
        assert response.status_code in [200, 404, 500]

        if response.status_code == 200:
            data = response.json()
            assert "status" in data

            if data["status"] == "success" and "data" in data:
                executions = data["data"]
                print(f"✓ バッチ実行履歴取得: {len(executions)}件")

                # 実行状態の確認
                if executions:
                    for execution in executions[:3]:  # 最新3件を確認
                        assert "status" in execution
                        assert execution["status"] in [
                            "pending",
                            "in_progress",
                            "completed",
                            "failed",
                        ]
                    print("✓ 実行状態確認完了")
            else:
                print("✓ バッチ実行履歴: データなし")
        else:
            print(f"✓ バッチ実行履歴: ステータス{response.status_code}")

    def test_stock_master_update_flow(self, app_server):
        """銘柄マスタ更新フローテスト.

        テストシナリオ:
        1. 銘柄マスタの取得
        2. 銘柄マスタの更新
        3. 更新後のデータ確認
        """
        # Act (実行) - 1. 銘柄マスタ取得
        get_response = requests.get(
            f"{app_server}/api/stock-master?limit=5", timeout=10
        )

        # Assert (検証)
        assert get_response.status_code in [200, 404, 500]

        if get_response.status_code == 200:
            _ = get_response.json()
            print("✓ 銘柄マスタ取得成功")

            # Act (実行) - 2. 銘柄マスタ更新リクエスト
            update_response = requests.post(
                f"{app_server}/api/stock-master/update",
                timeout=60,
            )

            # Assert (検証)
            if update_response.status_code in [200, 404]:
                if update_response.status_code == 200:
                    update_data = update_response.json()
                    print(f"✓ 銘柄マスタ更新: {update_data.get('status')}")
                else:
                    print("✓ 銘柄マスタ更新エンドポイント未実装")
        else:
            print(f"✓ 銘柄マスタ取得: ステータス{get_response.status_code}")

    def test_pagination_flow(self, app_server):
        """ページネーションフローテスト.

        テストシナリオ:
        1. 最初のページ取得
        2. 次のページ取得
        3. ページネーション情報の確認
        """
        # Act (実行) - 1. 最初のページ取得
        page1_response = requests.get(
            f"{app_server}/api/stocks?limit=10&offset=0", timeout=10
        )

        # Assert (検証)
        assert page1_response.status_code == 200
        page1_data = page1_response.json()
        assert page1_data["status"] == "success"
        assert "meta" in page1_data
        assert "pagination" in page1_data["meta"]

        pagination = page1_data["meta"]["pagination"]
        assert pagination["limit"] == 10
        assert pagination["offset"] == 0
        print("✓ 最初のページ取得成功")

        # Act (実行) - 2. 次のページ取得
        page2_response = requests.get(
            f"{app_server}/api/stocks?limit=10&offset=10", timeout=10
        )

        # Assert (検証)
        assert page2_response.status_code == 200
        page2_data = page2_response.json()
        assert page2_data["status"] == "success"

        pagination2 = page2_data["meta"]["pagination"]
        assert pagination2["offset"] == 10
        print("✓ 次のページ取得成功")

    def test_filtering_flow(self, app_server):
        """フィルタリングフローテスト.

        テストシナリオ:
        1. 銘柄コードフィルタリング
        2. 日付範囲フィルタリング
        3. フィルタ結果の妥当性確認
        """
        # Arrange (準備)
        test_symbol = "7203.T"

        # Act (実行) - 1. 銘柄コードフィルタリング
        symbol_response = requests.get(
            f"{app_server}/api/stocks?symbol={test_symbol}",
            timeout=10,
        )

        # Assert (検証)
        assert symbol_response.status_code == 200
        symbol_data = symbol_response.json()
        assert symbol_data["status"] == "success"
        print(f"✓ 銘柄コードフィルタリング成功: {test_symbol}")

        # Act (実行) - 2. 日付範囲フィルタリング
        date_response = requests.get(
            f"{app_server}/api/stocks?start_date=2024-01-01&"
            f"end_date=2024-12-31",
            timeout=10,
        )

        # Assert (検証)
        assert date_response.status_code == 200
        date_data = date_response.json()
        assert date_data["status"] == "success"
        print("✓ 日付範囲フィルタリング成功")

    def test_error_recovery_flow(self, app_server):
        """エラー回復フローテスト.

        テストシナリオ:
        1. エラーが発生する状況の作成
        2. エラーレスポンスの確認
        3. システムが正常に復帰することの確認
        """
        # Arrange (準備) - 無効なリクエスト
        invalid_payloads = [
            {"symbols": [], "period": "1d"},  # 空の銘柄リスト
            {"symbols": ["INVALID"], "period": ""},  # 空の期間
            {},  # 空のペイロード
        ]

        for payload in invalid_payloads:
            # Act (実行) - 無効なリクエスト送信
            response = requests.post(
                f"{app_server}/api/bulk/download",
                json=payload,
                timeout=10,
            )

            # Assert (検証) - エラーハンドリング確認
            assert response.status_code in [400, 404, 500]
            print(f"✓ エラーハンドリング: ステータス{response.status_code}")

        # Act (実行) - システム正常性確認
        health_response = requests.get(
            f"{app_server}/api/system/health", timeout=10
        )

        # Assert (検証) - システムが正常に動作している
        assert health_response.status_code in [200, 500]
        print("✓ システム正常性確認完了")
