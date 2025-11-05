---
category: development
ai_context: archived
last_updated: 2025-10-25
deprecated_date: 2025-11-02
status: DEPRECATED
replacement_doc: ../standards/testing-standards.md
related_docs:
  - testing_guide.md
  - coding_standards.md
## - ../architecture/project_architecture.md

# ⚠️ 非推奨: このドキュメントは統合されました

**このドキュメントは 2025年11月2日 に非推奨となりました。**

代わりに以下の統合ドキュメントを参照してください:
- **[テスト標準仕様書 (v3.0.0)](../standards/testing-standards.md)** ← こちらを使用

このファイルは `testing_guide.md`、`testing_strategy.md`、`test_coverage_report.md` を統合した最新バージョンです。
---
# テスト戦略 (ARCHIVED)

## 📋 目次

1. [テストの目的と重要性](#テストの目的と重要性)
2. [テストレベルの定義](#テストレベルの定義)
3. [テストカバレッジ目標](#テストカバレッジ目標)
4. [テスト命名規則](#テスト命名規則)
5. [テストパターン](#テストパターン)
6. [テストデータ管理](#テストデータ管理)
7. [モック使用ガイドライン](#モック使用ガイドライン)
8. [テスト実行ルール](#テスト実行ルール)
9. [まとめ](#まとめ)
---
## 1. テストの目的と重要性

### 1.1 なぜテストが必要か

テストは、ソフトウェア開発における品質保証の基盤であり、以下の目的で実施します:

1. **品質保証**: コードが期待通りに動作することを保証する
2. **回帰防止**: 既存機能の破壊を早期に検出し、安全なリファクタリングを可能にする
3. **仕様のドキュメント化**: テストコードが実装の振る舞いを示すドキュメントとして機能する
4. **設計の改善**: テストしやすいコードは、結合度が低く保守性の高いコードである
5. **開発速度の向上**: 自動テストにより手動確認の時間を削減し、開発サイクルを加速する

### 1.2 テストが保護するもの

- **機能の正確性**: ビジネスロジックが正しく実装されていることの保証
- **既存機能の互換性**: リファクタリングや新機能追加時の既存機能の保護
- **パフォーマンス**: システムのレスポンス時間とリソース使用量の適切性
- **セキュリティ**: 脆弱性の早期発見と対策
- **データ整合性**: データベース操作やデータフローの正確性

### 1.3 テストの重要性

特にリファクタリング時において、テストは**安全網**として機能します。包括的なテストスイートがあれば、コードの内部構造を大胆に変更しても、既存機能が破壊されていないことを確認できます。
---
## 2. テストレベルの定義

### 2.1 ユニットテスト (Unit Test)

#### 目的
個々の関数、メソッド、クラスの動作を検証する

#### スコープ
- **対象**: 単一の関数またはメソッド
- **外部依存**: モックやスタブで代替し、外部システムには依存しない
- **速度**: 非常に高速（ミリ秒単位）
- **実行頻度**: コミット前、CI/CDパイプラインで常時実行

#### 範囲と責任
- 関数やメソッドの入出力の検証
- エッジケース、境界値、異常系のテスト
- データベース、ファイルシステム、外部APIは使用しない
- ビジネスロジックの正確性を保証

#### 例
```python
import pytest
from decimal import Decimal
from datetime import date
from models import StockDaily

pytestmark = pytest.mark.unit


def test_stock_daily_repr_with_valid_data():
    """StockDailyモデルの文字列表現を検証する単体テスト"""
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
### 2.2 統合テスト (Integration Test)

#### 目的
複数のコンポーネント間の連携動作を検証する

#### スコープ
- **対象**: 複数のクラス、モジュール間の連携
- **外部依存**: 実際のデータベース、テスト用外部API、ファイルシステムを使用
- **速度**: 中速（秒単位）
- **実行頻度**: PR作成前、CI/CDパイプラインで実行

#### 範囲と責任
- コンポーネント間のデータフローの検証
- データベースとの連携動作の確認
- 外部APIとの統合動作の確認
- トランザクション処理の正確性

#### 例
```python
import pytest
from app import app
from models import Base, StockDaily
from services.stock_data_service import StockDataService

pytestmark = pytest.mark.integration


def test_stock_data_fetch_and_save_integration(app, db_session):
    """株価データ取得とDB保存の結合テスト"""
    # Arrange (準備)
    service = StockDataService()
    symbol = "7203.T"
    period = "5d"
    interval = "1d"

    # Act (実行)
    result = service.fetch_and_save_stock_data(
        symbol=symbol,
        period=period,
        interval=interval
    )

    # Assert (検証)
    assert result["success"] is True

    # データベースに保存されていることを確認
    saved_data = db_session.query(StockDaily).filter_by(
        symbol=symbol
    ).all()
    assert len(saved_data) > 0
```
---
### 2.3 E2Eテスト (End-to-End Test)

#### 目的
ユーザー視点での全体の動作を検証する

#### スコープ
- **対象**: ブラウザ操作を含むフルスタックフロー
- **外部依存**: 実際のUIとバックエンドシステム全体
- **速度**: 低速（分単位）
- **実行頻度**: リリース前、重要な機能変更後

#### 範囲と責任
- 実際のユーザーシナリオの再現
- UIからデータベースまでの全体フローの確認
- ブラウザの動作確認（レスポンシブデザイン等）
- 統合されたシステム全体の動作保証

#### 例
```python
import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait

pytestmark = pytest.mark.e2e


def test_stock_data_display_flow_e2e(selenium_driver):
    """株価データ表示フローのE2Eテスト"""
    # Arrange (準備)
    driver = selenium_driver
    driver.get("http://localhost:5000")

    # Act (実行)
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

    # Assert (検証)
    assert table.is_displayed()
    rows = table.find_elements(By.TAG_NAME, "tr")
    assert len(rows) > 1  # ヘッダー行 + データ行
```
---
## 3. テストカバレッジ目標

### 3.1 カバレッジ目標の設定

テストカバレッジは、コードがテストされている割合を示す指標です。本プロジェクトでは以下の目標を設定します:

| レベル               | 最低カバレッジ | 推奨カバレッジ |
| -------------------- | -------------- | -------------- |
| **プロジェクト全体** | **70%**        | 80%            |
| **重要モジュール**   | 80%            | 90%            |
| **ビジネスロジック** | 90%            | 95%            |
| **ユーティリティ**   | 70%            | 80%            |

### 3.2 重要モジュールの定義

以下のモジュールは、システムの中核を担うため、高いカバレッジを維持します:

- **`services/`**: ビジネスロジックを含むサービス層
- **`models.py`**: データモデル定義
- **`utils/`**: 共通ユーティリティ関数
- **`app/routes/`**: APIエンドポイント

### 3.3 測定方法

#### カバレッジレポート生成
```bash
# カバレッジレポート生成（HTML形式）
pytest --cov=app --cov=models --cov=services --cov=utils --cov-report=html

# HTML形式のレポート確認
# htmlcov/index.html をブラウザで開く
```

#### ターミナルでカバレッジ確認
```bash
# ターミナルでカバレッジ確認（未テスト行表示）
pytest --cov=app --cov-report=term-missing
```

#### 最低カバレッジ設定
```bash
# カバレッジ70%未満の場合、テスト失敗とする
pytest --cov --cov-fail-under=70
```

### 3.4 報告方法

- **PR作成時**: カバレッジレポートをPR説明に含める
- **CI/CD**: パイプラインでカバレッジを自動測定し、70%未満の場合はビルド失敗
- **定期レビュー**: 月次で全体カバレッジを確認し、改善計画を立てる
---
## 4. テスト命名規則

### 4.1 テストファイル命名規則

- **形式**: `test_*.py` または `*_test.py`
- **推奨**: `test_<モジュール名>.py`
- **例**:
  - `test_stock_data_service.py`
  - `test_models.py`
  - `test_bulk_data_service.py`

### 4.2 テストクラス命名規則（クラスベーステストの場合）

- **形式**: `Test<クラス名>`
- **例**:
  - `TestStockDataService`
  - `TestStockDaily`

### 4.3 テスト関数命名規則

- **形式**: `test_<機能>_<条件>_<期待結果>`
- **例**:
  - `test_fetch_stock_data_with_valid_symbol_returns_success()`
  - `test_save_stock_data_with_duplicate_record_raises_error()`
  - `test_calculate_moving_average_with_empty_data_returns_none()`

### 4.4 命名の良い例と悪い例

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

### 4.5 ファイル配置ルール

- **テストディレクトリ**: `tests/`
- **構造**: 実装コードのディレクトリ構造に対応
  ```
  app/
  ├── services/
  │   └── stock_data_service.py
  tests/
  ├── test_stock_data_service.py
  ```
---
## 5. テストパターン

### 5.1 AAAパターンの適用ルール

**AAAパターン**は、テストコードを明確に構造化するための標準的なパターンです。

#### パターンの構成

1. **Arrange (準備)**: テストに必要なデータ、オブジェクト、状態を準備
2. **Act (実行)**: テスト対象の処理を実行
3. **Assert (検証)**: 期待される結果を検証

#### 実装例

```python
import pytest
from services.stock_data_service import StockDataService

pytestmark = pytest.mark.unit


def test_fetch_stock_data_with_valid_symbol_returns_success():
    """正常な銘柄コードでデータ取得が成功することを検証"""
    # Arrange (準備)
    service = StockDataService()
    symbol = "7203.T"
    period = "5d"
    interval = "1d"

    # Act (実行)
    result = service.fetch_stock_data(
        symbol=symbol,
        period=period,
        interval=interval
    )

    # Assert (検証)
    assert result["success"] is True
    assert "data" in result
    assert len(result["data"]) > 0
```

#### AAAパターンのメリット

- **可読性向上**: テストの意図が明確になる
- **保守性向上**: 各セクションの役割が明確で、変更が容易
- **一貫性**: プロジェクト全体で統一されたテスト構造
---
## 6. テストデータ管理

### 6.1 フィクスチャの活用

#### 基本的なフィクスチャ定義（`conftest.py`）

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
    """データベースセッションフィクスチャ（各テスト後にクリーンアップ）"""
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

#### フィクスチャのスコープ

- **`function`**: 各テスト関数ごとに実行（デフォルト）
- **`class`**: テストクラスごとに実行
- **`module`**: モジュールごとに実行
- **`session`**: テストセッション全体で1回実行

### 6.2 ファクトリーパターンの使用

複雑なテストデータを生成する場合、ファクトリーパターンを使用します。

```python
from decimal import Decimal
from datetime import date
from models import StockDaily


def create_stock_daily(
    symbol="7203.T",
    date_value=date(2024, 1, 1),
    open_price=Decimal("2500.00"),
    high_price=Decimal("2550.00"),
    low_price=Decimal("2480.00"),
    close_price=Decimal("2520.00"),
    volume=1000000
):
    """StockDailyインスタンスを生成するファクトリー関数"""
    return StockDaily(
        symbol=symbol,
        date=date_value,
        open=open_price,
        high=high_price,
        low=low_price,
        close=close_price,
        volume=volume
    )


# 使用例
def test_stock_daily_factory():
    stock = create_stock_daily(symbol="6758.T", close_price=Decimal("3000.00"))
    assert stock.symbol == "6758.T"
    assert stock.close == Decimal("3000.00")
```
---
## 7. モック使用ガイドライン

### 7.1 いつモックを使うべきか

以下の場合にモックを使用します:

1. **外部APIへの依存**: Yahoo Finance API、JPX APIなど
2. **データベースアクセス**: ユニットテストでのDB操作
3. **ファイルシステム操作**: ファイル読み書き
4. **時間依存の処理**: 現在時刻、タイムアウト処理
5. **ネットワーク通信**: HTTP通信、WebSocket

### 7.2 モックの実装方法

#### pytest-mockを使用したモック

```python
from unittest.mock import Mock
import pytest

pytestmark = pytest.mark.unit


def test_fetch_stock_data_with_api_error_handles_gracefully(mocker):
    """外部API呼び出しをモック化してエラーハンドリングを検証"""
    # Arrange (準備)
    mock_yfinance = mocker.patch('yfinance.Ticker')
    mock_ticker = Mock()
    mock_ticker.history.side_effect = Exception("API Error")
    mock_yfinance.return_value = mock_ticker

    service = StockDataService()

    # Act (実行)
    result = service.fetch_stock_data(symbol="7203.T", period="1d")

    # Assert (検証)
    assert result["success"] is False
    assert "error" in result
```

#### デコレーター形式のモック

```python
from unittest.mock import Mock, patch
import pytest

pytestmark = pytest.mark.unit


@patch('services.stock_data_service.yfinance.Ticker')
def test_fetch_stock_data_with_mocked_response(mock_ticker_class):
    """デコレーター形式でモック化"""
    # Arrange (準備)
    mock_ticker = Mock()
    mock_data = Mock()
    mock_data.empty = False
    mock_ticker.history.return_value = mock_data
    mock_ticker_class.return_value = mock_ticker

    service = StockDataService()

    # Act (実行)
    result = service.fetch_stock_data(symbol="7203.T", period="1d")

    # Assert (検証)
    assert result["success"] is True
```

### 7.3 モック使用のベストプラクティス

- **最小限のモック化**: 必要最小限の範囲のみモック化
- **明確な振る舞い定義**: モックの返り値や例外を明確に定義
- **過度なモック化を避ける**: 統合テストでは実際の依存関係を使用
- **モックの検証**: モックが正しく呼び出されたかを検証（`assert_called_with`等）
---
## 8. テスト実行ルール

### 8.1 ローカルでのテスト実行義務

**すべての開発者は、コミット前に以下のテストを実行すること**:

```bash
# 全テスト実行
pytest

# 特定のマーカーのみ実行（E2Eテストを除く）
pytest -m "not e2e"

# カバレッジ付き実行
pytest --cov
```

### 8.2 PR作成前の全テスト通過必須

Pull Request作成前に、以下を確認すること:

- [ ] 全ユニットテストが通過している
- [ ] 全統合テストが通過している
- [ ] カバレッジ目標（70%以上）を達成している
- [ ] 新規追加した機能にテストが含まれている

```bash
# PR作成前の確認コマンド
pytest --cov --cov-fail-under=70
```

### 8.3 CI/CDでのテスト自動実行

#### CI/CDパイプラインでの自動テスト

- **トリガー**: Pull Request作成時、mainブランチへのマージ時
- **実行内容**:
  1. ユニットテスト実行
  2. 統合テスト実行
  3. カバレッジ測定（最低70%）
  4. E2Eテスト実行（リリース前のみ）
- **失敗時の対応**: ビルド失敗としてマージをブロック

#### テスト実行の並列化

```bash
# CPU数に応じた並列実行
pytest -n auto

# 指定数のワーカーで並列実行
pytest -n 4
```

### 8.4 テストマーカー別実行

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

### 8.5 テスト失敗時の対応

1. **失敗したテストの確認**: エラーメッセージとスタックトレースを確認
2. **再現性の確認**: ローカル環境で再現できるか確認
3. **修正または無効化**: テストまたは実装コードを修正、または一時的に無効化
4. **再テスト**: 修正後、全テストを再実行

```bash
# 失敗したテストのみ再実行
pytest --lf

# 最初の失敗で停止
pytest -x
```
---
## 9. まとめ

本ドキュメントで定義したテスト戦略は、リファクタリングの安全網として機能し、プロジェクト全体の品質を保証します。

### 9.1 重要ポイント

- **テストレベルの理解**: ユニット、統合、E2Eテストの役割を理解し、適切に使い分ける
- **カバレッジ目標の達成**: プロジェクト全体で70%以上のカバレッジを維持する
- **命名規則の遵守**: テスト内容が明確になる命名規則を徹底する
- **AAAパターンの適用**: テストコードの可読性と保守性を向上させる
- **フィクスチャとファクトリーの活用**: テストデータの管理を効率化する
- **モックの適切な使用**: 外部依存を分離し、テストの独立性を保つ
- **テスト実行の徹底**: コミット前、PR作成前、CI/CDでの自動実行

### 9.2 継続的改善

テスト戦略は固定されたものではなく、プロジェクトの進化に応じて継続的に改善します:

- **定期的なレビュー**: 月次でテスト戦略を見直し、改善点を特定
- **新しいベストプラクティスの導入**: 業界標準や新しいツールを積極的に採用
- **フィードバックの反映**: チームからのフィードバックを戦略に反映

### 9.3 関連ドキュメント

- [testing_guide.md](testing_guide.md) - テスト作成ガイドライン
- [coding_standards.md](coding_standards.md) - コーディング規約
- [GitHub Workflow](github_workflow.md) - GitHub運用ルール
---
**最終更新**: 2025-10-25
**文書バージョン**: v2.0.0
**次回見直し**: リファクタリング完了時
