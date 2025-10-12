-- ====================================
-- 銘柄マスタテーブル作成スクリプト (Phase 2)
-- ====================================
-- 作成日: 2025-10-12
-- 説明: JPX銘柄一覧を管理する銘柄マスタテーブルと更新履歴テーブルを作成

-- ====================================
-- 1. 銘柄マスタテーブル (stock_master)
-- ====================================
-- JPXデータの全項目を格納可能な拡張版
CREATE TABLE IF NOT EXISTS stock_master (
    id SERIAL PRIMARY KEY,

    -- 基本情報
    stock_code VARCHAR(10) UNIQUE NOT NULL,     -- 銘柄コード（例: "7203"）
    stock_name VARCHAR(100) NOT NULL,            -- 銘柄名（例: "トヨタ自動車"）
    market_category VARCHAR(50),                 -- 市場区分（例: "プライム（内国株式）"）

    -- 業種情報
    sector_code_33 VARCHAR(10),                  -- 33業種コード
    sector_name_33 VARCHAR(100),                 -- 33業種区分
    sector_code_17 VARCHAR(10),                  -- 17業種コード
    sector_name_17 VARCHAR(100),                 -- 17業種区分

    -- 規模情報
    scale_code VARCHAR(10),                      -- 規模コード
    scale_category VARCHAR(50),                  -- 規模区分（TOPIX分類）

    -- データ管理
    data_date VARCHAR(8),                        -- データ取得日（YYYYMMDD形式）
    is_active INTEGER DEFAULT 1 NOT NULL,        -- 有効フラグ（1=有効, 0=無効）
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- インデックス作成
CREATE INDEX IF NOT EXISTS idx_stock_master_code ON stock_master(stock_code);
CREATE INDEX IF NOT EXISTS idx_stock_master_active ON stock_master(is_active);
CREATE INDEX IF NOT EXISTS idx_stock_master_market ON stock_master(market_category);
CREATE INDEX IF NOT EXISTS idx_stock_master_sector_33 ON stock_master(sector_code_33);

-- コメント追加
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

-- ====================================
-- 2. 銘柄一覧更新履歴テーブル (stock_master_updates)
-- ====================================
CREATE TABLE IF NOT EXISTS stock_master_updates (
    id SERIAL PRIMARY KEY,
    update_type VARCHAR(20) NOT NULL,            -- 'manual', 'scheduled'
    total_stocks INTEGER NOT NULL,               -- 総銘柄数
    added_stocks INTEGER DEFAULT 0,              -- 新規追加銘柄数
    updated_stocks INTEGER DEFAULT 0,            -- 更新銘柄数
    removed_stocks INTEGER DEFAULT 0,            -- 削除（無効化）銘柄数
    status VARCHAR(20) NOT NULL,                 -- 'success', 'failed'
    error_message TEXT,
    started_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP WITH TIME ZONE
);

-- コメント追加
COMMENT ON TABLE stock_master_updates IS '銘柄マスタの更新履歴を管理するテーブル (Phase 2)';
COMMENT ON COLUMN stock_master_updates.update_type IS '更新タイプ（manual: 手動, scheduled: スケジュール）';
COMMENT ON COLUMN stock_master_updates.total_stocks IS '更新時の総銘柄数';
COMMENT ON COLUMN stock_master_updates.added_stocks IS '新規追加された銘柄数';
COMMENT ON COLUMN stock_master_updates.updated_stocks IS '更新された銘柄数';
COMMENT ON COLUMN stock_master_updates.removed_stocks IS '削除（無効化）された銘柄数';
COMMENT ON COLUMN stock_master_updates.status IS '更新ステータス（success: 成功, failed: 失敗）';
COMMENT ON COLUMN stock_master_updates.error_message IS 'エラーメッセージ（失敗時のみ）';

-- ====================================
-- 確認クエリ
-- ====================================
-- テーブル作成確認
SELECT
    table_name,
    table_type
FROM
    information_schema.tables
WHERE
    table_schema = 'public'
    AND table_name IN ('stock_master', 'stock_master_updates')
ORDER BY
    table_name;

-- カラム確認
SELECT
    table_name,
    column_name,
    data_type,
    is_nullable,
    column_default
FROM
    information_schema.columns
WHERE
    table_schema = 'public'
    AND table_name IN ('stock_master', 'stock_master_updates')
ORDER BY
    table_name,
    ordinal_position;

-- インデックス確認
SELECT
    tablename,
    indexname,
    indexdef
FROM
    pg_indexes
WHERE
    schemaname = 'public'
    AND tablename IN ('stock_master', 'stock_master_updates')
ORDER BY
    tablename,
    indexname;
