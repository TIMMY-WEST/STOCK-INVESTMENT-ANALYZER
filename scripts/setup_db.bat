@echo off
REM =============================================================================
REM PostgreSQL Database Setup Script for Windows
REM Stock Data System Database Automated Setup Script
REM =============================================================================

chcp 65001 >nul 2>&1
setlocal enabledelayedexpansion

REM Set PostgreSQL client encoding to UTF8
set PGCLIENTENCODING=UTF8

echo ========================================
echo PostgreSQL Database Setup Started
echo ========================================
echo.

REM Load configuration from .env file
echo Loading configuration from .env file...
if not exist "%~dp0..\.env" (
    echo ERROR: .env file not found
    echo Please create .env file in project root
    pause
    exit /b 1
)

REM Load .env file
for /f "tokens=1,2 delims==" %%i in ('findstr /v "^#" "%~dp0..\.env"') do (
    if "%%i"=="DB_NAME" set DB_NAME=%%j
    if "%%i"=="DB_USER" set DB_USER=%%j
    if "%%i"=="DB_PASSWORD" set DB_PASSWORD=%%j
    if "%%i"=="POSTGRES_PASSWORD" set POSTGRES_PASSWORD=%%j
    if "%%i"=="DB_DATA_DIR" set DB_DATA_DIR=%%j
)

REM Set default values
if not defined POSTGRES_PASSWORD set POSTGRES_PASSWORD=postgres
set POSTGRES_USER=postgres

REM Set default data directory if not specified
if not defined DB_DATA_DIR set DB_DATA_DIR=

REM Set PGPASSWORD environment variable to avoid password prompt
set PGPASSWORD=%POSTGRES_PASSWORD%

echo Configuration:
echo   Database Name: %DB_NAME%
echo   User Name: %DB_USER%
echo   PostgreSQL Password: [configured]
if defined DB_DATA_DIR (
    echo   Database Storage: %DB_DATA_DIR%
) else (
    echo   Database Storage: [default PostgreSQL data directory]
)
echo.

REM Check if PostgreSQL is installed
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

REM Check PostgreSQL service status
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
        )
    )
)
echo PostgreSQL service is running

REM Create database
echo.
echo [3/6] Creating database...
REM Set postgres user password in environment variable
set PGPASSWORD=%POSTGRES_PASSWORD%
psql -U %POSTGRES_USER% -h localhost -c "SELECT 1;" >nul 2>&1
if errorlevel 1 (
    echo ERROR: Failed to connect as postgres user
    echo Please check PostgreSQL configuration
    pause
    exit /b 1
)

REM Create custom data directory and tablespace if DB_DATA_DIR is specified
if defined DB_DATA_DIR (
    echo Creating custom database storage at: %DB_DATA_DIR%

    REM Create directory structure for database
    set DB_FULL_PATH=%DB_DATA_DIR%\%DB_NAME%
    if not exist "!DB_FULL_PATH!" (
        echo Creating directory: !DB_FULL_PATH!
        mkdir "!DB_FULL_PATH!"
        if errorlevel 1 (
            echo ERROR: Failed to create directory
            pause
            exit /b 1
        )
    )

    REM Check if tablespace already exists
    psql -U %POSTGRES_USER% -h localhost -t -c "SELECT 1 FROM pg_tablespace WHERE spcname='stock_data_space';" | findstr "1" >nul
    if errorlevel 1 (
        echo Creating tablespace stock_data_space...
        psql -U %POSTGRES_USER% -h localhost -c "CREATE TABLESPACE stock_data_space OWNER postgres LOCATION '!DB_FULL_PATH!';"
        if errorlevel 1 (
            echo ERROR: Failed to create tablespace
            echo Make sure the directory has proper permissions and is empty
            pause
            exit /b 1
        )
    ) else (
        echo Tablespace stock_data_space already exists
    )
)

REM Check if database already exists
psql -U %POSTGRES_USER% -h localhost -t -c "SELECT 1 FROM pg_database WHERE datname='%DB_NAME%';" | findstr "1" >nul
if errorlevel 1 (
    echo Creating database %DB_NAME%...

    if defined DB_DATA_DIR (
        REM Create database with custom tablespace and C locale
        psql -U %POSTGRES_USER% -h localhost -c "CREATE DATABASE %DB_NAME% WITH OWNER = postgres ENCODING = 'UTF8' LC_COLLATE = 'C' LC_CTYPE = 'C' TABLESPACE = stock_data_space TEMPLATE = template0 CONNECTION LIMIT = -1;"
    ) else (
        REM Create database with default tablespace and C locale
        psql -U %POSTGRES_USER% -h localhost -c "CREATE DATABASE %DB_NAME% WITH OWNER = postgres ENCODING = 'UTF8' LC_COLLATE = 'C' LC_CTYPE = 'C' TABLESPACE = pg_default TEMPLATE = template0 CONNECTION LIMIT = -1;"
    )

    if errorlevel 1 (
        echo ERROR: Failed to create database
        pause
        exit /b 1
    )

    REM Add comment to database
    psql -U %POSTGRES_USER% -h localhost -c "COMMENT ON DATABASE %DB_NAME% IS 'Stock Data System Database';"

    echo Database created successfully
    if defined DB_DATA_DIR (
        echo Database files location: !DB_FULL_PATH!
    )
) else (
    echo Database %DB_NAME% already exists
)

REM Create user if not exists
echo Creating database user...
psql -U %POSTGRES_USER% -h localhost -t -c "SELECT 1 FROM pg_catalog.pg_roles WHERE rolname='%DB_USER%';" | findstr "1" >nul
if errorlevel 1 (
    echo Creating user %DB_USER%...
    psql -U %POSTGRES_USER% -h localhost -c "CREATE ROLE %DB_USER% LOGIN PASSWORD '%DB_PASSWORD%';"
    if errorlevel 1 (
        echo ERROR: Failed to create user
        pause
        exit /b 1
    )
) else (
    echo User %DB_USER% already exists
)

REM Grant privileges
echo Granting privileges...
psql -U %POSTGRES_USER% -h localhost -c "GRANT ALL PRIVILEGES ON DATABASE %DB_NAME% TO %DB_USER%;"
psql -U %POSTGRES_USER% -h localhost -c "ALTER USER %DB_USER% CREATEDB;"

REM Grant schema privileges (required for PostgreSQL 15+)
echo Granting schema privileges...
psql -U %POSTGRES_USER% -h localhost -d %DB_NAME% -c "GRANT ALL ON SCHEMA public TO %DB_USER%;"
psql -U %POSTGRES_USER% -h localhost -d %DB_NAME% -c "GRANT CREATE ON SCHEMA public TO %DB_USER%;"
psql -U %POSTGRES_USER% -h localhost -d %DB_NAME% -c "ALTER SCHEMA public OWNER TO %DB_USER%;"

REM Grant default privileges for future objects
psql -U %POSTGRES_USER% -h localhost -d %DB_NAME% -c "ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO %DB_USER%;"
psql -U %POSTGRES_USER% -h localhost -d %DB_NAME% -c "ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO %DB_USER%;"

echo Database setup completed successfully

REM Create tables
echo.
echo [4/6] Creating tables...
REM Set stock_user password in environment variable
set PGPASSWORD=%DB_PASSWORD%

REM Set client encoding to UTF8 to handle SQL files properly
set PGCLIENTENCODING=UTF8

psql -U %DB_USER% -d %DB_NAME% -h localhost -f "%~dp0create_tables.sql"
if errorlevel 1 (
    echo ERROR: Failed to create tables
    pause
    exit /b 1
)
echo Tables created successfully

REM Insert sample data
echo.
echo [5/6] Inserting initial data...
if exist "%~dp0insert_sample_data.sql" (
    REM Set stock_user password in environment variable
    set PGPASSWORD=%DB_PASSWORD%

    REM Ensure client encoding is UTF8
    set PGCLIENTENCODING=UTF8

    psql -U %DB_USER% -d %DB_NAME% -h localhost -f "%~dp0insert_sample_data.sql"
    if errorlevel 1 (
        echo WARNING: Some sample data insertion failed
    ) else (
        echo Sample data inserted successfully
    )
) else (
    echo Sample data file not found (skipped)
)

REM Connection test
echo.
echo [6/6] Testing database connection...
REM Set stock_user password in environment variable
set PGPASSWORD=%DB_PASSWORD%

REM Ensure client encoding is UTF8
set PGCLIENTENCODING=UTF8

psql -U %DB_USER% -d %DB_NAME% -h localhost -c "\dt"
if errorlevel 1 (
    echo ERROR: Database connection test failed
    pause
    exit /b 1
)

echo.
echo ========================================
echo Database Setup Completed Successfully!
echo ========================================
echo.
echo Database Information:
echo   Database Name: %DB_NAME%
echo   User Name: %DB_USER%
echo   Password: %DB_PASSWORD%
echo   Host: localhost
echo   Port: 5432
if defined DB_DATA_DIR (
    set DB_FULL_PATH=%DB_DATA_DIR%\%DB_NAME%
    echo   Storage Location: !DB_FULL_PATH!
)
echo.
echo Connection command example:
echo   psql -U %DB_USER% -d %DB_NAME% -h localhost
echo.
echo Please configure .env file to connect from Python application
echo.

echo Setup completed successfully!
pause
