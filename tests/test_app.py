import pytest
import json


def test_index_route(client):
    """トップページのテスト"""
    response = client.get('/')
    assert response.status_code == 200
    assert '株価投資分析システム'.encode('utf-8') in response.data


def test_fetch_data_api_structure(client):
    """API基本構造のテスト（実際のAPIアクセス無し）"""
    # API エンドポイントの存在確認
    response = client.post('/api/fetch-data',
                          data=json.dumps({"symbol": "TEST", "period": "1mo"}),
                          content_type='application/json')

    # レスポンスの基本構造確認
    assert response.status_code in [200, 400, 404, 502]  # 正常, バリデーションエラー, データなし, 外部API エラーのいずれか

    data = json.loads(response.data)
    assert 'success' in data
    assert 'message' in data


def test_fetch_data_api_with_interval(client):
    """時間軸パラメータ付きAPI基本構造のテスト"""
    # 時間軸パラメータ付きでのAPI エンドポイントの確認
    response = client.post('/api/fetch-data',
                          data=json.dumps({
                              "symbol": "TEST", 
                              "period": "1mo",
                              "interval": "1d"
                          }),
                          content_type='application/json')

    # レスポンスの基本構造確認
    assert response.status_code in [200, 400, 404, 502]

    data = json.loads(response.data)
    assert 'success' in data
    assert 'message' in data


def test_intervals_api(client):
    """サポート時間軸取得APIのテスト"""
    response = client.get('/api/intervals')
    
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['success'] is True
    assert 'intervals' in data
    assert isinstance(data['intervals'], list)


def test_data_summary_api_structure(client):
    """データサマリーAPI基本構造のテスト"""
    response = client.post('/api/data-summary',
                          data=json.dumps({
                              "symbol": "TEST",
                              "interval": "1d"
                          }),
                          content_type='application/json')
    
    # レスポンスの基本構造確認
    assert response.status_code in [200, 400]
    
    data = json.loads(response.data)
    assert 'success' in data
    assert 'message' in data