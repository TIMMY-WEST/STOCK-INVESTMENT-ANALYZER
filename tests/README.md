# テスト実行ガイド

このディレクトリには、STOCK-INVESTMENT-ANALYZERプロジェクトのテストコードが含まれています。

## ディレクトリ構造

```
tests/
├── unit/           # ユニットテスト（外部依存なし）
├── integration/    # 統合テスト（DB/API連携）
├── e2e/           # E2Eテスト（ブラウザ操作）
├── conftest.py    # 共通フィクスチャ
└── README.md      # このファイル
```

**注意**: 既存のテストは現在のtests/直下に保持されています。新しいディレクトリ構造は段階的な移行のために追加されたもので、既存テストはリファクタリングの安全網として機能します。

## テストレベルの定義

### ユニットテスト（`tests/unit/`）
- **目的**: 個別の関数やクラスの動作を検証
- **特徴**: 外部依存なし、高速、独立性が高い
- **対象**: 純粋な関数、ビジネスロジック、ユーティリティ
- **実行時間**: 数秒以内

### 統合テスト（`tests/integration/`）
- **目的**: 複数のコンポーネント間の連携を検証
- **特徴**: DB、API、外部サービスとの連携をテスト
- **対象**: APIエンドポイント、データベースアクセス、サービス間連携
- **実行時間**: 数秒〜数分

### E2Eテスト（`tests/e2e/`）
- **目的**: ユーザー視点でのシステム全体の動作を検証
- **特徴**: ブラウザ操作、実際のユーザーフローを再現
- **対象**: Webアプリケーション全体、ユーザーインターフェース
- **実行時間**: 数分〜数十分

## テスト実行方法

### 全テスト実行

```bash
pytest tests/
```

### テストレベル別実行

```bash
# ユニットテストのみ
pytest tests/unit/

# 統合テストのみ
pytest tests/integration/

# E2Eテストのみ
pytest tests/e2e/
```

### マーカーを使った実行

```bash
# ユニットテストのみ（マーカー指定）
pytest -m unit

# 統合テストのみ（マーカー指定）
pytest -m integration

# E2Eテストのみ（マーカー指定）
pytest -m e2e

# 実行時間の長いテストを除外
pytest -m "not slow"
```

### カバレッジレポート生成

```bash
# HTMLレポート生成（デフォルトで有効）
pytest tests/

# レポート確認
# htmlcov/index.html をブラウザで開く
```

### 並列実行

```bash
# CPU数に応じて自動的に並列実行
pytest tests/ -n auto
```

### その他のオプション

```bash
# 詳細出力
pytest tests/ -v

# 最初の失敗で停止
pytest tests/ -x

# 最後に失敗したテストのみ再実行
pytest tests/ --lf

# 失敗したテストを最初に実行
pytest tests/ --ff

# 特定のテストファイルのみ実行
pytest tests/test_models.py

# 特定のテスト関数のみ実行
pytest tests/test_models.py::test_function_name
```

## テスト作成ガイドライン

### ファイル命名規則
- テストファイル: `test_*.py` または `*_test.py`
- テストクラス: `Test*`
- テスト関数: `test_*`

### マーカーの使用

```python
import pytest

@pytest.mark.unit
def test_pure_function():
    """ユニットテストの例"""
    assert True

@pytest.mark.integration
def test_database_access():
    """統合テストの例"""
    assert True

@pytest.mark.e2e
def test_user_flow():
    """E2Eテストの例"""
    assert True

@pytest.mark.slow
def test_long_running():
    """実行時間の長いテストの例"""
    assert True

### モジュールレベルマーカー（ファイル単位）

最近のリファクタリングにより、一部のテストファイルにはモジュール全体に対するマーカーを追加しています。
これはファイル単位でマーカーを指定することで、同一ファイル内の全テストをまとめて選択／除外できる利点があります。

例:

```python
# tests/docs/test_docs_quality.py
import pytest

pytestmark = pytest.mark.docs

def test_document_has_title():
    assert True
```

利用可能なモジュールレベルマーカー（プロジェクトで標準化されているもの）:

- `unit` — ユニットテスト（`tests/unit/`）
- `integration` — 統合テスト（`tests/integration/`）
- `e2e` — E2Eテスト（`tests/e2e/`）
- `slow` — 実行時間の長いテスト
- `docs` — ドキュメント品質関連テスト（`tests/docs/`）

これらのマーカーは `pytest.ini` に登録されており、`--strict-markers` オプション下でも問題なく利用できます。

例: ファイル単位でマーカーを利用して docs テストだけを実行する

```bash
pytest -m docs
```
```

### フィクスチャの利用

共通フィクスチャは `conftest.py` で定義されています。

#### Flask関連フィクスチャ

```python
def test_with_client(client):
    """Flaskテストクライアントを使用する例"""
    response = client.get('/api/endpoint')
    assert response.status_code == 200
```

#### データベース関連フィクスチャ

```python
def test_with_mock_db(mock_db_session):
    """モックDBセッションを使用する例（単体テスト向け）"""
    mock_db_session.query.return_value.filter.return_value.first.return_value = None
    result = some_database_function(mock_db_session)
    assert result is None
    mock_db_session.commit.assert_called_once()

def test_with_db_context(test_db_session):
    """DBコンテキストマネージャーを使用する例（統合テスト向け）"""
    with test_db_session as session:
        # セッションを使用した処理
        session.add(some_model)
        session.commit()
```

#### テストデータフィクスチャ

```python
def test_stock_data(sample_stock_data):
    """サンプル株価データを使用する例"""
    assert sample_stock_data["symbol"] == "7203.T"
    assert sample_stock_data["close"] == 1020.0
    # 必要に応じて値を変更
    sample_stock_data["close"] = 2000.0

def test_stock_list(sample_stock_list):
    """複数銘柄データを使用する例"""
    assert len(sample_stock_list) == 3
    for stock in sample_stock_list:
        process_stock(stock)

def test_dataframe(sample_dataframe):
    """DataFrameを使用する例"""
    assert not sample_dataframe.empty
    assert "Close" in sample_dataframe.columns
    assert sample_dataframe["Close"].iloc[0] == 1020.0
```

#### モックヘルパーフィクスチャ

```python
def test_yfinance_ticker(mock_yfinance_ticker):
    """Yahoo Finance Tickerモックを使用する例"""
    import yfinance as yf

    # yf.Ticker()は自動的にモックされる
    ticker = yf.Ticker("7203.T")
    data = ticker.history(period="1d")

    assert not data.empty
    assert "Close" in data.columns
    mock_yfinance_ticker.assert_called_once_with("7203.T")

def test_yfinance_download(mock_yfinance_download):
    """Yahoo Finance downloadモックを使用する例"""
    import yfinance as yf

    data = yf.download(["7203.T", "6758.T"], period="1d")

    assert not data.empty
    mock_yfinance_download.assert_called_once()
```

#### 利用可能なフィクスチャ一覧

| フィクスチャ名 | 用途 | スコープ |
|---|---|---|
| `app` | Flaskアプリケーション | function |
| `client` | Flaskテストクライアント | function |
| `mock_db_session` | モックDBセッション（単体テスト向け） | function |
| `test_db_session` | DBコンテキストマネージャー（統合テスト向け） | function |
| `sample_stock_data` | サンプル株価データ（辞書） | function |
| `sample_stock_list` | 複数銘柄データリスト | function |
| `sample_dataframe` | サンプル株価DataFrame | function |
| `mock_yfinance_ticker` | Yahoo Finance Tickerモック | function |
| `mock_yfinance_download` | Yahoo Finance downloadモック | function |

## カバレッジ目標

- **全体**: 70%以上（必須）
- **新規コード**: 80%以上（推奨）
- **重要なビジネスロジック**: 90%以上（推奨）

## トラブルシューティング

### テストが失敗する場合

1. **依存関係の確認**
   ```bash
   pip install -e ".[test]"
   ```

2. **データベースの初期化**
   ```bash
   python scripts/reset_db.py
   ```

3. **環境変数の設定**
   `.env`ファイルが正しく設定されているか確認

### カバレッジが低い場合

```bash
# カバレッジレポートで欠けている行を確認
pytest tests/ --cov-report=term-missing
```

## CI/CD統合

GitHub Actionsでのテスト実行は自動化されています。
詳細は `.github/workflows/` を参照してください。

## 参考資料

- [pytest公式ドキュメント](https://docs.pytest.org/)
- [pytest-cov](https://pytest-cov.readthedocs.io/)
- [pytest-mock](https://pytest-mock.readthedocs.io/)
- [テスト戦略ドキュメント](../docs/testing/test_strategy.md)

## 問い合わせ

テストに関する質問や提案は、GitHubのIssueで受け付けています。
