# STOCK-INVESTMENT-ANALYZER

![Python](https://img.shields.io/badge/python-3.8+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
[![Flask](https://img.shields.io/badge/Flask-3.0.0-green.svg)](https://flask.palletsprojects.com/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-12%2B-blue.svg)](https://www.postgresql.org/)
[![Code Style: Black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

Yahoo Financeから日本企業の株価データを取得しPostgreSQLに保存するWebアプリケーション。FlaskベースのMVP優先設計で、シンプルな構成から段階的に機能拡張できる株価データ収集・分析システム。

## 📋 目次

- [🎯 概要](#概要)
- [✨ 主な機能](#主な機能)
- [🚀 クイックスタート](#クイックスタートガイド)
- [🗄️ データベース構造](#データベース構造)
- [💻 開発環境](#開発環境)
- [🔧 トラブルシューティング](#トラブルシューティング)
- [❓ よくある質問 (FAQ)](#よくある質問-faq)
- [🤝 コントリビューション](#コントリビューション)
- [📄 ライセンス](#ライセンス)

## 🎯 概要

Yahoo Financeから日本企業の株価データを取得し、PostgreSQLに保存するWebアプリケーションです。FlaskベースのMVP優先設計により、シンプルな構成から段階的に機能拡張できる株価データ収集・分析システムを提供します。

## 🎯 プロジェクトの目的

本システムは、**日本の株式市場データを効率的に収集・保存・分析する**ためのWebアプリケーションです。投資判断に必要な多時間軸での株価データを一元管理し、データドリブンな投資分析の基盤を提供します。

## 📊 背景

- 株式投資において、複数の時間軸でのデータ分析は重要
- Yahoo Finance APIを活用した信頼性の高いデータ取得
- PostgreSQLによる高性能なデータ管理
- 段階的な機能拡張が可能なMVP設計

## 👥 対象ユーザー

- 個人投資家
- データアナリスト
- 金融システム開発者
- 株式投資の学習者

## ✨ 主な機能

### 📈 多時間軸データ管理
8つの異なる時間軸での株価データを効率的に保存・管理：

| 時間軸 | テーブル名 | データ型 | 用途 |
|--------|------------|----------|------|
| 1分足 | `stocks_1m` | TIMESTAMP | デイトレード分析 |
| 5分足 | `stocks_5m` | TIMESTAMP | 短期トレード |
| 15分足 | `stocks_15m` | TIMESTAMP | スイングトレード |
| 30分足 | `stocks_30m` | TIMESTAMP | 中期分析 |
| 1時間足 | `stocks_1h` | TIMESTAMP | トレンド分析 |
| 日足 | `stocks_1d` | DATE | 長期投資 |
| 週足 | `stocks_1wk` | DATE | 中長期分析 |
| 月足 | `stocks_1mo` | DATE | 長期トレンド |

### 🌐 Yahoo Finance連携
- **リアルタイムデータ取得**: 信頼性の高いリアルタイム株価データ
- **自動更新**: スケジューラーによる定期的なデータ更新
- **エラーハンドリング**: 堅牢なエラー処理とリトライ機能

### 🗄️ PostgreSQL統合
- **高性能データベース**: 大量データの高速処理
- **最適化されたスキーマ**: 効率的なクエリ実行
- **データ整合性**: トランザクション管理とバックアップ

### 🌐 直感的なWeb UI
- **Flask Webアプリ**: レスポンシブなユーザーインターフェース
- **リアルタイム更新**: WebSocketによるライブデータ表示
- **進捗表示**: データ取得の進捗とETA表示

### ⚡ 一括取得（バルクデータサービス）
- **並列処理**: 複数銘柄の効率的な同時取得
- **進捗トラッキング**: リアルタイムな処理状況の監視
- **リストファイル対応**: CSVファイルからの一括処理
- 詳細は [`docs/bulk-data-fetch.md`](docs/bulk-data-fetch.md) を参照

### 🛠️ 自動セットアップ
- **ワンコマンドセットアップ**: 15分以内の環境構築
- **クロスプラットフォーム**: Windows/Linux/macOS対応
- **依存関係管理**: 自動的な環境設定

## 🚀 クイックスタートガイド

### 📋 前提条件

| ソフトウェア | バージョン | 必須 |
|--------------|------------|------|
| Python | 3.8以上 | ✅ |
| PostgreSQL | 12以上 | ✅ |
| Git | 最新版 | ✅ |

### ⚡ ワンコマンドセットアップ（推奨）

新規開発者は以下のコマンドで**15分以内**に開発環境を構築できます：

#### Linux/macOS
```bash
git clone https://github.com/TIMMY-WEST/STOCK-INVESTMENT-ANALYZER.git
cd STOCK-INVESTMENT-ANALYZER
make setup
```

または

```bash
chmod +x scripts/setup/dev_setup.sh
./scripts/setup/dev_setup.sh
```

#### Windows
```cmd
git clone https://github.com/TIMMY-WEST/STOCK-INVESTMENT-ANALYZER.git
cd STOCK-INVESTMENT-ANALYZER
scripts\setup\dev_setup.bat
```

#### セットアップ内容
セットアップスクリプトは以下を自動的に実行します：

- ✅ Python仮想環境の作成
- ✅ 依存関係のインストール
- ✅ データベースの初期化
- ✅ サンプルデータの投入
- ✅ 環境変数ファイル（.env）の設定

### 🔧 手動セットアップ手順

自動セットアップが使用できない場合の詳細手順：

<details>
<summary>手動セットアップの詳細を表示</summary>

1. **リポジトリのクローン**
   ```bash
   git clone https://github.com/TIMMY-WEST/STOCK-INVESTMENT-ANALYZER.git
   cd STOCK-INVESTMENT-ANALYZER
   ```

2. **Python仮想環境の作成**
   ```bash
   python -m venv venv

   # 有効化（Linux/macOS）
   source venv/bin/activate

   # 有効化（Windows）
   venv\Scripts\activate
   ```

3. **依存関係のインストール**
   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   pip install -r requirements-dev.txt
   ```

4. **環境変数の設定**
   ```bash
   # Linux/macOS
   cp .env.example .env

   # Windows
   copy .env.example .env
   ```

   `.env`ファイルを編集してデータベース接続情報を設定してください。

5. **データベースセットアップ**

   **Windows:**
   ```cmd
   scripts\setup\setup_db.bat
   ```

   **Linux/macOS:**
   ```bash
   chmod +x scripts/setup/setup_db.sh
   ./scripts/setup/setup_db.sh
   ```

6. **アプリケーション起動**
   ```bash
   cd app
   python app.py
   ```

   サーバーが起動したら、ブラウザで `http://localhost:8000` にアクセスしてください。

</details>

### 🛠️ 便利なMakeコマンド（Linux/macOS）

```bash
make help       # 使用可能なコマンド一覧
make setup      # 開発環境の完全セットアップ
make run        # アプリケーション起動
make test       # テスト実行
make test-cov   # カバレッジ付きテスト実行
make format     # コードフォーマット
make lint       # コードチェック
make db-setup   # データベースセットアップ
make db-reset   # データベースリセット
make clean      # キャッシュクリア
make clean-all  # 全ての生成ファイル削除
```

## 🗄️ データベース構造

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

### データベース管理

#### 新規セットアップ
```bash
# テーブル作成
psql -U stock_user -d stock_data_system -f scripts/create_tables.sql

# サンプルデータ投入
psql -U stock_user -d stock_data_system -f scripts/insert_sample_data.sql
```

#### データベースリセット
開発中にデータベースをクリーンな状態に戻す場合：

**Windows:**
```cmd
scripts\setup\reset_db.bat
```

**Linux/macOS:**
```bash
chmod +x scripts/setup/reset_db.sh
./scripts/setup/reset_db.sh
```

**Makeコマンド（Linux/macOS）:**
```bash
make db-reset
```

⚠️ **注意:** このスクリプトは**全てのデータを削除**します。本番環境では使用しないでください。

## 🔧 開発環境

### ディレクトリ構造

```
STOCK-INVESTMENT-ANALYZER/
├── app/                       # Flaskアプリケーション
│   ├── api/                   # APIエンドポイント
│   ├── services/              # ビジネスロジック
│   ├── static/                # 静的ファイル
│   ├── templates/             # HTMLテンプレート
│   └── utils/                 # ユーティリティ
├── docs/                      # プロジェクトドキュメント
│   ├── api/                   # API仕様書
│   ├── architecture/          # アーキテクチャ設計
│   ├── development/           # 開発ガイドライン
│   └── guides/                # セットアップガイド
├── scripts/                   # データベーススクリプト
│   ├── database/              # DB管理スクリプト
│   └── setup/                 # セットアップスクリプト
├── tests/                     # テストコード
├── migrations/                # データベースマイグレーション
├── .env.example              # 環境設定テンプレート
├── requirements.txt          # Python依存関係
├── pyproject.toml           # プロジェクト設定
└── README.md                # このファイル
```

### 開発フロー

1. **ブランチ作成**: `feature/機能名` または `fix/修正内容`
2. **開発実装**: 機能開発とテスト作成
3. **テスト実行**: 全テストの通過確認
4. **Pull Request**: レビュー依頼とマージ

詳細な開発ガイドライン:
- [Git運用ワークフロー](docs/development/git_workflow.md) - 共同開発向けの詳細なGit運用ルール
- [GitHub運用ルール](docs/development/github_workflow.md) - 個人+AI開発向けの簡易版
- [ブランチ保護ルール](docs/development/branch_protection_rules.md) - mainブランチの保護設定とCI/CD要件
- [テスト戦略](docs/development/testing_strategy.md) - テスト方針とベストプラクティス

### サンプルデータ

システムには以下の日本企業のサンプルデータが含まれています：

- **トヨタ自動車** (7203.T)
- **ソニーグループ** (6758.T)
- **三菱UFJフィナンシャル・グループ** (8306.T)
- **任天堂** (7974.T)

各銘柄について、全8つの時間軸でのサンプルデータが投入されます。

## 🔧 トラブルシューティング

### よくある問題

#### 1. PostgreSQL接続エラー
**症状:** `psycopg2.OperationalError: could not connect to server`

**解決方法:**
```bash
# PostgreSQLサービスの状態確認
sudo systemctl status postgresql  # Linux
brew services list | grep postgresql  # macOS
sc query postgresql-x64-12  # Windows

# サービス開始
sudo systemctl start postgresql  # Linux
brew services start postgresql  # macOS
net start postgresql-x64-12  # Windows
```

#### 2. 権限エラー
**症状:** `permission denied for database`

**解決方法:**
```sql
-- PostgreSQLに管理者でログイン
psql -U postgres

-- ユーザー権限の確認と付与
GRANT ALL PRIVILEGES ON DATABASE stock_data_system TO stock_user;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO stock_user;
```

#### 3. テーブル作成エラー
**症状:** `relation already exists`

**解決方法:**
```bash
# 既存テーブルの確認
psql -U stock_user -d stock_data_system -c "\dt"

# 必要に応じてリセット
make db-reset  # Linux/macOS
scripts\setup\reset_db.bat  # Windows
```

#### 4. Python仮想環境の問題
**症状:** `ModuleNotFoundError`

**解決方法:**
```bash
# 仮想環境の再作成
rm -rf venv  # Linux/macOS
rmdir /s venv  # Windows

python -m venv venv
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate  # Windows

pip install -r requirements.txt
```

#### 5. ポート競合エラー
**症状:** `Address already in use: 8000`

**解決方法:**
```bash
# ポート使用状況の確認
lsof -i :8000  # Linux/macOS
netstat -ano | findstr :8000  # Windows

# プロセス終了
kill -9 <PID>  # Linux/macOS
taskkill /PID <PID> /F  # Windows
```

### ログの確認方法

```bash
# PostgreSQLログ確認（Linux）
sudo tail -f /var/log/postgresql/postgresql-*.log

# macOSの場合
tail -f /usr/local/var/log/postgres.log

# Windowsの場合
# Event Viewer でPostgreSQLイベントを確認
```

### パフォーマンス最適化

#### データベース最適化
```sql
-- インデックスの確認
SELECT schemaname, tablename, indexname
FROM pg_indexes
WHERE tablename LIKE 'stocks_%';

-- 統計情報の更新
ANALYZE;

-- バキューム実行
VACUUM ANALYZE;
```

## ❓ よくある質問 (FAQ)

### Q1: どの銘柄のデータを取得できますか？

**A1:** Yahoo Financeで取得可能な全ての日本株式（.T サフィックス）に対応しています。主要な銘柄例：
- 東証プライム市場の全銘柄
- 東証スタンダード市場の銘柄
- 東証グロース市場の銘柄

銘柄コードは「7203.T」（トヨタ自動車）のように、証券コード + ".T" の形式で指定してください。

### Q2: データの更新頻度はどの程度ですか？

**A2:** 以下の更新頻度で動作します：
- **リアルタイムデータ**: Yahoo Finance APIの制限内（通常15-20分遅延）
- **自動更新**: 設定可能（デフォルト: 1時間毎）
- **手動更新**: Web UIまたはAPIから即座に実行可能

詳細は [`docs/bulk-data-fetch.md`](docs/bulk-data-fetch.md) を参照してください。

### Q3: 大量のデータを一度に取得できますか？

**A3:** はい、バルクデータサービスを使用して効率的に大量取得が可能です：
- **並列処理**: 複数銘柄の同時取得
- **進捗表示**: リアルタイムな処理状況
- **エラー処理**: 失敗した銘柄の自動リトライ
- **レート制限**: Yahoo Finance APIの制限を考慮した調整

使用方法は Web UI の「一括取得」タブから実行できます。

### Q4: 本番環境での運用は可能ですか？

**A4:** 現在はMVP（最小実行可能製品）として設計されており、本格的な本番運用には以下の追加対応が推奨されます：
- **セキュリティ強化**: HTTPS、認証機能の実装
- **監視機能**: ログ監視、アラート機能
- **バックアップ**: 定期的なデータベースバックアップ
- **負荷分散**: 高負荷時の対応

詳細は [`docs/guides/performance_optimization_guide.md`](docs/guides/performance_optimization_guide.md) を参照してください。

### Q5: 他の証券取引所のデータも取得できますか？

**A5:** 現在は日本市場（東京証券取引所）に特化していますが、Yahoo Finance APIが対応している他の市場も技術的には可能です：
- **米国市場**: NASDAQ、NYSE
- **欧州市場**: LSE、Euronext
- **アジア市場**: 香港、韓国など

他市場対応のリクエストは [Issues](https://github.com/TIMMY-WEST/STOCK-INVESTMENT-ANALYZER/issues) でお知らせください。

### Q6: APIの利用制限はありますか？

**A6:** Yahoo Finance APIの制限に準拠しています：
- **リクエスト頻度**: 1秒間に2-3リクエスト程度
- **データ遅延**: 15-20分程度の遅延
- **利用規約**: Yahoo Financeの利用規約に従った使用

商用利用や大量アクセスの場合は、有料のデータプロバイダーの検討をお勧めします。

## 🤝 コントリビューション

プロジェクトへの貢献を歓迎します！以下の方法で参加できます：

### 貢献方法

1. **Issue報告**: バグ報告や機能要望
2. **Pull Request**: コードの改善や新機能の実装
3. **ドキュメント改善**: README、API仕様書の改善
4. **テスト追加**: テストカバレッジの向上

### 開発参加手順

1. リポジトリをフォーク
2. 機能ブランチを作成 (`git checkout -b feature/amazing-feature`)
3. 変更をコミット (`git commit -m 'Add some amazing feature'`)
4. ブランチにプッシュ (`git push origin feature/amazing-feature`)
5. Pull Requestを作成

### 開発ガイドライン

詳細な開発ガイドラインについては、以下のドキュメントを参照してください：

- **[CONTRIBUTING.md](docs/guides/contributing.md)** - 貢献ガイドライン
- **[コーディング規約](docs/development/coding_standards.md)** - コードスタイルとベストプラクティス
- **[Git運用ルール](docs/development/git_workflow.md)** - ブランチ戦略とコミット規約
- **[テスト戦略](docs/development/testing_strategy.md)** - テストの書き方と実行方法

### コミュニティ

- **Issues**: [GitHub Issues](https://github.com/TIMMY-WEST/STOCK-INVESTMENT-ANALYZER/issues)
- **Discussions**: プロジェクトに関する議論や質問
- **Wiki**: 詳細な技術情報とTips

## 📄 ライセンス

このプロジェクトは **MIT License** の下で公開されています。

```
MIT License

Copyright (c) 2024 TIMMY-WEST

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

詳細は [LICENSE](LICENSE) ファイルを参照してください。

## 🔗 関連リンク

### 外部リソース
- [Yahoo Finance](https://finance.yahoo.com/) - 株価データソース
- [PostgreSQL Documentation](https://www.postgresql.org/docs/) - データベース公式ドキュメント
- [Flask Documentation](https://flask.palletsprojects.com/) - Webフレームワーク公式ドキュメント

### プロジェクトドキュメント
- [API仕様書](docs/api/api_specification.md) - REST API詳細仕様
- [アーキテクチャ設計](docs/architecture/project_architecture.md) - システム設計概要
- [データベース設計](docs/architecture/database_design.md) - DB設計詳細
- [セットアップガイド](docs/guides/setup_guide.md) - 詳細なセットアップ手順

## 📝 更新履歴

### 2024-01-15
**v2.0.0 (Issue #47対応)**
- ✅ 8テーブル構成への移行
- ✅ 多時間軸データ管理機能追加
- ✅ マイグレーションスクリプト追加
- ✅ スキーマ検証機能強化

### 2023-12-01
**v1.0.0**
- ✅ 初期リリース
- ✅ 基本的な株価データ収集機能
- ✅ PostgreSQL統合
- ✅ Flask Webアプリケーション

---

<div align="center">

**⭐ このプロジェクトが役に立ったら、ぜひスターをお願いします！ ⭐**

[🐛 バグ報告](https://github.com/TIMMY-WEST/STOCK-INVESTMENT-ANALYZER/issues/new?template=bug_report.md) |
[💡 機能要望](https://github.com/TIMMY-WEST/STOCK-INVESTMENT-ANALYZER/issues/new?template=feature_request.md) |
[❓ 質問](https://github.com/TIMMY-WEST/STOCK-INVESTMENT-ANALYZER/issues/new?template=question.md)

</div>
