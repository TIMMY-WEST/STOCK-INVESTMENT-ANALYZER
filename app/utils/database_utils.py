"""データベース操作のユーティリティ関数.

セッション管理やデータベース操作の共通処理を提供します。
"""

from typing import Any, Callable, Dict, Optional, TypeVar

from sqlalchemy.orm import Session

from models import get_db_session


T = TypeVar("T")


def execute_with_session(
    operation: Callable[[Session], T],
    session: Optional[Session] = None,
) -> T:
    """セッションを使用してデータベース操作を実行.

    Args:
        operation: セッションを受け取り処理を実行する関数
        session: SQLAlchemyセッション（省略時は自動生成）

    Returns:
        operation関数の戻り値

    Raises:
        Exception: データベース操作中のエラー
    """
    if session:
        # セッションが提供されている場合はそれを使用
        return operation(session)
    else:
        # セッションが提供されていない場合は新規作成
        with get_db_session() as db_session:
            return operation(db_session)


def to_dict_if_exists(obj: Any) -> Optional[Dict[str, Any]]:
    """オブジェクトが存在する場合は辞書に変換.

    Args:
        obj: 変換対象のオブジェクト（to_dictメソッドを持つ）

    Returns:
        オブジェクトの辞書表現、存在しない場合はNone
    """
    return obj.to_dict() if obj else None
