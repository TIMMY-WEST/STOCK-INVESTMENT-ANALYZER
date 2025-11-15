"""Model-layer specific type definitions.

このモジュールではモデル層で使用する固有の型定義を提供します。

注意:
- ソース内のコメントは日本語で記載します。
"""

from __future__ import annotations

from typing import Generic, Optional, TypeVar


# typing_extensions があれば TypedDict のジェネリック化に対応できるため優先して使用する。
try:
    from typing_extensions import TypedDict
except (
    Exception
):  # pragma: no cover - fallback for environments without typing_extensions
    from typing import TypedDict

from typing import Literal

# プロジェクト共通型をインポート
from app.types import BatchStatus, ProcessStatus


# TablePrefix の候補はデータベース設計に依存するため、ここではプロジェクトでよく使う
# パターンを仮定して定義します。必要に応じて値を追加してください。
TablePrefix = Literal["mst", "trd", "log"]


# モデル設定を表す TypedDict
class ModelConfig(TypedDict, total=False):
    """Model の設定情報を保持する型定義.

    - table_name: テーブル名
    - primary_key: 主キーとなるカラム名
    - prefix: テーブルプレフィックス（厳密な値は TablePrefix）
    - timestamps: created_at / updated_at を扱うか
    - schema_version: スキーマのバージョン（任意）
    """

    table_name: str
    primary_key: str
    prefix: TablePrefix
    timestamps: bool
    schema_version: Optional[int]


T = TypeVar("T")


# Generic TypedDict を使った CRUDResult の定義
class CRUDResult(TypedDict, Generic[T]):
    """CRUD 操作の結果を表す型定義.

    - ok: 成功フラグ
    - data: 成功時に返されるデータ（任意）
    - error: 失敗時のエラーメッセージ（任意）
    """

    ok: bool
    data: Optional[T]
    error: Optional[str]


__all__ = [
    "ModelConfig",
    "TablePrefix",
    "CRUDResult",
    "T",
    "ProcessStatus",
    "BatchStatus",
]
