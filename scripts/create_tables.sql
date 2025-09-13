-- =============================================================================
-- PostgreSQL テーブル作成スクリプト
-- 株価データ取得システム用テーブル作成とインデックス設定
-- =============================================================================

-- データベースに接続していることを確認
-- 実行例: psql -U stock_user -d stock_data_system -f create_tables.sql

-- セッション設定
SET client_encoding = 'UTF8';
SET timezone = 'Asia/Tokyo';

-- 現在の接続情報を確認
SELECT
    current_database() as "接続中のデータベース",
    current_user as "現在のユーザー",
    version() as "PostgreSQLバージョン";

-- =============================================================================
-- stocks_daily テーブル作成（日足データ）
-- =============================================================================

-- 既存のテーブルが存在する場合は削除（開発環境でのリセット用）
-- DROP TABLE IF EXISTS stocks_daily CASCADE;

-- stocks_daily テーブル作成
CREATE TABLE IF NOT EXISTS stocks_daily (
    id SERIAL PRIMARY KEY,
    symbol VARCHAR(20) NOT NULL,
    date DATE NOT NULL,
    open DECIMAL(10,2) NOT NULL,
    high DECIMAL(10,2) NOT NULL,
    low DECIMAL(10,2) NOT NULL,
    close DECIMAL(10,2) NOT NULL,
    volume BIGINT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,

    -- 制約定義
    CONSTRAINT uk_stocks_daily_symbol_date UNIQUE (symbol, date),
    CONSTRAINT ck_stocks_daily_prices CHECK (
        open >= 0 AND high >= 0 AND low >= 0 AND close >= 0
    ),
    CONSTRAINT ck_stocks_daily_volume CHECK (volume >= 0),
    CONSTRAINT ck_stocks_daily_price_logic CHECK (
        high >= low AND
        high >= open AND
        high >= close AND
        low <= open AND
        low <= close
    )
);

-- テーブルコメント
COMMENT ON TABLE stocks_daily IS '日足株価データテーブル';
COMMENT ON COLUMN stocks_daily.id IS 'レコードID（自動採番）';
COMMENT ON COLUMN stocks_daily.symbol IS '銘柄コード（例：7203.T）';
COMMENT ON COLUMN stocks_daily.date IS '取引日';
COMMENT ON COLUMN stocks_daily.open IS '始値';
COMMENT ON COLUMN stocks_daily.high IS '高値';
COMMENT ON COLUMN stocks_daily.low IS '安値';
COMMENT ON COLUMN stocks_daily.close IS '終値';
COMMENT ON COLUMN stocks_daily.volume IS '出来高';
COMMENT ON COLUMN stocks_daily.created_at IS 'レコード作成日時';
COMMENT ON COLUMN stocks_daily.updated_at IS 'レコード更新日時';

-- =============================================================================
-- インデックス作成
-- =============================================================================

-- 銘柄コード検索インデックス
CREATE INDEX IF NOT EXISTS idx_stocks_daily_symbol
ON stocks_daily (symbol);

-- 日付検索インデックス
CREATE INDEX IF NOT EXISTS idx_stocks_daily_date
ON stocks_daily (date);

-- 複合インデックス（銘柄+日付降順）- 最新データ取得用
CREATE INDEX IF NOT EXISTS idx_stocks_daily_symbol_date_desc
ON stocks_daily (symbol, date DESC);

-- 日付範囲検索用インデックス
CREATE INDEX IF NOT EXISTS idx_stocks_daily_date_desc
ON stocks_daily (date DESC);

-- =============================================================================
-- updated_at 自動更新トリガー関数
-- =============================================================================

-- トリガー関数作成
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- トリガー作成
DROP TRIGGER IF EXISTS trigger_update_stocks_daily_updated_at ON stocks_daily;
CREATE TRIGGER trigger_update_stocks_daily_updated_at
    BEFORE UPDATE ON stocks_daily
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
WHERE tablename = 'stocks_daily';

-- カラム情報の確認
SELECT
    column_name as "カラム名",
    data_type as "データ型",
    is_nullable as "NULL許可",
    column_default as "デフォルト値"
FROM information_schema.columns
WHERE table_name = 'stocks_daily'
ORDER BY ordinal_position;

-- 制約の確認
SELECT
    constraint_name as "制約名",
    constraint_type as "制約タイプ"
FROM information_schema.table_constraints
WHERE table_name = 'stocks_daily'
ORDER BY constraint_name;

-- インデックスの確認
SELECT
    indexname as "インデックス名",
    indexdef as "インデックス定義"
FROM pg_indexes
WHERE tablename = 'stocks_daily'
ORDER BY indexname;

-- テーブル作成成功メッセージ
DO $$
BEGIN
    RAISE NOTICE '=== テーブル作成完了 ===';
    RAISE NOTICE 'stocks_daily テーブルが正常に作成されました';
    RAISE NOTICE 'インデックス、制約、トリガーも設定完了';
    RAISE NOTICE '次は初期データの投入を行ってください';
END $$;

-- =============================================================================
-- 使用方法:
-- 1. stock_data_system データベースに stock_user で接続
--    psql -U stock_user -d stock_data_system
--
-- 2. このスクリプトを実行
--    \i scripts/create_tables.sql
--
-- 3. テーブル作成確認
--    \dt
--    \d stocks_daily
-- =============================================================================