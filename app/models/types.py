# -*- coding: utf-8 -*-
"""Model layer specific type definitions.

モデル層で使用する固有の型定義をまとめるモジュール。

注意:
- ソース内のコメントは日本語で記載する（リポジトリのルールに従う）。
"""
from __future__ import annotations

from typing import Generic, List, Literal, Optional, TypeVar

from typing_extensions import TypedDict


# 汎用タイプ変数
T = TypeVar("T")


# テーブルプレフィックスを厳密に表現するリテラル型
# データアクセス層仕様書に記載のモデル群を想定して定義する
TablePrefix = Literal[
    "stocks",
    "stock_master",
    "stock_master_updates",
    "batch_executions",
    "batch_execution_details",
]


class ModelConfig(TypedDict, total=False):
    """モデル構成情報を表す TypedDict.

    使用例:
        ModelConfig = {
            "table_name": "stocks_1d",
            "prefix": "stocks",
            "version": 1,
        }
    """

    table_name: str
    prefix: TablePrefix
    version: int
    description: str


class ErrorDetail(TypedDict, total=False):
    """エラー情報の詳細を表す型定義."""

    code: Optional[str]
    message: Optional[str]
    field: Optional[str]


class CRUDResult(TypedDict, Generic[T], total=False):
    """CRUD 操作の結果を表す TypedDict.

    - success: 成功フラグ
    - data: 成功時に返すデータ（ジェネリック）
    - errors: エラー詳細のリスト

    Note: TypedDict と Generic の組み合わせは Python/mypy のバージョンに依存するため、
    必要に応じて実際の呼び出し側で具体化して使ってください。
    """

    success: bool
    data: Optional[T]
    errors: Optional[List[ErrorDetail]]


__all__ = ["TablePrefix", "ModelConfig", "ErrorDetail", "CRUDResult"]
# 汎用タイプ変数
