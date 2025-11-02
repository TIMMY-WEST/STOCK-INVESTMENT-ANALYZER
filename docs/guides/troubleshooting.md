# トラブルシューティングガイド

## 📋 目次

- [概要](#概要)
- [開発環境の問題](#開発環境の問題)
- [テスト実行の問題](#テスト実行の問題)
- [CI/CDパイプラインの問題](#cicdパイプラインの問題)
- [データベースの問題](#データベースの問題)
- [APIの問題](#apiの問題)
- [デバッグ方法](#デバッグ方法)

---

## 概要

**最終更新**: 2025-11-02
**文書バージョン**: v2.0.0
**AI優先度**: 中

本ドキュメントは、開発中に発生する一般的な問題と解決方法を提供します。

---

## 開発環境の問題

### Python バージョン不一致

**症状**:
```
ERROR: Python 3.11 is required but 3.9 is installed
```

**原因**: システムのPythonバージョンが要件を満たしていない

**解決策**:
```bash
# Pythonバージョンを確認
python --version

# Python 3.11をインストール
# Windows: https://www.python.org/downloads/
# macOS: brew install python@3.11
# Linux: sudo apt install python3.11

# 仮想環境を再作成
rm -rf venv
python3.11 -m venv venv

# 仮想環境を有効化
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate     # Windows

# 依存パッケージを再インストール
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

### 依存パッケージのインストール失敗

**症状**:
```
ERROR: Could not find a version that satisfies the requirement <package>
```

**原因**:
- パッケージ名が間違っている
- パッケージのバージョンが存在しない
- Pythonバージョンとの互換性がない

**解決策**:
```bash
# requirements.txtを確認
cat requirements.txt | grep <package>

# ローカルでインストール確認
pip install -r requirements.txt

# キャッシュをクリア
pip cache purge
pip install -r requirements.txt
```

---

## テスト実行の問題

### テストが失敗する

**症状**:
```
FAILED tests/test_example.py::test_function - AssertionError: ...
```

**解決策**:
```bash
# 1. 詳細なエラーログを確認
pytest tests/test_example.py::test_function -vv

# 2. 特定のテストを実行
pytest tests/test_example.py::test_function

# 3. デバッグモードで実行
pytest tests/test_example.py::test_function --pdb

# 4. ログ出力を確認
pytest tests/test_example.py::test_function --log-cli-level=DEBUG
```

### カバレッジが不足している

**症状**:
```
FAIL Required test coverage of 70% not reached. Total coverage: 65.23%
```

**解決策**:
```bash
# 1. カバレッジレポートを確認
pytest --cov=app --cov-report=html

# 2. HTMLレポートを開く
# htmlcov/index.html をブラウザで開く

# 3. カバレッジが低いファイルを確認

# 4. 不足しているテストケースを追加
#    - テストされていない関数・メソッド
#    - テストされていない分岐(if文、例外処理等)

# 5. カバレッジを再確認
pytest --cov=app --cov-report=term
```

### テストが遅い

**症状**: テスト実行に時間がかかりすぎる

**解決策**:
```bash
# 並列実行
pytest -n auto

# 遅いテストを特定
pytest --durations=10

# 特定のマーカーのテストのみ実行
pytest -m unit
pytest -m "not slow"
```

---

## CI/CDパイプラインの問題

### Pre-commit フックが実行されない

**症状**:
```bash
$ git commit -m "test"
# pre-commitフックが実行されずにコミットされる
```

**解決策**:
```bash
# Pre-commitがインストールされているか確認
pre-commit --version

# インストールされていない場合
pip install pre-commit

# フックを有効化
pre-commit install

# 確認
ls -la .git/hooks/pre-commit  # Linux/macOS
dir .git\hooks\pre-commit     # Windows
```

### Black フォーマットエラー

**症状**:
```
would reformat <file_path>
1 file would be reformatted
```

**解決策**:
```bash
# 自動修正
black app/ --line-length 79

# 特定ファイルのみ修正
black <file_path> --line-length 79

# 再コミット
git add .
git commit -m "your message"
```

### flake8 Linter エラー

**よくあるエラーコードと解決策**:

| エラーコード | 内容                 | 解決策                          |
| ------------ | -------------------- | ------------------------------- |
| E302         | 関数定義前の空行不足 | 関数定義の前に2行空ける         |
| E501         | 行が長すぎる         | 行を79文字以内に分割            |
| F401         | 未使用のインポート   | 不要なインポート文を削除        |
| E722         | bare except          | `except Exception as e:` に変更 |
| W293         | 空白行に空白文字     | 空白行から空白文字を削除        |

**解決策**:
```bash
# エラーを確認
flake8 app/ --statistics

# 自動修正可能なものはBlackで修正
black app/ --line-length 79

# 手動で修正が必要なものは該当箇所を修正

# 再確認
flake8 app/
```

### GitHub Actions でテストが失敗

**症状**: CI環境でのみテストが失敗する

**解決策**:

1. **ローカルで再現**:
```bash
# CI環境と同じ条件でテストを実行
pytest -m "not e2e" --cov=app --cov-fail-under=70
```

2. **ワークフローログを確認**:
   - GitHubリポジトリページ → Actions
   - 失敗したワークフローをクリック
   - 詳細なエラーログを確認

3. **環境変数を確認**:
```yaml
env:
  DB_HOST: localhost
  DB_PORT: 5432
  # ...
```

---

## データベースの問題

### データベース接続エラー

**症状**:
```
psycopg2.OperationalError: could not connect to server: Connection refused
```

**原因**:
- PostgreSQLサービスが起動していない
- 接続情報が正しくない

**解決策（ローカル環境）**:
```bash
# PostgreSQLが起動しているか確認
# Windows
pg_ctl status

# macOS/Linux
sudo systemctl status postgresql

# 起動していない場合は起動
# Windows
pg_ctl start

# macOS/Linux
sudo systemctl start postgresql

# 接続情報を確認
psql -h localhost -U stock_user -d stock_data_system
```

**解決策（CI環境）**:
`.github/workflows/quality.yml`の設定を確認:
```yaml
services:
  postgres:
    image: postgres:14
    env:
      POSTGRES_USER: stock_user
      POSTGRES_PASSWORD: stock_password
      POSTGRES_DB: stock_data_system
```

### マイグレーションエラー

**症状**: データベーススキーマが更新されない

**解決策**:
```bash
# マイグレーションスクリプトを確認
ls scripts/database/schema/

# スキーマを手動で適用
psql -h localhost -U stock_user -d stock_data_system -f scripts/database/schema/create_tables.sql

# サンプルデータを挿入
psql -h localhost -U stock_user -d stock_data_system -f scripts/database/seed/insert_sample_data.sql
```

---

## APIの問題

### APIエンドポイントが404を返す

**症状**:
```
GET /api/stocks → 404 Not Found
```

**解決策**:

1. **ルーティングを確認**:
```python
# app/app.py または app/routes/
@app.route('/api/stocks', methods=['GET'])
def get_stocks():
    pass
```

2. **Flaskアプリケーションが起動しているか確認**:
```bash
python app/app.py
```

3. **正しいポートにアクセスしているか確認**:
```
http://localhost:5000/api/stocks
```

### APIレスポンスが期待と異なる

**症状**: APIが期待と異なるデータを返す

**解決策**:

1. **リクエストログを確認**:
```python
# app/app.py
import logging
logging.basicConfig(level=logging.DEBUG)
```

2. **レスポンスを詳細に確認**:
```bash
curl -v http://localhost:5000/api/stocks
```

3. **データベースの中身を確認**:
```bash
psql -h localhost -U stock_user -d stock_data_system
SELECT * FROM stocks_1d LIMIT 10;
```

---

## デバッグ方法

### ローカルでのデバッグ

#### 1. ログ出力を追加

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

#### 2. ブレークポイントを設定

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

pdbデバッガが起動:
```
(Pdb) n          # 次の行へ
(Pdb) s          # ステップイン
(Pdb) c          # 続行
(Pdb) p variable # 変数の値を表示
(Pdb) l          # 現在の位置を表示
(Pdb) h          # ヘルプ
```

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

## よくある質問 (FAQ)

### Q1: コミット時にPre-commitフックをスキップしたい

**A**: `--no-verify` オプションを使用します:
```bash
git commit -m "your message" --no-verify
```

**注意**: CI環境でエラーになる可能性があるため、緊急時のみ使用してください。

### Q2: テストが不安定 (flaky test)

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

### Q3: エラーメッセージが分かりにくい

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

---

## まとめ

問題が発生した場合は、以下の流れで対応することを推奨します:

1. **エラーメッセージを確認**: 何が問題なのかを把握
2. **このドキュメントから解決策を探す**: 該当するエラーケースを探す
3. **ローカルで再現**: ローカル環境で問題を再現し、デバッグ
4. **修正と確認**: 修正後、ローカルでテストを実行
5. **Push**: 成功を確認後、GitHub にpush

問題が解決しない場合は:
- GitHub Issuesで質問
- プロジェクトメンバーに相談
- 関連ドキュメントを参照

---

## 関連ドキュメント

- [CI/CDパイプライン設定](../ci-cd/pipeline-config.md) - CI/CD詳細設定
- [テスト規約](../standards/testing-standards.md) - テスト作成ガイドライン
- [コーディング規約](../standards/coding-standards.md) - コーディング規約
- [開発ワークフロー](development-workflow.md) - 開発フロー全体

---

**最終更新**: 2025-11-02
**文書バージョン**: v2.0.0
