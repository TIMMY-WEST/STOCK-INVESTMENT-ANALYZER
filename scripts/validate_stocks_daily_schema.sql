-- =============================================================================
-- stocks_daily テーブル構造検証スクリプト
-- Issue #6: PRレビュー用構造確認
-- =============================================================================

\echo '=== stocks_daily テーブル構造検証 ==='

-- =============================================================================
-- 1. テーブル存在確認
-- =============================================================================
\echo '--- 1. テーブル存在確認 ---'

SELECT
    schemaname as "スキーマ",
    tablename as "テーブル名",
    tableowner as "所有者",
    hasindexes as "インデックスあり",
    hasrules as "ルールあり",
    hastriggers as "トリガーあり"
FROM pg_tables
WHERE tablename = 'stocks_daily';

-- =============================================================================
-- 2. カラム構造確認
-- =============================================================================
\echo '--- 2. カラム構造確認 ---'

SELECT
    ordinal_position as "順序",
    column_name as "カラム名",
    data_type as "データ型",
    character_maximum_length as "最大長",
    numeric_precision as "精度",
    numeric_scale as "小数点以下桁数",
    is_nullable as "NULL許可",
    column_default as "デフォルト値"
FROM information_schema.columns
WHERE table_name = 'stocks_daily'
ORDER BY ordinal_position;

-- =============================================================================
-- 3. 制約確認
-- =============================================================================
\echo '--- 3. 制約確認 ---'

SELECT
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
WHERE table_name = 'stocks_daily'
ORDER BY constraint_name;

-- =============================================================================
-- 4. チェック制約の詳細
-- =============================================================================
\echo '--- 4. チェック制約詳細 ---'

SELECT
    con.conname as "制約名",
    pg_get_constraintdef(con.oid) as "制約定義"
FROM pg_constraint con
JOIN pg_class rel ON rel.oid = con.conrelid
WHERE rel.relname = 'stocks_daily'
AND con.contype = 'c'
ORDER BY con.conname;

-- =============================================================================
-- 5. インデックス確認
-- =============================================================================
\echo '--- 5. インデックス確認 ---'

SELECT
    indexname as "インデックス名",
    indexdef as "インデックス定義",
    CASE
        WHEN indexdef LIKE '%UNIQUE%' THEN 'ユニーク'
        ELSE '通常'
    END as "タイプ"
FROM pg_indexes
WHERE tablename = 'stocks_daily'
ORDER BY indexname;

-- =============================================================================
-- 6. トリガー確認
-- =============================================================================
\echo '--- 6. トリガー確認 ---'

SELECT
    trigger_name as "トリガー名",
    event_manipulation as "イベント",
    action_timing as "タイミング",
    action_statement as "アクション"
FROM information_schema.triggers
WHERE event_object_table = 'stocks_daily'
ORDER BY trigger_name;

-- =============================================================================
-- 7. テーブルサイズ確認
-- =============================================================================
\echo '--- 7. テーブルサイズ確認 ---'

SELECT
    pg_size_pretty(pg_total_relation_size('stocks_daily')) as "総サイズ（インデックス含む）",
    pg_size_pretty(pg_relation_size('stocks_daily')) as "テーブルサイズ",
    pg_size_pretty(pg_indexes_size('stocks_daily')) as "インデックスサイズ";

-- =============================================================================
-- 8. データ件数確認
-- =============================================================================
\echo '--- 8. データ件数確認 ---'

SELECT
    COUNT(*) as "総レコード数",
    COUNT(DISTINCT symbol) as "ユニーク銘柄数",
    MIN(date) as "最古日付",
    MAX(date) as "最新日付"
FROM stocks_daily;

-- =============================================================================
-- 9. 設計書との適合性チェック
-- =============================================================================
\echo '--- 9. 設計書適合性チェック ---'

-- 必須カラムの存在確認
WITH expected_columns AS (
    SELECT unnest(ARRAY[
        'id', 'symbol', 'date', 'open', 'high', 'low', 'close', 'volume', 'created_at', 'updated_at'
    ]) as expected_column
),
actual_columns AS (
    SELECT column_name
    FROM information_schema.columns
    WHERE table_name = 'stocks_daily'
)
SELECT
    ec.expected_column as "必須カラム",
    CASE WHEN ac.column_name IS NOT NULL THEN '存在' ELSE '不足' END as "状態"
FROM expected_columns ec
LEFT JOIN actual_columns ac ON ec.expected_column = ac.column_name
ORDER BY ec.expected_column;

-- 必須制約の存在確認
WITH expected_constraints AS (
    SELECT unnest(ARRAY[
        'stocks_daily_pkey',
        'uk_stocks_daily_symbol_date',
        'ck_stocks_daily_prices',
        'ck_stocks_daily_volume',
        'ck_stocks_daily_price_logic'
    ]) as expected_constraint
),
actual_constraints AS (
    SELECT constraint_name
    FROM information_schema.table_constraints
    WHERE table_name = 'stocks_daily'
)
SELECT
    ec.expected_constraint as "必須制約",
    CASE WHEN ac.constraint_name IS NOT NULL THEN '存在' ELSE '不足' END as "状態"
FROM expected_constraints ec
LEFT JOIN actual_constraints ac ON ec.expected_constraint = ac.constraint_name
ORDER BY ec.expected_constraint;

\echo '=== 検証完了 ==='
\echo 'すべてのカラム・制約が「存在」になっていれば設計書に適合しています'