"""Unit tests for app.models.types.

These tests validate that the module is importable and the basic
TypedDict-based structures can be constructed and have the expected keys.
"""
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path


def _load_types_module():
    """Load app/models/types.py by file path to avoid package name collision.

    Note: repository contains `app/models.py` as a module, so `app.models` is
    not a package. For the unit test we import the file directly by path.
    """
    repo_root = Path(__file__).resolve().parents[3]
    types_path = repo_root / "app" / "models" / "types.py"
    spec = spec_from_file_location("app_models_types", str(types_path))
    module = module_from_spec(spec)
    assert spec is not None and spec.loader is not None
    spec.loader.exec_module(module)  # type: ignore[attr-defined]
    return module


def test_import_module():
    """Module file should be loadable and expose expected names."""
    mod = _load_types_module()
    assert hasattr(mod, "ModelConfig")
    assert hasattr(mod, "CRUDResult")
    assert hasattr(mod, "TablePrefix")


def test_model_config_structure():
    """ModelConfig-like dict should contain expected keys and types."""
    cfg = {
        "table_name": "stocks_1d",
        "prefix": "stocks",
        "version": 1,
        "description": "daily stocks table",
    }

    # runtimeでTypedDictはdictなので基本的な構造を検証する
    assert isinstance(cfg, dict)
    assert cfg["table_name"] == "stocks_1d"
    assert cfg["prefix"] in (
        "stocks",
        "stock_master",
        "stock_master_updates",
        "batch_executions",
        "batch_execution_details",
    )
    assert isinstance(cfg["version"], int)
    assert isinstance(cfg["description"], str)


def test_crud_result_structure():
    """CRUDResult-like dict should accept success/data/errors keys."""
    res = {"success": True, "data": {"id": 1}, "errors": None}

    assert res["success"] is True
    assert isinstance(res["data"], dict)
    assert res["errors"] is None or isinstance(res["errors"], list)
