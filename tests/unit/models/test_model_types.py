"""Tests for model-layer type definitions.

これらのテストは型定義モジュールが正しくエクスポートされ、
基本的な利用（辞書としての TypedDict 等）が問題ないことを確認します。
"""

from __future__ import annotations

from typing import cast

import pytest


def test_types_module_exports():
    """Verify the module exports expected symbols."""
    import app.models.types as mtypes

    assert hasattr(mtypes, "ModelConfig")
    assert hasattr(mtypes, "TablePrefix")
    assert hasattr(mtypes, "CRUDResult")


def test_modelconfig_structure_and_values():
    """Verify ModelConfig TypedDict works as a dict."""
    from app.models.types import ModelConfig

    cfg: ModelConfig = {
        "table_name": "stock_daily",
        "primary_key": "id",
        "prefix": "mst",
        "timestamps": True,
        "schema_version": 1,
    }

    assert cfg["table_name"] == "stock_daily"
    assert cfg["primary_key"] == "id"
    assert cfg["prefix"] == "mst"
    assert cfg["timestamps"] is True
    assert isinstance(cfg["schema_version"], int)


def test_crudresult_generic_usage():
    """Verify CRUDResult generic TypedDict can be used as a dict."""
    from app.models.types import CRUDResult

    # 型チェック目的で cast を使い、実行時には通常の dict として扱う
    result = cast(CRUDResult[int], {"ok": True, "data": 42, "error": None})

    assert result["ok"] is True
    assert result["data"] == 42
    assert result["error"] is None
