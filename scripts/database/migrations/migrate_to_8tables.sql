-- =============================================================================
-- PostgreSQL マイグレーションスクリプト
-- 既存 stocks_daily テーブルから 8テーブル構成への移行
-- =============================================================================

-- セッション設定
SET client_encoding = 'UTF8';
SET timezone = 'Asia/Tokyo';

-- 現在の接続情報を確認
SELECT
    current_database() as "接続中のデータベース",
    current_user as "現在のユーザー",
    CURRENT_TIMESTAMP as "マイグレーション開始時刻";

-- =============================================================================
-- 注意事項
-- =============================================================================
-- このスクリプトは既存の stocks_daily テーブルから新しい8テーブル構成に移行します。
-- 実行前に必ずデータベースのバックアップを取得してください。
--
-- バックアップコマンド例:
-- pg_dump -U stock_user -d stock_data_system > backup_before_migration.sql

-- =============================================================================
-- 1. 既存テーブル確認
-- =============================================================================

-- 既存テーブルの存在確認
DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'stocks_daily') THEN
        RAISE NOTICE '既存の stocks_daily テーブルが見つかりました';

        -- 既存データ件数確認
        EXECUTE 'SELECT COUNT(*) FROM stocks_daily' INTO @count;
        RAISE NOTICE 'stocks_daily テーブルのレコード数: %', @count;
    ELSE
        RAISE NOTICE '既存の stocks_daily テーブルが見つかりません';
        RAISE NOTICE '新規インストールとして処理します';
    END IF;
END $$;

-- =============================================================================
-- 2. 新しいテーブル構造の作成
-- =============================================================================

-- 新しい8テーブル構成を作成（既に存在する場合はスキップ）
DO $$
BEGIN
    -- stocks_1d テーブルが存在しない場合のみ作成
    IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'stocks_1d') THEN
        RAISE NOTICE '新しい8テーブル構成を作成します...';
        -- create_tables.sql の内容を実行
        -- 注意: この部分は実際の環境では \i scripts/create_tables.sql で実行してください
        RAISE NOTICE '新しいテーブル構成の作成が必要です';
        RAISE NOTICE '以下のコマンドを実行してください:';
        RAISE NOTICE '\i scripts/create_tables.sql';
    ELSE
        RAISE NOTICE '新しいテーブル構成は既に存在します';
    END IF;
END $$;

-- =============================================================================
-- 3. データ移行（stocks_daily → stocks_1d）
-- =============================================================================

-- stocks_daily テーブルが存在し、stocks_1d テーブルも存在する場合のみ実行
DO $$
DECLARE
    source_count INTEGER;
    target_count INTEGER;
BEGIN
    -- 移行元テーブルの存在確認
    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'stocks_daily') AND
       EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'stocks_1d') THEN

        -- 移行元データ件数確認
        SELECT COUNT(*) INTO source_count FROM stocks_daily;
        SELECT COUNT(*) INTO target_count FROM stocks_1d;

        RAISE NOTICE 'データ移行を開始します...';
        RAISE NOTICE '移行元 stocks_daily: % レコード', source_count;
        RAISE NOTICE '移行先 stocks_1d: % レコード', target_count;

        -- 重複データを避けるため、既存データをクリア（オプション）
        -- DELETE FROM stocks_1d;

        -- データ移行実行
        INSERT INTO stocks_1d (symbol, date, open, high, low, close, volume, created_at, updated_at)
        SELECT
            symbol,
            date,
            open,
            high,
            low,
            close,
            volume,
            COALESCE(created_at, CURRENT_TIMESTAMP),
            COALESCE(updated_at, CURRENT_TIMESTAMP)
        FROM stocks_daily
        ON CONFLICT (symbol, date) DO UPDATE SET
            open = EXCLUDED.open,
            high = EXCLUDED.high,
            low = EXCLUDED.low,
            close = EXCLUDED.close,
            volume = EXCLUDED.volume,
            updated_at = CURRENT_TIMESTAMP;

        -- 移行後データ件数確認
        SELECT COUNT(*) INTO target_count FROM stocks_1d;
        RAISE NOTICE 'データ移行完了: % レコードを stocks_1d に移行しました', target_count;

    ELSE
        RAISE NOTICE 'データ移行をスキップします（必要なテーブルが存在しません）';
    END IF;
END $$;

-- =============================================================================
-- 4. 移行結果確認
-- =============================================================================

-- 各テーブルのレコード数確認
DO $$
DECLARE
    table_name TEXT;
    record_count INTEGER;
BEGIN
    RAISE NOTICE '=== 移行結果確認 ===';

    -- 各テーブルのレコード数を確認
    FOR table_name IN
        SELECT t.table_name
        FROM information_schema.tables t
        WHERE t.table_schema = 'public'
        AND t.table_name LIKE 'stocks_%'
        ORDER BY t.table_name
    LOOP
        EXECUTE format('SELECT COUNT(*) FROM %I', table_name) INTO record_count;
        RAISE NOTICE 'テーブル %: % レコード', table_name, record_count;
    END LOOP;
END $$;

-- =============================================================================
-- 5. 旧テーブルのバックアップと削除（オプション）
-- =============================================================================

-- 注意: 以下の処理は慎重に実行してください
-- 移行が正常に完了し、アプリケーションの動作確認が済んでから実行することを推奨します

/*
-- 旧テーブルをバックアップテーブルとしてリネーム
DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'stocks_daily') THEN
        -- バックアップテーブル名に変更
        ALTER TABLE stocks_daily RENAME TO stocks_daily_backup_migration;
        RAISE NOTICE '旧テーブル stocks_daily を stocks_daily_backup_migration にリネームしました';

        -- バックアップテーブルにコメント追加
        COMMENT ON TABLE stocks_daily_backup_migration IS
            '8テーブル構成移行前のバックアップテーブル（' || CURRENT_TIMESTAMP || '）';
    END IF;
END $$;
*/

-- =============================================================================
-- 6. インデックス再構築（パフォーマンス最適化）
-- =============================================================================

-- 移行後のインデックス統計情報を更新
DO $$
DECLARE
    table_name TEXT;
BEGIN
    RAISE NOTICE 'インデックス統計情報を更新中...';

    FOR table_name IN
        SELECT t.table_name
        FROM information_schema.tables t
        WHERE t.table_schema = 'public'
        AND t.table_name LIKE 'stocks_%'
        AND t.table_name != 'stocks_daily_backup_migration'
    LOOP
        EXECUTE format('ANALYZE %I', table_name);
        RAISE NOTICE 'テーブル % の統計情報を更新しました', table_name;
    END LOOP;
END $$;

-- =============================================================================
-- マイグレーション完了メッセージ
-- =============================================================================

DO $$
BEGIN
    RAISE NOTICE '=== マイグレーション完了 ===';
    RAISE NOTICE '8テーブル構成への移行が完了しました';
    RAISE NOTICE '';
    RAISE NOTICE '次の手順:';
    RAISE NOTICE '1. アプリケーションの動作確認を実施してください';
    RAISE NOTICE '2. 問題がなければ旧テーブルの削除を検討してください';
    RAISE NOTICE '3. 新しいテーブル構成でのデータ投入テストを実施してください';
    RAISE NOTICE '';
    RAISE NOTICE '旧テーブル削除コマンド（動作確認後に実行）:';
    RAISE NOTICE 'DROP TABLE IF EXISTS stocks_daily_backup_migration;';
END $$;

-- =============================================================================
-- 使用方法:
-- 1. データベースのバックアップを取得
--    pg_dump -U stock_user -d stock_data_system > backup_before_migration.sql
--
-- 2. 新しいテーブル構造を作成
--    psql -U stock_user -d stock_data_system -f scripts/create_tables.sql
--
-- 3. このマイグレーションスクリプトを実行
--    psql -U stock_user -d stock_data_system -f scripts/migrate_to_8tables.sql
--
-- 4. アプリケーションの動作確認
--
-- 5. 問題がなければ旧テーブルを削除
--    psql -U stock_user -d stock_data_system -c "DROP TABLE IF EXISTS stocks_daily_backup_migration;"
-- =============================================================================
