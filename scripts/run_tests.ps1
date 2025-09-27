# データベース初期化スクリプト テスト実行 (PowerShell版)

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "データベース初期化スクリプト テスト実行" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 現在のディレクトリを取得
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path

# .envファイルから設定を読み込み
$envFile = Join-Path $ScriptDir ".env"
if (Test-Path $envFile) {
    Write-Host ".envファイルから設定を読み込み中..." -ForegroundColor Yellow
    Get-Content $envFile | ForEach-Object {
        if ($_ -match "^([^=]+)=(.*)$") {
            Set-Variable -Name $matches[1] -Value $matches[2] -Scope Global
        }
    }
} else {
    Write-Host ".envファイルが見つかりません。デフォルト設定を使用します。" -ForegroundColor Yellow
    $Global:DB_HOST = "localhost"
    $Global:DB_PORT = "5432"
    $Global:DB_NAME = "stock_data_system"
    $Global:DB_USER = "stock_user"
    $Global:DB_PASSWORD = "stock_password"
    $Global:POSTGRES_USER = "postgres"
    $Global:POSTGRES_PASSWORD = "postgres"
}

Write-Host ""
Write-Host "[1/4] テスト用データベース作成中..." -ForegroundColor Green

# テスト用データベース作成
$env:PGPASSWORD = $Global:POSTGRES_PASSWORD
try {
    & psql -U $Global:POSTGRES_USER -h localhost -c "DROP DATABASE IF EXISTS stock_data_system_test;" 2>$null
    & psql -U $Global:POSTGRES_USER -h localhost -c "CREATE DATABASE stock_data_system_test OWNER $Global:DB_USER;" 2>$null
    if ($LASTEXITCODE -ne 0) {
        throw "テスト用データベースの作成に失敗しました"
    }
    Write-Host "テスト用データベース作成完了" -ForegroundColor Green
} catch {
    Write-Host "エラー: $_" -ForegroundColor Red
    Read-Host "続行するには何かキーを押してください"
    exit 1
}

Write-Host ""
Write-Host "[2/4] テスト用テーブル作成中..." -ForegroundColor Green

# テスト用テーブル作成
$env:PGPASSWORD = $Global:DB_PASSWORD
try {
    $createTablesPath = Join-Path $ScriptDir "create_tables.sql"
    & psql -U $Global:DB_USER -d stock_data_system_test -h localhost -f $createTablesPath 2>$null
    if ($LASTEXITCODE -ne 0) {
        throw "テスト用テーブルの作成に失敗しました"
    }
    Write-Host "テスト用テーブル作成完了" -ForegroundColor Green
} catch {
    Write-Host "エラー: $_" -ForegroundColor Red
    Read-Host "続行するには何かキーを押してください"
    exit 1
}

Write-Host ""
Write-Host "[3/4] Python依存関係確認中..." -ForegroundColor Green

# Pythonの確認
try {
    & python --version 2>$null
    if ($LASTEXITCODE -ne 0) {
        throw "Pythonが見つかりません"
    }
} catch {
    Write-Host "エラー: Pythonが見つかりません" -ForegroundColor Red
    Write-Host "Pythonをインストールしてください: https://www.python.org/" -ForegroundColor Yellow
    Read-Host "続行するには何かキーを押してください"
    exit 1
}

# 必要なパッケージのインストール確認
try {
    & python -c "import psycopg2, pytest" 2>$null
    if ($LASTEXITCODE -ne 0) {
        Write-Host "必要なPythonパッケージをインストール中..." -ForegroundColor Yellow
        & pip install psycopg2-binary pytest 2>$null
        if ($LASTEXITCODE -ne 0) {
            throw "Pythonパッケージのインストールに失敗しました"
        }
    }
    Write-Host "Python環境確認完了" -ForegroundColor Green
} catch {
    Write-Host "エラー: $_" -ForegroundColor Red
    Read-Host "続行するには何かキーを押してください"
    exit 1
}

Write-Host ""
Write-Host "[4/4] テスト実行中..." -ForegroundColor Green
Write-Host ""

# テスト実行
Set-Location $ScriptDir
$testResult = 0
try {
    & python test_database_setup.py
    $testResult = $LASTEXITCODE
} catch {
    Write-Host "テスト実行中にエラーが発生しました: $_" -ForegroundColor Red
    $testResult = 1
}

Write-Host ""
Write-Host "[テスト後処理] テスト用データベース削除中..." -ForegroundColor Yellow

# テスト用データベース削除
$env:PGPASSWORD = $Global:POSTGRES_PASSWORD
& psql -U $Global:POSTGRES_USER -h localhost -c "DROP DATABASE IF EXISTS stock_data_system_test;" 2>$null

Write-Host ""
if ($testResult -eq 0) {
    Write-Host "========================================" -ForegroundColor Green
    Write-Host "✅ テスト完了: すべて成功" -ForegroundColor Green
    Write-Host "========================================" -ForegroundColor Green
} else {
    Write-Host "========================================" -ForegroundColor Red
    Write-Host "❌ テスト完了: 一部失敗" -ForegroundColor Red
    Write-Host "========================================" -ForegroundColor Red
}

Write-Host ""
Read-Host "続行するには何かキーを押してください"
exit $testResult