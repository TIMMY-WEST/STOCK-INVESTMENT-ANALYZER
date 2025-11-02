---
category: ci-cd
ai_context: high
last_updated: 2025-11-02
related_docs:
  - pipeline_overview.md
  - ../development/pre_commit_setup.md
  - ../development/testing_guide.md
---

# CI/CD トラブルシューティングガイド

## 📋 目次

- [概要](#概要)
- [Pre-commit Hooks のトラブルシューティング](#pre-commit-hooks-のトラブルシューティング)
- [GitHub Actions のトラブルシューティング](#github-actions-のトラブルシューティング)
- [デバッグ方法](#デバッグ方法)
- [よくある質問 (FAQ)](#よくある質問-faq)

## 概要

このドキュメントでは、CI/CDパイプラインで発生する一般的なエラーと解決方法を説明します。

### トラブルシューティングの基本フロー

```
エラー発生
    ↓
エラーメッセージを確認
    ↓
該当するエラーケースを探す
    ↓
解決策を試す
    ↓
問題が解決しない場合
    ↓
デバッグ方法セクションを参照
```

## Pre-commit Hooks のトラブルシューティング

### エラー1: Pre-commit フックが実行されない

**症状**:
```bash
$ git commit -m "test"
# pre-commitフックが実行されずにコミットされる
```

**原因**:
- Pre-commitがインストールされていない
- Pre-commitフックが有効化されていない

**解決策**:

1. Pre-commitがインストールされているか確認:
```bash
pre-commit --version
```

2. インストールされていない場合:
```bash
pip install pre-commit
```

3. フックを有効化:
```bash
pre-commit install
```

4. 確認:
```bash
ls -la .git/hooks/pre-commit
```

### エラー2: Black フォーマットエラー

**症状**:
```
would reformat <file_path>
1 file would be reformatted
```

**原因**:
- コードがBlackのフォーマット規則に従っていない

**解決策**:

1. 自動修正:
```bash
black app/ --line-length 79
```

2. 特定ファイルのみ修正:
```bash
black <file_path> --line-length 79
```

3. 再コミット:
```bash
git add .
git commit -m "your message"
```

**注意点**:
- 行の長さは79文字に設定されています
- Blackは自動修正可能なので、エラーが出たら実行するだけでOK

### エラー3: isort インポート整理エラー

**症状**:
```
ERROR: <file_path> Imports are incorrectly sorted and/or formatted.
```

**原因**:
- インポート文の順序が不正

**解決策**:

1. 自動修正:
```bash
isort app/ --profile black --line-length 79
```

2. 特定ファイルのみ修正:
```bash
isort <file_path> --profile black --line-length 79
```

3. 再コミット:
```bash
git add .
git commit -m "your message"
```

### エラー4: flake8 Linter エラー

**症状**:
```
app/example.py:10:1: E302 expected 2 blank lines, found 1
app/example.py:15:80: E501 line too long (85 > 79 characters)
app/example.py:20:1: F401 'os' imported but unused
```

**原因**:
- コーディング規約違反

**よくあるエラーコードと解決策**:

| エラーコード | 内容 | 解決策 |
|-------------|------|--------|
| E302 | 関数定義前の空行不足 | 関数定義の前に2行空ける |
| E501 | 行が長すぎる | 行を79文字以内に分割 |
| F401 | 未使用のインポート | 不要なインポート文を削除 |
| E722 | bare except | `except Exception as e:` に変更 |
| W293 | 空白行に空白文字 | 空白行から空白文字を削除 |

**解決策**:

1. エラーを確認:
```bash
flake8 app/ --statistics
```

2. 自動修正可能なものはBlackで修正:
```bash
black app/ --line-length 79
```

3. 手動で修正が必要なものは該当箇所を修正

4. 再確認:
```bash
flake8 app/
```

### エラー5: 複雑度エラー (McCabe)

**症状**:
```
app/example.py:10:1: C901 'function_name' is too complex (12)
```

**原因**:
- 関数の複雑度が10を超えている

**解決策**:

1. 複雑度を確認:
```bash
flake8 app/ --select=C901 --show-source
```

2. リファクタリング方法:
   - 大きな関数を小さな関数に分割
   - 条件分岐を減らす (早期return、辞書マッピング等)
   - ループのネストを減らす

**例**:

修正前 (複雑度が高い):
```python
def process_data(data, option):
    if option == "A":
        if data > 0:
            # 処理A-1
            pass
        else:
            # 処理A-2
            pass
    elif option == "B":
        if data > 0:
            # 処理B-1
            pass
        else:
            # 処理B-2
            pass
    # ... (さらに多くの分岐)
```

修正後 (複雑度が低い):
```python
def process_data(data, option):
    # 辞書マッピングで分岐を減らす
    processors = {
        ("A", True): process_a_positive,
        ("A", False): process_a_negative,
        ("B", True): process_b_positive,
        ("B", False): process_b_negative,
    }

    key = (option, data > 0)
    processor = processors.get(key)
    if processor:
        return processor(data)

    raise ValueError(f"Invalid option: {option}")

def process_a_positive(data):
    # 処理A-1
    pass

def process_a_negative(data):
    # 処理A-2
    pass
```

### エラー6: mypy 型チェックエラー

**症状**:
```
app/example.py:10: error: Incompatible return value type (got "str", expected "int")
app/example.py:15: error: Argument 1 to "function" has incompatible type "int"; expected "str"
```

**原因**:
- 型ヒントと実際の型が一致していない

**解決策**:

1. エラーを確認:
```bash
mypy app/
```

2. 型ヒントを修正:
```python
# 修正前
def get_value(key: str):  # 戻り値の型ヒントがない
    return 123

# 修正後
def get_value(key: str) -> int:  # 戻り値の型ヒントを追加
    return 123
```

3. 型が複雑な場合:
```python
from typing import Optional, List, Dict

def process_items(items: List[str]) -> Dict[str, int]:
    return {item: len(item) for item in items}

def get_user(user_id: int) -> Optional[dict]:
    # ユーザーが存在しない場合はNoneを返す
    return {"id": user_id} if user_id > 0 else None
```

**参考**: [型ヒントガイド](../development/type_hints_guide.md)

### エラー7: マージコンフリクトマーカーの検出

**症状**:
```
app/example.py:10: Found conflict marker
```

**原因**:
- マージコンフリクトの解決時に残ったマーカー (`<<<<<<<`, `=======`, `>>>>>>>`)

**解決策**:

1. 該当ファイルを開いてマーカーを検索:
```bash
grep -n "<<<<<<< " app/example.py
```

2. マーカーを手動で削除し、適切なコードに修正

3. 再コミット

### エラー8: 大きなファイルの追加

**症状**:
```
large_file.csv (5000 KB) exceeds 500 KB.
```

**原因**:
- 500KBを超えるファイルをコミットしようとしている

**解決策**:

1. ファイルが本当に必要か確認

2. 不要な場合は`.gitignore`に追加:
```bash
echo "large_file.csv" >> .gitignore
git add .gitignore
```

3. 必要な場合:
   - Git LFS (Large File Storage) を使用
   - ファイルを分割
   - 外部ストレージに保存してURLで参照

### エラー9: Pre-commit フック実行時間が長い

**症状**:
- コミット時に30秒以上かかる

**原因**:
- チェック対象のファイル数が多い
- キャッシュが無効

**解決策**:

1. 特定のファイルのみコミット:
```bash
git add <specific_file>
git commit -m "your message"
```

2. フックをスキップ (緊急時のみ):
```bash
git commit -m "your message" --no-verify
```

**注意**: `--no-verify`は品質チェックをスキップするため、CI環境でエラーになる可能性があります。

### エラー10: Python バージョン不一致

**症状**:
```
ERROR: Python 3.11 is required but 3.9 is installed
```

**原因**:
- システムのPythonバージョンが要件を満たしていない

**解決策**:

1. Pythonバージョンを確認:
```bash
python --version
```

2. Python 3.11をインストール:
   - Windows: https://www.python.org/downloads/
   - macOS: `brew install python@3.11`
   - Linux: `sudo apt install python3.11`

3. 仮想環境を再作成:
```bash
# 既存の仮想環境を削除
rm -rf venv

# Python 3.11で仮想環境を作成
python3.11 -m venv venv

# 仮想環境を有効化
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate     # Windows

# 依存パッケージを再インストール
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

## GitHub Actions のトラブルシューティング

### エラー11: テスト失敗

**症状**:
```
FAILED tests/test_example.py::test_function - AssertionError: ...
```

**原因**:
- テストケースが失敗している

**解決策**:

1. ローカルでテストを実行:
```bash
pytest tests/test_example.py::test_function -v
```

2. エラーメッセージを確認:
   - `AssertionError`: 期待値と実際の値が一致しない
   - `AttributeError`: 存在しないメソッド/属性にアクセス
   - `ImportError`: モジュールのインポート失敗

3. テストまたはコードを修正

4. 再度テスト実行:
```bash
pytest tests/test_example.py::test_function -v
```

5. 成功を確認後、push:
```bash
git add .
git commit -m "fix: テストエラーを修正"
git push
```

### エラー12: カバレッジ不足

**症状**:
```
FAIL Required test coverage of 70% not reached. Total coverage: 65.23%
```

**原因**:
- テストカバレッジが70%未満

**解決策**:

1. カバレッジレポートを確認:
```bash
pytest --cov=app --cov-report=term-missing --cov-report=html
```

2. HTMLレポートを開く:
```bash
# ブラウザで htmlcov/index.html を開く
```

3. カバレッジが低いファイルを確認

4. 不足しているテストケースを追加:
   - テストされていない関数・メソッドを特定
   - テストされていない分岐(if文、例外処理等)を特定
   - テストケースを追加

5. カバレッジを再確認:
```bash
pytest --cov=app --cov-report=term
```

6. 70%以上になったことを確認後、push

**参考**: [テスト作成ガイドライン](../development/testing_guide.md)

### エラー13: データベース接続エラー

**症状**:
```
psycopg2.OperationalError: could not connect to server: Connection refused
```

**原因**:
- PostgreSQLサービスが起動していない
- 接続情報が正しくない

**GitHub Actions での解決策**:

1. ワークフローファイル(`.github/workflows/quality.yml`)を確認:
   - PostgreSQLサービスが定義されているか
   - ヘルスチェックが正しく設定されているか

2. 環境変数を確認:
```yaml
env:
  DB_HOST: localhost
  DB_PORT: 5432
  DB_USER: stock_user
  DB_PASSWORD: stock_password
  DB_NAME: stock_data_system
```

3. データベースセットアップステップが実行されているか確認

**ローカル環境での解決策**:

1. PostgreSQLが起動しているか確認:
```bash
# Windows
pg_ctl status

# macOS/Linux
sudo systemctl status postgresql
```

2. 起動していない場合は起動:
```bash
# Windows
pg_ctl start

# macOS/Linux
sudo systemctl start postgresql
```

3. 接続情報を確認:
```bash
psql -h localhost -U stock_user -d stock_data_system
```

### エラー14: 依存パッケージのインストール失敗

**症状**:
```
ERROR: Could not find a version that satisfies the requirement <package>
```

**原因**:
- パッケージ名が間違っている
- パッケージのバージョンが存在しない
- Pythonバージョンとの互換性がない

**解決策**:

1. `requirements.txt`を確認:
```bash
cat requirements.txt | grep <package>
```

2. パッケージが存在するか確認:
```bash
pip search <package>
```

3. パッケージ名・バージョンを修正:
```
# 修正前
nonexistent-package==1.0.0

# 修正後
existing-package==2.0.0
```

4. ローカルでインストール確認:
```bash
pip install -r requirements.txt
```

5. 成功を確認後、push

### エラー15: キャッシュの問題

**症状**:
- 依存パッケージのインストールが異常に遅い
- 古いパッケージバージョンが使用される

**原因**:
- キャッシュが破損している
- キャッシュキーが正しくない

**解決策**:

1. GitHub Actionsのキャッシュを削除:
   - GitHubリポジトリページ → Actions → Caches
   - 該当するキャッシュを削除

2. ワークフローを再実行

3. キャッシュキーを確認 (`.github/workflows/quality.yml`):
```yaml
- name: Cache pip packages
  uses: actions/cache@v4
  with:
    path: ~/.cache/pip
    key: ${{ runner.os }}-pip-${{ hashFiles('**/requirements*.txt') }}
```

### エラー16: タイムアウト

**症状**:
```
The job running on runner has exceeded the maximum execution time of 360 minutes.
```

**原因**:
- ワークフローが6時間を超えて実行された

**解決策**:

1. ワークフローログを確認し、どこで時間がかかっているか特定

2. タイムアウトの原因:
   - 無限ループ
   - 外部APIの応答待ち
   - 大量のテストケース

3. 対処方法:
   - 無限ループを修正
   - タイムアウト設定を追加 (`pytest --timeout=300`)
   - テストを分割して並列実行

### エラー17: ワークフローファイルの構文エラー

**症状**:
```
Invalid workflow file: .github/workflows/quality.yml
```

**原因**:
- YAMLファイルの構文エラー
- インデントが正しくない

**解決策**:

1. YAMLの構文チェック:
```bash
# オンラインツール: https://www.yamllint.com/
# または
yamllint .github/workflows/quality.yml
```

2. よくあるエラー:
   - タブとスペースの混在 (スペースのみ使用)
   - インデントのずれ (2スペース単位)
   - クォートの不一致
   - コロンの後のスペース不足

3. 修正例:
```yaml
# エラー
jobs:
test:
  name: Run Tests

# 正解
jobs:
  test:
    name: Run Tests
```

### エラー18: 環境変数が設定されていない

**症状**:
```
KeyError: 'DB_HOST'
```

**原因**:
- 必要な環境変数が設定されていない

**解決策**:

1. ワークフローファイルで環境変数を確認:
```yaml
- name: Run tests
  env:
    DB_HOST: localhost
    DB_PORT: 5432
    # ... 他の環境変数
```

2. 環境変数が正しく設定されているか確認

3. コード内で環境変数を取得する際は、デフォルト値を設定:
```python
import os

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = int(os.getenv("DB_PORT", "5432"))
```

### エラー19: アーティファクトのアップロード失敗

**症状**:
```
Error: Unable to upload artifact
```

**原因**:
- ファイルパスが間違っている
- ファイルが存在しない
- ファイルサイズが大きすぎる (10GB制限)

**解決策**:

1. ファイルパスを確認:
```yaml
- name: Upload coverage report
  uses: actions/upload-artifact@v4
  with:
    name: coverage-report
    path: coverage.xml  # パスが正しいか確認
```

2. ファイルが生成されているか確認:
```yaml
- name: Check file exists
  run: |
    ls -la coverage.xml
```

3. ファイルサイズを確認:
```bash
du -h coverage.xml
```

### エラー20: ブランチ保護ルールによるマージブロック

**症状**:
- PRマージボタンがグレーアウト
- "Required status checks must pass"

**原因**:
- ブランチ保護ルールが有効
- 必須のステータスチェックが失敗

**解決策**:

1. ステータスチェックを確認:
   - PRページの "Checks" タブを開く
   - 失敗しているチェックを確認

2. 失敗しているチェックを修正:
   - テスト失敗 → テストを修正
   - カバレッジ不足 → テストを追加
   - Linterエラー → コードを修正

3. 修正をpush:
```bash
git add .
git commit -m "fix: ステータスチェックエラーを修正"
git push
```

4. ワークフローが再実行され、成功すればマージ可能

**参考**: [ブランチ保護ルール](../development/branch_protection_rules.md)

## デバッグ方法

### ローカルでのデバッグ

#### 1. Pre-commit を手動実行

すべてのファイルに対してPre-commitを実行:
```bash
pre-commit run --all-files
```

特定のフックのみ実行:
```bash
pre-commit run black --all-files
pre-commit run flake8 --all-files
pre-commit run mypy --all-files
```

詳細なログを表示:
```bash
pre-commit run --all-files --verbose
```

#### 2. テストをローカルで実行

すべてのテストを実行:
```bash
pytest
```

特定のテストファイルのみ実行:
```bash
pytest tests/test_example.py
```

特定のテスト関数のみ実行:
```bash
pytest tests/test_example.py::test_function_name
```

詳細な出力:
```bash
pytest -v
```

最初の失敗で停止:
```bash
pytest --maxfail=1
```

カバレッジ付きで実行:
```bash
pytest --cov=app --cov-report=term --cov-report=html
```

#### 3. GitHub Actions をローカルで実行

`act` ツールを使用してGitHub Actionsをローカルで実行:

1. `act` をインストール:
```bash
# macOS
brew install act

# Windows (Chocolatey)
choco install act-cli

# Linux
curl -s https://raw.githubusercontent.com/nektos/act/master/install.sh | sudo bash
```

2. ワークフローを実行:
```bash
# すべてのワークフローを実行
act

# 特定のイベントをトリガー
act push

# 特定のジョブのみ実行
act -j test
```

**注意**: PostgreSQLサービスコンテナを使用するため、Dockerが必要です。

### GitHub Actions でのデバッグ

#### 1. ワークフローログの確認

1. GitHubリポジトリページ → Actions
2. 失敗したワークフローをクリック
3. 失敗したジョブをクリック
4. 各ステップのログを確認

#### 2. デバッグモードの有効化

より詳細なログを表示:

1. リポジトリ設定 → Secrets and variables → Actions
2. New repository secret をクリック
3. Name: `ACTIONS_RUNNER_DEBUG`, Value: `true`
4. Add secret をクリック

次回のワークフロー実行時に、詳細なデバッグログが表示されます。

#### 3. ステップ実行モードの有効化

各ステップの実行詳細を表示:

1. リポジトリ設定 → Secrets and variables → Actions
2. New repository secret をクリック
3. Name: `ACTIONS_STEP_DEBUG`, Value: `true`
4. Add secret をクリック

#### 4. SSH でデバッグ

`tmate` を使用してワークフロー実行中にSSH接続:

```yaml
- name: Setup tmate session
  uses: mxschmitt/action-tmate@v3
```

**注意**: セキュリティリスクがあるため、公開リポジトリでは使用を推奨しません。

### よくあるデバッグテクニック

#### 1. ログ出力を追加

**Pythonコード**:
```python
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def my_function():
    logger.debug("デバッグ情報")
    logger.info("情報")
    logger.warning("警告")
    logger.error("エラー")
```

**テストコード**:
```python
def test_my_function(caplog):
    with caplog.at_level(logging.DEBUG):
        my_function()

    assert "デバッグ情報" in caplog.text
```

#### 2. ブレークポイントを設定

**ローカルテスト**:
```python
def test_my_function():
    # ブレークポイント
    breakpoint()

    result = my_function()
    assert result == expected
```

実行:
```bash
pytest tests/test_example.py::test_my_function
```

pdbデバッガが起動します:
```
(Pdb) n          # 次の行へ
(Pdb) s          # ステップイン
(Pdb) c          # 続行
(Pdb) p variable # 変数の値を表示
(Pdb) l          # 現在の位置を表示
(Pdb) h          # ヘルプ
```

#### 3. printデバッグ (簡易デバッグ)

```python
def my_function(data):
    print(f"DEBUG: data = {data}")

    result = process(data)
    print(f"DEBUG: result = {result}")

    return result
```

**注意**: デバッグ後は必ずprint文を削除してください。Pre-commitフックで検出されます。

## よくある質問 (FAQ)

### Q1: コミット時にPre-commitフックをスキップしたい

**A**: `--no-verify` オプションを使用します:
```bash
git commit -m "your message" --no-verify
```

**注意**: CI環境でエラーになる可能性があるため、緊急時のみ使用してください。

### Q2: カバレッジ70%は厳しすぎる。変更できますか?

**A**: 変更可能ですが、推奨しません。カバレッジ基準を下げると、バグの検出率が低下します。
カバレッジ不足の場合は、テストケースを追加することを推奨します。

変更する場合は、`.github/workflows/quality.yml` の以下の部分を修正:
```yaml
--cov-fail-under=70  # この値を変更
```

### Q3: GitHub Actionsの実行時間を短縮したい

**A**: 以下の方法があります:

1. **キャッシュの活用**: 既に設定済み
2. **テストの並列実行**:
```yaml
strategy:
  matrix:
    python-version: [3.11]
    test-group: [unit, integration]
```
3. **不要なテストのスキップ**: E2Eテストは既に除外済み

### Q4: ローカル環境とCI環境で結果が異なる

**A**: 原因:
- Pythonバージョンの違い
- 依存パッケージのバージョンの違い
- 環境変数の違い

解決策:
```bash
# Pythonバージョンを確認
python --version  # 3.11であることを確認

# 依存パッケージを最新化
pip install -r requirements.txt -r requirements-dev.txt --upgrade

# 環境変数を確認
env | grep DB_
```

### Q5: テストが不安定 (flaky test)

**A**: 原因:
- テスト間で状態が共有されている
- タイミング依存のテスト
- 外部APIへの依存

解決策:
- フィクスチャで状態を初期化
- モックを使用して外部依存を排除
- `pytest-randomly` を使用してランダムな順序でテストを実行

```bash
pip install pytest-randomly
pytest --randomly-seed=12345
```

### Q6: Pre-commitフックが遅い

**A**: 解決策:
1. 特定のフックのみ実行:
```bash
SKIP=mypy git commit -m "your message"
```

2. ファイルを分割してコミット:
```bash
git add file1.py
git commit -m "update file1"

git add file2.py
git commit -m "update file2"
```

### Q7: エラーメッセージが分かりにくい

**A**: 詳細なログを表示:

**Pre-commit**:
```bash
pre-commit run --all-files --verbose
```

**pytest**:
```bash
pytest -vv  # 非常に詳細
pytest -v   # 詳細
pytest      # 通常
```

**flake8**:
```bash
flake8 app/ --show-source  # エラー箇所のソースコードを表示
```

### Q8: 複数のエラーを一度に修正したい

**A**: 以下の順序で修正することを推奨:

1. **自動修正可能なもの**:
```bash
black app/ --line-length 79
isort app/ --profile black --line-length 79
```

2. **構文エラー**:
```bash
flake8 app/
```

3. **型エラー**:
```bash
mypy app/
```

4. **テストエラー**:
```bash
pytest
```

### Q9: GitHub Actionsのコストが心配

**A**: GitHubの無料枠:
- Public リポジトリ: 無制限
- Private リポジトリ: 月2,000分

本プロジェクトの1回のワークフロー実行: 約3〜5分

コスト削減策:
- 不要なブランチへのpushを避ける
- PRをdraftで作成し、準備完了後にready for reviewにする

### Q10: 特定のファイルをチェック対象から除外したい

**A**: `.pre-commit-config.yaml` の `exclude` を設定:

```yaml
- id: black
  exclude: ^(venv/|\.venv/|migrations/|specific_file.py)
```

または、`.flake8` ファイルで除外:
```ini
[flake8]
exclude =
    venv/,
    .venv/,
    migrations/,
    specific_file.py
```

## まとめ

CI/CDパイプラインのトラブルシューティングでは、以下の流れで対応することを推奨します:

1. **エラーメッセージを確認**: 何が問題なのかを把握
2. **該当するエラーケースを探す**: このドキュメントから解決策を探す
3. **ローカルで再現**: ローカル環境で問題を再現し、デバッグ
4. **修正と確認**: 修正後、ローカルでテストを実行
5. **Push**: 成功を確認後、GitHub にpush

問題が解決しない場合は:
- GitHub Issuesで質問
- プロジェクトメンバーに相談
- 関連ドキュメントを参照

## 関連ドキュメント

- [CI/CDパイプライン概要](pipeline_overview.md)
- [Pre-commit セットアップガイド](../development/pre_commit_setup.md)
- [テスト作成ガイドライン](../development/testing_guide.md)
- [コーディング規約](../development/coding_standards.md)
- [型ヒントガイド](../development/type_hints_guide.md)
