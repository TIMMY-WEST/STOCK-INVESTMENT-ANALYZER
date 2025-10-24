-- =============================================================================
-- stocks_daily テーブル制約テストスクリプト
-- Issue #6: 制約設定の動作確認用
-- =============================================================================

-- テスト実行前の状態確認
\echo '=== stocks_daily テーブル制約テスト開始 ==='

-- テーブル存在確認
SELECT EXISTS (
    SELECT FROM information_schema.tables
    WHERE table_name = 'stocks_daily'
) as "stocks_daily_exists";

-- 制約一覧確認
SELECT
    constraint_name,
    constraint_type,
    table_name
FROM information_schema.table_constraints
WHERE table_name = 'stocks_daily'
ORDER BY constraint_name;

-- =============================================================================
-- テスト1: 正常データの挿入テスト
-- =============================================================================
\echo '--- テスト1: 正常データ挿入 ---'

BEGIN;
INSERT INTO stocks_daily (symbol, date, open, high, low, close, volume)
VALUES ('TEST.T', '2024-12-01', 1000.00, 1100.00, 950.00, 1050.00, 500000);

SELECT 'テスト1: 正常データ挿入 - 成功' as test_result;
ROLLBACK;

-- =============================================================================
-- テスト2: 重複データ制約テスト (symbol + date)
-- =============================================================================
\echo '--- テスト2: 重複データ制約テスト ---'

BEGIN;
-- 最初のデータ挿入
INSERT INTO stocks_daily (symbol, date, open, high, low, close, volume)
VALUES ('DUP.T', '2024-12-01', 1000.00, 1100.00, 950.00, 1050.00, 500000);

-- 重複データ挿入（エラーになるはず）
DO $$
BEGIN
    BEGIN
        INSERT INTO stocks_daily (symbol, date, open, high, low, close, volume)
        VALUES ('DUP.T', '2024-12-01', 1100.00, 1200.00, 1050.00, 1150.00, 600000);
        RAISE NOTICE 'テスト2: 重複制約 - 失敗（制約が機能していません）';
    EXCEPTION
        WHEN unique_violation THEN
            RAISE NOTICE 'テスト2: 重複制約 - 成功（重複が正しく拒否されました）';
    END;
END $$;
ROLLBACK;

-- =============================================================================
-- テスト3: 負の価格制約テスト
-- =============================================================================
\echo '--- テスト3: 負の価格制約テスト ---'

BEGIN;
DO $$
BEGIN
    BEGIN
        INSERT INTO stocks_daily (symbol, date, open, high, low, close, volume)
        VALUES ('NEG.T', '2024-12-01', -100.00, 1100.00, 950.00, 1050.00, 500000);
        RAISE NOTICE 'テスト3: 負の価格制約 - 失敗（制約が機能していません）';
    EXCEPTION
        WHEN check_violation THEN
            RAISE NOTICE 'テスト3: 負の価格制約 - 成功（負の価格が正しく拒否されました）';
    END;
END $$;
ROLLBACK;

-- =============================================================================
-- テスト4: 負の出来高制約テスト
-- =============================================================================
\echo '--- テスト4: 負の出来高制約テスト ---'

BEGIN;
DO $$
BEGIN
    BEGIN
        INSERT INTO stocks_daily (symbol, date, open, high, low, close, volume)
        VALUES ('VOL.T', '2024-12-01', 1000.00, 1100.00, 950.00, 1050.00, -500000);
        RAISE NOTICE 'テスト4: 負の出来高制約 - 失敗（制約が機能していません）';
    EXCEPTION
        WHEN check_violation THEN
            RAISE NOTICE 'テスト4: 負の出来高制約 - 成功（負の出来高が正しく拒否されました）';
    END;
END $$;
ROLLBACK;

-- =============================================================================
-- テスト5: 価格論理制約テスト (high < low)
-- =============================================================================
\echo '--- テスト5: 価格論理制約テスト ---'

BEGIN;
DO $$
BEGIN
    BEGIN
        INSERT INTO stocks_daily (symbol, date, open, high, low, close, volume)
        VALUES ('LOGIC.T', '2024-12-01', 1000.00, 950.00, 1100.00, 1050.00, 500000);
        RAISE NOTICE 'テスト5: 価格論理制約 - 失敗（制約が機能していません）';
    EXCEPTION
        WHEN check_violation THEN
            RAISE NOTICE 'テスト5: 価格論理制約 - 成功（高値<安値が正しく拒否されました）';
    END;
END $$;
ROLLBACK;

-- =============================================================================
-- テスト6: インデックス確認
-- =============================================================================
\echo '--- テスト6: インデックス確認 ---'

SELECT
    indexname as "インデックス名",
    tablename as "テーブル名"
FROM pg_indexes
WHERE tablename = 'stocks_daily'
ORDER BY indexname;

-- =============================================================================
-- テスト完了
-- =============================================================================
\echo '=== stocks_daily テーブル制約テスト完了 ==='
\echo 'すべてのテストが「成功」と表示されていれば、制約が正しく動作しています'
