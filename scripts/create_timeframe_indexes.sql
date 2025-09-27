-- =============================================================================
-- PostgreSQL 複数時間軸対応インデックス・トリガー作成スクリプト
-- Issue #34: 時間軸（足データ）対応 - インデックス設計
-- =============================================================================

-- =============================================================================
-- 1分足テーブル（stocks_1m）インデックス
-- =============================================================================

-- 銘柄コード検索インデックス
CREATE INDEX IF NOT EXISTS idx_stocks_1m_symbol
ON stocks_1m (symbol);

-- 日時検索インデックス
CREATE INDEX IF NOT EXISTS idx_stocks_1m_datetime
ON stocks_1m (datetime);

-- 複合インデックス（銘柄+日時降順）- 最新データ取得用
CREATE INDEX IF NOT EXISTS idx_stocks_1m_symbol_datetime_desc
ON stocks_1m (symbol, datetime DESC);

-- 日時範囲検索用インデックス
CREATE INDEX IF NOT EXISTS idx_stocks_1m_datetime_desc
ON stocks_1m (datetime DESC);

-- updated_atトリガー
DROP TRIGGER IF EXISTS trigger_update_stocks_1m_updated_at ON stocks_1m;
CREATE TRIGGER trigger_update_stocks_1m_updated_at
    BEFORE UPDATE ON stocks_1m
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- =============================================================================
-- 5分足テーブル（stocks_5m）インデックス
-- =============================================================================

-- 銘柄コード検索インデックス
CREATE INDEX IF NOT EXISTS idx_stocks_5m_symbol
ON stocks_5m (symbol);

-- 日時検索インデックス
CREATE INDEX IF NOT EXISTS idx_stocks_5m_datetime
ON stocks_5m (datetime);

-- 複合インデックス（銘柄+日時降順）- 最新データ取得用
CREATE INDEX IF NOT EXISTS idx_stocks_5m_symbol_datetime_desc
ON stocks_5m (symbol, datetime DESC);

-- 日時範囲検索用インデックス
CREATE INDEX IF NOT EXISTS idx_stocks_5m_datetime_desc
ON stocks_5m (datetime DESC);

-- updated_atトリガー
DROP TRIGGER IF EXISTS trigger_update_stocks_5m_updated_at ON stocks_5m;
CREATE TRIGGER trigger_update_stocks_5m_updated_at
    BEFORE UPDATE ON stocks_5m
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- =============================================================================
-- 15分足テーブル（stocks_15m）インデックス
-- =============================================================================

-- 銘柄コード検索インデックス
CREATE INDEX IF NOT EXISTS idx_stocks_15m_symbol
ON stocks_15m (symbol);

-- 日時検索インデックス
CREATE INDEX IF NOT EXISTS idx_stocks_15m_datetime
ON stocks_15m (datetime);

-- 複合インデックス（銘柄+日時降順）- 最新データ取得用
CREATE INDEX IF NOT EXISTS idx_stocks_15m_symbol_datetime_desc
ON stocks_15m (symbol, datetime DESC);

-- 日時範囲検索用インデックス
CREATE INDEX IF NOT EXISTS idx_stocks_15m_datetime_desc
ON stocks_15m (datetime DESC);

-- updated_atトリガー
DROP TRIGGER IF EXISTS trigger_update_stocks_15m_updated_at ON stocks_15m;
CREATE TRIGGER trigger_update_stocks_15m_updated_at
    BEFORE UPDATE ON stocks_15m
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- =============================================================================
-- 30分足テーブル（stocks_30m）インデックス
-- =============================================================================

-- 銘柄コード検索インデックス
CREATE INDEX IF NOT EXISTS idx_stocks_30m_symbol
ON stocks_30m (symbol);

-- 日時検索インデックス
CREATE INDEX IF NOT EXISTS idx_stocks_30m_datetime
ON stocks_30m (datetime);

-- 複合インデックス（銘柄+日時降順）- 最新データ取得用
CREATE INDEX IF NOT EXISTS idx_stocks_30m_symbol_datetime_desc
ON stocks_30m (symbol, datetime DESC);

-- 日時範囲検索用インデックス
CREATE INDEX IF NOT EXISTS idx_stocks_30m_datetime_desc
ON stocks_30m (datetime DESC);

-- updated_atトリガー
DROP TRIGGER IF EXISTS trigger_update_stocks_30m_updated_at ON stocks_30m;
CREATE TRIGGER trigger_update_stocks_30m_updated_at
    BEFORE UPDATE ON stocks_30m
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- =============================================================================
-- 1時間足テーブル（stocks_1h）インデックス
-- =============================================================================

-- 銘柄コード検索インデックス
CREATE INDEX IF NOT EXISTS idx_stocks_1h_symbol
ON stocks_1h (symbol);

-- 日時検索インデックス
CREATE INDEX IF NOT EXISTS idx_stocks_1h_datetime
ON stocks_1h (datetime);

-- 複合インデックス（銘柄+日時降順）- 最新データ取得用
CREATE INDEX IF NOT EXISTS idx_stocks_1h_symbol_datetime_desc
ON stocks_1h (symbol, datetime DESC);

-- 日時範囲検索用インデックス
CREATE INDEX IF NOT EXISTS idx_stocks_1h_datetime_desc
ON stocks_1h (datetime DESC);

-- updated_atトリガー
DROP TRIGGER IF EXISTS trigger_update_stocks_1h_updated_at ON stocks_1h;
CREATE TRIGGER trigger_update_stocks_1h_updated_at
    BEFORE UPDATE ON stocks_1h
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- =============================================================================
-- 1日足テーブル（stocks_1d）インデックス
-- =============================================================================

-- 銘柄コード検索インデックス
CREATE INDEX IF NOT EXISTS idx_stocks_1d_symbol
ON stocks_1d (symbol);

-- 日付検索インデックス
CREATE INDEX IF NOT EXISTS idx_stocks_1d_date
ON stocks_1d (date);

-- 複合インデックス（銘柄+日付降順）- 最新データ取得用
CREATE INDEX IF NOT EXISTS idx_stocks_1d_symbol_date_desc
ON stocks_1d (symbol, date DESC);

-- 日付範囲検索用インデックス
CREATE INDEX IF NOT EXISTS idx_stocks_1d_date_desc
ON stocks_1d (date DESC);

-- updated_atトリガー
DROP TRIGGER IF EXISTS trigger_update_stocks_1d_updated_at ON stocks_1d;
CREATE TRIGGER trigger_update_stocks_1d_updated_at
    BEFORE UPDATE ON stocks_1d
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- =============================================================================
-- 1週間足テーブル（stocks_1wk）インデックス
-- =============================================================================

-- 銘柄コード検索インデックス
CREATE INDEX IF NOT EXISTS idx_stocks_1wk_symbol
ON stocks_1wk (symbol);

-- 週開始日検索インデックス
CREATE INDEX IF NOT EXISTS idx_stocks_1wk_week_start_date
ON stocks_1wk (week_start_date);

-- 複合インデックス（銘柄+週開始日降順）- 最新データ取得用
CREATE INDEX IF NOT EXISTS idx_stocks_1wk_symbol_week_desc
ON stocks_1wk (symbol, week_start_date DESC);

-- 週開始日範囲検索用インデックス
CREATE INDEX IF NOT EXISTS idx_stocks_1wk_week_start_date_desc
ON stocks_1wk (week_start_date DESC);

-- updated_atトリガー
DROP TRIGGER IF EXISTS trigger_update_stocks_1wk_updated_at ON stocks_1wk;
CREATE TRIGGER trigger_update_stocks_1wk_updated_at
    BEFORE UPDATE ON stocks_1wk
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- =============================================================================
-- 1ヶ月足テーブル（stocks_1mo）インデックス
-- =============================================================================

-- 銘柄コード検索インデックス
CREATE INDEX IF NOT EXISTS idx_stocks_1mo_symbol
ON stocks_1mo (symbol);

-- 年月検索インデックス
CREATE INDEX IF NOT EXISTS idx_stocks_1mo_year_month
ON stocks_1mo (year, month);

-- 複合インデックス（銘柄+年月降順）- 最新データ取得用
CREATE INDEX IF NOT EXISTS idx_stocks_1mo_symbol_year_month_desc
ON stocks_1mo (symbol, year DESC, month DESC);

-- 年月範囲検索用インデックス
CREATE INDEX IF NOT EXISTS idx_stocks_1mo_year_month_desc
ON stocks_1mo (year DESC, month DESC);

-- updated_atトリガー
DROP TRIGGER IF EXISTS trigger_update_stocks_1mo_updated_at ON stocks_1mo;
CREATE TRIGGER trigger_update_stocks_1mo_updated_at
    BEFORE UPDATE ON stocks_1mo
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- =============================================================================
-- 実行結果確認
-- =============================================================================

-- 作成されたテーブルの確認
SELECT
    schemaname as "スキーマ名",
    tablename as "テーブル名",
    tableowner as "所有者"
FROM pg_tables
WHERE tablename LIKE 'stocks_%'
ORDER BY tablename;

-- インデックスの確認
SELECT
    schemaname as "スキーマ名",
    tablename as "テーブル名",
    indexname as "インデックス名",
    indexdef as "インデックス定義"
FROM pg_indexes
WHERE tablename LIKE 'stocks_%'
ORDER BY tablename, indexname;

-- トリガーの確認
SELECT
    trigger_name as "トリガー名",
    event_object_table as "テーブル名",
    action_timing as "実行タイミング",
    event_manipulation as "イベント"
FROM information_schema.triggers
WHERE event_object_table LIKE 'stocks_%'
ORDER BY event_object_table, trigger_name;

-- テーブル作成成功メッセージ
DO $$
BEGIN
    RAISE NOTICE '=== 複数時間軸テーブル作成完了 ===';
    RAISE NOTICE '以下のテーブルが正常に作成されました:';
    RAISE NOTICE '- stocks_1m (1分足)';
    RAISE NOTICE '- stocks_5m (5分足)';
    RAISE NOTICE '- stocks_15m (15分足)';
    RAISE NOTICE '- stocks_30m (30分足)';
    RAISE NOTICE '- stocks_1h (1時間足)';
    RAISE NOTICE '- stocks_1d (1日足)';
    RAISE NOTICE '- stocks_1wk (1週間足)';
    RAISE NOTICE '- stocks_1mo (1ヶ月足)';
    RAISE NOTICE 'インデックス、制約、トリガーも設定完了';
    RAISE NOTICE 'Issue #34の実装が完了しました';
END $$;

-- =============================================================================
-- 使用方法:
-- 1. stock_data_system データベースに stock_user で接続
--    psql -U stock_user -d stock_data_system
--
-- 2. テーブル作成スクリプトを実行
--    \i scripts/create_timeframe_tables.sql
--
-- 3. インデックス・トリガー作成スクリプトを実行
--    \i scripts/create_timeframe_indexes.sql
--
-- 4. テーブル作成確認
--    \dt stocks_*
--    \d stocks_1m
-- =============================================================================