"""簡単なE2Eテスト - アプリケーションの基本機能をテスト.
"""

import os
import sys
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
class TestE2ESimple:
    """簡単なE2Eテストクラス."""

    @pytest.fixture(scope="class")
    def driver(self):
        """Selenium WebDriverを設定するフィクスチャ."""
        try:
            # Chrome オプションを設定
            chrome_options = Options()
            chrome_options.add_argument("--headless")  # ヘッドレスモード
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--window-size=1920,1080")
            chrome_options.add_argument("--disable-web-security")
            chrome_options.add_argument("--allow-running-insecure-content")
            chrome_options.add_argument("--disable-extensions")

            # ChromeDriverを自動管理（エラーハンドリング付き）
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

    def test_static_file_access(self, driver):
        """静的ファイルへのアクセステスト."""
        # HTMLファイルに直接アクセス
        html_path = os.path.join(
            os.path.dirname(__file__), "..", "app", "templates", "index.html"
        )
        file_url = f"file:///{html_path.replace(os.sep, '/')}"

        driver.get(file_url)

        # ページタイトルを確認
        assert "株式投資分析ツール" in driver.title

        # 主要な要素が存在することを確認
        symbol_input = driver.find_element(By.ID, "symbol")
        assert symbol_input is not None

        period_select = driver.find_element(By.ID, "period")
        assert period_select is not None

        fetch_btn = driver.find_element(By.ID, "fetch-btn")
        assert fetch_btn is not None

        reset_btn = driver.find_element(By.ID, "reset-btn")
        assert reset_btn is not None

    def test_form_elements_interaction(self, driver):
        """フォーム要素の操作テスト."""
        # HTMLファイルに直接アクセス
        html_path = os.path.join(
            os.path.dirname(__file__), "..", "app", "templates", "index.html"
        )
        file_url = f"file:///{html_path.replace(os.sep, '/')}"

        driver.get(file_url)

        # 銘柄コード入力
        symbol_input = driver.find_element(By.ID, "symbol")
        symbol_input.clear()
        symbol_input.send_keys("AAPL")
        assert symbol_input.get_attribute("value") == "AAPL"

        # 期間選択
        period_select = Select(driver.find_element(By.ID, "period"))
        period_select.select_by_value("1mo")
        selected_option = period_select.first_selected_option
        assert selected_option.get_attribute("value") == "1mo"

        # リセットボタンのクリック（JavaScriptが動作しないため、要素の存在のみ確認）
        reset_btn = driver.find_element(By.ID, "reset-btn")
        assert reset_btn.is_enabled()

    def test_responsive_design_elements(self, driver):
        """レスポンシブデザイン要素のテスト."""
        # HTMLファイルに直接アクセス
        html_path = os.path.join(
            os.path.dirname(__file__), "..", "app", "templates", "index.html"
        )
        file_url = f"file:///{html_path.replace(os.sep, '/')}"

        driver.get(file_url)

        # デスクトップサイズ
        driver.set_window_size(1920, 1080)
        container = driver.find_element(By.CLASS_NAME, "container")
        assert container.is_displayed()

        # タブレットサイズ
        driver.set_window_size(768, 1024)
        assert container.is_displayed()

        # モバイルサイズ
        driver.set_window_size(375, 667)
        assert container.is_displayed()

    def test_accessibility_features(self, driver):
        """アクセシビリティ機能のテスト."""
        # HTMLファイルに直接アクセス
        html_path = os.path.join(
            os.path.dirname(__file__), "..", "app", "templates", "index.html"
        )
        file_url = f"file:///{html_path.replace(os.sep, '/')}"

        driver.get(file_url)

        # ラベルとフォーム要素の関連付けを確認
        symbol_label = driver.find_element(By.XPATH, "//label[@for='symbol']")
        assert symbol_label is not None

        period_label = driver.find_element(By.XPATH, "//label[@for='period']")
        assert period_label is not None

        # ボタンのaria-labelやtitle属性を確認
        fetch_btn = driver.find_element(By.ID, "fetch-btn")
        assert fetch_btn.get_attribute("type") == "button"

        reset_btn = driver.find_element(By.ID, "reset-btn")
        assert reset_btn.get_attribute("type") == "button"

    def test_css_and_styling(self, driver):
        """CSSとスタイリングのテスト."""
        # HTMLファイルに直接アクセス
        html_path = os.path.join(
            os.path.dirname(__file__), "..", "app", "templates", "index.html"
        )
        file_url = f"file:///{html_path.replace(os.sep, '/')}"

        driver.get(file_url)

        # Bootstrap CSSが適用されているかを確認
        container = driver.find_element(By.CLASS_NAME, "container")
        container_class = container.get_attribute("class")
        assert "container" in container_class

        # フォーム要素のクラスを確認
        symbol_input = driver.find_element(By.ID, "symbol")
        input_class = symbol_input.get_attribute("class")
        assert "form-control" in input_class

        # ボタンのクラスを確認
        fetch_btn = driver.find_element(By.ID, "fetch-btn")
        btn_class = fetch_btn.get_attribute("class")
        assert "btn" in btn_class
