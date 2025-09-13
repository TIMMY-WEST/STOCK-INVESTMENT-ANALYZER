# PostgreSQL環境構築とデータベース接続設定（Issue #10改善版）

## 概要

このドキュメントでは、株価投資分析システム用のPostgreSQL環境構築手順について説明します。  
**Issue #10の改善により、Windows/Linux/macOS環境でのUnicode問題、トランザクション問題、権限設定が自動化されました。**

## ✅ Issue #10で実装された改善

- **トランザクション問題修正**: CREATE DATABASEをAUTOCOMMITモードで実行
- **Unicode文字エラー修正**: Windows環境での絵文字表示問題を解決
- **自動権限設定**: ユーザー作成から権限設定まで完全自動化
- **環境設定検証**: 設定値の自動チェックと修正提案
- **詳細エラーハンドリング**: 具体的なエラーメッセージと解決方法

## 完了条件チェックリスト

- ✅ PostgreSQLローカルインストールと起動確認
- ✅ 自動データベース・ユーザー作成（改善）
- ✅ .env環境変数ファイル作成と検証（改善）
- ✅ SQLAlchemyでの基本接続設定
- ✅ Windows環境でのUnicode対応（新規）
- ✅ 包括的な接続テスト成功（改善）

## 1. PostgreSQLのインストール

### Windows の場合

#### 方法1: Chocolatey を使用（推奨）
```bash
# Chocolatey経由でインストール
choco install postgresql

# サービス開始
net start postgresql-x64-16
```

#### 方法2: 公式インストーラー
1. [PostgreSQL公式サイト](https://www.postgresql.org/download/windows/)からダウンロード
2. インストーラーを実行
3. インストール時にパスワードを設定（例: `postgres`）

### macOS の場合
```bash
# Homebrew経由でインストール
brew install postgresql

# サービス開始
brew services start postgresql
```

### Ubuntu/Linux の場合
```bash
# パッケージ更新
sudo apt update

# PostgreSQLインストール
sudo apt install postgresql postgresql-contrib

# サービス開始
sudo systemctl start postgresql
sudo systemctl enable postgresql
```

## 2. 環境変数設定（重要！）

### .envファイル作成

**まず最初に**、プロジェクトルートに `.env` ファイルを作成し、PostgreSQL管理者パスワードを設定してください：

```env
# データベース設定
DB_HOST=localhost
DB_PORT=5432
DB_NAME=stock_data_system
DB_USER=stock_user
DB_PASSWORD=stock_password

# PostgreSQL管理者設定（重要！）
DB_ADMIN_USER=postgres
DB_ADMIN_PASSWORD=your_postgres_password

# アプリケーション設定
FLASK_ENV=development
FLASK_DEBUG=True
FLASK_PORT=8000
```

**⚠️ 重要**: `DB_ADMIN_PASSWORD` を正しく設定しないと、自動セットアップが失敗します。

## 3. 自動データベースセットアップ（推奨）

### Issue #10改善版スクリプトを使用

```bash
# 自動セットアップ実行（推奨）
python scripts/db/create_database.py

# 既存データベースを削除して再作成
python scripts/db/create_database.py --force

# 接続テストのみ実行
python scripts/db/create_database.py --test-connection

# テスト環境用
python scripts/db/create_database.py --env test
```

### 自動セットアップの内容

改善されたスクリプトは以下を自動実行します：

1. **環境設定検証**: `.env`設定値の妥当性チェック
2. **PostgreSQL接続テスト**: 管理者権限での接続確認
3. **データベース作成**: 指定された名前でデータベース作成
4. **ユーザー作成**: アプリケーション用ユーザーの自動作成
5. **権限設定**: データベースおよびスキーマ権限の自動設定
6. **接続テスト**: 設定完了後の動作確認

### 期待される出力

```
📊 現在の環境設定:
  環境: development
  ホスト: localhost
  ポート: 5432
  データベース名: stock_data_system
  ユーザー名: stock_user
  管理者ユーザー: postgres
  管理者パスワード: 設定済み

✅ 環境設定は正常です

✅ データベース 'stock_data_system' の作成が完了しました

📋 ユーザー作成と権限設定を実行中...
✅ ユーザー 'stock_user' の作成と権限設定が完了しました

🔒 スキーマ権限設定を実行中...
✅ データベース 'stock_data_system' のスキーマ権限設定が完了しました

🔍 データベース接続テストを実行中...
✅ データベース接続テストに成功しました

🎉 データベース作成処理が完了しました！
```

## 4. 手動セットアップ（自動セットアップが失敗した場合）

### PostgreSQLに接続
```bash
# Windowsの場合
psql -U postgres

# macOS/Linuxの場合
sudo -u postgres psql
```

### データベースとユーザーを作成
```sql
-- データベース作成
CREATE DATABASE stock_data_system;

-- 開発用ユーザー作成
CREATE USER stock_user WITH PASSWORD 'stock_password';

-- 権限付与
GRANT ALL PRIVILEGES ON DATABASE stock_data_system TO stock_user;

-- 接続テスト用に追加権限
ALTER USER stock_user CREATEDB;

-- データベースに接続
\c stock_data_system

-- スキーマ権限設定
GRANT ALL ON SCHEMA public TO stock_user;
GRANT ALL ON ALL TABLES IN SCHEMA public TO stock_user;
GRANT ALL ON ALL SEQUENCES IN SCHEMA public TO stock_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO stock_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO stock_user;

-- 終了
\q
```

## 3. 接続確認

### 作成したデータベースに接続
```bash
psql -U stock_user -d stock_data_system -h localhost
```

パスワードが要求されたら `stock_password` を入力してください。

### 接続成功の確認
```sql
-- 接続確認
SELECT current_database(), current_user;

-- 終了
\q
```

## 4. Pythonアプリケーションからの接続テスト

### 1. 仮想環境の有効化
```bash
# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate
```

### 2. 依存関係のインストール
```bash
pip install -r requirements.txt
```

### 3. 接続テストの実行
```bash
python app/simple_test.py
```

### 4. 期待される出力
```
PostgreSQL + SQLAlchemy Connection Test
==================================================
Test 1: Database Connection
[PASS] Connection successful: データベース接続に成功しました
  Database URL: postgresql://stock_user:***@localhost:5432/stock_data_system

Test 2: Table Creation
[PASS] Table creation successful: データベーステーブルの初期化が完了しました

Test 3: Basic CRUD Operations
  INSERT test...
  [PASS] Data inserted successfully
  SELECT test...
  [PASS] Data found: <StockDaily(symbol='7203.T', date='2024-xx-xx', close=2530.0)>
  UPDATE test...
  [PASS] Data updated successfully
  DELETE test...
  [PASS] Data deleted successfully

==================================================
All tests passed successfully!
PostgreSQL environment and SQLAlchemy connection are ready.
==================================================
```

## 6. トラブルシューティング（Issue #10改善版）

### 🔧 Unicode文字エラー（Windows環境） - ✅ 修正済み

**以前のエラー**: `UnicodeEncodeError: 'cp932' codec can't encode character`

**解決状況**: Issue #10で自動修正済み
- 絵文字が安全な文字（`[OK]`, `[ERROR]`, `[WARNING]`）に自動変換
- Windows環境でのUTF-8出力を自動設定

### 🔧 トランザクションエラー - ✅ 修正済み

**以前のエラー**: `current transaction is aborted`

**解決状況**: Issue #10で自動修正済み
- CREATE DATABASEをAUTOCOMMITモードで実行
- トランザクション内でのDDL操作問題を解決

### 問題: 認証エラー
```
FATAL: password authentication failed for user "postgres"
```

**解決方法:**
1. `.env`ファイルの`DB_ADMIN_PASSWORD`を確認
2. PostgreSQLインストール時に設定したパスワードを使用
3. パスワードリセット（必要時）:
   ```bash
   # Windows（管理者コマンドプロンプト）
   net user postgres new_password
   
   # Linux/macOS
   sudo -u postgres psql
   \password postgres
   ```

### 問題: 接続エラー
```
could not connect to server at "localhost", port 5432
```

**解決方法:**
1. PostgreSQLサービス状態確認:
   ```bash
   # Windows
   sc query postgresql
   net start postgresql
   
   # Linux/macOS
   sudo systemctl status postgresql
   sudo systemctl start postgresql
   ```

### 問題: 権限エラー
```
permission denied for database/schema public
```

**解決方法:**
1. 自動権限修正スクリプト実行:
   ```bash
   python fix_permissions.py
   ```
2. または自動セットアップを再実行:
   ```bash
   python scripts/db/create_database.py --force
   ```

### 問題: 環境設定エラー

改善されたスクリプトは環境設定を自動検証し、以下のような詳細な修正提案を表示します：

```
❌ エラー:
  - PostgreSQL管理者パスワード(DB_ADMIN_PASSWORD)が設定されていません

💡 修正提案:
  - 環境変数 DB_ADMIN_PASSWORD を設定してください
  - PostgreSQLサーバーが localhost:5432 で動作していることを確認してください
```

### デバッグ情報の確認

```bash
# 環境設定の詳細確認
python scripts/db/create_database.py --test-connection

# 包括的な機能テスト
python create_tables_simple.py
```

## 6. ファイル構成

このセットアップで作成されるファイル:

```
STOCK-INVESTMENT-ANALYZER/
├── .env                    # 環境変数設定 ✅
├── requirements.txt        # Python依存関係 ✅
├── app/
│   ├── __init__.py        # パッケージ初期化 ✅
│   ├── database.py        # データベース接続設定 ✅
│   ├── models.py          # SQLAlchemyモデル ✅
│   ├── simple_test.py     # 接続テストスクリプト ✅
│   └── test_connection.py # 詳細テストスクリプト ✅
└── DATABASE_SETUP.md      # このファイル ✅
```

## 7. 次のステップ

接続テストが成功したら、以下に進むことができます:

1. 株価データ取得API実装
2. WebアプリケーションのUI作成  
3. データ分析機能の追加

---

## 環境変数設定 (.env)

このセットアップで使用される環境変数:

```env
# データベース設定
DB_HOST=localhost
DB_PORT=5432
DB_NAME=stock_data_system
DB_USER=stock_user
DB_PASSWORD=stock_password

# アプリケーション設定
FLASK_ENV=development
FLASK_DEBUG=True
FLASK_PORT=8000
```

**注意:** `.env`ファイルには認証情報が含まれているため、バージョン管理には含めないでください。`.gitignore`に追加することを推奨します。

---

## 🎉 Issue #10改善の成果

### 実装前の問題
- Windows環境でのUnicode文字エラー
- CREATE DATABASEのトランザクション問題
- 手動での権限設定が必要
- 環境設定エラーの原因特定が困難

### 実装後の改善
- ✅ **クロスプラットフォーム対応**: Windows/Linux/macOSで統一動作
- ✅ **完全自動化**: データベース作成からユーザー権限設定まで
- ✅ **エラー解決支援**: 具体的なエラーメッセージと修正提案
- ✅ **環境検証**: 設定値の自動チェック機能
- ✅ **Unicode対応**: Windows環境での文字エンコーディング問題解決

### 使用推奨方法

1. **初回セットアップ**:
   ```bash
   # .envファイル作成 → DB_ADMIN_PASSWORD設定
   python scripts/db/create_database.py
   ```

2. **問題発生時**:
   ```bash
   python scripts/db/create_database.py --test-connection
   # エラーメッセージと修正提案を確認
   ```

3. **完全リセット**:
   ```bash
   python scripts/db/create_database.py --force
   ```

この改善により、**動作するシステムを素早く構築**し、**安定した開発環境**を提供できるようになりました。