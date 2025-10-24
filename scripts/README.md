# Scripts Directory

開発環境セットアップ、データベース管理、分析ツールなどのスクリプト集

## 📁 ディレクトリ構造

```
scripts/
├── setup/              # セットアップスクリプト
│   ├── dev_setup.sh       # Linux/macOS用開発環境セットアップ
│   ├── dev_setup.bat      # Windows用開発環境セットアップ
│   ├── setup_db.sh        # Linux/macOS用データベースセットアップ
│   └── setup_db.bat       # Windows用データベースセットアップ
├── database/           # データベース関連スクリプト
│   ├── schema/            # スキーマ定義
│   │   ├── create_database.sql           # データベース作成
│   │   ├── create_tables.sql             # テーブル作成（8テーブル構成）
│   │   └── create_stock_master_tables.sql # 株式マスタテーブル作成
│   ├── migrations/        # マイグレーションスクリプト
│   │   ├── migrate_to_8tables.sql        # 8テーブル構成への移行
│   │   └── remove_stocks_daily_table.sql # 旧テーブル削除
│   ├── validation/        # バリデーションスクリプト
│   │   ├── validate_migration_completion.sql # マイグレーション完了確認
│   │   ├── validate_stocks_daily_schema.sql  # スキーマ検証
│   │   └── test_stocks_daily_constraints.sql # 制約テスト
│   └── seed/              # サンプルデータ
│       └── insert_sample_data.sql        # サンプルデータ投入
├── analysis/           # 分析・テストスクリプト
│   ├── analyze_jpx_data.py                 # JPXデータ分析
│   └── test_multi_timeframe_fetching.py    # 複数時間軸取得テスト
└── README.md           # このファイル
```

## 🚀 セットアップスクリプト

### 開発環境セットアップ

新規開発者向けのワンコマンドセットアップスクリプト

**Linux/macOS:**
```bash
chmod +x scripts/setup/dev_setup.sh
./scripts/setup/dev_setup.sh
```

**Windows:**
```cmd
scripts\setup\dev_setup.bat
```

**実行内容:**
1. 前提条件チェック（Python, Git, PostgreSQL）
2. 環境変数ファイル（.env）作成
3. Python仮想環境作成
4. pip アップグレード
5. 依存関係インストール
6. データベースセットアップ（オプション）
7. セットアップ検証

### データベースセットアップ

データベースとテーブルの初期化

**Linux/macOS:**
```bash
chmod +x scripts/setup/setup_db.sh
./scripts/setup/setup_db.sh
```

**Windows:**
```cmd
scripts\setup\setup_db.bat
```

**実行内容:**
1. PostgreSQLインストール確認
2. PostgreSQLサービス起動確認
3. データベース作成
4. テーブル作成
5. サンプルデータ投入
6. 接続テスト

## 🗄️ データベーススクリプト

### スキーマ定義

**create_database.sql**
- データベース `stock_data_system` の作成
- ユーザー `stock_user` の作成と権限設定

**create_tables.sql**
- 8つの時間軸テーブル作成（1m, 5m, 15m, 30m, 1h, 1d, 1wk, 1mo）
- インデックス作成
- 制約設定

**create_stock_master_tables.sql**
- 株式マスタテーブル作成
- 銘柄情報管理

### マイグレーション

**migrate_to_8tables.sql**
- 旧 `stocks_daily` から新しい8テーブル構成への移行
- データ保持しながらスキーマ変更

**remove_stocks_daily_table.sql**
- 旧テーブルの削除

### バリデーション

**validate_migration_completion.sql**
- マイグレーション完了確認
- データ整合性チェック

**validate_stocks_daily_schema.sql**
- スキーマ構造の検証
- カラム・制約の確認

**test_stocks_daily_constraints.sql**
- 制約条件のテスト
- データ品質確認

### サンプルデータ

**insert_sample_data.sql**
- 主要日本企業のサンプルデータ投入
  - トヨタ自動車 (7203.T)
  - ソニーグループ (6758.T)
  - 三菱UFJフィナンシャル・グループ (8306.T)
  - 任天堂 (7974.T)
  - ファーストリテイリング (9983.T)

## 📊 分析スクリプト

### JPXデータ分析

**analyze_jpx_data.py**
- JPX（日本取引所グループ）データの分析
- 統計情報の出力

**使用方法:**
```bash
python scripts/analysis/analyze_jpx_data.py
```

### 複数時間軸取得テスト

**test_multi_timeframe_fetching.py**
- 複数の時間軸でのデータ取得テスト
- パフォーマンス測定

**使用方法:**
```bash
python scripts/analysis/test_multi_timeframe_fetching.py
```

## 🔧 トラブルシューティング

### PostgreSQL接続エラー

```bash
# PostgreSQLサービスの状態確認
# Linux
sudo systemctl status postgresql

# macOS
brew services list | grep postgresql

# Windows
net start | findstr postgresql
```

### パスワード認証エラー

1. `pg_hba.conf` の設定確認
2. PostgreSQLサービス再起動

```bash
# Linux
sudo systemctl restart postgresql

# macOS
brew services restart postgresql

# Windows
net restart postgresql-x64-16
```

### 権限エラー

```bash
# PostgreSQLに管理者権限で接続
sudo -u postgres psql

# 権限確認
\du
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

- [プロジェクトREADME](../README.md)
- [開発ワークフロー](../docs/development/github_workflow.md)
- [データベース設計](../docs/database_design.md)

## 🆘 サポート

問題が発生した場合は、以下を確認してください：

1. PostgreSQLのインストール状況
2. サービスの起動状況
3. ネットワーク設定
4. 権限設定
5. ログファイルの内容

詳細なエラー情報とともにIssueを作成してください。
