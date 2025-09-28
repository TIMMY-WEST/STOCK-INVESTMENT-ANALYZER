-- =====================================================
-- stocks_daily テーブル削除実行スクリプト
-- Issue #65: Remove stocks_daily table after migration
-- =====================================================

-- 実行前の注意事項:
-- 1. 必ずバックアップを取得してから実行してください
-- 2. データ移行が完了していることを validate_migration_completion.sql で確認してください
-- 3. 本番環境では十分なテストを行ってから実行してください

-- =====================================================
-- 1. 事前確認
-- =====================================================

-- 現在のデータベース情報を表示
SELECT 
    current_database() as database_name,
    current_user as current_user,
    now() as execution_time;

-- stocks_daily テーブルの存在確認
SELECT 
    schemaname,
    tablename,
    tableowner,
    hasindexes,
    hasrules,
    hastriggers
FROM pg_tables 
WHERE tablename = 'stocks_daily';

-- stocks_daily テーブルのレコード数確認
SELECT 
    'stocks_daily' as table_name,
    COUNT(*) as record_count
FROM stocks_daily;

-- stocks_1d テーブルのレコード数確認（移行先）
SELECT 
    'stocks_1d' as table_name,
    COUNT(*) as record_count
FROM stocks_1d;

-- =====================================================
-- 2. 依存関係の確認
-- =====================================================

-- stocks_daily テーブルに対する外部キー制約の確認
SELECT 
    tc.table_name,
    tc.constraint_name,
    tc.constraint_type,
    kcu.column_name,
    ccu.table_name AS foreign_table_name,
    ccu.column_name AS foreign_column_name
FROM information_schema.table_constraints AS tc
JOIN information_schema.key_column_usage AS kcu
    ON tc.constraint_name = kcu.constraint_name
    AND tc.table_schema = kcu.table_schema
JOIN information_schema.constraint_column_usage AS ccu
    ON ccu.constraint_name = tc.constraint_name
    AND ccu.table_schema = tc.table_schema
WHERE tc.constraint_type = 'FOREIGN KEY'
    AND (tc.table_name = 'stocks_daily' OR ccu.table_name = 'stocks_daily');

-- stocks_daily テーブルを参照するビューの確認
SELECT 
    schemaname,
    viewname,
    definition
FROM pg_views
WHERE definition LIKE '%stocks_daily%';

-- =====================================================
-- 3. インデックスとトリガーの確認
-- =====================================================

-- stocks_daily テーブルのインデックス一覧
SELECT 
    indexname,
    indexdef
FROM pg_indexes
WHERE tablename = 'stocks_daily';

-- stocks_daily テーブルのトリガー一覧
SELECT 
    trigger_name,
    event_manipulation,
    action_timing,
    action_statement
FROM information_schema.triggers
WHERE event_object_table = 'stocks_daily';

-- =====================================================
-- 4. 最終確認プロンプト
-- =====================================================

-- 以下のメッセージを確認してから削除を実行してください
SELECT 
    '警告: stocks_daily テーブルを削除しようとしています。' as warning_message,
    '続行する場合は、以下の削除コマンドのコメントアウトを解除して実行してください。' as instruction;

-- =====================================================
-- 5. stocks_daily テーブル削除実行
-- =====================================================

-- 注意: 以下のコマンドは慎重に実行してください
-- 削除を実行する場合は、コメントアウト（--）を削除してください

-- 5.1 関連するインデックスの削除（自動的に削除されますが、明示的に記載）
-- DROP INDEX IF EXISTS idx_stocks_daily_symbol;
-- DROP INDEX IF EXISTS idx_stocks_daily_date;
-- DROP INDEX IF EXISTS idx_stocks_daily_symbol_date_desc;

-- 5.2 関連する制約の削除（自動的に削除されますが、明示的に記載）
-- ALTER TABLE stocks_daily DROP CONSTRAINT IF EXISTS uk_stocks_daily_symbol_date;
-- ALTER TABLE stocks_daily DROP CONSTRAINT IF EXISTS ck_stocks_daily_prices;
-- ALTER TABLE stocks_daily DROP CONSTRAINT IF EXISTS ck_stocks_daily_volume;
-- ALTER TABLE stocks_daily DROP CONSTRAINT IF EXISTS ck_stocks_daily_price_logic;

-- 5.3 テーブル本体の削除
-- DROP TABLE IF EXISTS stocks_daily CASCADE;

-- =====================================================
-- 6. 削除後の確認
-- =====================================================

-- 削除実行後に以下のクエリで確認してください（削除実行時にコメントアウトを解除）

-- stocks_daily テーブルが削除されたことを確認
-- SELECT 
--     COUNT(*) as table_count
-- FROM information_schema.tables
-- WHERE table_name = 'stocks_daily';

-- stocks_1d テーブルが正常に存在することを確認
-- SELECT 
--     'stocks_1d' as table_name,
--     COUNT(*) as record_count
-- FROM stocks_1d;

-- 削除完了メッセージ
-- SELECT 
--     'stocks_daily テーブルの削除が完了しました。' as completion_message,
--     now() as completion_time;

-- =====================================================
-- 7. ロールバック手順（緊急時用）
-- =====================================================

-- 万が一問題が発生した場合のロールバック手順:
-- 1. バックアップファイルからのリストア:
--    psql -U stock_user -d stock_data_system < backup_file.sql
--
-- 2. 特定テーブルのみのリストア:
--    psql -U stock_user -d stock_data_system < stocks_daily_schema_backup.sql
--    psql -U stock_user -d stock_data_system < stocks_daily_data_backup.sql
--
-- 3. CSVからのリストア:
--    CREATE TABLE stocks_daily (...); -- スキーマ再作成
--    \COPY stocks_daily FROM 'stocks_daily_backup.csv' WITH CSV HEADER;

-- =====================================================
-- 実行ログ記録用
-- =====================================================

-- 実行ログをファイルに記録する場合:
-- \o stocks_daily_removal_log.txt
-- \echo '=== stocks_daily テーブル削除実行ログ ==='
-- \echo '実行日時: ' `date`
-- \echo '実行ユーザー: ' `whoami`
-- \echo '=================================='
-- 
-- 上記の削除コマンドを実行
-- 
-- \echo '削除処理完了'
-- \o

-- =====================================================
-- 注意事項とベストプラクティス
-- =====================================================

-- 1. 本スクリプトは段階的に実行することを推奨します
-- 2. 各段階で結果を確認してから次に進んでください
-- 3. 本番環境では必ずメンテナンス時間内に実行してください
-- 4. 削除後は必ずアプリケーションの動作確認を行ってください
-- 5. 削除実行前に関係者への通知を忘れずに行ってください

-- =====================================================
-- 完了チェックリスト
-- =====================================================

-- [ ] バックアップ取得完了
-- [ ] データ移行完了確認実行
-- [ ] 依存関係確認完了
-- [ ] 関係者への通知完了
-- [ ] メンテナンス時間確保
-- [ ] 削除実行完了
-- [ ] 削除後確認完了
-- [ ] アプリケーション動作確認完了
-- [ ] ログ保存完了