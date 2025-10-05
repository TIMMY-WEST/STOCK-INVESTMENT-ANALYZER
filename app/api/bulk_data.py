import os
import time
import threading
from functools import wraps
from typing import Dict, Any, Callable, Optional, List

from flask import request, jsonify, current_app

from api import bulk_api
from services.bulk_data_service import BulkDataService


# ジョブ状態のインメモリ管理（簡易実装）
JOBS: Dict[str, Dict[str, Any]] = {}


def get_bulk_service() -> BulkDataService:
    """BulkDataServiceのインスタンスを取得（テストでモック可能）"""
    return BulkDataService()


def _client_key() -> str:
    """レート制限対象キー（APIキーがあればそれを使用、なければIP）"""
    api_key = request.headers.get('X-API-KEY')
    if api_key:
        return f"key:{api_key}"
    return f"ip:{request.remote_addr}"


def require_api_key(func: Callable):
    """単純なAPIキー認証（ヘッダ: X-API-KEY）"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        expected = os.getenv('API_KEY')
        provided = request.headers.get('X-API-KEY')
        if expected and provided == expected:
            return func(*args, **kwargs)
        return jsonify({
            "success": False,
            "error": "UNAUTHORIZED",
            "message": "APIキーが不正です。ヘッダ 'X-API-KEY' を設定してください"
        }), 401
    return wrapper


_RATE_BUCKETS: Dict[str, List[float]] = {}
_RATE_WINDOWS: Dict[str, Dict[str, Any]] = {}


def rate_limit(max_per_minute: Optional[int] = None):
    """簡易レート制限（分単位の固定ウィンドウ）"""
    limit_env = os.getenv('RATE_LIMIT_PER_MINUTE', '60')
    default_limit = int(limit_env) if limit_env.isdigit() else 60
    limit = max_per_minute or default_limit

    def decorator(func: Callable):
        @wraps(func)
        def wrapper(*args, **kwargs):
            key = _client_key() + f"|path:{request.path}"
            now = time.time()
            window_id = int(now // 60)  # 現在の分をウィンドウIDとして使用

            win = _RATE_WINDOWS.get(key)
            if not win or win.get('window_id') != window_id:
                # 新しいウィンドウを開始
                _RATE_WINDOWS[key] = {'window_id': window_id, 'count': 0}
                win = _RATE_WINDOWS[key]

            if win['count'] >= limit:
                return jsonify({
                    "success": False,
                    "error": "RATE_LIMIT_EXCEEDED",
                    "message": "レート制限を超過しました。しばらく待って再試行してください"
                }), 429

            win['count'] += 1
            return func(*args, **kwargs)
        return wrapper
    return decorator


def _make_progress_callback(job_id: str) -> Callable[[Dict[str, Any]], None]:
    def cb(progress: Dict[str, Any]):
        job = JOBS.get(job_id)
        if not job:
            return
        job['progress'] = progress
        job['updated_at'] = time.time()

        # WebSocket通知（利用可能な場合のみ）
        try:
            socketio = current_app.config.get('SOCKETIO')
            if socketio:
                socketio.emit('bulk_progress', {
                    'job_id': job_id,
                    'progress': progress
                })
        except Exception:
            pass
    return cb


def _run_job(job_id: str, symbols: List[str], interval: str, period: Optional[str]):
    service = get_bulk_service()
    try:
        summary = service.fetch_multiple_stocks(
            symbols=symbols,
            interval=interval,
            period=period,
            progress_callback=_make_progress_callback(job_id)
        )
        job = JOBS.get(job_id)
        if job is not None:
            job['status'] = 'completed'
            job['summary'] = summary
            job['updated_at'] = time.time()

            # 完了通知（WebSocketが有効な場合）
            try:
                socketio = current_app.config.get('SOCKETIO')
                if socketio:
                    socketio.emit('bulk_complete', {
                        'job_id': job_id,
                        'summary': summary
                    })
            except Exception:
                pass
    except Exception as e:
        job = JOBS.get(job_id)
        if job is not None:
            job['status'] = 'failed'
            job['error'] = str(e)
            job['updated_at'] = time.time()


@bulk_api.route('/start', methods=['POST'])
@require_api_key
@rate_limit()
def start_bulk_fetch():
    """一括取得のジョブを開始"""
    data = request.get_json(silent=True) or {}
    symbols = data.get('symbols')
    interval = data.get('interval', '1d')
    period = data.get('period')

    # 入力検証
    if not symbols or not isinstance(symbols, list) or not all(isinstance(s, str) for s in symbols):
        return jsonify({
            "success": False,
            "error": "VALIDATION_ERROR",
            "message": "'symbols' は文字列リストで指定してください"
        }), 400

    job_id = f"job-{int(time.time() * 1000)}"
    JOBS[job_id] = {
        'id': job_id,
        'status': 'running',
        'progress': {
            'total': len(symbols),
            'processed': 0,
            'successful': 0,
            'failed': 0,
            'progress_percentage': 0.0
        },
        'created_at': time.time(),
        'updated_at': time.time()
    }

    thread = threading.Thread(target=_run_job, args=(job_id, symbols, interval, period), daemon=True)
    thread.start()

    return jsonify({
        "success": True,
        "job_id": job_id,
        "status": "accepted"
    }), 202


@bulk_api.route('/status/<job_id>', methods=['GET'])
@require_api_key
@rate_limit()
def get_job_status(job_id: str):
    job = JOBS.get(job_id)
    if not job:
        return jsonify({
            "success": False,
            "error": "NOT_FOUND",
            "message": "指定されたジョブが見つかりません"
        }), 404
    return jsonify({
        "success": True,
        "job": job
    })


@bulk_api.route('/stop/<job_id>', methods=['POST'])
@require_api_key
@rate_limit()
def stop_job(job_id: str):
    job = JOBS.get(job_id)
    if not job:
        return jsonify({
            "success": False,
            "error": "NOT_FOUND",
            "message": "指定されたジョブが見つかりません"
        }), 404
    job['status'] = 'cancel_requested'
    job['updated_at'] = time.time()
    return jsonify({
        "success": True,
        "message": "キャンセルを受け付けました",
        "job": job
    })