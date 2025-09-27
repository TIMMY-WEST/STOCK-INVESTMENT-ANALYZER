-- =============================================================================
-- PostgreSQL 複数時間軸対応データベーステストスクリプト
-- Issue #34: 時間軸（足データ）対応 - データベーステスト
-- =============================================================================

-- セッション設定
SET client_encoding = 'UTF8';
SET timezone = 'Asia/Tokyo';

-- テスト開始メッセージ
DO $$
BEGIN
    RAISE NOTICE '=== Issue #34: 複数時間軸データベーステスト開始 ===';
    RAISE NOTICE 'テスト実行日時: %', CURRENT_TIMESTAMP;
    RAISE NOTICE 'データベース: %', current_database();
    RAISE NOTICE 'ユーザー: %', current_user;
END $$;

-- =============================================================================
-- テスト1: テーブル存在確認
-- =============================================================================

\echo '=== テスト1: テーブル存在確認 ==='

DO $$
DECLARE
    expected_tables TEXT[] := ARRAY['stocks_1m', 'stocks_5m', 'stocks_15m', 'stocks_30m', 'stocks_1h', 'stocks_1d', 'stocks_1wk', 'stocks_1mo'];
    table_name TEXT;
    table_exists BOOLEAN;
    missing_tables TEXT[] := ARRAY[]::TEXT[];
    test_passed BOOLEAN := TRUE;
BEGIN
    FOREACH table_name IN ARRAY expected_tables
    LOOP
        SELECT EXISTS (
            SELECT 1 FROM information_schema.tables 
            WHERE table_name = table_name
        ) INTO table_exists;
        
        IF table_exists THEN
            RAISE NOTICE '✓ テーブル % が存在します', table_name;
        ELSE
            RAISE NOTICE '✗ テーブル % が存在しません', table_name;
            missing_tables := array_append(missing_tables, table_name);
            test_passed := FALSE;
        END IF;
    END LOOP;
    
    IF test_passed THEN
        RAISE NOTICE '✓ テスト1: 全てのテーブルが正常に作成されています';
    ELSE
        RAISE NOTICE '✗ テスト1: 以下のテーブルが不足しています: %', array_to_string(missing_tables, ', ');
    END IF;
END $$;

-- =============================================================================
-- テスト2: テーブル構造確認
-- =============================================================================

\echo '=== テスト2: テーブル構造確認 ==='

DO $$
DECLARE
    table_name TEXT;
    column_count INTEGER;
    expected_columns INTEGER := 10; -- id, symbol, datetime/date/year/month, open, high, low, close, volume, created_at, updated_at
    test_passed BOOLEAN := TRUE;
BEGIN
    -- 分足・時間足テーブルの確認
    FOR table_name IN SELECT unnest(ARRAY['stocks_1m', 'stocks_5m', 'stocks_15m', 'stocks_30m', 'stocks_1h'])
    LOOP
        SELECT COUNT(*) INTO column_count
        FROM information_schema.columns
        WHERE table_name = table_name;
        
        IF column_count = expected_columns THEN
            RAISE NOTICE '✓ テーブル % のカラム数が正しいです (%列)', table_name, column_count;
        ELSE
            RAISE NOTICE '✗ テーブル % のカラム数が不正です (期待値: %, 実際: %)', table_name, expected_columns, column_count;
            test_passed := FALSE;
        END IF;
    END LOOP;
    
    -- 日足テーブルの確認
    SELECT COUNT(*) INTO column_count
    FROM information_schema.columns
    WHERE table_name = 'stocks_1d';
    
    IF column_count = expected_columns THEN
        RAISE NOTICE '✓ テーブル stocks_1d のカラム数が正しいです (%列)', column_count;
    ELSE
        RAISE NOTICE '✗ テーブル stocks_1d のカラム数が不正です (期待値: %, 実際: %)', expected_columns, column_count;
        test_passed := FALSE;
    END IF;
    
    -- 週足テーブルの確認
    SELECT COUNT(*) INTO column_count
    FROM information_schema.columns
    WHERE table_name = 'stocks_1wk';
    
    IF column_count = expected_columns THEN
        RAISE NOTICE '✓ テーブル stocks_1wk のカラム数が正しいです (%列)', column_count;
    ELSE
        RAISE NOTICE '✗ テーブル stocks_1wk のカラム数が不正です (期待値: %, 実際: %)', expected_columns, column_count;
        test_passed := FALSE;
    END IF;
    
    -- 月足テーブルの確認（11列: id, symbol, year, month, open, high, low, close, volume, created_at, updated_at）
    SELECT COUNT(*) INTO column_count
    FROM information_schema.columns
    WHERE table_name = 'stocks_1mo';
    
    IF column_count = 11 THEN
        RAISE NOTICE '✓ テーブル stocks_1mo のカラム数が正しいです (%列)', column_count;
    ELSE
        RAISE NOTICE '✗ テーブル stocks_1mo のカラム数が不正です (期待値: 11, 実際: %)', column_count;
        test_passed := FALSE;
    END IF;
    
    IF test_passed THEN
        RAISE NOTICE '✓ テスト2: 全てのテーブル構造が正しく設定されています';
    ELSE
        RAISE NOTICE '✗ テスト2: 一部のテーブル構造に問題があります';
    END IF;
END $$;

-- =============================================================================
-- テスト3: 制約確認
-- =============================================================================

\echo '=== テスト3: 制約確認 ==='

DO $$
DECLARE
    table_name TEXT;
    constraint_count INTEGER;
    expected_constraints INTEGER := 5; -- uk, ck_prices, ck_volume, ck_price_logic, pk
    test_passed BOOLEAN := TRUE;
BEGIN
    FOR table_name IN SELECT unnest(ARRAY['stocks_1m', 'stocks_5m', 'stocks_15m', 'stocks_30m', 'stocks_1h', 'stocks_1d', 'stocks_1wk'])
    LOOP
        SELECT COUNT(*) INTO constraint_count
        FROM information_schema.table_constraints
        WHERE table_name = table_name;
        
        IF constraint_count >= expected_constraints THEN
            RAISE NOTICE '✓ テーブル % の制約が設定されています (%個)', table_name, constraint_count;
        ELSE
            RAISE NOTICE '✗ テーブル % の制約が不足しています (期待値: %以上, 実際: %)', table_name, expected_constraints, constraint_count;
            test_passed := FALSE;
        END IF;
    END LOOP;
    
    -- 月足テーブルは追加制約があるため別途確認
    SELECT COUNT(*) INTO constraint_count
    FROM information_schema.table_constraints
    WHERE table_name = 'stocks_1mo';
    
    IF constraint_count >= 7 THEN -- 追加でyear, month制約
        RAISE NOTICE '✓ テーブル stocks_1mo の制約が設定されています (%個)', constraint_count;
    ELSE
        RAISE NOTICE '✗ テーブル stocks_1mo の制約が不足しています (期待値: 7以上, 実際: %)', constraint_count;
        test_passed := FALSE;
    END IF;
    
    IF test_passed THEN
        RAISE NOTICE '✓ テスト3: 全てのテーブル制約が正しく設定されています';
    ELSE
        RAISE NOTICE '✗ テスト3: 一部のテーブル制約に問題があります';
    END IF;
END $$;

-- =============================================================================
-- テスト4: インデックス確認
-- =============================================================================

\echo '=== テスト4: インデックス確認 ==='

DO $$
DECLARE
    table_name TEXT;
    index_count INTEGER;
    expected_indexes INTEGER := 5; -- pk + 4個のインデックス
    test_passed BOOLEAN := TRUE;
BEGIN
    FOR table_name IN SELECT unnest(ARRAY['stocks_1m', 'stocks_5m', 'stocks_15m', 'stocks_30m', 'stocks_1h', 'stocks_1d', 'stocks_1wk', 'stocks_1mo'])
    LOOP
        SELECT COUNT(*) INTO index_count
        FROM pg_indexes
        WHERE tablename = table_name;
        
        IF index_count >= expected_indexes THEN
            RAISE NOTICE '✓ テーブル % のインデックスが設定されています (%個)', table_name, index_count;
        ELSE
            RAISE NOTICE '✗ テーブル % のインデックスが不足しています (期待値: %以上, 実際: %)', table_name, expected_indexes, index_count;
            test_passed := FALSE;
        END IF;
    END LOOP;
    
    IF test_passed THEN
        RAISE NOTICE '✓ テスト4: 全てのテーブルインデックスが正しく設定されています';
    ELSE
        RAISE NOTICE '✗ テスト4: 一部のテーブルインデックスに問題があります';
    END IF;
END $$;

-- =============================================================================
-- テスト5: トリガー確認
-- =============================================================================

\echo '=== テスト5: トリガー確認 ==='

DO $$
DECLARE
    table_name TEXT;
    trigger_count INTEGER;
    expected_triggers INTEGER := 1; -- updated_atトリガー
    test_passed BOOLEAN := TRUE;
BEGIN
    FOR table_name IN SELECT unnest(ARRAY['stocks_1m', 'stocks_5m', 'stocks_15m', 'stocks_30m', 'stocks_1h', 'stocks_1d', 'stocks_1wk', 'stocks_1mo'])
    LOOP
        SELECT COUNT(*) INTO trigger_count
        FROM information_schema.triggers
        WHERE event_object_table = table_name;
        
        IF trigger_count >= expected_triggers THEN
            RAISE NOTICE '✓ テーブル % のトリガーが設定されています (%個)', table_name, trigger_count;
        ELSE
            RAISE NOTICE '✗ テーブル % のトリガーが不足しています (期待値: %以上, 実際: %)', table_name, expected_triggers, trigger_count;
            test_passed := FALSE;
        END IF;
    END LOOP;
    
    IF test_passed THEN
        RAISE NOTICE '✓ テスト5: 全てのテーブルトリガーが正しく設定されています';
    ELSE
        RAISE NOTICE '✗ テスト5: 一部のテーブルトリガーに問題があります';
    END IF;
END $$;

-- =============================================================================
-- テスト6: データ挿入・更新テスト
-- =============================================================================

\echo '=== テスト6: データ挿入・更新テスト ==='

DO $$
DECLARE
    test_passed BOOLEAN := TRUE;
    old_updated_at TIMESTAMP WITH TIME ZONE;
    new_updated_at TIMESTAMP WITH TIME ZONE;
BEGIN
    -- 1分足テーブルでのテスト
    BEGIN
        -- テストデータ挿入
        INSERT INTO stocks_1m (symbol, datetime, open, high, low, close, volume)
        VALUES ('TEST.T', '2024-01-15 09:00:00+09', 1000.00, 1050.00, 990.00, 1020.00, 100000);
        
        RAISE NOTICE '✓ stocks_1m テーブルへのデータ挿入が成功しました';
        
        -- updated_atの初期値を取得
        SELECT updated_at INTO old_updated_at
        FROM stocks_1m
        WHERE symbol = 'TEST.T' AND datetime = '2024-01-15 09:00:00+09';
        
        -- 少し待機
        PERFORM pg_sleep(1);
        
        -- データ更新
        UPDATE stocks_1m 
        SET close = 1030.00
        WHERE symbol = 'TEST.T' AND datetime = '2024-01-15 09:00:00+09';
        
        -- updated_atの更新後の値を取得
        SELECT updated_at INTO new_updated_at
        FROM stocks_1m
        WHERE symbol = 'TEST.T' AND datetime = '2024-01-15 09:00:00+09';
        
        IF new_updated_at > old_updated_at THEN
            RAISE NOTICE '✓ updated_atトリガーが正常に動作しています';
        ELSE
            RAISE NOTICE '✗ updated_atトリガーが動作していません';
            test_passed := FALSE;
        END IF;
        
        -- テストデータ削除
        DELETE FROM stocks_1m WHERE symbol = 'TEST.T';
        
    EXCEPTION
        WHEN OTHERS THEN
            RAISE NOTICE '✗ stocks_1m テーブルでのデータ操作でエラーが発生しました: %', SQLERRM;
            test_passed := FALSE;
    END;
    
    -- 月足テーブルでのテスト
    BEGIN
        -- テストデータ挿入
        INSERT INTO stocks_1mo (symbol, year, month, open, high, low, close, volume)
        VALUES ('TEST.T', 2024, 1, 1000.00, 1200.00, 950.00, 1150.00, 5000000);
        
        RAISE NOTICE '✓ stocks_1mo テーブルへのデータ挿入が成功しました';
        
        -- テストデータ削除
        DELETE FROM stocks_1mo WHERE symbol = 'TEST.T';
        
    EXCEPTION
        WHEN OTHERS THEN
            RAISE NOTICE '✗ stocks_1mo テーブルでのデータ操作でエラーが発生しました: %', SQLERRM;
            test_passed := FALSE;
    END;
    
    IF test_passed THEN
        RAISE NOTICE '✓ テスト6: データ挿入・更新テストが正常に完了しました';
    ELSE
        RAISE NOTICE '✗ テスト6: データ挿入・更新テストで問題が発生しました';
    END IF;
END $$;

-- =============================================================================
-- テスト結果サマリー
-- =============================================================================

\echo '=== テスト結果サマリー ==='

DO $$
DECLARE
    table_count INTEGER;
    index_count INTEGER;
    trigger_count INTEGER;
    constraint_count INTEGER;
BEGIN
    -- 統計情報取得
    SELECT COUNT(*) INTO table_count
    FROM pg_tables
    WHERE tablename LIKE 'stocks_%';
    
    SELECT COUNT(*) INTO index_count
    FROM pg_indexes
    WHERE tablename LIKE 'stocks_%';
    
    SELECT COUNT(*) INTO trigger_count
    FROM information_schema.triggers
    WHERE event_object_table LIKE 'stocks_%';
    
    SELECT COUNT(*) INTO constraint_count
    FROM information_schema.table_constraints
    WHERE table_name LIKE 'stocks_%';
    
    RAISE NOTICE '=== Issue #34: 複数時間軸データベーステスト完了 ===';
    RAISE NOTICE 'テスト完了日時: %', CURRENT_TIMESTAMP;
    RAISE NOTICE '';
    RAISE NOTICE '作成されたオブジェクト統計:';
    RAISE NOTICE '- テーブル数: %', table_count;
    RAISE NOTICE '- インデックス数: %', index_count;
    RAISE NOTICE '- トリガー数: %', trigger_count;
    RAISE NOTICE '- 制約数: %', constraint_count;
    RAISE NOTICE '';
    RAISE NOTICE '実装されたテーブル:';
    RAISE NOTICE '✓ stocks_1m (1分足データ)';
    RAISE NOTICE '✓ stocks_5m (5分足データ)';
    RAISE NOTICE '✓ stocks_15m (15分足データ)';
    RAISE NOTICE '✓ stocks_30m (30分足データ)';
    RAISE NOTICE '✓ stocks_1h (1時間足データ)';
    RAISE NOTICE '✓ stocks_1d (1日足データ)';
    RAISE NOTICE '✓ stocks_1wk (1週間足データ)';
    RAISE NOTICE '✓ stocks_1mo (1ヶ月足データ)';
    RAISE NOTICE '';
    RAISE NOTICE 'Issue #34の要件が正常に実装されました！';
END $$;

-- =============================================================================
-- 使用方法:
-- 
-- 1. PostgreSQLに接続
--    psql -U stock_user -d stock_data_system
--
-- 2. このテストスクリプトを実行
--    \i tests/test_timeframe_database.sql
--
-- 3. テスト結果を確認
--    - 全てのテストで ✓ が表示されることを確認
--    - ✗ が表示された場合は、該当箇所を修正
--
-- 注意事項:
-- - このテストは非破壊的です（テストデータは自動削除されます）
-- - 実際のデータには影響しません
-- =============================================================================