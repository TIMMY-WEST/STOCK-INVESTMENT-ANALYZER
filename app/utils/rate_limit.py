"""
レート制限関連のユーティリティ
"""

from functools import wraps
from flask import request, jsonify


def rate_limit(requests_per_minute=60):
    """レート制限用のデコレータ（ダミー実装）"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # 本来はここでレート制限チェックを行う
            # 現在はダミー実装として常に許可とする
            return f(*args, **kwargs)
        return decorated_function
    return decorator