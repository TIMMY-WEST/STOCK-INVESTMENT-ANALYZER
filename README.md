# STOCK-INVESTMENT-ANALYZER

Yahoo Financeから日本企業の株価データを取得しPostgreSQLに保存するWebアプリケーション。FlaskベースのMVP優先設計で、シンプルな構成から段階的に機能拡張できる株価データ収集・分析システム。

## 概要

本システムは、日本の株式市場データを効率的に収集・保存・分析するためのWebアプリケーションです。複数の時間軸（分足、時間足、日足、週足、月足）での株価データを管理し、投資分析に必要な基盤を提供します。

## 主な機能

- **多時間軸データ管理**: 8つの異なる時間軸での株価データ保存
  - 1分足 (`stocks_1m`)
  - 5分足 (`stocks_5m`)
  - 15分足 (`stocks_15m`)
  - 30分足 (`stocks_30m`)
  - 1時間足 (`stocks_1h`)
  - 日足 (`stocks_1d`)
  - 週足 (`stocks_1wk`)
  - 月足 (`stocks_1mo`)

- **Yahoo Finance連携**: リアルタイム株価データ取得
- **PostgreSQL統合**: 高性能なデータベース管理
- **Flask Webアプリ**: 直感的なWeb UI
- **自動セットアップ**: ワンクリックでの環境構築

### 一括取得（バルクデータサービス）
- 複数銘柄の株価データを並列で取得・保存
- 進捗トラッキング・ETA推定・リストファイルからの処理に対応
- 詳細は `docs/bulk_data_service_guide.md` を参照

## データベース構造

### テーブル構成

システムは8つの株価データテーブルを使用し、それぞれ異なる時間軸のデータを管理します：

#### 分足・時間足テーブル（datetime型）
- `stocks_1m` - 1分足データ
- `stocks_5m` - 5分足データ
- `stocks_15m` - 15分足データ
- `stocks_30m` - 30分足データ
- `stocks_1h` - 1時間足データ

#### 日足・週足・月足テーブル（date型）
- `stocks_1d` - 日足データ
- `stocks_1wk` - 週足データ
- `stocks_1mo` - 月足データ

### 共通カラム構造

すべてのテーブルは以下の共通構造を持ちます：

```sql
- id: BIGSERIAL PRIMARY KEY
- symbol: VARCHAR(20) NOT NULL (銘柄コード)
- date/datetime: DATE/TIMESTAMP NOT NULL (日付/日時)
- open: DECIMAL(10,2) NOT NULL (始値)
- high: DECIMAL(10,2) NOT NULL (高値)
- low: DECIMAL(10,2) NOT NULL (安値)
- close: DECIMAL(10,2) NOT NULL (終値)
- volume: BIGINT NOT NULL (出来高)
- created_at: TIMESTAMP DEFAULT CURRENT_TIMESTAMP
- updated_at: TIMESTAMP DEFAULT CURRENT_TIMESTAMP
```

## クイックスタート

### 前提条件

- PostgreSQL 12以上
- Python 3.8以上
- Git

### インストール手順

1. **リポジトリのクローン**
   ```bash
   git clone https://github.com/TIMMY-WEST/STOCK-INVESTMENT-ANALYZER.git
   cd STOCK-INVESTMENT-ANALYZER
   ```

2. **データベースセットアップ**
   
   **Windows:**
   ```cmd
   scripts\setup_db.bat
   ```
   
   **Linux/macOS:**
   ```bash
   chmod +x scripts/setup_db.sh
   ./scripts/setup_db.sh
   ```

3. **環境設定**

   セットアップスクリプトが自動的に `.env` ファイルを生成します。必要に応じて設定を調整してください：

   ```env
   DB_HOST=localhost
   DB_PORT=5432
   DB_NAME=stock_data_system
   DB_USER=stock_user
   DB_PASSWORD=stock_password
   ```

4. **アプリケーション起動**

   ```bash
   cd app
   python app.py
   ```

   サーバーが起動したら、ブラウザで `http://localhost:8000` にアクセスしてください。

## データベース管理

### 新規セットアップ

```bash
# テーブル作成
psql -U stock_user -d stock_data_system -f scripts/create_tables.sql

# サンプルデータ投入
psql -U stock_user -d stock_data_system -f scripts/insert_sample_data.sql
```

### 既存環境からの移行

既存の `stocks_daily` テーブルから新しい8テーブル構成への移行：

```bash
psql -U stock_user -d stock_data_system -f scripts/migrate_to_8tables.sql
```

### スキーマ検証

データベース構造の検証：

```bash
psql -U stock_user -d stock_data_system -f scripts/validate_stocks_daily_schema.sql
```

## 開発環境

### ディレクトリ構造

```
STOCK-INVESTMENT-ANALYZER/
├── scripts/                    # データベーススクリプト
│   ├── create_database.sql     # データベース作成
│   ├── create_tables.sql       # テーブル作成（8テーブル構成）
│   ├── insert_sample_data.sql  # サンプルデータ投入
│   ├── migrate_to_8tables.sql  # 移行スクリプト
│   ├── validate_stocks_daily_schema.sql # スキーマ検証
│   ├── setup_db.bat           # Windows用セットアップ
│   └── setup_db.sh            # Linux/macOS用セットアップ
├── src/                       # アプリケーションソース
├── tests/                     # テストコード
├── docs/                      # ドキュメント
├── .env.example              # 環境設定テンプレート
└── README.md                 # このファイル
```

### 開発フロー

1. **ブランチ作成**: `feature/機能名` または `fix/修正内容`
2. **開発実装**: 機能開発とテスト作成
3. **テスト実行**: 全テストの通過確認
4. **Pull Request**: レビュー依頼とマージ

## サンプルデータ

システムには以下の日本企業のサンプルデータが含まれています：

- **トヨタ自動車** (7203.T)
- **ソニーグループ** (6758.T)
- **三菱UFJフィナンシャル・グループ** (8306.T)
- **任天堂** (7974.T)

各銘柄について、全8つの時間軸でのサンプルデータが投入されます。

## トラブルシューティング

### よくある問題

1. **PostgreSQL接続エラー**
   - PostgreSQLサービスが起動していることを確認
   - `.env` ファイルの接続情報を確認

2. **権限エラー**
   - データベースユーザーの権限を確認
   - セットアップスクリプトを管理者権限で実行

3. **テーブル作成エラー**
   - 既存テーブルとの競合を確認
   - 必要に応じて `migrate_to_8tables.sql` を使用

### ログ確認

```bash
# PostgreSQLログ確認（Linux）
sudo tail -f /var/log/postgresql/postgresql-*.log

# Windows Event Viewer でPostgreSQLイベントを確認
```

## 貢献

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## ライセンス

このプロジェクトはMITライセンスの下で公開されています。詳細は [LICENSE](LICENSE) ファイルを参照してください。

## 関連リンク

- [Yahoo Finance API](https://finance.yahoo.com/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [Flask Documentation](https://flask.palletsprojects.com/)

## 更新履歴

### v2.0.0 (Issue #47対応)
- 8テーブル構成への移行
- 多時間軸データ管理機能追加
- マイグレーションスクリプト追加
- スキーマ検証機能強化

### v1.0.0
- 初期リリース
- 基本的な株価データ収集機能
- PostgreSQL統合
- Flask Webアプリケーション