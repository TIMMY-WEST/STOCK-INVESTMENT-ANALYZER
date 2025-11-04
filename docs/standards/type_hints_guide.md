# 型ヒント使用ガイド

このドキュメントでは、STOCK-INVESTMENT-ANALYZERプロジェクトにおける型ヒントの記述ガイドラインと段階的導入方針について説明します。

## 目次

1. [概要](#概要)
2. [型ヒントの基本](#型ヒントの基本)
3. [記述ガイドライン](#記述ガイドライン)
4. [段階的導入方針](#段階的導入方針)
5. [mypy設定](#mypy設定)
6. [実装例](#実装例)
7. [よくある問題と解決方法](#よくある問題と解決方法)
---
## 概要

型ヒントは、Pythonコードの可読性と保守性を向上させる重要な機能です。本プロジェクトでは、mypyを使用した型チェックを導入し、段階的に型ヒントを追加していきます。

### 導入の目的

- **コードの可読性向上**: 関数の引数と戻り値の型が明確になる
- **開発効率の向上**: IDEでの補完機能が強化される
- **バグの早期発見**: 型の不整合を実行前に検出できる
- **リファクタリングの安全性**: 型情報により安全な変更が可能
---
## 型ヒントの基本

### 基本的な型の記述

```python
from typing import List, Dict, Optional, Union, Tuple, Any
from datetime import datetime
from decimal import Decimal

# 基本型
def get_stock_price(symbol: str) -> float:
    pass

# リスト型
def get_stock_symbols() -> List[str]:
    pass

# 辞書型
def get_stock_data(symbol: str) -> Dict[str, Any]:
    pass

# オプショナル型（None許可）
def find_stock(symbol: str) -> Optional[Dict[str, Any]]:
    pass

# ユニオン型（複数型許可）
def process_data(data: Union[str, Dict[str, Any]]) -> bool:
    pass

# タプル型
def get_price_range(symbol: str) -> Tuple[float, float]:
    pass
```

### クラスの型ヒント

```python
from typing import ClassVar
from sqlalchemy import Column, String, Decimal
from app.models import db

class StockData:
    # クラス変数の型ヒント
    table_name: ClassVar[str] = "stocks_1d"

    def __init__(self, symbol: str, price: Decimal) -> None:
        self.symbol: str = symbol
        self.price: Decimal = price

    def get_symbol(self) -> str:
        return self.symbol

    def update_price(self, new_price: Decimal) -> None:
        self.price = new_price
```
---
## 記述ガイドライン

### 1. 必須の型ヒント

以下の場合は型ヒントを必須とします：

- **公開API関数**: 他のモジュールから呼び出される関数
- **クラスの公開メソッド**: `__init__`メソッドを含む
- **複雑な戻り値**: 辞書、リスト、タプルなどの複合型
- **外部ライブラリとの境界**: データベース、API呼び出しなど

```python
# ✅ 良い例
def fetch_stock_data(symbol: str, timeframe: str) -> Dict[str, Any]:
    """株価データを取得する"""
    pass

# ❌ 避けるべき例
def fetch_stock_data(symbol, timeframe):
    """株価データを取得する"""
    pass
```

### 2. 推奨の型ヒント

以下の場合は型ヒントを推奨します：

- **内部関数**: モジュール内でのみ使用される関数
- **ヘルパー関数**: ユーティリティ関数
- **変数の型が不明確な場合**: 特に複合型の変数

```python
# ✅ 推奨
def _calculate_moving_average(prices: List[float], period: int) -> float:
    """移動平均を計算する内部関数"""
    pass

# 複雑な変数の型ヒント
stock_data: Dict[str, List[Decimal]] = {}
```

### 3. 型ヒントの省略可能なケース

以下の場合は型ヒントを省略できます：

- **明らかな型の場合**: `count = 0`、`name = "example"`など
- **一時的な変数**: ループ変数、短いスコープの変数
- **プライベート関数**: 単純な処理のみを行う関数

```python
# ✅ 省略可能
count = 0  # int型が明らか
for item in items:  # itemの型は文脈から明らか
    process(item)
```
---
## 段階的導入方針

### フェーズ1: 新規コードへの適用（即座に開始）

- **新規作成するすべてのファイル**に型ヒントを追加
- **新規追加する関数・メソッド**に型ヒントを追加
- **既存コードの修正時**に可能な範囲で型ヒントを追加

### フェーズ2: 重要モジュールの型ヒント追加（1-2週間後）

優先順位の高いモジュールから順次型ヒントを追加：

1. **app/models.py**: データベースモデル
2. **app/services/**: ビジネスロジック
3. **app/api/**: API エンドポイント
4. **app/utils/**: ユーティリティ関数

### フェーズ3: 全体の型ヒント完成（1-2ヶ月後）

- **app/static/**: フロントエンド関連（必要に応じて）
- **tests/**: テストコード
- **scripts/**: スクリプトファイル

### 導入時の注意点

- **一度に大量の変更を避ける**: 小さな単位で段階的に実施
- **テストの実行**: 型ヒント追加後は必ずテストを実行
- **mypy エラーの段階的解決**: 厳密度を徐々に上げる
---
## mypy設定

プロジェクトのmypy設定は`pyproject.toml`で管理されています：

```toml
[tool.mypy]
python_version = "3.8"
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = false  # 段階的導入のため初期はfalse
disallow_incomplete_defs = false  # 段階的導入のため初期はfalse
check_untyped_defs = true
no_implicit_optional = true
warn_redundant_casts = true
warn_unused_ignores = true
warn_no_return = true
warn_unreachable = true
strict_optional = true
pretty = true
show_error_codes = true
show_column_numbers = true
show_error_context = true

# 除外ディレクトリ
exclude = [
    "venv",
    ".venv",
    "migrations",
    "build",
    "dist",
]

# サードパーティライブラリの型スタブがない場合のエラーを無視
[[tool.mypy.overrides]]
module = [
    "yfinance.*",
    "selenium.*",
    "webdriver_manager.*",
    "eventlet.*",
    "flask_socketio.*",
]
ignore_missing_imports = true
```

### mypy実行コマンド

```bash
# プロジェクト全体をチェック
mypy app/

# 特定のファイルをチェック
mypy app/models.py

# 詳細な出力でチェック
mypy --show-error-codes --show-column-numbers app/
```
---
## 実装例

### データベースモデルの型ヒント例

```python
from typing import Optional, Dict, Any, List
from datetime import datetime
from decimal import Decimal
from sqlalchemy import Column, String, DateTime, Numeric, BigInteger
from app.models import db

class StockData1d(db.Model):
    __tablename__ = 'stocks_1d'

    id: Column[int] = Column(BigInteger, primary_key=True)
    symbol: Column[str] = Column(String(20), nullable=False)
    date: Column[datetime] = Column(DateTime, nullable=False)
    open: Column[Decimal] = Column(Numeric(10, 2), nullable=False)
    high: Column[Decimal] = Column(Numeric(10, 2), nullable=False)
    low: Column[Decimal] = Column(Numeric(10, 2), nullable=False)
    close: Column[Decimal] = Column(Numeric(10, 2), nullable=False)
    volume: Column[int] = Column(BigInteger, nullable=False)

    def __init__(self, symbol: str, date: datetime, open_price: Decimal,
                 high: Decimal, low: Decimal, close: Decimal, volume: int) -> None:
        self.symbol = symbol
        self.date = date
        self.open = open_price
        self.high = high
        self.low = low
        self.close = close
        self.volume = volume

    def to_dict(self) -> Dict[str, Any]:
        """モデルを辞書形式に変換"""
        return {
            'id': self.id,
            'symbol': self.symbol,
            'date': self.date.isoformat() if self.date else None,
            'open': float(self.open) if self.open else None,
            'high': float(self.high) if self.high else None,
            'low': float(self.low) if self.low else None,
            'close': float(self.close) if self.close else None,
            'volume': self.volume
        }
```

### サービスクラスの型ヒント例

```python
from typing import List, Dict, Any, Optional, Union
from datetime import datetime
import yfinance as yf
from app.models import StockData1d

class StockDataService:

    def __init__(self) -> None:
        self.cache: Dict[str, Any] = {}

    def fetch_stock_data(self, symbol: str, period: str = "1d") -> Optional[Dict[str, Any]]:
        """Yahoo Financeから株価データを取得"""
        try:
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period=period)

            if hist.empty:
                return None

            return self._convert_to_dict(hist)
        except Exception as e:
            print(f"Error fetching data for {symbol}: {e}")
            return None

    def _convert_to_dict(self, hist_data: Any) -> Dict[str, List[float]]:
        """pandas DataFrameを辞書形式に変換"""
        return {
            'open': hist_data['Open'].tolist(),
            'high': hist_data['High'].tolist(),
            'low': hist_data['Low'].tolist(),
            'close': hist_data['Close'].tolist(),
            'volume': hist_data['Volume'].tolist()
        }

    def save_stock_data(self, symbol: str, data: Dict[str, Any]) -> bool:
        """株価データをデータベースに保存"""
        try:
            # データベース保存ロジック
            return True
        except Exception as e:
            print(f"Error saving data: {e}")
            return False
```

### API エンドポイントの型ヒント例

```python
from typing import Dict, Any, Tuple
from flask import Flask, request, jsonify, Response
from app.services.stock_data_service import StockDataService

app = Flask(__name__)
service = StockDataService()

@app.route('/api/stock/<symbol>')
def get_stock_data(symbol: str) -> Tuple[Response, int]:
    """株価データを取得するAPIエンドポイント"""
    try:
        period: str = request.args.get('period', '1d')
        data: Optional[Dict[str, Any]] = service.fetch_stock_data(symbol, period)

        if data is None:
            return jsonify({'error': 'Stock data not found'}), 404

        return jsonify(data), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/stock/<symbol>', methods=['POST'])
def save_stock_data(symbol: str) -> Tuple[Response, int]:
    """株価データを保存するAPIエンドポイント"""
    try:
        data: Dict[str, Any] = request.get_json()
        success: bool = service.save_stock_data(symbol, data)

        if success:
            return jsonify({'message': 'Data saved successfully'}), 201
        else:
            return jsonify({'error': 'Failed to save data'}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500
```
---
## よくある問題と解決方法

### 1. サードパーティライブラリの型エラー

**問題**: `yfinance`や`selenium`などのライブラリで型エラーが発生

**解決方法**: `pyproject.toml`の`[[tool.mypy.overrides]]`セクションに追加

```toml
[[tool.mypy.overrides]]
module = ["yfinance.*", "selenium.*"]
ignore_missing_imports = true
```

### 2. 複雑な型の記述

**問題**: ネストした辞書やリストの型が複雑

**解決方法**: `TypedDict`や`NamedTuple`を使用

```python
from typing import TypedDict, List

class StockDataDict(TypedDict):
    symbol: str
    price: float
    volume: int
    timestamp: str

def process_stocks(stocks: List[StockDataDict]) -> bool:
    pass
```

### 3. 動的な型の処理

**問題**: 実行時に型が決まる場合

**解決方法**: `Union`型や`Any`型を適切に使用

```python
from typing import Union, Any

def process_data(data: Union[str, int, Dict[str, Any]]) -> Any:
    if isinstance(data, str):
        return data.upper()
    elif isinstance(data, int):
        return data * 2
    else:
        return data
```

### 4. 段階的導入時のエラー

**問題**: 既存コードに型ヒントを追加するとエラーが多発

**解決方法**: `# type: ignore`コメントを一時的に使用

```python
def legacy_function(data):  # type: ignore
    # 既存のコード（後で型ヒントを追加予定）
    pass
```
---
## 参考資料

- [PEP 484 - Type Hints](https://www.python.org/dev/peps/pep-0484/)
- [mypy公式ドキュメント](https://mypy.readthedocs.io/)
- [typing モジュール公式ドキュメント](https://docs.python.org/3/library/typing.html)
- [Real Python - Python Type Checking](https://realpython.com/python-type-checking/)
---
## 更新履歴

- 2024-01-XX: 初版作成（Issue #109対応）
