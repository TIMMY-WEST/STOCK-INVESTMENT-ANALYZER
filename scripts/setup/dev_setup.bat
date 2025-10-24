@echo off
REM =============================================================================
REM STOCK-INVESTMENT-ANALYZER - Development Environment Setup Script
REM Windows用開発環境自動セットアップスクリプト
REM =============================================================================

chcp 65001 >nul 2>&1
setlocal enabledelayedexpansion

REM プロジェクトルートディレクトリ
set SCRIPT_DIR=%~dp0
set PROJECT_ROOT=%SCRIPT_DIR:~0,-9%

REM Python関連設定
set PYTHON_CMD=python
set VENV_DIR=%PROJECT_ROOT%venv
set REQUIREMENTS_FILE=%PROJECT_ROOT%requirements.txt
set REQUIREMENTS_DEV_FILE=%PROJECT_ROOT%requirements-dev.txt

REM 環境変数ファイル
set ENV_EXAMPLE=%PROJECT_ROOT%.env.example
set ENV_FILE=%PROJECT_ROOT%.env

REM カラー出力（Windows 10以降）
set BLUE=[94m
set GREEN=[92m
set YELLOW=[93m
set RED=[91m
set CYAN=[96m
set NC=[0m

REM =============================================================================
REM メイン処理開始
REM =============================================================================

echo.
echo ========================================
echo STOCK-INVESTMENT-ANALYZER
echo Development Environment Setup
echo ========================================
echo.
echo Starting setup (estimated time: 5-15 minutes)
echo.

REM =============================================================================
REM ステップ1: 前提条件チェック
REM =============================================================================

echo %CYAN%[1/7]%NC% Checking prerequisites...

REM Python バージョンチェック
where %PYTHON_CMD% >nul 2>&1
if errorlevel 1 (
    echo %RED%[ERROR]%NC% Python not found
    echo Please install Python 3.8 or higher
    echo Install: https://www.python.org/downloads/
    pause
    exit /b 1
)

for /f "tokens=2" %%v in ('%PYTHON_CMD% --version 2^>^&1') do set PYTHON_VERSION=%%v
echo %BLUE%[INFO]%NC% Python version: %PYTHON_VERSION%

REM Python バージョンが3.8以上かチェック
for /f "tokens=1,2 delims=." %%a in ("%PYTHON_VERSION%") do (
    set PYTHON_MAJOR=%%a
    set PYTHON_MINOR=%%b
)

if %PYTHON_MAJOR% LSS 3 (
    echo %RED%[ERROR]%NC% Python 3.8 or higher is required (current: %PYTHON_VERSION%)
    pause
    exit /b 1
)

if %PYTHON_MAJOR% EQU 3 (
    if %PYTHON_MINOR% LSS 8 (
        echo %RED%[ERROR]%NC% Python 3.8 or higher is required (current: %PYTHON_VERSION%)
        pause
        exit /b 1
    )
)

REM Git チェック
where git >nul 2>&1
if errorlevel 1 (
    echo %YELLOW%[WARNING]%NC% Git not found (optional)
) else (
    for /f "tokens=3" %%v in ('git --version 2^>^&1') do (
        echo %BLUE%[INFO]%NC% Git version: %%v
        goto :git_found
    )
    :git_found
)

REM PostgreSQL チェック
where psql >nul 2>&1
if errorlevel 1 (
    echo %YELLOW%[WARNING]%NC% PostgreSQL not found
    echo You can continue if you want to skip database setup
    set /p continue_without_pg="Continue anyway? [y/N]: "
    if /i not "!continue_without_pg!"=="y" (
        echo %RED%[ERROR]%NC% Please install PostgreSQL and try again
        echo Install: https://www.postgresql.org/download/windows/
        pause
        exit /b 1
    )
    set SKIP_DB_SETUP=true
) else (
    echo %BLUE%[INFO]%NC% PostgreSQL found
    set SKIP_DB_SETUP=false
)

echo %GREEN%[SUCCESS]%NC% Prerequisites check completed
echo.

REM =============================================================================
REM ステップ2: 環境変数ファイルの設定
REM =============================================================================

echo %CYAN%[2/7]%NC% Setting up environment file...

if exist "%ENV_FILE%" (
    echo %YELLOW%[WARNING]%NC% .env file already exists
    set /p overwrite_env="Overwrite? [y/N]: "
    if /i "!overwrite_env!"=="y" (
        copy /y "%ENV_EXAMPLE%" "%ENV_FILE%" >nul
        echo %GREEN%[SUCCESS]%NC% .env file has been overwritten
    ) else (
        echo %BLUE%[INFO]%NC% Using existing .env file
    )
) else (
    if exist "%ENV_EXAMPLE%" (
        copy "%ENV_EXAMPLE%" "%ENV_FILE%" >nul
        echo %GREEN%[SUCCESS]%NC% .env file created
    ) else (
        echo %YELLOW%[WARNING]%NC% .env.example not found. Please create .env manually
    )
)

echo.

REM =============================================================================
REM ステップ3: Python仮想環境の作成
REM =============================================================================

echo %CYAN%[3/7]%NC% Creating Python virtual environment...

if exist "%VENV_DIR%" (
    echo %YELLOW%[WARNING]%NC% Virtual environment already exists
    set /p recreate_venv="Recreate? [y/N]: "
    if /i "!recreate_venv!"=="y" (
        echo %BLUE%[INFO]%NC% Removing existing virtual environment...
        rmdir /s /q "%VENV_DIR%"
        %PYTHON_CMD% -m venv "%VENV_DIR%"
        if errorlevel 1 (
            echo %RED%[ERROR]%NC% Failed to create virtual environment
            pause
            exit /b 1
        )
        echo %GREEN%[SUCCESS]%NC% Virtual environment recreated
    ) else (
        echo %BLUE%[INFO]%NC% Using existing virtual environment
    )
) else (
    %PYTHON_CMD% -m venv "%VENV_DIR%"
    if errorlevel 1 (
        echo %RED%[ERROR]%NC% Failed to create virtual environment
        pause
        exit /b 1
    )
    echo %GREEN%[SUCCESS]%NC% Virtual environment created
)

REM 仮想環境の有効化
call "%VENV_DIR%\Scripts\activate.bat"
echo %BLUE%[INFO]%NC% Virtual environment activated

echo.

REM =============================================================================
REM ステップ4: pip のアップグレード
REM =============================================================================

echo %CYAN%[4/7]%NC% Upgrading pip...

python -m pip install --upgrade pip >nul 2>&1
if errorlevel 1 (
    echo %YELLOW%[WARNING]%NC% Failed to upgrade pip
) else (
    for /f "tokens=2" %%v in ('pip --version 2^>^&1') do (
        echo %GREEN%[SUCCESS]%NC% pip upgraded (%%v)
        goto :pip_upgraded
    )
    :pip_upgraded
)

echo.

REM =============================================================================
REM ステップ5: 依存関係のインストール
REM =============================================================================

echo %CYAN%[5/7]%NC% Installing dependencies...

if not exist "%REQUIREMENTS_FILE%" (
    echo %RED%[ERROR]%NC% requirements.txt not found
    pause
    exit /b 1
)

echo %BLUE%[INFO]%NC% Installing production dependencies...
pip install -r "%REQUIREMENTS_FILE%"
if errorlevel 1 (
    echo %RED%[ERROR]%NC% Failed to install dependencies
    pause
    exit /b 1
)
echo %GREEN%[SUCCESS]%NC% Production dependencies installed

if exist "%REQUIREMENTS_DEV_FILE%" (
    echo %BLUE%[INFO]%NC% Installing development dependencies...
    pip install -r "%REQUIREMENTS_DEV_FILE%"
    if errorlevel 1 (
        echo %YELLOW%[WARNING]%NC% Some development dependencies failed to install
    ) else (
        echo %GREEN%[SUCCESS]%NC% Development dependencies installed
    )
) else (
    echo %YELLOW%[WARNING]%NC% requirements-dev.txt not found (skipped)
)

echo.

REM =============================================================================
REM ステップ6: データベースセットアップ
REM =============================================================================

echo %CYAN%[6/7]%NC% Setting up database...

if "%SKIP_DB_SETUP%"=="true" (
    echo %YELLOW%[WARNING]%NC% Skipping database setup (PostgreSQL not found)
) else (
    set /p setup_db="Run database setup? [Y/n]: "
    if /i not "!setup_db!"=="n" (
        set DB_SETUP_SCRIPT=%SCRIPT_DIR%setup_db.bat
        if exist "!DB_SETUP_SCRIPT!" (
            echo %BLUE%[INFO]%NC% Running database setup script...
            call "!DB_SETUP_SCRIPT!"
            if errorlevel 1 (
                echo %YELLOW%[WARNING]%NC% Database setup failed
                echo You can run it manually later: scripts\setup\setup_db.bat
            ) else (
                echo %GREEN%[SUCCESS]%NC% Database setup completed
            )
        ) else (
            echo %YELLOW%[WARNING]%NC% Database setup script not found
            echo You can run it manually later: scripts\setup\setup_db.bat
        )
    ) else (
        echo %BLUE%[INFO]%NC% Database setup skipped
        echo Run it later: scripts\setup\setup_db.bat
    )
)

echo.

REM =============================================================================
REM ステップ7: セットアップの検証
REM =============================================================================

echo %CYAN%[7/7]%NC% Verifying setup...

REM Pythonパッケージの確認
for /f %%c in ('pip list ^| find /c /v ""') do set PACKAGE_COUNT=%%c
echo %BLUE%[INFO]%NC% Installed packages: %PACKAGE_COUNT%

REM 重要なパッケージのバージョン確認
for /f "delims=" %%v in ('python -c "import flask; print(flask.__version__)" 2^>nul') do set FLASK_VERSION=%%v
if not defined FLASK_VERSION set FLASK_VERSION=not installed

for /f "delims=" %%v in ('python -c "import sqlalchemy; print(sqlalchemy.__version__)" 2^>nul') do set SQLALCHEMY_VERSION=%%v
if not defined SQLALCHEMY_VERSION set SQLALCHEMY_VERSION=not installed

echo %BLUE%[INFO]%NC% Flask: %FLASK_VERSION%
echo %BLUE%[INFO]%NC% SQLAlchemy: %SQLALCHEMY_VERSION%

REM .envファイルの確認
if exist "%ENV_FILE%" (
    echo %GREEN%[SUCCESS]%NC% .env file: exists
) else (
    echo %YELLOW%[WARNING]%NC% .env file: not created
)

echo %GREEN%[SUCCESS]%NC% Setup verification completed

echo.

REM =============================================================================
REM セットアップ完了
REM =============================================================================

echo ========================================
echo Setup completed successfully!
echo ========================================
echo.

echo %BLUE%[INFO]%NC% Next steps:
echo.
echo   1. Review/edit environment variables
echo      Edit .env file
echo.
echo   2. Activate virtual environment
echo      venv\Scripts\activate
echo.
echo   3. Start application
echo      cd app
echo      python app.py
echo.
echo   4. Access in browser
echo      http://localhost:8000
echo.

echo %BLUE%[INFO]%NC% Useful commands (with PowerShell or WSL):
echo   - make help       : List available commands
echo   - make test       : Run tests
echo   - make db-reset   : Reset database
echo   - make clean      : Clear caches
echo.

echo %BLUE%[INFO]%NC% Documentation:
echo   - README.md
echo   - docs\development\github_workflow.md
echo   - docs\development\troubleshooting.md
echo.

echo ========================================
echo Happy coding!
echo ========================================
echo.

pause
