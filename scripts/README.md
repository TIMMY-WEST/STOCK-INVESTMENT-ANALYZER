# PostgreSQL データベースセットアップスクリプト

株価データ取得システム用PostgreSQLデータベースの自動構築スクリプト集です。

## 📁 ファイル構成

```
scripts/
├── README.md              # このファイル（使用方法説明）
├── create_database.sql    # データベース・ユーザー作成スクリプト
├── create_tables.sql      # テーブル・インデックス作成スクリプト
├── insert_sample_data.sql # サンプルデータ投入スクリプト
├── setup_db.bat          # Windows用自動セットアップスクリプト
└── setup_db.sh           # Linux/macOS用自動セットアップスクリプト
```

## 🚀 クイックスタート

### Windows環境

```bash
# scripts ディレクトリに移動
cd scripts

# 自動セットアップ実行
setup_db.bat
```

### Linux/macOS環境

```bash
# scripts ディレクトリに移動
cd scripts

# 実行権限付与（初回のみ）
chmod +x setup_db.sh

# 自動セットアップ実行
./setup_db.sh
```

## 📋 手動セットアップ手順

自動スクリプトが使用できない場合の手動実行方法です。

### 1. データベース作成

```bash
# PostgreSQLに postgres ユーザーで接続
psql -U postgres -h localhost

# データベース作成スクリプト実行
\i create_database.sql

# 接続確認
\c stock_data_system stock_user
# パスワード: stock_password

# 終了
\q
```

### 2. テーブル作成

```bash
# 作成したデータベースに接続
psql -U stock_user -d stock_data_system -h localhost

# テーブル作成スクリプト実行
\i create_tables.sql

# テーブル確認
\dt

# 終了
\q
```

### 3. サンプルデータ投入

```bash
# データベースに接続
psql -U stock_user -d stock_data_system -h localhost

# サンプルデータ投入
\i insert_sample_data.sql

# データ確認
SELECT * FROM stocks_daily LIMIT 5;

# 終了
\q
```

## 🗄️ 作成されるデータベース構成

### データベース情報

- **データベース名**: `stock_data_system`
- **ユーザー名**: `stock_user`
- **パスワード**: `stock_password`
- **ホスト**: `localhost`
- **ポート**: `5432`

### テーブル構成

#### 8つの時間軸別テーブル

| テーブル名    | 時間軸 | 時間カラム | 説明                     |
| ------------- | ------ | ---------- | ------------------------ |
| `stocks_1d`   | 日足   | `date`     | 日次株価データ           |
| `stocks_1m`   | 1分足  | `datetime` | 1分間隔の株価データ      |
| `stocks_5m`   | 5分足  | `datetime` | 5分間隔の株価データ      |
| `stocks_15m`  | 15分足 | `datetime` | 15分間隔の株価データ     |
| `stocks_30m`  | 30分足 | `datetime` | 30分間隔の株価データ     |
| `stocks_1h`   | 1時間足| `datetime` | 1時間間隔の株価データ    |
| `stocks_1wk`  | 週足   | `date`     | 週次株価データ           |
| `stocks_1mo`  | 月足   | `date`     | 月次株価データ           |

#### 共通カラム構成

| カラム名     | データ型                 | 説明                     |
| ------------ | ------------------------ | ------------------------ |
| `id`         | SERIAL PRIMARY KEY       | レコードID（自動採番）   |
| `symbol`     | VARCHAR(20) NOT NULL     | 銘柄コード（例：7203.T） |
| `date`       | DATE NOT NULL            | 取引日（日足・週足・月足）|
| `datetime`   | TIMESTAMP NOT NULL       | 取引日時（分足・時間足） |
| `open`       | DECIMAL(10,2) NOT NULL   | 始値                     |
| `high`       | DECIMAL(10,2) NOT NULL   | 高値                     |
| `low`        | DECIMAL(10,2) NOT NULL   | 安値                     |
| `close`      | DECIMAL(10,2) NOT NULL   | 終値                     |
| `volume`     | BIGINT NOT NULL          | 出来高                   |
| `created_at` | TIMESTAMP WITH TIME ZONE | レコード作成日時         |
| `updated_at` | TIMESTAMP WITH TIME ZONE | レコード更新日時         |

### インデックス

各テーブルに以下のインデックスが作成されます：

- **主キーインデックス**: `id`（自動作成）
- **ユニーク制約インデックス**: `(symbol, date/datetime)`（自動作成）
- **銘柄検索用**: `idx_{table_name}_symbol`
- **時間検索用**: `idx_{table_name}_date` または `idx_{table_name}_datetime`
- **複合検索用**: `idx_{table_name}_symbol_date_desc` または `idx_{table_name}_symbol_datetime_desc`

### 制約

- **ユニーク制約**: 
  - 日足・週足・月足: `(symbol, date)` - 同一銘柄の同一日付データ重複防止
  - 分足・時間足: `(symbol, datetime)` - 同一銘柄の同一日時データ重複防止
- **チェック制約**: 価格・出来高の負数チェック、価格論理チェック

## 📊 サンプルデータ

以下の銘柄のサンプルデータが投入されます（2024年9月2日〜13日）：

- **7203.T**: トヨタ自動車
- **6758.T**: ソニーグループ
- **8306.T**: 三菱UFJフィナンシャル・グループ
- **7974.T**: 任天堂
- **9983.T**: ファーストリテイリング

## 🔧 トラブルシューティング

### PostgreSQLが見つからない

```bash
# Windows
choco install postgresql

# macOS
brew install postgresql

# Ubuntu/Linux
sudo apt install postgresql postgresql-contrib
```

### パスワード認証エラー

1. `pg_hba.conf` の設定確認
2. PostgreSQLサービス再起動

```bash
# Windows
net restart postgresql-x64-16

# Linux
sudo systemctl restart postgresql

# macOS
brew services restart postgresql
```

### ポート接続エラー

```bash
# ポート5432が使用されているか確認
netstat -an | grep 5432
lsof -i :5432
```

### 権限エラー

```bash
# PostgreSQLに管理者権限で接続
sudo -u postgres psql

# 権限確認
\du
```

## 🧪 動作確認

### データベース接続テスト

```bash
psql -U stock_user -d stock_data_system -h localhost -c "SELECT COUNT(*) FROM stocks_daily;"
```

### アプリケーション接続テスト

```bash
# Python仮想環境を有効化
source venv/bin/activate  # Linux/macOS
# または
venv\Scripts\activate  # Windows

# アプリケーション起動
cd app
python app.py

# ブラウザで http://localhost:8000 にアクセス
```

## 📝 注意事項

### セキュリティ

- **開発環境用設定**: パスワードは開発用のものです
- **本番環境**: 適切な認証設定とパスワードに変更してください
- **ファイアウォール**: 必要に応じてポート5432の設定を行ってください

### データ管理

- **バックアップ**: 重要なデータは定期的にバックアップしてください
- **ディスク容量**: データ量に応じて適切な容量を確保してください
- **パフォーマンス**: 大量データ時はインデックス最適化を検討してください

## 📚 関連ドキュメント

- [データベース設計書](../docs/database_design.md)
- [環境構築手順書](../docs/setup_guide.md)
- [GitHub運用ルール](../docs/github_workflow.md)

## 🆘 サポート

問題が発生した場合は、以下を確認してください：

1. PostgreSQLのインストール状況
2. サービスの起動状況
3. ネットワーク設定
4. 権限設定
5. ログファイルの内容

詳細なエラー情報とともにイシューを作成してください。