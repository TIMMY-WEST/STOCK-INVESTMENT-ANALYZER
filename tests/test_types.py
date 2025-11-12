# tests/test_types.py
# 日本語コメント: このテストは `app/types.py` に定義された共通型の基本的な動作を検証します。

import importlib.util
from pathlib import Path
import types as _types
from typing import get_args, get_origin

import pytest


# テスト実行環境に依存せず、直接ファイルからモジュールを読み込む
root = Path(__file__).resolve().parents[1]
module_path = root / "app" / "types.py"
spec = importlib.util.spec_from_file_location("app.types", str(module_path))
types = _types.ModuleType("app.types")
if spec and spec.loader:
    spec.loader.exec_module(types)
else:
    raise ImportError(f"Cannot load module from {module_path}")


def test_interval_literal_contains_expected_values() -> None:
    """Verify that Interval Literal contains expected strings.

    Interval の Literal が期待する文字列を含むことを確認する。
    """
    origin = get_origin(types.Interval)
    assert origin is not None
    # typing.Literal の場合 get_args で具体的な値が取得できる
    args = get_args(types.Interval)
    expected = ("1m", "5m", "15m", "30m", "1h", "1d", "1wk", "1mo")
    for val in expected:
        assert val in args


def test_process_and_batch_status_enum_values() -> None:
    """Verify ProcessStatus and BatchStatus enum values and names are correct.

    Enum の値とメンバ名が正しいことを検証する。
    """
    assert types.ProcessStatus.PENDING.value == "pending"
    assert types.ProcessStatus.RUNNING.value == "running"
    assert types.ProcessStatus.SUCCESS.value == "success"
    assert types.ProcessStatus.FAILED.value == "failed"

    assert types.BatchStatus.CREATED.value == "created"
    assert types.BatchStatus.IN_PROGRESS.value == "in_progress"
    assert types.BatchStatus.COMPLETED.value == "completed"
    assert types.BatchStatus.FAILED.value == "failed"


def test_pagination_params_typed_dict_behavior() -> None:
    """Verify TypedDict behaves like a dict and keys are optional.

    TypedDict は通常の辞書のように動作するがキーはオプションであることを確認する。
    """
    p1: types.PaginationParams = {"page": 1}
    assert p1["page"] == 1

    p2: types.PaginationParams = {"per_page": 50, "sort": "date"}
    assert p2["per_page"] == 50
    assert p2["sort"] == "date"


def test_module_exports() -> None:
    """Verify module __all__ includes required symbols.

    モジュールの __all__ に必要なシンボルが含まれていることを確認する。
    """
    exports = set(getattr(types, "__all__", []))
    assert "Interval" in exports
    assert "ProcessStatus" in exports
    assert "BatchStatus" in exports
    assert "PaginationParams" in exports
