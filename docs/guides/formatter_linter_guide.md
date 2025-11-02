# フォーマッタ・Linter使用ガイド

このドキュメントでは、STOCK-INVESTMENT-ANALYZERプロジェクトで使用するコードフォーマッタとLinterの使い方を説明します。

## 目次

1. [導入済みツール](#導入済みツール)
2. [セットアップ](#セットアップ)
3. [各ツールの使い方](#各ツールの使い方)
4. [VSCodeでの自動フォーマット](#vscodeでの自動フォーマット)
5. [トラブルシューティング](#トラブルシューティング)

---

## 導入済みツール

### コードフォーマッター

- **Black**: Pythonコードの自動フォーマッター
- **isort**: インポート文の自動ソート

### Linter（静的解析ツール）

- **flake8**: PEP 8準拠チェック、構文エラー検出
- **pylint**: より詳細な静的解析、コード品質チェック

### 型チェック

- **mypy**: 型ヒントの検証

---

## セットアップ

### 1. 開発用ツールのインストール

仮想環境を有効化してから、以下のコマンドを実行します。

```bash
# Windowsの場合
venv\Scripts\activate
pip install -r requirements-dev.txt

# macOS/Linuxの場合
source venv/bin/activate
pip install -r requirements-dev.txt
```

### 2. VSCode拡張機能のインストール

VSCodeで開発する場合、以下の拡張機能をインストールすることを推奨します：

- Python (ms-python.python)
- Black Formatter (ms-python.black-formatter)
- isort (ms-python.isort)
- Flake8 (ms-python.flake8)
- Pylint (ms-python.pylint)
- Mypy Type Checker (ms-python.mypy-type-checker)
- Pylance (ms-python.vscode-pylance)

プロジェクトを開くと、VSCodeが自動的にこれらの拡張機能をインストールするよう推奨します。

---

## 各ツールの使い方

### Black（コードフォーマッター）

#### 基本的な使い方

```bash
# ファイルをフォーマット（上書き）
python -m black app/models.py

# ディレクトリ全体をフォーマット
python -m black app/

# プロジェクト全体をフォーマット
python -m black .

# チェックのみ（変更しない）
python -m black --check app/models.py

# 差分を表示
python -m black --diff app/models.py
```

#### 設定

設定は[pyproject.toml](../../pyproject.toml)で管理されています。

主な設定：
- 行の最大長: 79文字
- 除外ディレクトリ: `migrations/`, `venv/`, `.venv/`, `.git/` など

---

### isort（インポート文ソート）

#### 基本的な使い方

```bash
# ファイルのインポートをソート（上書き）
python -m isort app/models.py

# ディレクトリ全体をソート
python -m isort app/

# プロジェクト全体をソート
python -m isort .

# チェックのみ（変更しない）
python -m isort --check-only app/models.py

# 差分を表示
python -m isort --diff app/models.py
```

#### 設定

設定は[pyproject.toml](../../pyproject.toml)で管理されています。

インポートの順序：
1. 標準ライブラリ
2. サードパーティライブラリ
3. ローカルモジュール（app, models, services, utils, tests）

---

### flake8（Linter）

#### 基本的な使い方

```bash
# ファイルをチェック
python -m flake8 app/models.py

# ディレクトリ全体をチェック
python -m flake8 app/

# プロジェクト全体をチェック
python -m flake8 .

# エラー数をカウント
python -m flake8 app/ --count

# 統計情報を表示
python -m flake8 app/ --statistics
```

#### 設定

設定は[.flake8](../../.flake8)ファイルで管理されています。

主な設定：
- 行の最大長: 79文字
- 複雑度の閾値: 10
- 無視するエラー: E203, W503, E501

---

### pylint（静的解析ツール）

#### 基本的な使い方

```bash
# ファイルをチェック
python -m pylint app/models.py

# ディレクトリ全体をチェック
python -m pylint app/

# 特定のメッセージのみ表示
python -m pylint app/models.py --disable=all --enable=line-too-long

# レポート形式の出力
python -m pylint app/models.py --output-format=text
```

#### 設定

設定は[pyproject.toml](../../pyproject.toml)で管理されています。

主な設定：
- 行の最大長: 79文字
- 無効化されたメッセージ: C0111, C0103, R0903, W0212

---

### mypy（型チェック）

#### 基本的な使い方

```bash
# ファイルをチェック
python -m mypy app/models.py

# ディレクトリ全体をチェック
python -m mypy app/

# プロジェクト全体をチェック
python -m mypy .

# エラーコードを表示
python -m mypy app/models.py --show-error-codes
```

#### 設定

設定は[pyproject.toml](../../pyproject.toml)で管理されています。

主な設定：
- Python バージョン: 3.8以上
- サードパーティライブラリの型スタブがない場合は警告を無視

---

## VSCodeでの自動フォーマット

### 設定内容

[.vscode/settings.json](../../.vscode/settings.json)に以下の設定が記載されています：

- **保存時に自動フォーマット**: 有効
- **デフォルトフォーマッター**: Black
- **保存時にインポート文を自動ソート**: 有効
- **Lintのチェック**: 有効（flake8, pylint）

### 使い方

1. VSCodeでPythonファイルを開く
2. ファイルを編集
3. `Ctrl+S`（Windows）または `Cmd+S`（macOS）で保存
4. 自動的にBlackでフォーマット、isortでインポートがソートされる

### 手動でフォーマット

- **フォーマット**: `Shift+Alt+F`（Windows）または `Shift+Option+F`（macOS）
- **インポートをソート**: コマンドパレット（`Ctrl+Shift+P`）→ "Organize Imports"

---

## 一括フォーマット・チェックのコマンド

プロジェクト全体を一括でフォーマット・チェックする場合は、以下のコマンドを使用します。

### 一括フォーマット

```bash
# Blackでフォーマット
python -m black .

# isortでインポートをソート
python -m isort .
```

### 一括チェック

```bash
# Blackのチェック（変更せずに確認）
python -m black --check .

# isortのチェック
python -m isort --check-only .

# flake8のチェック
python -m flake8 .

# pylintのチェック
python -m pylint app/ services/ utils/

# mypyのチェック
python -m mypy .
```

### すべてのチェックを実行

```bash
# まとめて実行（Windows）
python -m black --check . && python -m isort --check-only . && python -m flake8 . && python -m pylint app/ && python -m mypy .

# まとめて実行（macOS/Linux）
python -m black --check . && \
python -m isort --check-only . && \
python -m flake8 . && \
python -m pylint app/ && \
python -m mypy .
```

---

## トラブルシューティング

### 1. ツールがインストールされていない

```bash
pip install -r requirements-dev.txt
```

### 2. VSCodeで自動フォーマットが動作しない

- VSCodeの拡張機能がインストールされているか確認
- コマンドパレット（`Ctrl+Shift+P`）→ "Python: Select Interpreter" で正しいインタープリターが選択されているか確認
- `.vscode/settings.json`が正しく読み込まれているか確認

### 3. flake8やpylintのエラーが多すぎる

一度にすべてを修正する必要はありません。段階的に修正していきましょう。

優先順位：
1. **Blackとisortでフォーマット**: `python -m black . && python -m isort .`
2. **重要なflake8エラーを修正**: 構文エラー、未使用のインポートなど
3. **pylintの警告を確認**: コード品質の改善

### 4. Blackとflake8の設定が競合している

`.flake8`ファイルで以下のエラーコードを無視しています：
- `E203`: Blackと競合
- `W503`: PEP 8で推奨される改行位置
- `E501`: 行の長さはBlackに任せる

---

## 関連ドキュメント

- [コーディング規約とスタイルガイド](coding_standards.md)
- [PEP 8 -- Style Guide for Python Code](https://peps.python.org/pep-0008/)
- [Black公式ドキュメント](https://black.readthedocs.io/)
- [isort公式ドキュメント](https://pycqa.github.io/isort/)
- [flake8公式ドキュメント](https://flake8.pycqa.org/)
- [pylint公式ドキュメント](https://pylint.pycqa.org/)
- [mypy公式ドキュメント](https://mypy.readthedocs.io/)

---

**更新履歴**

- 2025-10-22: 初版作成 (Issue #108)
