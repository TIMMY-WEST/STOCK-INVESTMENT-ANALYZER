category: architecture
ai_context: high
last_updated: 2025-11-15
related_docs:
  - ./component_dependency.md
  - ./service_responsibilities.md
  - ./data_flow.md
  - ./database_design.md
  - ../api/api_reference.md
  - ../frontend/frontend_spec.md

# システムアーキテクチャ概要

## 目次

- [1. プロジェクト概要](#1-プロジェクト概要)
- [2. 主要機能一覧](#2-主要機能一覧)
- [3. システム全体像](#3-システム全体像)
- [4. アーキテクチャ構成(4層構造)](#4-アーキテクチャ構成4層構造)
- [5. 技術スタック](#5-技術スタック)
- [6. ディレクトリ構成(4層構造対応)](#6-ディレクトリ構成4層構造対応)

---

## 1. プロジェクト概要

### システムの目的

日本株の投資判断を支援するための株価データ収集・管理・分析システム。Yahoo Finance APIを活用し、JPX上場銘柄(4,000銘柄以上)の株価データを8種類の時間軸で自動取得・蓄積し、ダッシュボード、銘柄検索、スクリーニング、バックテスト等の機能を提供する。

### 解決する課題

| 課題                               | 解決策                                     |
| ---------------------------------- | ------------------------------------------ |
| 手動でのデータ収集には時間がかかる | Yahoo Finance APIとの自動連携              |
| 複数時間軸データの統一管理が困難   | 8種類の時間軸を一元管理するDB設計          |
| 大量銘柄データ取得の非効率性       | 並列処理とバッチ機能による高速化           |
| データ整合性の維持が困難           | PostgreSQLによる堅牢な管理                 |
| 投資判断に必要な情報の分散         | ダッシュボード・銘柄検索・分析ツールの統合 |

### 主な価値

- **時間節約**: 手動収集作業を自動化
- **多角的分析**: 8種類の時間軸(1分足〜月足)で短期〜長期投資に対応
- **スケーラビリティ**: 単一銘柄から全JPX銘柄まで柔軟に対応
- **信頼性**: PostgreSQLとエラーハンドリングによる安定稼働
- **総合的な投資支援**: データ収集から分析、バックテストまで一気通貫

### 設計理念

- **動作優先**: まず動くものを作る
- **シンプル設計**: 複雑さを避ける
- **段階的拡張**: 必要になってから機能追加

---

## 2. 主要機能一覧

frontend_spec.mdに定義された6つの主要機能を実現するためのシステム機能を以下に示します。

### 1. 日本株データのDB格納(データプラットフォーム)

| 機能                           | できること                                                                                                                    | エンドポイント/技術                            | 実装レイヤー                            |
| ------------------------------ | ----------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------- | --------------------------------------- |
| **JPX全銘柄取得**              | 4,000銘柄以上を自動取得<br>バッチ実行履歴の記録                                                                               | 既存: `POST /api/batch/jpx-sequential/start`    | API層<br>サービス層                     |
| **マルチタイムフレーム管理**   | 8種類の時間軸データを自動振り分け<br>(1分足、5分足、15分足、30分足、1時間足、1日足、1週足、1月足)<br>重複チェックとUPSERT操作 | 既存: サービス層(StockDataSaver)               | サービス層<br>データアクセス層          |
| **ファンダメンタルデータ取得** | EPS、BPS、売上、営業利益、純利益、ROE、自己資本比率等の財務指標取得                                                           | `POST /api/fetch-fundamental`<br>※今後実装予定 | API層<br>サービス層<br>データアクセス層 |

### 2. ダッシュボード

| 機能                         | できること                               | エンドポイント/画面                                 | 実装レイヤー                                                    |
| ---------------------------- | ---------------------------------------- | --------------------------------------------------- | --------------------------------------------------------------- |
| **ポートフォリオ概況表示**   | ポートフォリオ評価額、保有銘柄一覧の確認 | `GET /api/portfolio/summary`<br>※今後実装予定       | API層<br>サービス層<br>データアクセス層<br>プレゼンテーション層 |
| **主要インデックス表示**     | 時系列インデックスデータの表示           | `GET /api/indices`<br>※今後実装予定                 | API層<br>サービス層<br>データアクセス層                         |
| **データ取得ジョブ管理**     | 手動トリガボタン、ジョブステータス表示   | 既存: `POST /api/batch/start`<br>WebSocket           | API層<br>プレゼンテーション層<br>フロントエンド                 |
| **ウィジェットカスタマイズ** | ダッシュボードの表示項目カスタマイズ     | `PUT /api/user/dashboard-settings`<br>※今後実装予定 | API層<br>サービス層<br>データアクセス層                         |

### 3. 銘柄検索と詳細表示

| 機能                     | できること                                                | エンドポイント                                                       | 実装レイヤー                                                                              |
| ------------------------ | --------------------------------------------------------- | -------------------------------------------------------------------- | ----------------------------------------------------------------------------------------- |
| **銘柄マスタ検索**       | 銘柄コード/名称で検索<br>JPX全上場銘柄の基本情報管理      | 既存: `GET /api/stock-master/list`<br>`GET /api/stock-master/search` | API層<br>サービス層<br>データアクセス層                                                   |
| **株価データ参照**       | 時系列ごとの価格情報(OHLCV)の取得<br>ページネーション対応 | 既存: `GET /api/stocks`                                              | API層<br>データアクセス層                                                                 |
| **チャート表示**         | 複数期間の株価チャート表示                                | `GET /api/stocks/{symbol}/chart`<br>※今後実装予定                    | API層<br>サービス層<br>プレゼンテーション層<br>フロントエンド: チャートライブラリ(検討中) |
| **ファンダメンタル表示** | 財務指標の表示                                            | `GET /api/stocks/{symbol}/fundamental`<br>※今後実装予定              | API層<br>サービス層<br>データアクセス層                                                   |
| **銘柄比較機能**         | 複数銘柄の比較                                            | `POST /api/stocks/compare`<br>※今後実装予定                          | API層<br>サービス層<br>プレゼンテーション層                                               |

### 4. 分析ツール(スクリーニング)

| 機能                       | できること                                                    | エンドポイント                                                           | 実装レイヤー                                                    |
| -------------------------- | ------------------------------------------------------------- | ------------------------------------------------------------------------ | --------------------------------------------------------------- |
| **スクリーニング**         | PER、PBR、ROE等の指標で銘柄絞り込み<br>期間指定、複合条件設定 | `POST /api/screening/execute`<br>※今後実装予定                           | API層<br>サービス層<br>データアクセス層<br>プレゼンテーション層 |
| **スクリーニング結果保存** | 絞込結果の保存                                                | `POST /api/screening/save`<br>`GET /api/screening/list`<br>※今後実装予定 | API層<br>サービス層<br>データアクセス層                         |
| **データエクスポート**     | CSV形式でのエクスポート                                       | `GET /api/screening/{id}/export`<br>※今後実装予定                        | API層<br>サービス層                                             |

### 5. バックテスト(簡易)

| 機能                 | できること                                             | エンドポイント                                         | 実装レイヤー                                                                              |
| -------------------- | ------------------------------------------------------ | ------------------------------------------------------ | ----------------------------------------------------------------------------------------- |
| **バックテスト実行** | 期間、初期資金、売買ルールを設定し過去データで戦略検証 | `POST /api/backtest/start`<br>※今後実装予定            | API層<br>サービス層<br>データアクセス層<br>プレゼンテーション層                           |
| **結果可視化**       | 資産曲線、取引ログ、パフォーマンス指標の表示           | `GET /api/backtest/{id}/result`<br>※今後実装予定       | API層<br>サービス層<br>プレゼンテーション層<br>フロントエンド: チャートライブラリ(検討中) |
| **ジョブ管理**       | バックテスト実行状況の監視                             | `GET /api/backtest/jobs`<br>WebSocket<br>※今後実装予定 | API層<br>サービス層<br>WebSocket: Flask-SocketIO                                          |

### 6. ユーザー設定と認証

| 機能                 | できること                        | エンドポイント                                                                                  | 実装レイヤー                                                                                      |
| -------------------- | --------------------------------- | ----------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------- |
| **認証**             | ログイン/ログアウト(OAuth/メール) | `POST /api/auth/login`<br>`POST /api/auth/logout`<br>`POST /api/auth/register`<br>※今後実装予定 | API層<br>サービス層<br>データアクセス層<br>プレゼンテーション層                                   |
| **プロフィール管理** | ユーザープロフィール編集          | `GET /api/user/profile`<br>`PUT /api/user/profile`<br>※今後実装予定                             | API層<br>サービス層<br>データアクセス層<br>プレゼンテーション層                                   |
| **通知設定**         | 通知のオン/オフ設定               | `GET /api/user/notification-settings`<br>`PUT /api/user/notification-settings`<br>※今後実装予定 | API層<br>サービス層<br>データアクセス層<br>プレゼンテーション層                                   |
| **表示設定**         | テーマ・言語切替                  | `GET /api/user/display-settings`<br>`PUT /api/user/display-settings`<br>※今後実装予定           | API層<br>サービス層<br>データアクセス層<br>プレゼンテーション層<br>フロントエンド: CSS/JavaScript |

### 共通機能(監視・管理)

| 機能                 | できること                                  | エンドポイント                            | 実装レイヤー                                                                                      |
| -------------------- | ------------------------------------------- | ----------------------------------------- | ------------------------------------------------------------------------------------------------- |
| **ヘルスチェック**   | システム稼働状態、DB接続、外部API接続の確認 | 既存: `GET /api/system/health-check`      | API層<br>サービス層                                                                               |
| **バッチ履歴管理**   | バッチ処理の実行履歴、成功/失敗の記録       | `GET /api/batch/history`<br>※今後実装予定 | API層<br>サービス層<br>データアクセス層                                                           |
| **リアルタイム進捗** | WebSocketによる進捗配信、ETA表示            | 既存: WebSocket                           | プレゼンテーション層: Flask-SocketIO<br>フロントエンド: `app/static/script.js` (Socket.IO Client) |

---

## 3. システム全体像

### アーキテクチャ図(4層構造)

```mermaid
graph TB
    subgraph "クライアント"
        Browser[Webブラウザ]
    end

    subgraph "プレゼンテーション層"
        FastAPI[FastAPI App<br/>Routers/Templates/WebSocket]
        Swagger[Swagger UI<br/>自動生成APIドキュメント]
    end

    subgraph "API層"
        BatchAPI[一括データ取得API<br/>非同期エンドポイント]
        StockAPI[Stock Master API<br/>非同期エンドポイント]
        MonitorAPI[System Monitoring API<br/>非同期エンドポイント]
        ScreeningAPI[Screening API<br/>※今後実装]
        BacktestAPI[Backtest API<br/>※今後実装]
        AuthAPI[Auth API<br/>※今後実装]
    end

    subgraph "サービス層"
        StockService[StockDataService<br/>非同期統合サービス]
        JPXService[JPXStockService<br/>非同期処理]
        ScreeningService[ScreeningService<br/>※今後実装]
        BacktestService[BacktestService<br/>※今後実装]
        AuthService[AuthService<br/>※今後実装]
    end

    subgraph "データアクセス層"
        StockRepo[StockRepository<br/>非同期対応]
        JPXRepo[JPXRepository<br/>非同期対応]
        Models[SQLAlchemy Models<br/>11テーブル]
    end

    subgraph "外部API"
        YFinance[Yahoo Finance API]
    end

    subgraph "データストレージ"
        PostgreSQL[(PostgreSQL<br/>asyncpg接続)]
    end

    Browser -->|HTTP/WebSocket| FastAPI
    FastAPI --> Swagger
    FastAPI --> BatchAPI & StockAPI & MonitorAPI
    FastAPI -.-> ScreeningAPI & BacktestAPI & AuthAPI

    BatchAPI --> StockService
    StockAPI --> JPXService
    MonitorAPI --> StockService
    ScreeningAPI -.-> ScreeningService
    BacktestAPI -.-> BacktestService
    AuthAPI -.-> AuthService

    StockService -->|await| StockRepo
    JPXService -->|await| JPXRepo
    StockService -->|async| YFinance

    StockRepo -->|async| Models
    JPXRepo -->|async| Models
    Models -->|asyncpg| PostgreSQL

    style FastAPI fill:#e1f5ff
    style Swagger fill:#fffae1
    style PostgreSQL fill:#ffebe1
    style YFinance fill:#fff4e1
    style ScreeningAPI stroke-dasharray: 5 5
    style BacktestAPI stroke-dasharray: 5 5
    style AuthAPI stroke-dasharray: 5 5
    style ScreeningService stroke-dasharray: 5 5
    style BacktestService stroke-dasharray: 5 5
    style AuthService stroke-dasharray: 5 5
```

### データフロー(非同期処理)

```mermaid
sequenceDiagram
    participant Client as クライアント<br/>Webブラウザ
    participant Presentation as プレゼンテーション層<br/>FastAPI App
    participant API as API層<br/>APIRouter
    participant Service as サービス層<br/>StockDataService<br/>(async)
    participant Repository as データアクセス層<br/>Repository<br/>(async)
    participant DB as PostgreSQL<br/>(asyncpg)
    participant YFinance as Yahoo Finance API

    Client->>Presentation: データ取得リクエスト
    Presentation->>API: ルーティング
    API->>Service: await fetch_and_save(symbol)

    par 並列処理可能
        Service->>YFinance: async データ取得
        YFinance-->>Service: 株価データ
    and
        Service->>Service: Pydantic検証
    end

    Service->>Service: データ変換
    Service->>Repository: await save(data)
    Repository->>DB: async UPSERT実行
    DB-->>Repository: 完了
    Repository-->>Service: 完了
    Service-->>API: 結果返却
    API-->>Presentation: Pydanticレスポンス生成
    Presentation-->>Client: JSONレスポンス返却

    Note over Service,YFinance: async/awaitにより<br/>非同期I/O待機中も<br/>他リクエスト処理可能
```

---

## 4. アーキテクチャ構成(4層構造)

### レイヤー構成

```mermaid
graph TB
    A[プレゼンテーション層<br/>FastAPI App/APIRouter/Templates/WebSocket]
    B[API層<br/>APIRouter/Pydanticモデル/エンドポイント定義]
    C[サービス層<br/>非同期ビジネスロジック/外部API連携]
    D[データアクセス層<br/>非同期Repository/SQLAlchemy Models]
    E[(PostgreSQL<br/>asyncpg)]

    A -->|HTTP/WebSocket<br/>async| B
    B -->|await サービス呼び出し<br/>Pydantic検証| C
    C -->|await Repository経由| D
    D -->|async SQL| E

    style A fill:#e1f5ff
    style B fill:#fff4e1
    style C fill:#e1ffe1
    style D fill:#ffe1f5
    style E fill:#ffebe1
```

### レイヤー別責任と配置

| レイヤー               | 責任                                                                                   | 配置ディレクトリ                            | 担当分担例        |
| ---------------------- | -------------------------------------------------------------------------------------- | ------------------------------------------- | ----------------- |
| **プレゼンテーション層** | 非同期HTTPリクエスト処理、画面表示(HTML/CSS/JS)、WebSocket通信、Swagger UI自動生成    | `app/main.py`, `app/templates/`, `app/static/` | 開発者A(フロント) |
| **API層**              | 非同期RESTful APIエンドポイント定義、Pydantic検証、OpenAPIスキーマ自動生成             | `app/api/`                                  | 開発者A(フロント) |
| **サービス層**         | 非同期ビジネスロジック、非同期外部API連携(Yahoo Finance)、Pydanticデータ変換・検証     | `app/services/`                             | 開発者B(バック)   |
| **データアクセス層**   | 非同期Repository Pattern、SQLAlchemy Models(async)、非同期DB操作の抽象化               | `app/repositories/`                         | 開発者B(バック)   |

### 共通モジュール

| モジュール         | 責任                                                               | 配置ディレクトリ  | 共有範囲   |
| ------------------ | ------------------------------------------------------------------ | ----------------- | ---------- |
| **型定義**         | Pydanticモデル、APIリクエスト/レスポンススキーマ、OpenAPI自動生成元 | `app/schemas/`    | 全レイヤー |
| **例外定義**       | カスタムException、FastAPI HTTPExceptionラッパー                   | `app/exceptions/` | 全レイヤー |
| **ユーティリティ** | ロガー、時間軸変換、非同期DB接続など                               | `app/utils/`      | 全レイヤー |

### 4層構造の利点

#### 1. 責任の明確な分離
- 各層が独立した責務を持つ
- レイヤー間の依存関係が一方向
- テストとメンテナンスが容易

#### 2. 並行開発の実現
```
開発者A(フロントエンド/API):
├── プレゼンテーション層の実装
│   ├── HTMLテンプレート
│   ├── CSS/JavaScript
│   ├── WebSocket UI
│   └── Swagger UI設定
└── API層の実装
    ├── APIRouterエンドポイント(async def)
    ├── Pydanticリクエスト/レスポンススキーマ
    ├── OpenAPIメタデータ定義
    └── 自動バリデーション設定

開発者B(バックエンド/データ):
├── サービス層の実装
│   ├── 非同期ビジネスロジック(async def)
│   ├── 非同期Yahoo Finance連携
│   ├── Pydanticデータ変換・検証
│   └── 並列処理実装(asyncio.gather)
└── データアクセス層の実装
    ├── 非同期Repository実装
    ├── SQLAlchemy Models定義(async)
    ├── asyncpg接続設定
    └── 非同期クエリ最適化
```

#### 3. 契約駆動開発(Contract-First Development with FastAPI)
1. **Pydanticスキーマを先に決定** → OpenAPI自動生成
2. **並行開発開始**
   - 開発者A: Swagger UIを見ながらUI開発
   - 開発者B: Pydanticスキーマに従ってビジネスロジック開発
3. **統合**: 型安全性により統合時のエラーが激減

#### 4. Repository Patternの採用(非同期対応)
サービス層がデータベースの実装詳細に依存しないため:
- テスト時に非同期モックRepositoryに差し替え可能
- データソース変更時の影響範囲が限定的
- 非同期クエリロジックの再利用性向上
- asyncpg/psycopg2の切り替えが容易

---

## 5. 技術スタック

### FastAPI選定理由

| 理由                       | 説明                                                                                     |
| -------------------------- | ---------------------------------------------------------------------------------------- |
| **非同期処理ネイティブ**   | 4,000銘柄の並列取得に最適。async/awaitでYahoo Finance API呼び出しを効率化               |
| **自動APIドキュメント生成** | OpenAPI/Swagger UI/ReDocが自動生成。フロント/バック並行開発を促進                        |
| **型安全性**               | Pydantic統合により`app/types/`の型定義を実行時検証。バリデーションを自動化              |
| **高パフォーマンス**       | Starlette/Uvicorn基盤でFlaskより高速。大量データ処理に有利                               |
| **WebSocket対応**          | Starlette経由でWebSocketをネイティブサポート。リアルタイム進捗表示に最適                |
| **モダンなPython**         | Python 3.8+の機能をフル活用。既存の設計理念(型重視、シンプル設計)に合致                 |
| **SQLAlchemy互換**         | 既存のRepository PatternとModelsをそのまま利用可能。移行コストが低い                     |
| **段階的拡張に適合**       | 必要な機能だけを追加可能。「動作優先」「シンプル設計」「段階的拡張」の設計理念に完全一致 |

### バックエンド

| カテゴリ          | 技術            | バージョン | 用途                               |
| ----------------- | --------------- | ---------- | ---------------------------------- |
| Webフレームワーク | FastAPI         | 0.104.0+   | 非同期HTTPサーバー                 |
| バリデーション    | Pydantic        | 2.5.0+     | 型検証・シリアライズ               |
| ASGIサーバー      | Uvicorn         | 0.24.0+    | 本番環境(Gunicornとの組み合わせ可) |
| WebSocket         | Starlette       | 0.27.0+    | リアルタイム通信(FastAPI内包)      |
| ORM               | SQLAlchemy      | 2.0.23     | データベース操作(非同期対応)       |
| 非同期DBドライバ  | asyncpg         | 0.29.0     | PostgreSQL非同期接続               |
| 同期DBドライバ    | psycopg2-binary | 2.9.9      | 移行期の互換性用                   |
| データ取得        | yfinance        | 0.2.66     | Yahoo Finance API                  |
| データ処理        | pandas          | 2.2.0+     | データ操作                         |
| スケジューラ      | APScheduler     | 3.10.4     | 定期実行                           |

### フロントエンド

| カテゴリ     | 技術                           | 用途                                       |
| ------------ | ------------------------------ | ------------------------------------------ |
| テンプレート | Jinja2                         | サーバーサイドレンダリング(FastAPI互換)    |
| WebSocket    | JavaScript WebSocket API       | リアルタイム通信(Starlette WebSocket対応)  |
| スクリプト   | Vanilla JavaScript             | UI制御                                     |
| チャート     | ※検討中                        | 株価チャート描画                           |
| APIクライアント | Fetch API / Axios (検討中) | FastAPI自動生成OpenAPIスキーマとの連携     |

### データベース

| 項目       | 内容                            |
| ---------- | ------------------------------- |
| RDBMS      | PostgreSQL 12+                  |
| テーブル数 | 11(株価8 + 管理3) ※今後拡張予定 |

### 開発・テスト

| カテゴリ       | 技術           | 用途                |
| -------------- | -------------- | ------------------- |
| テスト         | pytest         | ユニット/統合テスト |
| スクレイピング | selenium       | JPX銘柄一覧取得     |
| Excelファイル  | xlrd, openpyxl | 銘柄リスト読込      |

---

## 6. ディレクトリ構成(4層構造対応)

### アプリケーション全体構成

```
STOCK-INVESTMENT-ANALYZER/
├── app/                # アプリケーション本体
│   ├── api/            # API層: APIRouterエンドポイント(async)
│   ├── services/       # サービス層: 非同期ビジネスロジック
│   ├── repositories/   # データアクセス層: 非同期Repository + Models
│   ├── schemas/        # 共通: Pydanticスキーマ定義
│   ├── templates/      # プレゼンテーション層: HTMLテンプレート
│   ├── static/         # プレゼンテーション層: 静的ファイル
│   ├── exceptions/     # 共通: カスタムException
│   ├── utils/          # 共通: ユーティリティ
│   └── main.py         # プレゼンテーション層: FastAPIアプリメイン
├── docs/               # ドキュメント
├── tests/              # テストコード
│   ├── unit/           # ユニットテスト(非同期対応)
│   ├── integration/    # 統合テスト(非同期対応)
│   └── e2e/            # E2Eテスト
└── requirements.txt    # 依存パッケージ
```


### 開発者別の担当範囲

| 開発者 | 担当レイヤー | 主な作業 |
|--------|-------------|----------|
| **開発者A** | プレゼンテーション層<br/>API層 | - UI/UX設計・実装<br/>- APIRouterエンドポイント実装<br/>- Pydanticスキーマ定義<br/>- Swagger UI/ReDoc設定 |
| **開発者B** | サービス層<br/>データアクセス層 | - 非同期ビジネスロジック実装<br/>- 非同期Repository実装<br/>- SQLAlchemy Models設計<br/>- 並列処理実装 |
| **共通** | スキーマ/例外/ユーティリティ | - Pydanticスキーマ設計<br/>- エラーハンドリング戦略<br/>- 依存性注入設計 |

### FastAPI固有の設計要素

#### Pydanticスキーマの役割
- レイヤー間の契約を明確化
- 実行時型検証による自動バリデーション
- OpenAPI/Swagger UI/ReDocの自動生成
- JSON⇔Pythonオブジェクトの自動変換

#### 非同期処理の実装方針
- 全レイヤーで`async/await`を使用
- 並列処理は`asyncio.gather()`を活用
- DBアクセスは`asyncpg`で非同期化
- 外部API呼び出しも非同期対応

#### 依存性注入の活用
- DB接続: `Depends(get_async_db)`
- サービス層: `Depends(get_service)`
- 認証/認可: `Depends(get_current_user)`

---

## 関連ドキュメント

- [フロントエンド機能仕様](../frontend/frontend_spec.md)
- [コンポーネント依存関係](./component_dependency.md)
- [サービス責任分掌](./service_responsibilities.md)
- [データフロー](./data_flow.md)
- [データベース設計](./database_design.md)
- [APIリファレンス](../api/api_reference.md)

---

**最終更新**: 2025-11-15
