"""Bulk data API endpoints.

This module provides API endpoints for bulk data fetching operations,
including job management and progress tracking.
"""

from functools import wraps
import logging
import os
import threading
import time
from typing import Any, Callable, Dict, List, Optional

from api import bulk_api
from flask import current_app, jsonify, request

from services.batch_service import BatchService, BatchServiceError
from services.bulk_data_service import BulkDataService


logger = logging.getLogger(__name__)

# Phase 1: ジョブ状態のインメモリ管理（後方互換性のため保持）
# Phase 2では、BatchServiceを使用してデータベースに永続化します
JOBS: Dict[str, Dict[str, Any]] = {}

# Phase 2機能フラグ（環境変数で制御可能）
ENABLE_PHASE2 = os.getenv("ENABLE_PHASE2", "true").lower() == "true"


def get_bulk_service() -> BulkDataService:
    """BulkDataServiceのインスタンスを取得（テストでモック可能）."""
    return BulkDataService()


def _client_key() -> str:
    """レート制限対象キー（APIキーがあればそれを使用、なければIP）."""
    api_key = request.headers.get("X-API-KEY")
    if api_key:
        return f"key:{api_key}"
    return f"ip:{request.remote_addr}"


def require_api_key(func: Callable):
    """API_KEY環境変数が設定されていない場合は認証をスキップ（開発環境向け）."""

    @wraps(func)
    def wrapper(*args, **kwargs):
        expected = os.getenv("API_KEY")
        # API_KEYが設定されていない場合は認証不要
        if not expected:
            return func(*args, **kwargs)

        # API_KEYが設定されている場合は認証必須
        provided = request.headers.get("X-API-KEY")
        if provided == expected:
            return func(*args, **kwargs)

        return (
            jsonify(
                {
                    "success": False,
                    "error": "UNAUTHORIZED",
                    "message": "APIキーが不正です。ヘッダ 'X-API-KEY' を設定してください",
                }
            ),
            401,
        )

    return wrapper


_RATE_BUCKETS: Dict[str, List[float]] = {}
_RATE_WINDOWS: Dict[str, Dict[str, Any]] = {}


def rate_limit(max_per_minute: Optional[int] = None):
    """簡易レート制限（分単位の固定ウィンドウ）."""
    limit_env = os.getenv("RATE_LIMIT_PER_MINUTE", "60")
    default_limit = int(limit_env) if limit_env.isdigit() else 60
    limit = max_per_minute or default_limit

    def decorator(func: Callable):
        @wraps(func)
        def wrapper(*args, **kwargs):
            key = _client_key() + f"|path:{request.path}"
            now = time.time()
            window_id = int(now // 60)  # 現在の分をウィンドウIDとして使用

            win = _RATE_WINDOWS.get(key)
            if not win or win.get("window_id") != window_id:
                # 新しいウィンドウを開始
                _RATE_WINDOWS[key] = {"window_id": window_id, "count": 0}
                win = _RATE_WINDOWS[key]

            if win["count"] >= limit:
                return (
                    jsonify(
                        {
                            "success": False,
                            "error": "RATE_LIMIT_EXCEEDED",
                            "message": "レート制限を超過しました。しばらく待って再試行してください",
                        }
                    ),
                    429,
                )

            win["count"] += 1
            return func(*args, **kwargs)

        return wrapper

    return decorator


def _update_phase1_progress(job_id: str, progress: Dict[str, Any]) -> None:
    """Phase 1の進捗情報を更新.

    Args:
        job_id: ジョブID
        progress: 進捗情報
    """
    job = JOBS.get(job_id)
    if job:
        job["progress"] = progress
        job["updated_at"] = time.time()
        logger.debug(
            f"[progress_callback] Phase 1進捗更新完了: job_id={job_id}"
        )
    else:
        logger.warning(
            f"[progress_callback] Phase 1ジョブが見つかりません: job_id={job_id}"
        )


def _update_phase2_progress(
    batch_db_id: int, progress: Dict[str, Any]
) -> None:
    """Phase 2の進捗情報を更新.

    Args:
        batch_db_id: バッチDB ID
        progress: 進捗情報
    """
    try:
        logger.debug(
            f"[progress_callback] Phase 2進捗更新開始: batch_db_id={batch_db_id}"
        )
        BatchService.update_batch_progress(
            batch_id=batch_db_id,
            processed_stocks=progress.get("processed", 0),
            successful_stocks=progress.get("successful", 0),
            failed_stocks=progress.get("failed", 0),
        )
        logger.debug(
            f"[progress_callback] Phase 2進捗更新完了: batch_db_id={batch_db_id}"
        )
    except BatchServiceError as e:
        logger.error(f"[progress_callback] Phase 2バッチ進捗更新エラー: {e}")


def _send_websocket_progress(
    job_id: str, batch_db_id: Optional[int], progress: Dict[str, Any]
) -> None:
    """WebSocket経由で進捗情報を送信.

    Args:
        job_id: ジョブID
        batch_db_id: バッチDB ID
        progress: 進捗情報
    """
    try:
        from flask import current_app

        try:
            socketio = current_app.config.get("SOCKETIO")
            if socketio:
                logger.debug(
                    f"[progress_callback] WebSocket進捗通知送信: job_id={job_id}"
                )
                socketio.emit(
                    "bulk_progress",
                    {
                        "job_id": job_id,
                        "batch_db_id": batch_db_id,
                        "progress": progress,
                    },
                )
            else:
                logger.debug(
                    "[progress_callback] WebSocket未設定のため進捗通知スキップ"
                )
        except RuntimeError:
            logger.debug(
                "[progress_callback] アプリケーションコンテキスト外のためWebSocket通知スキップ"
            )
    except Exception as e:
        logger.error(f"[progress_callback] WebSocket進捗通知エラー: {e}")


def _make_progress_callback(
    job_id: str, batch_db_id: Optional[int] = None
) -> Callable[[Dict[str, Any]], None]:
    """進捗更新コールバックを生成.

    Args:
        job_id: Phase 1のジョブID
        batch_db_id: Phase 2のバッチDB ID

    Returns:
        進捗更新コールバック関数。
    """

    def cb(progress: Dict[str, Any]):
        logger.info(
            f"[progress_callback] 進捗更新: job_id={job_id}, progress={progress}"
        )

        # Phase 1: インメモリ管理の更新
        _update_phase1_progress(job_id, progress)

        # Phase 2: データベースの更新
        if ENABLE_PHASE2 and batch_db_id:
            _update_phase2_progress(batch_db_id, progress)

        # WebSocket通知
        _send_websocket_progress(job_id, batch_db_id, progress)

    return cb


def _update_job_completion(
    job_id: str, batch_db_id: Optional[int], summary: dict
) -> None:
    """ジョブ完了時の更新処理.

    Args:
        job_id: ジョブID
        batch_db_id: バッチDB ID（Phase 2用）
        summary: 実行サマリー
    """
    # Phase 1: インメモリ管理の更新
    job = JOBS.get(job_id)
    if job is not None:
        job["status"] = "completed"
        job["summary"] = summary
        job["updated_at"] = time.time()
        logger.info(f"[_run_job] Phase 1ジョブ完了更新: job_id={job_id}")

    # Phase 2: データベースの更新
    if ENABLE_PHASE2 and batch_db_id:
        try:
            logger.info(
                f"[_run_job] Phase 2バッチ完了更新開始: batch_db_id={batch_db_id}"
            )
            BatchService.complete_batch(
                batch_id=batch_db_id, status="completed"
            )
            logger.info(
                f"[_run_job] Phase 2バッチ完了更新成功: batch_db_id={batch_db_id}"
            )
        except BatchServiceError as e:
            logger.error(f"[_run_job] Phase 2バッチ完了更新エラー: {e}")


def _update_job_failure(
    job_id: str, batch_db_id: Optional[int], error: Exception
) -> None:
    """ジョブ失敗時の更新処理.

    Args:
        job_id: ジョブID
        batch_db_id: バッチDB ID（Phase 2用）
        error: エラー情報
    """
    # Phase 1: インメモリ管理の更新
    job = JOBS.get(job_id)
    if job is not None:
        job["status"] = "failed"
        job["error"] = str(error)
        job["updated_at"] = time.time()
        logger.info(f"[_run_job] Phase 1ジョブ失敗更新: job_id={job_id}")

    # Phase 2: データベースの更新
    if ENABLE_PHASE2 and batch_db_id:
        try:
            logger.info(
                f"[_run_job] Phase 2バッチ失敗更新開始: batch_db_id={batch_db_id}"
            )
            BatchService.complete_batch(
                batch_id=batch_db_id,
                status="failed",
                error_message=str(error),
            )
            logger.info(
                f"[_run_job] Phase 2バッチ失敗更新成功: batch_db_id={batch_db_id}"
            )
        except BatchServiceError as db_err:
            logger.error(f"[_run_job] Phase 2バッチ失敗更新エラー: {db_err}")


def _send_websocket_completion(
    job_id: str, batch_db_id: Optional[int], summary: dict
) -> None:
    """WebSocket経由で完了通知を送信.

    Args:
        job_id: ジョブID
        batch_db_id: バッチDB ID
        summary: 実行サマリー
    """
    try:
        socketio = current_app.config.get("SOCKETIO")
        if not socketio:
            logger.info("[_run_job] WebSocket未設定のため完了通知スキップ")
            return

        logger.info(f"[_run_job] WebSocket完了通知送信: job_id={job_id}")

        # フロントエンド用にサマリーフォーマットを変換
        frontend_summary = {
            "total_symbols": summary.get("total"),
            "successful": summary.get("successful"),
            "failed": summary.get("failed"),
            "duration_seconds": summary.get("elapsed_time"),
        }

        socketio.emit(
            "bulk_complete",
            {
                "job_id": job_id,
                "batch_db_id": batch_db_id,
                "summary": frontend_summary,
            },
        )
    except Exception as e:
        logger.error(f"[_run_job] WebSocket完了通知エラー: {e}")


def _run_job(
    app,
    job_id: str,
    symbols: List[str],
    interval: str,
    period: Optional[str],
    batch_db_id: Optional[int] = None,
):
    """バッチ処理を実行.

    Args:
        app: Flaskアプリケーションインスタンス
        job_id: Phase 1のジョブID（インメモリ管理用）
        symbols: 銘柄コードのリスト
        interval: 時間軸
        period: 取得期間
        batch_db_id: Phase 2のバッチDB ID（データベース永続化用）。
    """
    with app.app_context():
        logger.info(
            f"[_run_job] ジョブ実行開始: job_id={job_id}, symbols_count={len(symbols)}, interval={interval}, period={period}"
        )

        service = get_bulk_service()
        try:
            logger.info(
                "[_run_job] BulkDataService.fetch_multiple_stocks 呼び出し開始"
            )
            summary = service.fetch_multiple_stocks(
                symbols=symbols,
                interval=interval,
                period=period,
                progress_callback=_make_progress_callback(job_id, batch_db_id),
            )

            logger.info(
                f"[_run_job] データ取得完了: job_id={job_id}, summary={summary}"
            )

            # ジョブ完了の更新処理
            _update_job_completion(job_id, batch_db_id, summary)

            # WebSocket完了通知
            _send_websocket_completion(job_id, batch_db_id, summary)

        except Exception as e:
            logger.error(
                f"[_run_job] ジョブ実行エラー: job_id={job_id}, error={e}",
                exc_info=True,
            )

            # ジョブ失敗の更新処理
            _update_job_failure(job_id, batch_db_id, e)

        logger.info(f"[_run_job] ジョブ実行終了: job_id={job_id}")


@bulk_api.route("/start", methods=["POST"])
@require_api_key
@rate_limit()
def start_bulk_fetch():
    """一括取得のジョブを開始.

    Phase 1とPhase 2の両方に対応:
    - Phase 1: インメモリ管理 (job_id)
    - Phase 2: データベース永続化 (batch_db_id)

    下位互換性のため、レスポンスにはjob_idを含めますが、
    Phase 2が有効な場合はbatch_db_idも返します。
    """
    try:
        logger.info("[bulk_data] 一括取得リクエスト受信")

        data = request.get_json(silent=True) or {}
        symbols = data.get("symbols")
        interval = data.get("interval", "1d")
        period = data.get("period")

        logger.info(
            f"[bulk_data] リクエストパラメータ: symbols_count={len(symbols) if symbols else 0}, interval={interval}, period={period}"
        )

        # 入力検証
        if (
            not symbols
            or not isinstance(symbols, list)
            or not all(isinstance(s, str) for s in symbols)
        ):
            logger.error("[bulk_data] バリデーションエラー: symbols が無効")
            return (
                jsonify(
                    {
                        "success": False,
                        "error": "VALIDATION_ERROR",
                        "message": "'symbols' は文字列リストで指定してください",
                    }
                ),
                400,
            )

        # リクエストサイズ制限チェック
        if len(symbols) > 5000:
            logger.error(
                f"[bulk_data] リクエストサイズエラー: symbols_count={len(symbols)}"
            )
            return (
                jsonify(
                    {
                        "success": False,
                        "error": "REQUEST_TOO_LARGE",
                        "message": f"一度に処理できる銘柄数は5000件までです。現在: {len(symbols)}件",
                    }
                ),
                413,
            )

        # Phase 1: インメモリ管理用のジョブID生成
        job_id = f"job-{int(time.time() * 1000)}"
        logger.info(f"[bulk_data] ジョブID生成: {job_id}")

        JOBS[job_id] = {
            "id": job_id,
            "status": "running",
            "progress": {
                "total": len(symbols),
                "processed": 0,
                "successful": 0,
                "failed": 0,
                "progress_percentage": 0.0,
            },
            "created_at": time.time(),
            "updated_at": time.time(),
        }

        # Phase 2: データベースにバッチ実行レコードを作成
        batch_db_id = None
        if ENABLE_PHASE2:
            try:
                logger.info("[bulk_data] Phase 2バッチ作成開始")
                batch_info = BatchService.create_batch(
                    batch_type="partial", total_stocks=len(symbols)
                )
                batch_db_id = batch_info["id"]
                logger.info(
                    f"[bulk_data] Phase 2バッチ作成成功: batch_db_id={batch_db_id}"
                )
            except BatchServiceError as e:
                logger.error(f"[bulk_data] Phase 2バッチ作成エラー: {e}")
                # Phase 2失敗時もPhase 1で継続

        # バックグラウンドでジョブ実行
        logger.info(f"[bulk_data] バックグラウンドジョブ開始: job_id={job_id}")
        app = current_app._get_current_object()
        thread = threading.Thread(
            target=_run_job,
            args=(app, job_id, symbols, interval, period, batch_db_id),
            daemon=True,
        )
        thread.start()

        response_data = {
            "success": True,
            "job_id": job_id,
            "status": "accepted",
        }

        # Phase 2が有効な場合はbatch_db_idも返す
        if batch_db_id:
            response_data["batch_db_id"] = batch_db_id

        logger.info(
            f"[bulk_data] 一括取得開始成功: job_id={job_id}, batch_db_id={batch_db_id}"
        )
        return jsonify(response_data), 202

    except Exception as e:
        logger.error(f"[bulk_data] 一括取得開始エラー: {e}", exc_info=True)
        return (
            jsonify(
                {
                    "success": False,
                    "error": "INTERNAL_ERROR",
                    "message": f"内部エラーが発生しました: {str(e)}",
                }
            ),
            500,
        )


@bulk_api.route("/status/<job_id>", methods=["GET"])
@require_api_key
@rate_limit()
def get_job_status(job_id: str):
    """ジョブステータスを取得.

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
                return (
                    jsonify(
                        {
                            "success": False,
                            "error": "NOT_FOUND",
                            "message": "指定されたバッチが見つかりません",
                        }
                    ),
                    404,
                )

            # Phase 2のレスポンス形式をPhase 1形式に変換
            job = {
                "id": str(batch_info["id"]),
                "batch_db_id": batch_info["id"],
                "status": batch_info["status"],
                "progress": {
                    "total": batch_info["total_stocks"],
                    "processed": batch_info["processed_stocks"],
                    "successful": batch_info["successful_stocks"],
                    "failed": batch_info["failed_stocks"],
                    "progress_percentage": batch_info.get(
                        "progress_percentage", 0.0
                    ),
                },
                "created_at": batch_info["start_time"],
                "updated_at": batch_info["created_at"],
            }

            if batch_info.get("end_time"):
                job["summary"] = {
                    "total_symbols": batch_info["total_stocks"],
                    "successful": batch_info["successful_stocks"],
                    "failed": batch_info["failed_stocks"],
                    "duration_seconds": batch_info.get("duration_seconds"),
                }

            return jsonify({"success": True, "job": job})

        except BatchServiceError as e:
            logger.error(f"Phase 2バッチ取得エラー: {e}")
            return (
                jsonify(
                    {
                        "success": False,
                        "error": "DATABASE_ERROR",
                        "message": f"バッチ情報の取得に失敗しました: {e}",
                    }
                ),
                500,
            )

    # Phase 1: インメモリ管理から取得
    job = JOBS.get(job_id)
    if not job:
        return (
            jsonify(
                {
                    "success": False,
                    "error": "NOT_FOUND",
                    "message": "指定されたジョブが見つかりません",
                }
            ),
            404,
        )

    # フロントエンド用にサマリーフォーマットを変換
    response_job = dict(job)
    if "summary" in response_job and response_job["summary"]:
        summary = response_job["summary"]
        response_job["summary"] = {
            "total_symbols": summary.get("total"),
            "successful": summary.get("successful"),
            "failed": summary.get("failed"),
            "duration_seconds": summary.get("elapsed_time"),
        }

    return jsonify({"success": True, "job": response_job})


@bulk_api.route("/stop/<job_id>", methods=["POST"])
@require_api_key
@rate_limit()
def stop_job(job_id: str):
    """Stop a running job by job ID.

    Args:
        job_id: The ID of the job to stop.

    Returns:
        JSON response with success status.
    """
    job = JOBS.get(job_id)
    if not job:
        return (
            jsonify(
                {
                    "success": False,
                    "error": "NOT_FOUND",
                    "message": "指定されたジョブが見つかりません",
                }
            ),
            404,
        )
    job["status"] = "cancel_requested"
    job["updated_at"] = time.time()
    return jsonify(
        {"success": True, "message": "キャンセルを受け付けました", "job": job}
    )


# ========================================
# JPX全銘柄順次取得API (8種類の時間軸を順次実行)
# ========================================

# 8種類の時間軸定義
JPX_SEQUENTIAL_INTERVALS = [
    {"interval": "1m", "period": "5d", "name": "1分足、5日間"},
    {"interval": "5m", "period": "1mo", "name": "5分足、1ヶ月"},
    {"interval": "15m", "period": "1mo", "name": "15分足、1ヶ月"},
    {"interval": "30m", "period": "1mo", "name": "30分足、1ヶ月"},
    {"interval": "1h", "period": "2y", "name": "1時間足、2年"},
    {"interval": "1d", "period": "max", "name": "1日足、最大期間"},
    {"interval": "1wk", "period": "max", "name": "週足、最大期間"},
    {"interval": "1mo", "period": "max", "name": "月足、最大期間"},
]


@bulk_api.route("/jpx-sequential/get-symbols", methods=["GET"])
@require_api_key
@rate_limit()
def get_jpx_symbols():
    """JPX銘柄マスタから銘柄コード一覧を取得.

    Query Parameters:
        - limit: 取得件数上限（デフォルト: 5000、最大: 5000）
        - market_category: 市場区分でフィルタ（オプション）

    Returns:
        銘柄コード一覧。
    """
    try:
        logger.info("[jpx-sequential] JPX銘柄一覧取得リクエスト受信")

        # クエリパラメータを取得
        limit = request.args.get("limit", "5000")
        market_category = request.args.get("market_category")

        # パラメータ検証
        try:
            limit = int(limit)
        except ValueError:
            return (
                jsonify(
                    {
                        "success": False,
                        "error": "VALIDATION_ERROR",
                        "message": "limitは数値である必要があります",
                    }
                ),
                400,
            )

        if limit < 1 or limit > 5000:
            return (
                jsonify(
                    {
                        "success": False,
                        "error": "VALIDATION_ERROR",
                        "message": "limitは1から5000の間である必要があります",
                    }
                ),
                400,
            )

        logger.info(
            f"[jpx-sequential] パラメータ: limit={limit}, market_category={market_category}"
        )

        # JPX銘柄サービスを使用して銘柄一覧を取得
        from services.jpx_stock_service import JPXStockService

        service = JPXStockService()
        result = service.get_stock_list(
            is_active=True,
            market_category=market_category,
            limit=limit,
            offset=0,
        )

        # 銘柄コードリストを作成（Yahoo Finance形式: コード.T）
        symbols = [f"{stock['stock_code']}.T" for stock in result["stocks"]]

        logger.info(
            f"[jpx-sequential] JPX銘柄一覧取得成功: {len(symbols)}銘柄"
        )

        return (
            jsonify(
                {
                    "success": True,
                    "symbols": symbols,
                    "total": len(symbols),
                    "market_category": market_category,
                }
            ),
            200,
        )

    except Exception as e:
        logger.error(f"[jpx-sequential] エラー: {e}", exc_info=True)
        return (
            jsonify(
                {
                    "success": False,
                    "error": "INTERNAL_ERROR",
                    "message": f"内部エラーが発生しました: {str(e)}",
                }
            ),
            500,
        )


def _process_single_interval(
    service, symbols: List[str], interval_config: dict
) -> dict:
    """単一時間軸のバッチ処理を実行.

    Args:
        service: BulkDataServiceインスタンス
        symbols: 銘柄コードのリスト
        interval_config: 時間軸設定

    Returns:
        処理結果の辞書
    """
    interval = interval_config["interval"]
    period = interval_config["period"]
    name = interval_config["name"]

    try:
        start_time = time.time()
        summary = service.fetch_multiple_stocks(
            symbols=symbols,
            interval=interval,
            period=period,
            progress_callback=None,
        )
        duration = time.time() - start_time

        result = {
            "interval": interval,
            "period": period,
            "name": name,
            "success": True,
            "summary": {
                "total_symbols": len(symbols),
                "successful": summary.get("successful", 0),
                "failed": summary.get("failed", 0),
                "total_downloaded": summary.get("total_downloaded", 0),
                "total_saved": summary.get("total_saved", 0),
                "duration_seconds": round(duration, 2),
            },
        }

        logger.info(
            f"[jpx-sequential] 時間軸処理完了: {name} - 成功: {result['summary']['successful']}"
        )
        return result

    except Exception as e:
        logger.error(f"[jpx-sequential] 時間軸処理エラー: {name} - {e}")
        return {
            "interval": interval,
            "period": period,
            "name": name,
            "success": False,
            "error": str(e),
        }


def _send_jpx_interval_notification(
    job_id: str,
    batch_db_id: Optional[int],
    interval_index: int,
    interval_result: dict,
) -> None:
    """JPX時間軸完了のWebSocket通知を送信.

    Args:
        job_id: ジョブID
        batch_db_id: バッチDB ID
        interval_index: 時間軸インデックス
        interval_result: 時間軸処理結果
    """
    try:
        socketio = current_app.config.get("SOCKETIO")
        if socketio:
            socketio.emit(
                "jpx_interval_complete",
                {
                    "job_id": job_id,
                    "batch_db_id": batch_db_id,
                    "interval_index": interval_index,
                    "total_intervals": len(JPX_SEQUENTIAL_INTERVALS),
                    "interval_result": interval_result,
                },
            )
    except Exception as e:
        logger.error(f"[jpx-sequential] WebSocket通知エラー: {e}")


def _send_jpx_complete_notification(
    job_id: str, batch_db_id: Optional[int], summary: dict
) -> None:
    """JPX全体完了のWebSocket通知を送信.

    Args:
        job_id: ジョブID
        batch_db_id: バッチDB ID
        summary: 実行サマリー
    """
    try:
        socketio = current_app.config.get("SOCKETIO")
        if socketio:
            socketio.emit(
                "jpx_complete",
                {
                    "job_id": job_id,
                    "batch_db_id": batch_db_id,
                    "summary": summary,
                },
            )
    except Exception as e:
        logger.error(f"[jpx-sequential] WebSocket完了通知エラー: {e}")


def _run_jpx_sequential_job(
    app, job_id: str, symbols: List[str], batch_db_id: Optional[int] = None
):
    """JPX全銘柄順次取得ジョブを実行.

    Args:
        app: Flaskアプリケーションインスタンス
        job_id: ジョブID
        symbols: 銘柄コードのリスト
        batch_db_id: バッチDB ID（オプション）。
    """
    with app.app_context():
        logger.info(
            f"[jpx-sequential] ジョブ実行開始: job_id={job_id}, symbols_count={len(symbols)}"
        )

        service = get_bulk_service()
        job = JOBS.get(job_id)

        if not job:
            logger.error(
                f"[jpx-sequential] ジョブが見つかりません: job_id={job_id}"
            )
            return

        try:
            interval_results = []

            # 8種類の時間軸を順次実行
            for idx, interval_config in enumerate(JPX_SEQUENTIAL_INTERVALS):
                name = interval_config["name"]
                logger.info(
                    f"[jpx-sequential] 時間軸処理開始: {idx + 1}/8 - {name}"
                )

                # ジョブステータスを更新
                job["current_interval"] = name
                job["current_interval_index"] = idx + 1
                job["updated_at"] = time.time()

                # 単一時間軸の処理を実行
                interval_result = _process_single_interval(
                    service, symbols, interval_config
                )

                # 結果を記録
                interval_results.append(interval_result)
                job["interval_results"] = interval_results
                job["completed_intervals"] = len(interval_results)
                job["updated_at"] = time.time()

                # WebSocket通知（各時間軸完了時）
                _send_jpx_interval_notification(
                    job_id, batch_db_id, idx + 1, interval_result
                )

            # 全時間軸完了サマリーを作成
            successful_intervals = sum(
                1 for r in interval_results if r.get("success")
            )
            failed_intervals = len(interval_results) - successful_intervals

            summary = {
                "total_intervals": len(JPX_SEQUENTIAL_INTERVALS),
                "completed_intervals": len(interval_results),
                "successful_intervals": successful_intervals,
                "failed_intervals": failed_intervals,
                "interval_results": interval_results,
            }

            # ジョブ完了を記録
            job["status"] = "completed"
            job["summary"] = summary
            job["updated_at"] = time.time()

            logger.info(
                f"[jpx-sequential] ジョブ完了: job_id={job_id}, 成功: {successful_intervals}/8"
            )

            # WebSocket通知（全体完了時）
            _send_jpx_complete_notification(job_id, batch_db_id, summary)

        except Exception as e:
            logger.error(
                f"[jpx-sequential] ジョブ実行エラー: job_id={job_id}, error={e}",
                exc_info=True,
            )
            job["status"] = "failed"
            job["error"] = str(e)
            job["updated_at"] = time.time()


@bulk_api.route("/jpx-sequential/start", methods=["POST"])
@require_api_key
@rate_limit()
def start_jpx_sequential():
    """JPX全銘柄順次取得を開始.

    Request Body:
        {
            "symbols": ["7203.T", "6758.T", ...]
        }

    Returns:
        ジョブ情報。
    """
    try:
        logger.info("[jpx-sequential] 順次取得リクエスト受信")

        data = request.get_json(silent=True) or {}
        symbols = data.get("symbols")

        # 入力検証
        if (
            not symbols
            or not isinstance(symbols, list)
            or not all(isinstance(s, str) for s in symbols)
        ):
            logger.error(
                "[jpx-sequential] バリデーションエラー: symbols が無効"
            )
            return (
                jsonify(
                    {
                        "success": False,
                        "error": "VALIDATION_ERROR",
                        "message": "'symbols' は文字列リストで指定してください",
                    }
                ),
                400,
            )

        # リクエストサイズ制限チェック
        if len(symbols) > 5000:
            logger.error(
                f"[jpx-sequential] リクエストサイズエラー: symbols_count={len(symbols)}"
            )
            return (
                jsonify(
                    {
                        "success": False,
                        "error": "REQUEST_TOO_LARGE",
                        "message": f"一度に処理できる銘柄数は5000件までです。現在: {len(symbols)}件",
                    }
                ),
                413,
            )

        # ジョブID生成
        job_id = f"jpx-seq-{int(time.time() * 1000)}"
        logger.info(f"[jpx-sequential] ジョブID生成: {job_id}")

        # ジョブを作成
        JOBS[job_id] = {
            "id": job_id,
            "type": "jpx_sequential",
            "status": "running",
            "total_symbols": len(symbols),
            "total_intervals": len(JPX_SEQUENTIAL_INTERVALS),
            "completed_intervals": 0,
            "current_interval": None,
            "current_interval_index": 0,
            "interval_results": [],
            "created_at": time.time(),
            "updated_at": time.time(),
        }

        # Phase 2: データベースにバッチ実行レコードを作成（オプション）
        batch_db_id = None
        if ENABLE_PHASE2:
            try:
                logger.info("[jpx-sequential] Phase 2バッチ作成開始")
                batch_info = BatchService.create_batch(
                    batch_type="jpx_sequential", total_stocks=len(symbols)
                )
                batch_db_id = batch_info["id"]
                logger.info(
                    f"[jpx-sequential] Phase 2バッチ作成成功: batch_db_id={batch_db_id}"
                )
            except Exception as e:
                logger.error(f"[jpx-sequential] Phase 2バッチ作成エラー: {e}")

        # バックグラウンドでジョブ実行
        logger.info(
            f"[jpx-sequential] バックグラウンドジョブ開始: job_id={job_id}"
        )
        app = current_app._get_current_object()
        thread = threading.Thread(
            target=_run_jpx_sequential_job,
            args=(app, job_id, symbols, batch_db_id),
            daemon=True,
        )
        thread.start()

        response_data = {
            "success": True,
            "job_id": job_id,
            "batch_db_id": batch_db_id,
            "status": "accepted",
            "total_symbols": len(symbols),
            "intervals": JPX_SEQUENTIAL_INTERVALS,
        }

        logger.info(f"[jpx-sequential] 順次取得開始成功: job_id={job_id}")
        return jsonify(response_data), 202

    except Exception as e:
        logger.error(
            f"[jpx-sequential] 順次取得開始エラー: {e}", exc_info=True
        )
        return (
            jsonify(
                {
                    "success": False,
                    "error": "INTERNAL_ERROR",
                    "message": f"内部エラーが発生しました: {str(e)}",
                }
            ),
            500,
        )
