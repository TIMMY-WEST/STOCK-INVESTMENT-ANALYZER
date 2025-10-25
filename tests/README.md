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
```

### フィクスチャの利用

共通フィクスチャは `conftest.py` で定義されています。

```python
def test_with_client(client):
    """Flaskテストクライアントを使用する例"""
    response = client.get('/api/endpoint')
    assert response.status_code == 200
```

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
