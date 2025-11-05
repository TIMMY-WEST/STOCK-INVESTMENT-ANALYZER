# ⚠️ 非推奨: このドキュメントは統合されました

**このドキュメントは 2025年11月2日 に非推奨となりました。**

代わりに以下の統合ドキュメントを参照してください:
- **[テスト標準仕様書 (v3.0.0)](../standards/testing-standards.md)** ← 統合テスト含む全テスト方針
---
# API統合テストガイド (ARCHIVED)

本ドキュメントでは、株価投資分析システムのAPI統合テストの実装方針とベストプラクティスについて説明します。

## 目次

1. [概要](#概要)
2. [テストファイル構成](#テストファイル構成)
3. [テスト実行方法](#テスト実行方法)
4. [テストケース分類](#テストケース分類)
5. [モッキング戦略](#モッキング戦略)
6. [ベストプラクティス](#ベストプラクティス)

## 概要

API統合テストは、APIエンドポイントの動作を検証し、リグレッションを防止するために実装されています。

### テストの目的

- **品質向上**: 各エンドポイントが仕様通りに動作することを保証
- **リグレッション防止**: 既存機能の破壊を早期に検出
- **ドキュメント化**: テストコードが実質的なAPI仕様書として機能

## テストファイル構成

統合テストは`tests/integration/`ディレクトリに配置されています:

```
tests/integration/
├── test_stock_data_api_integration.py      # 株価データAPI統合テスト
├── test_bulk_data_api_integration.py        # バルクデータAPI統合テスト
└── test_stock_master_system_api_integration.py  # 銘柄マスター・システム監視API統合テスト
```

### ファイル別のテスト対象

#### 1. test_stock_data_api_integration.py

**対象エンドポイント:**
- `POST /api/stocks/data` - 株価データ取得
- `GET /api/stocks` - 株価データ一覧取得
- `GET /api/stocks/{stock_id}` - 株価データ詳細取得
- `PUT /api/stocks/{stock_id}` - 株価データ更新
- `DELETE /api/stocks/{stock_id}` - 株価データ削除
- `POST /api/stocks/test` - テスト用株価データ作成

**テストクラス:**
- `TestStockDataAPIIntegration`: 基本的な機能テスト
- `TestStockDataAPIResponseFormat`: レスポンス形式の検証
- `TestStockDataAPIEdgeCases`: エッジケーステスト

#### 2. test_bulk_data_api_integration.py

**対象エンドポイント:**
- `POST /api/bulk-data/jobs` - バルクジョブ作成
- `GET /api/bulk-data/jobs/{job_id}` - ジョブステータス取得
- `POST /api/bulk-data/jobs/{job_id}/stop` - ジョブ停止
- `GET /api/bulk-data/jpx-sequential/symbols` - JPX銘柄一覧取得
- `POST /api/bulk-data/jpx-sequential/jobs` - JPXバルクジョブ作成

**テストクラス:**
- `TestBulkDataJobsAPI`: バルクジョブ管理のテスト
- `TestJPXSequentialAPI`: JPX銘柄一括取得のテスト
- `TestBulkDataAPIErrorHandling`: エラーハンドリングテスト
- `TestBulkDataAPIResponseFormat`: レスポンス形式の検証
- `TestBulkDataAPIAuthentication`: 認証機能のテスト

#### 3. test_stock_master_system_api_integration.py

**対象エンドポイント:**
- `POST /api/stock-master/` - 銘柄マスター更新
- `GET /api/stock-master/` - 銘柄マスター一覧取得
- `GET /api/stock-master/status` - 銘柄マスターステータス取得
- `GET /api/system/database/connection` - DB接続テスト
- `GET /api/system/external-api/connection` - 外部API接続テスト
- `GET /api/system/health` - ヘルスチェック

**テストクラス:**
- `TestStockMasterAPI`: 銘柄マスターAPI のテスト
- `TestSystemMonitoringAPI`: システム監視APIのテスト
- `TestSystemMonitoringAPIEdgeCases`: エッジケーステスト
- `TestCombinedAPIIntegration`: 複合API統合テスト

## テスト実行方法

### 全統合テストの実行

```bash
# すべての統合テストを実行
pytest tests/integration/ -v

# 特定のテストファイルのみ実行
pytest tests/integration/test_stock_data_api_integration.py -v

# 特定のテストクラスのみ実行
pytest tests/integration/test_stock_data_api_integration.py::TestStockDataAPIIntegration -v

# 特定のテストメソッドのみ実行
pytest tests/integration/test_stock_data_api_integration.py::TestStockDataAPIIntegration::test_fetch_stock_data_success_response -v
```

### カバレッジレポート付き実行

```bash
# カバレッジを測定して実行
pytest tests/integration/ --cov=app --cov-report=html --cov-report=term

# カバレッジレポートの確認
# htmlcov/index.html をブラウザで開く
```

### 並列実行

```bash
# 複数のCPUコアを使用して高速化
pytest tests/integration/ -n auto
```

## テストケース分類

### 1. 成功系テスト (Happy Path)

正常な入力に対して期待通りのレスポンスが返ることを検証します。

```python
def test_fetch_stock_data_success_response(self, client, mocker):
    """POST /api/stocks/data - 成功時のレスポンス検証."""
    # モックデータの準備
    mock_df = pd.DataFrame(...)
    mocker.patch("yfinance.Ticker", ...)

    # APIコール
    response = client.post("/api/stocks/data", json={...})

    # アサーション
    assert response.status_code == 200
    assert data["status"] == "success"
```

### 2. エラーケーステスト

異常な入力や外部サービスの障害時の挙動を検証します。

```python
def test_fetch_stock_data_validation_error(self, client, mocker):
    """POST /api/stocks/data - バリデーションエラーのテスト."""
    # 空のDataFrameを返すモック
    mock_df = pd.DataFrame()
    mocker.patch("yfinance.Ticker", ...)

    response = client.post("/api/stocks/data", json={...})

    # エラーレスポンスの検証
    assert data["status"] == "error"
    assert "message" in data
```

### 3. 認証テスト

APIキーによる認証機能を検証します。

```python
def test_create_bulk_job_unauthorized(self, client):
    """POST /api/bulk-data/jobs - 認証エラー."""
    response = client.post(
        "/api/bulk-data/jobs",
        json={"symbols": ["7203.T"]},
        # X-API-KEYヘッダーを付けない
    )

    assert response.status_code == 401
```

### 4. ページネーションテスト

`limit`と`offset`パラメータの動作を検証します。

```python
def test_get_stocks_pagination(self, client, mocker):
    """GET /api/stocks - ページネーションのテスト."""
    response = client.get("/api/stocks?limit=10&offset=0")

    assert response.status_code == 200
    assert "data" in data
```

### 5. レスポンス形式検証

APIレスポンスの構造とデータ型を検証します。

```python
def test_success_response_structure(self, client, mocker):
    """成功時のレスポンス構造検証."""
    response = client.get("/api/stocks")
    data = response.get_json()

    # 成功時の必須フィールド
    assert "status" in data
    assert data["status"] == "success"
    assert "data" in data
```

## モッキング戦略

### 外部サービスのモック

外部APIやデータベースは常にモック化して、テストの独立性と高速化を図ります。

#### yfinance (Yahoo Finance API) のモック

```python
import pandas as pd
from datetime import datetime

# DataFrameのモック
mock_df = pd.DataFrame(
    {
        "Open": [1000.0],
        "High": [1050.0],
        "Low": [990.0],
        "Close": [1020.0],
        "Volume": [1000000],
    },
    index=pd.DatetimeIndex([datetime(2025, 1, 1)]),
)

mock_ticker = mocker.Mock()
mock_ticker.history.return_value = mock_df
mocker.patch("yfinance.Ticker", return_value=mock_ticker)
```

#### データベースCRUDのモック

```python
# 取得の成功パターン
mock_stock = mocker.Mock()
mock_stock.to_dict.return_value = {
    "id": 1,
    "symbol": "7203.T",
    ...
}

mocker.patch("app.models.StockDailyCRUD.get_by_id", return_value=mock_stock)

# 存在しない場合(404)
mocker.patch("app.models.StockDailyCRUD.get_by_id", return_value=None)

# 削除の成功
mocker.patch("app.models.StockDailyCRUD.delete", return_value=True)
```

### フィクスチャの活用

共通のセットアップは`@pytest.fixture`を使用します。

```python
@pytest.fixture
def client():
    """テスト用のFlaskクライアント."""
    flask_app.config["TESTING"] = True
    with flask_app.test_client() as client:
        yield client

@pytest.fixture(autouse=True)
def setup_env(monkeypatch):
    """テスト環境のセットアップ."""
    monkeypatch.setenv("API_KEY", "test-key")
    monkeypatch.setenv("RATE_LIMIT_PER_MINUTE", "10")
```

## ベストプラクティス

### 1. テストの独立性

各テストは独立して実行可能であること:

- テスト間で状態を共有しない
- モックを各テストで明示的に設定
- `autouse=True`のフィクスチャで環境をクリーンに保つ

### 2. アサーションの明確性

何をテストしているか明確に:

```python
# Good: 何を検証しているかが明確
assert response.status_code == 200
assert data["success"] is True
assert "message" in data

# Bad: 曖昧なアサーション
assert response
assert data
```

### 3. ドキュメンテーション

docstringで各テストの目的を明記:

```python
def test_fetch_stock_data_success_response(self, client, mocker):
    """POST /api/stocks/data - 成功時のレスポンス検証.

    正常な株価データ取得リクエストに対して、
    200 OKと正しいフォーマットのレスポンスが返ることを検証する。
    """
```

### 4. テストデータの管理

テストデータは意味のある値を使用:

```python
# Good: 実際の銘柄コードを使用
{"symbol": "7203.T", "period": "1mo"}

# Bad: 意味のない値
{"symbol": "XXX", "period": "YYY"}
```

### 5. エラーメッセージの検証

エラー時はステータスコードだけでなくメッセージも検証:

```python
assert response.status_code == 404
data = response.get_json()
assert data["success"] is False
assert "error" in data
assert "message" in data
assert "見つかりません" in data["message"]  # 具体的な内容も検証
```

### 6. 複数のステータスコードを許容

実装の詳細に依存しない柔軟なテスト:

```python
# 実装によって200または202が返る可能性がある
assert response.status_code in [200, 202]
```

## まとめ

API統合テストは、システムの品質を保証する重要な要素です。本ガイドに従ってテストを追加・修正することで、保守性の高いテストコードを実現できます。

### 次のステップ

- [ ] カバレッジを80%以上に維持
- [ ] CI/CDパイプラインへの組み込み
- [ ] E2Eテストの追加検討
- [ ] パフォーマンステストの実装

## 関連ドキュメント

- [テスト戦略全体像](../architecture/testing_strategy.md)
- [ユニットテストガイド](./unit_testing_guide.md)
- [E2Eテストガイド](./e2e_testing_guide.md)
