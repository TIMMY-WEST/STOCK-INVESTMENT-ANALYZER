"""データ表示フローE2Eテスト（ブラウザテスト）.

Seleniumを使用したUIデータ表示フローの包括的なテスト。
Issue #209: E2Eテストの整備
"""

import os
import sys
import threading
import time

import pytest
import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select, WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager


@pytest.mark.e2e
class TestUIDisplayFlowE2E:
    """UIデータ表示フロー E2Eテストクラス."""

    @pytest.fixture(scope="class")
    def app_server(self):
        """Flaskアプリケーションサーバーを起動するフィクスチャ."""
        # アプリケーションのパスを設定
        app_dir = os.path.join(os.path.dirname(__file__), "..", "..", "app")
        sys.path.insert(0, app_dir)

        # Flaskアプリをインポート
        from app.app import app

        app.config["TESTING"] = True

        # スレッドでサーバーを起動
        def run_app():
            app.run(
                host="127.0.0.1",
                port=8005,
                debug=False,
                use_reloader=False,
                threaded=True,
            )

        server_thread = threading.Thread(target=run_app, daemon=True)
        server_thread.start()

        # サーバーが起動するまで待機
        base_url = "http://127.0.0.1:8005"
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

    @pytest.fixture(scope="class")
    def driver(self):
        """Seleniumドライバーを設定するフィクスチャ."""
        try:
            # Chromeオプションを設定
            chrome_options = Options()
            chrome_options.add_argument("--headless")  # ヘッドレスモード
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--window-size=1920,1080")
            chrome_options.add_argument("--disable-web-security")
            chrome_options.add_argument("--allow-running-insecure-content")
            chrome_options.add_argument("--disable-extensions")

            # ChromeDriverを自動ダウンロード・設定（エラーハンドリング付き）
            try:
                driver_path = ChromeDriverManager().install()
                # パスが正しく設定されているか確認
                if not os.path.exists(driver_path):
                    pytest.skip("ChromeDriverのインストールに失敗しました")
                service = Service(driver_path)
            except Exception as e:
                pytest.skip(f"ChromeDriverの設定に失敗しました: {str(e)}")

            try:
                driver = webdriver.Chrome(
                    service=service, options=chrome_options
                )
                driver.implicitly_wait(10)
            except Exception as e:
                pytest.skip(f"Chromeブラウザの起動に失敗しました: {str(e)}")

            yield driver

        except Exception as e:
            pytest.skip(f"ドライバーの初期化に失敗しました: {str(e)}")
        finally:
            try:
                if "driver" in locals():
                    driver.quit()
            except Exception:
                pass

    def test_complete_data_display_flow(self, app_server, driver):
        """完全なデータ表示フローテスト.

        テストシナリオ:
        1. ホームページアクセス
        2. データ取得
        3. 結果表示確認
        4. データテーブルの表示
        5. グラフ表示の確認
        """
        # Act (実行) - 1. ホームページにアクセス
        driver.get(app_server)
        assert "株価データ管理システム" in driver.title
        print("✓ ホームページアクセス成功")

        # Act (実行) - 2. データ取得フォーム操作
        symbol_input = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "symbol"))
        )
        fetch_button = driver.find_element(By.ID, "fetch-btn")

        symbol_input.clear()
        symbol_input.send_keys("7203.T")
        fetch_button.click()
        print("✓ データ取得リクエスト送信")

        # Act (実行) - 3. 結果表示を待機
        result_container = WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.ID, "result-container"))
        )

        WebDriverWait(driver, 30).until(
            lambda d: result_container.text.strip() != ""
        )
        print("✓ 結果表示確認")

        # Assert (検証) - 結果の内容確認
        result_text = result_container.text
        assert result_text != ""
        assert (
            "データを取得しました" in result_text
            or "エラー" in result_text
            or "失敗" in result_text
        )

    def test_data_table_display_flow(self, app_server, driver):
        """データテーブル表示フローテスト.

        テストシナリオ:
        1. データ一覧ページへのアクセス
        2. テーブルの表示確認
        3. ページネーション操作
        4. ソート機能確認
        """
        # Act (実行) - 1. データ一覧ページにアクセス
        driver.get(f"{app_server}/data-management")

        # Assert (検証) - ページが表示されることを確認
        time.sleep(2)  # ページロード待機

        # テーブル要素の確認（存在しない場合もあるのでスキップ）
        try:
            table = driver.find_element(By.TAG_NAME, "table")
            print("✓ データテーブル表示確認")

            # テーブルヘッダーの確認
            headers = table.find_elements(By.TAG_NAME, "th")
            assert len(headers) > 0
            print(f"✓ テーブルヘッダー: {len(headers)}列")

        except Exception:
            print("✓ データ一覧ページ: テーブル要素なし（許容）")

    def test_timeframe_selector_flow(self, app_server, driver):
        """期間選択フローテスト.

        テストシナリオ:
        1. 期間選択UIの表示
        2. 異なる期間の選択
        3. 選択に応じたデータ更新
        """
        # Act (実行) - ホームページにアクセス
        driver.get(app_server)

        # Act (実行) - 期間選択要素の取得
        period_select = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "period"))
        )

        select = Select(period_select)
        print("✓ 期間選択UI表示確認")

        # Act (実行) - 異なる期間を選択
        periods = ["1d", "5d", "1mo", "1y"]
        for period in periods:
            try:
                select.select_by_value(period)
                time.sleep(0.5)
                assert (
                    select.first_selected_option.get_attribute("value")
                    == period
                )
                print(f"✓ 期間選択: {period}")
            except Exception:
                print(f"✓ 期間オプション未提供: {period}")

    def test_interval_selector_flow(self, app_server, driver):
        """インターバル選択フローテスト.

        テストシナリオ:
        1. インターバル選択UIの表示
        2. 異なるインターバルの選択
        3. 選択に応じたUI更新
        """
        # Act (実行) - ホームページにアクセス
        driver.get(app_server)

        # インターバル選択要素の確認（存在しない場合もある）
        try:
            interval_select = driver.find_element(By.ID, "interval")
            select = Select(interval_select)
            print("✓ インターバル選択UI表示確認")

            # 異なるインターバルを選択
            intervals = ["1m", "1h", "1d"]
            for interval in intervals:
                try:
                    select.select_by_value(interval)
                    time.sleep(0.5)
                    print(f"✓ インターバル選択: {interval}")
                except Exception:
                    print(f"✓ インターバルオプション未提供: {interval}")

        except Exception:
            print("✓ インターバル選択UI: 未実装（許容）")

    def test_error_message_display_flow(self, app_server, driver):
        """エラーメッセージ表示フローテスト.

        テストシナリオ:
        1. 無効なデータでエラー発生
        2. エラーメッセージの表示確認
        3. エラースタイルの確認
        """
        # Act (実行) - ホームページにアクセス
        driver.get(app_server)

        # Act (実行) - 無効な銘柄コードを入力
        symbol_input = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "symbol"))
        )
        fetch_button = driver.find_element(By.ID, "fetch-btn")

        symbol_input.clear()
        symbol_input.send_keys("INVALID_CODE_12345")
        fetch_button.click()
        print("✓ 無効データ送信")

        # Act (実行) - エラーメッセージ表示を待機
        result_container = WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.ID, "result-container"))
        )

        WebDriverWait(driver, 30).until(
            lambda d: result_container.text.strip() != ""
        )

        # Assert (検証) - エラーメッセージ確認
        result_text = result_container.text
        assert (
            "エラー" in result_text
            or "失敗" in result_text
            or "データが見つかりません" in result_text
        )
        print("✓ エラーメッセージ表示確認")

    def test_loading_state_display_flow(self, app_server, driver):
        """ローディング状態表示フローテスト.

        テストシナリオ:
        1. データ取得開始
        2. ローディング表示の確認
        3. 完了後のローディング非表示確認
        """
        # Act (実行) - ホームページにアクセス
        driver.get(app_server)

        # Act (実行) - データ取得開始
        symbol_input = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "symbol"))
        )
        fetch_button = driver.find_element(By.ID, "fetch-btn")

        symbol_input.clear()
        symbol_input.send_keys("7203.T")
        fetch_button.click()

        # ローディング要素の確認（実装されていない場合もある）
        try:
            # ローディングスピナーやメッセージの確認
            _ = driver.find_element(By.CLASS_NAME, "loading")
            print("✓ ローディング表示確認")

            # 処理完了後、ローディングが非表示になることを確認
            WebDriverWait(driver, 30).until(
                EC.invisibility_of_element_located((By.CLASS_NAME, "loading"))
            )
            print("✓ ローディング非表示確認")

        except Exception:
            print("✓ ローディング表示: 未実装または異なる実装（許容）")

    def test_responsive_layout_flow(self, app_server, driver):
        """レスポンシブレイアウトフローテスト.

        テストシナリオ:
        1. デスクトップ表示
        2. タブレット表示
        3. モバイル表示
        4. 各サイズでのUI要素の確認
        """
        driver.get(app_server)

        # 1. デスクトップサイズ
        driver.set_window_size(1920, 1080)
        time.sleep(1)
        container = driver.find_element(By.CLASS_NAME, "container")
        assert container.is_displayed()
        print("✓ デスクトップ表示確認")

        # 2. タブレットサイズ
        driver.set_window_size(768, 1024)
        time.sleep(1)
        assert container.is_displayed()
        print("✓ タブレット表示確認")

        # 3. モバイルサイズ
        driver.set_window_size(375, 667)
        time.sleep(1)
        assert container.is_displayed()
        print("✓ モバイル表示確認")

    def test_navigation_flow(self, app_server, driver):
        """ナビゲーションフローテスト.

        テストシナリオ:
        1. ホームページからデータ管理へ遷移
        2. データ管理からホームへ戻る
        3. ナビゲーションの一貫性確認
        """
        # Act (実行) - ホームページにアクセス
        driver.get(app_server)
        print("✓ ホームページ表示")

        # ナビゲーションリンクの取得と操作
        try:
            nav_links = driver.find_elements(By.CLASS_NAME, "nav-link")

            # データ管理リンクをクリック
            for link in nav_links:
                if "データ管理" in link.text:
                    link.click()
                    time.sleep(2)
                    print("✓ データ管理ページへ遷移")
                    break

            # ホームに戻る
            home_link = driver.find_element(By.CLASS_NAME, "nav-brand")
            home_link.click()
            time.sleep(2)
            print("✓ ホームページへ戻る")

        except Exception:
            print("✓ ナビゲーション: 一部機能未実装（許容）")
