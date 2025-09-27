-- =============================================================================
-- PostgreSQL 複数時間軸対応テーブル作成スクリプト
-- Issue #34: 時間軸（足データ）対応 - データベース設計
-- =============================================================================

-- データベースに接続していることを確認
-- 実行例: psql -U stock_user -d stock_data_system -f create_timeframe_tables.sql

-- セッション設定
SET client_encoding = 'UTF8';
SET timezone = 'Asia/Tokyo';

-- 現在の接続情報を確認
SELECT
    current_database() as "接続中のデータベース",
    current_user as "現在のユーザー",
    version() as "PostgreSQLバージョン";

-- =============================================================================
-- 既存テーブルのリネーム（stocks_daily → stocks_1d）
-- =============================================================================

-- 既存のstocks_dailyテーブルをstocks_1dにリネーム
DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'stocks_daily') THEN
        ALTER TABLE stocks_daily RENAME TO stocks_1d;
        RAISE NOTICE 'stocks_dailyテーブルをstocks_1dにリネームしました';
    ELSE
        RAISE NOTICE 'stocks_dailyテーブルが存在しないため、リネームをスキップしました';
    END IF;
END $$;

-- =============================================================================
-- 共通テーブル構造定義関数
-- =============================================================================

-- updated_at 自動更新トリガー関数（既存の場合は再作成）
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- =============================================================================
-- 1分足テーブル（stocks_1m）
-- =============================================================================

CREATE TABLE IF NOT EXISTS stocks_1m (
    id SERIAL PRIMARY KEY,
    symbol VARCHAR(20) NOT NULL,
    datetime TIMESTAMP WITH TIME ZONE NOT NULL,
    open DECIMAL(10,2) NOT NULL,
    high DECIMAL(10,2) NOT NULL,
    low DECIMAL(10,2) NOT NULL,
    close DECIMAL(10,2) NOT NULL,
    volume BIGINT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,

    -- 制約定義
    CONSTRAINT uk_stocks_1m_symbol_datetime UNIQUE (symbol, datetime),
    CONSTRAINT ck_stocks_1m_prices CHECK (
        open >= 0 AND high >= 0 AND low >= 0 AND close >= 0
    ),
    CONSTRAINT ck_stocks_1m_volume CHECK (volume >= 0),
    CONSTRAINT ck_stocks_1m_price_logic CHECK (
        high >= low AND
        high >= open AND
        high >= close AND
        low <= open AND
        low <= close
    )
);

-- テーブルコメント
COMMENT ON TABLE stocks_1m IS '1分足株価データテーブル';
COMMENT ON COLUMN stocks_1m.id IS 'レコードID（自動採番）';
COMMENT ON COLUMN stocks_1m.symbol IS '銘柄コード（例：7203.T）';
COMMENT ON COLUMN stocks_1m.datetime IS '取引日時（1分単位）';
COMMENT ON COLUMN stocks_1m.open IS '始値';
COMMENT ON COLUMN stocks_1m.high IS '高値';
COMMENT ON COLUMN stocks_1m.low IS '安値';
COMMENT ON COLUMN stocks_1m.close IS '終値';
COMMENT ON COLUMN stocks_1m.volume IS '出来高';
COMMENT ON COLUMN stocks_1m.created_at IS 'レコード作成日時';
COMMENT ON COLUMN stocks_1m.updated_at IS 'レコード更新日時';

-- =============================================================================
-- 5分足テーブル（stocks_5m）
-- =============================================================================

CREATE TABLE IF NOT EXISTS stocks_5m (
    id SERIAL PRIMARY KEY,
    symbol VARCHAR(20) NOT NULL,
    datetime TIMESTAMP WITH TIME ZONE NOT NULL,
    open DECIMAL(10,2) NOT NULL,
    high DECIMAL(10,2) NOT NULL,
    low DECIMAL(10,2) NOT NULL,
    close DECIMAL(10,2) NOT NULL,
    volume BIGINT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,

    -- 制約定義
    CONSTRAINT uk_stocks_5m_symbol_datetime UNIQUE (symbol, datetime),
    CONSTRAINT ck_stocks_5m_prices CHECK (
        open >= 0 AND high >= 0 AND low >= 0 AND close >= 0
    ),
    CONSTRAINT ck_stocks_5m_volume CHECK (volume >= 0),
    CONSTRAINT ck_stocks_5m_price_logic CHECK (
        high >= low AND
        high >= open AND
        high >= close AND
        low <= open AND
        low <= close
    )
);

-- テーブルコメント
COMMENT ON TABLE stocks_5m IS '5分足株価データテーブル';
COMMENT ON COLUMN stocks_5m.id IS 'レコードID（自動採番）';
COMMENT ON COLUMN stocks_5m.symbol IS '銘柄コード（例：7203.T）';
COMMENT ON COLUMN stocks_5m.datetime IS '取引日時（5分単位）';
COMMENT ON COLUMN stocks_5m.open IS '始値';
COMMENT ON COLUMN stocks_5m.high IS '高値';
COMMENT ON COLUMN stocks_5m.low IS '安値';
COMMENT ON COLUMN stocks_5m.close IS '終値';
COMMENT ON COLUMN stocks_5m.volume IS '出来高';
COMMENT ON COLUMN stocks_5m.created_at IS 'レコード作成日時';
COMMENT ON COLUMN stocks_5m.updated_at IS 'レコード更新日時';

-- =============================================================================
-- 15分足テーブル（stocks_15m）
-- =============================================================================

CREATE TABLE IF NOT EXISTS stocks_15m (
    id SERIAL PRIMARY KEY,
    symbol VARCHAR(20) NOT NULL,
    datetime TIMESTAMP WITH TIME ZONE NOT NULL,
    open DECIMAL(10,2) NOT NULL,
    high DECIMAL(10,2) NOT NULL,
    low DECIMAL(10,2) NOT NULL,
    close DECIMAL(10,2) NOT NULL,
    volume BIGINT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,

    -- 制約定義
    CONSTRAINT uk_stocks_15m_symbol_datetime UNIQUE (symbol, datetime),
    CONSTRAINT ck_stocks_15m_prices CHECK (
        open >= 0 AND high >= 0 AND low >= 0 AND close >= 0
    ),
    CONSTRAINT ck_stocks_15m_volume CHECK (volume >= 0),
    CONSTRAINT ck_stocks_15m_price_logic CHECK (
        high >= low AND
        high >= open AND
        high >= close AND
        low <= open AND
        low <= close
    )
);

-- テーブルコメント
COMMENT ON TABLE stocks_15m IS '15分足株価データテーブル';
COMMENT ON COLUMN stocks_15m.id IS 'レコードID（自動採番）';
COMMENT ON COLUMN stocks_15m.symbol IS '銘柄コード（例：7203.T）';
COMMENT ON COLUMN stocks_15m.datetime IS '取引日時（15分単位）';
COMMENT ON COLUMN stocks_15m.open IS '始値';
COMMENT ON COLUMN stocks_15m.high IS '高値';
COMMENT ON COLUMN stocks_15m.low IS '安値';
COMMENT ON COLUMN stocks_15m.close IS '終値';
COMMENT ON COLUMN stocks_15m.volume IS '出来高';
COMMENT ON COLUMN stocks_15m.created_at IS 'レコード作成日時';
COMMENT ON COLUMN stocks_15m.updated_at IS 'レコード更新日時';

-- =============================================================================
-- 30分足テーブル（stocks_30m）
-- =============================================================================

CREATE TABLE IF NOT EXISTS stocks_30m (
    id SERIAL PRIMARY KEY,
    symbol VARCHAR(20) NOT NULL,
    datetime TIMESTAMP WITH TIME ZONE NOT NULL,
    open DECIMAL(10,2) NOT NULL,
    high DECIMAL(10,2) NOT NULL,
    low DECIMAL(10,2) NOT NULL,
    close DECIMAL(10,2) NOT NULL,
    volume BIGINT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,

    -- 制約定義
    CONSTRAINT uk_stocks_30m_symbol_datetime UNIQUE (symbol, datetime),
    CONSTRAINT ck_stocks_30m_prices CHECK (
        open >= 0 AND high >= 0 AND low >= 0 AND close >= 0
    ),
    CONSTRAINT ck_stocks_30m_volume CHECK (volume >= 0),
    CONSTRAINT ck_stocks_30m_price_logic CHECK (
        high >= low AND
        high >= open AND
        high >= close AND
        low <= open AND
        low <= close
    )
);

-- テーブルコメント
COMMENT ON TABLE stocks_30m IS '30分足株価データテーブル';
COMMENT ON COLUMN stocks_30m.id IS 'レコードID（自動採番）';
COMMENT ON COLUMN stocks_30m.symbol IS '銘柄コード（例：7203.T）';
COMMENT ON COLUMN stocks_30m.datetime IS '取引日時（30分単位）';
COMMENT ON COLUMN stocks_30m.open IS '始値';
COMMENT ON COLUMN stocks_30m.high IS '高値';
COMMENT ON COLUMN stocks_30m.low IS '安値';
COMMENT ON COLUMN stocks_30m.close IS '終値';
COMMENT ON COLUMN stocks_30m.volume IS '出来高';
COMMENT ON COLUMN stocks_30m.created_at IS 'レコード作成日時';
COMMENT ON COLUMN stocks_30m.updated_at IS 'レコード更新日時';

-- =============================================================================
-- 1時間足テーブル（stocks_1h）
-- =============================================================================

CREATE TABLE IF NOT EXISTS stocks_1h (
    id SERIAL PRIMARY KEY,
    symbol VARCHAR(20) NOT NULL,
    datetime TIMESTAMP WITH TIME ZONE NOT NULL,
    open DECIMAL(10,2) NOT NULL,
    high DECIMAL(10,2) NOT NULL,
    low DECIMAL(10,2) NOT NULL,
    close DECIMAL(10,2) NOT NULL,
    volume BIGINT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,

    -- 制約定義
    CONSTRAINT uk_stocks_1h_symbol_datetime UNIQUE (symbol, datetime),
    CONSTRAINT ck_stocks_1h_prices CHECK (
        open >= 0 AND high >= 0 AND low >= 0 AND close >= 0
    ),
    CONSTRAINT ck_stocks_1h_volume CHECK (volume >= 0),
    CONSTRAINT ck_stocks_1h_price_logic CHECK (
        high >= low AND
        high >= open AND
        high >= close AND
        low <= open AND
        low <= close
    )
);

-- テーブルコメント
COMMENT ON TABLE stocks_1h IS '1時間足株価データテーブル';
COMMENT ON COLUMN stocks_1h.id IS 'レコードID（自動採番）';
COMMENT ON COLUMN stocks_1h.symbol IS '銘柄コード（例：7203.T）';
COMMENT ON COLUMN stocks_1h.datetime IS '取引日時（1時間単位）';
COMMENT ON COLUMN stocks_1h.open IS '始値';
COMMENT ON COLUMN stocks_1h.high IS '高値';
COMMENT ON COLUMN stocks_1h.low IS '安値';
COMMENT ON COLUMN stocks_1h.close IS '終値';
COMMENT ON COLUMN stocks_1h.volume IS '出来高';
COMMENT ON COLUMN stocks_1h.created_at IS 'レコード作成日時';
COMMENT ON COLUMN stocks_1h.updated_at IS 'レコード更新日時';

-- =============================================================================
-- 1日足テーブル（stocks_1d）- 既存テーブルの構造確認・調整
-- =============================================================================

-- stocks_1dテーブルが存在しない場合は作成
CREATE TABLE IF NOT EXISTS stocks_1d (
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
    CONSTRAINT uk_stocks_1d_symbol_date UNIQUE (symbol, date),
    CONSTRAINT ck_stocks_1d_prices CHECK (
        open >= 0 AND high >= 0 AND low >= 0 AND close >= 0
    ),
    CONSTRAINT ck_stocks_1d_volume CHECK (volume >= 0),
    CONSTRAINT ck_stocks_1d_price_logic CHECK (
        high >= low AND
        high >= open AND
        high >= close AND
        low <= open AND
        low <= close
    )
);

-- テーブルコメント
COMMENT ON TABLE stocks_1d IS '1日足株価データテーブル';
COMMENT ON COLUMN stocks_1d.id IS 'レコードID（自動採番）';
COMMENT ON COLUMN stocks_1d.symbol IS '銘柄コード（例：7203.T）';
COMMENT ON COLUMN stocks_1d.date IS '取引日';
COMMENT ON COLUMN stocks_1d.open IS '始値';
COMMENT ON COLUMN stocks_1d.high IS '高値';
COMMENT ON COLUMN stocks_1d.low IS '安値';
COMMENT ON COLUMN stocks_1d.close IS '終値';
COMMENT ON COLUMN stocks_1d.volume IS '出来高';
COMMENT ON COLUMN stocks_1d.created_at IS 'レコード作成日時';
COMMENT ON COLUMN stocks_1d.updated_at IS 'レコード更新日時';

-- =============================================================================
-- 1週間足テーブル（stocks_1wk）
-- =============================================================================

CREATE TABLE IF NOT EXISTS stocks_1wk (
    id SERIAL PRIMARY KEY,
    symbol VARCHAR(20) NOT NULL,
    week_start_date DATE NOT NULL,
    open DECIMAL(10,2) NOT NULL,
    high DECIMAL(10,2) NOT NULL,
    low DECIMAL(10,2) NOT NULL,
    close DECIMAL(10,2) NOT NULL,
    volume BIGINT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,

    -- 制約定義
    CONSTRAINT uk_stocks_1wk_symbol_week UNIQUE (symbol, week_start_date),
    CONSTRAINT ck_stocks_1wk_prices CHECK (
        open >= 0 AND high >= 0 AND low >= 0 AND close >= 0
    ),
    CONSTRAINT ck_stocks_1wk_volume CHECK (volume >= 0),
    CONSTRAINT ck_stocks_1wk_price_logic CHECK (
        high >= low AND
        high >= open AND
        high >= close AND
        low <= open AND
        low <= close
    )
);

-- テーブルコメント
COMMENT ON TABLE stocks_1wk IS '1週間足株価データテーブル';
COMMENT ON COLUMN stocks_1wk.id IS 'レコードID（自動採番）';
COMMENT ON COLUMN stocks_1wk.symbol IS '銘柄コード（例：7203.T）';
COMMENT ON COLUMN stocks_1wk.week_start_date IS '週の開始日（月曜日）';
COMMENT ON COLUMN stocks_1wk.open IS '始値';
COMMENT ON COLUMN stocks_1wk.high IS '高値';
COMMENT ON COLUMN stocks_1wk.low IS '安値';
COMMENT ON COLUMN stocks_1wk.close IS '終値';
COMMENT ON COLUMN stocks_1wk.volume IS '出来高';
COMMENT ON COLUMN stocks_1wk.created_at IS 'レコード作成日時';
COMMENT ON COLUMN stocks_1wk.updated_at IS 'レコード更新日時';

-- =============================================================================
-- 1ヶ月足テーブル（stocks_1mo）
-- =============================================================================

CREATE TABLE IF NOT EXISTS stocks_1mo (
    id SERIAL PRIMARY KEY,
    symbol VARCHAR(20) NOT NULL,
    year INTEGER NOT NULL,
    month INTEGER NOT NULL,
    open DECIMAL(10,2) NOT NULL,
    high DECIMAL(10,2) NOT NULL,
    low DECIMAL(10,2) NOT NULL,
    close DECIMAL(10,2) NOT NULL,
    volume BIGINT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,

    -- 制約定義
    CONSTRAINT uk_stocks_1mo_symbol_year_month UNIQUE (symbol, year, month),
    CONSTRAINT ck_stocks_1mo_prices CHECK (
        open >= 0 AND high >= 0 AND low >= 0 AND close >= 0
    ),
    CONSTRAINT ck_stocks_1mo_volume CHECK (volume >= 0),
    CONSTRAINT ck_stocks_1mo_year CHECK (year >= 1900 AND year <= 2100),
    CONSTRAINT ck_stocks_1mo_month CHECK (month >= 1 AND month <= 12),
    CONSTRAINT ck_stocks_1mo_price_logic CHECK (
        high >= low AND
        high >= open AND
        high >= close AND
        low <= open AND
        low <= close
    )
);

-- テーブルコメント
COMMENT ON TABLE stocks_1mo IS '1ヶ月足株価データテーブル';
COMMENT ON COLUMN stocks_1mo.id IS 'レコードID（自動採番）';
COMMENT ON COLUMN stocks_1mo.symbol IS '銘柄コード（例：7203.T）';
COMMENT ON COLUMN stocks_1mo.year IS '年';
COMMENT ON COLUMN stocks_1mo.month IS '月';
COMMENT ON COLUMN stocks_1mo.open IS '始値';
COMMENT ON COLUMN stocks_1mo.high IS '高値';
COMMENT ON COLUMN stocks_1mo.low IS '安値';
COMMENT ON COLUMN stocks_1mo.close IS '終値';
COMMENT ON COLUMN stocks_1mo.volume IS '出来高';
COMMENT ON COLUMN stocks_1mo.created_at IS 'レコード作成日時';
COMMENT ON COLUMN stocks_1mo.updated_at IS 'レコード更新日時';