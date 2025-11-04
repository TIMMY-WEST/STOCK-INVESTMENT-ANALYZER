category: guide
ai_context: low
last_updated: 2025-10-18
related_docs:
  - ../guides/DATABASE_SETUP.md
  - ../architecture/database_design.md

# データベースバックアップ手順書

## 概要
本ドキュメントは、`stocks_daily`テーブル削除前に実施すべきバックアップ手順を明文化したものです。
データの安全性を確保するため、必ず以下の手順に従ってバックアップを取得してください。

## 前提条件
- PostgreSQLクライアント（psql）がインストールされていること
- データベースへの接続権限があること
- 十分なディスク容量があること（データベースサイズの2倍以上を推奨）

## バックアップ手順

### 1. 事前確認

#### 1.1 データベース接続確認
```bash
psql -U stock_user -d stock_data_system -h localhost -c "SELECT current_database(), current_user, now();"
```

#### 1.2 対象テーブルの存在確認
```bash
psql -U stock_user -d stock_data_system -h localhost -c "SELECT COUNT(*) FROM stocks_daily;"
```

#### 1.3 ディスク容量確認
```bash
# Windows
dir C:\ | findstr "bytes free"

# データベースサイズ確認
psql -U stock_user -d stock_data_system -h localhost -c "SELECT pg_size_pretty(pg_database_size('stock_data_system'));"
```

### 2. 完全バックアップ（推奨）

#### 2.1 データベース全体のバックアップ
```bash
# バックアップディレクトリ作成
mkdir -p backups/$(date +%Y%m%d_%H%M%S)
cd backups/$(date +%Y%m%d_%H%M%S)

# 完全バックアップ実行
pg_dump -U stock_user -h localhost -d stock_data_system > full_backup_before_stocks_daily_removal.sql

# バックアップファイルの確認
ls -la full_backup_before_stocks_daily_removal.sql
```

#### 2.2 バックアップファイルの検証
```bash
# ファイルサイズ確認
wc -l full_backup_before_stocks_daily_removal.sql

# バックアップ内容の簡易確認
head -20 full_backup_before_stocks_daily_removal.sql
tail -20 full_backup_before_stocks_daily_removal.sql

# stocks_dailyテーブルの存在確認
grep -n "CREATE TABLE.*stocks_daily" full_backup_before_stocks_daily_removal.sql
```

### 3. テーブル単位バックアップ（補完用）

#### 3.1 stocks_dailyテーブルのスキーマバックアップ
```bash
pg_dump -U stock_user -h localhost -d stock_data_system -s -t stocks_daily > stocks_daily_schema_backup.sql
```

#### 3.2 stocks_dailyテーブルのデータバックアップ
```bash
pg_dump -U stock_user -h localhost -d stock_data_system -a -t stocks_daily > stocks_daily_data_backup.sql
```

#### 3.3 CSVフォーマットでのデータエクスポート
```bash
psql -U stock_user -d stock_data_system -h localhost -c "\COPY stocks_daily TO 'stocks_daily_backup.csv' WITH CSV HEADER;"
```

### 4. バックアップファイルの管理

#### 4.1 バックアップファイル一覧の作成
```bash
# バックアップ情報をファイルに記録
cat > backup_info.txt << EOF
バックアップ作成日時: $(date)
データベース名: stock_data_system
対象テーブル: stocks_daily
バックアップ理由: Issue #65 - stocks_dailyテーブル削除対応

ファイル一覧:
$(ls -la *.sql *.csv)

データ件数:
$(psql -U stock_user -d stock_data_system -h localhost -t -c "SELECT COUNT(*) FROM stocks_daily;")
EOF
```

#### 4.2 バックアップファイルの圧縮
```bash
# 圧縮してストレージ容量を節約
tar -czf stocks_daily_backup_$(date +%Y%m%d_%H%M%S).tar.gz *.sql *.csv backup_info.txt
```

#### 4.3 バックアップファイルの安全な保存
```bash
# 複数の場所にバックアップを保存
cp stocks_daily_backup_*.tar.gz /path/to/safe/location/
cp stocks_daily_backup_*.tar.gz /path/to/another/location/
```

### 5. バックアップの検証

#### 5.1 テストリストア（推奨）
```bash
# テスト用データベース作成
createdb -U stock_user -h localhost test_restore_db

# バックアップからのリストア
psql -U stock_user -h localhost -d test_restore_db < full_backup_before_stocks_daily_removal.sql

# リストア結果の確認
psql -U stock_user -d test_restore_db -h localhost -c "SELECT COUNT(*) FROM stocks_daily;"

# テスト用データベース削除
dropdb -U stock_user -h localhost test_restore_db
```

#### 5.2 バックアップファイルの整合性確認
```bash
# SQLファイルの構文チェック
psql -U stock_user -d stock_data_system -h localhost --set ON_ERROR_STOP=on -f full_backup_before_stocks_daily_removal.sql --dry-run

# CSVファイルの行数確認
wc -l stocks_daily_backup.csv
psql -U stock_user -d stock_data_system -h localhost -t -c "SELECT COUNT(*) + 1 FROM stocks_daily;" # +1 for header
```

## 緊急時のリストア手順

### 完全リストア
```bash
# データベース削除・再作成
dropdb -U stock_user -h localhost stock_data_system
createdb -U stock_user -h localhost stock_data_system

# バックアップからのリストア
psql -U stock_user -h localhost -d stock_data_system < full_backup_before_stocks_daily_removal.sql
```

### テーブル単位リストア
```bash
# スキーマリストア
psql -U stock_user -h localhost -d stock_data_system < stocks_daily_schema_backup.sql

# データリストア
psql -U stock_user -h localhost -d stock_data_system < stocks_daily_data_backup.sql
```

### CSVからのリストア
```bash
# テーブル作成後
psql -U stock_user -d stock_data_system -h localhost -c "\COPY stocks_daily FROM 'stocks_daily_backup.csv' WITH CSV HEADER;"
```

## チェックリスト

### バックアップ実行前
- [ ] データベース接続確認完了
- [ ] 対象テーブルの存在確認完了
- [ ] ディスク容量確認完了（十分な空き容量あり）
- [ ] バックアップディレクトリ作成完了

### バックアップ実行中
- [ ] 完全バックアップ実行完了
- [ ] テーブル単位バックアップ実行完了
- [ ] CSVエクスポート実行完了
- [ ] バックアップファイル検証完了

### バックアップ実行後
- [ ] バックアップファイル一覧作成完了
- [ ] バックアップファイル圧縮完了
- [ ] 安全な場所への保存完了
- [ ] テストリストア実行完了（推奨）
- [ ] バックアップ整合性確認完了

## 注意事項

1. **実行タイミング**: システムの負荷が低い時間帯に実行してください
2. **権限確認**: 必要な権限（SELECT, USAGE等）があることを事前に確認してください
3. **容量監視**: バックアップ実行中はディスク容量を監視してください
4. **ログ保存**: バックアップ実行時のログは必ず保存してください
5. **複数保存**: バックアップファイルは複数の場所に保存してください

## トラブルシューティング

### よくある問題と対処法

#### 権限エラー
```bash
# エラー例: permission denied for table stocks_daily
# 対処法: 権限確認と付与
psql -U postgres -d stock_data_system -c "GRANT SELECT ON stocks_daily TO stock_user;"
```

#### 容量不足エラー
```bash
# エラー例: No space left on device
# 対処法: 不要ファイル削除または別ディスクへの保存
df -h
du -sh /path/to/backup/directory
```

#### 接続エラー
```bash
# エラー例: could not connect to server
# 対処法: PostgreSQLサービス確認
systemctl status postgresql
# または
net start postgresql-x64-13
```

## 関連ドキュメント
- [データベース設計](../architecture/database_design.md)
- [トラブルシューティング](./troubleshooting.md)
---
**重要**: このバックアップ手順は、データの安全性を確保するための重要なプロセスです。必ず全ての手順を実行し、バックアップの検証まで完了してから次の作業に進んでください。
