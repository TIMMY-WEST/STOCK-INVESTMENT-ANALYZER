# ⚠️ このドキュメントは非推奨です

**移行日**: 2025-11-02
**理由**: 内容が `docs/standards/` 配下のファイルに統合されました
**移行先**:
- コーディング規約全般: `docs/standards/coding-standards.md`
- 例外処理: `docs/standards/exception_handling.md`
- 型ヒント: `docs/standards/type_hints_guide.md`
- フロントエンド: `docs/standards/frontend_guide.md`

このドキュメントは参照用として保管されていますが、最新情報は上記の移行先を参照してください。

---

# コーディング規約とスタイルガイド

## 概要

このドキュメントは、STOCK-INVESTMENT-ANALYZERプロジェクトにおけるPythonコードの記述ルールを定めます。
本プロジェクトは**PEP 8**（Python Enhancement Proposal 8）に準拠し、一貫性のある読みやすいコードを目指します。

## 目次

1. [基本方針](#基本方針)
2. [コードレイアウト](#コードレイアウト)
3. [命名規則](#命名規則)
4. [インポート文](#インポート文)
5. [型ヒント](#型ヒント)
6. [コメントとドキュメンテーション](#コメントとドキュメンテーション)
7. [例外処理](#例外処理)
8. [その他のベストプラクティス](#その他のベストプラクティス)

---

## 基本方針

### PEP 8準拠

- **PEP 8**を基本とし、可読性と保守性を重視します
- 一貫性を保つことを最優先とします
- チーム全体で実行可能なルールを策定します

### 参考資料

- [PEP 8 -- Style Guide for Python Code](https://peps.python.org/pep-0008/)
- [Google Python Style Guide](https://google.github.io/styleguide/pyguide.html)

---

## コードレイアウト

### インデント

```python
# 良い例
def function_name(param1, param2):
    if condition:
        return result
```

- **スペース4つ**を使用（タブは使用しない）
- 継続行のインデントも4スペース

### 行の最大長

```python
# 良い例（79文字以内）
def fetch_data(symbol: str, interval: str, period: str) -> pd.DataFrame:
    """株価データを取得する"""
    pass

# 長い文字列の場合
message = (
    "これは非常に長いメッセージです。"
    "複数行に分割して記述します。"
)
```

- **1行79文字以内**を推奨
- docstringやコメントは72文字以内を推奨
- 長い行は適切に改行する

### 空行

```python
# モジュールレベルの定数
DEFAULT_INTERVAL = '1d'
MAX_RETRIES = 3


class StockDataFetcher:
    """株価データ取得クラス"""

    def __init__(self):
        """初期化"""
        pass

    def fetch_data(self):
        """データ取得"""
        pass


def standalone_function():
    """スタンドアロン関数"""
    pass
```

- トップレベルの関数とクラス定義の前後に**2行**
- クラス内のメソッド定義の間に**1行**
- 関数内の論理的なセクションの区切りに適宜1行

### 文字列の引用符

```python
# 良い例
message = "これはメッセージです"
sql_query = 'SELECT * FROM stocks WHERE symbol = "7203.T"'

# docstringは三重引用符
def function():
    """
    関数の説明
    """
    pass
```

- 通常は**ダブルクォーテーション（"）** を使用
- 文字列内にダブルクォーテーションが含まれる場合はシングルクォーテーション（'）を使用
- docstringは常に**三重ダブルクォーテーション（"""）** を使用

---

## 命名規則

### モジュール名（ファイル名）

```python
# 良い例
stock_data_fetcher.py
structured_logger.py
timeframe_utils.py

# 悪い例
StockDataFetcher.py
StructuredLogger.py
```

- **小文字のみ使用**
- 単語の区切りは**アンダースコア（_）**
- 短く簡潔に

### パッケージ名（ディレクトリ名）

```python
# 良い例
services/
utils/
api/

# 悪い例
Services/
stock_utils/
```

- **小文字のみ使用**
- アンダースコアは避け、短く簡潔に

### クラス名

```python
# 良い例
class StockDataFetcher:
    pass

class BatchExecutionDetail:
    pass

class StockDataFetchError(Exception):
    pass

# 悪い例
class stock_data_fetcher:
    pass

class STOCK_DATA_FETCHER:
    pass
```

- **PascalCase（CapWords）** を使用
- 例外クラスは`Error`で終わる名前を使用

### 関数名・メソッド名

```python
# 良い例
def fetch_stock_data(symbol: str) -> pd.DataFrame:
    pass

def _format_symbol_for_yahoo(symbol: str) -> str:
    pass

# 悪い例
def FetchStockData(symbol: str):
    pass

def fetchStockData(symbol: str):
    pass
```

- **小文字とアンダースコア（snake_case）** を使用
- 動詞から始めることを推奨（例: `get_`, `fetch_`, `validate_`, `calculate_`）
- プライベートメソッドは**アンダースコア（_）で開始**

### 変数名

```python
# 良い例
stock_code = "7203.T"
batch_execution_id = 123
retry_count = 0

# インスタンス変数
self.logger = logger
self._is_running = False

# 悪い例
stockCode = "7203.T"
s = "7203.T"
BatchExecutionID = 123
```

- **小文字とアンダースコア（snake_case）** を使用
- 意味のある名前を使用（1文字変数は避ける）
- プライベート変数は**アンダースコア（_）で開始**

### 定数

```python
# 良い例
DATABASE_URL = "postgresql://localhost/stock_db"
MAX_RETRY_COUNT = 3
DEFAULT_INTERVAL = "1d"

# モジュールレベルの設定
VALID_INTERVALS = ['1m', '5m', '15m', '30m', '1h', '1d', '1wk', '1mo']

# 悪い例
database_url = "postgresql://localhost/stock_db"
MaxRetryCount = 3
```

- **全て大文字とアンダースコア（UPPER_SNAKE_CASE）** を使用
- モジュールレベルで定義

### 命名のベストプラクティス

```python
# 良い例
is_valid = True  # 真偽値には is_, has_, can_ などの接頭辞
has_data = False
can_retry = True

total_count = 100  # 数値には count, total, max などの接尾辞
max_retries = 3

stock_list = []  # コレクションには list, dict, set などの接尾辞
symbol_dict = {}

# 悪い例
valid = True
data = False
retry = True
```

- 真偽値には`is_`, `has_`, `can_`などの接頭辞を使用
- コレクションには型を示す接尾辞（`_list`, `_dict`, `_set`）を使用

---

## インポート文

### インポートの順序

```python
# 1. 標準ライブラリ
import os
import sys
from datetime import datetime, date
from typing import Optional, Dict, Any

# 2. サードパーティライブラリ
import pandas as pd
import yfinance as yf
from flask import Flask, jsonify
from sqlalchemy import Column, Integer, String

# 3. ローカルモジュール
from models import StockMaster, BatchExecution
from utils.structured_logger import get_batch_logger
from utils.timeframe_utils import validate_interval
```

1. **標準ライブラリ**
2. **サードパーティライブラリ**
3. **ローカルモジュール**

各グループの間に1行の空行を挿入

### インポートのスタイル

```python
# 良い例
import os
import sys

from typing import Optional, Dict, Any

# 悪い例
import os, sys
from typing import *
```

- 1行に1つのインポート（標準ライブラリ）
- `from ... import`は複数まとめて可
- ワイルドカードインポート（`*`）は避ける

### 絶対インポートと相対インポート

```python
# 推奨: 絶対インポート
from app.models import StockMaster
from app.utils.timeframe_utils import validate_interval

# 相対インポート（同じパッケージ内では可）
from .models import StockMaster
from ..utils.timeframe_utils import validate_interval

# 悪い例
from models import *
```

- **絶対インポート**を推奨
- 相対インポートは同じパッケージ内でのみ使用

---

## 型ヒント

### 基本的な型ヒント

```python
from typing import Optional, Dict, Any, List
import pandas as pd

def fetch_stock_data(
    symbol: str,
    interval: str = '1d',
    period: Optional[str] = None
) -> pd.DataFrame:
    """株価データを取得"""
    pass

def get_stock_info(symbol: str) -> Dict[str, Any]:
    """銘柄情報を取得"""
    return {"code": symbol, "name": "トヨタ"}

def get_symbol_list() -> List[str]:
    """銘柄リストを取得"""
    return ["7203.T", "9984.T"]
```

- 関数の引数と戻り値に型ヒントを記述
- `Optional[T]`は`None`を許容する場合に使用
- 複雑な型は`typing`モジュールを使用

### クラスの型ヒント

```python
from typing import Optional
from datetime import datetime

class BatchExecution:
    """バッチ実行クラス"""

    def __init__(
        self,
        batch_id: int,
        start_time: datetime,
        end_time: Optional[datetime] = None
    ) -> None:
        self.batch_id: int = batch_id
        self.start_time: datetime = start_time
        self.end_time: Optional[datetime] = end_time

    def get_duration(self) -> int:
        """実行時間を取得（秒）"""
        if self.end_time is None:
            return 0
        return int((self.end_time - self.start_time).total_seconds())
```

- クラス属性にも型ヒントを記述
- `__init__`の戻り値は`None`

### 型ヒントのベストプラクティス

```python
# 良い例
def process_data(data: pd.DataFrame) -> pd.DataFrame:
    """データを処理"""
    pass

def validate_symbol(symbol: str) -> bool:
    """銘柄コードを検証"""
    pass

# 悪い例（型ヒントなし）
def process_data(data):
    pass

def validate_symbol(symbol):
    pass
```

- 全ての公開関数・メソッドに型ヒントを記述
- プライベート関数でも可能な限り型ヒントを使用

---

## コメントとドキュメンテーション

### モジュールレベルのdocstring

```python
"""株価データ取得サービス

yfinanceを使用して各時間軸の株価データを取得します。

主な機能:
- Yahoo Financeからの株価データ取得
- 複数の時間軸に対応（1m, 5m, 15m, 30m, 1h, 1d, 1wk, 1mo）
- エラーハンドリングとリトライ機能
"""

import yfinance as yf
import pandas as pd
```

- ファイルの先頭に記述
- モジュールの目的と主な機能を説明
- 日本語で記述

### クラスのdocstring

```python
class StockDataFetcher:
    """株価データ取得クラス

    Yahoo Financeから株価データを取得し、適切な形式に変換します。

    Attributes:
        logger: ロガーインスタンス

    Example:
        >>> fetcher = StockDataFetcher()
        >>> data = fetcher.fetch_stock_data("7203.T", interval="1d")
    """

    def __init__(self):
        """初期化"""
        self.logger = logging.getLogger(__name__)
```

- クラスの目的と主要な機能を説明
- 主要な属性を記述
- 使用例を含めることを推奨

### 関数・メソッドのdocstring

```python
def fetch_stock_data(
    self,
    symbol: str,
    interval: str = '1d',
    period: Optional[str] = None,
    start: Optional[str] = None,
    end: Optional[str] = None
) -> pd.DataFrame:
    """株価データを取得

    Yahoo Financeから指定された銘柄の株価データを取得します。

    Args:
        symbol: 銘柄コード（例: '7203.T'）
        interval: データの時間軸（デフォルト: '1d'）
            有効な値: '1m', '5m', '15m', '30m', '1h', '1d', '1wk', '1mo'
        period: データ取得期間（例: '1mo', '3mo', '1y'）
            startとendが指定されている場合は無視されます
        start: データ取得開始日（YYYY-MM-DD形式）
        end: データ取得終了日（YYYY-MM-DD形式）

    Returns:
        株価データを含むDataFrame
        カラム: ['Open', 'High', 'Low', 'Close', 'Volume']

    Raises:
        StockDataFetchError: データ取得に失敗した場合
        ValueError: 無効なパラメータが指定された場合

    Example:
        >>> fetcher = StockDataFetcher()
        >>> data = fetcher.fetch_stock_data(
        ...     symbol="7203.T",
        ...     interval="1d",
        ...     period="1mo"
        ... )
    """
    pass
```

- **Google Style**に準拠
- セクション: `Args`, `Returns`, `Raises`, `Example`
- 引数の説明は詳細に記述
- 使用例を含める

### インラインコメント

```python
# 良い例
# .T サフィックスを除去して銘柄コードを正規化
code = symbol.replace('.T', '')

# リトライカウントをインクリメント
retry_count += 1

# 悪い例
code = symbol.replace('.T', '')  # .Tを除去
retry_count += 1  # 1を足す
```

- コードの「なぜ」を説明（「何を」ではない）
- 複雑なロジックや非自明な処理に記述
- 日本語で記述

### TODOコメント

```python
# TODO: リトライロジックの改善が必要
# TODO(username): エラーハンドリングを追加 (Issue #123)
# FIXME: メモリリークの可能性あり
# NOTE: この処理は一時的な対応です
```

- `TODO`: 将来実装すべき機能
- `FIXME`: 修正が必要なバグ
- `NOTE`: 重要な注意事項
- 担当者やIssue番号を含めることを推奨

---

## 例外処理

### 例外クラスの定義

```python
# 良い例
class StockDataError(Exception):
    """株価データ関連の基底例外"""
    pass

class StockDataFetchError(StockDataError):
    """データ取得エラー"""
    pass

class DatabaseError(Exception):
    """データベース関連エラー"""
    pass
```

- 独自の例外クラスを定義
- 例外クラス名は`Error`で終わる
- 必要に応じて階層構造を作る

### 例外のキャッチと再送出

```python
# 良い例
try:
    data = fetch_stock_data(symbol)
except ValueError as e:
    logger.error(f"無効な銘柄コード: {symbol}, エラー: {e}")
    raise StockDataFetchError(f"データ取得失敗: {symbol}") from e
except Exception as e:
    logger.exception("予期しないエラーが発生")
    raise

# 悪い例
try:
    data = fetch_stock_data(symbol)
except:
    pass
```

- 具体的な例外をキャッチ
- `except:`（bare except）は避ける
- 例外を握りつぶさない
- 必要に応じてログを出力

### finally句の使用

```python
# 良い例
db_session = SessionLocal()
try:
    # データベース操作
    result = db_session.query(StockMaster).all()
    db_session.commit()
except Exception as e:
    db_session.rollback()
    logger.error(f"データベースエラー: {e}")
    raise
finally:
    db_session.close()
```

- リソースの解放は`finally`句で行う
- コンテキストマネージャー（`with`文）を使用することを推奨

---

## その他のベストプラクティス

### コンテキストマネージャーの使用

```python
# 良い例
with open('data.txt', 'r', encoding='utf-8') as f:
    content = f.read()

with SessionLocal() as session:
    stocks = session.query(StockMaster).all()

# 悪い例
f = open('data.txt', 'r')
content = f.read()
f.close()  # 例外が発生すると閉じられない
```

- ファイルやデータベース接続は`with`文を使用
- リソースの自動解放を保証

### リスト内包表記

```python
# 良い例
stock_codes = [stock.code for stock in stocks if stock.is_active]

squared_numbers = [x ** 2 for x in range(10)]

# 悪い例（可読性が低い）
result = [x ** 2 for x in range(100) if x % 2 == 0 if x % 3 == 0 if x > 50]

# 複雑な場合は通常のループを使用
result = []
for x in range(100):
    if x % 2 == 0 and x % 3 == 0 and x > 50:
        result.append(x ** 2)
```

- シンプルなリスト生成には内包表記を使用
- 複雑になる場合は通常のループを使用

### 比較演算

```python
# 良い例
if value is None:
    pass

if value is not None:
    pass

if not items:  # 空のリスト・辞書・文字列
    pass

if items:  # 要素がある場合
    pass

# 悪い例
if value == None:
    pass

if len(items) == 0:
    pass
```

- `None`との比較は`is`/`is not`を使用
- 空のチェックは`if not items:`を使用

### デフォルト引数

```python
# 良い例
def fetch_data(symbol: str, options: Optional[Dict[str, Any]] = None):
    if options is None:
        options = {}
    # 処理

# 悪い例（ミュータブルなデフォルト引数）
def fetch_data(symbol: str, options: Dict[str, Any] = {}):
    # 処理
```

- ミュータブルなオブジェクト（リスト、辞書など）をデフォルト引数にしない
- `None`をデフォルトにして関数内で初期化

### f-string の使用

```python
# 良い例
symbol = "7203.T"
message = f"銘柄コード: {symbol}"

# 良い例（複雑な式）
message = f"合計: {sum(values)}, 平均: {sum(values) / len(values):.2f}"

# 悪い例
message = "銘柄コード: %s" % symbol
message = "銘柄コード: {}".format(symbol)
```

- Python 3.6以降は**f-string**を使用
- 可読性とパフォーマンスが向上

---

## まとめ

このコーディング規約は、チーム全体で一貫性のあるコードを書くためのガイドラインです。

### 重要なポイント

1. **PEP 8に準拠**する
2. **命名規則を統一**する（snake_case, PascalCase, UPPER_SNAKE_CASE）
3. **型ヒント**を積極的に使用する
4. **docstring**を適切に記述する（日本語で）
5. **例外処理**を適切に行う
6. **可読性**を常に意識する

### ツールによる自動化

コーディング規約の遵守は、以下のツールで自動化できます：

- **フォーマッター**: Black, autopep8
- **Linter**: pylint, flake8, mypy
- **型チェック**: mypy

詳細は[Issue #108 (フォーマッタ・Linterの導入)](https://github.com/TIMMY-WEST/STOCK-INVESTMENT-ANALYZER/issues/108)を参照してください。

---

## 参考文献

- [PEP 8 -- Style Guide for Python Code](https://peps.python.org/pep-0008/)
- [Google Python Style Guide](https://google.github.io/styleguide/pyguide.html)
- [The Hitchhiker's Guide to Python - Code Style](https://docs.python-guide.org/writing/style/)

---

**更新履歴**

- 2025-10-22: 初版作成 (Issue #107)
