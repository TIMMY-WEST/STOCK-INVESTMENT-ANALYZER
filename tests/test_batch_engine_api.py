"""
BatchEngine APIのテストコード

Phase 2のバッチエンジンAPIエンドポイントをテストします。
"""

import pytest
import json
from unittest.mock import Mock, patch, MagicMock

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'app'))

from app import app
from services.batch_engine import BatchStatus

@pytest.fixture
def client():
    """テスト用Flaskクライアント"""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

@pytest.fixture
def auth_headers():
    """認証ヘッダー"""
    return {'X-API-Key': 'test-api-key'}

class TestBatchEngineAPI:
    """BatchEngine APIのテスト"""
    
    @patch('api.batch_engine_api.require_api_key')
    @patch('api.batch_engine_api.rate_limit')
    @patch('api.batch_engine_api.get_batch_engine')
    @patch('api.batch_engine_api.get_db_session')
    def test_start_batch_all_stocks(self, mock_db_session, mock_get_engine, mock_rate_limit, mock_auth, client):
        """全銘柄バッチ開始テスト"""
        # 認証とレート制限をバイパス
        mock_auth.return_value = lambda f: f
        mock_rate_limit.return_value = lambda f: f
        
        # データベースセッションのモック
        mock_session = Mock()
        mock_db_session.return_value.__enter__.return_value = mock_session
        
        # 銘柄マスタのモック
        mock_stock = Mock()
        mock_stock.stock_code = "7203"
        mock_session.query.return_value.filter_by.return_value.all.return_value = [mock_stock]
        
        # BatchEngineのモック
        mock_engine = Mock()
        mock_engine.create_execution.return_value = "test_execution_id"
        mock_engine.start_execution.return_value = True
        mock_get_engine.return_value = mock_engine
        
        response = client.post('/api/v2/batch/start', 
                             json={'batch_type': 'all_stocks', 'interval': '1d'})
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'execution_id' in data
        assert data['execution_id'] == "test_execution_id"
        assert data['batch_type'] == 'all_stocks'
        assert data['status'] == 'started'
    
    @patch('api.batch_engine_api.require_api_key')
    @patch('api.batch_engine_api.get_batch_engine')
    def test_get_batch_status(self, mock_get_engine, mock_auth, client):
        """バッチステータス取得テスト"""
        mock_auth.return_value = lambda f: f
        
        mock_engine = Mock()
        mock_engine.get_execution_status.return_value = {
            'execution_id': 'test_id',
            'status': BatchStatus.RUNNING.value,
            'progress_percentage': 50.0
        }
        mock_get_engine.return_value = mock_engine
        
        response = client.get('/api/v2/batch/status/test_id')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['execution_id'] == 'test_id'
        assert data['status'] == BatchStatus.RUNNING.value

if __name__ == '__main__':
    pytest.main([__file__, '-v'])