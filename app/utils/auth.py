"""
認証関連のユーティリティ
"""

from functools import wraps
from flask import request, jsonify


def require_auth(f):
    """認証が必要なエンドポイント用のデコレータ（ダミー実装）"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # 本来はここで認証チェックを行う
        # 現在はダミー実装として常に認証成功とする
        return f(*args, **kwargs)
    return decorated_function


def require_api_key(f):
    """APIキーが必要なエンドポイント用のデコレータ（ダミー実装）"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # 本来はここでAPIキーチェックを行う
        # 現在はダミー実装として常に認証成功とする
        return f(*args, **kwargs)
    return decorated_function