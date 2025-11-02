# テスト規約と戦略

## 📋 目次

- [概要](#概要)
- [テストの目的と原則](#テストの目的と原則)
- [テストレベルの定義](#テストレベルの定義)
- [テストカバレッジ目標](#テストカバレッジ目標)
- [テスト命名規則](#テスト命名規則)
- [テストコーディング規約](#テストコーディング規約)
- [テスト実行とCI/CD](#テスト実行とcicd)
- [pytest設定とプラグイン](#pytest設定とプラグイン)
- [ベストプラクティス](#ベストプラクティス)

---

## 概要

**最終更新**: 2025-11-02
**文書バージョン**: v3.0.0
**AI優先度**: 高

本ドキュメントは、STOCK-INVESTMENT-ANALYZERプロジェクトにおけるテストの規約と戦略を統合的に定義します。
`testing_guide.md`、`testing_strategy.md`、`test_coverage_report.md`の内容を統合し、実装と整合性の取れた単一のリファレンスとして機能します。

### 関連ドキュメント
- [コーディング規約](coding-standards.md) - 一般的なコーディング規約
- [Git/GitHub運用ルール](git-workflow.md) - 開発フロー全体
- [CI/CDパイプライン設定](../ci-cd/pipeline-config.md) - CI/CD詳細
- [トラブルシューティング](../guides/troubleshooting.md) - 問題解決

---

## テストの目的と原則

### テストの目的

1. **品質保証**: コードの正しい動作を保証する
2. **回帰防止**: 既存機能の破壊を早期に発見する
3. **ドキュメント**: コードの振る舞いを示すドキュメントとして機能する
4. **設計改善**: テストしやすいコードは良い設計である
5. **開発速度の向上**: 自動テストにより手動確認の時間を削減し、開発サイクルを加速する

### FIRST原則

テストは以下の原則に従うべきです:

- **F**ast (高速): テストは迅速に実行されるべき
- **I**ndependent (独立): テストは互いに独立しているべき
- **R**epeatable (再現可能): 同じ条件で同じ結果を返すべき
- **S**elf-validating (自己検証): テスト結果は明確に成功/失敗を示すべき
- **T**imely (適時): テストはコードと同時に書くべき

### AAAパターン

全てのテストは以下のパターンに従うこと:

- **A**rrange (準備): テストに必要なデータ・状態を準備
- **A**ct (実行): テスト対象の処理を実行
- **A**ssert (検証): 期待される結果を検証

```python
import pytest

pytestmark = pytest.mark.unit


def test_stock_daily_repr_with_valid_data():
    """StockDailyモデルの文字列表現を検証する"""
    # Arrange (準備)
    stock = StockDaily()
    stock.symbol = "7203.T"
    stock.date = date(2024, 9, 13)
    stock.close = Decimal("2500.00")

    # Act (実行)
    result = str(stock)

    # Assert (検証)
    expected = "<Stocks1d(symbol='7203.T', date='2024-09-13', close=2500.00)>"
    assert result == expected
```

---

## テストレベルの定義

### 1. ユニットテスト (Unit Test)

**目的**: 個々の関数・メソッド・クラスの動作を検証

**スコープ**:
- 単一の関数またはメソッド
- 外部依存を持たない、またはモック化する
- データベース、ファイルシステム、外部APIは使用しない
- 実行時間: ミリ秒単位

**マーカー**: `pytest.mark.unit`

**配置**: `tests/unit/`

```python
import pytest
from decimal import Decimal
from datetime import date
from models import StockDaily

pytestmark = pytest.mark.unit


def test_stock_daily_repr():
    """StockDailyモデルの文字列表現を検証"""
    # Arrange
    stock = StockDaily()
    stock.symbol = "7203.T"
    stock.date = date(2024, 9, 13)
    stock.close = Decimal("2500.00")

    # Act
    result = str(stock)

    # Assert
    expected = "<Stocks1d(symbol='7203.T', date='2024-09-13', close=2500.00)>"
    assert result == expected
```

### 2. 統合テスト (Integration Test)

**目的**: 複数のコンポーネント間の連携動作を検証

**スコープ**:
- 複数のクラス・モジュール間の連携
- データベースとの連携
- 外部APIとの連携（モックまたはテスト環境）
- 実行時間: 秒単位

**マーカー**: `pytest.mark.integration`

**配置**: `tests/integration/`

```python
import pytest
from app import app
from models import Base, StockDaily
from services.stock_data_service import StockDataService

pytestmark = pytest.mark.integration


def test_stock_data_fetch_and_save(app, db_session):
    """株価データ取得とDB保存の結合テスト"""
    # Arrange
    service = StockDataService()
    symbol = "7203.T"
    period = "5d"
    interval = "1d"

    # Act
    result = service.fetch_and_save_stock_data(
        symbol=symbol,
        period=period,
        interval=interval
    )

    # Assert
    assert result["success"] is True
    saved_data = db_session.query(StockDaily).filter_by(
        symbol=symbol
    ).all()
    assert len(saved_data) > 0
```

### 3. E2Eテスト (End-to-End Test)

**目的**: ユーザー視点での全体の動作を検証

**スコープ**:
- ブラウザ操作を含むフルスタックテスト
- 実際のユーザーシナリオを再現
- UIからデータベースまでの全体フロー
- 実行時間: 分単位

**マーカー**: `pytest.mark.e2e`

**配置**: `tests/e2e/`

```python
import pytest
from selenium import webdriver

pytestmark = pytest.mark.e2e


def test_stock_data_display_flow(selenium_driver):
    """株価データ表示フローのE2Eテスト"""
    # Arrange
    driver = selenium_driver
    driver.get("http://localhost:5000")

    # Act
    symbol_input = driver.find_element(By.ID, "symbol-input")
    symbol_input.send_keys("7203.T")
    fetch_button = driver.find_element(By.ID, "fetch-button")
    fetch_button.click()

    # Assert
    wait = WebDriverWait(driver, 10)
    table = wait.until(
        lambda d: d.find_element(By.ID, "stock-data-table")
    )
    assert table.is_displayed()
```

---

## テストカバレッジ目標

### カバレッジ基準

| レベル               | 最低カバレッジ | 推奨カバレッジ |
| -------------------- | -------------- | -------------- |
| **プロジェクト全体** | **70%**        | 80%            |
| **重要モジュール**   | 80%            | 90%            |
| **ビジネスロジック** | 90%            | 95%            |
| **ユーティリティ**   | 70%            | 80%            |

### 重要モジュールの定義

以下のモジュールは、システムの中核を担うため、高いカバレッジを維持します:

- **`app/services/`**: ビジネスロジックを含むサービス層
- **`app/models.py`**: データモデル定義
- **`app/utils/`**: 共通ユーティリティ関数
- **`app/api/`**: APIエンドポイント

### 現在の状況（2025-11-01時点）

- **総カバレッジ**: 69%
- **テスト数**: 107テスト（全合格）
- **ステートメント数**: 1,394
- **未カバー**: 426

#### サービス別カバレッジ

| サービス                 | カバレッジ | 状態       |
| ------------------------ | ---------- | ---------- |
| scheduler.py             | 97%        | ✅ 優秀     |
| validator.py             | 92%        | ✅ 優秀     |
| saver.py                 | 87%        | ✅ 優秀     |
| fetcher.py               | 85%        | ✅ 優秀     |
| stock_batch_processor.py | 83%        | ✅ 良好     |
| converter.py             | 80%        | ✅ 良好     |
| jpx_stock_service.py     | 76%        | ✅ 良好     |
| bulk_service.py          | 61%        | ⚠️ 改善推奨 |
| error_handler.py         | 60%        | ⚠️ 改善推奨 |
| orchestrator.py          | 49%        | ⚠️ 要改善   |
| batch_service.py         | 22%        | ❌ 要改善   |

### カバレッジ測定方法

```bash
# カバレッジレポート生成（HTML形式）
pytest --cov=app --cov-report=html --cov-report=term

# HTML形式のレポート確認
# htmlcov/index.html をブラウザで開く

# ターミナルでカバレッジ確認（未テスト行表示）
pytest --cov=app --cov-report=term-missing

# 最低カバレッジ設定（70%未満の場合、テスト失敗）
pytest --cov --cov-fail-under=70
```

---

## テスト命名規則

### ファイル命名規則

- **形式**: `test_<モジュール名>.py`
- **例**:
  - `test_stock_data_service.py`
  - `test_models.py`
  - `test_bulk_data_service.py`

### クラス命名規則（クラスベーステストの場合）

- **形式**: `Test<クラス名>`
- **例**:
  - `class TestStockDataService`
  - `class TestStockDaily`

### 関数命名規則

- **形式**: `test_<機能>_<条件>_<期待結果>`
- **例**:
  - `test_fetch_stock_data_with_valid_symbol_returns_success()`
  - `test_save_stock_data_with_duplicate_record_raises_error()`
  - `test_calculate_moving_average_with_empty_data_returns_none()`

### 命名の良い例と悪い例

```python
# ❌ 悪い例: 何をテストしているか不明瞭
def test_1():
    pass

def test_stock():
    pass

# ✅ 良い例: テスト内容が明確
def test_stock_daily_model_creates_instance_with_valid_data():
    pass

def test_fetch_stock_data_with_invalid_symbol_returns_error():
    pass

def test_calculate_sma_with_period_greater_than_data_length_returns_none():
    pass
```

---

## テストコーディング規約

### 1. モジュールレベルマーカーの使用

**全てのテストファイルの先頭に適切なマーカーを記述すること**:

```python
import pytest

# ユニットテスト
pytestmark = pytest.mark.unit

# 統合テスト
pytestmark = pytest.mark.integration

# E2Eテスト
pytestmark = pytest.mark.e2e
```

### 2. AAAパターンの徹底

全てのテストはAAA (Arrange-Act-Assert) パターンに従うこと:

```python
def test_example():
    """テストの説明"""
    # Arrange (準備)
    # テストに必要なデータ・状態を準備

    # Act (実行)
    # テスト対象の処理を実行

    # Assert (検証)
    # 期待される結果を検証
```

### 3. Docstringの記述

全てのテスト関数に明確なdocstringを記述すること:

```python
def test_fetch_stock_data_with_valid_symbol_returns_success():
    """正常な銘柄コードでデータ取得が成功することを検証

    有効な銘柄コード（例: 7203.T）を使用してYahoo Finance APIから
    株価データを取得し、成功レスポンスが返されることを確認する。
    """
    pass
```

### 4. フィクスチャの活用

共通のセットアップは`conftest.py`でフィクスチャとして定義すること:

```python
# tests/conftest.py
import pytest
from app import app as flask_app

@pytest.fixture(scope="session")
def app():
    """Flaskアプリケーションフィクスチャ"""
    flask_app.config["TESTING"] = True
    return flask_app

@pytest.fixture(scope="function")
def db_session(app):
    """データベースセッションフィクスチャ"""
    # セットアップ
    session = create_session()
    yield session
    # クリーンアップ
    session.close()
```

### 5. モックの適切な使用

外部依存は必ずモック化すること:

```python
def test_fetch_stock_data_with_api_error(mocker):
    """外部API呼び出しをモック化してエラーハンドリングを検証"""
    # モックの設定
    mock_yfinance = mocker.patch('yfinance.Ticker')
    mock_ticker = Mock()
    mock_ticker.history.side_effect = Exception("API Error")
    mock_yfinance.return_value = mock_ticker

    service = StockDataService()
    result = service.fetch_stock_data(symbol="7203.T", period="1d")

    assert result["success"] is False
    assert "error" in result
```

### 6. パラメータ化テスト

類似のテストケースはパラメータ化すること:

```python
@pytest.mark.parametrize("symbol,period,expected", [
    ("7203.T", "1d", True),
    ("6758.T", "5d", True),
    ("9984.T", "1mo", True),
])
def test_fetch_stock_data_with_various_parameters(symbol, period, expected):
    """複数のパラメータパターンをテスト"""
    service = StockDataService()
    result = service.fetch_stock_data(symbol=symbol, period=period)
    assert result["success"] == expected
```

---

## テスト実行とCI/CD

### ローカルでのテスト実行

```bash
# 全テスト実行
pytest

# 特定レベルのテスト実行
pytest -m unit                # ユニットテストのみ
pytest -m integration         # 統合テストのみ
pytest -m e2e                 # E2Eテストのみ
pytest -m "not e2e"          # E2E以外

# カバレッジ付き実行
pytest --cov=app --cov-report=html --cov-report=term

# 並列実行（高速化）
pytest -n auto

# 詳細出力
pytest -v

# 最初の失敗で停止
pytest -x
```

### CI/CDでの自動テスト

**PR作成時**:
- ユニットテスト実行
- 統合テスト実行
- カバレッジ測定（最低70%）

**mainブランチマージ時**:
- 全テスト実行（E2E含む）
- カバレッジレポート保存

詳細は [CI/CDパイプライン設定](../ci-cd/pipeline-config.md) を参照。

---

## pytest設定とプラグイン

### 必須プラグイン

プロジェクトでは以下のpytestプラグインを使用します:

1. **pytest-cov** - カバレッジ測定
2. **pytest-mock** - モック機能
3. **pytest-xdist** - 並列テスト実行
4. **pytest-timeout** - テストタイムアウト設定

### pytest.ini設定

```ini
[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*

# マーカー定義
markers =
    unit: Unit tests
    integration: Integration tests
    e2e: End-to-End tests
    slow: Slow running tests
    docs: Documentation tests

# デフォルト設定
addopts =
    --strict-markers
    --verbose
    --cov=app
    --cov-report=term-missing
    --cov-report=html
    --cov-fail-under=70

# ログ設定
log_cli = true
log_cli_level = INFO
```

### テストマーカーの使用

```python
import pytest

# モジュールレベルマーカー（推奨）
pytestmark = pytest.mark.unit

# 個別マーカー
@pytest.mark.integration
def test_database_integration():
    pass

@pytest.mark.slow
def test_long_running_process():
    pass

# 複数マーカー
@pytest.mark.e2e
@pytest.mark.slow
def test_full_user_flow():
    pass
```

---

## ベストプラクティス

### やるべきこと ✅

1. **テストの独立性を保つ**: テスト間で状態を共有しない
2. **意味のある名前**: テスト内容が一目で分かる命名
3. **小さく保つ**: 1つのテストは1つの振る舞いを検証
4. **失敗メッセージを明確に**: 何が失敗したかがすぐに分かるアサーション
5. **外部依存をモック化**: データベース、外部APIは必ずモック
6. **定期的な実行**: コミット前に全テストを実行
7. **カバレッジを確認**: 新規コードは必ずテストを追加

### 避けるべきこと ❌

1. **長すぎるテスト**: 500行を超えるテストファイルは分割検討
2. **外部依存への直接アクセス**: 実際のDBやAPIを使用しない
3. **スリープの使用**: `time.sleep()`の代わりに適切な待機機構を使用
4. **マジックナンバー**: 定数には意味のある名前を付ける
5. **テストのスキップ**: 恒久的なスキップは避け、修正または削除
6. **重複したテスト**: 同じ内容のテストは統合する
7. **実装詳細への依存**: インターフェースをテストし、実装詳細は避ける

### コードレビューチェックリスト

- [ ] テスト名が明確で、何をテストしているか理解できるか
- [ ] AAAパターンに従っているか
- [ ] 各テストが独立しているか
- [ ] モックが適切に使用されているか
- [ ] 正常系だけでなく異常系もテストされているか
- [ ] 境界値がテストされているか
- [ ] Docstringが記述されているか
- [ ] 適切なマーカーが付与されているか

---

## 関連ドキュメント

- [コーディング規約](coding-standards.md) - 一般的なコーディング規約
- [Git/GitHub運用ルール](git-workflow.md) - 開発フロー全体
- [CI/CDパイプライン設定](../ci-cd/pipeline-config.md) - CI/CD詳細設定
- [トラブルシューティング](../guides/troubleshooting.md) - テスト関連の問題解決

---

**最終更新**: 2025-11-02
**文書バージョン**: v3.0.0
**次回見直し**: カバレッジ70%達成時
