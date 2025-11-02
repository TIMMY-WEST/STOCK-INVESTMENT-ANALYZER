# 例外処理ガイド

## 概要

本プロジェクトでは、統一された例外処理体系を提供するため、カスタム例外クラスを導入しています。
このガイドでは、新しい例外クラスの使用方法とエラーハンドリングのベストプラクティスを説明します。

## 例外クラス体系

### 基底クラス

```python
from app.exceptions import BaseStockAnalyzerException, ErrorCode

# 基本的な使用方法
raise BaseStockAnalyzerException(
    message="エラーメッセージ",
    error_code=ErrorCode.SYSTEM_ERROR
)

# 詳細情報付きの使用方法
raise BaseStockAnalyzerException(
    message="データベース接続エラー",
    error_code=ErrorCode.DATABASE_CONNECTION,
    details={"host": "localhost", "port": 5432}
)
```

### カテゴリ別例外クラス

#### 1. SystemException
システム全体に関わる重大なエラー

```python
from app.exceptions import SystemException, ErrorCode

raise SystemException(
    message="システムリソース不足",
    error_code=ErrorCode.SYSTEM_RESOURCE
)
```

#### 2. DatabaseException
データベース関連のエラー

```python
from app.exceptions import DatabaseException, ErrorCode

# 接続エラー（一時的）
raise DatabaseException(
    message="データベース接続タイムアウト",
    error_code=ErrorCode.DATABASE_TIMEOUT
)

# 保存エラー（永続的）
raise DatabaseException(
    message="データ保存に失敗",
    error_code=ErrorCode.DATABASE_SAVE,
    details={"table": "stocks_1d", "stock_code": "7203.T"}
)
```

#### 3. APIException
外部API関連のエラー

```python
from app.exceptions import APIException, ErrorCode

# タイムアウトエラー（一時的）
raise APIException(
    message="Yahoo Finance APIタイムアウト",
    error_code=ErrorCode.API_TIMEOUT,
    details={"endpoint": "/v8/finance/chart", "timeout": 30}
)

# 認証エラー（永続的）
raise APIException(
    message="API認証に失敗",
    error_code=ErrorCode.API_AUTHENTICATION
)
```

#### 4. StockDataException
株価データ関連のエラー

```python
from app.exceptions import StockDataException, ErrorCode

raise StockDataException(
    message="株価データの取得に失敗",
    error_code=ErrorCode.STOCK_DATA_FETCH,
    details={"stock_code": "7203.T", "timeframe": "1d"}
)
```

#### 5. ValidationException
データ検証関連のエラー

```python
from app.exceptions import ValidationException, ErrorCode

raise ValidationException(
    message="必須フィールドが不足",
    error_code=ErrorCode.VALIDATION_REQUIRED_FIELD,
    details={"missing_fields": ["stock_code", "date"]}
)
```

## エラーハンドリング

### ErrorHandlerとの連携

新しい例外クラスは`ErrorHandler`と自動的に連携し、適切な分類とアクションが実行されます：

```python
from app.services.common.error_handler import ErrorHandler
from app.exceptions import APIException, ErrorCode

error_handler = ErrorHandler()

try:
    # 何らかの処理
    pass
except Exception as e:
    # エラーハンドラーが自動的に分類・処理
    action = error_handler.handle_error(e, stock_code="7203.T")

    if action == ErrorAction.RETRY:
        # リトライ処理
        pass
    elif action == ErrorAction.SKIP:
        # スキップして次の処理へ
        pass
    elif action == ErrorAction.ABORT:
        # バッチ処理を停止
        break
```

### エラー分類

例外は以下の3つのタイプに自動分類されます：

| エラータイプ | 説明 | アクション | 例 |
|-------------|------|-----------|---|
| TEMPORARY | 一時的なエラー | リトライ | ネットワークタイムアウト、レート制限 |
| PERMANENT | 永続的なエラー | スキップ | データ形式エラー、認証エラー |
| SYSTEM | システムエラー | バッチ停止 | メモリ不足、設定エラー |

## 既存コードとの互換性

既存の例外クラス（`DatabaseError`、`StockDataError`など）は引き続き使用可能です：

```python
# 既存コード（引き続き動作）
from app.exceptions import DatabaseError

raise DatabaseError("データベースエラー")

# 新しいコード（推奨）
from app.exceptions import DatabaseException, ErrorCode

raise DatabaseException(
    message="データベースエラー",
    error_code=ErrorCode.DATABASE_CONNECTION
)
```

## ベストプラクティス

### 1. 適切なエラーコードの選択

```python
# 良い例：具体的なエラーコード
raise APIException(
    message="レート制限に達しました",
    error_code=ErrorCode.API_RATE_LIMIT
)

# 悪い例：汎用的すぎるエラーコード
raise APIException(
    message="レート制限に達しました",
    error_code=ErrorCode.API_ERROR  # 汎用的すぎる
)
```

### 2. 詳細情報の活用

```python
# 良い例：デバッグに有用な詳細情報
raise StockDataException(
    message="株価データの変換に失敗",
    error_code=ErrorCode.STOCK_DATA_CONVERSION,
    details={
        "stock_code": "7203.T",
        "timeframe": "1d",
        "raw_data_length": 100,
        "expected_columns": ["Open", "High", "Low", "Close"],
        "actual_columns": ["open", "high", "low"]  # 大文字小文字の違い
    }
)
```

### 3. ログとの連携

```python
import logging
from app.exceptions import DatabaseException, ErrorCode

logger = logging.getLogger(__name__)

try:
    # データベース処理
    pass
except Exception as e:
    # カスタム例外として再発生
    db_error = DatabaseException(
        message=f"データ保存に失敗: {str(e)}",
        error_code=ErrorCode.DATABASE_SAVE,
        details={"original_error": str(e)}
    )

    logger.error(f"Database error: {db_error}")
    raise db_error
```

## 参考資料

- [エラーハンドラー実装](../app/services/common/error_handler.py)
- [例外クラス定義](../app/exceptions.py)
- [テストコード](../tests/unit/test_exceptions.py)
