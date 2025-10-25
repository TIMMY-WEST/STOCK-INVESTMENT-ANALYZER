@echo off
REM =============================================================================
REM PostgreSQL Database Reset Script for Windows
REM Stock Data System Database Clean Reset Script
REM =============================================================================

chcp 65001 >nul 2>&1
setlocal enabledelayedexpansion

REM PostgreSQLクライアントエンコーディングをUTF8に設定
set PGCLIENTENCODING=UTF8

cls
echo =========================================
echo   Database Reset Script
echo =========================================
echo.
echo This script will perform the following operations:
echo   1. Create database backup (optional)
echo   2. Drop existing database
echo   3. Recreate database
echo   4. Create tables
echo   5. Insert sample data
echo.
echo WARNING: This will delete ALL existing data!
echo.

REM .envファイルから設定を読み込み
echo Loading configuration from .env file...
if not exist "%~dp0..\.env" (
    echo ERROR: .env file not found
    echo Please create .env file in project root
    pause
    exit /b 1
)

REM .envファイルを読み込み
for /f "tokens=1,2 delims==" %%i in ('findstr /v "^#" "%~dp0..\.env"') do (
    if "%%i"=="DB_NAME" set DB_NAME=%%j
    if "%%i"=="DB_USER" set DB_USER=%%j
    if "%%i"=="DB_PASSWORD" set DB_PASSWORD=%%j
    if "%%i"=="POSTGRES_PASSWORD" set POSTGRES_PASSWORD=%%j
)

REM デフォルト値設定
if not defined POSTGRES_PASSWORD set POSTGRES_PASSWORD=postgres
set POSTGRES_USER=postgres

REM バックアップディレクトリ設定
set BACKUP_DIR=%~dp0..\database\backups
set TIMESTAMP=%date:~0,4%%date:~5,2%%date:~8,2%_%time:~0,2%%time:~3,2%%time:~6,2%
set TIMESTAMP=%TIMESTAMP: =0%

echo.
echo Configuration:
echo   Database Name: %DB_NAME%
echo   User Name: %DB_USER%
echo.

REM 最終確認
set /p CONFIRM="Are you sure you want to reset the database? [y/N]: "
if /i not "%CONFIRM%"=="y" if /i not "%CONFIRM%"=="yes" (
    echo Operation cancelled by user
    pause
    exit /b 0
)

REM PostgreSQLインストール確認
echo.
echo [1/6] Checking PostgreSQL installation...
psql --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: PostgreSQL is not installed
    echo Please install PostgreSQL and try again
    echo Installation guide: https://www.postgresql.org/download/windows/
    pause
    exit /b 1
)
echo PostgreSQL found

REM PostgreSQLサービス状態確認
echo.
echo [2/6] Checking PostgreSQL service status...
net start | findstr -i "postgresql" >nul
if errorlevel 1 (
    echo PostgreSQL service is not running
    echo Starting service...
    net start postgresql-x64-16 >nul 2>&1
    if errorlevel 1 (
        net start postgresql >nul 2>&1
        if errorlevel 1 (
            echo WARNING: Failed to start PostgreSQL service automatically
            echo Please start the service manually using services.msc
            pause
            exit /b 1
        )
    )
)
echo PostgreSQL service is running

REM バックアップ作成（オプション）
echo.
echo [OPTION] Create database backup
set /p BACKUP_CONFIRM="Do you want to create a backup? [y/N]: "
if /i "%BACKUP_CONFIRM%"=="y" (
    echo Creating backup directory...
    if not exist "%BACKUP_DIR%" mkdir "%BACKUP_DIR%"

    set BACKUP_FILE=%BACKUP_DIR%\%DB_NAME%_backup_%TIMESTAMP%.sql

    echo Creating backup: !BACKUP_FILE!
    set PGPASSWORD=%DB_PASSWORD%
    pg_dump -U %DB_USER% -h localhost %DB_NAME% > "!BACKUP_FILE!" 2>nul
    if errorlevel 1 (
        echo WARNING: Failed to create backup (database might not exist)
        set /p CONTINUE="Continue without backup? [y/N]: "
        if /i not "!CONTINUE!"=="y" (
            echo Operation cancelled by user
            pause
            exit /b 0
        )
    ) else (
        echo Backup created successfully: !BACKUP_FILE!

        REM 30日以上前の古いバックアップを削除
        forfiles /P "%BACKUP_DIR%" /M "%DB_NAME%_backup_*.sql" /D -30 /C "cmd /c del @path" 2>nul
    )
) else (
    echo Backup skipped
)

REM データベース削除と再作成
echo.
echo [3/6] Dropping and recreating database...
echo Dropping existing database...

REM postgresユーザーのパスワードを環境変数に設定
set PGPASSWORD=%POSTGRES_PASSWORD%

REM アクティブな接続を強制終了
psql -U %POSTGRES_USER% -h localhost -c "SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname = '%DB_NAME%' AND pid <> pg_backend_pid();" >nul 2>&1

REM データベース削除
psql -U %POSTGRES_USER% -h localhost -c "DROP DATABASE IF EXISTS %DB_NAME%;" >nul 2>&1
if errorlevel 1 (
    echo ERROR: Failed to drop database
    echo Please ensure no other applications are connected to the database
    pause
    exit /b 1
)
echo Existing database dropped

REM データベース作成
echo Creating new database...

REM ユーザーが存在しない場合は作成
psql -U %POSTGRES_USER% -h localhost -t -c "SELECT 1 FROM pg_catalog.pg_roles WHERE rolname='%DB_USER%';" | findstr "1" >nul
if errorlevel 1 (
    echo Creating user %DB_USER%...
    psql -U %POSTGRES_USER% -h localhost -c "CREATE ROLE %DB_USER% LOGIN PASSWORD '%DB_PASSWORD%';" >nul
    if errorlevel 1 (
        echo ERROR: Failed to create user
        pause
        exit /b 1
    )
)

REM データベース作成
psql -U %POSTGRES_USER% -h localhost -c "CREATE DATABASE %DB_NAME% WITH OWNER = %DB_USER% ENCODING = 'UTF8' LC_COLLATE = 'C' LC_CTYPE = 'C' TABLESPACE = pg_default TEMPLATE = template0 CONNECTION LIMIT = -1;" >nul
if errorlevel 1 (
    echo ERROR: Failed to create database
    pause
    exit /b 1
)

REM コメント追加
psql -U %POSTGRES_USER% -h localhost -c "COMMENT ON DATABASE %DB_NAME% IS 'Stock Data System Database';" >nul

REM 権限付与
psql -U %POSTGRES_USER% -h localhost -c "GRANT ALL PRIVILEGES ON DATABASE %DB_NAME% TO %DB_USER%;" >nul
psql -U %POSTGRES_USER% -h localhost -c "ALTER USER %DB_USER% CREATEDB;" >nul

REM スキーマ権限付与（PostgreSQL 15+で必要）
psql -U %POSTGRES_USER% -h localhost -d %DB_NAME% -c "GRANT ALL ON SCHEMA public TO %DB_USER%;" >nul
psql -U %POSTGRES_USER% -h localhost -d %DB_NAME% -c "GRANT CREATE ON SCHEMA public TO %DB_USER%;" >nul
psql -U %POSTGRES_USER% -h localhost -d %DB_NAME% -c "ALTER SCHEMA public OWNER TO %DB_USER%;" >nul

REM 将来のオブジェクトへのデフォルト権限付与
psql -U %POSTGRES_USER% -h localhost -d %DB_NAME% -c "ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO %DB_USER%;" >nul
psql -U %POSTGRES_USER% -h localhost -d %DB_NAME% -c "ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO %DB_USER%;" >nul

echo Database created successfully

REM テーブル作成
echo.
echo [4/6] Creating tables...
echo Creating tables...

REM stock_userのパスワードを環境変数に設定
set PGPASSWORD=%DB_PASSWORD%

REM クライアントエンコーディングをUTF8に設定してSQLファイルを正しく処理
set PGCLIENTENCODING=UTF8

if exist "%~dp0..\database\schema\create_tables.sql" (
    psql -U %DB_USER% -d %DB_NAME% -h localhost -f "%~dp0..\database\schema\create_tables.sql" >nul
    if errorlevel 1 (
        echo ERROR: Failed to create tables
        pause
        exit /b 1
    )
    echo Tables created successfully
) else (
    echo ERROR: Table creation script not found: %~dp0..\database\schema\create_tables.sql
    pause
    exit /b 1
)

REM サンプルデータ投入
echo.
echo [5/6] Inserting sample data...
echo Inserting sample data...

if exist "%~dp0..\database\seed\insert_sample_data.sql" (
    REM stock_userのパスワードを環境変数に設定
    set PGPASSWORD=%DB_PASSWORD%

    REM クライアントエンコーディングをUTF8に設定
    set PGCLIENTENCODING=UTF8

    psql -U %DB_USER% -d %DB_NAME% -h localhost -f "%~dp0..\database\seed\insert_sample_data.sql" >nul 2>&1
    if errorlevel 1 (
        echo WARNING: Failed to insert some sample data (skipped)
    ) else (
        echo Sample data inserted successfully
    )
) else (
    echo Sample data file not found (skipped)
)

REM 接続テスト
echo.
echo [6/6] Testing database connection...
echo Running connection test...

REM stock_userのパスワードを環境変数に設定
set PGPASSWORD=%DB_PASSWORD%

REM クライアントエンコーディングをUTF8に設定
set PGCLIENTENCODING=UTF8

psql -U %DB_USER% -d %DB_NAME% -h localhost -c "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'public' AND table_name LIKE 'stocks_%%';" >nul
if errorlevel 1 (
    echo ERROR: Database connection test failed
    pause
    exit /b 1
)

echo Connection test passed

REM 完了メッセージ
echo.
echo =========================================
echo   Database Reset Completed!
echo =========================================
echo.
echo Database Information:
echo   Database Name: %DB_NAME%
echo   User: %DB_USER%
echo   Host: localhost
echo   Port: 5432
echo.
echo Connection Command:
echo   psql -U %DB_USER% -d %DB_NAME% -h localhost
echo.
echo Created Tables:
psql -U %DB_USER% -d %DB_NAME% -h localhost -c "\dt"
echo.
echo Reset process completed successfully!
echo.

pause
