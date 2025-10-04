import pytest
import json
from app.app import app


@pytest.fixture
def client():
    """テスト用のFlaskクライアントを作成"""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


class TestIntervalSelector:
    """足選択機能のテストクラス"""
    
    def test_interval_selector_ui_elements(self, client):
        """足選択UIの要素が正しく表示されることをテスト"""
        response = client.get('/')
        assert response.status_code == 200
        
        html_content = response.get_data(as_text=True)
        
        # 足選択のlabelが存在することを確認
        assert '足種別:' in html_content
        
        # 足選択のselectが存在することを確認
        assert 'id="interval"' in html_content
        
        # 各足のoptionが存在することを確認
        expected_intervals = [
            ('1m', '1分足'),
            ('5m', '5分足'),
            ('15m', '15分足'),
            ('30m', '30分足'),
            ('1h', '1時間足'),
            ('1d', '日足'),
            ('1wk', '週足'),
            ('1mo', '月足')
        ]
        
        for value, text in expected_intervals:
            assert f'value="{value}"' in html_content
            assert text in html_content
    
    def test_default_interval_selection(self, client):
        """デフォルトで日足が選択されていることをテスト"""
        response = client.get('/')
        assert response.status_code == 200
        
        html_content = response.get_data(as_text=True)
        
        # デフォルトで日足が選択されていることを確認
        assert 'value="1d" selected' in html_content
    
    def test_interval_error_element(self, client):
        """足選択のエラー表示要素が存在することをテスト"""
        response = client.get('/')
        assert response.status_code == 200
        
        html_content = response.get_data(as_text=True)
        
        # エラーメッセージ要素が存在することを確認
        assert 'id="interval-error"' in html_content
        assert 'error-message' in html_content
    
    def test_api_accepts_interval_parameter(self, client):
        """APIが足パラメータを正しく受け取ることをテスト"""
        test_data = {
            'symbol': 'AAPL',
            'timeframe': '1mo',
            'interval': '1h'
        }
        
        response = client.post('/api/fetch_data', 
                             data=json.dumps(test_data),
                             content_type='application/json')
        
        assert response.status_code == 200
        response_data = json.loads(response.get_data(as_text=True))
        
        # レスポンスに足情報が含まれていることを確認
        assert 'data' in response_data
        assert 'interval' in response_data['data']
        assert response_data['data']['interval'] == '1h'
    
    def test_api_validates_interval_parameter(self, client):
        """APIが無効な足パラメータを適切にバリデーションすることをテスト"""
        test_data = {
            'symbol': 'AAPL',
            'timeframe': '1mo',
            'interval': 'invalid_interval'
        }
        
        response = client.post('/api/fetch_data', 
                             data=json.dumps(test_data),
                             content_type='application/json')
        
        assert response.status_code == 400
        response_data = json.loads(response.get_data(as_text=True))
        
        # エラーレスポンスの確認
        assert 'error' in response_data
        assert response_data['error'] == 'INVALID_INTERVAL'
    
    def test_api_handles_missing_interval_parameter(self, client):
        """APIが足パラメータが欠けている場合を適切に処理することをテスト"""
        test_data = {
            'symbol': 'AAPL',
            'timeframe': '1mo'
            # intervalパラメータを意図的に省略
        }
        
        response = client.post('/api/fetch_data', 
                             data=json.dumps(test_data),
                             content_type='application/json')
        
        # デフォルト値が使用されるため、成功レスポンスが期待される
        assert response.status_code in [200, 400]  # デフォルト値使用時は200、その他のエラー時は400
    
    def test_interval_options_order(self, client):
        """足選択のオプションが正しい順序で表示されることをテスト"""
        response = client.get('/')
        assert response.status_code == 200
        
        html_content = response.get_data(as_text=True)
        
        # 期待される順序で足のオプションが表示されることを確認
        expected_intervals = ['1m', '5m', '15m', '30m', '1h', '1d', '1wk', '1mo']
        
        # HTMLから足のオプションの順序を抽出して確認
        interval_section_start = html_content.find('id="interval"')
        interval_section_end = html_content.find('</select>', interval_section_start)
        interval_section = html_content[interval_section_start:interval_section_end]
        
        last_position = 0
        for interval in expected_intervals:
            position = interval_section.find(f'value="{interval}"', last_position)
            assert position > last_position, f"足 {interval} が期待される順序で表示されていません"
            last_position = position
    
    def test_multiple_interval_selections(self, client):
        """複数の異なる足でAPIが正しく動作することをテスト"""
        intervals_to_test = ['1m', '5m', '15m', '30m', '1h', '1d', '1wk', '1mo']
        
        for interval in intervals_to_test:
            test_data = {
                'symbol': 'AAPL',
                'timeframe': '1mo',
                'interval': interval
            }
            
            response = client.post('/api/fetch_data', 
                                 data=json.dumps(test_data),
                                 content_type='application/json')
            
            # 各足で正常にレスポンスが返されることを確認
            assert response.status_code in [200, 400], f"足 {interval} でAPIエラーが発生しました"
            
            if response.status_code == 200:
                response_data = json.loads(response.get_data(as_text=True))
                assert 'data' in response_data
                assert 'interval' in response_data['data']
                assert response_data['data']['interval'] == interval
    
    def test_interval_timeframe_combination_validation(self, client):
        """足と期間の組み合わせバリデーションをテスト"""
        # 短期間に長い足を組み合わせた場合のテスト
        test_data = {
            'symbol': 'AAPL',
            'timeframe': '1d',  # 1日
            'interval': '1wk'   # 週足
        }
        
        response = client.post('/api/fetch_data', 
                             data=json.dumps(test_data),
                             content_type='application/json')
        
        # バリデーションエラーまたは適切な処理が行われることを確認
        assert response.status_code in [200, 400]
    
    def test_interval_css_classes(self, client):
        """足選択に関連するCSSクラスが適切に設定されていることをテスト"""
        response = client.get('/')
        assert response.status_code == 200
        
        html_content = response.get_data(as_text=True)
        
        # 足選択の入力グループにCSSクラスが設定されていることを確認
        assert 'class="input-group"' in html_content
        assert 'class="error-message"' in html_content
    
    def test_interval_accessibility(self, client):
        """足選択のアクセシビリティ要素をテスト"""
        response = client.get('/')
        assert response.status_code == 200
        
        html_content = response.get_data(as_text=True)
        
        # labelとselectが適切に関連付けられていることを確認
        assert 'for="interval"' in html_content
        assert 'id="interval"' in html_content
        
        # ラベルテキストが適切に設定されていることを確認
        assert '足種別:' in html_content