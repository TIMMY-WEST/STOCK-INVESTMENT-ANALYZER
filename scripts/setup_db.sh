#!/bin/bash
# =============================================================================
# PostgreSQL データベースセットアップ用Linuxシェルスクリプト
# 株価データ取得システム用データベース自動構築スクリプト
# =============================================================================

# エラー発生時の処理
set -e

# カラー定義
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 設定値
DB_NAME="stock_data_system"
DB_USER="stock_user"
DB_PASSWORD="stock_password"
POSTGRES_USER="postgres"

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

# スクリプト開始
echo "========================================"
echo "PostgreSQL データベースセットアップ開始"
echo "========================================"
echo

# PostgreSQLがインストールされているかチェック
log_info "[1/6] PostgreSQL インストール確認中..."
if ! command -v psql &> /dev/null; then
    log_error "PostgreSQLがインストールされていません"
    echo "PostgreSQLをインストールしてから再実行してください"
    echo
    echo "Ubuntuの場合:"
    echo "  sudo apt update"
    echo "  sudo apt install postgresql postgresql-contrib"
    echo
    echo "macOSの場合:"
    echo "  brew install postgresql"
    echo
    exit 1
fi
log_success "PostgreSQL が見つかりました"

# PostgreSQLサービス開始確認
log_info "[2/6] PostgreSQL サービス状態確認中..."
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    # Linux
    if ! systemctl is-active --quiet postgresql; then
        log_warning "PostgreSQLサービスが開始されていません"
        log_info "サービスを開始しています..."
        sudo systemctl start postgresql
        sudo systemctl enable postgresql
    fi
elif [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS
    if ! brew services list | grep postgresql | grep started > /dev/null; then
        log_warning "PostgreSQLサービスが開始されていません"
        log_info "サービスを開始しています..."
        brew services start postgresql
    fi
fi
log_success "PostgreSQL サービスは稼働中です"

# スクリプトディレクトリ取得
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

# データベース作成
log_info "[3/6] データベース作成中..."
log_info "パスワードの入力を求められたら $POSTGRES_USER ユーザーのパスワードを入力してください"

# PostgreSQL接続テスト
if ! psql -U "$POSTGRES_USER" -h localhost -c "SELECT 1;" > /dev/null 2>&1; then
    log_error "postgres ユーザーでの接続に失敗しました"
    echo "PostgreSQLの設定を確認してください"
    exit 1
fi

# データベース作成スクリプト実行
log_info "データベース作成スクリプト実行中..."
psql -U "$POSTGRES_USER" -h localhost -f "$SCRIPT_DIR/create_database.sql"
log_success "データベース作成完了"

# テーブル作成
log_info "[4/6] テーブル作成中..."
log_info "パスワードの入力を求められたら '$DB_PASSWORD' を入力してください"

# PGPASSWORD環境変数でパスワードを設定（非対話的実行）
export PGPASSWORD="$DB_PASSWORD"
psql -U "$DB_USER" -d "$DB_NAME" -h localhost -f "$SCRIPT_DIR/create_tables.sql"
log_success "テーブル作成完了"

# サンプルデータ投入
log_info "[5/6] 初期データ投入中..."
if [ -f "$SCRIPT_DIR/insert_sample_data.sql" ]; then
    if psql -U "$DB_USER" -d "$DB_NAME" -h localhost -f "$SCRIPT_DIR/insert_sample_data.sql"; then
        log_success "サンプルデータ投入完了"
    else
        log_warning "サンプルデータ投入に一部失敗しました"
    fi
else
    log_warning "サンプルデータファイルが見つかりません（スキップ）"
fi

# 接続テスト
log_info "[6/6] データベース接続テスト中..."
psql -U "$DB_USER" -d "$DB_NAME" -h localhost -c "\dt"

echo
echo "========================================"
echo "データベースセットアップ完了！"
echo "========================================"
echo
echo "データベース情報:"
echo "  データベース名: $DB_NAME"
echo "  ユーザー名: $DB_USER"
echo "  パスワード: $DB_PASSWORD"
echo "  ホスト: localhost"
echo "  ポート: 5432"
echo
echo "接続コマンド例:"
echo "  psql -U $DB_USER -d $DB_NAME -h localhost"
echo

# .envファイル作成確認
ENV_FILE="$SCRIPT_DIR/../.env"
if [ ! -f "$ENV_FILE" ]; then
    echo ".env ファイルがありません。作成しますか？ [y/N]"
    read -r response
    if [[ "$response" =~ ^([yY][eE][sS]|[yY])$ ]]; then
        cat > "$ENV_FILE" << EOF
# データベース設定
DB_HOST=localhost
DB_PORT=5432
DB_NAME=$DB_NAME
DB_USER=$DB_USER
DB_PASSWORD=$DB_PASSWORD

# アプリケーション設定
FLASK_ENV=development
FLASK_DEBUG=True
FLASK_PORT=8000
EOF
        log_success ".env ファイルを作成しました"
    fi
fi

# パスワード環境変数をクリア
unset PGPASSWORD

log_success "セットアップが完了しました！"

echo
echo "次の手順:"
echo "1. Python仮想環境を有効化してください"
echo "   source venv/bin/activate"
echo "2. アプリケーションを起動してください"
echo "   cd app && python app.py"
echo