"""models パッケージの初期化.

このパッケージは既存の単一モジュール `app/models.py` を段階的にパッケージ化するための
ブリッジを提供します。

実行時に古い `app/models.py` をロードして、その公開シンボルをこのパッケージの名前空間に
再公開します。これにより既存の `from app import models` や `from app.models import StockDataBase` といった
インポート呼び出しを壊さずに、モデル固有の型定義ファイルを同階層に追加できます。

注: コメントは日本語で記述します（プロジェクト規約）。
"""

from __future__ import annotations

import importlib.util
import logging
from pathlib import Path
import sys
from types import ModuleType


_logger = logging.getLogger(__name__)


# まず、モデル層固有の型を読み込む（同パッケージ内の types.py）
try:
    from .types import CRUDResult, ErrorDetail, ModelConfig, TablePrefix
except (ImportError, ModuleNotFoundError):
    # 開発環境や一時的な状態で types.py が存在しない場合があるため、安全に動作する
    # 明確な ignore 理由を付与して型チェックツールが警告を解釈しやすくする
    CRUDResult = None  # type: ignore[assignment] 型互換のため None で初期化
    ErrorDetail = None  # type: ignore[assignment] 型互換のため None で初期化
    ModelConfig = None  # type: ignore[assignment] 型互換のため None で初期化
    TablePrefix = None  # type: ignore[assignment] 型互換のため None で初期化


# 次に既存の単一モジュールファイル（app/models.py）をロードして、そのシンボルを再公開する
_models_py = Path(__file__).parent.parent / "models.py"
if _models_py.exists():
    spec = importlib.util.spec_from_file_location(
        "app._models_impl", str(_models_py)
    )
    if spec and spec.loader:
        _mod = importlib.util.module_from_spec(spec)  # type: ModuleType
        sys.modules["app._models_impl"] = _mod
        try:
            spec.loader.exec_module(_mod)
        except Exception:
            # モジュールの実行中に予期しないエラーが発生した場合はログに残す。
            _logger.exception(
                "failed to execute app/models.py when bridging to package import"
            )
            # 続行して空の __all__ を生成する（既存の動作を壊さないようにする）
            __all__ = []
            # 中断せずに外側の分岐に委ねる
        else:
            # 可能な限り元の models.py の公開シンボルをこのパッケージの名前空間に再公開する。
            # __all__ が定義されていればそれを用い、無ければ public な属性を全て再公開する。
            if hasattr(_mod, "__all__") and isinstance(
                getattr(_mod, "__all__"), (list, tuple)
            ):
                public_names = list(getattr(_mod, "__all__"))
            else:
                public_names = [n for n in dir(_mod) if not n.startswith("_")]

            for name in public_names:
                try:
                    globals()[name] = getattr(_mod, name)
                except AttributeError as exc:
                    # 指定された属性が存在しない場合のみスキップする。
                    # 予期しない例外はログに残すことでデバッグしやすくする。
                    _logger.debug(
                        "missing attribute %s in bridged module: %s", name, exc
                    )
                    continue
                except Exception:
                    # その他の例外は詳細にログに残してからスキップする。
                    _logger.exception(
                        "unexpected error while copying attribute %s from bridged module",
                        name,
                    )
                    continue

            # __all__ を構築
            __all__ = list(public_names)
    else:
        __all__ = []
else:
    __all__ = []

# 型定義を優先的に __all__ に追加（存在する場合）
for t in ("ModelConfig", "TablePrefix", "ErrorDetail", "CRUDResult"):
    if t not in __all__ and t in globals():
        __all__.append(t)
