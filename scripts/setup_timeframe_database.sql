-- =============================================================================
-- PostgreSQL 複数時間軸対応データベース統合セットアップスクリプト
-- Issue #34: 時間軸（足データ）対応 - データベース設計
-- 
-- このスクリプトは以下を実行します：
-- 1. 既存のstocks_dailyテーブルをstocks_1dにリネーム
-- 2. 8つの時間軸テーブルを作成
-- 3. 統一されたインデックス設計を適用
-- 4. トリガーの設定
-- =============================================================================

-- セッション設定
SET client_encoding = 'UTF8';
SET timezone = 'Asia/Tokyo';

-- 実行開始メッセージ
DO $$
BEGIN
    RAISE NOTICE '=== Issue #34: 複数時間軸対応データベースセットアップ開始 ===';
    RAISE NOTICE '実行日時: %', CURRENT_TIMESTAMP;
    RAISE NOTICE 'データベース: %', current_database();
    RAISE NOTICE 'ユーザー: %', current_user;
END $$;

-- =============================================================================
-- ステップ1: テーブル作成
-- =============================================================================

\echo '=== ステップ1: 複数時間軸テーブル作成 ==='
\i scripts/create_timeframe_tables.sql

-- =============================================================================
-- ステップ2: インデックス・トリガー作成
-- =============================================================================

\echo '=== ステップ2: インデックス・トリガー作成 ==='
\i scripts/create_timeframe_indexes.sql

-- =============================================================================
-- ステップ3: セットアップ完了確認
-- =============================================================================

\echo '=== ステップ3: セットアップ完了確認 ==='

-- 作成されたテーブル一覧
\echo '--- 作成されたテーブル一覧 ---'
SELECT
    schemaname as "スキーマ",
    tablename as "テーブル名",
    tableowner as "所有者"
FROM pg_tables
WHERE tablename LIKE 'stocks_%'
ORDER BY 
    CASE tablename
        WHEN 'stocks_1m' THEN 1
        WHEN 'stocks_5m' THEN 2
        WHEN 'stocks_15m' THEN 3
        WHEN 'stocks_30m' THEN 4
        WHEN 'stocks_1h' THEN 5
        WHEN 'stocks_1d' THEN 6
        WHEN 'stocks_1wk' THEN 7
        WHEN 'stocks_1mo' THEN 8
        ELSE 9
    END;

-- テーブル数確認
\echo '--- テーブル数確認 ---'
SELECT 
    COUNT(*) as "作成されたテーブル数"
FROM pg_tables
WHERE tablename LIKE 'stocks_%';

-- インデックス数確認
\echo '--- インデックス数確認 ---'
SELECT 
    COUNT(*) as "作成されたインデックス数"
FROM pg_indexes
WHERE tablename LIKE 'stocks_%';

-- トリガー数確認
\echo '--- トリガー数確認 ---'
SELECT 
    COUNT(*) as "作成されたトリガー数"
FROM information_schema.triggers
WHERE event_object_table LIKE 'stocks_%';

-- 各テーブルの構造確認（サンプル）
\echo '--- stocks_1mテーブル構造確認 ---'
\d stocks_1m

-- 完了メッセージ
DO $$
DECLARE
    table_count INTEGER;
    index_count INTEGER;
    trigger_count INTEGER;
BEGIN
    -- テーブル数取得
    SELECT COUNT(*) INTO table_count
    FROM pg_tables
    WHERE tablename LIKE 'stocks_%';
    
    -- インデックス数取得
    SELECT COUNT(*) INTO index_count
    FROM pg_indexes
    WHERE tablename LIKE 'stocks_%';
    
    -- トリガー数取得
    SELECT COUNT(*) INTO trigger_count
    FROM information_schema.triggers
    WHERE event_object_table LIKE 'stocks_%';
    
    RAISE NOTICE '=== Issue #34: 複数時間軸対応データベースセットアップ完了 ===';
    RAISE NOTICE '作成されたテーブル数: %', table_count;
    RAISE NOTICE '作成されたインデックス数: %', index_count;
    RAISE NOTICE '作成されたトリガー数: %', trigger_count;
    RAISE NOTICE '';
    RAISE NOTICE '作成されたテーブル:';
    RAISE NOTICE '- stocks_1m (1分足データ)';
    RAISE NOTICE '- stocks_5m (5分足データ)';
    RAISE NOTICE '- stocks_15m (15分足データ)';
    RAISE NOTICE '- stocks_30m (30分足データ)';
    RAISE NOTICE '- stocks_1h (1時間足データ)';
    RAISE NOTICE '- stocks_1d (1日足データ)';
    RAISE NOTICE '- stocks_1wk (1週間足データ)';
    RAISE NOTICE '- stocks_1mo (1ヶ月足データ)';
    RAISE NOTICE '';
    RAISE NOTICE '次のステップ:';
    RAISE NOTICE '1. アプリケーションコードでの各テーブルへの対応';
    RAISE NOTICE '2. データ取得・保存ロジックの実装';
    RAISE NOTICE '3. テストデータの投入と動作確認';
    RAISE NOTICE '';
    RAISE NOTICE 'セットアップ完了日時: %', CURRENT_TIMESTAMP;
END $$;

-- =============================================================================
-- 使用方法:
-- 
-- 1. PostgreSQLに接続
--    psql -U stock_user -d stock_data_system
--
-- 2. このスクリプトを実行
--    \i scripts/setup_timeframe_database.sql
--
-- 3. 実行結果を確認
--    - テーブル一覧: \dt stocks_*
--    - 特定テーブル詳細: \d stocks_1m
--    - インデックス確認: \di stocks_*
--
-- 注意事項:
-- - 既存のstocks_dailyテーブルがある場合、stocks_1dにリネームされます
-- - 既存データは保持されます
-- - 実行前にバックアップを取ることを推奨します
-- =============================================================================