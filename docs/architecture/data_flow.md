# データフロー

## 目次

- [1. 概要](#1-概要)
- [2. データフロー全体図](#2-データフロー全体図)
- [3. 主要データフロー](#3-主要データフロー)
- [4. データ変換処理](#4-データ変換処理)
- [5. エラー処理フロー](#5-エラー処理フロー)

## 1. 概要

本ドキュメントでは、システム内のデータの流れを可視化し、データ取得から保存までの処理フローを明確にします。

**データフローの特徴:**
- **Yahoo Finance → PostgreSQL**: 外部APIからデータベースへの一方向フロー
- **リアルタイム配信**: WebSocketによる進捗情報の即時配信
- **マルチタイムフレーム対応（実装済み）**: 8種類の時間軸（1m, 5m, 15m, 30m, 1h, 1d, 1wk, 1mo）に対応したデータ振り分け
- **並列処理**: ThreadPoolExecutorによる最大10並列の効率的なデータ取得

## 2. データフロー全体図

### 2.1 システム全体のデータフロー

```mermaid
flowchart TB
    subgraph "External"
        YFinance[Yahoo Finance API<br/>株価データソース]
    end

    subgraph "Input Layer"
        WebUI[Web UI<br/>ユーザー入力]
        WebSocket[WebSocket Client<br/>進捗受信]
    end

    subgraph "Application Layer"
        Flask[Flask Routes<br/>リクエスト受付]

        subgraph "API Blueprint"
            BulkAPI[Bulk Data API]
            StockAPI[Stock Master API]
            MonitorAPI[Monitoring API]
        end

        subgraph "Service Layer"
            Orchestrator[StockDataOrchestrator<br/>単一銘柄処理]
            BulkService[BulkDataService<br/>一括処理]
            JPXService[JPXStockService<br/>銘柄マスタ]
            Fetcher[StockDataFetcher<br/>データ取得]
            Saver[StockDataSaver<br/>データ保存]
        end

        SocketIOServer[SocketIO Server<br/>進捗配信]
    end

    subgraph "Data Layer"
        Models[SQLAlchemy Models<br/>8種類の株価テーブル]
        MasterModels[Master Models<br/>銘柄/バッチ管理]
    end

    subgraph "Storage"
        PostgreSQL[(PostgreSQL<br/>stock_data_system)]
    end

    %% Input Flow
    WebUI -->|HTTP Request| Flask
    Flask --> BulkAPI
    Flask --> StockAPI
    Flask --> MonitorAPI
    Flask --> Orchestrator

    %% Service Flow
    BulkAPI --> BulkService
    BulkAPI --> JPXService
    StockAPI --> JPXService
    MonitorAPI --> MasterModels

    Orchestrator --> Fetcher
    Orchestrator --> Saver
    BulkService --> Fetcher
    BulkService --> Saver

    %% External Data Flow
    Fetcher -->|API Request| YFinance
    YFinance -->|JSON Response| Fetcher

    %% Database Flow
    Saver --> Models
    JPXService --> MasterModels
    Models --> PostgreSQL
    MasterModels --> PostgreSQL

    %% Progress Flow
    BulkService -.->|Progress Event| SocketIOServer
    SocketIOServer -.->|WebSocket| WebSocket
    WebSocket -.->|Real-time Update| WebUI

    style YFinance fill:#fff4e1
    style PostgreSQL fill:#ffebe1
    style Fetcher fill:#e1f5ff
    style Saver fill:#ffe1f5
```

### 2.2 サービスモジュール構造（実装済み）

**実装完了済み（v1.0）:**

```
app/services/
├── stock_data/      # 株価データ取得・保存
│   ├── fetcher.py          # StockDataFetcher
│   ├── saver.py            # StockDataSaver
│   ├── orchestrator.py     # StockDataOrchestrator
│   └── scheduler.py        # StockDataScheduler
├── bulk/            # 一括データ取得
│   └── bulk_service.py     # BulkDataService
├── jpx/             # JPX銘柄マスタ管理
│   └── jpx_stock_service.py # JPXStockService
└── batch/           # バッチ実行管理
    └── batch_service.py    # BatchService
```

**データフローへの影響:**
- データフロー自体（取得→変換→保存）は変更なし
- サービスの所在が機能別ディレクトリに整理
- Orchestrator/BulkはFetcher/Saverを組み合わせて動作（従来どおり）

## 3. 主要データフロー

### 3.1 単一銘柄データ取得フロー

```mermaid
sequenceDiagram
    participant User as ユーザー
    participant Flask as Flask App
    participant Orch as StockDataOrchestrator
    participant Fetcher as StockDataFetcher
    participant YF as Yahoo Finance
    participant Saver as StockDataSaver
    participant Utils as TimeframeUtils
    participant Models as SQLAlchemy Models
    participant DB as PostgreSQL

    User->>Flask: POST /api/fetch-data<br/>{symbol, period, interval}
    Flask->>Orch: fetch_and_save()

    Orch->>Fetcher: fetch_stock_data(symbol, period, interval)
    Fetcher->>YF: yfinance.download()
    YF-->>Fetcher: DataFrame (OHLCV)
    Fetcher->>Fetcher: データ正規化・変換
    Fetcher-->>Orch: DataFrame

    Orch->>Saver: save_stock_data(df, symbol, interval)
    Saver->>Utils: get_model_for_interval(interval)
    Utils-->>Saver: Model Class (e.g., Stocks1d)

    Saver->>Models: UPSERT操作
    Models->>DB: INSERT ... ON CONFLICT UPDATE
    DB-->>Models: 成功
    Models-->>Saver: 保存件数

    Saver-->>Orch: {saved, skipped, date_range}
    Orch-->>Flask: {success, data, message}
    Flask-->>User: JSON Response
```

**処理ステップ:**
1. **リクエスト受付**: ユーザーが銘柄コード・期間・時間軸を指定
2. **データ取得**: Yahoo Finance APIから株価データを取得
3. **データ変換**: DataFrameを正規化（カラム名統一、型変換）
4. **テーブル選択**: 時間軸に応じて保存先テーブルを決定
5. **データ保存**: UPSERT操作で重複を避けて保存
6. **結果返却**: 保存件数・スキップ件数・日付範囲を返却

### 3.2 バルクデータ取得フロー（並列処理）

```mermaid
sequenceDiagram
    participant User as ユーザー
    participant Flask as Flask App
    participant BulkAPI as Bulk Data API
    participant BulkSvc as BulkDataService
    participant SocketIO as SocketIO Server
    participant Fetcher as StockDataFetcher
    participant Saver as StockDataSaver
    participant DB as PostgreSQL

    User->>Flask: POST /api/bulk/start<br/>{symbols[], interval}
    Flask->>BulkAPI: start_bulk_fetch()
    BulkAPI->>BulkSvc: fetch_multiple_stocks(symbols, interval)
    BulkAPI-->>User: {job_id, status}

    Note over BulkSvc: ThreadPoolExecutor起動<br/>(max_workers=10)

    par 並列処理 (銘柄1)
        BulkSvc->>Fetcher: fetch_stock_data(symbol1)
        Fetcher-->>BulkSvc: DataFrame1
        BulkSvc->>Saver: save_stock_data(df1)
        Saver->>DB: INSERT/UPDATE
        DB-->>Saver: 成功
        Saver-->>BulkSvc: 結果1
        BulkSvc->>SocketIO: 進捗イベント (1/N完了)
        SocketIO-->>User: WebSocket配信
    and 並列処理 (銘柄2)
        BulkSvc->>Fetcher: fetch_stock_data(symbol2)
        Fetcher-->>BulkSvc: DataFrame2
        BulkSvc->>Saver: save_stock_data(df2)
        Saver->>DB: INSERT/UPDATE
        DB-->>Saver: 成功
        Saver-->>BulkSvc: 結果2
        BulkSvc->>SocketIO: 進捗イベント (2/N完了)
        SocketIO-->>User: WebSocket配信
    and 並列処理 (銘柄N)
        BulkSvc->>Fetcher: fetch_stock_data(symbolN)
        Fetcher-->>BulkSvc: DataFrameN
        BulkSvc->>Saver: save_stock_data(dfN)
        Saver->>DB: INSERT/UPDATE
        DB-->>Saver: 成功
        Saver-->>BulkSvc: 結果N
        BulkSvc->>SocketIO: 進捗イベント (N/N完了)
        SocketIO-->>User: WebSocket配信
    end

    BulkSvc->>SocketIO: 完了イベント
    SocketIO-->>User: WebSocket配信（処理完了）
```

**処理ステップ:**
1. **ジョブ登録**: バルク取得ジョブを登録し、job_idを返却
2. **並列実行**: ThreadPoolExecutorで最大10銘柄を並列処理
3. **進捗配信**: 各銘柄の処理完了時にWebSocketで進捗を配信
4. **ETA計算**: 処理速度から残り時間を推定
5. **完了通知**: 全銘柄の処理完了をWebSocketで通知

### 3.3 JPX全銘柄順次取得フロー（実装済み）

```mermaid
sequenceDiagram
    participant User as ユーザー
    participant BulkAPI as Bulk Data API
    participant JPXSvc as JPXStockService
    participant BulkSvc as BulkDataService
    participant Selenium as Selenium Driver
    participant JPX as JPX Website
    participant DB as PostgreSQL

    User->>BulkAPI: POST /api/bulk/jpx-sequential/start
    BulkAPI->>JPXSvc: get_jpx_symbols(limit, offset)

    JPXSvc->>Selenium: WebDriverを起動
    Selenium->>JPX: 銘柄一覧ページにアクセス
    JPX-->>Selenium: HTML
    Selenium->>Selenium: 銘柄一覧を解析
    Selenium-->>JPXSvc: symbols[] (4000+銘柄)

    JPXSvc->>DB: 銘柄マスタに保存
    DB-->>JPXSvc: 保存完了
    JPXSvc-->>BulkAPI: symbols[]

    loop 8種類の時間軸 (1m, 5m, 15m, 30m, 1h, 1d, 1wk, 1mo)
        BulkAPI->>BulkSvc: fetch_multiple_stocks(symbols, interval)
        Note over BulkSvc: ThreadPoolExecutor（最大10並列）で全銘柄取得
        BulkSvc-->>BulkAPI: 処理結果
    end

    BulkAPI-->>User: {job_id, status, total_symbols, intervals}
```

**処理ステップ（実装済み）:**
1. **銘柄一覧取得**: SeleniumでJPX公式サイトから銘柄一覧を取得
2. **銘柄マスタ保存**: 取得した銘柄をstock_masterテーブルに保存
3. **8時間軸ループ**: 実装済みの8種類の時間軸それぞれで全銘柄のデータを取得
4. **並列処理**: ThreadPoolExecutorで最大10銘柄を並列処理
5. **進捗管理**: WebSocket経由でリアルタイム進捗配信（時間軸 × 銘柄数）

### 3.4 銘柄マスタ更新フロー

```mermaid
flowchart LR
    User[ユーザー] -->|POST /api/stock-master/update| StockAPI[Stock Master API]
    StockAPI --> JPXService[JPXStockService]
    JPXService --> Selenium[Selenium WebDriver]
    Selenium -->|スクレイピング| JPXSite[JPX Website]
    JPXSite -->|HTML| Selenium
    Selenium -->|解析結果| JPXService
    JPXService -->|UPSERT| StockMaster[(stock_master table)]
    StockMaster -->|更新完了| JPXService
    JPXService -->|結果| StockAPI
    StockAPI -->|JSON Response| User

    style JPXSite fill:#fff4e1
    style StockMaster fill:#ffebe1
```

### 3.5 データ取得フロー（詳細）

```mermaid
flowchart TB
    Start([データ取得開始]) --> ValidateInput{入力検証}
    ValidateInput -->|無効| ErrorInvalid[エラー: INVALID_SYMBOL]
    ValidateInput -->|有効| FetchYFinance[Yahoo Finance API呼び出し]

    FetchYFinance --> CheckResponse{レスポンス確認}
    CheckResponse -->|空データ| ErrorNoData[エラー: NO_DATA_FOUND]
    CheckResponse -->|エラー| ErrorAPI[エラー: API_ERROR]
    CheckResponse -->|成功| NormalizeData[データ正規化]

    NormalizeData --> ConvertColumns[カラム名変換<br/>Date→date, Open→open, etc.]
    ConvertColumns --> ConvertTypes[型変換<br/>datetime, decimal, bigint]
    ConvertTypes --> ValidateData{データ検証}

    ValidateData -->|不正データ| ErrorData[エラー: INVALID_DATA]
    ValidateData -->|正常| ReturnDF[DataFrame返却]

    ReturnDF --> End([データ取得完了])

    ErrorInvalid --> End
    ErrorNoData --> End
    ErrorAPI --> End
    ErrorData --> End

    style Start fill:#e1ffe1
    style End fill:#e1ffe1
    style ErrorInvalid fill:#ffe1e1
    style ErrorNoData fill:#ffe1e1
    style ErrorAPI fill:#ffe1e1
    style ErrorData fill:#ffe1e1
```

### 3.6 データ保存フロー（詳細）

```mermaid
flowchart TB
    Start([データ保存開始]) --> ReceiveDF[DataFrameを受領]
    ReceiveDF --> GetInterval[時間軸を取得]
    GetInterval --> SelectModel[TimeframeUtilsで<br/>モデルクラスを選択]

    SelectModel --> Model1m{1m?}
    Model1m -->|Yes| UseStocks1m[Stocks1m モデル]
    Model1m -->|No| Model5m{5m?}
    Model5m -->|Yes| UseStocks5m[Stocks5m モデル]
    Model5m -->|No| Model1d{1d?}
    Model1d -->|Yes| UseStocks1d[Stocks1d モデル]
    Model1d -->|No| OtherModels[その他のモデル<br/>15m, 30m, 1h, 1wk, 1mo]

    UseStocks1m --> PrepareData[データ準備]
    UseStocks5m --> PrepareData
    UseStocks1d --> PrepareData
    OtherModels --> PrepareData

    PrepareData --> StartTx[トランザクション開始]
    StartTx --> LoopRows{全行処理}

    LoopRows -->|各行| CheckDuplicate{重複チェック<br/>symbol + date/datetime}
    CheckDuplicate -->|存在| UpdateRow[UPDATE]
    CheckDuplicate -->|新規| InsertRow[INSERT]

    UpdateRow --> NextRow[次の行へ]
    InsertRow --> NextRow
    NextRow --> LoopRows

    LoopRows -->|完了| CommitTx[トランザクションコミット]
    CommitTx --> CalcResult[結果計算<br/>saved, skipped, date_range]
    CalcResult --> ReturnResult[結果返却]
    ReturnResult --> End([保存完了])

    StartTx -.->|エラー| RollbackTx[ロールバック]
    RollbackTx --> ErrorSave[エラー: SAVE_ERROR]
    ErrorSave --> End

    style Start fill:#e1ffe1
    style End fill:#e1ffe1
    style ErrorSave fill:#ffe1e1
    style CommitTx fill:#e1f5ff
```

## 4. データ変換処理

### 4.1 Yahoo Finance → DataFrame変換

```mermaid
flowchart LR
    subgraph "Yahoo Finance Response"
        YFData[Yahoo Finance JSON<br/>timestamp, Open, High, Low, Close, Volume]
    end

    subgraph "pandas DataFrame"
        DF[DataFrame<br/>index: Date/Datetime<br/>columns: Open, High, Low, Close, Volume]
    end

    subgraph "Normalized DataFrame"
        NormDF[Normalized DataFrame<br/>columns: date/datetime, open, high, low, close, volume<br/>types: datetime64/date, float64, int64]
    end

    YFData -->|yfinance.download| DF
    DF -->|カラム名小文字化| NormDF
    DF -->|インデックスをカラムに| NormDF
    DF -->|型変換| NormDF

    style YFData fill:#fff4e1
    style NormDF fill:#e1f5ff
```

**変換ルール:**

| 変換前（Yahoo Finance） | 変換後（システム） | 型                |
| ----------------------- | ------------------ | ----------------- |
| Date (index)            | date / datetime    | datetime64 / date |
| Open                    | open               | DECIMAL(10,2)     |
| High                    | high               | DECIMAL(10,2)     |
| Low                     | low                | DECIMAL(10,2)     |
| Close                   | close              | DECIMAL(10,2)     |
| Volume                  | volume             | BIGINT            |

### 4.2 DataFrame → SQLAlchemyモデル変換

```mermaid
flowchart TB
    DF[DataFrame] --> TimeframeCheck{時間軸判定}

    TimeframeCheck -->|1m, 5m, 15m, 30m, 1h| DatetimeType[datetime型<br/>TIMESTAMP]
    TimeframeCheck -->|1d, 1wk, 1mo| DateType[date型<br/>DATE]

    DatetimeType --> CreateModel1[モデルインスタンス生成<br/>Stocks1m, Stocks5m, etc.]
    DateType --> CreateModel2[モデルインスタンス生成<br/>Stocks1d, Stocks1wk, etc.]

    CreateModel1 --> MapColumns[カラムマッピング<br/>df → model attributes]
    CreateModel2 --> MapColumns

    MapColumns --> SetSymbol[symbol設定]
    SetSymbol --> SetDateTime[date/datetime設定]
    SetDateTime --> SetOHLCV[OHLCV設定]
    SetOHLCV --> SetTimestamps[created_at/updated_at設定]
    SetTimestamps --> ModelReady[モデル準備完了]

    style DF fill:#e1f5ff
    style ModelReady fill:#e1ffe1
```

### 4.3 時間軸ごとのテーブル振り分け

```mermaid
graph TD
    Interval[時間軸<br/>interval parameter]

    Interval --> TF1m{1m?}
    Interval --> TF5m{5m?}
    Interval --> TF15m{15m?}
    Interval --> TF30m{30m?}
    Interval --> TF1h{1h?}
    Interval --> TF1d{1d?}
    Interval --> TF1wk{1wk?}
    Interval --> TF1mo{1mo?}

    TF1m -->|Yes| Table1m[(stocks_1m<br/>datetime型)]
    TF5m -->|Yes| Table5m[(stocks_5m<br/>datetime型)]
    TF15m -->|Yes| Table15m[(stocks_15m<br/>datetime型)]
    TF30m -->|Yes| Table30m[(stocks_30m<br/>datetime型)]
    TF1h -->|Yes| Table1h[(stocks_1h<br/>datetime型)]
    TF1d -->|Yes| Table1d[(stocks_1d<br/>date型)]
    TF1wk -->|Yes| Table1wk[(stocks_1wk<br/>date型)]
    TF1mo -->|Yes| Table1mo[(stocks_1mo<br/>date型)]

    style Table1m fill:#e1f5ff
    style Table5m fill:#e1f5ff
    style Table15m fill:#e1f5ff
    style Table30m fill:#e1f5ff
    style Table1h fill:#e1f5ff
    style Table1d fill:#ffe1f5
    style Table1wk fill:#ffe1f5
    style Table1mo fill:#ffe1f5
```

## 5. エラー処理フロー

### 5.1 エラーハンドリング階層

```mermaid
flowchart TB
    Request[HTTPリクエスト] --> Layer1[プレゼンテーション層<br/>Flask Routes]

    Layer1 --> TryCatch1{try-catch}
    TryCatch1 -->|エラー| ErrorType1{エラー種別判定}

    ErrorType1 -->|StockDataError| Return400[HTTP 400<br/>VALIDATION_ERROR]
    ErrorType1 -->|DatabaseError| Return500[HTTP 500<br/>DATABASE_ERROR]
    ErrorType1 -->|Exception| Return500_2[HTTP 500<br/>INTERNAL_SERVER_ERROR]

    TryCatch1 -->|正常| Layer2[サービス層<br/>Orchestrator/BulkService]

    Layer2 --> TryCatch2{try-catch}
    TryCatch2 -->|エラー| ErrorHandler[ErrorHandler<br/>エラー分類・ログ記録]

    ErrorHandler --> LogError[StructuredLogger<br/>JSON形式でログ出力]
    LogError --> RaiseError[カスタム例外をraise]
    RaiseError --> Layer1

    TryCatch2 -->|正常| Layer3[データアクセス層<br/>Fetcher/Saver]

    Layer3 --> TryCatch3{try-catch}
    TryCatch3 -->|エラー| CheckErrorType{エラー種別}

    CheckErrorType -->|YFinance Error| HandleAPIError[API_ERROR<br/>リトライ可能]
    CheckErrorType -->|DB Error| HandleDBError[DATABASE_ERROR<br/>リトライ不可]
    CheckErrorType -->|Network Error| HandleNetError[NETWORK_ERROR<br/>リトライ可能]

    HandleAPIError --> Retry{リトライ<br/>上限チェック}
    Retry -->|再試行| Layer3
    Retry -->|上限到達| FinalError[最終エラー]

    HandleDBError --> FinalError
    HandleNetError --> Retry

    FinalError --> Layer2

    TryCatch3 -->|正常| Success[成功レスポンス]
    Success --> Layer2
    Layer2 --> Layer1
    Layer1 --> Response[HTTPレスポンス]

    style Return400 fill:#ffe1e1
    style Return500 fill:#ffe1e1
    style Return500_2 fill:#ffe1e1
    style FinalError fill:#ffe1e1
    style Success fill:#e1ffe1
```

### 5.2 エラー種別と対応

```mermaid
graph TD
    Error[エラー発生]

    Error --> Cat1{カテゴリ1:<br/>入力検証}
    Error --> Cat2{カテゴリ2:<br/>外部API}
    Error --> Cat3{カテゴリ3:<br/>データベース}
    Error --> Cat4{カテゴリ4:<br/>その他}

    Cat1 --> E1[INVALID_SYMBOL<br/>無効な銘柄コード]
    Cat1 --> E2[INVALID_INTERVAL<br/>無効な時間軸]
    Cat1 --> E3[VALIDATION_ERROR<br/>パラメータ不正]

    Cat2 --> E4[NO_DATA_FOUND<br/>データが取得できない]
    Cat2 --> E5[API_ERROR<br/>API呼び出しエラー]
    Cat2 --> E6[NETWORK_ERROR<br/>ネットワークエラー]

    Cat3 --> E7[DATABASE_ERROR<br/>DB接続/操作エラー]
    Cat3 --> E8[DUPLICATE_ERROR<br/>重複データ]

    Cat4 --> E9[INTERNAL_SERVER_ERROR<br/>予期しないエラー]

    E1 --> Action1[HTTP 400<br/>ユーザーに修正を促す]
    E2 --> Action1
    E3 --> Action1

    E4 --> Action2[HTTP 400<br/>銘柄コード確認を促す]
    E5 --> Action3[HTTP 502<br/>リトライまたは後で再試行]
    E6 --> Action3

    E7 --> Action4[HTTP 500<br/>システム管理者に通知]
    E8 --> Action5[スキップ<br/>既存データ保持]

    E9 --> Action4

    style E1 fill:#ffe1e1
    style E2 fill:#ffe1e1
    style E3 fill:#ffe1e1
    style E4 fill:#fff4e1
    style E5 fill:#fff4e1
    style E6 fill:#fff4e1
    style E7 fill:#ffebe1
    style E8 fill:#e1f5ff
    style E9 fill:#ffebe1
```

### 5.3 リトライロジック

```mermaid
stateDiagram-v2
    [*] --> FetchData: データ取得開始

    FetchData --> CheckResult: API呼び出し

    CheckResult --> Success: 成功
    CheckResult --> CheckRetry: エラー

    CheckRetry --> CheckRetryType: リトライ可能?

    CheckRetryType --> IncrementRetry: Yes (API/Network Error)
    CheckRetryType --> FinalFailure: No (Validation/DB Error)

    IncrementRetry --> CheckRetryCount: リトライカウント+1

    CheckRetryCount --> Wait: カウント < 上限 (3回)
    CheckRetryCount --> FinalFailure: カウント >= 上限

    Wait --> FetchData: 待機後再試行<br/>(exponential backoff)

    Success --> [*]: 処理完了
    FinalFailure --> [*]: エラー終了
```

**リトライ設定:**
- **最大リトライ回数**: 3回
- **待機時間**: Exponential Backoff (1秒 → 2秒 → 4秒)
- **リトライ可能エラー**: API_ERROR, NETWORK_ERROR
- **リトライ不可エラー**: VALIDATION_ERROR, DATABASE_ERROR

### 5.4 WebSocket進捗配信フロー

```mermaid
sequenceDiagram
    participant Client as Webブラウザ
    participant SocketIO as SocketIO Server
    participant BulkSvc as BulkDataService
    participant Worker as ThreadPool Worker

    Client->>SocketIO: WebSocket接続
    SocketIO-->>Client: 接続確立

    Client->>BulkSvc: バルク処理開始

    loop 並列処理
        Worker->>Worker: 銘柄データ取得
        Worker->>BulkSvc: 処理完了通知
        BulkSvc->>BulkSvc: 進捗計算<br/>(完了数/総数, ETA)
        BulkSvc->>SocketIO: emit('progress', data)
        SocketIO-->>Client: 進捗イベント配信
        Client->>Client: UI更新<br/>(プログレスバー, ETA表示)
    end

    BulkSvc->>SocketIO: emit('complete', data)
    SocketIO-->>Client: 完了イベント配信
    Client->>Client: 完了UI表示
```

**進捗データ構造:**
```json
{
  "job_id": "job_123456",
  "status": "running",
  "progress": {
    "total": 100,
    "completed": 45,
    "failed": 2,
    "percentage": 45.0
  },
  "eta": {
    "seconds_remaining": 120,
    "estimated_completion_time": "2025-10-22T16:45:30"
  },
  "current_symbol": "7203.T"
}
```

## 関連ドキュメント

- [アーキテクチャ概要](architecture_overview.md) - システム全体のアーキテクチャ
- [コンポーネント依存関係](component_dependency.md) - サービス間の依存関係
- [サービス責任分掌](service_responsibilities.md) - 各サービスの役割と責任
- [データベース設計](database_design.md) - データベーススキーマ詳細
- [API仕様書](../api/README.md) - API エンドポイント詳細
