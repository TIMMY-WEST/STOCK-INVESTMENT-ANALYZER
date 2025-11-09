---
category: task_planning
type: refactoring_plan
phase: Phase 3
ai_context: critical
status: planning
priority: medium
last_updated: 2025-01-09
planned_start: 2025-05-12
planned_end: 2025-05-18
duration: 1 week
dependencies:
  - Phase 2: API層リファクタリング完了
related_docs:
  - ./refactoring_plan.md
  - ../../architecture/layers/presentation_layer.md
  - ./api_layer_plan.md
  - ../../architecture/architecture_overview.md
  - ../../guides/CONTRIBUTING.md
---

# 【Phase 3 計画書】プレゼンテーション層リファクタリング

> **📋 ドキュメント種別**: リファクタリング詳細計画書
> **🎯 Phase**: Phase 3
> **📅 実施期間**: 2025年5月12日 ～ 2025年5月18日（1週間）
> **👥 対象読者**: フロントエンド開発者、アプリケーション設定担当者
> **⚠️ 優先度**: 🟡 Medium
> **⚡ 依存関係**: Phase 2（API層）完了後に開始

## 目次

- [1. 概要](#1-概要)
- [2. 現状の問題点](#2-現状の問題点)
- [3. Application Factory パターンとは](#3-application-factory-パターンとは)
- [4. リファクタリング設計](#4-リファクタリング設計)
- [5. クラス図](#5-クラス図)
- [6. シーケンス図](#6-シーケンス図)
- [7. ディレクトリ構造](#7-ディレクトリ構造)
- [8. 実装詳細](#8-実装詳細)
- [9. 移行計画](#9-移行計画)
- [10. メリット・デメリット](#10-メリットデメリット)

---

## 1. 概要

### 目的

現在の[app/app.py](../../app/app.py)をApplication Factoryパターンにリファクタリングし、以下を実現します:

- **テスタビリティの向上**: 異なる設定でアプリインスタンスを生成可能
- **環境分離**: 開発/テスト/本番環境の設定を明確に分離
- **モジュール性の向上**: 初期化ロジックの関心分離
- **拡張性の向上**: Blueprint登録や設定の柔軟な管理

### スコープ

- `app.py` を複数モジュールに分割
- `create_app()` ファクトリ関数の実装
- 設定管理の抽象化
- 既存機能の完全な互換性維持

---

## 2. 現状の問題点

### 現在の実装（app.py）

```python
# グローバルスコープでインスタンス生成
app = Flask(__name__)
socketio = SocketIO(app)

# モジュールレベルで初期化
Base.metadata.create_all(bind=engine)

# 直接Blueprint登録
app.register_blueprint(bulk_api)
app.register_blueprint(stock_master_api)
# ...

if __name__ == "__main__":
    socketio.run(app, ...)
```

### 問題点

| 問題 | 影響 | 深刻度 |
|------|------|--------|
| **グローバルなapp インスタンス** | テスト時に異なる設定のappを作成できない | 高 |
| **循環インポートのリスク** | モジュール間の依存関係が複雑化 | 中 |
| **設定の硬直性** | 環境ごとの設定変更が困難 | 中 |
| **初期化ロジックの分散** | app.pyが肥大化し保守性が低下 | 中 |
| **再利用性の欠如** | 複数のappインスタンスを生成できない | 低 |

---

## 3. Application Factory パターンとは

### 定義

アプリケーションインスタンスを返す関数（ファクトリ）を定義し、実行時に動的にアプリを生成するデザインパターン。

### 基本構造

```python
def create_app(config_name='default'):
    """アプリケーションファクトリ関数"""
    app = Flask(__name__)

    # 設定読み込み
    app.config.from_object(config[config_name])

    # 拡張機能初期化
    init_extensions(app)

    # Blueprint登録
    register_blueprints(app)

    return app
```

### Flaskベストプラクティス

Flask公式ドキュメントでも推奨されているパターン:
- [Application Factories](https://flask.palletsprojects.com/en/3.0.x/patterns/appfactories/)
- [Testing Flask Applications](https://flask.palletsprojects.com/en/3.0.x/testing/)

---

## 4. リファクタリング設計

### 設計方針

1. **段階的移行**: 既存機能を壊さず段階的にリファクタリング
2. **後方互換性**: 既存のエンドポイントは全て維持
3. **シンプル優先**: 過度な抽象化は避ける
4. **テスト可能性**: ユニットテスト・統合テストが容易に

### アーキテクチャ概要

```
app/
├── __init__.py              # create_app() 定義（ファクトリ）
├── config.py                # 設定クラス（開発/テスト/本番）
├── extensions.py            # 拡張機能インスタンス（db, socketio等）
├── routes/                  # ルート定義（分離）
│   ├── __init__.py
│   ├── main.py              # メインページルート
│   ├── stocks.py            # 株価データCRUD
│   └── websocket.py         # WebSocketイベント
├── api/                     # 既存API Blueprint（変更なし）
├── services/                # 既存サービス（変更なし）
└── app.py                   # エントリーポイント（最小限）
```

---

## 5. クラス図

### リファクタリング後のクラス構成

```mermaid
classDiagram
    class AppFactory {
        +create_app(config_name: str) Flask
        -init_extensions(app: Flask)
        -register_blueprints(app: Flask)
        -register_routes(app: Flask)
        -register_error_handlers(app: Flask)
    }

    class Config {
        <<abstract>>
        +SECRET_KEY: str
        +SQLALCHEMY_DATABASE_URI: str
        +API_DEFAULT_VERSION: str
        +init_app(app: Flask)
    }

    class DevelopmentConfig {
        +DEBUG: bool = True
        +TESTING: bool = False
    }

    class TestingConfig {
        +DEBUG: bool = False
        +TESTING: bool = True
        +SQLALCHEMY_DATABASE_URI: str
    }

    class ProductionConfig {
        +DEBUG: bool = False
        +TESTING: bool = False
        +SSL_REQUIRED: bool = True
    }

    class Extensions {
        +db: SQLAlchemy
        +socketio: SocketIO
        +migrate: Migrate
        +init_app(app: Flask)
    }

    class BlueprintRegistry {
        +bulk_api: Blueprint
        +stock_master_api: Blueprint
        +system_api: Blueprint
        +swagger_bp: Blueprint
        +register_all(app: Flask)
    }

    class RouteRegistry {
        +main_routes: Blueprint
        +stock_routes: Blueprint
        +websocket_handlers: module
        +register_all(app: Flask)
    }

    AppFactory --> Config : uses
    AppFactory --> Extensions : initializes
    AppFactory --> BlueprintRegistry : registers
    AppFactory --> RouteRegistry : registers
    Config <|-- DevelopmentConfig : inherits
    Config <|-- TestingConfig : inherits
    Config <|-- ProductionConfig : inherits
```

### モジュール依存関係図

```mermaid
graph TB
    subgraph "エントリーポイント"
        AppPy[app.py]
    end

    subgraph "ファクトリ層"
        Init[__init__.py<br/>create_app]
    end

    subgraph "設定層"
        Config[config.py<br/>Config Classes]
    end

    subgraph "拡張機能層"
        Ext[extensions.py<br/>db, socketio]
    end

    subgraph "ルーティング層"
        Routes[routes/<br/>main, stocks, websocket]
        API[api/<br/>blueprints]
    end

    subgraph "サービス層"
        Services[services/<br/>business logic]
    end

    subgraph "データ層"
        Models[models.py]
    end

    AppPy --> Init
    Init --> Config
    Init --> Ext
    Init --> Routes
    Init --> API
    Routes --> Services
    API --> Services
    Services --> Models
    Ext --> Models

    style Init fill:#e1f5ff
    style Config fill:#fff4e1
    style Ext fill:#e1ffe1
```

---

## 6. シーケンス図

### アプリケーション起動シーケンス

```mermaid
sequenceDiagram
    participant Main as app.py
    participant Factory as create_app()
    participant Config as Config
    participant Ext as Extensions
    participant BP as Blueprints
    participant Routes as Routes
    participant DB as Database

    Main->>Factory: create_app('development')

    Factory->>Config: load_config('development')
    Config-->>Factory: DevelopmentConfig

    Factory->>Factory: app = Flask(__name__)
    Factory->>Factory: app.config.from_object(config)

    Factory->>Ext: init_extensions(app)
    Ext->>Ext: db.init_app(app)
    Ext->>Ext: socketio.init_app(app)
    Ext->>Ext: migrate.init_app(app, db)
    Ext-->>Factory: Extensions initialized

    Factory->>DB: db.create_all()
    DB-->>Factory: Tables created

    Factory->>BP: register_blueprints(app)
    BP->>BP: app.register_blueprint(bulk_api_v1)
    BP->>BP: app.register_blueprint(stock_master_api_v1)
    BP->>BP: app.register_blueprint(system_api_v1)
    BP->>BP: app.register_blueprint(swagger_bp)
    BP-->>Factory: Blueprints registered

    Factory->>Routes: register_routes(app)
    Routes->>Routes: app.register_blueprint(main_bp)
    Routes->>Routes: app.register_blueprint(stock_bp)
    Routes->>Routes: register_websocket_handlers(socketio)
    Routes-->>Factory: Routes registered

    Factory->>Factory: register_error_handlers(app)

    Factory-->>Main: app instance
    Main->>Main: socketio.run(app)
```

### テスト環境でのアプリ生成

```mermaid
sequenceDiagram
    participant Test as test_*.py
    participant Factory as create_app()
    participant Config as TestingConfig
    participant Ext as Extensions
    participant DB as Test Database

    Test->>Factory: create_app('testing')

    Factory->>Config: load_config('testing')
    Config-->>Factory: TestingConfig
    Note over Config: TESTING=True<br/>DATABASE_URI=sqlite:///:memory:

    Factory->>Factory: app = Flask(__name__)
    Factory->>Ext: init_extensions(app)
    Ext->>DB: Connect to in-memory DB
    DB-->>Ext: Connection established

    Factory->>Factory: Register minimal blueprints
    Factory-->>Test: test_app instance

    Test->>Test: with app.test_client() as client
    Test->>Test: Run tests

    Test->>DB: db.drop_all()
    DB-->>Test: Database cleaned
```

### 複数環境での起動シーケンス比較

```mermaid
sequenceDiagram
    participant Dev as 開発環境
    participant Prod as 本番環境
    participant Factory as create_app()

    rect rgb(200, 230, 255)
        Note over Dev: 開発環境起動
        Dev->>Factory: create_app('development')
        Factory-->>Dev: app (DEBUG=True, sqlite)
    end

    rect rgb(255, 230, 200)
        Note over Prod: 本番環境起動
        Prod->>Factory: create_app('production')
        Factory-->>Prod: app (DEBUG=False, PostgreSQL)
    end
```

---

## 7. ディレクトリ構造

### リファクタリング前

```
app/
├── app.py                   # 857行（全てが1ファイル）
├── models.py
├── api/
│   ├── bulk_data.py
│   ├── stock_master.py
│   └── system_monitoring.py
├── services/
└── utils/
```

### リファクタリング後

```
app/
├── __init__.py              # create_app() 定義（約100行）
├── config.py                # 設定クラス（約150行）
├── extensions.py            # 拡張機能初期化（約50行）
├── app.py                   # エントリーポイント（約20行）
├── models.py                # 変更なし
│
├── routes/                  # 新規ディレクトリ
│   ├── __init__.py
│   ├── main.py              # メインページルート（約30行）
│   ├── stocks.py            # 株価CRUD（約400行）
│   └── websocket.py         # WebSocketイベント（約30行）
│
├── api/                     # 既存（変更なし）
│   ├── __init__.py
│   ├── bulk_data.py
│   ├── stock_master.py
│   └── system_monitoring.py
│
├── middleware/              # 既存（変更なし）
│   └── versioning.py
│
├── services/                # 既存（変更なし）
│   ├── stock_data/
│   ├── bulk/
│   └── jpx/
│
├── utils/                   # 既存（変更なし）
│   ├── api_response.py
│   └── timeframe_utils.py
│
├── static/                  # 既存（変更なし）
└── templates/               # 既存（変更なし）
```

---

## 8. 実装詳細

### 8.1 ファクトリ関数（app/__init__.py）

```python
"""Application factory for Flask app.

This module provides the create_app factory function that creates
and configures the Flask application instance.
"""

from flask import Flask
from flask_socketio import SocketIO

from app.config import config
from app.extensions import db, socketio, migrate, init_extensions
from app.api import bulk_api, stock_master_api, system_api
from app.api.swagger import swagger_bp
from app.routes import register_routes
from app.routes.websocket import register_websocket_handlers


def create_app(config_name='default'):
    """Application factory pattern.

    Args:
        config_name: Configuration name ('development', 'testing', 'production')

    Returns:
        Flask application instance
    """
    app = Flask(__name__)

    # 設定読み込み
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)

    # 拡張機能初期化
    init_extensions(app)

    # データベーステーブル作成
    with app.app_context():
        db.create_all()

    # Blueprint登録
    register_blueprints(app)

    # ルート登録
    register_routes(app)

    # WebSocketハンドラ登録
    register_websocket_handlers(socketio)

    # エラーハンドラ登録
    register_error_handlers(app)

    return app


def register_blueprints(app):
    """Register Flask blueprints."""
    from app.middleware.versioning import (
        create_versioned_blueprint_name,
        create_versioned_url_prefix,
    )
    from flask import Blueprint

    # 既存Blueprint（後方互換性）
    app.register_blueprint(bulk_api)
    app.register_blueprint(stock_master_api)
    app.register_blueprint(system_api)

    # v1 Blueprint
    # ... (既存のv1登録ロジック)

    # Swagger UI
    app.register_blueprint(swagger_bp)


def register_error_handlers(app):
    """Register error handlers."""

    @app.errorhandler(404)
    def not_found(error):
        return {"error": "Not Found"}, 404

    @app.errorhandler(500)
    def internal_error(error):
        return {"error": "Internal Server Error"}, 500
```

### 8.2 設定クラス（app/config.py）

```python
"""Application configuration.

This module defines configuration classes for different environments.
"""

import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    """Base configuration."""

    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')

    # Database
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = False

    # API Versioning
    API_DEFAULT_VERSION = 'v1'
    API_SUPPORTED_VERSIONS = ['v1']

    # Flask-SocketIO
    SOCKETIO_CORS_ALLOWED_ORIGINS = '*'

    @staticmethod
    def init_app(app):
        """Initialize application."""
        pass


class DevelopmentConfig(Config):
    """Development configuration."""

    DEBUG = True
    TESTING = False

    SQLALCHEMY_DATABASE_URI = os.getenv(
        'DATABASE_URL',
        'postgresql://postgres:postgres@localhost:5432/stock_investment'
    )
    SQLALCHEMY_ECHO = True  # SQL出力ON


class TestingConfig(Config):
    """Testing configuration."""

    DEBUG = False
    TESTING = True

    # インメモリSQLiteデータベース
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'

    # WebSocketテスト用
    SOCKETIO_ASYNC_MODE = 'threading'

    @staticmethod
    def init_app(app):
        """Initialize testing environment."""
        # テスト用の追加設定
        app.config['WTF_CSRF_ENABLED'] = False


class ProductionConfig(Config):
    """Production configuration."""

    DEBUG = False
    TESTING = False

    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL')

    # セキュリティ設定
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'

    @staticmethod
    def init_app(app):
        """Initialize production environment."""
        # ログ設定など
        import logging
        from logging.handlers import RotatingFileHandler

        if not os.path.exists('logs'):
            os.mkdir('logs')

        file_handler = RotatingFileHandler(
            'logs/stock_analyzer.log',
            maxBytes=10240000,
            backupCount=10
        )
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s '
            '[in %(pathname)s:%(lineno)d]'
        ))
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)

        app.logger.setLevel(logging.INFO)
        app.logger.info('Stock Analyzer startup')


# 設定辞書
config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
```

### 8.3 拡張機能（app/extensions.py）

```python
"""Flask extensions.

This module initializes Flask extensions that can be used across the application.
"""

from flask_sqlalchemy import SQLAlchemy
from flask_socketio import SocketIO
from flask_migrate import Migrate

# 拡張機能インスタンス（アプリなしで初期化）
db = SQLAlchemy()
socketio = SocketIO()
migrate = Migrate()


def init_extensions(app):
    """Initialize Flask extensions.

    Args:
        app: Flask application instance
    """
    db.init_app(app)
    socketio.init_app(app, cors_allowed_origins=app.config['SOCKETIO_CORS_ALLOWED_ORIGINS'])
    migrate.init_app(app, db)

    # SocketIOをapp.configに格納（後方互換性）
    app.config['SOCKETIO'] = socketio
```

### 8.4 ルート分離（app/routes/main.py）

```python
"""Main page routes.

This module defines routes for main pages (index, websocket test).
"""

from flask import Blueprint, render_template

main_bp = Blueprint('main', __name__)


@main_bp.route('/')
def index():
    """Render the main index page."""
    return render_template('index.html')


@main_bp.route('/websocket-test')
def websocket_test():
    """WebSocket progress test page."""
    return render_template('websocket_test.html')
```

### 8.5 株価データルート（app/routes/stocks.py）

```python
"""Stock data CRUD routes.

This module defines routes for stock data operations.
"""

from datetime import datetime
from flask import Blueprint, request

from app.extensions import db
from app.models import StockDailyCRUD, get_db_session
from app.services.stock_data.orchestrator import StockDataOrchestrator
from app.utils.api_response import APIResponse, ErrorCode
from app.utils.timeframe_utils import (
    get_model_for_interval,
    get_table_name,
    validate_interval,
)

stock_bp = Blueprint('stock', __name__, url_prefix='/api/stocks')


@stock_bp.route('/data', methods=['POST'])
def fetch_data():
    """Fetch stock data for a given symbol and period."""
    # ... (既存のfetch_data実装)
    pass


@stock_bp.route('', methods=['GET'])
def get_stocks():
    """Get stock data with pagination."""
    # ... (既存のget_stocks実装)
    pass


@stock_bp.route('', methods=['POST'])
def create_stock():
    """Create stock data."""
    # ... (既存のcreate_stock実装)
    pass


@stock_bp.route('/<int:stock_id>', methods=['GET'])
def get_stock_by_id(stock_id):
    """Get stock data by ID."""
    # ... (既存のget_stock_by_id実装)
    pass


@stock_bp.route('/<int:stock_id>', methods=['PUT'])
def update_stock(stock_id):
    """Update stock data."""
    # ... (既存のupdate_stock実装)
    pass


@stock_bp.route('/<int:stock_id>', methods=['DELETE'])
def delete_stock(stock_id):
    """Delete stock data."""
    # ... (既存のdelete_stock実装)
    pass


@stock_bp.route('/test', methods=['POST'])
def create_test_data():
    """Create test sample data."""
    # ... (既存のcreate_test_data実装)
    pass
```

### 8.6 WebSocketハンドラ（app/routes/websocket.py）

```python
"""WebSocket event handlers.

This module defines WebSocket event handlers.
"""

from flask import request


def register_websocket_handlers(socketio):
    """Register WebSocket event handlers.

    Args:
        socketio: SocketIO instance
    """

    @socketio.on('connect')
    def handle_connect():
        """Handle client connection."""
        print(f"クライアントが接続しました: {request.sid}")

    @socketio.on('disconnect')
    def handle_disconnect():
        """Handle client disconnection."""
        print(f"クライアントが切断しました: {request.sid}")
```

### 8.7 ルート登録（app/routes/__init__.py）

```python
"""Routes package.

This module registers all route blueprints.
"""

from app.routes.main import main_bp
from app.routes.stocks import stock_bp


def register_routes(app):
    """Register all route blueprints.

    Args:
        app: Flask application instance
    """
    app.register_blueprint(main_bp)
    app.register_blueprint(stock_bp)
```

### 8.8 エントリーポイント（app/app.py）

```python
"""Application entry point.

This module starts the Flask application server.
"""

import os
from app import create_app
from app.extensions import socketio

# 環境変数から設定名を取得（デフォルト: development）
config_name = os.getenv('FLASK_ENV', 'development')

# アプリケーション作成
app = create_app(config_name)

if __name__ == '__main__':
    port = int(os.getenv('FLASK_PORT', 8000))
    host = os.getenv('FLASK_HOST', '127.0.0.1')

    print(f"Starting app in {config_name} mode")
    print(f"http://{host}:{port}/")

    socketio.run(
        app,
        debug=app.config['DEBUG'],
        port=port,
        host=host,
    )
```

---

## 9. 型定義戦略

### 9.1 プロジェクト全体の型定義構造

プレゼンテーション層のリファクタリングにおいても、プロジェクト全体で一貫した**階層的型定義構造**を採用します。

詳細は [型定義配置戦略](../type_definition_strategy.md) を参照してください。

### 9.2 Application Factory パターンでの型使用

**app/config.py での型定義**

```python
"""アプリケーション設定クラス.

環境ごとの設定を型安全に管理します。
"""

from typing import TypedDict, Optional
from enum import Enum


class Environment(str, Enum):
    """環境種別."""
    DEVELOPMENT = "development"
    TESTING = "testing"
    PRODUCTION = "production"


class DatabaseConfig(TypedDict):
    """データベース設定."""
    host: str
    port: int
    name: str
    user: str
    password: str


class Config:
    """基本設定クラス."""

    # 基本設定
    SECRET_KEY: str
    DEBUG: bool = False
    TESTING: bool = False

    # データベース設定
    SQLALCHEMY_DATABASE_URI: str
    SQLALCHEMY_TRACK_MODIFICATIONS: bool = False

    # API設定
    API_DEFAULT_VERSION: str = "v1"
    API_TIMEOUT: int = 30

    @staticmethod
    def init_app(app) -> None:
        """アプリケーション初期化."""
        pass


class DevelopmentConfig(Config):
    """開発環境設定."""
    DEBUG = True
    SQLALCHEMY_ECHO = True


class TestingConfig(Config):
    """テスト環境設定."""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"


class ProductionConfig(Config):
    """本番環境設定."""
    DEBUG = False
    TESTING = False


# 設定マップ
config: dict[Environment, type[Config]] = {
    Environment.DEVELOPMENT: DevelopmentConfig,
    Environment.TESTING: TestingConfig,
    Environment.PRODUCTION: ProductionConfig,
}
```

**app/__init__.py での型使用**

```python
"""アプリケーションファクトリモジュール."""

from typing import Optional
from flask import Flask

from app.config import Config, config, Environment
from app.extensions import init_extensions
from app.routes import register_routes
from app.api import register_blueprints


def create_app(
    config_name: Optional[Environment] = None
) -> Flask:
    """Flask アプリケーションファクトリ.

    Args:
        config_name: 環境設定名（development, testing, production）
                     None の場合は環境変数から取得

    Returns:
        設定済みの Flask アプリケーションインスタンス

    Raises:
        ValueError: 不正な設定名が指定された場合

    Example:
        >>> app = create_app(Environment.DEVELOPMENT)
        >>> app.run()
    """
    app = Flask(__name__)

    # 設定読み込み
    if config_name is None:
        config_name = Environment.DEVELOPMENT

    if config_name not in config:
        raise ValueError(f"Invalid config name: {config_name}")

    app.config.from_object(config[config_name])
    config[config_name].init_app(app)

    # 拡張機能初期化
    init_extensions(app)

    # Blueprint登録
    register_blueprints(app)

    # ルート登録
    register_routes(app)

    return app
```

### 9.3 型定義によるメリット

#### 設定の型安全性

```python
# 型安全な設定アクセス
app = create_app(Environment.DEVELOPMENT)  # OK
app = create_app("invalid")  # ERROR: 型エラー

# IDE補完が効く
env = Environment.PRODUCTION  # IDE が候補を表示
```

#### ドキュメント性の向上

```python
# 関数シグネチャから使い方が明確
def create_app(
    config_name: Optional[Environment] = None
) -> Flask:
    """型ヒントにより引数と戻り値の型が明確."""
    ...
```

---

## 10. 移行計画

### Phase 1: 準備フェーズ（1-2時間）

| タスク | 内容 | 成果物 |
|--------|------|--------|
| 1. 新規ファイル作成 | config.py, extensions.py, __init__.py | 設定基盤 |
| 2. routesディレクトリ作成 | main.py, stocks.py, websocket.py | ルート分離 |
| 3. テストスイート準備 | test_factory.py作成 | テスト基盤 |

### Phase 2: 実装フェーズ（3-4時間）

| タスク | 内容 | 検証方法 |
|--------|------|---------|
| 1. create_app実装 | ファクトリ関数完成 | ユニットテスト |
| 2. ルート移行 | app.py → routes/ | 機能テスト |
| 3. 既存app.py更新 | 最小限のエントリーポイントに | 統合テスト |

### Phase 3: テストフェーズ（2-3時間）

| テスト項目 | 内容 |
|-----------|------|
| ユニットテスト | 各モジュールの単体テスト |
| 統合テスト | API エンドポイントのE2Eテスト |
| WebSocketテスト | リアルタイム通信の動作確認 |
| 負荷テスト | パフォーマンス回帰テスト |

### Phase 4: デプロイフェーズ（1-2時間）

| タスク | 内容 |
|--------|------|
| 1. ドキュメント更新 | README、CONTRIBUTING更新 |
| 2. 環境変数設定 | FLASK_ENV追加 |
| 3. 段階的ロールアウト | 開発→ステージング→本番 |

### ロールバック計画

問題発生時は以下の手順で即座にロールバック:

1. Git revertで前バージョンに戻す
2. 環境変数を元に戻す
3. サーバー再起動

---

## 11. メリット・デメリット

### メリット

| カテゴリ | メリット | 具体例 |
|---------|---------|--------|
| **テスタビリティ** | 異なる設定で複数のappインスタンスを生成可能 | テスト用にインメモリDBを使用 |
| **環境分離** | 開発/テスト/本番の設定を明確に分離 | ProductionConfigでログ設定 |
| **モジュール性** | 関心の分離により保守性向上 | ルートとビジネスロジックの分離 |
| **拡張性** | 新機能追加が容易 | 新しいBlueprintを簡単に追加 |
| **ベストプラクティス** | Flask公式推奨パターンに準拠 | 循環インポート回避 |
| **デバッグ性** | 初期化フローが明確 | エラー箇所の特定が容易 |

### デメリット

| カテゴリ | デメリット | 軽減策 |
|---------|----------|--------|
| **学習コスト** | チームメンバーの学習が必要 | ドキュメント整備、レビュー会実施 |
| **初期工数** | リファクタリングに時間が必要 | 段階的移行、優先度づけ |
| **ファイル数増加** | ディレクトリ構造が複雑化 | 明確な命名規則、README整備 |
| **移行リスク** | 既存機能が一時的に不安定になる可能性 | 十分なテスト、ロールバック計画 |

### ROI（投資対効果）

```
初期投資: 8-12時間
長期効果:
- テスト作成時間: 50%削減
- バグ修正時間: 30%削減
- 新機能開発時間: 20%削減

→ 3ヶ月以内で投資回収可能
```

---

## 11. 参考資料

### Flask公式ドキュメント

- [Application Factories](https://flask.palletsprojects.com/en/3.0.x/patterns/appfactories/)
- [Application Structure](https://flask.palletsprojects.com/en/3.0.x/tutorial/layout/)
- [Testing Flask Applications](https://flask.palletsprojects.com/en/3.0.x/testing/)

### ベストプラクティス

- [The Flask Mega-Tutorial by Miguel Grinberg](https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-xv-a-better-application-structure)
- [Flask Application Factory Pattern](https://hackersandslackers.com/flask-application-factory/)

### 関連ドキュメント

- [プレゼンテーション層仕様書](../layers/presentation_layer.md)
- [アーキテクチャ概要](../architecture_overview.md)
- [コントリビューションガイド](../../guides/CONTRIBUTING.md)

---

**最終更新**: 2025-01-08
**作成者**: Claude Code
**レビュー状態**: Draft
