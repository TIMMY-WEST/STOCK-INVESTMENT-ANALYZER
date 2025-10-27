"""システム監視API.

データベース接続テスト、Yahoo Finance API接続テスト、統合ヘルスチェック機能を提供。
"""

from datetime import datetime
import logging
import time

from flask import Blueprint, request

from app.models import get_db_session
from app.services.stock_data.fetcher import StockDataFetcher
from app.utils.api_response import APIResponse, ErrorCode


# Blueprintの作成
system_api = Blueprint("system_api", __name__, url_prefix="/api/system")

logger = logging.getLogger(__name__)


@system_api.route("/database/connection", methods=["GET"])
def test_database_connection():
    """データベース接続テスト.

    Returns:
        JSONレスポンス: データベース接続の状態と詳細情報。
    """
    start_time = time.time()

    try:
        from sqlalchemy import text

        # データベースセッションを取得（コンテキストマネージャーとして使用）
        with get_db_session() as session:
            # 接続テスト用のクエリを実行
            session.execute(text("SELECT 1"))

            # データベース情報を取得
            db_result = session.execute(
                text("SELECT current_database()")
            ).scalar()

            # アクティブ接続数を取得
            connection_count_result = session.execute(
                text(
                    "SELECT count(*) FROM pg_stat_activity WHERE datname = current_database()"
                )
            ).scalar()

            # テーブル存在確認
            table_exists_result = session.execute(
                text(
                    "SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'stocks_1d')"
                )
            ).scalar()

            response_time = (time.time() - start_time) * 1000  # ミリ秒

            return APIResponse.success(
                data={
                    "database": db_result,
                    "table_exists": table_exists_result,
                    "connection_count": connection_count_result,
                },
                message="データベース接続正常",
                meta={
                    "response_time_ms": round(response_time, 2),
                    "timestamp": datetime.utcnow().isoformat() + "Z",
                },
                status_code=200,
            )

    except Exception as e:
        logger.error(f"データベース接続テストエラー: {e}", exc_info=True)
        response_time = (time.time() - start_time) * 1000

        return APIResponse.error(
            error_code=ErrorCode.DATABASE_ERROR,
            message=f"データベース接続エラー: {str(e)}",
            details={
                "response_time_ms": round(response_time, 2),
                "timestamp": datetime.utcnow().isoformat() + "Z",
            },
            status_code=500,
        )


@system_api.route("/external-api/connection", methods=["GET"])
def test_api_connection():
    """Yahoo Finance API接続テスト.

    Request Body:
        symbol (str): テスト用の銘柄コード（デフォルト: 7203.T）

    Returns:
        JSONレスポンス: API接続の状態と詳細情報。
    """
    start_time = time.time()

    try:
        data = request.get_json(silent=True) or {}
        symbol = data.get("symbol", "7203.T")

        # Yahoo Finance APIから少量のデータを取得してテスト
        fetcher = StockDataFetcher()
        stock_data = fetcher.fetch_stock_data(
            symbol=symbol, period="5d", interval="1d"
        )

        response_time = (time.time() - start_time) * 1000  # ミリ秒

        # stock_dataはリストまたはDataFrame。データの有無を適切にチェック
        has_data = stock_data is not None and len(stock_data) > 0

        if has_data:
            # データポイント数を取得
            data_points = len(stock_data)

            return APIResponse.success(
                data={
                    "symbol": symbol,
                    "data_available": True,
                    "data_points": data_points,
                },
                message="Yahoo Finance API接続正常",
                meta={
                    "response_time_ms": round(response_time, 2),
                    "timestamp": datetime.utcnow().isoformat() + "Z",
                },
                status_code=200,
            )
        else:
            return APIResponse.error(
                error_code=ErrorCode.DATA_NOT_FOUND,
                message=f"銘柄データを取得できませんでした: {symbol}",
                details={
                    "symbol": symbol,
                    "response_time_ms": round(response_time, 2),
                    "timestamp": datetime.utcnow().isoformat() + "Z",
                },
                status_code=404,
            )

    except Exception as e:
        logger.error(f"API接続テストエラー: {e}", exc_info=True)
        response_time = (time.time() - start_time) * 1000

        return APIResponse.error(
            error_code=ErrorCode.EXTERNAL_API_ERROR,
            message=f"Yahoo Finance API接続エラー: {str(e)}",
            details={
                "response_time_ms": round(response_time, 2),
                "timestamp": datetime.utcnow().isoformat() + "Z",
            },
            status_code=500,
        )


@system_api.route("/health", methods=["GET"])
def health_check():
    """統合ヘルスチェック.

    データベースとYahoo Finance APIの両方の状態をチェック

    Returns:
        JSONレスポンス: システム全体の健全性状態。
    """
    try:
        # データベース接続テスト
        db_status = "healthy"
        db_message = "接続正常"
        try:
            from sqlalchemy import text

            with get_db_session() as session:
                session.execute(text("SELECT 1"))
        except Exception as e:
            db_status = "error"
            db_message = f"接続エラー: {str(e)}"
            logger.error(f"ヘルスチェック - DB接続エラー: {e}")

        # Yahoo Finance API接続テスト
        api_status = "healthy"
        api_message = "API接続正常"
        try:
            fetcher = StockDataFetcher()
            stock_data = fetcher.fetch_stock_data(
                symbol="7203.T", period="1d", interval="1d"
            )

            # stock_dataの有無を適切にチェック
            has_data = stock_data is not None and len(stock_data) > 0
            if not has_data:
                api_status = "warning"
                api_message = "データ取得できず"
        except Exception as e:
            api_status = "error"
            api_message = f"接続エラー: {str(e)}"
            logger.error(f"ヘルスチェック - API接続エラー: {e}")

        # 総合ステータスを判定
        if db_status == "error" or api_status == "error":
            overall_status = "error"
        elif db_status == "warning" or api_status == "warning":
            overall_status = "degraded"
        else:
            overall_status = "healthy"

        return APIResponse.success(
            data={
                "overall_status": overall_status,
                "services": {
                    "database": {
                        "status": db_status,
                        "message": db_message,
                    },
                    "yahoo_finance_api": {
                        "status": api_status,
                        "message": api_message,
                    },
                },
            },
            meta={
                "timestamp": datetime.utcnow().isoformat() + "Z",
            },
            status_code=200,
        )

    except Exception as e:
        logger.error(f"ヘルスチェックエラー: {e}", exc_info=True)

        return APIResponse.error(
            error_code=ErrorCode.INTERNAL_SERVER_ERROR,
            message="ヘルスチェック実行中にエラーが発生しました",
            details={
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat() + "Z",
            },
            status_code=500,
        )
