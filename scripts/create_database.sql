-- =============================================================================
-- PostgreSQL データベース作成スクリプト
-- 株価データ取得システム用データベースとユーザーのセットアップ
-- =============================================================================

-- データベース作成
-- 注意: このスクリプトは postgres ユーザーで実行する必要があります
-- 実行例: psql -U postgres -f create_database.sql

-- 既存のデータベースが存在するかチェックし、存在しない場合のみ作成
DO
$do$
BEGIN
   IF NOT EXISTS (
      SELECT FROM pg_database WHERE datname = 'stock_data_system'
   ) THEN
      PERFORM dblink_exec('dbname=' || current_database(), 'CREATE DATABASE stock_data_system');
   END IF;
END
$do$;

-- 上記のコマンドが動作しない場合は、以下のシンプルな方法を使用
-- DROP DATABASE IF EXISTS stock_data_system;
CREATE DATABASE stock_data_system
    WITH
    OWNER = postgres
    ENCODING = 'UTF8'
    LC_COLLATE = 'Japanese_Japan.932'
    LC_CTYPE = 'Japanese_Japan.932'
    TABLESPACE = pg_default
    CONNECTION LIMIT = -1;

-- データベースにコメントを追加
COMMENT ON DATABASE stock_data_system IS '株価データ取得システム用データベース';

-- 開発用ユーザーの作成
-- 既存のユーザーが存在するかチェックし、存在しない場合のみ作成
DO
$do$
BEGIN
   IF NOT EXISTS (
      SELECT FROM pg_catalog.pg_roles
      WHERE  rolname = 'stock_user') THEN

      CREATE ROLE stock_user LOGIN PASSWORD 'stock_password';
   END IF;
END
$do$;

-- ユーザーにデータベースへの権限を付与
GRANT ALL PRIVILEGES ON DATABASE stock_data_system TO stock_user;

-- ユーザーにデータベース作成権限を付与（開発・テスト用）
ALTER USER stock_user CREATEDB;

-- セキュリティ設定（本番環境では適切に調整してください）
-- ALTER USER stock_user SET statement_timeout = '30min';
-- ALTER USER stock_user SET lock_timeout = '10s';

-- 実行確認用クエリ
SELECT
    datname as "データベース名",
    datcollate as "照合順序",
    datctype as "文字分類"
FROM pg_database
WHERE datname = 'stock_data_system';

SELECT
    rolname as "ユーザー名",
    rolcanlogin as "ログイン可能",
    rolcreatedb as "DB作成権限"
FROM pg_roles
WHERE rolname = 'stock_user';

-- =============================================================================
-- 使用方法:
-- 1. PostgreSQLに postgres ユーザーでログイン
--    psql -U postgres
--
-- 2. このスクリプトを実行
--    \i scripts/create_database.sql
--
-- 3. 作成したデータベースに接続確認
--    \c stock_data_system stock_user
--
-- 4. パスワード入力: stock_password
-- =============================================================================