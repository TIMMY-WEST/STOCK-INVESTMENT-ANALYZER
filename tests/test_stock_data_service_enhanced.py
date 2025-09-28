"""
StockDataService強化版のテストケース
Issue #37: エラーハンドリング強化とパフォーマンス最適化のテスト
"""

import pytest
import pandas as pd
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta
import time

from app.services.stock_data_service import (
    StockDataService,
    StockDataServiceError,
    DataFetchError,
    DataSaveError,
    ValidationError
)


class TestStockDataServiceEnhanced:
    """StockDataService強化版のテストクラス"""
    
    def test_validate_inputs_success(self):
        """入力値検証の成功ケース"""
        # 正常な入力値では例外が発生しないことを確認
        StockDataService._validate_inputs("AAPL", "1y", "1d")
        StockDataService._validate_inputs("GOOGL", "6mo", "1h")
        StockDataService._validate_inputs("MSFT", "max", "1wk")
    
    def test_validate_inputs_invalid_symbol(self):
        """無効な銘柄コードのテスト"""
        with pytest.raises(ValidationError, match="銘柄コード"):
            StockDataService._validate_inputs("", "1y", "1d")
        
        with pytest.raises(ValidationError, match="銘柄コード"):
            StockDataService._validate_inputs(None, "1y", "1d")
        
        with pytest.raises(ValidationError, match="銘柄コード"):
            StockDataService._validate_inputs(123, "1y", "1d")
    
    def test_validate_inputs_invalid_period(self):
        """無効な期間のテスト"""
        with pytest.raises(ValidationError, match="期間"):
            StockDataService._validate_inputs("AAPL", "", "1d")
        
        with pytest.raises(ValidationError, match="期間"):
            StockDataService._validate_inputs("AAPL", None, "1d")
    
    def test_validate_inputs_invalid_interval(self):
        """無効な時間軸のテスト"""
        with pytest.raises(ValidationError, match="サポートされていない時間軸"):
            StockDataService._validate_inputs("AAPL", "1y", "invalid")
        
        with pytest.raises(ValidationError, match="サポートされていない時間軸"):
            StockDataService._validate_inputs("AAPL", "1y", "2h")
    
    @patch('app.services.stock_data_service.yf.Ticker')
    def test_fetch_data_with_retry_success(self, mock_ticker):
        """リトライ機能付きデータ取得の成功ケース"""
        # モックデータの設定
        mock_data = pd.DataFrame({
            'Open': [100.0, 101.0],
            'High': [105.0, 106.0],
            'Low': [95.0, 96.0],
            'Close': [102.0, 103.0],
            'Volume': [1000, 1100]
        }, index=pd.date_range('2024-01-01', periods=2))
        
        mock_ticker_instance = Mock()
        mock_ticker_instance.history.return_value = mock_data
        mock_ticker.return_value = mock_ticker_instance
        
        # テスト実行
        result = StockDataService._fetch_data_with_retry("AAPL", "1y", "1d")
        
        # 検証
        assert not result.empty
        assert len(result) == 2
        mock_ticker.assert_called_once_with("AAPL")
        mock_ticker_instance.history.assert_called_once_with(period="1y", interval="1d")
    
    @patch('app.services.stock_data_service.yf.Ticker')
    @patch('app.services.stock_data_service.time.sleep')
    def test_fetch_data_with_retry_failure(self, mock_sleep, mock_ticker):
        """リトライ機能付きデータ取得の失敗ケース"""
        # yfinanceが例外を発生させるように設定
        mock_ticker_instance = Mock()
        mock_ticker_instance.history.side_effect = Exception("Network error")
        mock_ticker.return_value = mock_ticker_instance
        
        # テスト実行と検証
        with pytest.raises(DataFetchError, match="データ取得に失敗しました"):
            StockDataService._fetch_data_with_retry("AAPL", "1y", "1d")
        
        # リトライが3回実行されることを確認
        assert mock_ticker_instance.history.call_count == 3
        # スリープが2回呼ばれることを確認（最後の試行後はスリープしない）
        assert mock_sleep.call_count == 2
    
    @patch('app.services.stock_data_service.yf.Ticker')
    @patch('app.services.stock_data_service.time.sleep')
    def test_fetch_data_with_retry_empty_data_then_success(self, mock_sleep, mock_ticker):
        """空データ後に成功するケース"""
        # 最初は空データ、2回目で成功
        mock_data = pd.DataFrame({
            'Open': [100.0],
            'High': [105.0],
            'Low': [95.0],
            'Close': [102.0],
            'Volume': [1000]
        }, index=pd.date_range('2024-01-01', periods=1))
        
        mock_ticker_instance = Mock()
        mock_ticker_instance.history.side_effect = [pd.DataFrame(), mock_data]
        mock_ticker.return_value = mock_ticker_instance
        
        # テスト実行
        result = StockDataService._fetch_data_with_retry("AAPL", "1y", "1d")
        
        # 検証
        assert not result.empty
        assert len(result) == 1
        assert mock_ticker_instance.history.call_count == 2
        mock_sleep.assert_called_once()
    
    @patch('app.services.stock_data_service.StockDataService._fetch_data_with_retry')
    @patch('app.services.stock_data_service.StockDataService._save_data_to_database_optimized')
    def test_fetch_and_save_data_success(self, mock_save, mock_fetch):
        """データ取得・保存の成功ケース"""
        # モックデータの設定
        mock_data = pd.DataFrame({
            'Open': [100.0, 101.0],
            'High': [105.0, 106.0],
            'Low': [95.0, 96.0],
            'Close': [102.0, 103.0],
            'Volume': [1000, 1100]
        }, index=pd.date_range('2024-01-01', periods=2))
        
        mock_fetch.return_value = mock_data
        mock_save.return_value = (2, 0)  # 保存件数, スキップ件数
        
        # テスト実行
        result = StockDataService.fetch_and_save_data("AAPL", "1y", "1d")
        
        # 検証
        assert result['success'] is True
        assert result['data_count'] == 2
        assert result['skipped_count'] == 0
        assert result['total_records'] == 2
        assert result['symbol'] == "AAPL"
        assert result['interval'] == "1d"
        assert result['period'] == "1y"
        assert 'processing_time' in result
        assert 'date_range' in result
    
    @patch('app.services.stock_data_service.StockDataService._fetch_data_with_retry')
    def test_fetch_and_save_data_empty_data(self, mock_fetch):
        """空データの場合のテスト"""
        mock_fetch.return_value = pd.DataFrame()
        
        # テスト実行
        result = StockDataService.fetch_and_save_data("INVALID", "1y", "1d")
        
        # 検証
        assert result['success'] is False
        assert result['error_code'] == 'NO_DATA_FOUND'
        assert result['data_count'] == 0
        assert 'データが見つかりませんでした' in result['message']
    
    def test_fetch_and_save_data_validation_error(self):
        """バリデーションエラーのテスト"""
        # テスト実行
        result = StockDataService.fetch_and_save_data("", "1y", "1d")
        
        # 検証
        assert result['success'] is False
        assert result['error_code'] == 'VALIDATION_ERROR'
        assert result['data_count'] == 0
    
    @patch('app.services.stock_data_service.StockDataService._fetch_data_with_retry')
    def test_fetch_and_save_data_fetch_error(self, mock_fetch):
        """データ取得エラーのテスト"""
        mock_fetch.side_effect = DataFetchError("Network error")
        
        # テスト実行
        result = StockDataService.fetch_and_save_data("AAPL", "1y", "1d")
        
        # 検証
        assert result['success'] is False
        assert result['error_code'] == 'DATA_FETCH_ERROR'
        assert result['data_count'] == 0
        assert 'データ取得に失敗しました' in result['message']
    
    @patch('app.services.stock_data_service.StockDataService._fetch_data_with_retry')
    @patch('app.services.stock_data_service.StockDataService._save_data_to_database_optimized')
    def test_fetch_and_save_data_save_error(self, mock_save, mock_fetch):
        """データ保存エラーのテスト"""
        mock_data = pd.DataFrame({
            'Open': [100.0],
            'High': [105.0],
            'Low': [95.0],
            'Close': [102.0],
            'Volume': [1000]
        }, index=pd.date_range('2024-01-01', periods=1))
        
        mock_fetch.return_value = mock_data
        mock_save.side_effect = DataSaveError("Database error")
        
        # テスト実行
        result = StockDataService.fetch_and_save_data("AAPL", "1y", "1d")
        
        # 検証
        assert result['success'] is False
        assert result['error_code'] == 'DATA_SAVE_ERROR'
        assert result['data_count'] == 0
        assert 'データ保存に失敗しました' in result['message']
    
    def test_get_supported_intervals(self):
        """サポート時間軸リスト取得のテスト"""
        intervals = StockDataService.get_supported_intervals()
        
        expected_intervals = ['1m', '5m', '15m', '30m', '1h', '1d', '1wk', '1mo']
        assert intervals == expected_intervals
        
        # 元のリストが変更されないことを確認
        intervals.append('invalid')
        assert StockDataService.get_supported_intervals() == expected_intervals
    
    def test_validate_interval(self):
        """時間軸妥当性検証のテスト"""
        # 有効な時間軸
        assert StockDataService.validate_interval('1d') is True
        assert StockDataService.validate_interval('1h') is True
        assert StockDataService.validate_interval('1wk') is True
        
        # 無効な時間軸
        assert StockDataService.validate_interval('invalid') is False
        assert StockDataService.validate_interval('2h') is False
        assert StockDataService.validate_interval('') is False
    
    @patch('app.services.stock_data_service.get_db_session')
    def test_get_data_summary_daily_success(self, mock_session):
        """日足データサマリー取得の成功ケース"""
        # モックセッションの設定
        mock_session_instance = Mock()
        mock_session.__enter__.return_value = mock_session_instance
        
        # モックCRUDクラスの設定
        with patch('app.services.stock_data_service.TIMEFRAME_MODELS', {
            '1d': {
                'crud': Mock(
                    count_by_symbol=Mock(return_value=100),
                    get_latest_date_by_symbol=Mock(return_value=datetime(2024, 1, 10).date())
                )
            }
        }):
            # テスト実行
            result = StockDataService.get_data_summary("AAPL", "1d")
            
            # 検証
            assert result['success'] is True
            assert result['symbol'] == "AAPL"
            assert result['interval'] == "1d"
            assert result['data_count'] == 100
            assert result['latest_date'] == "2024-01-10"
    
    def test_get_data_summary_invalid_interval(self):
        """無効な時間軸でのデータサマリー取得テスト"""
        result = StockDataService.get_data_summary("AAPL", "invalid")
        
        assert result['success'] is False
        assert result['error_code'] == 'INVALID_INTERVAL'
        assert 'サポートされていない時間軸' in result['error']
    
    @patch('app.services.stock_data_service.get_db_session')
    def test_get_data_summary_error(self, mock_session):
        """データサマリー取得エラーのテスト"""
        mock_session.side_effect = Exception("Database connection error")
        
        result = StockDataService.get_data_summary("AAPL", "1d")
        
        assert result['success'] is False
        assert result['error_code'] == 'SUMMARY_ERROR'
        assert 'データサマリー取得中にエラーが発生しました' in result['error']


class TestBatchProcessing:
    """バッチ処理のテストクラス"""
    
    @patch('app.services.stock_data_service.get_db_session')
    def test_save_batch_data_success(self, mock_session):
        """バッチデータ保存の成功ケース"""
        # モックセッションの設定
        mock_session_instance = Mock()
        mock_session.__enter__.return_value = mock_session_instance
        
        # モックCRUDクラスの設定
        mock_crud = Mock()
        mock_crud.create = Mock()
        
        # テストデータ
        batch_data = [
            {'symbol': 'AAPL', 'date': datetime(2024, 1, 1).date(), 'open': 100.0},
            {'symbol': 'AAPL', 'date': datetime(2024, 1, 2).date(), 'open': 101.0}
        ]
        
        # テスト実行
        saved_count = StockDataService._save_batch_data(mock_session_instance, mock_crud, batch_data)
        
        # 検証
        assert saved_count == 2
        assert mock_crud.create.call_count == 2
        mock_session_instance.commit.assert_called_once()
    
    @patch('app.services.stock_data_service.get_db_session')
    def test_save_batch_data_with_integrity_error(self, mock_session):
        """重複データによるIntegrityErrorのテスト"""
        from sqlalchemy.exc import IntegrityError
        
        # モックセッションの設定
        mock_session_instance = Mock()
        mock_session.__enter__.return_value = mock_session_instance
        
        # モックCRUDクラスの設定（最初の呼び出しでIntegrityError）
        mock_crud = Mock()
        mock_crud.create.side_effect = [IntegrityError("", "", ""), None]
        
        # テストデータ
        batch_data = [
            {'symbol': 'AAPL', 'date': datetime(2024, 1, 1).date(), 'open': 100.0},
            {'symbol': 'AAPL', 'date': datetime(2024, 1, 2).date(), 'open': 101.0}
        ]
        
        # テスト実行
        saved_count = StockDataService._save_batch_data(mock_session_instance, mock_crud, batch_data)
        
        # 検証
        assert saved_count == 1  # 1件はIntegrityErrorでスキップ、1件は成功
        assert mock_crud.create.call_count == 2
        assert mock_session_instance.rollback.call_count == 1
        mock_session_instance.commit.assert_called_once()


class TestPerformanceOptimization:
    """パフォーマンス最適化のテストクラス"""
    
    def test_batch_size_configuration(self):
        """バッチサイズ設定のテスト"""
        assert StockDataService.BATCH_SIZE == 1000
        assert StockDataService.MAX_RETRY_COUNT == 3
        assert StockDataService.RETRY_DELAY == 1.0
    
    @patch('app.services.stock_data_service.time.time')
    @patch('app.services.stock_data_service.StockDataService._fetch_data_with_retry')
    @patch('app.services.stock_data_service.StockDataService._save_data_to_database_optimized')
    def test_processing_time_measurement(self, mock_save, mock_fetch, mock_time):
        """処理時間測定のテスト"""
        # 時間のモック設定
        mock_time.side_effect = [0.0, 2.5]  # 開始時刻と終了時刻
        
        # モックデータの設定
        mock_data = pd.DataFrame({
            'Open': [100.0],
            'High': [105.0],
            'Low': [95.0],
            'Close': [102.0],
            'Volume': [1000]
        }, index=pd.date_range('2024-01-01', periods=1))
        
        mock_fetch.return_value = mock_data
        mock_save.return_value = (1, 0)
        
        # テスト実行
        result = StockDataService.fetch_and_save_data("AAPL", "1y", "1d")
        
        # 検証
        assert result['success'] is True
        assert result['processing_time'] == 2.5