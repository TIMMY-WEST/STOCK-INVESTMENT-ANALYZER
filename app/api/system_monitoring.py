"""
システム監視API

データベース接続テスト、Yahoo Finance API接続テスト、統合ヘルスチェック機能を提供
"""

from flask import Blueprint, jsonify, request
from datetime import datetime
import time
import logging

# Blueprintの作成
system_api = Blueprint('system_api', __name__, url_prefix='/api/system')

logger = logging.getLogger(__name__)


@system_api.route('/db-connection-test', methods=['POST'])
def test_database_connection():
    """
    データベース接続テスト

    Returns:
        JSONレスポンス: データベース接続の状態と詳細情報
    """
    start_time = time.time()

    try:
        from models import get_db_session, Stocks1d
        from sqlalchemy import text

        # データベースセッションを取得
        session = get_db_session()

        try:
            # 接続テスト用のクエリを実行
            session.execute(text("SELECT 1"))

            # データベース情報を取得
            db_result = session.execute(text("SELECT current_database()")).scalar()

            # アクティブ接続数を取得
            connection_count_result = session.execute(
                text("SELECT count(*) FROM pg_stat_activity WHERE datname = current_database()")
            ).scalar()

            # テーブル存在確認
            table_exists_result = session.execute(
                text("SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'stocks_1d')")
            ).scalar()

            response_time = (time.time() - start_time) * 1000  # ミリ秒

            return jsonify({
                "success": True,
                "message": "データベース接続正常",
                "responseTime": round(response_time, 2),
                "details": {
                    "host": "localhost",  # 実際の設定から取得可能
                    "database": db_result,
                    "tableExists": table_exists_result,
                    "connectionCount": connection_count_result
                },
                "timestamp": datetime.utcnow().isoformat() + 'Z'
            }), 200

        finally:
            session.close()

    except Exception as e:
        logger.error(f"データベース接続テストエラー: {e}", exc_info=True)
        response_time = (time.time() - start_time) * 1000

        return jsonify({
            "success": False,
            "message": f"データベース接続エラー: {str(e)}",
            "responseTime": round(response_time, 2),
            "details": {},
            "timestamp": datetime.utcnow().isoformat() + 'Z'
        }), 500


@system_api.route('/api-connection-test', methods=['POST'])
def test_api_connection():
    """
    Yahoo Finance API接続テスト

    Request Body:
        symbol (str): テスト用の銘柄コード（デフォルト: 7203.T）

    Returns:
        JSONレスポンス: API接続の状態と詳細情報
    """
    start_time = time.time()

    try:
        data = request.get_json(silent=True) or {}
        symbol = data.get('symbol', '7203.T')

        from services.stock_data_fetcher import StockDataFetcher

        # Yahoo Finance APIから少量のデータを取得してテスト
        fetcher = StockDataFetcher()
        stock_data = fetcher.fetch_stock_data(
            symbol=symbol,
            period='5d',
            interval='1d'
        )

        response_time = (time.time() - start_time) * 1000  # ミリ秒

        if stock_data and len(stock_data) > 0:
            # データポイント数とメタ情報を取得
            data_points = len(stock_data)
            last_data = stock_data[-1] if stock_data else {}
            last_update = last_data.get('date', 'N/A')

            # 銘柄名を取得（可能であれば）
            company_name = "N/A"
            try:
                import yfinance as yf
                ticker = yf.Ticker(symbol)
                info = ticker.info
                company_name = info.get('longName', info.get('shortName', 'N/A'))
            except Exception:
                pass

            return jsonify({
                "success": True,
                "message": "Yahoo Finance API接続正常",
                "responseTime": round(response_time, 2),
                "details": {
                    "symbol": symbol,
                    "dataPoints": data_points,
                    "lastUpdate": str(last_update),
                    "companyName": company_name
                },
                "timestamp": datetime.utcnow().isoformat() + 'Z'
            }), 200
        else:
            return jsonify({
                "success": False,
                "message": f"銘柄データを取得できませんでした: {symbol}",
                "responseTime": round(response_time, 2),
                "details": {
                    "symbol": symbol
                },
                "timestamp": datetime.utcnow().isoformat() + 'Z'
            }), 404

    except Exception as e:
        logger.error(f"API接続テストエラー: {e}", exc_info=True)
        response_time = (time.time() - start_time) * 1000

        return jsonify({
            "success": False,
            "message": f"Yahoo Finance API接続エラー: {str(e)}",
            "responseTime": round(response_time, 2),
            "details": {},
            "timestamp": datetime.utcnow().isoformat() + 'Z'
        }), 500


@system_api.route('/health-check', methods=['GET'])
def health_check():
    """
    統合ヘルスチェック

    データベースとYahoo Finance APIの両方の状態をチェック

    Returns:
        JSONレスポンス: システム全体の健全性状態
    """
    try:
        # データベース接続テスト
        db_status = "healthy"
        db_message = "接続正常"
        try:
            from models import get_db_session
            from sqlalchemy import text

            session = get_db_session()
            try:
                session.execute(text("SELECT 1"))
            finally:
                session.close()
        except Exception as e:
            db_status = "error"
            db_message = f"接続エラー: {str(e)}"
            logger.error(f"ヘルスチェック - DB接続エラー: {e}")

        # Yahoo Finance API接続テスト
        api_status = "healthy"
        api_message = "API接続正常"
        try:
            from services.stock_data_fetcher import StockDataFetcher

            fetcher = StockDataFetcher()
            stock_data = fetcher.fetch_stock_data(
                symbol='7203.T',
                period='1d',
                interval='1d'
            )

            if not stock_data or len(stock_data) == 0:
                api_status = "warning"
                api_message = "データ取得できず"
        except Exception as e:
            api_status = "error"
            api_message = f"接続エラー: {str(e)}"
            logger.error(f"ヘルスチェック - API接続エラー: {e}")

        # 総合ステータスを判定
        if db_status == "error" or api_status == "error":
            overall = "error"
        elif db_status == "warning" or api_status == "warning":
            overall = "warning"
        else:
            overall = "healthy"

        return jsonify({
            "overall": overall,
            "timestamp": datetime.utcnow().isoformat() + 'Z',
            "services": {
                "database": {
                    "status": db_status,
                    "message": db_message
                },
                "api": {
                    "status": api_status,
                    "message": api_message
                }
            }
        }), 200

    except Exception as e:
        logger.error(f"ヘルスチェックエラー: {e}", exc_info=True)

        return jsonify({
            "overall": "error",
            "timestamp": datetime.utcnow().isoformat() + 'Z',
            "services": {
                "database": {
                    "status": "unknown",
                    "message": "ステータス不明"
                },
                "api": {
                    "status": "unknown",
                    "message": "ステータス不明"
                }
            },
            "error": str(e)
        }), 500
