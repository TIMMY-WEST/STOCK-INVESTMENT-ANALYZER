from flask import Blueprint

# Bulk Fetch API 用のBlueprint
bulk_api = Blueprint('bulk_api', __name__, url_prefix='/api/bulk-fetch')

# WebSocket進捗通知（flask_socketioが存在する場合のみ有効）
try:
    from flask_socketio import SocketIO
    socketio: SocketIO | None = None  # 実体はアプリ初期化側で設定される想定
    SOCKETIO_AVAILABLE = True
except Exception:
    socketio = None
    SOCKETIO_AVAILABLE = False