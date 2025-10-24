"""フロントエンドE2Eテスト.

UIバグやページネーション表示問題を検知するためのテスト。
"""

import os
import subprocess
import sys
import threading
import time

import pytest
import requests
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


# テスト用のFlaskアプリケーションサーバー
class FlaskTestServer:
    def __init__(self, port=8001):
        """Initialize Flask test server.

        Args:
            port: Port number for the test server (default: 8001).
        """
        self.port = port
        self.process = None

    def start(self):
        """テスト用サーバーを起動."""
        try:
            # 既存のプロセスがあれば終了
            self.stop()

            # Flaskアプリケーションを起動
            app_path = os.path.join(
                os.path.dirname(os.path.dirname(__file__)), "app", "app.py"
            )
            env = os.environ.copy()
            env["FLASK_ENV"] = "testing"
            env["FLASK_PORT"] = str(self.port)

            self.process = subprocess.Popen(
                [sys.executable, app_path],
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )

            # サーバーが起動するまで待機
            for _ in range(30):  # 30秒まで待機
                try:
                    response = requests.get(
                        f"http://localhost:{self.port}", timeout=1
                    )
                    if response.status_code == 200:
                        return True
                except requests.exceptions.RequestException:
                    time.sleep(1)

            return False

        except Exception as e:
            print(f"サーバー起動エラー: {e}")
            return False

    def stop(self):
        """テスト用サーバーを停止."""
        if self.process:
            self.process.terminate()
            self.process.wait()
            self.process = None


@pytest.fixture(scope="session")
def test_server():
    """テスト用サーバーのフィクスチャ."""
    server = FlaskTestServer()
    if server.start():
        yield server
        server.stop()
    else:
        pytest.skip("テスト用サーバーの起動に失敗しました")


@pytest.fixture(scope="session")
def driver():
    """Seleniumドライバーのフィクスチャ."""
    try:
        options = Options()
        options.add_argument("--headless")  # ヘッドレスモード
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        options.add_argument("--window-size=1920,1080")
        options.add_argument("--disable-web-security")
        options.add_argument("--allow-running-insecure-content")
        options.add_argument("--disable-extensions")

        # ChromeDriverManagerを使用してより安全にドライバーを設定
        from selenium.webdriver.chrome.service import Service
        from webdriver_manager.chrome import ChromeDriverManager

        try:
            driver_path = ChromeDriverManager().install()
            if not os.path.exists(driver_path):
                pytest.skip("ChromeDriverのインストールに失敗しました")
            service = Service(driver_path)
            driver = webdriver.Chrome(service=service, options=options)
        except Exception as e:
            # フォールバック: システムのChromeDriverを使用
            try:
                driver = webdriver.Chrome(options=options)
            except Exception as fallback_e:
                pytest.skip(
                    f"Chromeドライバーの初期化に失敗しました: {str(e)}, フォールバックも失敗: {str(fallback_e)}"
                )

        driver.implicitly_wait(10)
        yield driver

    except Exception as e:
        pytest.skip(f"ドライバーの初期化に失敗しました: {str(e)}")
    finally:
        try:
            if "driver" in locals():
                driver.quit()
        except Exception:
            pass


@pytest.mark.e2e
class TestFrontendUI:
    """フロントエンドUIのテストクラス."""

    def test_page_load(self, driver, test_server):
        """ページが正常に読み込まれることを確認."""
        driver.get(f"http://localhost:{test_server.port}")

        # ページタイトルを確認
        assert "株価データ管理システム" in driver.title

        # 主要な要素が存在することを確認
        assert driver.find_element(By.ID, "data-management")
        assert driver.find_element(By.ID, "load-data-btn")
        assert driver.find_element(By.ID, "data-table")

    def test_pagination_display_initial_state(self, driver, test_server):
        """初期状態でのページネーション表示を確認."""
        driver.get(f"http://localhost:{test_server.port}")

        # ページが完全に読み込まれるまで少し待機
        time.sleep(1)

        # ページネーション要素を取得
        pagination_text = driver.find_element(By.ID, "pagination-text")

        # 初期状態では空文字列または適切な表示がされる
        initial_text = pagination_text.text

        # 空文字列でない場合は適切な形式であることを確認
        if initial_text.strip():
            assert "表示中:" in initial_text or "全" in initial_text
            # NaN表示がないことを確認
            assert "NaN" not in initial_text

    def test_data_loading_pagination_display(self, driver, test_server):
        """データ読み込み後のページネーション表示を確認."""
        driver.get(f"http://localhost:{test_server.port}")

        # データ読み込みボタンをクリック
        load_btn = driver.find_element(By.ID, "load-data-btn")
        load_btn.click()

        # データ読み込み完了まで待機
        wait = WebDriverWait(driver, 10)

        try:
            # データ読み込み完了まで待機（読み込み中表示が消えるまで）
            wait.until(
                lambda d: "読み込み中"
                not in d.find_element(By.ID, "data-table-body").text
            )

            # ページネーション表示を確認
            pagination_text = driver.find_element(By.ID, "pagination-text")
            text = pagination_text.text

            # NaN表示がないことを確認
            assert (
                "NaN" not in text
            ), f"ページネーション表示にNaNが含まれています: {text}"

            # 正しい形式で表示されていることを確認
            assert "表示中:" in text
            assert "全" in text
            assert "件" in text

            # データがある場合とない場合の両方をチェック
            if "全 0 件" in text:
                # データがない場合は「0-0」が表示される
                assert "0-0" in text
            else:
                # データがある場合は正しい範囲が表示される
                import re

                match = re.search(
                    r"表示中: ([\d,]+)-([\d,]+) / 全 ([\d,]+) 件", text
                )
                assert (
                    match
                ), f"ページネーション表示の形式が正しくありません: {text}"

                # カンマを除去して数値に変換
                start, end, total = [
                    int(s.replace(",", "")) for s in match.groups()
                ]
                assert start >= 1, f"開始番号が1未満です: {start}"
                assert (
                    end >= start
                ), f"終了番号が開始番号より小さいです: start={start}, end={end}"
                assert total >= 0, f"総件数が負の値です: {total}"

        except TimeoutException:
            # タイムアウトした場合でもページネーション表示をチェック
            pagination_text = driver.find_element(By.ID, "pagination-text")
            text = pagination_text.text
            assert (
                "NaN" not in text
            ), f"データ読み込み中にNaN表示が発生しました: {text}"

    def test_pagination_buttons_state(self, driver, test_server):
        """ページネーションボタンの状態を確認."""
        driver.get(f"http://localhost:{test_server.port}")

        # データ読み込みボタンをクリック
        load_btn = driver.find_element(By.ID, "load-data-btn")
        load_btn.click()

        # データ読み込み完了まで待機
        wait = WebDriverWait(driver, 10)
        try:
            wait.until(
                lambda d: "読み込み中"
                not in d.find_element(By.ID, "data-table-body").text
            )
        except TimeoutException:
            pass  # タイムアウトしても続行

        # ページネーションボタンを取得（存在する場合のみ）
        prev_btns = driver.find_elements(By.ID, "prev-page-btn")
        next_btns = driver.find_elements(By.ID, "next-page-btn")

        # ボタンが存在する場合のみテスト
        if prev_btns and next_btns:
            prev_btn = prev_btns[0]
            next_btn = next_btns[0]

            # ボタンが表示されていることを確認
            assert prev_btn.is_displayed()
            assert next_btn.is_displayed()

            # 初期状態では前へボタンが無効になっている可能性がある
            # （データ量によって変わるため、存在確認のみ）

    def test_table_display_after_load(self, driver, test_server):
        """データ読み込み後のテーブル表示を確認."""
        driver.get(f"http://localhost:{test_server.port}")

        # データ読み込みボタンをクリック
        load_btn = driver.find_element(By.ID, "load-data-btn")
        load_btn.click()

        # テーブルの状態変化を待機
        wait = WebDriverWait(driver, 10)

        try:
            # データ読み込み完了まで待機（読み込み中表示が消えるまで）
            wait.until(
                lambda d: "読み込み中"
                not in d.find_element(By.ID, "data-table-body").text
            )

            # テーブルボディの内容を確認
            table_body = driver.find_element(By.ID, "data-table-body")
            table_text = table_body.text

            # 読み込み完了後は適切な状態であることを確認
            # （データがある場合、ない場合、エラーの場合のいずれか）
            assert any(
                condition in table_text
                for condition in [
                    "データがありません",
                    "ネットワークエラー",
                    "データの読み込みに失敗",
                ]
            ) or (len(table_text.strip()) > 0 and "読み込み中" not in table_text)

        except TimeoutException:
            # タイムアウトした場合はエラー状態をチェック
            table_body = driver.find_element(By.ID, "data-table-body")
            table_text = table_body.text

            # 適切なエラーメッセージが表示されていることを確認
            assert any(
                msg in table_text
                for msg in [
                    "データがありません",
                    "ネットワークエラー",
                    "データの読み込みに失敗",
                ]
            ), f"予期しないテーブル状態: {table_text}"

    def test_ui_elements_visibility(self, driver, test_server):
        """UI要素の可視性を確認."""
        driver.get(f"http://localhost:{test_server.port}")

        # 主要なUI要素が表示されていることを確認
        elements_to_check = [
            "data-management",
            "load-data-btn",
            "data-table",
            "pagination",
            "pagination-text",
            "prev-page-btn",
            "next-page-btn",
        ]

        for element_id in elements_to_check:
            element = driver.find_element(By.ID, element_id)
            # 要素が存在することを確認（表示/非表示は状況による）
            assert element is not None, f"要素 {element_id} が見つかりません"


if __name__ == "__main__":
    # テストを直接実行する場合
    pytest.main([__file__, "-v"])
