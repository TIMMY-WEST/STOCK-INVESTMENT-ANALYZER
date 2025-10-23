"""JPX銘柄マスタ管理API.

JPX銘柄一覧の取得・更新機能を提供するAPIエンドポイント。
"""

from functools import wraps
import logging
import os

from flask import Blueprint, jsonify, request

from services.jpx_stock_service import JPXStockService, JPXStockServiceError


logger = logging.getLogger(__name__)

# Blueprintを作成
stock_master_api = Blueprint("stock_master_api", __name__)


# APIキー認証
def require_api_key(f):
    """API key authentication decorator.

    Skips authentication if API_KEY environment variable is not set (for development).
    """

    @wraps(f)
    def decorated_function(*args, **kwargs):
        expected_api_key = os.getenv("API_KEY")

        # API_KEYが設定されていない場合は認証不要
        if not expected_api_key:
            return f(*args, **kwargs)

        # API_KEYが設定されている場合は認証必須
        api_key = request.headers.get("X-API-Key")
        if not api_key or api_key != expected_api_key:
            logger.warning(f"無効なAPIキー: {api_key}")
            return jsonify({"error": "認証が必要です"}), 401

        return f(*args, **kwargs)

    return decorated_function


@stock_master_api.route("/api/stock-master/update", methods=["POST"])
@require_api_key
def update_stock_master():
    """JPX銘柄マスタ更新API.

    JPXから最新の銘柄一覧を取得してデータベースを更新します。

    Request Body (JSON):
        {
            "update_type": "manual" | "scheduled"  // 更新タイプ（オプション、デフォルト: "manual"）
        }

    Response:
        成功時 (200):
        {
            "status": "success",
            "message": "銘柄マスタの更新が完了しました",
            "data": {
                "update_type": "manual",
                "total_stocks": 3800,
                "added_stocks": 50,
                "updated_stocks": 3700,
                "removed_stocks": 10,
                "status": "success"
            }
        }

        エラー時 (400/500):
        {
            "status": "error",
            "message": "エラーメッセージ",
            "error_code": "JPX_DOWNLOAD_ERROR" | "JPX_PARSE_ERROR" | "DATABASE_ERROR"
        }.
    """
    try:
        # リクエストボディを取得
        data = request.get_json() or {}
        update_type = data.get("update_type", "manual")

        # 更新タイプの検証
        if update_type not in ["manual", "scheduled"]:
            return (
                jsonify(
                    {
                        "status": "error",
                        "message": 'update_typeは "manual" または "scheduled" である必要があります',
                        "error_code": "INVALID_PARAMETER",
                    }
                ),
                400,
            )

        logger.info(f"銘柄マスタ更新開始: update_type={update_type}")

        # JPX銘柄サービスを使用して更新
        service = JPXStockService()
        result = service.update_stock_master(update_type=update_type)

        logger.info(f"銘柄マスタ更新完了: {result}")

        return (
            jsonify(
                {
                    "status": "success",
                    "message": "銘柄マスタの更新が完了しました",
                    "data": result,
                }
            ),
            200,
        )

    except JPXStockServiceError as e:
        logger.error(f"JPX銘柄サービスエラー: {str(e)}")

        # エラータイプに応じてエラーコードを設定
        error_code = "JPX_SERVICE_ERROR"
        if "ダウンロード" in str(e):
            error_code = "JPX_DOWNLOAD_ERROR"
        elif "パース" in str(e) or "正規化" in str(e):
            error_code = "JPX_PARSE_ERROR"
        elif "データベース" in str(e):
            error_code = "DATABASE_ERROR"

        return (
            jsonify(
                {
                    "status": "error",
                    "message": str(e),
                    "error_code": error_code,
                }
            ),
            500,
        )

    except Exception as e:
        logger.error(f"予期しないエラー: {str(e)}")
        return (
            jsonify(
                {
                    "status": "error",
                    "message": "内部サーバーエラーが発生しました",
                    "error_code": "INTERNAL_ERROR",
                }
            ),
            500,
        )


@stock_master_api.route("/api/stock-master/list", methods=["GET"])
@require_api_key
def get_stock_master_list():
    """JPX銘柄マスタ一覧取得API.

    データベースに保存されている銘柄マスタ一覧を取得します。

    Query Parameters:
        - is_active: 有効フラグ (true/false/all, デフォルト: true)
        - market_category: 市場区分でフィルタ (部分一致)
        - limit: 取得件数上限 (1-1000, デフォルト: 100)
        - offset: オフセット (0以上, デフォルト: 0)

    Response:
        成功時 (200):
        {
            "status": "success",
            "message": "銘柄一覧を取得しました",
            "data": {
                "total": 3800,
                "stocks": [
                    {
                        "id": 1,
                        "stock_code": "1301",
                        "stock_name": "極洋",
                        "market_category": "プライム",
                        "sector_code_33": "050",
                        "sector_name_33": "水産・農林業",
                        "sector_code_17": "01",
                        "sector_name_17": "食品",
                        "scale_code": "2",
                        "scale_category": "中型株",
                        "data_date": "20241201",
                        "is_active": true,
                        "created_at": "2024-12-01T10:00:00Z",
                        "updated_at": "2024-12-01T10:00:00Z"
                    }
                ]
            }
        }

        エラー時 (400/500):
        {
            "status": "error",
            "message": "エラーメッセージ",
            "error_code": "INVALID_PARAMETER" | "DATABASE_ERROR"
        }.
    """
    try:
        # クエリパラメータを取得
        is_active_param = request.args.get("is_active", "true").lower()
        market_category = request.args.get("market_category")
        limit = request.args.get("limit", "100")
        offset = request.args.get("offset", "0")

        # パラメータの検証
        try:
            limit = int(limit)
            offset = int(offset)
        except ValueError:
            return (
                jsonify(
                    {
                        "status": "error",
                        "message": "limitとoffsetは数値である必要があります",
                        "error_code": "INVALID_PARAMETER",
                    }
                ),
                400,
            )

        if limit < 1 or limit > 1000:
            return (
                jsonify(
                    {
                        "status": "error",
                        "message": "limitは1から1000の間である必要があります",
                        "error_code": "INVALID_PARAMETER",
                    }
                ),
                400,
            )

        if offset < 0:
            return (
                jsonify(
                    {
                        "status": "error",
                        "message": "offsetは0以上である必要があります",
                        "error_code": "INVALID_PARAMETER",
                    }
                ),
                400,
            )

        # is_activeパラメータの処理
        if is_active_param == "all":
            is_active = None
        elif is_active_param == "true":
            is_active = True
        elif is_active_param == "false":
            is_active = False
        else:
            return (
                jsonify(
                    {
                        "status": "error",
                        "message": 'is_activeは "true", "false", "all" のいずれかである必要があります',
                        "error_code": "INVALID_PARAMETER",
                    }
                ),
                400,
            )

        logger.info(
            f"銘柄一覧取得: is_active={is_active}, market_category={market_category}, limit={limit}, offset={offset}"
        )

        # JPX銘柄サービスを使用して一覧を取得
        service = JPXStockService()
        result = service.get_stock_list(
            is_active=is_active,
            market_category=market_category,
            limit=limit,
            offset=offset,
        )

        logger.info(
            f"銘柄一覧取得完了: total={result['total']}, count={len(result['stocks'])}"
        )

        return (
            jsonify(
                {
                    "status": "success",
                    "message": "銘柄一覧を取得しました",
                    "data": result,
                }
            ),
            200,
        )

    except JPXStockServiceError as e:
        logger.error(f"JPX銘柄サービスエラー: {str(e)}")
        return (
            jsonify(
                {
                    "status": "error",
                    "message": str(e),
                    "error_code": "DATABASE_ERROR",
                }
            ),
            500,
        )

    except Exception as e:
        logger.error(f"予期しないエラー: {str(e)}")
        return (
            jsonify(
                {
                    "status": "error",
                    "message": "内部サーバーエラーが発生しました",
                    "error_code": "INTERNAL_ERROR",
                }
            ),
            500,
        )


@stock_master_api.route("/api/stock-master/status", methods=["GET"])
@require_api_key
def get_stock_master_status():
    """JPX銘柄マスタ状態取得API.

    銘柄マスタの現在の状態と最新の更新履歴を取得します。

    Response:
        成功時 (200):
        {
            "status": "success",
            "message": "銘柄マスタ状態を取得しました",
            "data": {
                "total_stocks": 3800,
                "active_stocks": 3790,
                "inactive_stocks": 10,
                "last_update": {
                    "id": 123,
                    "update_type": "manual",
                    "total_stocks": 3800,
                    "added_stocks": 50,
                    "updated_stocks": 3700,
                    "removed_stocks": 10,
                    "status": "success",
                    "created_at": "2024-12-01T10:00:00Z",
                    "completed_at": "2024-12-01T10:05:00Z"
                }
            }
        }.
    """
    try:
        from models import StockMaster, StockMasterUpdate, get_db_session

        with get_db_session() as session:
            # 銘柄統計を取得
            total_stocks = session.query(StockMaster).count()
            active_stocks = (
                session.query(StockMaster)
                .filter(StockMaster.is_active == 1)
                .count()
            )
            inactive_stocks = total_stocks - active_stocks

            # 最新の更新履歴を取得
            last_update = (
                session.query(StockMasterUpdate)
                .order_by(StockMasterUpdate.started_at.desc())
                .first()
            )

            last_update_data = None
            if last_update:
                last_update_data = last_update.to_dict()

        logger.info(
            f"銘柄マスタ状態取得完了: total={total_stocks}, active={active_stocks}"
        )

        return (
            jsonify(
                {
                    "status": "success",
                    "message": "銘柄マスタ状態を取得しました",
                    "data": {
                        "total_stocks": total_stocks,
                        "active_stocks": active_stocks,
                        "inactive_stocks": inactive_stocks,
                        "last_update": last_update_data,
                    },
                }
            ),
            200,
        )

    except Exception as e:
        logger.error(f"銘柄マスタ状態取得エラー: {str(e)}")
        return (
            jsonify(
                {
                    "status": "error",
                    "message": "内部サーバーエラーが発生しました",
                    "error_code": "INTERNAL_ERROR",
                }
            ),
            500,
        )
