"""モデル層固有の型定義モジュール.

このモジュールは Issue #252 に基づき、モデル層で使う型を定義します。
ソース内コメントは日本語で記載します。
"""

from __future__ import annotations

# All imports are placed at the top for clarity and consistency
from typing import Any, List, Literal, Optional, TypedDict, TypeVar


# 汎用タイプ変数
T = TypeVar("T")


class ModelConfig(TypedDict, total=False):
    """モデル毎の設定を表す TypedDict.

    total=False としてオプショナルなキーを許容する設計にする。
    """

    table_name: str  # テーブル名
    prefix: Optional[str]  # テーブルプレフィックス（TablePrefix を別途導入して厳密化可）
    schema: Optional[str]  # スキーマ名（Postgres等で使用）


# テーブル接頭辞を厳密にする例。実際の値はプロジェクト方針に合わせる。
TablePrefix = Literal["public", "private", "archive"]


class ErrorDetail(TypedDict, total=False):
    """エラー情報の詳細を表す型定義."""

    code: Optional[str]
    message: Optional[str]
    field: Optional[str]


class CRUDResult(TypedDict, total=False):
    """CRUD 操作の結果を表す TypedDict.

    ジェネリック型を明示したいが、現状互換性のために汎用的な構造で定義する。
    - ok: 操作成功フラグ
    - data: 成功した場合のデータ（任意の型）
    - errors: エラーリスト
    """

    ok: bool
    data: Optional[Any]
    errors: Optional[List[ErrorDetail]]


__all__ = [
    "ModelConfig",
    "TablePrefix",
    "ErrorDetail",
    "CRUDResult",
]
