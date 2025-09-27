@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

echo ========================================
echo データベース初期化スクリプト テスト実行
echo ========================================
echo.

REM 現在のディレクトリを取得
set SCRIPT_DIR=%~dp0

REM .envファイルから設定を読み込み
if exist "%SCRIPT_DIR%.env" (
    echo .envファイルから設定を読み込み中...
    for /f "usebackq tokens=1,2 delims==" %%a in ("%SCRIPT_DIR%.env") do (
        set %%a=%%b
    )
) else (
    echo .envファイルが見つかりません。デフォルト設定を使用します。
    set DB_HOST=localhost
    set DB_PORT=5432
    set DB_NAME=stock_data_system
    set DB_USER=stock_user
    set DB_PASSWORD=stock_password
    set POSTGRES_USER=postgres
    set POSTGRES_PASSWORD=postgres
)

echo.
echo [1/4] テスト用データベース作成中...

REM テスト用データベース作成
set PGPASSWORD=%POSTGRES_PASSWORD%
psql -U %POSTGRES_USER% -h localhost -c "DROP DATABASE IF EXISTS stock_data_system_test;" >nul 2>&1
psql -U %POSTGRES_USER% -h localhost -c "CREATE DATABASE stock_data_system_test OWNER %DB_USER%;" >nul 2>&1
if errorlevel 1 (
    echo エラー: テスト用データベースの作成に失敗しました
    pause
    exit /b 1
)
echo テスト用データベース作成完了

echo.
echo [2/4] テスト用テーブル作成中...

REM テスト用テーブル作成
set PGPASSWORD=%DB_PASSWORD%
psql -U %DB_USER% -d stock_data_system_test -h localhost -f "%SCRIPT_DIR%create_tables.sql" >nul 2>&1
if errorlevel 1 (
    echo エラー: テスト用テーブルの作成に失敗しました
    pause
    exit /b 1
)
echo テスト用テーブル作成完了

echo.
echo [3/4] Python依存関係確認中...

REM Pythonとpytestの確認
python --version >nul 2>&1
if errorlevel 1 (
    echo エラー: Pythonが見つかりません
    echo Pythonをインストールしてください: https://www.python.org/
    pause
    exit /b 1
)

REM 必要なパッケージのインストール確認
python -c "import psycopg2, pytest" >nul 2>&1
if errorlevel 1 (
    echo 必要なPythonパッケージをインストール中...
    pip install psycopg2-binary pytest >nul 2>&1
    if errorlevel 1 (
        echo エラー: Pythonパッケージのインストールに失敗しました
        pause
        exit /b 1
    )
)
echo Python環境確認完了

echo.
echo [4/4] テスト実行中...
echo.

REM テスト実行
cd /d "%SCRIPT_DIR%"
python test_database_setup.py
set TEST_RESULT=!errorlevel!

echo.
echo [テスト後処理] テスト用データベース削除中...

REM テスト用データベース削除
set PGPASSWORD=%POSTGRES_PASSWORD%
psql -U %POSTGRES_USER% -h localhost -c "DROP DATABASE IF EXISTS stock_data_system_test;" >nul 2>&1

echo.
if !TEST_RESULT! equ 0 (
    echo ========================================
    echo ✅ テスト完了: すべて成功
    echo ========================================
) else (
    echo ========================================
    echo ❌ テスト完了: 一部失敗
    echo ========================================
)

echo.
pause
exit /b !TEST_RESULT!