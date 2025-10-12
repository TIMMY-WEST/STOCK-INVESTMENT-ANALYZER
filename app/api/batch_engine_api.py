"""
Phase 2 バッチエンジンAPI

高度なバッチ処理機能を提供するAPIエンドポイント
- 複数ワーカーによる並列処理
- データベース永続化
- 詳細な進捗管理
- エラーハンドリング
"""

from flask import Blueprint, request, jsonify
from typing import Dict, Any, List, Optional
import logging
from datetime import datetime

from services.batch_engine import BatchEngine, BatchTask, BatchStatus
from services.bulk_data_service import BulkDataService
from models import get_db_session, StockMaster
from utils.auth import require_api_key
from utils.rate_limit import rate_limit

# ブループリント作成
batch_engine_bp = Blueprint('batch_engine', __name__, url_prefix='/api/v2/batch')

# ログ設定
logger = logging.getLogger(__name__)

# グローバルバッチエンジンインスタンス
batch_engine: Optional[BatchEngine] = None

def get_batch_engine() -> BatchEngine:
    """バッチエンジンインスタンスを取得"""
    global batch_engine
    if batch_engine is None:
        batch_engine = BatchEngine(max_workers=4, queue_size=1000)
        batch_engine.start_workers()
    return batch_engine

@batch_engine_bp.route('/start', methods=['POST'])
@require_api_key
@rate_limit(requests_per_minute=10)
def start_batch():
    """
    バッチ処理を開始
    
    Request Body:
    {
        "batch_type": "all_stocks",  # "all_stocks", "symbol_list", "custom"
        "symbols": ["7203", "9984"],  # batch_type が "symbol_list" の場合
        "interval": "1d",  # データ取得間隔
        "period": "1y",    # データ取得期間
        "max_workers": 4   # 最大ワーカー数（オプション）
    }
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Request body is required'}), 400
        
        batch_type = data.get('batch_type', 'all_stocks')
        symbols = data.get('symbols', [])
        interval = data.get('interval', '1d')
        period = data.get('period', '1y')
        max_workers = data.get('max_workers', 4)
        
        # バッチタイプに応じて銘柄リストを準備
        if batch_type == 'all_stocks':
            # 全銘柄を取得
            with get_db_session() as session:
                stock_masters = session.query(StockMaster).filter_by(is_active=1).all()
                symbols = [stock.stock_code for stock in stock_masters]
        elif batch_type == 'symbol_list':
            if not symbols:
                return jsonify({'error': 'symbols is required for symbol_list batch_type'}), 400
        else:
            return jsonify({'error': 'Invalid batch_type'}), 400
        
        if not symbols:
            return jsonify({'error': 'No symbols found'}), 400
        
        # バッチエンジンを取得
        engine = get_batch_engine()
        
        # 進捗コールバック関数
        def progress_callback(execution_info):
            logger.info(f"Batch progress: {execution_info.progress_percentage:.1f}% "
                       f"({execution_info.completed_tasks}/{execution_info.total_tasks})")
        
        # バッチ実行を作成
        execution_id = engine.create_execution(
            batch_type=batch_type,
            total_tasks=len(symbols),
            progress_callback=progress_callback
        )
        
        # タスクを作成
        tasks = []
        for symbol in symbols:
            task = BatchTask(
                id=f"{execution_id}_{symbol}",
                symbol=symbol,
                interval=interval,
                period=period,
                execution_id=execution_id
            )
            tasks.append(task)
        
        # バッチ実行を開始
        engine.start_execution(execution_id, tasks)
        
        return jsonify({
            'execution_id': execution_id,
            'batch_type': batch_type,
            'total_tasks': len(symbols),
            'status': 'started',
            'message': f'Batch processing started with {len(symbols)} symbols'
        }), 200
        
    except Exception as e:
        logger.error(f"Failed to start batch: {e}")
        return jsonify({'error': str(e)}), 500

@batch_engine_bp.route('/status/<execution_id>', methods=['GET'])
@require_api_key
def get_batch_status(execution_id: str):
    """
    バッチ処理のステータスを取得
    """
    try:
        engine = get_batch_engine()
        status = engine.get_execution_status(execution_id)
        
        if not status:
            return jsonify({'error': 'Execution not found'}), 404
        
        return jsonify(status), 200
        
    except Exception as e:
        logger.error(f"Failed to get batch status: {e}")
        return jsonify({'error': str(e)}), 500

@batch_engine_bp.route('/pause/<execution_id>', methods=['POST'])
@require_api_key
def pause_batch(execution_id: str):
    """
    バッチ処理を一時停止
    """
    try:
        engine = get_batch_engine()
        engine.pause_execution(execution_id)
        
        return jsonify({
            'execution_id': execution_id,
            'status': 'paused',
            'message': 'Batch execution paused'
        }), 200
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        logger.error(f"Failed to pause batch: {e}")
        return jsonify({'error': str(e)}), 500

@batch_engine_bp.route('/resume/<execution_id>', methods=['POST'])
@require_api_key
def resume_batch(execution_id: str):
    """
    バッチ処理を再開
    """
    try:
        engine = get_batch_engine()
        engine.resume_execution(execution_id)
        
        return jsonify({
            'execution_id': execution_id,
            'status': 'resumed',
            'message': 'Batch execution resumed'
        }), 200
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        logger.error(f"Failed to resume batch: {e}")
        return jsonify({'error': str(e)}), 500

@batch_engine_bp.route('/cancel/<execution_id>', methods=['POST'])
@require_api_key
def cancel_batch(execution_id: str):
    """
    バッチ処理をキャンセル
    """
    try:
        engine = get_batch_engine()
        engine.cancel_execution(execution_id)
        
        return jsonify({
            'execution_id': execution_id,
            'status': 'cancelled',
            'message': 'Batch execution cancelled'
        }), 200
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        logger.error(f"Failed to cancel batch: {e}")
        return jsonify({'error': str(e)}), 500

@batch_engine_bp.route('/workers', methods=['GET'])
@require_api_key
def get_worker_status():
    """
    ワーカーのステータスを取得
    """
    try:
        engine = get_batch_engine()
        status = engine.get_worker_status()
        
        return jsonify(status), 200
        
    except Exception as e:
        logger.error(f"Failed to get worker status: {e}")
        return jsonify({'error': str(e)}), 500

@batch_engine_bp.route('/queue', methods=['GET'])
@require_api_key
def get_queue_status():
    """
    キューのステータスを取得
    """
    try:
        engine = get_batch_engine()
        status = engine.get_queue_status()
        
        return jsonify(status), 200
        
    except Exception as e:
        logger.error(f"Failed to get queue status: {e}")
        return jsonify({'error': str(e)}), 500

@batch_engine_bp.route('/history', methods=['GET'])
@require_api_key
def get_batch_history():
    """
    バッチ実行履歴を取得
    """
    try:
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 20, type=int), 100)
        
        with get_db_session() as session:
            # バッチ実行履歴を取得
            from ..models import BatchExecution
            query = session.query(BatchExecution).order_by(BatchExecution.start_time.desc())
            
            # ページネーション
            offset = (page - 1) * per_page
            executions = query.offset(offset).limit(per_page).all()
            total = query.count()
            
            # レスポンス作成
            history = []
            for execution in executions:
                history.append({
                    'id': execution.id,
                    'batch_type': execution.batch_type,
                    'status': execution.status,
                    'total_stocks': execution.total_stocks,
                    'processed_stocks': execution.processed_stocks,
                    'successful_stocks': execution.successful_stocks,
                    'failed_stocks': execution.failed_stocks,
                    'progress_percentage': execution.progress_percentage,
                    'start_time': execution.start_time.isoformat() if execution.start_time else None,
                    'end_time': execution.end_time.isoformat() if execution.end_time else None,
                    'duration_seconds': execution.duration_seconds,
                    'error_message': execution.error_message
                })
            
            return jsonify({
                'history': history,
                'pagination': {
                    'page': page,
                    'per_page': per_page,
                    'total': total,
                    'pages': (total + per_page - 1) // per_page
                }
            }), 200
            
    except Exception as e:
        logger.error(f"Failed to get batch history: {e}")
        return jsonify({'error': str(e)}), 500

@batch_engine_bp.route('/shutdown', methods=['POST'])
@require_api_key
def shutdown_engine():
    """
    バッチエンジンをシャットダウン（管理者用）
    """
    try:
        global batch_engine
        if batch_engine:
            batch_engine.shutdown()
            batch_engine = None
        
        return jsonify({
            'status': 'shutdown',
            'message': 'Batch engine shutdown completed'
        }), 200
        
    except Exception as e:
        logger.error(f"Failed to shutdown batch engine: {e}")
        return jsonify({'error': str(e)}), 500

# エラーハンドラー
@batch_engine_bp.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found'}), 404

@batch_engine_bp.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500