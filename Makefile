# =============================================================================
# STOCK-INVESTMENT-ANALYZER - Makefile
# Development Environment Setup and Common Commands
# =============================================================================

.PHONY: help setup clean test run install db-setup db-reset format lint

# デフォルトターゲット
.DEFAULT_GOAL := help

# 環境変数
PYTHON := python3
VENV := venv
VENV_BIN := $(VENV)/bin
PIP := $(VENV_BIN)/pip
PYTEST := $(VENV_BIN)/pytest
FLASK := $(VENV_BIN)/python

# カラー出力
BLUE := \033[0;34m
GREEN := \033[0;32m
YELLOW := \033[1;33m
NC := \033[0m

# =============================================================================
# メインコマンド
# =============================================================================

## setup: 開発環境の完全セットアップ（推奨）
setup:
	@echo "$(BLUE)========================================$(NC)"
	@echo "$(BLUE)開発環境セットアップを開始します$(NC)"
	@echo "$(BLUE)========================================$(NC)"
	@chmod +x scripts/setup/dev_setup.sh
	@./scripts/setup/dev_setup.sh

## install: Python依存関係のみインストール
install: venv
	@echo "$(BLUE)[INFO]$(NC) 依存関係をインストール中..."
	@$(PIP) install --upgrade pip
	@$(PIP) install -r requirements.txt
	@if [ -f requirements-dev.txt ]; then \
		$(PIP) install -r requirements-dev.txt; \
	fi
	@echo "$(GREEN)[SUCCESS]$(NC) 依存関係のインストールが完了しました"

## venv: Python仮想環境の作成
venv:
	@if [ ! -d "$(VENV)" ]; then \
		echo "$(BLUE)[INFO]$(NC) 仮想環境を作成中..."; \
		$(PYTHON) -m venv $(VENV); \
		echo "$(GREEN)[SUCCESS]$(NC) 仮想環境が作成されました"; \
	else \
		echo "$(YELLOW)[INFO]$(NC) 仮想環境は既に存在します"; \
	fi

# =============================================================================
# データベース管理
# =============================================================================

## db-setup: データベースのセットアップ
db-setup:
	@echo "$(BLUE)[INFO]$(NC) データベースをセットアップ中..."
	@chmod +x scripts/setup/setup_db.sh
	@./scripts/setup/setup_db.sh

## db-reset: データベースのリセット（注意: 全データ削除）
db-reset:
	@echo "$(YELLOW)[WARNING]$(NC) データベースをリセットします（全データが削除されます）"
	@read -p "続行しますか? [y/N]: " confirm; \
	if [ "$$confirm" = "y" ] || [ "$$confirm" = "Y" ]; then \
		echo "$(BLUE)[INFO]$(NC) データベースをリセット中..."; \
		chmod +x scripts/setup/setup_db.sh; \
		./scripts/setup/setup_db.sh; \
		echo "$(GREEN)[SUCCESS]$(NC) データベースがリセットされました"; \
	else \
		echo "$(YELLOW)[INFO]$(NC) キャンセルされました"; \
	fi

# =============================================================================
# アプリケーション実行
# =============================================================================

## run: アプリケーションの起動
run:
	@if [ ! -d "$(VENV)" ]; then \
		echo "$(YELLOW)[WARNING]$(NC) 仮想環境が見つかりません。先に 'make setup' を実行してください"; \
		exit 1; \
	fi
	@echo "$(BLUE)[INFO]$(NC) アプリケーションを起動中..."
	@cd app && $(FLASK) app.py

# =============================================================================
# テスト
# =============================================================================

## test: 全テストの実行
test:
	@if [ ! -d "$(VENV)" ]; then \
		echo "$(YELLOW)[WARNING]$(NC) 仮想環境が見つかりません。先に 'make setup' を実行してください"; \
		exit 1; \
	fi
	@echo "$(BLUE)[INFO]$(NC) テストを実行中..."
	@$(PYTEST) tests/ -v

## test-cov: カバレッジ付きテスト実行
test-cov:
	@if [ ! -d "$(VENV)" ]; then \
		echo "$(YELLOW)[WARNING]$(NC) 仮想環境が見つかりません。先に 'make setup' を実行してください"; \
		exit 1; \
	fi
	@echo "$(BLUE)[INFO]$(NC) カバレッジ付きテストを実行中..."
	@$(PYTEST) tests/ --cov=app --cov-report=html --cov-report=term

# =============================================================================
# コード品質
# =============================================================================

## format: コードフォーマット（black + isort）
format:
	@if [ ! -d "$(VENV)" ]; then \
		echo "$(YELLOW)[WARNING]$(NC) 仮想環境が見つかりません。先に 'make setup' を実行してください"; \
		exit 1; \
	fi
	@echo "$(BLUE)[INFO]$(NC) コードをフォーマット中..."
	@$(VENV_BIN)/black app/ tests/ --line-length 79
	@$(VENV_BIN)/isort app/ tests/
	@echo "$(GREEN)[SUCCESS]$(NC) フォーマットが完了しました"

## lint: コードチェック（flake8 + mypy）
lint:
	@if [ ! -d "$(VENV)" ]; then \
		echo "$(YELLOW)[WARNING]$(NC) 仮想環境が見つかりません。先に 'make setup' を実行してください"; \
		exit 1; \
	fi
	@echo "$(BLUE)[INFO]$(NC) コードをチェック中..."
	@$(VENV_BIN)/flake8 app/ tests/
	@$(VENV_BIN)/mypy app/ --exclude tests/
	@echo "$(GREEN)[SUCCESS]$(NC) コードチェックが完了しました"

# =============================================================================
# クリーンアップ
# =============================================================================

## clean: キャッシュファイルと一時ファイルの削除
clean:
	@echo "$(BLUE)[INFO]$(NC) クリーンアップ中..."
	@find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true
	@find . -type f -name "*.pyc" -delete 2>/dev/null || true
	@find . -type f -name "*.pyo" -delete 2>/dev/null || true
	@rm -rf .coverage htmlcov/ 2>/dev/null || true
	@echo "$(GREEN)[SUCCESS]$(NC) クリーンアップが完了しました"

## clean-all: 全ての生成ファイルを削除（仮想環境含む）
clean-all: clean
	@echo "$(YELLOW)[WARNING]$(NC) 仮想環境を含む全てのファイルを削除します"
	@read -p "続行しますか? [y/N]: " confirm; \
	if [ "$$confirm" = "y" ] || [ "$$confirm" = "Y" ]; then \
		echo "$(BLUE)[INFO]$(NC) 仮想環境を削除中..."; \
		rm -rf $(VENV); \
		echo "$(GREEN)[SUCCESS]$(NC) 全てのファイルが削除されました"; \
	else \
		echo "$(YELLOW)[INFO]$(NC) キャンセルされました"; \
	fi

# =============================================================================
# ヘルプ
# =============================================================================

## help: 使用可能なコマンドの一覧表示
help:
	@echo "$(BLUE)========================================$(NC)"
	@echo "$(BLUE)STOCK-INVESTMENT-ANALYZER - Makefile$(NC)"
	@echo "$(BLUE)========================================$(NC)"
	@echo ""
	@echo "$(GREEN)使用可能なコマンド:$(NC)"
	@echo ""
	@sed -n 's/^##//p' $(MAKEFILE_LIST) | column -t -s ':' | sed -e 's/^/ /'
	@echo ""
	@echo "$(BLUE)クイックスタート:$(NC)"
	@echo "  1. $(GREEN)make setup$(NC)    - 開発環境の完全セットアップ"
	@echo "  2. $(GREEN)make run$(NC)      - アプリケーションの起動"
	@echo "  3. $(GREEN)make test$(NC)     - テストの実行"
	@echo ""
	@echo "$(BLUE)詳細情報:$(NC)"
	@echo "  - README.md"
	@echo "  - docs/development/github_workflow.md"
	@echo ""
