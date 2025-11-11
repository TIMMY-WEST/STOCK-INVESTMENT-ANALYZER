"""モデル層の型定義がインポートできることを確認するテスト."""

from __future__ import annotations

from app.models import CRUDResult, ErrorDetail, ModelConfig


def test_imports_and_structures():
    """型定義を使って辞書を作成できる(ランタイムチェック)."""
    # ModelConfig のサンプル（必要なキーのみ設定）
    cfg: ModelConfig = {"table_name": "stocks", "schema": "public"}
    assert cfg["table_name"] == "stocks"

    # ErrorDetail と CRUDResult のサンプル
    err: ErrorDetail = {"code": "E001", "message": "sample error"}
    result: CRUDResult = {"ok": False, "errors": [err]}
    assert result["ok"] is False
    assert isinstance(result["errors"], list)
