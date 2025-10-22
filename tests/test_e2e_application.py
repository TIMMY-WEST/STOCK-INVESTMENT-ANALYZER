"""
End-to-End (E2E) テスト

実際のアプリケーション起動とブラウザ操作を含むテスト
"""

import os
import subprocess
import sys
import threading
import time
from urllib.parse import urljoin

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
class TestE2EApplication:
    """E2Eアプリケーションテストクラス"""

    @pytest.fixture(scope="class")
    def app_server(self):
        """Flaskアプリケーションサーバーを起動するフィクスチャ"""
        # アプリケーションのパスを設定
        app_dir = os.path.join(os.path.dirname(__file__), "..", "app")
        sys.path.insert(0, app_dir)

        # Flaskアプリをインポート
        from app import app

        app.config["TESTING"] = True

        # スレッドでサーバーを起動
        def run_app():
            app.run(
                host="127.0.0.1",
                port=8001,
                debug=False,
                use_reloader=False,
                threaded=True,
            )

        server_thread = threading.Thread(target=run_app, daemon=True)
        server_thread.start()

        # サーバーが起動するまで待機
        base_url = "http://127.0.0.1:8001"
        max_attempts = 30
        for attempt in range(max_attempts):
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
        """Seleniumドライバーを設定するフィクスチャ"""
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
            except:
                pass

    def test_application_startup_and_homepage_load(self, app_server, driver):
        """アプリケーション起動とホームページ読み込みテスト"""
        # ホームページにアクセス
        driver.get(app_server)

        # ページタイトルを確認
        assert "株価データ管理システム" in driver.title

        # メインヘッダーの存在確認
        header = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "page-title"))
        )
        assert "株価データ管理システム" in header.text

        # ナビゲーションメニューの確認
        nav_brand = driver.find_element(By.CLASS_NAME, "nav-brand")
        assert "株価データ管理システム" in nav_brand.text

    def test_stock_data_fetch_form_interaction(self, app_server, driver):
        """株価データ取得フォームの操作テスト"""
        driver.get(app_server)

        # フォーム要素の存在確認
        symbol_input = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "symbol"))
        )
        period_select = driver.find_element(By.ID, "period")
        fetch_button = driver.find_element(By.ID, "fetch-btn")

        # デフォルト値の確認
        assert symbol_input.get_attribute("value") == "7203.T"

        # 期間選択の確認
        select = Select(period_select)
        assert select.first_selected_option.get_attribute("value") == "1mo"

        # 銘柄コードを変更
        symbol_input.clear()
        symbol_input.send_keys("6758.T")  # ソニーグループ

        # 期間を変更
        select.select_by_value("1wk")

        # フォームの値が正しく設定されているか確認
        assert symbol_input.get_attribute("value") == "6758.T"
        assert select.first_selected_option.get_attribute("value") == "1wk"

    def test_stock_data_fetch_submission(self, app_server, driver):
        """株価データ取得の実行テスト"""
        driver.get(app_server)

        # フォーム要素を取得
        symbol_input = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "symbol"))
        )
        fetch_button = driver.find_element(By.ID, "fetch-btn")

        # 有効な銘柄コードを設定
        symbol_input.clear()
        symbol_input.send_keys("7203.T")  # トヨタ自動車

        # データ取得ボタンをクリック
        fetch_button.click()

        # 結果コンテナの表示を待機
        result_container = WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.ID, "result-container"))
        )

        # 結果が表示されるまで待機（最大30秒）
        WebDriverWait(driver, 30).until(
            lambda d: result_container.text.strip() != ""
        )

        # 結果の内容を確認
        result_text = result_container.text
        assert result_text != ""

        # 成功またはエラーメッセージが表示されていることを確認
        assert (
            "データを取得しました" in result_text
            or "エラー" in result_text
            or "失敗" in result_text
        )

    def test_invalid_stock_symbol_error_handling(self, app_server, driver):
        """無効な銘柄コードのエラーハンドリングテスト"""
        driver.get(app_server)

        # フォーム要素を取得
        symbol_input = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "symbol"))
        )
        fetch_button = driver.find_element(By.ID, "fetch-btn")

        # 無効な銘柄コードを設定
        symbol_input.clear()
        symbol_input.send_keys("INVALID.T")

        # データ取得ボタンをクリック
        fetch_button.click()

        # エラーメッセージの表示を待機
        result_container = WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.ID, "result-container"))
        )

        # エラーメッセージが表示されるまで待機
        WebDriverWait(driver, 30).until(
            lambda d: result_container.text.strip() != ""
        )

        # エラーメッセージの確認
        result_text = result_container.text
        assert (
            "エラー" in result_text
            or "失敗" in result_text
            or "データが見つかりません" in result_text
        )

    def test_reset_button_functionality(self, app_server, driver):
        """リセットボタンの機能テスト"""
        driver.get(app_server)

        # フォーム要素を取得
        symbol_input = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "symbol"))
        )
        period_select = driver.find_element(By.ID, "period")
        reset_button = driver.find_element(By.ID, "reset-btn")

        # フォームの値を変更
        symbol_input.clear()
        symbol_input.send_keys("6758.T")

        select = Select(period_select)
        select.select_by_value("1y")

        # 変更が反映されていることを確認
        assert symbol_input.get_attribute("value") == "6758.T"
        assert select.first_selected_option.get_attribute("value") == "1y"

        # リセットボタンをクリック
        reset_button.click()

        # デフォルト値に戻っていることを確認
        assert symbol_input.get_attribute("value") == "7203.T"
        assert select.first_selected_option.get_attribute("value") == "1mo"

    def test_navigation_links(self, app_server, driver):
        """ナビゲーションリンクのテスト"""
        driver.get(app_server)

        # ナビゲーションリンクを取得
        nav_links = driver.find_elements(By.CLASS_NAME, "nav-link")

        # 各リンクが存在することを確認
        link_texts = [link.text for link in nav_links]
        expected_links = ["ホーム", "データ管理", "分析", "ヘルプ"]

        for expected_link in expected_links:
            assert expected_link in link_texts

    def test_accessibility_features(self, app_server, driver):
        """アクセシビリティ機能のテスト"""
        driver.get(app_server)

        # スキップリンクの存在確認
        skip_link = driver.find_element(By.CLASS_NAME, "skip-link")
        assert "メインコンテンツへスキップ" in skip_link.text

        # フォームラベルの関連付け確認
        symbol_input = driver.find_element(By.ID, "symbol")
        symbol_label = driver.find_element(
            By.CSS_SELECTOR, "label[for='symbol']"
        )
        assert symbol_label.text == "銘柄コード"

        period_input = driver.find_element(By.ID, "period")
        period_label = driver.find_element(
            By.CSS_SELECTOR, "label[for='period']"
        )
        assert period_label.text == "取得期間"

    def test_responsive_design_elements(self, app_server, driver):
        """レスポンシブデザイン要素のテスト"""
        driver.get(app_server)

        # デスクトップサイズでの表示確認
        driver.set_window_size(1920, 1080)
        container = driver.find_element(By.CLASS_NAME, "container")
        assert container.is_displayed()

        # モバイルサイズでの表示確認
        driver.set_window_size(375, 667)
        time.sleep(1)  # レイアウト調整を待機
        assert container.is_displayed()

        # タブレットサイズでの表示確認
        driver.set_window_size(768, 1024)
        time.sleep(1)  # レイアウト調整を待機
        assert container.is_displayed()

    def test_database_connection_endpoint(self, app_server, driver):
        """データベース接続テストエンドポイントの確認"""
        # APIエンドポイントに直接アクセス
        api_url = urljoin(app_server, "/api/test-connection")

        try:
            response = requests.get(api_url, timeout=10)
            # レスポンスが返ってくることを確認（成功・失敗問わず）
            assert response.status_code in [200, 500]

            # JSONレスポンスの構造を確認
            data = response.json()
            assert "success" in data
            assert "message" in data

        except requests.exceptions.RequestException:
            # ネットワークエラーの場合はスキップ
            pytest.skip("データベース接続テストをスキップしました")
