import os
import time
import threading
from functools import wraps
from typing import Dict, Any, Callable, Optional, List
import logging

from flask import request, jsonify, current_app

from api import bulk_api
from services.bulk_data_service import BulkDataService
from services.batch_service import BatchService, BatchServiceError

logger = logging.getLogger(__name__)

# Phase 1: ジョブ状態のインメモリ管理（後方互換性のため保持）
# Phase 2では、BatchServiceを使用してデータベースに永続化します
JOBS: Dict[str, Dict[str, Any]] = {}

# Phase 2機能フラグ（環境変数で制御可能）
ENABLE_PHASE2 = os.getenv('ENABLE_PHASE2', 'true').lower() == 'true'


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
    """単純なAPIキー認証（ヘッダ: X-API-KEY）

    API_KEY環境変数が設定されていない場合は認証をスキップ（開発環境向け）
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        expected = os.getenv('API_KEY')
        # API_KEYが設定されていない場合は認証不要
        if not expected:
            return func(*args, **kwargs)

        # API_KEYが設定されている場合は認証必須
        provided = request.headers.get('X-API-KEY')
        if provided == expected:
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


def _make_progress_callback(job_id: str, batch_db_id: Optional[int] = None) -> Callable[[Dict[str, Any]], None]:
    """
    進捗更新コールバックを生成

    Args:
        job_id: Phase 1のジョブID
        batch_db_id: Phase 2のバッチDB ID

    Returns:
        進捗更新コールバック関数
    """
    def cb(progress: Dict[str, Any]):
        logger.info(f"[progress_callback] 進捗更新: job_id={job_id}, progress={progress}")
        
        # Phase 1: インメモリ管理の更新
        job = JOBS.get(job_id)
        if job:
            job['progress'] = progress
            job['updated_at'] = time.time()
            logger.debug(f"[progress_callback] Phase 1進捗更新完了: job_id={job_id}")
        else:
            logger.warning(f"[progress_callback] Phase 1ジョブが見つかりません: job_id={job_id}")

        # Phase 2: データベースの更新
        if ENABLE_PHASE2 and batch_db_id:
            try:
                logger.debug(f"[progress_callback] Phase 2進捗更新開始: batch_db_id={batch_db_id}")
                BatchService.update_batch_progress(
                    batch_id=batch_db_id,
                    processed_stocks=progress.get('processed', 0),
                    successful_stocks=progress.get('successful', 0),
                    failed_stocks=progress.get('failed', 0)
                )
                logger.debug(f"[progress_callback] Phase 2進捗更新完了: batch_db_id={batch_db_id}")
            except BatchServiceError as e:
                logger.error(f"[progress_callback] Phase 2バッチ進捗更新エラー: {e}")

        # WebSocket通知（利用可能な場合のみ）
        try:
            from flask import current_app
            # アプリケーションコンテキストが利用可能かチェック
            try:
                socketio = current_app.config.get('SOCKETIO')
                if socketio:
                    logger.debug(f"[progress_callback] WebSocket進捗通知送信: job_id={job_id}")
                    socketio.emit('bulk_progress', {
                        'job_id': job_id,
                        'batch_db_id': batch_db_id,
                        'progress': progress
                    })
                else:
                    logger.debug(f"[progress_callback] WebSocket未設定のため進捗通知スキップ")
            except RuntimeError:
                # アプリケーションコンテキスト外で実行されている場合はスキップ
                logger.debug(f"[progress_callback] アプリケーションコンテキスト外のためWebSocket通知スキップ")
        except Exception as e:
            logger.error(f"[progress_callback] WebSocket進捗通知エラー: {e}")
    return cb


def _run_job(job_id: str, symbols: List[str], interval: str, period: Optional[str], batch_db_id: Optional[int] = None):
    """
    バッチ処理を実行

    Args:
        job_id: Phase 1のジョブID（インメモリ管理用）
        symbols: 銘柄コードのリスト
        interval: 時間軸
        period: 取得期間
        batch_db_id: Phase 2のバッチDB ID（データベース永続化用）
    """
    logger.info(f"[_run_job] ジョブ実行開始: job_id={job_id}, symbols_count={len(symbols)}, interval={interval}, period={period}")
    
    service = get_bulk_service()
    try:
        logger.info(f"[_run_job] BulkDataService.fetch_multiple_stocks 呼び出し開始")
        summary = service.fetch_multiple_stocks(
            symbols=symbols,
            interval=interval,
            period=period,
            progress_callback=_make_progress_callback(job_id, batch_db_id)
        )
        
        logger.info(f"[_run_job] データ取得完了: job_id={job_id}, summary={summary}")

        # Phase 1: インメモリ管理の更新
        job = JOBS.get(job_id)
        if job is not None:
            job['status'] = 'completed'
            job['summary'] = summary
            job['updated_at'] = time.time()
            logger.info(f"[_run_job] Phase 1ジョブ完了更新: job_id={job_id}")

        # Phase 2: データベースの更新
        if ENABLE_PHASE2 and batch_db_id:
            try:
                logger.info(f"[_run_job] Phase 2バッチ完了更新開始: batch_db_id={batch_db_id}")
                BatchService.complete_batch(
                    batch_id=batch_db_id,
                    status='completed'
                )
                logger.info(f"[_run_job] Phase 2バッチ完了更新成功: batch_db_id={batch_db_id}")
            except BatchServiceError as e:
                logger.error(f"[_run_job] Phase 2バッチ完了更新エラー: {e}")

        # 完了通知（WebSocketが有効な場合）
        try:
            from flask import current_app
            # アプリケーションコンテキストが利用可能かチェック
            try:
                socketio = current_app.config.get('SOCKETIO')
                if socketio:
                    logger.info(f"[_run_job] WebSocket完了通知送信: job_id={job_id}")
                    socketio.emit('bulk_complete', {
                        'job_id': job_id,
                        'batch_db_id': batch_db_id,
                        'summary': summary
                    })
                else:
                    logger.info(f"[_run_job] WebSocket未設定のため完了通知スキップ")
            except RuntimeError:
                # アプリケーションコンテキスト外で実行されている場合はスキップ
                logger.info(f"[_run_job] アプリケーションコンテキスト外のためWebSocket完了通知スキップ")
        except Exception as e:
            logger.error(f"[_run_job] WebSocket完了通知エラー: {e}")

    except Exception as e:
        logger.error(f"[_run_job] ジョブ実行エラー: job_id={job_id}, error={e}", exc_info=True)
        
        # Phase 1: インメモリ管理の更新
        job = JOBS.get(job_id)
        if job is not None:
            job['status'] = 'failed'
            job['error'] = str(e)
            job['updated_at'] = time.time()
            logger.info(f"[_run_job] Phase 1ジョブ失敗更新: job_id={job_id}")

        # Phase 2: データベースの更新
        if ENABLE_PHASE2 and batch_db_id:
            try:
                logger.info(f"[_run_job] Phase 2バッチ失敗更新開始: batch_db_id={batch_db_id}")
                BatchService.complete_batch(
                    batch_id=batch_db_id,
                    status='failed',
                    error_message=str(e)
                )
                logger.info(f"[_run_job] Phase 2バッチ失敗更新成功: batch_db_id={batch_db_id}")
            except BatchServiceError as db_err:
                logger.error(f"[_run_job] Phase 2バッチ失敗更新エラー: {db_err}")

    logger.info(f"[_run_job] ジョブ実行終了: job_id={job_id}")


@bulk_api.route('/start', methods=['POST'])
@require_api_key
@rate_limit()
def start_bulk_fetch():
    """
    一括取得のジョブを開始

    Phase 1とPhase 2の両方に対応:
    - Phase 1: インメモリ管理 (job_id)
    - Phase 2: データベース永続化 (batch_db_id)

    下位互換性のため、レスポンスにはjob_idを含めますが、
    Phase 2が有効な場合はbatch_db_idも返します。
    """
    try:
        logger.info("[bulk_data] 一括取得リクエスト受信")
        
        data = request.get_json(silent=True) or {}
        symbols = data.get('symbols')
        interval = data.get('interval', '1d')
        period = data.get('period')

        logger.info(f"[bulk_data] リクエストパラメータ: symbols_count={len(symbols) if symbols else 0}, interval={interval}, period={period}")

        # 入力検証
        if not symbols or not isinstance(symbols, list) or not all(isinstance(s, str) for s in symbols):
            logger.error("[bulk_data] バリデーションエラー: symbols が無効")
            return jsonify({
                "success": False,
                "error": "VALIDATION_ERROR",
                "message": "'symbols' は文字列リストで指定してください"
            }), 400

        # リクエストサイズ制限チェック
        if len(symbols) > 5000:
            logger.error(f"[bulk_data] リクエストサイズエラー: symbols_count={len(symbols)}")
            return jsonify({
                "success": False,
                "error": "REQUEST_TOO_LARGE",
                "message": f"一度に処理できる銘柄数は5000件までです。現在: {len(symbols)}件"
            }), 413

        # Phase 1: インメモリ管理用のジョブID生成
        job_id = f"job-{int(time.time() * 1000)}"
        logger.info(f"[bulk_data] ジョブID生成: {job_id}")
        
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

        # Phase 2: データベースにバッチ実行レコードを作成
        batch_db_id = None
        if ENABLE_PHASE2:
            try:
                logger.info("[bulk_data] Phase 2バッチ作成開始")
                batch_info = BatchService.create_batch(
                    batch_type='partial',
                    total_stocks=len(symbols)
                )
                batch_db_id = batch_info['id']
                logger.info(f"[bulk_data] Phase 2バッチ作成成功: batch_db_id={batch_db_id}")
            except BatchServiceError as e:
                logger.error(f"[bulk_data] Phase 2バッチ作成エラー: {e}")
                # Phase 2失敗時もPhase 1で継続

        # バックグラウンドでジョブ実行
        logger.info(f"[bulk_data] バックグラウンドジョブ開始: job_id={job_id}")
        thread = threading.Thread(
            target=_run_job,
            args=(job_id, symbols, interval, period, batch_db_id),
            daemon=True
        )
        thread.start()

        response_data = {
            "success": True,
            "job_id": job_id,
            "status": "accepted"
        }

        # Phase 2が有効な場合はbatch_db_idも返す
        if batch_db_id:
            response_data["batch_db_id"] = batch_db_id

        logger.info(f"[bulk_data] 一括取得開始成功: job_id={job_id}, batch_db_id={batch_db_id}")
        return jsonify(response_data), 202

    except Exception as e:
        logger.error(f"[bulk_data] 一括取得開始エラー: {e}", exc_info=True)
        return jsonify({
            "success": False,
            "error": "INTERNAL_ERROR",
            "message": f"内部エラーが発生しました: {str(e)}"
        }), 500


@bulk_api.route('/status/<job_id>', methods=['GET'])
@require_api_key
@rate_limit()
def get_job_status(job_id: str):
    """
    ジョブステータスを取得

    Phase 1とPhase 2の両方に対応:
    - job_idが "job-" で始まる場合: Phase 1のインメモリ管理から取得
    - job_idが数値の場合: Phase 2のデータベースから取得

    下位互換性のため、両方をサポートします。
    """
    # Phase 2: job_idが数値の場合はデータベースから取得
    if ENABLE_PHASE2 and job_id.isdigit():
        batch_db_id = int(job_id)
        try:
            batch_info = BatchService.get_batch(batch_db_id)
            if not batch_info:
                return jsonify({
                    "success": False,
                    "error": "NOT_FOUND",
                    "message": "指定されたバッチが見つかりません"
                }), 404

            # Phase 2のレスポンス形式をPhase 1形式に変換
            job = {
                'id': str(batch_info['id']),
                'batch_db_id': batch_info['id'],
                'status': batch_info['status'],
                'progress': {
                    'total': batch_info['total_stocks'],
                    'processed': batch_info['processed_stocks'],
                    'successful': batch_info['successful_stocks'],
                    'failed': batch_info['failed_stocks'],
                    'progress_percentage': batch_info.get('progress_percentage', 0.0)
                },
                'created_at': batch_info['start_time'],
                'updated_at': batch_info['created_at']
            }

            if batch_info.get('end_time'):
                job['summary'] = {
                    'total_symbols': batch_info['total_stocks'],
                    'successful': batch_info['successful_stocks'],
                    'failed': batch_info['failed_stocks'],
                    'duration_seconds': batch_info.get('duration_seconds')
                }

            return jsonify({
                "success": True,
                "job": job
            })

        except BatchServiceError as e:
            logger.error(f"Phase 2バッチ取得エラー: {e}")
            return jsonify({
                "success": False,
                "error": "DATABASE_ERROR",
                "message": f"バッチ情報の取得に失敗しました: {e}"
            }), 500

    # Phase 1: インメモリ管理から取得
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