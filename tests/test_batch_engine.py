"""
BatchEngineクラスのテストコード

Phase 2のバッチエンジン機能をテストします。
"""

import pytest
import threading
import time
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime
from queue import Queue

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'app'))

from services.batch_engine import (
    BatchTask, ProgressManager, StockDataWorker, BatchEngine, 
    BatchStatus, WorkerStatus, BatchExecutionInfo
)

class TestBatchTask:
    """BatchTaskクラスのテスト"""
    
    def test_batch_task_initialization(self):
        """BatchTaskの初期化テスト"""
        task = BatchTask(
            id="test_001",
            symbol="7203",
            interval="1d",
            period="1y"
        )
        
        assert task.id == "test_001"
        assert task.symbol == "7203"
        assert task.interval == "1d"
        assert task.period == "1y"
        assert task.retry_count == 0
        assert task.created_at is not None


class TestProgressManager:
    """ProgressManagerクラスのテスト"""
    
    def test_progress_manager_initialization(self):
        """ProgressManagerの初期化テスト"""
        manager = ProgressManager()
        assert len(manager.callbacks) == 0
    
    def test_callback_management(self):
        """コールバック管理テスト"""
        manager = ProgressManager()
        callback = Mock()
        
        # コールバック追加
        manager.add_callback(callback)
        assert len(manager.callbacks) == 1
        assert callback in manager.callbacks
        
        # コールバック削除
        manager.remove_callback(callback)
        assert len(manager.callbacks) == 0
        assert callback not in manager.callbacks


class TestStockDataWorker:
    """StockDataWorkerクラスのテスト"""
    
    def test_worker_initialization(self):
        """ワーカーの初期化テスト"""
        mock_engine = Mock()
        
        worker = StockDataWorker(
            worker_id="test_worker",
            batch_engine=mock_engine
        )
        
        assert worker.worker_id == "test_worker"
        assert worker.batch_engine == mock_engine
        assert worker.status == WorkerStatus.IDLE
        assert worker.current_task is None

class TestBatchEngine:
    """BatchEngineクラスのテスト"""
    
    def test_batch_engine_initialization(self):
        """BatchEngineの初期化テスト"""
        engine = BatchEngine(max_workers=2, queue_size=100)
        
        assert engine.max_workers == 2
        assert engine.queue_size == 100
        assert len(engine.workers) == 0
        assert len(engine.executions) == 0
        assert engine.progress_manager is not None
        assert not engine._shutdown
    
    @patch('services.batch_engine.get_db_session')
    def test_worker_management(self, mock_db_session):
        """ワーカー管理テスト"""
        mock_session = Mock()
        mock_db_session.return_value.__enter__.return_value = mock_session
        
        engine = BatchEngine(max_workers=2)
        
        # ワーカー開始
        engine.start_workers()
        assert len(engine.workers) == 2
        
        # ワーカー停止
        engine.stop_workers()
        assert len(engine.workers) == 0
    
    @patch('services.batch_engine.get_db_session')
    def test_execution_creation(self, mock_db_session):
        """実行作成テスト"""
        mock_session = Mock()
        mock_db_session.return_value.__enter__.return_value = mock_session
        
        engine = BatchEngine()
        
        execution_id = engine.create_execution(
            batch_type="symbol_list",
            total_tasks=10
        )
        
        assert execution_id is not None
        assert execution_id in engine.executions
        
        execution = engine.executions[execution_id]
        assert execution.batch_type == "symbol_list"
        assert execution.status == BatchStatus.PENDING
        assert execution.total_tasks == 10
    
    @patch('services.batch_engine.get_db_session')
    def test_status_retrieval(self, mock_db_session):
        """ステータス取得テスト"""
        mock_session = Mock()
        mock_db_session.return_value.__enter__.return_value = mock_session
        
        engine = BatchEngine()
        
        execution_id = engine.create_execution(
            batch_type="symbol_list",
            total_tasks=5
        )
        
        status = engine.get_execution_status(execution_id)
        assert status['execution_id'] == execution_id
        assert status['status'] == BatchStatus.PENDING.value
        assert status['total_tasks'] == 5

if __name__ == '__main__':
    pytest.main([__file__, '-v'])