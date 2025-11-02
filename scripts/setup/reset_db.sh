#!/bin/bash
# =============================================================================
# PostgreSQL データベースリセット用Linuxシェルスクリプト
# 株価データ取得システム用データベースクリーンリセットスクリプト
# =============================================================================

# エラー発生時の処理
set -e

# カラー定義
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# 設定値
DB_NAME="stock_data_system"
DB_USER="stock_user"
DB_PASSWORD="stock_password"
POSTGRES_USER="postgres"

# バックアップディレクトリ
BACKUP_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )/../database/backups"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")

# ログ関数
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

log_step() {
    echo -e "${CYAN}[STEP]${NC} $1"
}

# 確認プロンプト関数
confirm_action() {
    local message="$1"
    echo -e "${YELLOW}${message}${NC}"
    read -p "Do you want to continue? [y/N]: " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        log_warning "Operation cancelled by user"
        exit 0
    fi
}

# バックアップ作成関数
create_backup() {
    log_step "[OPTION] Create database backup"
    read -p "Do you want to create a backup? [y/N]: " -n 1 -r
    echo

    if [[ $REPLY =~ ^[Yy]$ ]]; then
        # バックアップディレクトリ作成
        mkdir -p "$BACKUP_DIR"

        local backup_file="$BACKUP_DIR/${DB_NAME}_backup_${TIMESTAMP}.sql"

        log_info "Creating backup: $backup_file"

        export PGPASSWORD="$DB_PASSWORD"
        if pg_dump -U "$DB_USER" -h localhost "$DB_NAME" > "$backup_file" 2>/dev/null; then
            log_success "Backup created successfully: $backup_file"

            # 30日以上前の古いバックアップを削除
            find "$BACKUP_DIR" -name "${DB_NAME}_backup_*.sql" -mtime +30 -delete 2>/dev/null || true
        else
            log_warning "Failed to create backup (database might not exist)"
            read -p "Continue without backup? [y/N]: " -n 1 -r
            echo
            if [[ ! $REPLY =~ ^[Yy]$ ]]; then
                log_warning "Operation cancelled by user"
                exit 0
            fi
        fi
        unset PGPASSWORD
    else
        log_info "Backup skipped"
    fi
}

# エラーハンドリング関数
handle_error() {
    local exit_code=$?
    log_error "An error occurred (exit code: $exit_code)"

    # ロールバック処理
    log_warning "Attempting rollback..."

    # 最新のバックアップファイルを探す
    if [ -d "$BACKUP_DIR" ]; then
        local latest_backup=$(ls -t "$BACKUP_DIR"/${DB_NAME}_backup_*.sql 2>/dev/null | head -n 1)

        if [ -n "$latest_backup" ]; then
            log_info "Latest backup found: $latest_backup"
            read -p "Restore from this backup? [y/N]: " -n 1 -r
            echo

            if [[ $REPLY =~ ^[Yy]$ ]]; then
                export PGPASSWORD="$DB_PASSWORD"
                psql -U "$DB_USER" -h localhost -d "$DB_NAME" < "$latest_backup"
                unset PGPASSWORD
                log_success "Restored from backup"
            fi
        fi
    fi

    exit $exit_code
}

# エラートラップ設定
trap handle_error ERR

# スクリプト開始
clear
echo "========================================="
echo "  Database Reset Script"
echo "========================================="
echo
echo "This script will perform the following operations:"
echo "  1. Create database backup (optional)"
echo "  2. Drop existing database"
echo "  3. Recreate database"
echo "  4. Create tables"
echo "  5. Insert sample data"
echo
log_warning "⚠️  WARNING: This will delete ALL existing data! ⚠️"
echo

# 最終確認
confirm_action "Are you sure you want to reset the database?"

# PostgreSQLインストール確認
log_step "[1/6] Checking PostgreSQL installation"
if ! command -v psql &> /dev/null; then
    log_error "PostgreSQL is not installed"
    echo
    echo "Please install PostgreSQL and try again"
    echo
    echo "For Ubuntu:"
    echo "  sudo apt update"
    echo "  sudo apt install postgresql postgresql-contrib"
    echo
    echo "For macOS:"
    echo "  brew install postgresql"
    echo
    exit 1
fi
log_success "PostgreSQL found"

# PostgreSQLサービス確認
log_step "[2/6] Checking PostgreSQL service status"
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    # Linux
    if ! systemctl is-active --quiet postgresql 2>/dev/null; then
        log_warning "PostgreSQL service is not running"
        log_info "Starting PostgreSQL service..."
        sudo systemctl start postgresql
    fi
elif [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS
    if ! brew services list 2>/dev/null | grep postgresql | grep started > /dev/null; then
        log_warning "PostgreSQL service is not running"
        log_info "Starting PostgreSQL service..."
        brew services start postgresql
    fi
fi
log_success "PostgreSQL service is running"

# バックアップ作成
create_backup

# スクリプトディレクトリ取得
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

# データベース削除と再作成
log_step "[3/6] Dropping and recreating database"
log_info "Dropping existing database..."

# アクティブな接続を強制終了
export PGPASSWORD="${POSTGRES_PASSWORD:-postgres}"
psql -U "$POSTGRES_USER" -h localhost << EOF 2>/dev/null || true
-- アクティブな接続を強制終了
SELECT pg_terminate_backend(pid)
FROM pg_stat_activity
WHERE datname = '$DB_NAME' AND pid <> pg_backend_pid();
EOF

# データベース削除
psql -U "$POSTGRES_USER" -h localhost << EOF
DROP DATABASE IF EXISTS $DB_NAME;
EOF
log_success "Existing database dropped"

# データベース作成
log_info "Creating new database..."
if [ -f "$SCRIPT_DIR/../database/schema/create_database.sql" ]; then
    psql -U "$POSTGRES_USER" -h localhost -f "$SCRIPT_DIR/../database/schema/create_database.sql"
else
    # create_database.sqlが存在しない場合は直接作成
    psql -U "$POSTGRES_USER" -h localhost << EOF
-- ユーザーが存在しない場合のみ作成
DO \$\$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_user WHERE usename = '$DB_USER') THEN
        CREATE USER $DB_USER WITH PASSWORD '$DB_PASSWORD';
    END IF;
END
\$\$;

-- データベース作成
CREATE DATABASE $DB_NAME OWNER $DB_USER ENCODING 'UTF8';

-- 権限付与
GRANT ALL PRIVILEGES ON DATABASE $DB_NAME TO $DB_USER;
EOF
fi
log_success "Database created successfully"

# テーブル作成
log_step "[4/6] Creating tables"
log_info "Creating tables..."

export PGPASSWORD="$DB_PASSWORD"
if [ -f "$SCRIPT_DIR/../database/schema/create_tables.sql" ]; then
    psql -U "$DB_USER" -d "$DB_NAME" -h localhost -f "$SCRIPT_DIR/../database/schema/create_tables.sql" > /dev/null
    log_success "Tables created successfully"
else
    log_error "Table creation script not found: $SCRIPT_DIR/../database/schema/create_tables.sql"
    exit 1
fi

# サンプルデータ投入
log_step "[5/6] Inserting sample data"
log_info "Inserting sample data..."

if [ -f "$SCRIPT_DIR/../database/seed/insert_sample_data.sql" ]; then
    if psql -U "$DB_USER" -d "$DB_NAME" -h localhost -f "$SCRIPT_DIR/../database/seed/insert_sample_data.sql" > /dev/null 2>&1; then
        log_success "Sample data inserted successfully"
    else
        log_warning "Failed to insert some sample data (skipped)"
    fi
else
    log_warning "Sample data file not found (skipped)"
fi

# 接続テスト
log_step "[6/6] Testing database connection"
log_info "Running connection test..."

psql -U "$DB_USER" -d "$DB_NAME" -h localhost << EOF > /dev/null
-- テーブル存在確認
SELECT COUNT(*) FROM information_schema.tables
WHERE table_schema = 'public'
AND table_name LIKE 'stocks_%';
EOF

log_success "Connection test passed"

# パスワード環境変数をクリア
unset PGPASSWORD

# 完了メッセージ
echo
echo "========================================="
echo "  Database Reset Completed!"
echo "========================================="
echo
echo "Database Information:"
echo "  Database Name: $DB_NAME"
echo "  User: $DB_USER"
echo "  Host: localhost"
echo "  Port: 5432"
echo
echo "Connection Command:"
echo "  psql -U $DB_USER -d $DB_NAME -h localhost"
echo
echo "Created Tables:"
psql -U "$DB_USER" -d "$DB_NAME" -h localhost << EOF
\dt
EOF
echo
log_success "Reset process completed successfully!"
echo
