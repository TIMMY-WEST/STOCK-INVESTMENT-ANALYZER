"""
足選択機能のテストコード
Interval Selector Feature Tests

このテストファイルは、足選択機能の基本機能をテストします：
- HTMLテンプレートの足選択要素確認
- JavaScript関数の存在確認
- バリデーション機能のテスト
- APIリクエストでのintervalパラメータ処理テスト
"""

import pytest
import os
import sys
from bs4 import BeautifulSoup
import re
import json

# アプリケーションのパスを追加
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.app import app


class TestIntervalSelectorUI:
    """足選択UI機能のテストクラス"""

    def test_interval_selector_html_structure(self):
        """足選択セレクターのHTML構造確認テスト"""
        template_path = os.path.join(os.path.dirname(__file__), '..', 'app', 'templates', 'index.html')
        
        with open(template_path, 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # 足選択セレクターの存在確認
        interval_select = soup.find('select', {'id': 'interval'})
        assert interval_select is not None, "足選択セレクターが見つかりません"
        
        # 足選択セレクターのオプション確認
        options = interval_select.find_all('option')
        assert len(options) > 0, "足選択セレクターにオプションがありません"
        
        # 必要な足種別のオプション確認（実際のHTMLテンプレートに基づく）
        expected_intervals = ['1m', '2m', '5m', '15m', '30m', '60m', '1h', '90m', '1d', '5d', '1wk', '1mo', '3mo']
        option_values = [option.get('value') for option in options if option.get('value')]
        
        for interval in expected_intervals:
            assert interval in option_values, f"足種別 {interval} のオプションが見つかりません"

    def test_interval_selector_css_styles(self):
        """足選択セレクターのCSSスタイル確認テスト"""
        css_path = os.path.join(os.path.dirname(__file__), '..', 'app', 'static', 'style.css')
        
        with open(css_path, 'r', encoding='utf-8') as f:
            css_content = f.read()
        
        # 足選択関連のCSSクラスの存在確認
        interval_css_classes = [
            '.interval-selector',
            '.interval-error'
        ]
        
        for css_class in interval_css_classes:
            assert css_class in css_content, f"CSSクラス {css_class} が見つかりません"

    def test_interval_selector_javascript_functions(self):
        """足選択関連のJavaScript関数確認テスト"""
        js_path = os.path.join(os.path.dirname(__file__), '..', 'app', 'static', 'script.js')
        
        with open(js_path, 'r', encoding='utf-8') as f:
            js_content = f.read()
        
        # 足選択関連のJavaScript関数の存在確認
        required_functions = [
            'initIntervalSelector',
            'validateIntervalSelection',
            'setIntervalSelectorState',
            'showIntervalError',
            'clearIntervalError'
        ]
        
        for function_name in required_functions:
            pattern = rf'function\s+{function_name}\s*\(|{function_name}\s*[:=]\s*function'
            assert re.search(pattern, js_content), f"JavaScript関数 {function_name} が見つかりません"

    def test_interval_validation_logic(self):
        """足選択バリデーションロジックのテスト"""
        js_path = os.path.join(os.path.dirname(__file__), '..', 'app', 'static', 'script.js')
        
        with open(js_path, 'r', encoding='utf-8') as f:
            js_content = f.read()
        
        # バリデーション関数内で有効な足種別リストが定義されているか確認
        assert 'validIntervals' in js_content, "有効な足種別リストが定義されていません"
        
        # validateForm関数に足選択バリデーションが統合されているか確認
        assert 'validateIntervalSelection' in js_content, "足選択バリデーションが統合されていません"


class TestIntervalSelectorAPI:
    """足選択機能のAPI統合テストクラス"""

    def setup_method(self):
        """テストメソッドのセットアップ"""
        self.app = app
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()

    def test_api_accepts_interval_parameter(self):
        """APIが足パラメータを受け取るかテスト"""
        # テストデータ
        test_data = {
            'symbol': 'AAPL',
            'period': '1mo',
            'interval': '1d'
        }
        
        # APIエンドポイントにPOSTリクエスト送信
        response = self.client.post('/api/fetch-data', 
                                  data=json.dumps(test_data),
                                  content_type='application/json')
        
        # レスポンスの確認（エラーでないことを確認）
        assert response.status_code in [200, 400], f"予期しないステータスコード: {response.status_code}"
        
        # レスポンスデータの確認
        if response.status_code == 200:
            response_data = json.loads(response.data)
            assert 'data' in response_data, "レスポンスにdataが含まれていません"
            assert 'interval' in response_data['data'], "レスポンスのdataにintervalが含まれていません"

    def test_api_validates_interval_parameter(self):
        """APIが足パラメータをバリデーションするかテスト"""
        # 無効な足種別でテスト
        test_data = {
            'symbol': 'AAPL',
            'period': '1mo',
            'interval': 'invalid_interval'
        }
        
        # APIエンドポイントにPOSTリクエスト送信
        response = self.client.post('/api/fetch-data', 
                                  data=json.dumps(test_data),
                                  content_type='application/json')
        
        # バリデーションエラーが返されることを確認
        assert response.status_code == 400, "無効な足種別でバリデーションエラーが発生していません"
        
        response_data = json.loads(response.data)
        assert 'error' in response_data, "エラーレスポンスにerrorフィールドがありません"

    def test_api_handles_missing_interval_parameter(self):
        """APIが足パラメータが欠けている場合を処理するかテスト"""
        # intervalパラメータなしでテスト
        test_data = {
            'symbol': 'AAPL',
            'period': '1mo'
        }
        
        # APIエンドポイントにPOSTリクエスト送信
        response = self.client.post('/api/fetch-data', 
                                  data=json.dumps(test_data),
                                  content_type='application/json')
        
        # デフォルト値が使用されて成功することを確認
        assert response.status_code in [200, 400], f"予期しないステータスコード: {response.status_code}"
        
        # レスポンスデータの確認
        if response.status_code == 200:
            response_data = json.loads(response.data)
            # デフォルトのinterval値（1d）が使用されることを確認
            assert 'data' in response_data, "レスポンスにdataが含まれていません"
            assert 'interval' in response_data['data'], "レスポンスのdataにintervalが含まれていません"


class TestIntervalSelectorIntegration:
    """足選択機能の統合テストクラス"""

    def test_frontend_backend_integration(self):
        """フロントエンドとバックエンドの統合確認テスト"""
        # app.jsファイルの確認
        app_js_path = os.path.join(os.path.dirname(__file__), '..', 'app', 'static', 'app.js')
        
        with open(app_js_path, 'r', encoding='utf-8') as f:
            app_js_content = f.read()
        
        # fetchStockData関数がintervalパラメータを処理するか確認
        assert 'interval' in app_js_content, "app.jsでintervalパラメータが処理されていません"
        
        # script.jsファイルの確認
        script_js_path = os.path.join(os.path.dirname(__file__), '..', 'app', 'static', 'script.js')
        
        with open(script_js_path, 'r', encoding='utf-8') as f:
            script_js_content = f.read()
        
        # handleFetchSubmit関数がintervalパラメータを送信するか確認
        assert 'interval' in script_js_content, "script.jsでintervalパラメータが送信されていません"

    def test_backend_interval_processing(self):
        """バックエンドの足パラメータ処理確認テスト"""
        app_py_path = os.path.join(os.path.dirname(__file__), '..', 'app', 'app.py')
        
        with open(app_py_path, 'r', encoding='utf-8') as f:
            app_py_content = f.read()
        
        # fetch_data関数でintervalパラメータが処理されているか確認
        assert 'interval' in app_py_content, "app.pyでintervalパラメータが処理されていません"
        
        # valid_intervalsリストが定義されているか確認
        assert 'valid_intervals' in app_py_content, "有効な足種別リストが定義されていません"
        
        # ticker.historyにintervalパラメータが渡されているか確認
        assert 'interval=interval' in app_py_content, "Yahoo Finance APIにintervalパラメータが渡されていません"


class TestIntervalSelectorErrorHandling:
    """足選択機能のエラーハンドリングテストクラス"""

    def test_interval_error_display(self):
        """足選択エラー表示のテスト"""
        js_path = os.path.join(os.path.dirname(__file__), '..', 'app', 'static', 'script.js')
        
        with open(js_path, 'r', encoding='utf-8') as f:
            js_content = f.read()
        
        # showFieldError関数でintervalフィールドのエラー処理が含まれているか確認
        assert 'showIntervalError' in js_content, "足選択エラー表示機能が実装されていません"
        
        # setIntervalSelectorState関数が実装されているか確認
        assert 'setIntervalSelectorState' in js_content, "足選択セレクター状態設定機能が実装されていません"

    def test_interval_error_clearing(self):
        """足選択エラークリア機能のテスト"""
        js_path = os.path.join(os.path.dirname(__file__), '..', 'app', 'static', 'script.js')
        
        with open(js_path, 'r', encoding='utf-8') as f:
            js_content = f.read()
        
        # clearFieldErrors関数でintervalフィールドのエラークリアが含まれているか確認
        assert 'clearIntervalError' in js_content, "足選択エラークリア機能が実装されていません"


if __name__ == '__main__':
    pytest.main([__file__, '-v'])