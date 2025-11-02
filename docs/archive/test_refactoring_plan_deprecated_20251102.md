---
category: testing
ai_context: archived
last_updated: 2025-10-29
deprecated_date: 2025-11-02
status: DEPRECATED
replacement_doc: ../standards/testing-standards.md
related_docs:
  - testing_strategy.md
  - testing_guide.md
  - ../development/coding_standards.md
---

# ⚠️ 非推奨: このドキュメントは統合されました

**このドキュメントは 2025年11月2日 に非推奨となりました。**

代わりに以下の統合ドキュメントを参照してください:
- **[テスト標準仕様書 (v3.0.0)](../standards/testing-standards.md)** ← テスト戦略とベストプラクティス

このリファクタリング計画で提案された内容は統合ドキュメントに反映されています。

---

# テストリファクタリング計画 (ARCHIVED)

## 📋 目次

1. [エグゼクティブサマリー](#エグゼクティブサマリー)
2. [監査結果の概要](#監査結果の概要)
3. [発見された問題点](#発見された問題点)
4. [リファクタリング優先順位](#リファクタリング優先順位)
5. [フェーズ別実装計画](#フェーズ別実装計画)
6. [リスク評価と対策](#リスク評価と対策)
7. [成功基準](#成功基準)
8. [関連Issue](#関連issue)

---

## 1. エグゼクティブサマリー

### 1.1 監査実施概要

**監査実施日**: 2025-10-29
**監査対象**: `tests/` ディレクトリ内の全テストファイル
**監査基準**: [docs/development/testing_strategy.md](../development/testing_strategy.md)

### 1.2 全体的な評価

**総合テスト品質スコア**: **65-70% / 100**

| 評価カテゴリ           | 準拠率 | 評価     |
| ---------------------- | ------ | -------- |
| テストファイル命名規則 | 100%   | ✓ 優秀   |
| テスト関数命名規則     | 75-80% | △ 要改善 |
| AAAパターン適用        | 30%    | ✗ 不十分 |
| テストマーカー         | 7.7%   | ✗ 深刻   |
| ディレクトリ配置       | 95%    | ✓ 良好   |
| Docstring              | 85%    | △ 良好   |
| pytest vs unittest統一 | 94%    | △ 良好   |

### 1.3 主なリスク

1. **テストマーカーの欠落（92.3%のファイル）**: テスト実行の柔軟性が低い
2. **AAAパターン未適用（70%のファイル）**: テストの可読性と保守性が低い
3. **unittest と pytest の混在**: テストスタイルの不統一
4. **恒久的なテストスキップ（2件）**: テストカバレッジの低下

### 1.4 推奨アクション

リファクタリングを3つのフェーズに分割して実施:
- **フェーズ1**: テストマーカーの追加と pytest への統一（1-2週間）
- **フェーズ2**: AAAパターンの適用と docstring の充実（2-3週間）
- **フェーズ3**: 命名規則の統一と品質向上（1-2週間）

**総見積もり工数**: 4-7週間

---

## 2. 監査結果の概要

### 2.1 テストファイル総数と分布

**総テストファイル数**: **52ファイル**
**総行数**: **14,928行**

#### ディレクトリ別分布

| ディレクトリ         | ファイル数 | 割合  |
| -------------------- | ---------- | ----- |
| `tests/unit/`        | 23         | 44.2% |
| `tests/integration/` | 7          | 13.5% |
| `tests/api/`         | 6          | 11.5% |
| `tests/e2e/`         | 5          | 9.6%  |
| `tests/docs/`        | 5          | 9.6%  |
| `tests/utils/`       | 1          | 1.9%  |
| `tests/` (直下)      | 2          | 3.8%  |
| その他               | 3          | 5.8%  |

### 2.2 テスト規模の分析

- **最大テストファイル**: `tests/unit/test_bulk_data_service.py` （推定500+行）
- **最小テストファイル**: `tests/e2e/.gitkeep` （0行）
- **平均行数**: 約287行/ファイル

---

## 3. 発見された問題点

### 3.1 テストマーカーの欠落 (優先度: P1)

#### 問題の詳細

**影響を受けるファイル数**: 48ファイル（92.3%）

| ディレクトリ         | マーカー欠落ファイル数 | 割合  |
| -------------------- | ---------------------- | ----- |
| `tests/unit/`        | 22                     | 95.7% |
| `tests/integration/` | 6                      | 85.7% |
| `tests/api/`         | 5                      | 83.3% |
| `tests/e2e/`         | 2                      | 40.0% |
| その他               | 13                     | 100%  |

#### 具体的な問題例

1. **マーカーが完全に欠落**
   ```python
   # tests/unit/test_models.py
   # pytestmark がない
   def test_stock_daily_repr_with_valid_data():
       ...
   ```

2. **誤ったマーカー**
   ```python
   # tests/e2e/test_e2e_api.py
   pytestmark = pytest.mark.integration  # E2Eなのにintegration
   ```

   ```python
   # tests/unit/test_error_handling.py
   pytestmark = pytest.mark.integration  # unitなのにintegration
   ```

#### 影響

- テストレベル別の実行ができない（`pytest -m unit` が正しく機能しない）
- CI/CDパイプラインでのテスト実行戦略が適用できない
- テスト実行時間の最適化が困難

#### 修正方法

```python
# tests/unit/test_*.py の場合
import pytest

pytestmark = pytest.mark.unit

# tests/integration/test_*.py の場合
pytestmark = pytest.mark.integration

# tests/e2e/test_*.py の場合
pytestmark = pytest.mark.e2e
```

---

### 3.2 AAAパターンの未適用 (優先度: P2)

#### 問題の詳細

**AAAパターン適用率**: 約30%（16/52ファイル）
**未適用ファイル**: 約35ファイル以上

#### 具体的な問題例

**悪い例**: AAAパターンが不明確

```python
# tests/api/test_app.py:9-13
def test_index_route(client):
    response = client.get("/")
    assert response.status_code == 200
    data = json.loads(response.data)
    assert "message" in data
```

**良い例**: AAAパターンが明確

```python
# tests/unit/test_error_handler.py:88-94
def test_handle_temporary_error_returns_retry(error_handler):
    """一時的エラーの場合、RETRYアクションを返す."""
    # Arrange (準備)
    error = Timeout("Request timed out")

    # Act (実行)
    action = error_handler.handle_error(
        error, "7203.T", {"retry_count": 0}
    )

    # Assert (検証)
    assert action == ErrorAction.RETRY
```

#### 影響

- テストの可読性が低下
- テストの保守性が低下
- 新規メンバーがテストを理解しづらい

#### 修正対象ファイル（一部）

- `tests/api/test_app.py`
- `tests/unit/test_exceptions.py`
- `tests/test_api_response.py`
- `tests/integration/test_reset_db.py`
- その他30+ファイル

---

### 3.3 unittest と pytest の混在 (優先度: P1)

#### 問題の詳細

**影響を受けるファイル数**: 3ファイル

| ファイルパス                                     | 問題のクラス                 | 行番号 |
| ------------------------------------------------ | ---------------------------- | ------ |
| `tests/integration/test_stocks_daily_removal.py` | `TestStocksDailyRemoval`     | 46     |
| `tests/unit/test_database_connection.py`         | `TestDatabaseConnectionPool` | 17     |
| `tests/test_api_usage_guide.py`                  | `TestAPIUsageGuide`          | 13     |

#### 具体的な問題例

```python
# tests/integration/test_stocks_daily_removal.py:46
import unittest

class TestStocksDailyRemoval(unittest.TestCase):  # ✗ unittest使用
    def setUp(self):
        # pytest の fixture ではなく unittest の setUp
        ...
```

#### 影響

- テストスタイルの不統一
- pytest の高度な機能（fixture、parametrize等）が使えない
- テストコードの保守性低下

#### 修正方法

```python
# 修正前
import unittest

class TestStocksDailyRemoval(unittest.TestCase):
    def setUp(self):
        self.db = create_db()

    def test_removal(self):
        ...

# 修正後
import pytest

class TestStocksDailyRemoval:
    @pytest.fixture
    def db(self):
        return create_db()

    def test_removal(self, db):
        ...
```

---

### 3.4 テスト関数命名規則の不統一 (優先度: P2)

#### 問題の詳細

**準拠率**: 約75-80%
**非準拠ファイル数**: 12-15ファイル

#### 具体的な問題例

| ファイル                           | 関数名                                  | 問題点                 | 推奨                                                     |
| ---------------------------------- | --------------------------------------- | ---------------------- | -------------------------------------------------------- |
| `tests/api/test_bulk_api.py`       | `test_start_requires_api_key()`         | 条件・期待結果が不明確 | `test_bulk_start_without_api_key_returns_401()`          |
| `tests/api/test_app.py`            | `test_index_route()`                    | 詳細度不足             | `test_index_route_returns_welcome_message()`             |
| `tests/unit/test_websocket.py`     | `test_websocket_connection()`           | 条件・期待結果が不明確 | `test_websocket_connection_with_valid_client_succeeds()` |
| `tests/unit/test_state_manager.py` | `test_create_state_manager_test_file()` | テスト内容が不明確     | `test_state_manager_creates_html_test_file()`            |

#### 推奨命名規則

```
test_<機能>_<条件>_<期待結果>
```

**例**:
- ✓ `test_fetch_stock_data_with_valid_symbol_returns_success()`
- ✓ `test_save_stock_data_with_duplicate_record_raises_error()`
- ✗ `test_fetch()` - 詳細度不足
- ✗ `test_stock_data()` - 曖昧

---

### 3.5 恒久的なテストスキップ (優先度: P1)

#### 問題の詳細

**スキップされているテスト数**: 2件

| ファイル                             | 行番号 | スキップ理由                           |
| ------------------------------------ | ------ | -------------------------------------- |
| `tests/api/test_stock_master_api.py` | 116    | モック設定が複雑なため一時的にスキップ |
| `tests/api/test_stock_master_api.py` | 132    | 同上                                   |

#### コード例

```python
# tests/api/test_stock_master_api.py:116
@pytest.mark.skip(reason="モック設定が複雑なため一時的にスキップ")
def test_export_stocks_csv_success():
    ...

@pytest.mark.skip(reason="モック設定が複雑なため一時的にスキップ")
def test_export_stocks_json_success():
    ...
```

#### 影響

- テストカバレッジの低下
- 実装済み機能が未検証のまま

#### 対策

1. モック設定を修正してテストを有効化
2. テストが不要な場合は削除
3. 技術的に困難な場合は別のアプローチでテスト（統合テスト等）

---

### 3.6 その他の問題

#### A. ディレクトリ配置の不整合

**影響ファイル**: 3ファイル

| ファイル                            | 現在の場所    | 問題                               |
| ----------------------------------- | ------------- | ---------------------------------- |
| `tests/e2e/test_e2e_api.py`         | `tests/e2e/`  | マーカーが `integration`           |
| `tests/unit/test_error_handling.py` | `tests/unit/` | マーカーが `integration`           |
| `tests/unit/test_state_manager.py`  | `tests/unit/` | HTMLテスト生成（セットアップ用途） |

#### B. Docstring の不足

**影響ファイル**: 10-15ファイル

- `tests/api/test_bulk_api.py`: 複数の関数に docstring なし
- `tests/unit/test_websocket.py`: 複数の関数に docstring なし

#### C. テスト品質の問題

- **エラーハンドリングテスト不足**: 正常系のテストが多く、異常系のテストが少ない
- **パラメトライズドテストの不足**: 類似テストケースの重複

---

## 4. リファクタリング優先順位

### 4.1 優先順位の基準

リファクタリングの優先順位は以下の基準で決定:

1. **影響範囲**: 問題が影響するファイル数
2. **重要度**: テスト品質への影響度
3. **実装難易度**: 修正の技術的難易度
4. **依存関係**: 他のリファクタリングへの依存

### 4.2 優先順位マトリックス

| 優先度 | 問題                           | 影響ファイル数 | 重要度 | 難易度 | 推奨実施時期 |
| ------ | ------------------------------ | -------------- | ------ | ------ | ------------ |
| **P1** | テストマーカーの追加           | 48             | 高     | 低     | フェーズ1    |
| **P1** | pytest への統一                | 3              | 高     | 中     | フェーズ1    |
| **P1** | 誤ったマーカーの修正           | 2              | 高     | 低     | フェーズ1    |
| **P1** | テストスキップの解決           | 2              | 高     | 中     | フェーズ1    |
| **P2** | AAAパターンの適用              | 35+            | 中     | 低     | フェーズ2    |
| **P2** | docstring の統一               | 10-15          | 中     | 低     | フェーズ2    |
| **P2** | テスト関数命名規則の統一       | 12-15          | 中     | 低     | フェーズ3    |
| **P3** | エラーハンドリングテストの充実 | 全体           | 中     | 中     | フェーズ3    |
| **P3** | パフォーマンステストの追加     | 全体           | 低     | 中     | 継続的に実施 |

---

## 5. フェーズ別実装計画

### フェーズ1: 基盤整備とマーカー追加 (1-2週間)

#### 目的
テスト実行の柔軟性を確保し、pytest への統一を図る

#### 対象Issue
- [#203: 既存テストの命名規則修正](https://github.com/TIMMY-WEST/STOCK-INVESTMENT-ANALYZER/issues/203)
- テストマーカーの追加（新規Issue作成推奨）

#### 実施内容

##### 1.1 テストマーカーの一括追加（48ファイル）

**対象ディレクトリ**: `tests/unit/`, `tests/integration/`, `tests/api/`, `tests/e2e/`

**作業内容**:
```python
# 各ファイルの先頭に追加
import pytest

pytestmark = pytest.mark.unit  # またはintegration, e2e, api
```

**ファイル別マーカー指定**:
- `tests/unit/test_*.py` → `pytest.mark.unit`
- `tests/integration/test_*.py` → `pytest.mark.integration`
- `tests/api/test_*.py` → `pytest.mark.unit` または `pytest.mark.integration`（内容による）
- `tests/e2e/test_*.py` → `pytest.mark.e2e`

**見積もり工数**: 3-4日

##### 1.2 誤ったマーカーの修正（2ファイル）

**対象ファイル**:
- `tests/e2e/test_e2e_api.py`: `integration` → `e2e`
- `tests/unit/test_error_handling.py`: `integration` → `unit`

**見積もり工数**: 0.5日

##### 1.3 unittest から pytest への移行（3ファイル）

**対象ファイル**:
1. `tests/integration/test_stocks_daily_removal.py`
2. `tests/unit/test_database_connection.py`
3. `tests/test_api_usage_guide.py`

**移行手順**:
1. `unittest.TestCase` の継承を削除
2. `setUp` / `tearDown` を pytest fixture に変更
3. `self.assert*` を `assert` に変更
4. テスト実行して動作確認

**見積もり工数**: 2-3日

##### 1.4 テストスキップの解決（2ファイル）

**対象ファイル**: `tests/api/test_stock_master_api.py`

**作業内容**:
1. スキップされているテストのモック設定を修正
2. テストを有効化して動作確認
3. 不要な場合は削除を検討

**見積もり工数**: 1-2日

#### フェーズ1の成功基準

- [ ] 全テストファイルに適切なマーカーが付与されている
- [ ] `pytest -m unit` でユニットテストのみが実行される
- [ ] `pytest -m integration` で統合テストのみが実行される
- [ ] `pytest -m e2e` でE2Eテストのみが実行される
- [ ] unittest を使用しているテストが存在しない
- [ ] 恒久的にスキップされているテストが存在しない

---

### フェーズ2: テストパターンと品質向上 (2-3週間)

#### 目的
テストの可読性と保守性を向上させる

#### 対象Issue
- [#204: 既存テストのAAAパターン適用](https://github.com/TIMMY-WEST/STOCK-INVESTMENT-ANALYZER/issues/204)
- [#206: テストフィクスチャの共通化とリファクタリング](https://github.com/TIMMY-WEST/STOCK-INVESTMENT-ANALYZER/issues/206)

#### 実施内容

##### 2.1 AAAパターンの適用（35+ファイル）

**対象**: AAAパターンが適用されていない全テストファイル

**作業内容**:
```python
# 修正前
def test_example(client):
    response = client.get("/api/test")
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data["success"] is True

# 修正後
def test_example(client):
    """APIテストエンドポイントが正常に動作することを検証"""
    # Arrange (準備)
    endpoint = "/api/test"

    # Act (実行)
    response = client.get(endpoint)

    # Assert (検証)
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data["success"] is True
```

**優先対象ファイル**:
1. `tests/unit/test_models.py`
2. `tests/api/test_app.py`
3. `tests/unit/test_exceptions.py`
4. `tests/test_api_response.py`
5. `tests/integration/test_reset_db.py`
6. その他30+ファイル

**見積もり工数**: 5-7日

##### 2.2 Docstring の統一（10-15ファイル）

**対象**: docstring が不足しているテスト関数

**作業内容**:
```python
# 修正前
def test_start_requires_api_key():
    ...

# 修正後
def test_start_requires_api_key():
    """APIキーなしでバルク処理開始リクエストを送信すると401エラーが返される"""
    ...
```

**見積もり工数**: 2-3日

##### 2.3 テストフィクスチャの共通化

**対象**: `tests/conftest.py` と各テストファイル

**作業内容**:
- 重複しているフィクスチャを `conftest.py` に集約
- スコープの適切な設定（function, class, module, session）
- フィクスチャの文書化

**見積もり工数**: 2-3日

#### フェーズ2の成功基準

- [ ] 全テストファイルにAAAパターンが適用されている
- [ ] 各テスト関数に説明的なdocstringが付与されている
- [ ] 共通フィクスチャが `conftest.py` に集約されている
- [ ] テストの可読性が向上している

---

### フェーズ3: 命名規則統一と品質向上 (1-2週間)

#### 目的
テストの命名規則を統一し、全体的な品質を向上させる

#### 対象Issue
- [#203: 既存テストの命名規則修正](https://github.com/TIMMY-WEST/STOCK-INVESTMENT-ANALYZER/issues/203)（継続）
- [#207: 不要テストの削除と統合](https://github.com/TIMMY-WEST/STOCK-INVESTMENT-ANALYZER/issues/207)
- [#208: テストカバレッジの向上（サービス層）](https://github.com/TIMMY-WEST/STOCK-INVESTMENT-ANALYZER/issues/208)

#### 実施内容

##### 3.1 テスト関数命名規則の統一（12-15ファイル）

**対象**: 命名規則に準拠していないテスト関数

**作業内容**:
```python
# 修正前
def test_start_requires_api_key():
    ...

# 修正後
def test_bulk_start_without_api_key_returns_401():
    ...
```

**見積もり工数**: 3-4日

##### 3.2 エラーハンドリングテストの追加

**対象**: 正常系テストのみ存在するファイル

**作業内容**:
- 各APIエンドポイントに異常系テストを追加
- バリデーションエラーのテスト
- タイムアウト、ネットワークエラーのテスト

**見積もり工数**: 3-4日

##### 3.3 不要テストの削除と統合

**対象**: 重複しているテストや不要なテスト

**作業内容**:
- テストの重複を削除
- 類似テストをパラメトライズドテストに統合
- 古いテストの削除

**見積もり工数**: 1-2日

#### フェーズ3の成功基準

- [ ] 全テスト関数が命名規則に準拠している
- [ ] エラーハンドリングテストが充実している
- [ ] 不要なテストが削除されている
- [ ] テストカバレッジが70%以上

---

### フェーズ4: CI/CD統合とドキュメント整備 (1週間)

#### 目的
CI/CDパイプラインへのテスト統合とドキュメント整備

#### 対象Issue
- [#209: E2Eテストの整備](https://github.com/TIMMY-WEST/STOCK-INVESTMENT-ANALYZER/issues/209)
- [#210: GitHub Actionsワークフローの作成](https://github.com/TIMMY-WEST/STOCK-INVESTMENT-ANALYZER/issues/210)
- [#211: 品質ゲートの設定](https://github.com/TIMMY-WEST/STOCK-INVESTMENT-ANALYZER/issues/211)
- [#212: CI/CDドキュメントの作成](https://github.com/TIMMY-WEST/STOCK-INVESTMENT-ANALYZER/issues/212)

#### 実施内容

##### 4.1 GitHub Actions ワークフローの作成

**作業内容**:
- ユニットテスト実行ワークフロー
- 統合テスト実行ワークフロー
- E2Eテスト実行ワークフロー（リリース前のみ）
- カバレッジレポート生成

**見積もり工数**: 2日

##### 4.2 品質ゲートの設定

**作業内容**:
- 最低カバレッジ70%の設定
- テスト失敗時のビルド失敗設定
- PR作成前のテスト実行必須化

**見積もり工数**: 1日

##### 4.3 CI/CDドキュメントの作成

**作業内容**:
- CI/CD運用ドキュメント作成
- トラブルシューティングガイド作成

**見積もり工数**: 2日

#### フェーズ4の成功基準

- [ ] GitHub Actions でテストが自動実行される
- [ ] カバレッジ70%未満でビルドが失敗する
- [ ] CI/CD運用ドキュメントが整備されている

---

## 6. リスク評価と対策

### 6.1 リスク一覧

| リスク                     | 影響度 | 発生確率 | 対策                         |
| -------------------------- | ------ | -------- | ---------------------------- |
| テスト修正によるバグ混入   | 高     | 中       | 修正前後でテスト実行を徹底   |
| リファクタリング工数の超過 | 中     | 中       | フェーズ分割による段階的実施 |
| テスト実行時間の増加       | 中     | 低       | 並列実行の活用               |
| チーム内での合意形成       | 低     | 中       | ドキュメントとレビューの徹底 |

### 6.2 対策の詳細

#### リスク1: テスト修正によるバグ混入

**対策**:
1. 修正前に既存テストを全実行して通過を確認
2. 修正後に再度全テストを実行
3. カバレッジレポートで変更影響を確認
4. PRレビューで2名以上の承認を必須化

#### リスク2: リファクタリング工数の超過

**対策**:
1. フェーズを小さく分割
2. 各フェーズでの成功基準を明確化
3. 週次で進捗確認
4. 優先度の低いタスクは後回し

#### リスク3: テスト実行時間の増加

**対策**:
1. `pytest-xdist` による並列実行
2. スローテストの特定と最適化
3. CI/CDでのテストレベル別実行

#### リスク4: チーム内での合意形成

**対策**:
1. リファクタリング計画のレビュー
2. 定期的な進捗共有
3. 疑問点の早期解決

---

## 7. 成功基準

### 7.1 定量的基準

| 指標                 | 現状   | 目標 | 測定方法                 |
| -------------------- | ------ | ---- | ------------------------ |
| テスト品質スコア     | 65-70% | 90%+ | 本ドキュメントの評価基準 |
| テストマーカー適用率 | 7.7%   | 100% | grep 検索                |
| AAAパターン適用率    | 30%    | 90%+ | 目視確認                 |
| pytest 統一率        | 94%    | 100% | grep 検索                |
| テストカバレッジ     | 不明   | 70%+ | pytest-cov               |
| 命名規則準拠率       | 75-80% | 95%+ | 目視確認                 |

### 7.2 定性的基準

- [ ] 新規メンバーがテストを理解しやすい
- [ ] テストの保守性が向上している
- [ ] テスト実行が柔軟に行える
- [ ] CI/CDパイプラインが安定稼働している
- [ ] チーム内でテスト戦略が共有されている

### 7.3 最終確認項目

- [ ] 全テストファイルに適切なマーカーが付与されている
- [ ] 全テストにAAAパターンが適用されている
- [ ] unittest を使用しているテストが存在しない
- [ ] 恒久的にスキップされているテストが存在しない
- [ ] テストカバレッジが70%以上
- [ ] CI/CDパイプラインでテストが自動実行される
- [ ] 品質ゲートが設定されている

---

## 8. 関連Issue

### 8.1 既存Issue

| Issue番号                                                                  | タイトル                                     | 優先度 | 関連フェーズ |
| -------------------------------------------------------------------------- | -------------------------------------------- | ------ | ------------ |
| [#203](https://github.com/TIMMY-WEST/STOCK-INVESTMENT-ANALYZER/issues/203) | 既存テストの命名規則修正                     | P1/P2  | フェーズ1, 3 |
| [#204](https://github.com/TIMMY-WEST/STOCK-INVESTMENT-ANALYZER/issues/204) | 既存テストのAAAパターン適用                  | P2     | フェーズ2    |
| [#205](https://github.com/TIMMY-WEST/STOCK-INVESTMENT-ANALYZER/issues/205) | テストディレクトリ構造の再編成               | P2     | フェーズ2    |
| [#206](https://github.com/TIMMY-WEST/STOCK-INVESTMENT-ANALYZER/issues/206) | テストフィクスチャの共通化とリファクタリング | P2     | フェーズ2    |
| [#207](https://github.com/TIMMY-WEST/STOCK-INVESTMENT-ANALYZER/issues/207) | 不要テストの削除と統合                       | P2     | フェーズ3    |
| [#208](https://github.com/TIMMY-WEST/STOCK-INVESTMENT-ANALYZER/issues/208) | テストカバレッジの向上（サービス層）         | P2     | フェーズ3    |
| [#209](https://github.com/TIMMY-WEST/STOCK-INVESTMENT-ANALYZER/issues/209) | E2Eテストの整備                              | P2     | フェーズ4    |
| [#210](https://github.com/TIMMY-WEST/STOCK-INVESTMENT-ANALYZER/issues/210) | GitHub Actionsワークフローの作成             | P2     | フェーズ4    |
| [#211](https://github.com/TIMMY-WEST/STOCK-INVESTMENT-ANALYZER/issues/211) | 品質ゲートの設定                             | P2     | フェーズ4    |
| [#212](https://github.com/TIMMY-WEST/STOCK-INVESTMENT-ANALYZER/issues/212) | CI/CDドキュメントの作成                      | P2     | フェーズ4    |

### 8.2 新規Issue推奨

以下のIssueを新規作成することを推奨:

1. **テストマーカーの一括追加**
   - タイトル: `[REFACTOR] テストマーカーの一括追加`
   - 優先度: P1
   - 見積もり: Small（3-4日）

2. **unittest から pytest への移行**
   - タイトル: `[REFACTOR] unittest から pytest への移行`
   - 優先度: P1
   - 見積もり: Small（2-3日）

3. **テストスキップの解決**
   - タイトル: `[FIX] 恒久的にスキップされているテストの解決`
   - 優先度: P1
   - 見積もり: Small（1-2日）

---

## 9. 参考情報

### 9.1 関連ドキュメント

- [テスト戦略](../development/testing_strategy.md)
- [テストガイド](testing_guide.md)
- [コーディング規約](../development/coding_standards.md)
- [GitHub Workflow](../development/github_workflow.md)

### 9.2 参考資料

- [pytest ドキュメント](https://docs.pytest.org/)
- [pytest-cov ドキュメント](https://pytest-cov.readthedocs.io/)
- [AAAパターンのベストプラクティス](https://docs.pytest.org/en/latest/explanation/anatomy.html)

---

**最終更新**: 2025-10-29
**文書バージョン**: v1.0.0
**次回見直し**: フェーズ1完了時
