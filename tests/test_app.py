import pytest
import json

pytestmark = pytest.mark.unit


def test_index_route(client):
    """トップページのテスト"""
    response = client.get('/')
    assert response.status_code == 200
    assert '株価データ管理システム'.encode('utf-8') in response.data


def test_fetch_data_api_structure(client):
    """API基本構造のテスト（実際のAPIアクセス無し）"""
    # API エンドポイントの存在確認
    response = client.post('/api/fetch-data',
                          data=json.dumps({"symbol": "TEST", "period": "1mo"}),
                          content_type='application/json')

    # レスポンスの基本構造確認
    assert response.status_code in [200, 400, 502]  # 正常, バリデーションエラー, 外部API エラーのいずれか

    data = json.loads(response.data)
    assert 'success' in data
    assert 'message' in data