# Pre-commit フック セットアップガイド

## 概要

このプロジェクトでは、コミット前に自動的にコードチェックとフォーマットを実行するため、pre-commitフックを使用しています。

## 目的

- コード品質の一貫性を保つ
- コミット前に自動的にコードスタイルを統一
- 潜在的なバグやエラーを早期に検出
- レビュー時間の短縮

## 実行されるチェック

### 1. 基本チェック（pre-commit-hooks）
- **end-of-file-fixer**: ファイル末尾に空行を追加
- **trailing-whitespace**: 行末の空白を削除
- **check-merge-conflict**: マージコンフリクトマーカーの検出
- **check-yaml/json/toml**: 各種設定ファイルの構文チェック
- **check-added-large-files**: 大きなファイル（500KB以上）の追加を防ぐ
- **check-ast**: Pythonの構文チェック
- **debug-statements**: デバッグ文（breakpoint、pdb等）の検出

### 2. Black（コードフォーマッタ）
- PEP 8準拠の自動フォーマット
- 行の長さ: 79文字
- 対象: すべての`.py`ファイル

### 3. isort（インポート文の整理）
- インポート文の自動整理とソート
- Blackと互換性のある設定
- 標準ライブラリ、サードパーティ、ローカルモジュールの順に整理

### 4. flake8（Linter）
- コーディング規約の違反を検出
- 複雑度のチェック（McCabe complexity: 10以下）
- 以下の拡張プラグインを使用:
  - `flake8-bugbear`: よくあるバグパターンを検出
  - `flake8-docstrings`: docstringの品質チェック
  - `flake8-comprehensions`: リスト内包表記の最適化提案

### 5. mypy（型チェック）
- 型ヒントのチェック
- 型の不整合を検出
- 現在は警告モード（エラーでもコミット可能）

## セットアップ手順

### 1. 前提条件

Python 3.8以上がインストールされていること

```bash
python --version
```

### 2. 依存パッケージのインストール

#### 開発用依存関係をインストール

```bash
# プロジェクトルートで実行
pip install -e ".[dev]"
```

これにより、以下のツールがインストールされます:
- black
- isort
- flake8
- pylint
- mypy

#### pre-commitのインストール

```bash
pip install pre-commit
```

### 3. pre-commitフックの有効化

```bash
# プロジェクトルートで実行
pre-commit install
```

実行後、以下のメッセージが表示されます:
```
pre-commit installed at .git/hooks/pre-commit
```

### 4. 初回実行（オプション）

すべてのファイルに対してpre-commitを実行したい場合:

```bash
pre-commit run --all-files
```

## 使用方法

### 通常のコミット

pre-commitフックが有効化された後は、通常通り`git commit`するだけで自動的にチェックが実行されます。

```bash
git add .
git commit -m "コミットメッセージ"
```

### 実行の流れ

1. `git commit`を実行
2. pre-commitフックが起動
3. 各チェックが順次実行される:
   - ファイル修正系（end-of-file-fixer、trailing-whitespace等）
   - Black（自動フォーマット）
   - isort（インポート整理）
   - flake8（Linterチェック）
   - mypy（型チェック）
4. すべてのチェックが成功したらコミット完了
5. チェックが失敗した場合:
   - 自動修正可能な場合: ファイルが修正される → 再度`git add`して`git commit`
   - 手動修正が必要な場合: エラーメッセージを確認して修正

### 実行例

#### 成功例
```bash
$ git commit -m "機能追加"
ファイル末尾の空行を修正................................................合格
行末の空白を削除......................................................合格
マージコンフリクトのマーカーをチェック................................合格
YAMLファイルの構文チェック.............................................合格
Blackによるコードフォーマット..........................................合格
isortによるインポート文の整理..........................................合格
flake8によるコードチェック.............................................合格
mypyによる型チェック...................................................合格
[feature/example abc1234] 機能追加
 2 files changed, 20 insertions(+), 5 deletions(-)
```

#### 自動修正が行われた例
```bash
$ git commit -m "機能追加"
ファイル末尾の空行を修正................................................失敗
- hook id: end-of-file-fixer
- exit code: 1
- files were modified by this hook

Fixing app/main.py

行末の空白を削除......................................................合格
Blackによるコードフォーマット..........................................失敗
- hook id: black
- files were modified by this hook

reformatted app/main.py
All done! ✨ 🍰 ✨
1 file reformatted.

# 修正されたファイルを再度addしてcommit
$ git add .
$ git commit -m "機能追加"
[すべてのチェックが合格]
```

#### 手動修正が必要な例
```bash
$ git commit -m "機能追加"
flake8によるコードチェック.............................................失敗
- hook id: flake8
- exit code: 1

app/main.py:15:1: E302 expected 2 blank lines, found 1
app/main.py:42:80: E501 line too long (85 > 79 characters)

# エラーを修正してから再度commit
```

## 特定のチェックをスキップする方法

### すべてのチェックをスキップ（非推奨）

```bash
git commit --no-verify -m "コミットメッセージ"
```

**注意**: 緊急時以外は使用しないでください。

### 特定のフックのみスキップ

環境変数`SKIP`を使用:

```bash
SKIP=flake8 git commit -m "コミットメッセージ"
```

複数スキップする場合:
```bash
SKIP=flake8,mypy git commit -m "コミットメッセージ"
```

## 手動実行

### すべてのファイルに対して実行

```bash
pre-commit run --all-files
```

### 特定のフックのみ実行

```bash
# Blackのみ実行
pre-commit run black --all-files

# flake8のみ実行
pre-commit run flake8 --all-files
```

### ステージされたファイルのみ実行

```bash
pre-commit run
```

## 設定ファイル

### .pre-commit-config.yaml

pre-commitの設定ファイル。各フックの設定が記述されています。

主要な設定項目:
- `repos`: 使用するフックのリポジトリ
- `rev`: フックのバージョン
- `hooks`: 実行するフック
- `exclude`: 除外するファイルパターン

### pyproject.toml

Black、isort、mypy、pylintの設定が含まれています。

### .flake8

flake8の設定ファイル（pyproject.tomlに対応していないため別ファイル）。

## トラブルシューティング

### 問題1: pre-commitが実行されない

**症状**: `git commit`してもpre-commitが実行されない

**解決方法**:
```bash
# フックが正しくインストールされているか確認
ls -la .git/hooks/pre-commit

# 再インストール
pre-commit uninstall
pre-commit install
```

### 問題2: 既存のコードで大量のエラーが出る

**症状**: 既存のコードをコミットしようとすると大量のフォーマットエラーが発生

**解決方法**:
```bash
# 全ファイルを一括フォーマット
pre-commit run --all-files

# 修正されたファイルをコミット
git add .
git commit -m "style: pre-commitによる自動フォーマット適用"
```

### 問題3: mypyで型エラーが大量に出る

**症状**: 型チェックで多数のエラーが表示される

**解決方法**:

現在の設定では、mypyは警告モードで動作しており、エラーが出てもコミットは可能です。

段階的に型ヒントを追加していくことを推奨します:

1. 新規コードには必ず型ヒントを追加
2. 既存コードは少しずつ修正
3. 将来的に`verbose: true`に変更してエラーを厳格にチェック

一時的にスキップする場合:
```bash
SKIP=mypy git commit -m "コミットメッセージ"
```

### 問題4: パフォーマンスが遅い

**症状**: コミット時に時間がかかりすぎる

**原因**: 多数のファイルを一度にチェックしている

**解決方法**:

1. **小さく頻繁にコミット**: 一度に大量のファイルを変更しない
2. **事前にフォーマット**: コミット前に手動で実行
   ```bash
   black app/
   isort app/
   ```
3. **特定のチェックを無効化**: 必要に応じて`.pre-commit-config.yaml`を調整

### 問題5: WindowsとLinux/macOSの改行コード問題

**症状**: 改行コード（CRLF/LF）の違いでエラーが発生

**解決方法**:

Gitの設定を確認:
```bash
# Windowsの場合
git config --global core.autocrlf true

# Linux/macOSの場合
git config --global core.autocrlf input
```

### 問題6: 外部ライブラリの型スタブがない

**症状**: mypyで`Cannot find implementation or library stub`エラー

**解決方法**:

該当するライブラリを`pyproject.toml`の`[[tool.mypy.overrides]]`に追加:

```toml
[[tool.mypy.overrides]]
module = [
    "ライブラリ名.*",
]
ignore_missing_imports = true
```

または、型スタブパッケージをインストール:
```bash
pip install types-ライブラリ名
```

### 問題7: フックの更新が反映されない

**症状**: `.pre-commit-config.yaml`を変更しても反映されない

**解決方法**:
```bash
# フックの依存関係を再インストール
pre-commit clean
pre-commit install --install-hooks
```

## 更新とメンテナンス

### フックのバージョン更新

```bash
# 最新バージョンに自動更新
pre-commit autoupdate
```

### 設定の確認

```bash
# 現在の設定を確認
pre-commit run --all-files --verbose
```

## CI/CD環境での使用

GitHub ActionsなどのCI環境でもpre-commitを実行できます。

`.github/workflows/pre-commit.yml`の例:
```yaml
name: pre-commit

on:
  pull_request:
  push:
    branches: [main]

jobs:
  pre-commit:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.8'
      - uses: pre-commit/action@v3.0.0
```

## ベストプラクティス

1. **定期的な更新**: `pre-commit autoupdate`を月に一度実行
2. **チーム全体での共有**: 新メンバーには必ずセットアップ手順を案内
3. **小さく頻繁にコミット**: pre-commitの実行時間を短縮
4. **段階的な導入**: 新規プロジェクトは厳格に、既存プロジェクトは段階的に
5. **ドキュメント化**: プロジェクト固有のルールをREADMEに記載

## 参考リンク

- [pre-commit 公式ドキュメント](https://pre-commit.com/)
- [Black 公式ドキュメント](https://black.readthedocs.io/)
- [isort 公式ドキュメント](https://pycqa.github.io/isort/)
- [flake8 公式ドキュメント](https://flake8.pycqa.org/)
- [mypy 公式ドキュメント](https://mypy.readthedocs.io/)

## サポート

問題が解決しない場合は、プロジェクトのIssueトラッカーで質問してください。
