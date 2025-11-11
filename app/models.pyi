from typing import Any, List

# NOTE (日本語): このファイルはタイプスタブ（.pyi）です。
# - 目的: 実行時の `app.models` モジュールがエクスポートするシンボルを型チェックツールに
#   認識させるためのスタブを提供します。
# - ファイル名が `.pyi` なのは意図的で、mypy や IDE がスタブとして扱えるようにするためです。
# - 小文字で始まるシンボル（例: `get_db_session`）は関数や変数を示しており、型名ではありません。
#   大文字/小文字の命名はランタイムのエクスポートに合わせています。
#
# If you prefer a different convention (e.g. move some entries to runtime module or refine types),
# please advise and I can adjust the stubs accordingly.

# Type stubs to help static type checkers (mypy) understand symbols exported by app.models

Base: Any
DatabaseError: Any
StockDataError: Any
StockDataBase: Any
Stocks1m: Any
Stocks5m: Any
Stocks15m: Any
Stocks30m: Any
Stocks1h: Any
Stocks1d: Any
Stocks1wk: Any
Stocks1mo: Any
StockDaily: Any
StockMaster: Any
StockMasterUpdate: Any
BatchExecution: Any
BatchExecutionDetail: Any
get_db_session: Any
SessionLocal: Any
DATABASE_URL: Any
engine: Any
StockDailyCRUD: Any

__all__: List[str]
