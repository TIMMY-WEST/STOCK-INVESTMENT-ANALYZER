-- =============================================================================
-- PostgreSQL テーブル作成スクリプト
-- 株価データ取得システム用テーブル作成とインデックス設定（8テーブル構成）
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
-- updated_at 自動更新トリガー関数（全テーブル共通）
-- =============================================================================

-- トリガー関数作成
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- =============================================================================
-- 1. stocks_1d テーブル作成（日足データ）
-- =============================================================================

-- 既存のテーブルが存在する場合は削除（開発環境でのリセット用）
-- DROP TABLE IF EXISTS stocks_1d CASCADE;

-- stocks_1d テーブル作成
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
COMMENT ON TABLE stocks_1d IS '日足株価データテーブル';
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

-- インデックス作成
CREATE INDEX IF NOT EXISTS idx_stocks_1d_symbol ON stocks_1d (symbol);
CREATE INDEX IF NOT EXISTS idx_stocks_1d_date ON stocks_1d (date);
CREATE INDEX IF NOT EXISTS idx_stocks_1d_symbol_date_desc ON stocks_1d (symbol, date DESC);
CREATE INDEX IF NOT EXISTS idx_stocks_1d_date_desc ON stocks_1d (date DESC);

-- トリガー作成
DROP TRIGGER IF EXISTS trigger_update_stocks_1d_updated_at ON stocks_1d;
CREATE TRIGGER trigger_update_stocks_1d_updated_at
    BEFORE UPDATE ON stocks_1d
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- =============================================================================
-- 2. stocks_1m テーブル作成（1分足データ）
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
COMMENT ON COLUMN stocks_1m.datetime IS '取引日時（精密な時刻）';

-- インデックス作成
CREATE INDEX IF NOT EXISTS idx_stocks_1m_symbol ON stocks_1m (symbol);
CREATE INDEX IF NOT EXISTS idx_stocks_1m_datetime ON stocks_1m (datetime);
CREATE INDEX IF NOT EXISTS idx_stocks_1m_symbol_datetime_desc ON stocks_1m (symbol, datetime DESC);

-- トリガー作成
DROP TRIGGER IF EXISTS trigger_update_stocks_1m_updated_at ON stocks_1m;
CREATE TRIGGER trigger_update_stocks_1m_updated_at
    BEFORE UPDATE ON stocks_1m
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- =============================================================================
-- 3. stocks_5m テーブル作成（5分足データ）
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

-- インデックス作成
CREATE INDEX IF NOT EXISTS idx_stocks_5m_symbol ON stocks_5m (symbol);
CREATE INDEX IF NOT EXISTS idx_stocks_5m_datetime ON stocks_5m (datetime);
CREATE INDEX IF NOT EXISTS idx_stocks_5m_symbol_datetime_desc ON stocks_5m (symbol, datetime DESC);

-- トリガー作成
DROP TRIGGER IF EXISTS trigger_update_stocks_5m_updated_at ON stocks_5m;
CREATE TRIGGER trigger_update_stocks_5m_updated_at
    BEFORE UPDATE ON stocks_5m
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- =============================================================================
-- 4. stocks_15m テーブル作成（15分足データ）
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

-- インデックス作成
CREATE INDEX IF NOT EXISTS idx_stocks_15m_symbol ON stocks_15m (symbol);
CREATE INDEX IF NOT EXISTS idx_stocks_15m_datetime ON stocks_15m (datetime);
CREATE INDEX IF NOT EXISTS idx_stocks_15m_symbol_datetime_desc ON stocks_15m (symbol, datetime DESC);

-- トリガー作成
DROP TRIGGER IF EXISTS trigger_update_stocks_15m_updated_at ON stocks_15m;
CREATE TRIGGER trigger_update_stocks_15m_updated_at
    BEFORE UPDATE ON stocks_15m
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- =============================================================================
-- 5. stocks_30m テーブル作成（30分足データ）
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

-- インデックス作成
CREATE INDEX IF NOT EXISTS idx_stocks_30m_symbol ON stocks_30m (symbol);
CREATE INDEX IF NOT EXISTS idx_stocks_30m_datetime ON stocks_30m (datetime);
CREATE INDEX IF NOT EXISTS idx_stocks_30m_symbol_datetime_desc ON stocks_30m (symbol, datetime DESC);

-- トリガー作成
DROP TRIGGER IF EXISTS trigger_update_stocks_30m_updated_at ON stocks_30m;
CREATE TRIGGER trigger_update_stocks_30m_updated_at
    BEFORE UPDATE ON stocks_30m
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- =============================================================================
-- 6. stocks_1h テーブル作成（1時間足データ）
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

-- インデックス作成
CREATE INDEX IF NOT EXISTS idx_stocks_1h_symbol ON stocks_1h (symbol);
CREATE INDEX IF NOT EXISTS idx_stocks_1h_datetime ON stocks_1h (datetime);
CREATE INDEX IF NOT EXISTS idx_stocks_1h_symbol_datetime_desc ON stocks_1h (symbol, datetime DESC);

-- トリガー作成
DROP TRIGGER IF EXISTS trigger_update_stocks_1h_updated_at ON stocks_1h;
CREATE TRIGGER trigger_update_stocks_1h_updated_at
    BEFORE UPDATE ON stocks_1h
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- =============================================================================
-- 7. stocks_1wk テーブル作成（1週間足データ）
-- =============================================================================

CREATE TABLE IF NOT EXISTS stocks_1wk (
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
    CONSTRAINT uk_stocks_1wk_symbol_date UNIQUE (symbol, date),
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

-- インデックス作成
CREATE INDEX IF NOT EXISTS idx_stocks_1wk_symbol ON stocks_1wk (symbol);
CREATE INDEX IF NOT EXISTS idx_stocks_1wk_date ON stocks_1wk (date);
CREATE INDEX IF NOT EXISTS idx_stocks_1wk_symbol_date_desc ON stocks_1wk (symbol, date DESC);

-- トリガー作成
DROP TRIGGER IF EXISTS trigger_update_stocks_1wk_updated_at ON stocks_1wk;
CREATE TRIGGER trigger_update_stocks_1wk_updated_at
    BEFORE UPDATE ON stocks_1wk
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- =============================================================================
-- 8. stocks_1mo テーブル作成（1ヶ月足データ）
-- =============================================================================

CREATE TABLE IF NOT EXISTS stocks_1mo (
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
    CONSTRAINT uk_stocks_1mo_symbol_date UNIQUE (symbol, date),
    CONSTRAINT ck_stocks_1mo_prices CHECK (
        open >= 0 AND high >= 0 AND low >= 0 AND close >= 0
    ),
    CONSTRAINT ck_stocks_1mo_volume CHECK (volume >= 0),
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

-- インデックス作成
CREATE INDEX IF NOT EXISTS idx_stocks_1mo_symbol ON stocks_1mo (symbol);
CREATE INDEX IF NOT EXISTS idx_stocks_1mo_date ON stocks_1mo (date);
CREATE INDEX IF NOT EXISTS idx_stocks_1mo_symbol_date_desc ON stocks_1mo (symbol, date DESC);

-- トリガー作成
DROP TRIGGER IF EXISTS trigger_update_stocks_1mo_updated_at ON stocks_1mo;
CREATE TRIGGER trigger_update_stocks_1mo_updated_at
    BEFORE UPDATE ON stocks_1mo
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- =============================================================================
-- 9. stock_master テーブル作成（銘柄マスタ - JPX全項目対応版）
-- =============================================================================

CREATE TABLE IF NOT EXISTS stock_master (
    id SERIAL PRIMARY KEY,

    -- 基本情報
    stock_code VARCHAR(10) UNIQUE NOT NULL,
    stock_name VARCHAR(100) NOT NULL,
    market_category VARCHAR(50),

    -- 業種情報
    sector_code_33 VARCHAR(10),
    sector_name_33 VARCHAR(100),
    sector_code_17 VARCHAR(10),
    sector_name_17 VARCHAR(100),

    -- 規模情報
    scale_code VARCHAR(10),
    scale_category VARCHAR(50),

    -- データ管理
    data_date VARCHAR(8),
    is_active INTEGER DEFAULT 1 NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- テーブルコメント
COMMENT ON TABLE stock_master IS 'JPX銘柄一覧を管理する銘柄マスタテーブル（全項目対応版） (Phase 2)';
COMMENT ON COLUMN stock_master.stock_code IS '銘柄コード（例: 7203）';
COMMENT ON COLUMN stock_master.stock_name IS '銘柄名（例: トヨタ自動車）';
COMMENT ON COLUMN stock_master.market_category IS '市場区分（例: プライム（内国株式））';
COMMENT ON COLUMN stock_master.sector_code_33 IS '33業種コード';
COMMENT ON COLUMN stock_master.sector_name_33 IS '33業種区分';
COMMENT ON COLUMN stock_master.sector_code_17 IS '17業種コード';
COMMENT ON COLUMN stock_master.sector_name_17 IS '17業種区分';
COMMENT ON COLUMN stock_master.scale_code IS '規模コード';
COMMENT ON COLUMN stock_master.scale_category IS '規模区分（TOPIX分類）';
COMMENT ON COLUMN stock_master.data_date IS 'データ取得日（YYYYMMDD形式）';
COMMENT ON COLUMN stock_master.is_active IS '有効フラグ（1=有効, 0=無効）';

-- インデックス作成
CREATE INDEX IF NOT EXISTS idx_stock_master_code ON stock_master(stock_code);
CREATE INDEX IF NOT EXISTS idx_stock_master_active ON stock_master(is_active);
CREATE INDEX IF NOT EXISTS idx_stock_master_market ON stock_master(market_category);
CREATE INDEX IF NOT EXISTS idx_stock_master_sector_33 ON stock_master(sector_code_33);

-- トリガー作成
DROP TRIGGER IF EXISTS trigger_update_stock_master_updated_at ON stock_master;
CREATE TRIGGER trigger_update_stock_master_updated_at
    BEFORE UPDATE ON stock_master
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- =============================================================================
-- 10. stock_master_updates テーブル作成（銘柄マスタ更新履歴）
-- =============================================================================

CREATE TABLE IF NOT EXISTS stock_master_updates (
    id SERIAL PRIMARY KEY,
    update_type VARCHAR(20) NOT NULL,
    total_stocks INTEGER NOT NULL,
    added_stocks INTEGER DEFAULT 0,
    updated_stocks INTEGER DEFAULT 0,
    removed_stocks INTEGER DEFAULT 0,
    status VARCHAR(20) NOT NULL,
    error_message TEXT,
    started_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP WITH TIME ZONE
);

-- テーブルコメント
COMMENT ON TABLE stock_master_updates IS '銘柄マスタ更新履歴テーブル (Phase 2)';
COMMENT ON COLUMN stock_master_updates.update_type IS '更新タイプ（manual, scheduled）';
COMMENT ON COLUMN stock_master_updates.total_stocks IS '更新後の総銘柄数';
COMMENT ON COLUMN stock_master_updates.added_stocks IS '追加された銘柄数';
COMMENT ON COLUMN stock_master_updates.updated_stocks IS '更新された銘柄数';
COMMENT ON COLUMN stock_master_updates.removed_stocks IS '削除された銘柄数';
COMMENT ON COLUMN stock_master_updates.status IS 'ステータス（success, failed）';
COMMENT ON COLUMN stock_master_updates.error_message IS 'エラーメッセージ（失敗時）';

-- =============================================================================
-- 11. batch_executions テーブル作成（バッチ実行情報）
-- =============================================================================

CREATE TABLE IF NOT EXISTS batch_executions (
    id SERIAL PRIMARY KEY,
    batch_type VARCHAR(50) NOT NULL,
    status VARCHAR(20) NOT NULL,
    total_stocks INTEGER NOT NULL,
    processed_stocks INTEGER DEFAULT 0,
    successful_stocks INTEGER DEFAULT 0,
    failed_stocks INTEGER DEFAULT 0,
    start_time TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    end_time TIMESTAMP WITH TIME ZONE,
    error_message TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- テーブルコメント
COMMENT ON TABLE batch_executions IS 'バッチ実行情報テーブル - バッチ処理の実行状況を管理 (Phase 2)';
COMMENT ON COLUMN batch_executions.batch_type IS 'バッチタイプ（all_stocks, partial, etc.）';
COMMENT ON COLUMN batch_executions.status IS 'ステータス（running, completed, failed, paused）';
COMMENT ON COLUMN batch_executions.total_stocks IS '総銘柄数';
COMMENT ON COLUMN batch_executions.processed_stocks IS '処理済み銘柄数';
COMMENT ON COLUMN batch_executions.successful_stocks IS '成功銘柄数';
COMMENT ON COLUMN batch_executions.failed_stocks IS '失敗銘柄数';
COMMENT ON COLUMN batch_executions.start_time IS 'バッチ開始時刻';
COMMENT ON COLUMN batch_executions.end_time IS 'バッチ終了時刻';
COMMENT ON COLUMN batch_executions.error_message IS 'エラーメッセージ';

-- インデックス作成
CREATE INDEX IF NOT EXISTS idx_batch_executions_status ON batch_executions (status);
CREATE INDEX IF NOT EXISTS idx_batch_executions_batch_type ON batch_executions (batch_type);
CREATE INDEX IF NOT EXISTS idx_batch_executions_start_time ON batch_executions (start_time);

-- =============================================================================
-- 12. batch_execution_details テーブル作成（バッチ実行詳細）
-- =============================================================================

CREATE TABLE IF NOT EXISTS batch_execution_details (
    id SERIAL PRIMARY KEY,
    batch_execution_id INTEGER NOT NULL,
    stock_code VARCHAR(10) NOT NULL,
    status VARCHAR(20) NOT NULL,
    start_time TIMESTAMP WITH TIME ZONE,
    end_time TIMESTAMP WITH TIME ZONE,
    error_message TEXT,
    records_inserted INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    -- 外部キー制約
    CONSTRAINT fk_batch_execution_details_batch_id 
        FOREIGN KEY (batch_execution_id) 
        REFERENCES batch_executions(id) 
        ON DELETE CASCADE
);

-- テーブルコメント
COMMENT ON TABLE batch_execution_details IS 'バッチ実行詳細テーブル - 個別銘柄の処理状況を管理 (Phase 2)';
COMMENT ON COLUMN batch_execution_details.batch_execution_id IS 'batch_executionsテーブルへの外部キー';
COMMENT ON COLUMN batch_execution_details.stock_code IS '銘柄コード';
COMMENT ON COLUMN batch_execution_details.status IS 'ステータス（pending, processing, completed, failed）';
COMMENT ON COLUMN batch_execution_details.start_time IS '処理開始時刻';
COMMENT ON COLUMN batch_execution_details.end_time IS '処理終了時刻';
COMMENT ON COLUMN batch_execution_details.error_message IS 'エラーメッセージ';
COMMENT ON COLUMN batch_execution_details.records_inserted IS '挿入されたレコード数';

-- インデックス作成
CREATE INDEX IF NOT EXISTS idx_batch_execution_details_batch_id ON batch_execution_details (batch_execution_id);
CREATE INDEX IF NOT EXISTS idx_batch_execution_details_status ON batch_execution_details (status);
CREATE INDEX IF NOT EXISTS idx_batch_execution_details_stock_code ON batch_execution_details (stock_code);
CREATE INDEX IF NOT EXISTS idx_batch_execution_details_batch_stock ON batch_execution_details (batch_execution_id, stock_code);

-- =============================================================================
-- 実行結果確認
-- =============================================================================

-- 作成されたテーブルの確認
SELECT
    schemaname as "スキーマ名",
    tablename as "テーブル名",
    tableowner as "所有者"
FROM pg_tables
WHERE tablename LIKE 'stocks_%' OR tablename LIKE 'stock_master%' OR tablename LIKE 'batch_%'
ORDER BY tablename;

-- テーブル作成成功メッセージ
DO $$
BEGIN
    RAISE NOTICE '=== 12テーブル構成作成完了 ===';
    RAISE NOTICE '【株価データテーブル（8テーブル）】';
    RAISE NOTICE '  - stocks_1d (日足)';
    RAISE NOTICE '  - stocks_1m (1分足)';
    RAISE NOTICE '  - stocks_5m (5分足)';
    RAISE NOTICE '  - stocks_15m (15分足)';
    RAISE NOTICE '  - stocks_30m (30分足)';
    RAISE NOTICE '  - stocks_1h (1時間足)';
    RAISE NOTICE '  - stocks_1wk (1週間足)';
    RAISE NOTICE '  - stocks_1mo (1ヶ月足)';
    RAISE NOTICE '【銘柄マスタテーブル（2テーブル）】';
    RAISE NOTICE '  - stock_master (JPX銘柄一覧 - 全項目対応版)';
    RAISE NOTICE '  - stock_master_updates (更新履歴)';
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
--    SELECT tablename FROM pg_tables WHERE tablename LIKE 'stocks_%';
-- =============================================================================