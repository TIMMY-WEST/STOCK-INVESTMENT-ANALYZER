"""バッチ処理エンジン（Phase 2）

高度なバッチ処理エンジンとワーカープール管理による並列データ取得機能を提供します。
"""

import asyncio
import logging
import threading
import time
import uuid
from concurrent.futures import ThreadPoolExecutor, as_completed, Future
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional, Callable, Any, Set
from queue import Queue, Empty
import json

from sqlalchemy.orm import Session
from models import BatchExecution, BatchExecutionDetail, get_db_session
from services.stock_data_fetcher import StockDataFetcher, StockDataFetchError
from services.stock_data_saver import StockDataSaver, StockDataSaveError

logger = logging.getLogger(__name__)


class BatchStatus(Enum):
    """バッチ実行ステータス"""
    PENDING = "pending"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class WorkerStatus(Enum):
    """ワーカーステータス"""
    IDLE = "idle"
    WORKING = "working"
    ERROR = "error"
    STOPPED = "stopped"


@dataclass
class BatchTask:
    """バッチタスク"""
    id: str
    symbol: str
    interval: str
    period: Optional[str]
    priority: int = 0
    retry_count: int = 0
    max_retries: int = 3
    created_at: datetime = field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None
    worker_id: Optional[str] = None
    execution_id: Optional[str] = None

    def __post_init__(self):
        if not self.id:
            self.id = str(uuid.uuid4())
    
    @property
    def task_id(self) -> str:
        """タスクIDを取得"""
        return self.id


@dataclass
class BatchExecutionInfo:
    """バッチ実行情報（メモリ内管理用）"""
    execution_id: str
    batch_type: str
    status: BatchStatus
    total_tasks: int
    completed_tasks: int = 0
    failed_tasks: int = 0
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    error_message: Optional[str] = None
    progress_callback: Optional[Callable] = None
    db_execution_id: Optional[int] = None  # データベースのID
    
    @property
    def progress_percentage(self) -> float:
        """進捗率を計算"""
        if self.total_tasks == 0:
            return 0.0
        return (self.completed_tasks / self.total_tasks) * 100.0
    
    @property
    def success_rate(self) -> float:
        """成功率を計算"""
        processed = self.completed_tasks + self.failed_tasks
        if processed == 0:
            return 0.0
        return (self.completed_tasks / processed) * 100.0


class StockDataWorker:
    """株価データ取得ワーカー"""
    
    def __init__(self, worker_id: str, batch_engine: 'BatchEngine'):
        self.worker_id = worker_id
        self.batch_engine = batch_engine
        self.status = WorkerStatus.IDLE
        self.current_task: Optional[BatchTask] = None
        self.fetcher = StockDataFetcher()
        self.saver = StockDataSaver()
        self.logger = logging.getLogger(f"{__name__}.Worker.{worker_id}")
        self.stop_event = threading.Event()
        self.thread: Optional[threading.Thread] = None
        self.processed_tasks = 0
        self.failed_tasks = 0
        self.last_activity: Optional[datetime] = None
        
    def start(self):
        """ワーカーを開始"""
        if self.thread and self.thread.is_alive():
            return
        
        self.stop_event.clear()
        self.thread = threading.Thread(target=self._run, daemon=True)
        self.thread.start()
        self.logger.info(f"ワーカー {self.worker_id} を開始しました")
    
    def stop(self):
        """ワーカーを停止"""
        self.stop_event.set()
        if self.thread and self.thread.is_alive():
            self.thread.join(timeout=5.0)
        self.status = WorkerStatus.STOPPED
        self.logger.info(f"ワーカー {self.worker_id} を停止しました")
    
    def join(self, timeout: Optional[float] = None) -> None:
        """ワーカースレッドの終了を待機"""
        if self.thread and self.thread.is_alive():
            self.thread.join(timeout=timeout)
    
    def _run(self):
        """ワーカーのメインループ"""
        self.logger.info(f"ワーカー {self.worker_id} のメインループを開始")
        
        while not self.stop_event.is_set():
            try:
                # タスクを取得
                task = self.batch_engine.get_next_task()
                if task is None:
                    # タスクがない場合は少し待機
                    time.sleep(0.1)
                    continue
                
                self.current_task = task
                self.status = WorkerStatus.WORKING
                task.worker_id = self.worker_id
                task.started_at = datetime.now()
                
                self.logger.info(f"タスク開始: {task.symbol} (ID: {task.id})")
                
                # タスクを実行
                result = self._execute_task(task)
                
                # 結果を報告
                self.batch_engine.report_task_result(task, result)
                
                # カウンターを更新
                if result.get('success', False):
                    self.processed_tasks += 1
                else:
                    self.failed_tasks += 1
                self.last_activity = datetime.now()
                
                self.current_task = None
                self.status = WorkerStatus.IDLE
                
            except Exception as e:
                self.logger.error(f"ワーカー {self.worker_id} でエラー: {e}")
                self.status = WorkerStatus.ERROR
                if self.current_task:
                    self.batch_engine.report_task_result(
                        self.current_task, 
                        {'success': False, 'error': str(e)}
                    )
                time.sleep(1.0)  # エラー時は少し待機
    
    def _execute_task(self, task: BatchTask) -> Dict[str, Any]:
        """タスクを実行"""
        try:
            # データ取得
            df = self.fetcher.fetch_stock_data(
                symbol=task.symbol,
                interval=task.interval,
                period=task.period
            )
            
            # データ変換
            data_list = self.fetcher.convert_to_dict(df, task.interval)
            
            # データ保存
            save_result = self.saver.save_stock_data(
                symbol=task.symbol,
                interval=task.interval,
                data_list=data_list
            )
            
            return {
                'success': True,
                'symbol': task.symbol,
                'interval': task.interval,
                'records_fetched': len(data_list),
                'records_saved': save_result.get('saved', 0),
                'worker_id': self.worker_id
            }
            
        except (StockDataFetchError, StockDataSaveError) as e:
            return {
                'success': False,
                'symbol': task.symbol,
                'interval': task.interval,
                'error': str(e),
                'worker_id': self.worker_id
            }
        except Exception as e:
            return {
                'success': False,
                'symbol': task.symbol,
                'interval': task.interval,
                'error': f"予期しないエラー: {str(e)}",
                'worker_id': self.worker_id
            }


class ProgressManager:
    """進捗管理クラス"""
    
    def __init__(self):
        self.callbacks: List[Callable[[Dict[str, Any]], None]] = []
        self.logger = logging.getLogger(f"{__name__}.ProgressManager")
    
    def add_callback(self, callback: Callable[[Dict[str, Any]], None]):
        """進捗通知コールバックを追加"""
        self.callbacks.append(callback)
    
    def remove_callback(self, callback: Callable[[Dict[str, Any]], None]):
        """進捗通知コールバックを削除"""
        if callback in self.callbacks:
            self.callbacks.remove(callback)
    
    def notify_progress(self, execution: BatchExecution, additional_data: Optional[Dict[str, Any]] = None):
        """進捗を通知"""
        progress_data = {
            'execution_id': execution.id,
            'name': execution.name,
            'status': execution.status.value,
            'total_tasks': execution.total_tasks,
            'completed_tasks': execution.completed_tasks,
            'failed_tasks': execution.failed_tasks,
            'cancelled_tasks': execution.cancelled_tasks,
            'progress_percentage': execution.progress_percentage,
            'created_at': execution.created_at.isoformat(),
            'started_at': execution.started_at.isoformat() if execution.started_at else None,
            'completed_at': execution.completed_at.isoformat() if execution.completed_at else None,
            'timestamp': datetime.now().isoformat()
        }
        
        if additional_data:
            progress_data.update(additional_data)
        
        for callback in self.callbacks:
            try:
                callback(progress_data)
            except Exception as e:
                self.logger.error(f"進捗通知コールバックエラー: {e}")


class BatchEngine:
    """バッチ処理エンジン"""
    
    def __init__(self, max_workers: int = 4, queue_size: int = 1000):
        self.max_workers = max_workers
        self.queue_size = queue_size
        self.task_queue = Queue(maxsize=queue_size)
        self.result_queue = Queue()
        self.workers: Dict[str, StockDataWorker] = {}
        self.executions: Dict[str, BatchExecutionInfo] = {}
        self.progress_manager = ProgressManager()
        self._lock = threading.Lock()
        self._shutdown = False
        
        # ログ設定
        self.logger = logging.getLogger(__name__)
        
    def start_workers(self) -> None:
        """ワーカーを起動"""
        with self._lock:
            if self._shutdown:
                raise RuntimeError("BatchEngine is shutdown")
                
            for i in range(self.max_workers):
                worker_id = f"worker_{i}"
                worker = StockDataWorker(
                    worker_id=worker_id,
                    batch_engine=self
                )
                worker.start()
                self.workers[worker_id] = worker
                
        self.logger.info(f"Started {self.max_workers} workers")
    
    def stop_workers(self) -> None:
        """ワーカーを停止"""
        with self._lock:
            for worker in self.workers.values():
                worker.stop()
                
            # 全ワーカーの終了を待機
            for worker in self.workers.values():
                worker.join(timeout=30)
                
            self.workers.clear()
            
        self.logger.info("All workers stopped")
    
    def shutdown(self) -> None:
        """エンジンをシャットダウン"""
        self._shutdown = True
        self.stop_workers()
        self.logger.info("BatchEngine shutdown completed")
    
    def get_next_task(self) -> Optional[BatchTask]:
        """次のタスクを取得"""
        try:
            return self.task_queue.get(timeout=0.1)
        except Empty:
            return None
    
    def report_task_result(self, task: BatchTask, result: Dict[str, Any]) -> None:
        """タスク結果を報告"""
        execution_id = getattr(task, 'execution_id', None)
        if not execution_id:
            return
            
        with self._lock:
            if execution_id not in self.executions:
                return
                
            execution = self.executions[execution_id]
            
            if result.get('success', False):
                execution.completed_tasks += 1
            else:
                execution.failed_tasks += 1
                
            # 進捗コールバックを呼び出し
            if execution.progress_callback:
                try:
                    execution.progress_callback({
                        'execution_id': execution_id,
                        'completed_tasks': execution.completed_tasks,
                        'failed_tasks': execution.failed_tasks,
                        'total_tasks': execution.total_tasks,
                        'progress_percentage': execution.progress_percentage
                    })
                except Exception as e:
                    self.logger.error(f"Progress callback error: {e}")
                    
            # 完了チェック
            total_processed = execution.completed_tasks + execution.failed_tasks
            if total_processed >= execution.total_tasks:
                if execution.failed_tasks == 0:
                    execution.status = BatchStatus.COMPLETED
                else:
                    execution.status = BatchStatus.FAILED
                    
                execution.end_time = datetime.now()
    
    def create_execution(self, batch_type: str, total_tasks: int, 
                        progress_callback: Optional[Callable] = None) -> str:
        """バッチ実行を作成"""
        execution_id = str(uuid.uuid4())
        
        # データベースにバッチ実行を記録
        db_execution_id = None
        try:
            with get_db_session() as session:
                db_execution = BatchExecution(
                    batch_type=batch_type,
                    status='pending',
                    total_stocks=total_tasks,
                    processed_stocks=0,
                    successful_stocks=0,
                    failed_stocks=0
                )
                session.add(db_execution)
                session.commit()
                db_execution_id = db_execution.id
        except Exception as e:
            self.logger.error(f"Failed to create database execution: {e}")
        
        execution = BatchExecutionInfo(
            execution_id=execution_id,
            batch_type=batch_type,
            status=BatchStatus.PENDING,
            total_tasks=total_tasks,
            progress_callback=progress_callback,
            db_execution_id=db_execution_id
        )
        
        with self._lock:
            self.executions[execution_id] = execution
            
        self.logger.info(f"Created batch execution: {execution_id}")
        return execution_id
    
    def start_execution(self, execution_id: str, tasks: List[BatchTask]) -> None:
        """バッチ実行を開始"""
        with self._lock:
            if execution_id not in self.executions:
                raise ValueError(f"Execution not found: {execution_id}")
                
            execution = self.executions[execution_id]
            if execution.status != BatchStatus.PENDING:
                raise ValueError(f"Execution is not in pending state: {execution.status}")
                
            execution.status = BatchStatus.RUNNING
            execution.start_time = datetime.now()
            
        # データベースのステータスを更新
        if execution.db_execution_id:
            try:
                with get_db_session() as session:
                    db_execution = session.query(BatchExecution).filter_by(id=execution.db_execution_id).first()
                    if db_execution:
                        db_execution.status = 'running'
                        session.commit()
            except Exception as e:
                self.logger.error(f"Failed to update database execution status: {e}")
        
        # タスクをキューに追加
        for task in tasks:
            task.execution_id = execution_id
            self.task_queue.put(task)
            
        self.logger.info(f"Started batch execution: {execution_id} with {len(tasks)} tasks")
    
    def pause_execution(self, execution_id: str) -> None:
        """バッチ実行を一時停止"""
        with self._lock:
            if execution_id not in self.executions:
                raise ValueError(f"Execution not found: {execution_id}")
                
            execution = self.executions[execution_id]
            if execution.status == BatchStatus.RUNNING:
                execution.status = BatchStatus.PAUSED
                
                # データベースのステータスを更新
                if execution.db_execution_id:
                    try:
                        with get_db_session() as session:
                            db_execution = session.query(BatchExecution).filter_by(id=execution.db_execution_id).first()
                            if db_execution:
                                db_execution.status = 'paused'
                                session.commit()
                    except Exception as e:
                        self.logger.error(f"Failed to update database execution status: {e}")
                        
                self.logger.info(f"Paused batch execution: {execution_id}")
    
    def resume_execution(self, execution_id: str) -> None:
        """バッチ実行を再開"""
        with self._lock:
            if execution_id not in self.executions:
                raise ValueError(f"Execution not found: {execution_id}")
                
            execution = self.executions[execution_id]
            if execution.status == BatchStatus.PAUSED:
                execution.status = BatchStatus.RUNNING
                
                # データベースのステータスを更新
                if execution.db_execution_id:
                    try:
                        with get_db_session() as session:
                            db_execution = session.query(BatchExecution).filter_by(id=execution.db_execution_id).first()
                            if db_execution:
                                db_execution.status = 'running'
                                session.commit()
                    except Exception as e:
                        self.logger.error(f"Failed to update database execution status: {e}")
                        
                self.logger.info(f"Resumed batch execution: {execution_id}")
    
    def cancel_execution(self, execution_id: str) -> None:
        """バッチ実行をキャンセル"""
        with self._lock:
            if execution_id not in self.executions:
                raise ValueError(f"Execution not found: {execution_id}")
                
            execution = self.executions[execution_id]
            if execution.status in [BatchStatus.RUNNING, BatchStatus.PAUSED]:
                execution.status = BatchStatus.CANCELLED
                execution.end_time = datetime.now()
                
                # データベースのステータスを更新
                if execution.db_execution_id:
                    try:
                        with get_db_session() as session:
                            db_execution = session.query(BatchExecution).filter_by(id=execution.db_execution_id).first()
                            if db_execution:
                                db_execution.status = 'cancelled'
                                db_execution.end_time = execution.end_time
                                session.commit()
                    except Exception as e:
                        self.logger.error(f"Failed to update database execution status: {e}")
                        
                self.logger.info(f"Cancelled batch execution: {execution_id}")
    
    def get_task(self, worker_id: str) -> Optional[BatchTask]:
        """ワーカーがタスクを取得"""
        try:
            task = self.task_queue.get_nowait()
            
            # 実行がキャンセルされている場合はタスクを破棄
            with self._lock:
                if task.execution_id in self.executions:
                    execution = self.executions[task.execution_id]
                    if execution.status == BatchStatus.CANCELLED:
                        return None
                        
            return task
        except Empty:
            return None
    
    def report_result(self, worker_id: str, task: BatchTask, success: bool, 
                     error_message: Optional[str] = None) -> None:
        """ワーカーが結果を報告"""
        with self._lock:
            if task.execution_id not in self.executions:
                return
                
            execution = self.executions[task.execution_id]
            
            if success:
                execution.completed_tasks += 1
            else:
                execution.failed_tasks += 1
                
            # データベースの進捗を更新
            if execution.db_execution_id:
                try:
                    with get_db_session() as session:
                        db_execution = session.query(BatchExecution).filter_by(id=execution.db_execution_id).first()
                        if db_execution:
                            db_execution.processed_stocks = execution.completed_tasks + execution.failed_tasks
                            db_execution.successful_stocks = execution.completed_tasks
                            db_execution.failed_stocks = execution.failed_tasks
                            session.commit()
                except Exception as e:
                    self.logger.error(f"Failed to update database execution progress: {e}")
                    
            # 進捗コールバックを呼び出し
            if execution.progress_callback:
                try:
                    execution.progress_callback(execution)
                except Exception as e:
                    self.logger.error(f"Progress callback error: {e}")
                    
            # 完了チェック
            total_processed = execution.completed_tasks + execution.failed_tasks
            if total_processed >= execution.total_tasks:
                if execution.failed_tasks == 0:
                    execution.status = BatchStatus.COMPLETED
                    db_status = 'completed'
                else:
                    execution.status = BatchStatus.FAILED
                    db_status = 'failed'
                    
                execution.end_time = datetime.now()
                
                # データベースの最終ステータスを更新
                if execution.db_execution_id:
                    try:
                        with get_db_session() as session:
                            db_execution = session.query(BatchExecution).filter_by(id=execution.db_execution_id).first()
                            if db_execution:
                                db_execution.status = db_status
                                db_execution.end_time = execution.end_time
                                session.commit()
                    except Exception as e:
                        self.logger.error(f"Failed to update database execution final status: {e}")
                
        self.logger.debug(f"Task result reported: {task.task_id}, success: {success}")
    
    def get_execution_status(self, execution_id: str) -> Optional[Dict[str, Any]]:
        """実行ステータスを取得"""
        with self._lock:
            if execution_id not in self.executions:
                return None
                
            execution = self.executions[execution_id]
            return {
                'execution_id': execution.execution_id,
                'batch_type': execution.batch_type,
                'status': execution.status.value,
                'total_tasks': execution.total_tasks,
                'completed_tasks': execution.completed_tasks,
                'failed_tasks': execution.failed_tasks,
                'progress_percentage': execution.progress_percentage,
                'success_rate': execution.success_rate,
                'start_time': execution.start_time.isoformat() if execution.start_time else None,
                'end_time': execution.end_time.isoformat() if execution.end_time else None,
                'error_message': execution.error_message,
                'db_execution_id': execution.db_execution_id
            }
    
    def get_worker_status(self) -> Dict[str, Any]:
        """ワーカーステータスを取得"""
        with self._lock:
            worker_statuses = {}
            for worker_id, worker in self.workers.items():
                worker_statuses[worker_id] = {
                    'worker_id': worker_id,
                    'status': worker.status.value,
                    'current_task': worker.current_task.task_id if worker.current_task else None,
                    'processed_tasks': worker.processed_tasks,
                    'failed_tasks': worker.failed_tasks,
                    'last_activity': worker.last_activity.isoformat() if worker.last_activity else None
                }
                
            return {
                'total_workers': len(self.workers),
                'active_workers': sum(1 for w in self.workers.values() if w.status == WorkerStatus.WORKING),
                'workers': worker_statuses
            }
    
    def get_queue_status(self) -> Dict[str, Any]:
        """キューステータスを取得"""
        return {
            'task_queue_size': self.task_queue.qsize(),
            'result_queue_size': self.result_queue.qsize(),
            'task_queue_max_size': self.queue_size
        }