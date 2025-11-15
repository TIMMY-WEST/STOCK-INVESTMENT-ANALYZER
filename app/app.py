"""Flask application main module.

This module initializes and configures the Flask application,
including WebSocket support, database setup, and API blueprints.
"""

from datetime import date, datetime
import os

from dotenv import load_dotenv
from flask import Blueprint, Flask, jsonify, render_template, request
from flask_socketio import SocketIO

from app.api.bulk_data import (
    bulk_api,
    get_job_status,
    start_bulk_fetch,
    stop_job,
)
from app.api.stock_master import (
    get_stock_master_list,
    stock_master_api,
    update_stock_master,
)
from app.api.swagger import swagger_bp
from app.api.system_monitoring import (
    health_check,
    system_api,
    test_api_connection,
    test_database_connection,
)
from app.middleware import APIVersioningMiddleware
from app.middleware.versioning import (
    create_versioned_blueprint_name,
    create_versioned_url_prefix,
)
from app.models import (
    Base,
    CRUDOperationError,
    DatabaseError,
    StockDailyCRUD,
    engine,
    get_db_session,
)
from app.services.stock_data.orchestrator import StockDataOrchestrator
from app.utils.api_response import APIResponse, ErrorCode
from app.utils.timeframe_utils import (
    get_model_for_interval,
    get_table_name,
    validate_interval,
)


# 環境変数読み込み
load_dotenv()

app = Flask(__name__)

# WebSocket初期化
socketio = SocketIO(app, cors_allowed_origins="*")
app.config["SOCKETIO"] = socketio

# APIバージョニング設定
app.config["API_DEFAULT_VERSION"] = "v1"
app.config["API_SUPPORTED_VERSIONS"] = ["v1"]

# APIバージョニングミドルウェア初期化
versioning_middleware = APIVersioningMiddleware(app)

# テーブル作成
Base.metadata.create_all(bind=engine)

# 既存Blueprint登録（後方互換性のため保持）
app.register_blueprint(bulk_api)
app.register_blueprint(stock_master_api)
app.register_blueprint(system_api)

# バージョン付きBlueprint登録（v1）
# v1バージョンのBlueprint作成と登録
bulk_api_v1 = Blueprint(
    create_versioned_blueprint_name("bulk_api", "v1"),
    __name__,
    url_prefix=create_versioned_url_prefix("/api/bulk-data", "v1"),
)

stock_master_api_v1 = Blueprint(
    create_versioned_blueprint_name("stock_master_api", "v1"),
    __name__,
    url_prefix=create_versioned_url_prefix("/api/stock-master", "v1"),
)

system_api_v1 = Blueprint(
    create_versioned_blueprint_name("system_api", "v1"),
    __name__,
    url_prefix=create_versioned_url_prefix("/api/system", "v1"),
)

# v1 APIエンドポイントを既存のAPIエンドポイントと同じ実装で登録
# bulk_data APIのv1エンドポイント
bulk_api_v1.add_url_rule(
    "/jobs", "start_bulk_fetch", start_bulk_fetch, methods=["POST"]
)
bulk_api_v1.add_url_rule(
    "/jobs/<job_id>", "get_job_status", get_job_status, methods=["GET"]
)
bulk_api_v1.add_url_rule(
    "/jobs/<job_id>/stop", "stop_job", stop_job, methods=["POST"]
)

# stock_master APIのv1エンドポイント
stock_master_api_v1.add_url_rule(
    "/", "update_stock_master", update_stock_master, methods=["POST"]
)
stock_master_api_v1.add_url_rule(
    "/stocks", "get_stock_master_list", get_stock_master_list, methods=["GET"]
)

# system APIのv1エンドポイント
system_api_v1.add_url_rule(
    "/database/connection",
    "test_database_connection",
    test_database_connection,
    methods=["GET"],
)
system_api_v1.add_url_rule(
    "/external-api/connection",
    "test_api_connection",
    test_api_connection,
    methods=["GET"],
)
system_api_v1.add_url_rule(
    "/health-check", "health_check", health_check, methods=["GET"]
)

# バージョン付きBlueprint登録
app.register_blueprint(bulk_api_v1)
app.register_blueprint(stock_master_api_v1)
app.register_blueprint(system_api_v1)

# Swagger UIブループリント登録
app.register_blueprint(swagger_bp)


# WebSocketイベントハンドラ
@socketio.on("connect")
def handle_connect():
    """クライアントがWebSocketに接続した時の処理."""
    print(f"クライアントが接続しました: {request.sid}")


@socketio.on("disconnect")
def handle_disconnect():
    """クライアントがWebSocketから切断した時の処理."""
    print(f"クライアントが切断しました: {request.sid}")


@app.route("/")
def index():
    """Render the main index page.

    Returns:
        Rendered HTML template for the index page.
    """
    return render_template("index.html")


@app.route("/websocket-test")
def websocket_test():
    """WebSocket進捗配信のテストページ."""
    return render_template("websocket_test.html")


@app.route("/api/stocks/data", methods=["POST"])
def fetch_data():
    """Fetch stock data for a given symbol and period.

    Returns:
        JSON response with stock data or error information.
    """
    try:
        data = request.get_json()
        symbol = data.get("symbol", "7203.T")
        period = data.get("period", "1mo")
        interval = data.get("interval", "1d")

        # intervalパラメータのバリデーション
        valid_intervals = [
            "1m",
            "2m",
            "5m",
            "15m",
            "30m",
            "60m",
            "90m",
            "1h",
            "1d",
            "5d",
            "1wk",
            "1mo",
            "3mo",
        ]
        if interval not in valid_intervals:
            return APIResponse.error(
                error_code=ErrorCode.INVALID_INTERVAL,
                message=f"無効な足種別です。有効な値: {', '.join(valid_intervals)}",
                details={
                    "interval": interval,
                    "valid_intervals": valid_intervals,
                },
                status_code=400,
            )

        # StockDataOrchestratorを使用してデータ取得・保存
        orchestrator = StockDataOrchestrator()
        result = orchestrator.fetch_and_save(
            symbol=symbol, interval=interval, period=period
        )

        if result["success"]:
            save_result = result["save_result"]

            return APIResponse.success(
                data={
                    "symbol": symbol,
                    "period": period,
                    "interval": interval,
                    "records_count": result["fetch_count"],
                    "saved_records": save_result["saved"],
                    "skipped_records": save_result.get("skipped", 0),
                    "date_range": {
                        "start": save_result.get("date_range", {}).get(
                            "start", "N/A"
                        ),
                        "end": save_result.get("date_range", {}).get(
                            "end", "N/A"
                        ),
                    },
                },
                message="データを正常に取得し、データベースに保存しました",
                meta={"table_name": get_table_name(interval)},
                status_code=200,
            )
        else:
            # エラーの詳細を分析して適切なエラーコードとステータスコードを返す
            error_message = result.get("error", "Unknown error")

            # 銘柄コード無効のエラー判定（より包括的な条件）
            if (
                "データが取得できませんでした" in error_message
                or "Empty ticker name" in error_message
                or "No data found" in error_message
                or "Invalid symbol" in error_message
                or "無効な銘柄コード" in error_message
            ):
                return APIResponse.error(
                    error_code=ErrorCode.INVALID_SYMBOL,
                    message=f"指定された銘柄コード '{symbol}' のデータが取得できません。銘柄コードを確認してください。",
                    details={"symbol": symbol},
                    status_code=400,
                )

            # その他のデータ取得エラー
            return APIResponse.error(
                error_code=ErrorCode.DATA_FETCH_ERROR,
                message=f"データ取得に失敗しました: {error_message}",
                details={
                    "symbol": symbol,
                    "interval": interval,
                    "period": period,
                },
                status_code=500,
            )

    except Exception as e:
        return APIResponse.error(
            error_code=ErrorCode.EXTERNAL_API_ERROR,
            message=f"データ取得に失敗しました: {str(e)}",
            details={"symbol": symbol if "symbol" in locals() else None},
            status_code=502,
        )


# CRUD API エンドポイント


@app.route("/api/stocks", methods=["POST"])
def create_stock():
    """株価データを作成."""
    try:
        data = request.get_json()
        required_fields = [
            "symbol",
            "date",
            "open",
            "high",
            "low",
            "close",
            "volume",
        ]

        # 必須フィールドのバリデーション
        for field in required_fields:
            if field not in data:
                return (
                    jsonify(
                        {
                            "success": False,
                            "error": "VALIDATION_ERROR",
                            "message": f"必須フィールド '{field}' が不足しています",
                        }
                    ),
                    400,
                )

        # 日付のパース
        try:
            if isinstance(data["date"], str):
                data["date"] = datetime.strptime(
                    data["date"], "%Y-%m-%d"
                ).date()
        except ValueError:
            return (
                jsonify(
                    {
                        "success": False,
                        "error": "VALIDATION_ERROR",
                        "message": "日付の形式が正しくありません (YYYY-MM-DD)",
                    }
                ),
                400,
            )

        with get_db_session() as session:
            stock_data = StockDailyCRUD.create(session, **data)
            return (
                jsonify(
                    {
                        "success": True,
                        "message": "株価データを作成しました",
                        "data": stock_data.to_dict(),
                    }
                ),
                201,
            )

    except CRUDOperationError as e:
        return (
            jsonify(
                {
                    "success": False,
                    "error": "STOCK_DATA_ERROR",
                    "message": str(e),
                }
            ),
            400,
        )
    except DatabaseError as e:
        return (
            jsonify(
                {
                    "success": False,
                    "error": "DATABASE_ERROR",
                    "message": str(e),
                }
            ),
            500,
        )
    except Exception as e:
        return (
            jsonify(
                {
                    "success": False,
                    "error": "INTERNAL_SERVER_ERROR",
                    "message": f"予期しないエラーが発生しました: {str(e)}",
                }
            ),
            500,
        )


@app.route("/api/stocks/<int:stock_id>", methods=["GET"])
def get_stock_by_id(stock_id):
    """ID で株価データを取得."""
    try:
        with get_db_session() as session:
            stock_data = StockDailyCRUD.get_by_id(session, stock_id)
            if not stock_data:
                return (
                    jsonify(
                        {
                            "success": False,
                            "error": "NOT_FOUND",
                            "message": f"ID {stock_id} の株価データが見つかりません",
                        }
                    ),
                    404,
                )

            return jsonify({"success": True, "data": stock_data.to_dict()})

    except DatabaseError as e:
        return (
            jsonify(
                {
                    "success": False,
                    "error": "DATABASE_ERROR",
                    "message": str(e),
                }
            ),
            500,
        )
    except Exception as e:
        return (
            jsonify(
                {
                    "success": False,
                    "error": "INTERNAL_SERVER_ERROR",
                    "message": f"予期しないエラーが発生しました: {str(e)}",
                }
            ),
            500,
        )


def _validate_pagination_params(limit: int, offset: int) -> tuple[bool, dict]:
    """ページネーションパラメータのバリデーション.

    Args:
        limit: 取得件数の上限
        offset: オフセット

    Returns:
        (バリデーション成功フラグ, エラーレスポンス辞書)
    """
    if limit <= 0:
        return False, {
            "success": False,
            "error": "VALIDATION_ERROR",
            "message": "limit は1以上の値を指定してください",
        }

    if offset < 0:
        return False, {
            "success": False,
            "error": "VALIDATION_ERROR",
            "message": "offset は0以上の値を指定してください",
        }

    return True, {}


def _parse_date_param(
    date_str: str, param_name: str
) -> tuple[bool, date | None, dict]:
    """日付パラメータのパース.

    Args:
        date_str: 日付文字列
        param_name: パラメータ名（エラーメッセージ用）

    Returns:
        (パース成功フラグ, パースされた日付, エラーレスポンス辞書)
    """
    try:
        parsed_date = datetime.strptime(date_str, "%Y-%m-%d").date()
        return True, parsed_date, {}
    except ValueError:
        return (
            False,
            None,
            {
                "success": False,
                "error": "VALIDATION_ERROR",
                "message": f"{param_name} の形式が正しくありません (YYYY-MM-DD)",
            },
        )


def _build_stock_query(
    session,
    model_class,
    symbol: str | None,
    start_date: date | None,
    end_date: date | None,
):
    """株価データクエリの構築.

    Args:
        session: データベースセッション
        model_class: モデルクラス
        symbol: 銘柄コード（オプション）
        start_date: 開始日（オプション）
        end_date: 終了日（オプション）

    Returns:
        構築されたクエリオブジェクト
    """
    # 時間軸に応じた日時カラム名を決定
    time_column = (
        model_class.datetime
        if hasattr(model_class, "datetime")
        else model_class.date
    )

    # クエリベースの構築
    query = session.query(model_class)

    # 銘柄フィルタ
    if symbol:
        query = query.filter(model_class.symbol == symbol)

    # 日付範囲フィルタ
    if start_date:
        query = query.filter(time_column >= start_date)
    if end_date:
        query = query.filter(time_column <= end_date)

    return query, time_column


@app.route("/api/stocks", methods=["GET"])
def get_stocks():
    """株価データを取得（クエリパラメータに応じて）."""
    try:
        # クエリパラメータの取得
        symbol = request.args.get("symbol")
        interval = request.args.get("interval", "1d")
        limit = request.args.get("limit", 100, type=int)
        offset = request.args.get("offset", 0, type=int)
        from_param = request.args.get("from")
        to_param = request.args.get("to")
        start_date_raw = (
            from_param if from_param else request.args.get("start_date")
        )
        end_date_raw = to_param if to_param else request.args.get("end_date")

        # 時間軸のバリデーション
        if not validate_interval(interval):
            return APIResponse.error(
                error_code=ErrorCode.VALIDATION_ERROR,
                message=f"無効な時間軸です: {interval}",
                details={"interval": interval},
                status_code=400,
            )

        # ページネーションパラメータのバリデーション
        valid, error_response = _validate_pagination_params(limit, offset)
        if not valid:
            return APIResponse.error(
                error_code=ErrorCode.VALIDATION_ERROR,
                message=error_response.get("message", "パラメータが無効です"),
                details=error_response.get("details", {}),
                status_code=400,
            )

        # 日付のパース
        parsed_start_date = None
        parsed_end_date = None

        if start_date_raw:
            param_name = "from" if from_param else "start_date"
            valid, parsed_start_date, error_response = _parse_date_param(
                start_date_raw, param_name
            )
            if not valid:
                return APIResponse.error(
                    error_code=ErrorCode.VALIDATION_ERROR,
                    message=error_response.get("message", "日付が無効です"),
                    details=error_response.get("details", {}),
                    status_code=400,
                )

        if end_date_raw:
            param_name = "to" if to_param else "end_date"
            valid, parsed_end_date, error_response = _parse_date_param(
                end_date_raw, param_name
            )
            if not valid:
                return APIResponse.error(
                    error_code=ErrorCode.VALIDATION_ERROR,
                    message=error_response.get("message", "日付が無効です"),
                    details=error_response.get("details", {}),
                    status_code=400,
                )

        # 時間軸に応じたモデルクラスを取得
        model_class = get_model_for_interval(interval)

        with get_db_session() as session:
            # クエリの構築
            query, time_column = _build_stock_query(
                session,
                model_class,
                symbol,
                parsed_start_date,
                parsed_end_date,
            )

            # 総件数取得
            total_count = query.count()

            # 並び替えとページネーション
            stocks = (
                query.order_by(time_column.desc())
                .limit(limit)
                .offset(offset)
                .all()
            )

            return APIResponse.paginated(
                data=[stock.to_dict() for stock in stocks],
                total=total_count,
                limit=limit,
                offset=offset,
                meta={
                    "interval": interval,
                    "table_name": get_table_name(interval),
                },
            )

    except DatabaseError as e:
        return APIResponse.error(
            error_code=ErrorCode.DATABASE_ERROR,
            message=str(e),
            status_code=500,
        )
    except Exception as e:
        return APIResponse.error(
            error_code=ErrorCode.INTERNAL_SERVER_ERROR,
            message=f"予期しないエラーが発生しました: {str(e)}",
            status_code=500,
        )


@app.route("/api/stocks/<int:stock_id>", methods=["PUT"])
def update_stock(stock_id):
    """株価データを更新."""
    try:
        data = request.get_json()

        # 日付のパース
        if "date" in data and isinstance(data["date"], str):
            try:
                data["date"] = datetime.strptime(
                    data["date"], "%Y-%m-%d"
                ).date()
            except ValueError:
                return (
                    jsonify(
                        {
                            "success": False,
                            "error": "VALIDATION_ERROR",
                            "message": "日付の形式が正しくありません (YYYY-MM-DD)",
                        }
                    ),
                    400,
                )

        with get_db_session() as session:
            stock_data = StockDailyCRUD.update(session, stock_id, **data)
            if not stock_data:
                return (
                    jsonify(
                        {
                            "success": False,
                            "error": "NOT_FOUND",
                            "message": f"ID {stock_id} の株価データが見つかりません",
                        }
                    ),
                    404,
                )

            return jsonify(
                {
                    "success": True,
                    "message": "株価データを更新しました",
                    "data": stock_data.to_dict(),
                }
            )

    except CRUDOperationError as e:
        return (
            jsonify(
                {
                    "success": False,
                    "error": "STOCK_DATA_ERROR",
                    "message": str(e),
                }
            ),
            400,
        )
    except DatabaseError as e:
        return (
            jsonify(
                {
                    "success": False,
                    "error": "DATABASE_ERROR",
                    "message": str(e),
                }
            ),
            500,
        )
    except Exception as e:
        return (
            jsonify(
                {
                    "success": False,
                    "error": "INTERNAL_SERVER_ERROR",
                    "message": f"予期しないエラーが発生しました: {str(e)}",
                }
            ),
            500,
        )


@app.route("/api/stocks/<int:stock_id>", methods=["DELETE"])
def delete_stock(stock_id):
    """株価データを削除."""
    try:
        with get_db_session() as session:
            if StockDailyCRUD.delete(session, stock_id):
                return jsonify(
                    {
                        "success": True,
                        "message": f"ID {stock_id} の株価データを削除しました",
                    }
                )
            else:
                return (
                    jsonify(
                        {
                            "success": False,
                            "error": "NOT_FOUND",
                            "message": f"ID {stock_id} の株価データが見つかりません",
                        }
                    ),
                    404,
                )

    except DatabaseError as e:
        return (
            jsonify(
                {
                    "success": False,
                    "error": "DATABASE_ERROR",
                    "message": str(e),
                }
            ),
            500,
        )
    except Exception as e:
        return (
            jsonify(
                {
                    "success": False,
                    "error": "INTERNAL_SERVER_ERROR",
                    "message": f"予期しないエラーが発生しました: {str(e)}",
                }
            ),
            500,
        )


@app.route("/api/stocks/test", methods=["POST"])
def create_test_data():
    """テスト用サンプルデータを作成."""
    try:
        test_data = [
            {
                "symbol": "7203.T",
                "date": date(2024, 9, 9),
                "open": 2500.00,
                "high": 2550.00,
                "low": 2480.00,
                "close": 2530.00,
                "volume": 1500000,
            },
            {
                "symbol": "7203.T",
                "date": date(2024, 9, 8),
                "open": 2480.00,
                "high": 2520.00,
                "low": 2460.00,
                "close": 2500.00,
                "volume": 1200000,
            },
            {
                "symbol": "6502.T",
                "date": date(2024, 9, 9),
                "open": 4500.00,
                "high": 4580.00,
                "low": 4450.00,
                "close": 4550.00,
                "volume": 800000,
            },
        ]

        with get_db_session() as session:
            created_stocks = StockDailyCRUD.bulk_create(session, test_data)
            return (
                jsonify(
                    {
                        "success": True,
                        "message": f"{len(created_stocks)} 件のテストデータを作成しました",
                        "data": [stock.to_dict() for stock in created_stocks],
                    }
                ),
                201,
            )

    except CRUDOperationError as e:
        return (
            jsonify(
                {
                    "success": False,
                    "error": "STOCK_DATA_ERROR",
                    "message": str(e),
                }
            ),
            400,
        )
    except DatabaseError as e:
        return (
            jsonify(
                {
                    "success": False,
                    "error": "DATABASE_ERROR",
                    "message": str(e),
                }
            ),
            500,
        )
    except Exception as e:
        return (
            jsonify(
                {
                    "success": False,
                    "error": "INTERNAL_SERVER_ERROR",
                    "message": f"予期しないエラーが発生しました: {str(e)}",
                }
            ),
            500,
        )


if __name__ == "__main__":
    port = int(os.getenv("FLASK_PORT", 8000))
    host = os.getenv("FLASK_HOST", "127.0.0.1")
    # 明示的にアクセス用アドレスを表示
    print(f"http://{host}:{port}/")

    socketio.run(
        app,
        debug=os.getenv("FLASK_DEBUG", "False").lower() == "true",
        port=port,
        host=host,
    )
