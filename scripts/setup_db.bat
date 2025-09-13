@echo off
REM =============================================================================
REM PostgreSQL データベースセットアップ用Windowsバッチファイル
REM 株価データ取得システム用データベース自動構築スクリプト
REM =============================================================================

setlocal enabledelayedexpansion

echo ========================================
echo PostgreSQL データベースセットアップ開始
echo ========================================
echo.

REM .envファイルから設定値を読み込み
echo .envファイルから設定を読み込み中...
if not exist "%~dp0..\.env" (
    echo エラー: .envファイルが見つかりません
    echo プロジェクトルートに.envファイルを作成してください
    pause
    exit /b 1
)

REM .envファイルの読み込み
for /f "tokens=1,2 delims==" %%i in ('findstr /v "^#" "%~dp0..\.env"') do (
    if "%%i"=="DB_NAME" set DB_NAME=%%j
    if "%%i"=="DB_USER" set DB_USER=%%j
    if "%%i"=="DB_PASSWORD" set DB_PASSWORD=%%j
    if "%%i"=="POSTGRES_PASSWORD" set POSTGRES_PASSWORD=%%j
)

REM デフォルト値設定
if not defined POSTGRES_PASSWORD set POSTGRES_PASSWORD=postgres
set POSTGRES_USER=postgres

REM 環境変数PGPASSWORD設定（パスワード入力を回避）
set PGPASSWORD=%POSTGRES_PASSWORD%

echo 設定値確認:
echo   データベース名: %DB_NAME%
echo   ユーザー名: %DB_USER%
echo   PostgreSQLパスワード: [設定済み]
echo.

REM PostgreSQLがインストールされているかチェック
echo [1/6] PostgreSQL インストール確認中...
psql --version >nul 2>&1
if errorlevel 1 (
    echo エラー: PostgreSQLがインストールされていません
    echo PostgreSQLをインストールしてから再実行してください
    echo インストール方法: https://www.postgresql.org/download/windows/
    pause
    exit /b 1
)
echo PostgreSQL が見つかりました

REM PostgreSQLサービス開始確認
echo.
echo [2/6] PostgreSQL サービス状態確認中...
net start | findstr -i "postgresql" >nul
if errorlevel 1 (
    echo PostgreSQLサービスが開始されていません
    echo サービスを開始しています...
    net start postgresql-x64-16 >nul 2>&1
    if errorlevel 1 (
        net start postgresql >nul 2>&1
        if errorlevel 1 (
            echo 警告: PostgreSQLサービスを自動開始できませんでした
            echo 手動でサービスを開始してください（services.msc）
            pause
        )
    )
)
echo PostgreSQL サービスは稼働中です

REM データベース作成
echo.
echo [3/6] データベース作成中...
REM postgresユーザーのパスワードを環境変数に設定
set PGPASSWORD=%POSTGRES_PASSWORD%
psql -U %POSTGRES_USER% -h localhost -c "SELECT 1;" >nul 2>&1
if errorlevel 1 (
    echo エラー: postgres ユーザーでの接続に失敗しました
    echo PostgreSQLの設定を確認してください
    pause
    exit /b 1
)

REM データベース作成スクリプト実行
echo データベース作成スクリプト実行中...
REM postgresユーザーのパスワードを環境変数に設定
set PGPASSWORD=%POSTGRES_PASSWORD%
psql -U %POSTGRES_USER% -h localhost -f "%~dp0create_database.sql"
if errorlevel 1 (
    echo エラー: データベース作成に失敗しました
    pause
    exit /b 1
)
echo データベース作成完了

REM テーブル作成
echo.
echo [4/6] テーブル作成中...
REM stock_userのパスワードを環境変数に設定
set PGPASSWORD=%DB_PASSWORD%
psql -U %DB_USER% -d %DB_NAME% -h localhost -f "%~dp0create_tables.sql"
if errorlevel 1 (
    echo エラー: テーブル作成に失敗しました
    pause
    exit /b 1
)
echo テーブル作成完了

REM サンプルデータ投入
echo.
echo [5/6] 初期データ投入中...
if exist "%~dp0insert_sample_data.sql" (
    REM stock_userのパスワードを環境変数に設定
    set PGPASSWORD=%DB_PASSWORD%
    psql -U %DB_USER% -d %DB_NAME% -h localhost -f "%~dp0insert_sample_data.sql"
    if errorlevel 1 (
        echo 警告: サンプルデータ投入に一部失敗しました
    ) else (
        echo サンプルデータ投入完了
    )
) else (
    echo サンプルデータファイルが見つかりません（スキップ）
)

REM 接続テスト
echo.
echo [6/6] データベース接続テスト中...
REM stock_userのパスワードを環境変数に設定
set PGPASSWORD=%DB_PASSWORD%
psql -U %DB_USER% -d %DB_NAME% -h localhost -c "\dt"
if errorlevel 1 (
    echo エラー: データベース接続テストに失敗しました
    pause
    exit /b 1
)

echo.
echo ========================================
echo データベースセットアップ完了！
echo ========================================
echo.
echo データベース情報:
echo   データベース名: %DB_NAME%
echo   ユーザー名: %DB_USER%
echo   パスワード: %DB_PASSWORD%
echo   ホスト: localhost
echo   ポート: 5432
echo.
echo 接続コマンド例:
echo   psql -U %DB_USER% -d %DB_NAME% -h localhost
echo.
echo Pythonアプリケーションから接続するために .env ファイルを設定してください
echo.

REM .envファイル作成確認
if not exist "%~dp0..\.env" (
    echo .env ファイルがありません。作成しますか？ [Y/N]
    choice /c YN /n
    if !errorlevel!==1 (
        echo # データベース設定 > "%~dp0..\.env"
        echo DB_HOST=localhost >> "%~dp0..\.env"
        echo DB_PORT=5432 >> "%~dp0..\.env"
        echo DB_NAME=%DB_NAME% >> "%~dp0..\.env"
        echo DB_USER=%DB_USER% >> "%~dp0..\.env"
        echo DB_PASSWORD=%DB_PASSWORD% >> "%~dp0..\.env"
        echo. >> "%~dp0..\.env"
        echo # アプリケーション設定 >> "%~dp0..\.env"
        echo FLASK_ENV=development >> "%~dp0..\.env"
        echo FLASK_DEBUG=True >> "%~dp0..\.env"
        echo FLASK_PORT=8000 >> "%~dp0..\.env"
        echo .env ファイルを作成しました
    )
)

echo セットアップが完了しました！
pause