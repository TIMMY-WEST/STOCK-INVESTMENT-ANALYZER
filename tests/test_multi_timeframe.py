"""
各時間軸でのデータ取得・保存機能のテストコード
Issue #37 対応
"""

import pytest
import json
from datetime import datetime, date, timedelta
from unittest.mock import patch, MagicMock
import pandas as pd

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'app'))

from app import app
from models import (
    get_db_session, 
    StockDaily, StockIntraday, StockWeekly, StockMonthly,
    StockDailyCRUD, StockIntradayCRUD, StockWeeklyCRUD, StockMonthlyCRUD,
    TIMEFRAME_MODELS
)
from services.stock_data_service import StockDataService


class TestMultiTimeframeAPI:
    """各時間軸対応APIのテストクラス"""
    
    @pytest.fixture
    def client(self):
        """テスト用Flaskクライアント"""
        app.config['TESTING'] = True
        with app.test_client() as client:
            yield client
    
    def test_get_supported_intervals(self, client):
        """サポートされている時間軸リスト取得のテスト"""
        response = client.get('/api/intervals')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['success'] is True
        assert 'intervals' in data
        assert isinstance(data['intervals'], list)
        assert '1d' in data['intervals']
        assert '1h' in data['intervals']
        assert '1wk' in data['intervals']
        assert '1mo' in data['intervals']
    
    def test_fetch_data_with_interval_parameter(self, client):
        """時間軸パラメータ付きでのデータ取得テスト"""
        # モックデータの準備
        mock_data = pd.DataFrame({
            'Open': [100.0, 101.0],
            'High': [105.0, 106.0],
            'Low': [99.0, 100.0],
            'Close': [104.0, 105.0],
            'Volume': [1000, 1100]
        }, index=pd.date_range('2024-01-01', periods=2, freq='D'))
        
        with patch('services.stock_data_service.yf.Ticker') as mock_ticker:
            mock_instance = MagicMock()
            mock_instance.history.return_value = mock_data
            mock_ticker.return_value = mock_instance
            
            # 日足データ取得テスト
            response = client.post('/api/fetch-data', 
                                 json={
                                     'symbol': 'TEST.T',
                                     'period': '5d',
                                     'interval': '1d'
                                 })
            
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['success'] is True
            assert 'data_count' in data
    
    def test_fetch_data_invalid_interval(self, client):
        """無効な時間軸でのエラーテスト"""
        response = client.post('/api/fetch-data', 
                             json={
                                 'symbol': 'TEST.T',
                                 'period': '1d',
                                 'interval': 'invalid'
                             })
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['success'] is False
        assert 'サポートされていない時間軸' in data['message']
    
    def test_fetch_data_missing_symbol(self, client):
        """銘柄コード未指定でのエラーテスト"""
        response = client.post('/api/fetch-data', 
                             json={
                                 'period': '1d',
                                 'interval': '1d'
                             })
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['success'] is False
        assert '銘柄コード (symbol) が必要です' in data['message']
    
    def test_data_summary_api(self, client):
        """データサマリーAPI のテスト"""
        response = client.post('/api/data-summary',
                             json={
                                 'symbol': 'TEST.T',
                                 'interval': '1d'
                             })
        
        # データが存在しない場合でもエラーにならないことを確認
        assert response.status_code in [200, 400]
        data = json.loads(response.data)
        assert 'success' in data
    
    def test_data_summary_invalid_interval(self, client):
        """データサマリーAPI 無効時間軸テスト"""
        response = client.post('/api/data-summary',
                             json={
                                 'symbol': 'TEST.T',
                                 'interval': 'invalid'
                             })
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['success'] is False


class TestStockDataService:
    """StockDataServiceクラスのテストクラス"""
    
    def test_validate_interval(self):
        """時間軸妥当性検証のテスト"""
        # 有効な時間軸
        assert StockDataService.validate_interval('1d') is True
        assert StockDataService.validate_interval('1h') is True
        assert StockDataService.validate_interval('1wk') is True
        assert StockDataService.validate_interval('1mo') is True
        
        # 無効な時間軸
        assert StockDataService.validate_interval('invalid') is False
        assert StockDataService.validate_interval('') is False
        assert StockDataService.validate_interval(None) is False
    
    def test_get_supported_intervals(self):
        """サポート時間軸リスト取得のテスト"""
        intervals = StockDataService.get_supported_intervals()
        assert isinstance(intervals, list)
        assert len(intervals) > 0
        assert '1d' in intervals
        assert '1h' in intervals
        assert '1wk' in intervals
        assert '1mo' in intervals
    
    @patch('services.stock_data_service.yf.Ticker')
    def test_fetch_and_save_data_success(self, mock_ticker):
        """データ取得・保存成功のテスト"""
        # モックデータの準備
        mock_data = pd.DataFrame({
            'Open': [100.0],
            'High': [105.0],
            'Low': [99.0],
            'Close': [104.0],
            'Volume': [1000]
        }, index=pd.date_range('2024-01-01', periods=1, freq='D'))
        
        mock_instance = MagicMock()
        mock_instance.history.return_value = mock_data
        mock_ticker.return_value = mock_instance
        
        # テスト実行
        result = StockDataService.fetch_and_save_data('TEST.T', '1d', '1d')
        
        # 結果検証
        assert result['success'] is True
        assert 'data_count' in result
        assert result['symbol'] == 'TEST.T'
        assert result['interval'] == '1d'
    
    @patch('services.stock_data_service.yf.Ticker')
    def test_fetch_and_save_data_no_data(self, mock_ticker):
        """データ取得失敗のテスト"""
        # 空のデータフレームを返すモック
        mock_instance = MagicMock()
        mock_instance.history.return_value = pd.DataFrame()
        mock_ticker.return_value = mock_instance
        
        # テスト実行
        result = StockDataService.fetch_and_save_data('INVALID.T', '1d', '1d')
        
        # 結果検証
        assert result['success'] is False
        assert 'データが取得できませんでした' in result['message']
        assert result['data_count'] == 0
    
    def test_fetch_and_save_data_invalid_interval(self):
        """無効な時間軸でのエラーテスト"""
        result = StockDataService.fetch_and_save_data('TEST.T', '1d', 'invalid')
        
        assert result['success'] is False
        assert 'サポートされていない時間軸' in result['message']


class TestTimeframeModels:
    """各時間軸モデルのテストクラス"""
    
    def test_timeframe_models_mapping(self):
        """TIMEFRAME_MODELSマッピングのテスト"""
        assert '1d' in TIMEFRAME_MODELS
        assert '1h' in TIMEFRAME_MODELS
        assert '1wk' in TIMEFRAME_MODELS
        assert '1mo' in TIMEFRAME_MODELS
        
        # 各モデルに必要なキーが存在することを確認
        for interval, model_info in TIMEFRAME_MODELS.items():
            assert 'model' in model_info
            assert 'crud' in model_info
            assert model_info['model'] is not None
            assert model_info['crud'] is not None
    
    def test_stock_intraday_model(self):
        """StockIntradayモデルのテスト"""
        # モデルの基本属性確認
        assert hasattr(StockIntraday, 'symbol')
        assert hasattr(StockIntraday, 'datetime')
        assert hasattr(StockIntraday, 'interval')
        assert hasattr(StockIntraday, 'open')
        assert hasattr(StockIntraday, 'high')
        assert hasattr(StockIntraday, 'low')
        assert hasattr(StockIntraday, 'close')
        assert hasattr(StockIntraday, 'volume')
    
    def test_stock_weekly_model(self):
        """StockWeeklyモデルのテスト"""
        # モデルの基本属性確認
        assert hasattr(StockWeekly, 'symbol')
        assert hasattr(StockWeekly, 'week_start_date')
        assert hasattr(StockWeekly, 'open')
        assert hasattr(StockWeekly, 'high')
        assert hasattr(StockWeekly, 'low')
        assert hasattr(StockWeekly, 'close')
        assert hasattr(StockWeekly, 'volume')
    
    def test_stock_monthly_model(self):
        """StockMonthlyモデルのテスト"""
        # モデルの基本属性確認
        assert hasattr(StockMonthly, 'symbol')
        assert hasattr(StockMonthly, 'year')
        assert hasattr(StockMonthly, 'month')
        assert hasattr(StockMonthly, 'open')
        assert hasattr(StockMonthly, 'high')
        assert hasattr(StockMonthly, 'low')
        assert hasattr(StockMonthly, 'close')
        assert hasattr(StockMonthly, 'volume')


class TestDataIntegrity:
    """データ整合性のテストクラス"""
    
    def test_duplicate_data_handling(self):
        """重複データ処理のテスト"""
        # このテストは実際のデータベース操作を伴うため、
        # テスト用データベースでの実行が必要
        # 現在は基本的な構造テストのみ実装
        pass
    
    def test_data_validation(self):
        """データ妥当性検証のテスト"""
        # 価格データの妥当性（負の値でないこと等）
        # 出来高データの妥当性（負の値でないこと等）
        # 日付・時刻データの妥当性
        # 現在は基本的な構造テストのみ実装
        pass


if __name__ == '__main__':
    pytest.main([__file__, '-v'])