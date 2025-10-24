-- =============================================================================
-- 株価データテーブル構造検証スクリプト（8テーブル構成）
-- Issue #47: データベーススクリプト更新対応
-- =============================================================================

\echo '=== 株価データテーブル構造検証（8テーブル構成） ==='

-- =============================================================================
-- 1. 全テーブル存在確認
-- =============================================================================
\echo '--- 1. 全テーブル存在確認 ---'

SELECT
    schemaname as "スキーマ",
    tablename as "テーブル名",
    tableowner as "所有者",
    hasindexes as "インデックスあり",
    hasrules as "ルールあり",
    hastriggers as "トリガーあり"
FROM pg_tables
WHERE tablename IN ('stocks_1d', 'stocks_1m', 'stocks_5m', 'stocks_15m',
                   'stocks_30m', 'stocks_1h', 'stocks_1wk', 'stocks_1mo')
ORDER BY tablename;

-- 期待されるテーブル数の確認
SELECT
    COUNT(*) as "作成済みテーブル数",
    CASE
        WHEN COUNT(*) = 8 THEN '✓ 全テーブル作成済み'
        ELSE '⚠ 一部テーブルが不足'
    END as "ステータス"
FROM pg_tables
WHERE tablename IN ('stocks_1d', 'stocks_1m', 'stocks_5m', 'stocks_15m',
                   'stocks_30m', 'stocks_1h', 'stocks_1wk', 'stocks_1mo');

-- =============================================================================
-- 2. 各テーブルのカラム構造確認
-- =============================================================================
\echo '--- 2. 各テーブルのカラム構造確認 ---'

-- 日足・週足・月足テーブル（date型使用）
\echo '--- 2-1. 日足・週足・月足テーブル（date型使用） ---'
SELECT
    table_name as "テーブル名",
    ordinal_position as "順序",
    column_name as "カラム名",
    data_type as "データ型",
    character_maximum_length as "最大長",
    numeric_precision as "精度",
    numeric_scale as "小数点以下桁数",
    is_nullable as "NULL許可",
    column_default as "デフォルト値"
FROM information_schema.columns
WHERE table_name IN ('stocks_1d', 'stocks_1wk', 'stocks_1mo')
ORDER BY table_name, ordinal_position;

-- 分足・時間足テーブル（datetime型使用）
\echo '--- 2-2. 分足・時間足テーブル（datetime型使用） ---'
SELECT
    table_name as "テーブル名",
    ordinal_position as "順序",
    column_name as "カラム名",
    data_type as "データ型",
    character_maximum_length as "最大長",
    numeric_precision as "精度",
    numeric_scale as "小数点以下桁数",
    is_nullable as "NULL許可",
    column_default as "デフォルト値"
FROM information_schema.columns
WHERE table_name IN ('stocks_1m', 'stocks_5m', 'stocks_15m', 'stocks_30m', 'stocks_1h')
ORDER BY table_name, ordinal_position;

-- =============================================================================
-- 3. 制約確認（全テーブル）
-- =============================================================================
\echo '--- 3. 制約確認（全テーブル） ---'

SELECT
    table_name as "テーブル名",
    constraint_name as "制約名",
    constraint_type as "制約タイプ",
    CASE constraint_type
        WHEN 'PRIMARY KEY' THEN 'プライマリキー'
        WHEN 'UNIQUE' THEN 'ユニーク制約'
        WHEN 'CHECK' THEN 'チェック制約'
        WHEN 'FOREIGN KEY' THEN '外部キー制約'
        ELSE constraint_type
    END as "制約説明"
FROM information_schema.table_constraints
WHERE table_name IN ('stocks_1d', 'stocks_1m', 'stocks_5m', 'stocks_15m',
                     'stocks_30m', 'stocks_1h', 'stocks_1wk', 'stocks_1mo')
ORDER BY table_name, constraint_name;

-- =============================================================================
-- 4. チェック制約の詳細確認
-- =============================================================================
\echo '--- 4. チェック制約詳細確認 ---'

SELECT
    rel.relname as "テーブル名",
    con.conname as "制約名",
    pg_get_constraintdef(con.oid) as "制約定義"
FROM pg_constraint con
JOIN pg_class rel ON rel.oid = con.conrelid
WHERE rel.relname IN ('stocks_1d', 'stocks_1m', 'stocks_5m', 'stocks_15m',
                      'stocks_30m', 'stocks_1h', 'stocks_1wk', 'stocks_1mo')
AND con.contype = 'c'
ORDER BY rel.relname, con.conname;

-- =============================================================================
-- 5. インデックス確認（全テーブル）
-- =============================================================================
\echo '--- 5. インデックス確認（全テーブル） ---'

SELECT
    tablename as "テーブル名",
    indexname as "インデックス名",
    indexdef as "インデックス定義",
    CASE
        WHEN indexdef LIKE '%UNIQUE%' THEN 'ユニーク'
        WHEN indexdef LIKE '%pkey%' THEN 'プライマリキー'
        ELSE '通常'
    END as "タイプ"
FROM pg_indexes
WHERE tablename IN ('stocks_1d', 'stocks_1m', 'stocks_5m', 'stocks_15m',
                   'stocks_30m', 'stocks_1h', 'stocks_1wk', 'stocks_1mo')
ORDER BY tablename, indexname;

-- =============================================================================
-- 6. トリガー確認（全テーブル）
-- =============================================================================
\echo '--- 6. トリガー確認（全テーブル） ---'

SELECT
    event_object_table as "テーブル名",
    trigger_name as "トリガー名",
    event_manipulation as "イベント",
    action_timing as "タイミング",
    action_statement as "アクション"
FROM information_schema.triggers
WHERE event_object_table IN ('stocks_1d', 'stocks_1m', 'stocks_5m', 'stocks_15m',
                             'stocks_30m', 'stocks_1h', 'stocks_1wk', 'stocks_1mo')
ORDER BY event_object_table, trigger_name;

-- =============================================================================
-- 7. テーブルサイズとレコード数確認
-- =============================================================================
\echo '--- 7. テーブルサイズとレコード数確認 ---'

SELECT
    schemaname as "スキーマ",
    tablename as "テーブル名",
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as "テーブルサイズ",
    pg_size_pretty(pg_relation_size(schemaname||'.'||tablename)) as "データサイズ",
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename) - pg_relation_size(schemaname||'.'||tablename)) as "インデックスサイズ"
FROM pg_tables
WHERE tablename IN ('stocks_1d', 'stocks_1m', 'stocks_5m', 'stocks_15m',
                   'stocks_30m', 'stocks_1h', 'stocks_1wk', 'stocks_1mo')
ORDER BY tablename;

-- 各テーブルのレコード数確認
DO $$
DECLARE
    table_name TEXT;
    record_count INTEGER;
BEGIN
    RAISE NOTICE '--- レコード数確認 ---';

    FOR table_name IN
        SELECT t.tablename
        FROM pg_tables t
        WHERE t.tablename IN ('stocks_1d', 'stocks_1m', 'stocks_5m', 'stocks_15m',
                             'stocks_30m', 'stocks_1h', 'stocks_1wk', 'stocks_1mo')
        ORDER BY t.tablename
    LOOP
        EXECUTE format('SELECT COUNT(*) FROM %I', table_name) INTO record_count;
        RAISE NOTICE 'テーブル %: % レコード', table_name, record_count;
    END LOOP;
END $$;

-- =============================================================================
-- 8. カラムコメント確認
-- =============================================================================
\echo '--- 8. カラムコメント確認 ---'

SELECT
    c.table_name as "テーブル名",
    c.column_name as "カラム名",
    col_description(pgc.oid, c.ordinal_position) as "コメント"
FROM information_schema.columns c
JOIN pg_class pgc ON pgc.relname = c.table_name
WHERE c.table_name IN ('stocks_1d', 'stocks_1m', 'stocks_5m', 'stocks_15m',
                      'stocks_30m', 'stocks_1h', 'stocks_1wk', 'stocks_1mo')
AND col_description(pgc.oid, c.ordinal_position) IS NOT NULL
ORDER BY c.table_name, c.ordinal_position;

-- =============================================================================
-- 9. 構造整合性チェック
-- =============================================================================
\echo '--- 9. 構造整合性チェック ---'

-- 日足・週足・月足テーブルの構造一致確認
WITH date_tables AS (
    SELECT table_name, column_name, data_type, ordinal_position
    FROM information_schema.columns
    WHERE table_name IN ('stocks_1d', 'stocks_1wk', 'stocks_1mo')
),
structure_check AS (
    SELECT
        ordinal_position,
        column_name,
        COUNT(DISTINCT data_type) as type_variations,
        string_agg(DISTINCT table_name || ':' || data_type, ', ') as table_types
    FROM date_tables
    GROUP BY ordinal_position, column_name
)
SELECT
    ordinal_position as "順序",
    column_name as "カラム名",
    CASE
        WHEN type_variations = 1 THEN '✓ 一致'
        ELSE '⚠ 不一致'
    END as "構造一致",
    table_types as "テーブル:データ型"
FROM structure_check
ORDER BY ordinal_position;

-- 分足・時間足テーブルの構造一致確認
WITH datetime_tables AS (
    SELECT table_name, column_name, data_type, ordinal_position
    FROM information_schema.columns
    WHERE table_name IN ('stocks_1m', 'stocks_5m', 'stocks_15m', 'stocks_30m', 'stocks_1h')
),
structure_check AS (
    SELECT
        ordinal_position,
        column_name,
        COUNT(DISTINCT data_type) as type_variations,
        string_agg(DISTINCT table_name || ':' || data_type, ', ') as table_types
    FROM datetime_tables
    GROUP BY ordinal_position, column_name
)
SELECT
    ordinal_position as "順序",
    column_name as "カラム名",
    CASE
        WHEN type_variations = 1 THEN '✓ 一致'
        ELSE '⚠ 不一致'
    END as "構造一致",
    table_types as "テーブル:データ型"
FROM structure_check
ORDER BY ordinal_position;

-- =============================================================================
-- 10. 検証結果サマリー
-- =============================================================================
\echo '--- 10. 検証結果サマリー ---'

DO $$
DECLARE
    table_count INTEGER;
    total_records INTEGER := 0;
    table_name TEXT;
    record_count INTEGER;
BEGIN
    -- テーブル数確認
    SELECT COUNT(*) INTO table_count
    FROM pg_tables
    WHERE tablename IN ('stocks_1d', 'stocks_1m', 'stocks_5m', 'stocks_15m',
                       'stocks_30m', 'stocks_1h', 'stocks_1wk', 'stocks_1mo');

    -- 総レコード数計算
    FOR table_name IN
        SELECT t.tablename
        FROM pg_tables t
        WHERE t.tablename IN ('stocks_1d', 'stocks_1m', 'stocks_5m', 'stocks_15m',
                             'stocks_30m', 'stocks_1h', 'stocks_1wk', 'stocks_1mo')
    LOOP
        EXECUTE format('SELECT COUNT(*) FROM %I', table_name) INTO record_count;
        total_records := total_records + record_count;
    END LOOP;

    RAISE NOTICE '=== 検証結果サマリー ===';
    RAISE NOTICE '作成済みテーブル数: % / 8', table_count;
    RAISE NOTICE '総レコード数: %', total_records;
    RAISE NOTICE '検証完了時刻: %', CURRENT_TIMESTAMP;

    IF table_count = 8 THEN
        RAISE NOTICE 'ステータス: ✓ 8テーブル構成の作成が完了しています';
    ELSE
        RAISE NOTICE 'ステータス: ⚠ 一部テーブルが不足しています';
    END IF;
END $$;

-- =============================================================================
-- 使用方法:
-- psql -U stock_user -d stock_data_system -f scripts/validate_stocks_daily_schema.sql
-- =============================================================================
