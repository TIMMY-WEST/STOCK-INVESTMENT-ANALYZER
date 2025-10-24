#!/bin/bash
# =============================================================================
# STOCK-INVESTMENT-ANALYZER - Development Environment Setup Script
# Linux/macOS用開発環境自動セットアップスクリプト
# =============================================================================

# エラー発生時は即座に終了
set -e

# カラー定義
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# プロジェクトルートディレクトリ
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Python関連設定
PYTHON_CMD="python3"
VENV_DIR="$PROJECT_ROOT/venv"
REQUIREMENTS_FILE="$PROJECT_ROOT/requirements.txt"
REQUIREMENTS_DEV_FILE="$PROJECT_ROOT/requirements-dev.txt"

# 環境変数ファイル
ENV_EXAMPLE="$PROJECT_ROOT/.env.example"
ENV_FILE="$PROJECT_ROOT/.env"

# =============================================================================
# ログ関数
# =============================================================================

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
    echo -e "${CYAN}[$1]${NC} $2"
}

print_separator() {
    echo "========================================"
}

# =============================================================================
# エラーハンドリング
# =============================================================================

error_exit() {
    log_error "$1"
    echo ""
    log_error "Setup failed"
    log_info "See docs/development/troubleshooting.md for troubleshooting information"
    exit 1
}

# トラップでエラーキャッチ
trap 'error_exit "Unexpected error occurred (line: $LINENO)"' ERR

# =============================================================================
# メイン処理開始
# =============================================================================

echo ""
print_separator
echo -e "${BLUE}STOCK-INVESTMENT-ANALYZER${NC}"
echo -e "${BLUE}Development Environment Setup${NC}"
print_separator
echo ""

log_info "Starting setup (estimated time: 5-15 minutes)"
echo ""

# =============================================================================
# ステップ1: 前提条件チェック
# =============================================================================

log_step "1/7" "Checking prerequisites..."

# Python バージョンチェック
if ! command -v $PYTHON_CMD &> /dev/null; then
    error_exit "Python 3 not found. Please install Python 3.8 or higher"
fi

PYTHON_VERSION=$($PYTHON_CMD --version 2>&1 | awk '{print $2}')
log_info "Python version: $PYTHON_VERSION"

# Python バージョンが3.8以上かチェック
PYTHON_MAJOR=$($PYTHON_CMD -c 'import sys; print(sys.version_info.major)')
PYTHON_MINOR=$($PYTHON_CMD -c 'import sys; print(sys.version_info.minor)')

if [ "$PYTHON_MAJOR" -lt 3 ] || ([ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -lt 8 ]); then
    error_exit "Python 3.8 or higher is required (current: $PYTHON_VERSION)"
fi

# Git チェック
if ! command -v git &> /dev/null; then
    log_warning "Git not found (optional)"
else
    log_info "Git version: $(git --version | awk '{print $3}')"
fi

# PostgreSQL チェック
if ! command -v psql &> /dev/null; then
    log_warning "PostgreSQL not found"
    log_warning "You can continue if you want to skip database setup"
    read -p "Continue anyway? [y/N]: " continue_without_pg
    if [ "$continue_without_pg" != "y" ] && [ "$continue_without_pg" != "Y" ]; then
        error_exit "Please install PostgreSQL and try again"
    fi
    SKIP_DB_SETUP=true
else
    log_info "PostgreSQL found"
    SKIP_DB_SETUP=false
fi

log_success "Prerequisites check completed"
echo ""

# =============================================================================
# ステップ2: 環境変数ファイルの設定
# =============================================================================

log_step "2/7" "Setting up environment file..."

if [ -f "$ENV_FILE" ]; then
    log_warning ".env file already exists"
    read -p "Overwrite? [y/N]: " overwrite_env
    if [ "$overwrite_env" = "y" ] || [ "$overwrite_env" = "Y" ]; then
        cp "$ENV_EXAMPLE" "$ENV_FILE"
        log_success ".env file has been overwritten"
    else
        log_info "Using existing .env file"
    fi
else
    if [ -f "$ENV_EXAMPLE" ]; then
        cp "$ENV_EXAMPLE" "$ENV_FILE"
        log_success ".env file created"
    else
        log_warning ".env.example not found. Please create .env manually"
    fi
fi

echo ""

# =============================================================================
# ステップ3: Python仮想環境の作成
# =============================================================================

log_step "3/7" "Creating Python virtual environment..."

if [ -d "$VENV_DIR" ]; then
    log_warning "Virtual environment already exists"
    read -p "Recreate? [y/N]: " recreate_venv
    if [ "$recreate_venv" = "y" ] || [ "$recreate_venv" = "Y" ]; then
        log_info "Removing existing virtual environment..."
        rm -rf "$VENV_DIR"
        $PYTHON_CMD -m venv "$VENV_DIR"
        log_success "Virtual environment recreated"
    else
        log_info "Using existing virtual environment"
    fi
else
    $PYTHON_CMD -m venv "$VENV_DIR"
    log_success "Virtual environment created"
fi

# 仮想環境の有効化
source "$VENV_DIR/bin/activate"
log_info "Virtual environment activated"

echo ""

# =============================================================================
# ステップ4: pip のアップグレード
# =============================================================================

log_step "4/7" "Upgrading pip..."

pip install --upgrade pip > /dev/null 2>&1
log_success "pip upgraded ($(pip --version | awk '{print $2}'))"

echo ""

# =============================================================================
# ステップ5: 依存関係のインストール
# =============================================================================

log_step "5/7" "Installing dependencies..."

if [ ! -f "$REQUIREMENTS_FILE" ]; then
    error_exit "requirements.txt not found"
fi

log_info "Installing production dependencies..."
pip install -r "$REQUIREMENTS_FILE"
log_success "Production dependencies installed"

if [ -f "$REQUIREMENTS_DEV_FILE" ]; then
    log_info "Installing development dependencies..."
    pip install -r "$REQUIREMENTS_DEV_FILE"
    log_success "Development dependencies installed"
else
    log_warning "requirements-dev.txt not found (skipped)"
fi

echo ""

# =============================================================================
# ステップ6: データベースセットアップ
# =============================================================================

log_step "6/7" "Setting up database..."

if [ "$SKIP_DB_SETUP" = true ]; then
    log_warning "Skipping database setup (PostgreSQL not found)"
else
    read -p "Run database setup? [Y/n]: " setup_db
    if [ "$setup_db" != "n" ] && [ "$setup_db" != "N" ]; then
        DB_SETUP_SCRIPT="$SCRIPT_DIR/setup_db.sh"
        if [ -f "$DB_SETUP_SCRIPT" ]; then
            log_info "Running database setup script..."
            chmod +x "$DB_SETUP_SCRIPT"

            # setup_db.sh を実行
            if "$DB_SETUP_SCRIPT"; then
                log_success "Database setup completed"
            else
                log_warning "Database setup failed"
                log_info "You can run it manually later: ./scripts/setup/setup_db.sh"
            fi
        else
            log_warning "Database setup script not found"
            log_info "You can run it manually later: ./scripts/setup/setup_db.sh"
        fi
    else
        log_info "Database setup skipped"
        log_info "Run it later: ./scripts/setup/setup_db.sh or make db-setup"
    fi
fi

echo ""

# =============================================================================
# ステップ7: セットアップの検証
# =============================================================================

log_step "7/7" "Verifying setup..."

# Pythonパッケージの確認
log_info "Installed packages: $(pip list | wc -l)"

# 重要なパッケージのバージョン確認
FLASK_VERSION=$(python -c "import flask; print(flask.__version__)" 2>/dev/null || echo "not installed")
SQLALCHEMY_VERSION=$(python -c "import sqlalchemy; print(sqlalchemy.__version__)" 2>/dev/null || echo "not installed")

log_info "Flask: $FLASK_VERSION"
log_info "SQLAlchemy: $SQLALCHEMY_VERSION"

# .envファイルの確認
if [ -f "$ENV_FILE" ]; then
    log_success ".env file: exists"
else
    log_warning ".env file: not created"
fi

log_success "Setup verification completed"

echo ""

# =============================================================================
# セットアップ完了
# =============================================================================

print_separator
echo -e "${GREEN}Setup completed successfully!${NC}"
print_separator
echo ""

log_info "Next steps:"
echo ""
echo "  1. Review/edit environment variables"
echo "     $ vi .env"
echo ""
echo "  2. Activate virtual environment"
echo "     $ source venv/bin/activate"
echo ""
echo "  3. Start application"
echo "     $ cd app && python app.py"
echo "     or"
echo "     $ make run"
echo ""
echo "  4. Access in browser"
echo "     http://localhost:8000"
echo ""

log_info "Other useful commands:"
echo "  - make help       : List available commands"
echo "  - make test       : Run tests"
echo "  - make db-reset   : Reset database"
echo "  - make clean      : Clear caches"
echo ""

log_info "Documentation:"
echo "  - README.md"
echo "  - docs/development/github_workflow.md"
echo "  - docs/development/troubleshooting.md"
echo ""

print_separator
echo -e "${GREEN}Happy coding!${NC}"
print_separator
echo ""
