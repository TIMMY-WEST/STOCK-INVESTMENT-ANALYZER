# CI/CDパイプライン設定

## 📋 目次

- [概要](#概要)
- [パイプライン全体像](#パイプライン全体像)
- [GitHub Actionsワークフロー](#github-actionsワークフロー)
- [Pre-commit Hooks](#pre-commit-hooks)
- [品質ゲート](#品質ゲート)
- [環境変数とシークレット](#環境変数とシークレット)
- [トラブルシューティング](#トラブルシューティング)
---
## 概要

**最終更新**: 2025-11-02
**文書バージョン**: v2.0.0
**AI優先度**: 高

本ドキュメントは、CI/CDパイプラインの設定と運用に関する詳細な情報を提供します。
`ci-cd/pipeline_overview.md`と`ci-cd/troubleshooting.md`の内容を統合しています。
---
## パイプライン全体像

### 2層構造

```
┌─────────────────────────────────────────────────────────────┐
│                    開発者のローカル環境                      │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  コード変更 → git add → git commit                            │
│                          ↓                                    │
│                   Pre-commit Hooks                            │
│                   ├─ Black (フォーマット)                     │
│                   ├─ isort (インポート整理)                   │
│                   ├─ flake8 (Linter)                         │
│                   ├─ 複雑度チェック                           │
│                   └─ mypy (型チェック)                        │
│                          ↓                                    │
│                   git push                                    │
│                                                               │
└─────────────────────────────────────────────────────────────┘
                          │
                          ↓
┌─────────────────────────────────────────────────────────────┐
│                    GitHub (リモート環境)                      │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  Push/Pull Request イベント                                   │
│      ↓                                                        │
│  GitHub Actions ワークフロー起動                               │
│      ├─ 環境セットアップ                                       │
│      ├─ PostgreSQL サービス起動                                │
│      ├─ テスト実行                                             │
│      └─ カバレッジレポート保存                                  │
│      ↓                                                        │
│  品質ゲートチェック                                             │
│      ├─ カバレッジ 70%以上                                     │
│      ├─ 全テスト通過                                           │
│      └─ Linterエラーなし                                       │
│      ↓                                                        │
│  マージ可能 ✅                                                 │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```
---
## GitHub Actionsワークフロー

### ワークフローファイル

**ファイルパス**: `.github/workflows/quality.yml`

**トリガー条件**:
```yaml
on:
  push:
    branches: ["**"]  # すべてのブランチへのpush
  pull_request:
    branches: ["**"]  # すべてのブランチへのPR
```

### ジョブ構成

#### Job: test (テスト実行)

**実行環境**: `ubuntu-latest`

**ステップ詳細**:

##### 1. 環境セットアップ

```yaml
- name: Checkout repository
  uses: actions/checkout@v4

- name: Set up Python 3.11
  uses: actions/setup-python@v4
  with:
    python-version: '3.11'

- name: Cache pip packages
  uses: actions/cache@v4
  with:
    path: ~/.cache/pip
    key: ${{ runner.os }}-pip-${{ hashFiles('**/requirements*.txt') }}

- name: Install dependencies
  run: |
    python -m pip install --upgrade pip
    pip install -r requirements.txt
    pip install -r requirements-dev.txt
```

##### 2. PostgreSQLサービス起動

```yaml
services:
  postgres:
    image: postgres:14
    env:
      POSTGRES_USER: stock_user
      POSTGRES_PASSWORD: stock_password
      POSTGRES_DB: stock_data_system
    options: >-
      --health-cmd pg_isready
      --health-interval 10s
      --health-timeout 5s
      --health-retries 5
    ports:
      - 5432:5432
```

##### 3. テスト実行

```yaml
- name: Run tests with coverage
  env:
    DB_HOST: localhost
    DB_PORT: 5432
    DB_USER: stock_user
    DB_PASSWORD: stock_password
    DB_NAME: stock_data_system
  run: |
    pytest -m "not e2e" \
      --verbosity=1 \
      --maxfail=1 \
      --cov=app \
      --cov-report=xml \
      --cov-report=term \
      --cov-fail-under=70
```

**テストオプション**:
| オプション            | 説明                            |
| --------------------- | ------------------------------- |
| `-m "not e2e"`        | E2Eテストを除外                 |
| `--verbosity=1`       | 標準的な詳細度                  |
| `--maxfail=1`         | 最初の失敗で即座に停止          |
| `--cov=app`           | appディレクトリのカバレッジ計測 |
| `--cov-fail-under=70` | カバレッジ70%未満で失敗         |

##### 4. カバレッジレポート保存

```yaml
- name: Upload coverage report
  uses: actions/upload-artifact@v4
  with:
    name: coverage-report
    path: coverage.xml
```
---
## Pre-commit Hooks

### セットアップ

**インストール**:
```bash
pip install pre-commit
pre-commit install
```

**設定ファイル**: `.pre-commit-config.yaml`

### 実行されるチェック

#### 1. 基本チェック

| チェック項目            | 内容                             | 修正 |
| ----------------------- | -------------------------------- | ---- |
| end-of-file-fixer       | ファイル末尾の空行を統一         | 自動 |
| trailing-whitespace     | 行末の空白を削除                 | 自動 |
| check-merge-conflict    | マージコンフリクトマーカーの検出 | 手動 |
| check-yaml/json/toml    | 設定ファイルの構文チェック       | 手動 |
| check-added-large-files | 大きなファイル(500KB以上)の検出  | 手動 |

#### 2. コードフォーマット

```bash
# Black - PEP 8準拠の自動フォーマット
black app/ --line-length 79

# isort - インポート文の自動整理
isort app/ --profile black --line-length 79
```

#### 3. 静的解析

```bash
# flake8 - コーディング規約チェック
flake8 app/ --max-line-length=79 --max-complexity=10

# mypy - 型ヒントチェック
mypy app/
```

### 手動実行

```bash
# すべてのファイルに対して実行
pre-commit run --all-files

# 特定のフックのみ実行
pre-commit run black --all-files
pre-commit run flake8 --all-files

# 詳細なログを表示
pre-commit run --all-files --verbose
```

### スキップ（緊急時のみ）

```bash
git commit -m "your message" --no-verify
```

**注意**: `--no-verify`は品質チェックをスキップするため、CI環境でエラーになる可能性があります。
---
## 品質ゲート

### カバレッジ品質ゲート

**基準**: コードカバレッジ 70%以上

**チェックタイミング**: GitHub Actions (CI環境)

**失敗時の動作**:
- テストジョブが失敗
- PRマージがブロック (ブランチ保護ルールが有効な場合)
- 開発者はカバレッジを向上させる必要あり

### 複雑度品質ゲート

**基準**: McCabe複雑度 10以下

**チェックタイミング**: Pre-commit Hooks (ローカル)、flake8 (CI環境)

**失敗時の動作**:
- コミットがブロック (pre-commit)
- 開発者はコードをリファクタリングして複雑度を下げる必要あり

### 型チェック品質ゲート

**基準**: mypy型チェックエラーなし

**チェックタイミング**: Pre-commit Hooks (ローカル)

**失敗時の動作**:
- 警告を表示するが、コミットはブロックしない (現在の設定)
- 開発者は型ヒントを追加・修正することを推奨
---
## 環境変数とシークレット

### 必要な環境変数

**CI環境**:
```yaml
DB_HOST: localhost
DB_PORT: 5432
DB_USER: stock_user
DB_PASSWORD: stock_password
DB_NAME: stock_data_system
```

### GitHubシークレットの設定

1. リポジトリ設定 → Secrets and variables → Actions
2. New repository secret をクリック
3. Name と Value を入力
4. Add secret をクリック

**デバッグモード有効化**:
- Name: `ACTIONS_RUNNER_DEBUG`, Value: `true`
- Name: `ACTIONS_STEP_DEBUG`, Value: `true`
---
## トラブルシューティング

### Pre-commit Hooks のトラブルシューティング

#### エラー1: Pre-commit フックが実行されない

**症状**:
```bash
$ git commit -m "test"
# pre-commitフックが実行されずにコミットされる
```

**解決策**:
```bash
# Pre-commitインストール確認
pre-commit --version

# インストールされていない場合
pip install pre-commit

# フックを有効化
pre-commit install

# 確認
ls -la .git/hooks/pre-commit
```

#### エラー2: Black フォーマットエラー

**症状**:
```
would reformat <file_path>
```

**解決策**:
```bash
# 自動修正
black app/ --line-length 79

# 再コミット
git add .
git commit -m "your message"
```

#### エラー3: flake8 Linter エラー

**よくあるエラーと解決策**:

| エラーコード | 内容                 | 解決策                   |
| ------------ | -------------------- | ------------------------ |
| E302         | 関数定義前の空行不足 | 関数定義の前に2行空ける  |
| E501         | 行が長すぎる         | 行を79文字以内に分割     |
| F401         | 未使用のインポート   | 不要なインポート文を削除 |
| W293         | 空白行に空白文字     | 空白行から空白文字を削除 |

#### エラー4: 複雑度エラー (McCabe)

**症状**:
```
app/example.py:10:1: C901 'function_name' is too complex (12)
```

**解決策**:
- 大きな関数を小さな関数に分割
- 条件分岐を減らす (早期return、辞書マッピング等)
- ループのネストを減らす

### GitHub Actions のトラブルシューティング

#### エラー11: テスト失敗

**症状**:
```
FAILED tests/test_example.py::test_function - AssertionError: ...
```

**解決策**:
```bash
# ローカルでテストを実行
pytest tests/test_example.py::test_function -v

# エラーを修正後、再度テスト
pytest tests/test_example.py::test_function -v

# 成功を確認後、push
git add .
git commit -m "fix: テストエラーを修正"
git push
```

#### エラー12: カバレッジ不足

**症状**:
```
FAIL Required test coverage of 70% not reached. Total coverage: 65.23%
```

**解決策**:
```bash
# カバレッジレポートを確認
pytest --cov=app --cov-report=html

# HTMLレポートを開く
# htmlcov/index.html をブラウザで開く

# 不足しているテストケースを追加

# カバレッジを再確認
pytest --cov=app --cov-report=term
```

#### エラー13: データベース接続エラー

**症状**:
```
psycopg2.OperationalError: could not connect to server
```

**解決策**:

**ローカル環境**:
```bash
# PostgreSQL起動確認
pg_ctl status  # Windows
sudo systemctl status postgresql  # Linux/macOS

# 起動していない場合
pg_ctl start  # Windows
sudo systemctl start postgresql  # Linux/macOS
```

**CI環境**:
`.github/workflows/quality.yml`の設定を確認

#### エラー15: キャッシュの問題

**解決策**:
1. GitHub Actions のキャッシュを削除
   - GitHubリポジトリページ → Actions → Caches
   - 該当するキャッシュを削除
2. ワークフローを再実行
---
## デバッグ方法

### GitHub Actions でのデバッグ

#### 1. ワークフローログの確認

1. GitHubリポジトリページ → Actions
2. 失敗したワークフローをクリック
3. 失敗したジョブをクリック
4. 各ステップのログを確認

#### 2. デバッグモードの有効化

1. リポジトリ設定 → Secrets and variables → Actions
2. New repository secret をクリック
3. Name: `ACTIONS_RUNNER_DEBUG`, Value: `true`
4. Add secret をクリック
---
## まとめ

本プロジェクトのCI/CDパイプラインは、以下の2層構造で品質を保証しています:

1. **ローカル層 (Pre-commit Hooks)**:
   - コミット前に基本的な品質チェックを実施
   - 開発者に即座にフィードバック
   - コードフォーマットの統一

2. **リモート層 (GitHub Actions)**:
   - テストの自動実行
   - カバレッジの計測と品質ゲート
   - 統合的な品質保証
---
## 関連ドキュメント

- [テスト規約](../standards/testing-standards.md) - テスト作成ガイドライン
- [コーディング規約](../standards/coding-standards.md) - コーディング規約
- [開発ワークフロー](../guides/development-workflow.md) - 開発フロー全体
- [トラブルシューティング](../guides/troubleshooting.md) - 全般的な問題解決
---
**最終更新**: 2025-11-02
**文書バージョン**: v2.0.0
