"""株価投資分析システムのデータベースモデル定義.

このモジュールは、株価データ、銘柄マスタ、バッチ実行履歴などの
データベースモデルとCRUD操作を提供します。

モジュール構成:
    - base: SQLAlchemyのベースクラスと共通機能
    - database: データベース接続とセッション管理
    - exceptions: カスタム例外クラス定義
    - types: 型定義
    - stock_data: 株価データモデル
    - master: 銘柄マスタモデル
    - batch: バッチ実行管理モデル
    - crud: CRUD操作クラス
"""

# Base classes and database utilities
from app.models.base import Base, StockDataBase

# Batch execution models
from app.models.batch import BatchExecution, BatchExecutionDetail

# CRUD classes
from app.models.crud import StockDailyCRUD
from app.models.database import (
    DATABASE_URL,
    SessionLocal,
    engine,
    get_db_session,
)

# Exception classes
from app.models.exceptions import (
    BaseModelException,
    CRUDOperationError,
    DatabaseError,
    ModelNotFoundError,
    ValidationError,
)

# Master data models
from app.models.master import StockMaster, StockMasterUpdate

# Stock data models
from app.models.stock_data import (
    StockDaily,
    Stocks1d,
    Stocks1h,
    Stocks1m,
    Stocks1mo,
    Stocks1wk,
    Stocks5m,
    Stocks15m,
    Stocks30m,
)

# Type definitions
from app.models.types import (
    BatchStatus,
    CRUDResult,
    ModelConfig,
    ProcessStatus,
    TablePrefix,
)


__all__ = [
    # Base classes
    "Base",
    "StockDataBase",
    # Exception classes
    "BaseModelException",
    "DatabaseError",
    "CRUDOperationError",
    "ModelNotFoundError",
    "ValidationError",
    # Stock data models
    "Stocks1m",
    "Stocks5m",
    "Stocks15m",
    "Stocks30m",
    "Stocks1h",
    "Stocks1d",
    "Stocks1wk",
    "Stocks1mo",
    "StockDaily",
    # Master data models
    "StockMaster",
    "StockMasterUpdate",
    # Batch execution models
    "BatchExecution",
    "BatchExecutionDetail",
    # Database utilities
    "DATABASE_URL",
    "engine",
    "SessionLocal",
    "get_db_session",
    # CRUD classes
    "StockDailyCRUD",
    # Model-layer types
    "BatchStatus",
    "CRUDResult",
    "ModelConfig",
    "ProcessStatus",
    "TablePrefix",
]
