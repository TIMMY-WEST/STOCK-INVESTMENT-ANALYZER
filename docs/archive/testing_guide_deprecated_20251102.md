---
category: development
ai_context: archived
last_updated: 2025-10-22
deprecated_date: 2025-11-02
status: DEPRECATED
replacement_doc: ../standards/testing-standards.md
related_docs:
  - testing_strategy.md
  - coding_standards.md
## - ../architecture/project_architecture.md

# ⚠️ 非推奨: このドキュメントは統合されました

**このドキュメントは 2025年11月2日 に非推奨となりました。**

代わりに以下の統合ドキュメントを参照してください:
- **[テスト標準仕様書 (v3.0.0)](../standards/testing-standards.md)** ← こちらを使用

このファイルは `testing_guide.md`、`testing_strategy.md`、`test_coverage_report.md` を統合した最新バージョンです。
---
# テスト作成ガイドライン (ARCHIVED)

## 📋 概要

本ドキュメントは、株価データ取得システムにおけるテストコード作成のガイドラインを定義します。
単体テスト、結合テストの作成方法、命名規則、カバレッジ目標などを規定し、プロジェクト全体で一貫性のあるテストコードを維持します。

## 🎯 テストの目的と原則

### テストの目的

1. **品質保証**: コードの正しい動作を保証する
2. **回帰防止**: 既存機能の破壊を早期に検出する
3. **ドキュメント**: コードの振る舞いを示すドキュメントとして機能する
4. **設計改善**: テストしやすいコードは良い設計である

### テストの原則

- **FIRST原則**
  - **F**ast (高速): テストは迅速に実行されるべき
  - **I**ndependent (独立): テストは互いに独立しているべき
  - **R**epeatable (再現可能): 同じ条件で同じ結果を返すべき
  - **S**elf-validating (自己検証): テスト結果は明確に成功/失敗を示すべき
  - **T**imely (適時): テストはコードと同時に書くべき

- **AAAパターン**
  - **A**rrange (準備): テストに必要なデータ・状態を準備
  - **A**ct (実行): テスト対象の処理を実行
  - **A**ssert (検証): 期待される結果を検証

## 📂 テストの分類とスコープ

### 1. 単体テスト (Unit Test)

**目的**: 個々の関数・メソッド・クラスの動作を検証

**スコープ**:
- 単一の関数またはメソッド
- 外部依存を持たない、またはモック化する
- データベース、ファイルシステム、外部APIは使用しない

**例**:
```python
import pytest
from decimal import Decimal
from datetime import date
from models import StockDaily

pytestmark = pytest.mark.unit


def test_stock_daily_repr():
    """StockDailyモデルの文字列表現を検証する単体テスト"""
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

### 2. 結合テスト (Integration Test)

**目的**: 複数のコンポーネント間の連携動作を検証

**スコープ**:
- 複数のクラス・モジュール間の連携
- データベースとの連携
- 外部APIとの連携（モックまたはテスト環境）

**例**:
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

    # データベースに保存されていることを確認
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

**例**:
```python
import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait

pytestmark = pytest.mark.e2e


def test_stock_data_display_flow(selenium_driver):
    """株価データ表示フローのE2Eテスト"""
    # Arrange
    driver = selenium_driver
    driver.get("http://localhost:5000")

    # Act
    # 銘柄コード入力
    symbol_input = driver.find_element(By.ID, "symbol-input")
    symbol_input.send_keys("7203.T")

    # データ取得ボタンクリック
    fetch_button = driver.find_element(By.ID, "fetch-button")
    fetch_button.click()

    # データ表示を待機
    wait = WebDriverWait(driver, 10)
    table = wait.until(
        lambda d: d.find_element(By.ID, "stock-data-table")
    )

    # Assert
    assert table.is_displayed()
    rows = table.find_elements(By.TAG_NAME, "tr")
    assert len(rows) > 1  # ヘッダー行 + データ行
```

## 🏷️ テスト命名規則

### 基本ルール

1. **テストファイル名**: `test_<モジュール名>.py`
   - 例: `test_stock_data_service.py`, `test_models.py`

2. **テストクラス名**: `Test<クラス名>` (クラスベーステストの場合)
   - 例: `TestStockDataService`, `TestStockDaily`

3. **テスト関数名**: `test_<テスト対象>_<条件>_<期待結果>`
   - 例:
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

## 📊 テストカバレッジ目標

### カバレッジ目標

| レベル               | 最低カバレッジ | 推奨カバレッジ |
| -------------------- | -------------- | -------------- |
| **プロジェクト全体** | 70%            | 80%            |
| **重要モジュール**   | 80%            | 90%            |
| **ビジネスロジック** | 90%            | 95%            |
| **ユーティリティ**   | 70%            | 80%            |

### 重要モジュールの定義

- `services/` - ビジネスロジックを含むサービス層
- `models.py` - データモデル定義
- `utils/` - 共通ユーティリティ関数
- `app/routes/` - APIエンドポイント

### カバレッジ測定方法

```bash
# カバレッジレポート生成
pytest --cov=app --cov=models --cov=services --cov=utils --cov-report=html

# HTML形式のレポート確認
# htmlcov/index.html をブラウザで開く

# ターミナルでカバレッジ確認
pytest --cov=app --cov-report=term-missing
```

## 🔧 pytest設定とプラグイン

### 必須プラグイン

プロジェクトでは以下のpytestプラグインを使用します:

1. **pytest-cov** - カバレッジ測定
2. **pytest-mock** - モック機能
3. **pytest-xdist** - 並列テスト実行
4. **pytest-timeout** - テストタイムアウト設定

### pytest設定ファイル

設定は `pytest.ini` または `pyproject.toml` で管理します。

**pytest.ini の例**:
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
    e2e: End-to-End tests (requires browser)
    slow: Slow running tests

# デフォルト設定
addopts =
    --strict-markers
    --verbose
    --cov=app
    --cov=models
    --cov=services
    --cov=utils
    --cov-report=term-missing
    --cov-report=html
    --cov-fail-under=70

# ログ設定
log_cli = true
log_cli_level = INFO

# 警告設定
filterwarnings =
    ignore::DeprecationWarning
    ignore::PendingDeprecationWarning
```

### テストマーカーの使用

```python
import pytest

# 単体テストマーカー
pytestmark = pytest.mark.unit

def test_something():
    pass

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

### マーカー別テスト実行

```bash
# 単体テストのみ実行
pytest -m unit

# 結合テストのみ実行
pytest -m integration

# E2Eテスト以外を実行
pytest -m "not e2e"

# 単体テストと結合テストを実行
pytest -m "unit or integration"

# 遅いテストを除外
pytest -m "not slow"
```

## 🎯 テスト作成のベストプラクティス

### 1. フィクスチャの活用

**conftest.py での共通フィクスチャ定義**:

```python
import pytest
from app import app as flask_app
from models import Base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

@pytest.fixture(scope="session")
def app():
    """Flaskアプリケーションフィクスチャ"""
    flask_app.config["TESTING"] = True
    flask_app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
    return flask_app

@pytest.fixture(scope="function")
def db_session(app):
    """データベースセッションフィクスチャ"""
    engine = create_engine(app.config["SQLALCHEMY_DATABASE_URI"])
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()

    yield session

    session.close()
    Base.metadata.drop_all(engine)

@pytest.fixture
def client(app):
    """Flaskテストクライアント"""
    return app.test_client()
```

### 2. モックの適切な使用

```python
from unittest.mock import Mock, patch, MagicMock
import pytest

pytestmark = pytest.mark.unit


def test_fetch_stock_data_with_api_error_handles_gracefully(mocker):
    """外部API呼び出しをモック化"""
    # Arrange
    mock_yfinance = mocker.patch('yfinance.Ticker')
    mock_ticker = Mock()
    mock_ticker.history.side_effect = Exception("API Error")
    mock_yfinance.return_value = mock_ticker

    service = StockDataService()

    # Act
    result = service.fetch_stock_data(symbol="7203.T", period="1d")

    # Assert
    assert result["success"] is False
    assert "error" in result


@patch('services.stock_data_service.yfinance.Ticker')
def test_fetch_stock_data_with_mocked_response(mock_ticker_class):
    """デコレーター形式のモック"""
    # Arrange
    mock_ticker = Mock()
    mock_data = Mock()
    mock_data.empty = False
    mock_ticker.history.return_value = mock_data
    mock_ticker_class.return_value = mock_ticker

    service = StockDataService()

    # Act
    result = service.fetch_stock_data(symbol="7203.T", period="1d")

    # Assert
    assert result["success"] is True
```

### 3. パラメータ化テスト

```python
import pytest

pytestmark = pytest.mark.unit


@pytest.mark.parametrize("symbol,period,interval,expected", [
    ("7203.T", "1d", "1m", True),
    ("6758.T", "5d", "1d", True),
    ("9984.T", "1mo", "1wk", True),
])
def test_fetch_stock_data_with_various_parameters(
    symbol, period, interval, expected
):
    """複数のパラメータパターンをテスト"""
    service = StockDataService()
    result = service.fetch_stock_data(
        symbol=symbol,
        period=period,
        interval=interval
    )
    assert result["success"] == expected


@pytest.mark.parametrize("invalid_symbol", [
    "",
    None,
    "INVALID",
    "12345",
    "   ",
])
def test_fetch_stock_data_with_invalid_symbols_returns_error(invalid_symbol):
    """無効な銘柄コードのテスト"""
    service = StockDataService()
    result = service.fetch_stock_data(symbol=invalid_symbol, period="1d")
    assert result["success"] is False
```

### 4. 例外テスト

```python
import pytest

pytestmark = pytest.mark.unit


def test_stock_data_service_raises_value_error_on_invalid_period():
    """無効な期間指定で例外が発生することを検証"""
    service = StockDataService()

    with pytest.raises(ValueError) as exc_info:
        service.fetch_stock_data(symbol="7203.T", period="invalid_period")

    assert "Invalid period" in str(exc_info.value)


def test_database_connection_error_is_handled():
    """データベース接続エラーのハンドリング検証"""
    service = StockDataService()

    # データベース接続を意図的に失敗させる
    with patch('services.stock_data_service.get_db_session') as mock_db:
        mock_db.side_effect = ConnectionError("DB connection failed")

        # エラーが適切にハンドリングされることを確認
        result = service.save_stock_data(data=[])
        assert result["success"] is False
        assert "connection" in result["error"].lower()
```

### 5. データベーステスト

```python
import pytest
from models import StockDaily, Base
from datetime import date
from decimal import Decimal

pytestmark = pytest.mark.integration


def test_stock_daily_crud_operations(db_session):
    """StockDailyモデルのCRUD操作テスト"""
    # Create
    stock = StockDaily(
        symbol="7203.T",
        date=date(2024, 1, 1),
        open=Decimal("2500.00"),
        high=Decimal("2550.00"),
        low=Decimal("2480.00"),
        close=Decimal("2520.00"),
        volume=1000000
    )
    db_session.add(stock)
    db_session.commit()

    # Read
    retrieved = db_session.query(StockDaily).filter_by(
        symbol="7203.T"
    ).first()
    assert retrieved is not None
    assert retrieved.close == Decimal("2520.00")

    # Update
    retrieved.close = Decimal("2530.00")
    db_session.commit()

    updated = db_session.query(StockDaily).filter_by(
        symbol="7203.T"
    ).first()
    assert updated.close == Decimal("2530.00")

    # Delete
    db_session.delete(updated)
    db_session.commit()

    deleted = db_session.query(StockDaily).filter_by(
        symbol="7203.T"
    ).first()
    assert deleted is None
```

## 🚀 テスト実行方法

### 基本的な実行

```bash
# 全テスト実行
pytest

# 詳細出力
pytest -v

# 特定のファイルを実行
pytest tests/test_models.py

# 特定のテスト関数を実行
pytest tests/test_models.py::test_stock_daily_repr

# 特定のクラスを実行
pytest tests/test_models.py::TestStockDaily
```

### カバレッジ付き実行

```bash
# カバレッジ測定付き実行
pytest --cov

# カバレッジレポート（HTML）
pytest --cov --cov-report=html

# カバレッジレポート（ターミナル）
pytest --cov --cov-report=term-missing

# 最低カバレッジ設定
pytest --cov --cov-fail-under=70
```

### 並列実行

```bash
# CPU数に応じた並列実行
pytest -n auto

# 指定数のワーカーで並列実行
pytest -n 4
```

### その他のオプション

```bash
# 最初の失敗で停止
pytest -x

# 失敗したテストのみ再実行
pytest --lf

# 新規または変更されたテストのみ実行
pytest --nf

# テスト実行時間を表示
pytest --durations=10

# 詳細なログ出力
pytest -vv --log-cli-level=DEBUG
```

## 📝 テストコードレビューチェックリスト

テストコードのレビュー時には以下をチェックします:

### 基本チェック
- [ ] テスト名が明確で、何をテストしているか理解できるか
- [ ] AAAパターンに従っているか
- [ ] 各テストが独立しているか
- [ ] テストが高速に実行されるか（外部依存を最小化）

### 網羅性チェック
- [ ] 正常系だけでなく異常系もテストされているか
- [ ] 境界値がテストされているか
- [ ] エッジケースが考慮されているか

### 品質チェック
- [ ] モックが適切に使用されているか
- [ ] アサーションが適切か（期待値と実際の値が明確）
- [ ] テストコードが読みやすいか
- [ ] マジックナンバーが使用されていないか

### メンテナンス性チェック
- [ ] 共通フィクスチャが活用されているか
- [ ] 重複コードが最小化されているか
- [ ] テストデータが明確に定義されているか

## 🔄 継続的改善

### テストメトリクスの監視

以下のメトリクスを定期的に確認し、テスト品質を維持します:

1. **カバレッジ率**: 目標70%以上を維持
2. **テスト実行時間**: 全テスト5分以内を目標
3. **失敗率**: 継続的に低下させる
4. **テストコード行数**: 実装コードの0.5〜1.5倍程度

### テストの追加タイミング

- 新機能追加時: 機能実装と同時にテストを作成
- バグ修正時: バグを再現するテストを先に作成
- リファクタリング時: 既存のテストで動作を保証

## 📚 参考資料

- [pytest公式ドキュメント](https://docs.pytest.org/)
- [testing_strategy.md](testing_strategy.md) - 統合テスト戦略
- [coding_standards.md](coding_standards.md) - コーディング規約
- [Real Python - Testing Guide](https://realpython.com/pytest-python-testing/)
---
**最終更新**: 2025-10-22
**文書バージョン**: v1.0.0
**次回見直し**: マイルストーン3開始時
