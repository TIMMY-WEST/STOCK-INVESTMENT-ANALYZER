# APIリファレンス

STOCK-INVESTMENT-ANALYZER APIの完全なリファレンスドキュメントです。

## 目次

- [基本情報](#基本情報)
- [認証](#認証)
- [エンドポイント一覧](#エンドポイント一覧)
  - [株価データAPI](#株価データapi)
  - [バルクデータAPI](#バルクデータapi)
  - [銘柄マスターAPI](#銘柄マスターapi)
  - [システム監視API](#システム監視api)
- [データモデル](#データモデル)
- [エラーハンドリング](#エラーハンドリング)
- [レスポンス形式](#レスポンス形式)

---

## 基本情報

- **ベースURL**: `http://localhost:8000`
- **APIバージョン**: v1 (オプション: `/api/v1/...`)
- **Content-Type**: `application/json`
- **文字エンコーディング**: UTF-8

### サポートされているバージョン

- **非バージョン**: `/api/*` (デフォルト、v1として動作)
- **v1**: `/api/v1/*` (明示的なバージョン指定)

---

## 認証

現在のバージョンでは認証は実装されていません。将来的にAPIキー認証が追加される予定です。

### 将来の認証方式（予定）

```http
X-API-Key: your_api_key_here
```

---

## エンドポイント一覧

### 株価データAPI

#### 1. 株価データ取得・保存

Yahoo Financeから株価データを取得し、データベースに保存します。

**エンドポイント**
```
POST /api/stocks/data
```

**リクエストボディ**
```json
{
  "symbol": "7203.T",
  "period": "1mo",
  "interval": "1d"
}
```

**パラメータ**

| フィールド | 型 | 必須 | 説明 | デフォルト |
|-----------|-----|------|------|-----------|
| `symbol` | string | ○ | 銘柄コード（例: 7203.T = トヨタ） | - |
| `period` | string | - | 取得期間 | "1mo" |
| `interval` | string | - | 時間軸 | "1d" |

**期間（period）の指定可能な値**
- `1d`, `5d`, `1mo`, `3mo`, `6mo`, `1y`, `2y`, `5y`, `10y`, `ytd`, `max`

**時間軸（interval）の指定可能な値**
- 分足: `1m`, `2m`, `5m`, `15m`, `30m`, `60m`, `90m`
- 時間足: `1h`
- 日足以上: `1d`, `5d`, `1wk`, `1mo`, `3mo`

**成功レスポンス (200)**
```json
{
  "success": true,
  "message": "データを正常に取得し、データベースに保存しました",
  "data": {
    "symbol": "7203.T",
    "period": "1mo",
    "interval": "1d",
    "records_count": 20,
    "saved_records": 18,
    "skipped_records": 2,
    "date_range": {
      "start": "2024-01-01",
      "end": "2024-01-31"
    }
  },
  "meta": {
    "table_name": "stocks_1d"
  }
}
```

**エラーレスポンス**

無効な銘柄コード (400):
```json
{
  "success": false,
  "error": {
    "code": "INVALID_SYMBOL",
    "message": "指定された銘柄コード '9999.T' のデータが取得できません。銘柄コードを確認してください。",
    "details": {
      "symbol": "9999.T"
    }
  }
}
```

無効な時間軸 (400):
```json
{
  "success": false,
  "error": {
    "code": "INVALID_INTERVAL",
    "message": "無効な足種別です。有効な値: 1m, 2m, 5m, 15m, 30m, 60m, 90m, 1h, 1d, 5d, 1wk, 1mo, 3mo",
    "details": {
      "interval": "invalid",
      "valid_intervals": ["1m", "2m", "5m", "15m", "30m", "60m", "90m", "1h", "1d", "5d", "1wk", "1mo", "3mo"]
    }
  }
}
```

---

#### 2. 株価データ一覧取得

保存済みの株価データを検索・取得します。

**エンドポイント**
```
GET /api/stocks
```

**クエリパラメータ**

| パラメータ | 型 | 必須 | 説明 | デフォルト |
|-----------|-----|------|------|-----------|
| `symbol` | string | - | 銘柄コード（指定時はその銘柄のみ） | - |
| `interval` | string | - | 時間軸 | "1d" |
| `limit` | integer | - | 取得件数制限（1-1000） | 100 |
| `offset` | integer | - | オフセット（0以上） | 0 |
| `start_date` | string | - | 開始日（YYYY-MM-DD） | - |
| `end_date` | string | - | 終了日（YYYY-MM-DD） | - |
| `from` | string | - | 開始日のエイリアス（start_dateより優先） | - |
| `to` | string | - | 終了日のエイリアス（end_dateより優先） | - |

**リクエスト例**
```
GET /api/stocks?symbol=7203.T&interval=1d&limit=30
GET /api/stocks?interval=1wk&start_date=2024-01-01&end_date=2024-12-31
GET /api/stocks?symbol=6758.T&from=2024-01-01&to=2024-01-31
GET /api/stocks?interval=5m&limit=100&offset=100
```

**成功レスポンス (200)**
```json
{
  "success": true,
  "data": [
    {
      "id": 1,
      "symbol": "7203.T",
      "date": "2024-01-15",
      "open": 2500.0,
      "high": 2550.0,
      "low": 2480.0,
      "close": 2530.0,
      "volume": 1500000,
      "created_at": "2024-01-15T10:00:00Z",
      "updated_at": "2024-01-15T10:00:00Z"
    }
  ],
  "pagination": {
    "total": 100,
    "limit": 30,
    "offset": 0,
    "has_next": true
  },
  "meta": {
    "interval": "1d",
    "table_name": "stocks_1d"
  }
}
```

**エラーレスポンス**

無効なパラメータ (400):
```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "無効な時間軸です: invalid",
    "details": {
      "interval": "invalid"
    }
  }
}
```

---

#### 3. 株価データ作成

新しい株価データレコードを作成します。

**エンドポイント**
```
POST /api/stocks
```

**リクエストボディ**
```json
{
  "symbol": "7203.T",
  "interval": "1d",
  "date": "2024-01-15",
  "open": 2500.0,
  "high": 2550.0,
  "low": 2480.0,
  "close": 2530.0,
  "volume": 1500000
}
```

**成功レスポンス (201)**
```json
{
  "success": true,
  "message": "株価データが正常に作成されました",
  "data": {
    "id": 123,
    "symbol": "7203.T",
    "date": "2024-01-15",
    "open": 2500.0,
    "high": 2550.0,
    "low": 2480.0,
    "close": 2530.0,
    "volume": 1500000
  }
}
```

---

#### 4. 株価データ詳細取得

特定のIDの株価データを取得します。

**エンドポイント**
```
GET /api/stocks/{stock_id}
```

**パスパラメータ**

| パラメータ | 型 | 説明 |
|-----------|-----|------|
| `stock_id` | integer | 株価データのID |

**成功レスポンス (200)**
```json
{
  "success": true,
  "data": {
    "id": 123,
    "symbol": "7203.T",
    "date": "2024-01-15",
    "open": 2500.0,
    "high": 2550.0,
    "low": 2480.0,
    "close": 2530.0,
    "volume": 1500000,
    "created_at": "2024-01-15T10:00:00Z",
    "updated_at": "2024-01-15T10:00:00Z"
  }
}
```

**エラーレスポンス (404)**
```json
{
  "success": false,
  "error": {
    "code": "NOT_FOUND",
    "message": "指定されたIDのデータが見つかりません",
    "details": {
      "stock_id": 123
    }
  }
}
```

---

#### 5. 株価データ更新

特定のIDの株価データを更新します。

**エンドポイント**
```
PUT /api/stocks/{stock_id}
```

**リクエストボディ**
```json
{
  "open": 2510.0,
  "high": 2560.0,
  "low": 2490.0,
  "close": 2540.0,
  "volume": 1600000
}
```

**成功レスポンス (200)**
```json
{
  "success": true,
  "message": "株価データが正常に更新されました",
  "data": {
    "id": 123,
    "symbol": "7203.T",
    "date": "2024-01-15",
    "open": 2510.0,
    "high": 2560.0,
    "low": 2490.0,
    "close": 2540.0,
    "volume": 1600000
  }
}
```

---

#### 6. 株価データ削除

特定のIDの株価データを削除します。

**エンドポイント**
```
DELETE /api/stocks/{stock_id}
```

**成功レスポンス (200)**
```json
{
  "success": true,
  "message": "株価データが正常に削除されました"
}
```

---

### バルクデータAPI

バージョン付きエンドポイントのみサポート。

#### 1. バルクジョブ開始

複数銘柄の株価データを一括取得します。

**エンドポイント**
```
POST /api/v1/bulk-data/jobs
```

**リクエストボディ**
```json
{
  "symbols": ["7203.T", "6758.T", "9984.T"],
  "period": "1mo",
  "interval": "1d"
}
```

**成功レスポンス (202)**
```json
{
  "success": true,
  "message": "バルクデータ取得ジョブを開始しました",
  "data": {
    "job_id": "bulk_20240115_123456",
    "status": "pending",
    "symbols": ["7203.T", "6758.T", "9984.T"],
    "total_symbols": 3,
    "created_at": "2024-01-15T10:00:00Z"
  }
}
```

---

#### 2. バルクジョブステータス確認

実行中のバルクジョブの進捗を確認します。

**エンドポイント**
```
GET /api/v1/bulk-data/jobs/{job_id}
```

**成功レスポンス (200)**
```json
{
  "success": true,
  "data": {
    "job_id": "bulk_20240115_123456",
    "status": "running",
    "total_symbols": 3,
    "processed_symbols": 2,
    "failed_symbols": 0,
    "progress_percentage": 66.7,
    "started_at": "2024-01-15T10:00:00Z",
    "estimated_completion": "2024-01-15T10:05:00Z"
  }
}
```

**ステータス値**
- `pending`: 待機中
- `running`: 実行中
- `completed`: 完了
- `failed`: 失敗
- `cancelled`: キャンセル済み

---

#### 3. バルクジョブ停止

実行中のバルクジョブを停止します。

**エンドポイント**
```
POST /api/v1/bulk-data/jobs/{job_id}/stop
```

**成功レスポンス (200)**
```json
{
  "success": true,
  "message": "ジョブを停止しました",
  "data": {
    "job_id": "bulk_20240115_123456",
    "status": "cancelled",
    "processed_symbols": 2,
    "total_symbols": 3
  }
}
```

---

### 銘柄マスターAPI

バージョン付きエンドポイントのみサポート。

#### 1. 銘柄マスター更新

JPXから最新の銘柄情報を取得してマスターを更新します。

**エンドポイント**
```
POST /api/v1/stock-master
```

**リクエストボディ**
```json
{
  "force_update": false
}
```

**パラメータ**

| フィールド | 型 | 必須 | 説明 | デフォルト |
|-----------|-----|------|------|-----------|
| `force_update` | boolean | - | 強制更新フラグ | false |

**成功レスポンス (200)**
```json
{
  "success": true,
  "message": "銘柄マスターを正常に更新しました",
  "data": {
    "total_stocks": 3800,
    "added_stocks": 10,
    "updated_stocks": 25,
    "removed_stocks": 5,
    "last_updated": "2024-01-15T10:00:00Z"
  }
}
```

---

#### 2. 銘柄マスター一覧取得

登録されている銘柄マスター情報を取得します。

**エンドポイント**
```
GET /api/v1/stock-master/stocks
```

**クエリパラメータ**

| パラメータ | 型 | 必須 | 説明 | デフォルト |
|-----------|-----|------|------|-----------|
| `market` | string | - | 市場（Prime, Standard, Growth） | - |
| `sector` | string | - | 業種 | - |
| `limit` | integer | - | 取得件数制限 | 100 |
| `offset` | integer | - | オフセット | 0 |

**成功レスポンス (200)**
```json
{
  "success": true,
  "data": [
    {
      "symbol": "7203.T",
      "name": "トヨタ自動車",
      "market": "Prime",
      "sector": "輸送用機器",
      "industry": "自動車"
    }
  ],
  "pagination": {
    "total": 3800,
    "limit": 100,
    "offset": 0,
    "has_next": true
  }
}
```

---

### システム監視API

#### 1. ヘルスチェック

システム全体の健全性を確認します。

**エンドポイント**
```
GET /api/system/health-check
GET /api/v1/system/health-check
```

**成功レスポンス (200)**
```json
{
  "success": true,
  "data": {
    "status": "healthy",
    "timestamp": "2024-01-15T10:00:00Z",
    "components": {
      "database": {
        "status": "healthy",
        "response_time_ms": 5
      },
      "external_api": {
        "status": "healthy",
        "response_time_ms": 120
      }
    }
  }
}
```

**ステータス値**
- `healthy`: 正常
- `degraded`: 一部機能に問題あり
- `unhealthy`: システムエラー

---

#### 2. データベース接続テスト

データベース接続の健全性を確認します。

**エンドポイント**
```
POST /api/system/db-connection-test
GET /api/v1/system/database/connection
```

**成功レスポンス (200)**
```json
{
  "success": true,
  "data": {
    "connected": true,
    "database": "stock_investment_analyzer",
    "host": "localhost",
    "tables_exist": true,
    "connection_count": 5,
    "response_time_ms": 5
  }
}
```

---

#### 3. 外部API接続テスト

Yahoo Finance APIへの接続を確認します。

**エンドポイント**
```
POST /api/system/api-connection-test
GET /api/v1/system/external-api/connection
```

**クエリパラメータ**

| パラメータ | 型 | 必須 | 説明 | デフォルト |
|-----------|-----|------|------|-----------|
| `symbol` | string | - | テスト用銘柄コード | "7203.T" |

**成功レスポンス (200)**
```json
{
  "success": true,
  "data": {
    "connected": true,
    "symbol": "7203.T",
    "data_available": true,
    "response_time_ms": 120
  }
}
```

---

## データモデル

### 株価データ（StockData）

時間軸に応じて異なるテーブルに格納されます。

#### 日足・週足・月足データ

**テーブル**: `stocks_1d`, `stocks_1wk`, `stocks_1mo`

| フィールド | 型 | NULL | 説明 |
|-----------|-----|------|------|
| `id` | INTEGER | NOT NULL | 主キー（自動採番） |
| `symbol` | VARCHAR(20) | NOT NULL | 銘柄コード |
| `date` | DATE | NOT NULL | 取引日 |
| `open` | FLOAT | - | 始値 |
| `high` | FLOAT | - | 高値 |
| `low` | FLOAT | - | 安値 |
| `close` | FLOAT | - | 終値 |
| `volume` | BIGINT | - | 出来高 |
| `created_at` | TIMESTAMP | NOT NULL | 作成日時 |
| `updated_at` | TIMESTAMP | NOT NULL | 更新日時 |

**複合ユニークキー**: `(symbol, date)`

#### 分足・時間足データ

**テーブル**: `stocks_1m`, `stocks_5m`, `stocks_15m`, `stocks_30m`, `stocks_1h`

| フィールド | 型 | NULL | 説明 |
|-----------|-----|------|------|
| `id` | INTEGER | NOT NULL | 主キー（自動採番） |
| `symbol` | VARCHAR(20) | NOT NULL | 銘柄コード |
| `datetime` | TIMESTAMP | NOT NULL | 取引日時 |
| `open` | FLOAT | - | 始値 |
| `high` | FLOAT | - | 高値 |
| `low` | FLOAT | - | 安値 |
| `close` | FLOAT | - | 終値 |
| `volume` | BIGINT | - | 出来高 |
| `created_at` | TIMESTAMP | NOT NULL | 作成日時 |
| `updated_at` | TIMESTAMP | NOT NULL | 更新日時 |

**複合ユニークキー**: `(symbol, datetime)`

### 時間軸とテーブル対応表

| interval | テーブル名 | 時間フィールド | 説明 |
|----------|-----------|---------------|------|
| 1m | stocks_1m | datetime | 1分足 |
| 5m | stocks_5m | datetime | 5分足 |
| 15m | stocks_15m | datetime | 15分足 |
| 30m | stocks_30m | datetime | 30分足 |
| 1h | stocks_1h | datetime | 1時間足 |
| 1d | stocks_1d | date | 日足 |
| 1wk | stocks_1wk | date | 週足 |
| 1mo | stocks_1mo | date | 月足 |

---

## エラーハンドリング

### エラーコード一覧

| エラーコード | HTTPステータス | 説明 |
|------------|---------------|------|
| `INVALID_SYMBOL` | 400 | 無効な銘柄コード |
| `INVALID_INTERVAL` | 400 | 無効な時間軸指定 |
| `INVALID_PERIOD` | 400 | 無効な期間指定 |
| `VALIDATION_ERROR` | 400 | バリデーションエラー |
| `NOT_FOUND` | 404 | リソースが見つからない |
| `DATABASE_ERROR` | 500 | データベースエラー |
| `DATA_FETCH_ERROR` | 500 | データ取得エラー |
| `EXTERNAL_API_ERROR` | 502 | 外部APIエラー |
| `INTERNAL_SERVER_ERROR` | 500 | 内部サーバーエラー |

### エラーレスポンス形式

すべてのエラーレスポンスは以下の形式で返されます：

```json
{
  "success": false,
  "error": {
    "code": "ERROR_CODE",
    "message": "エラーの詳細説明",
    "details": {
      "additional": "context"
    }
  }
}
```

---

## レスポンス形式

### 成功レスポンス

#### 単一データ
```json
{
  "success": true,
  "message": "操作が正常に完了しました",
  "data": {
    "field": "value"
  },
  "meta": {
    "additional": "metadata"
  }
}
```

#### ページネーション付きデータ
```json
{
  "success": true,
  "data": [
    {"field": "value"}
  ],
  "pagination": {
    "total": 100,
    "limit": 30,
    "offset": 0,
    "has_next": true
  },
  "meta": {
    "additional": "metadata"
  }
}
```

### 共通フィールド

| フィールド | 型 | 説明 |
|-----------|-----|------|
| `success` | boolean | 成功フラグ（true/false） |
| `message` | string | メッセージ（成功時） |
| `data` | object/array | レスポンスデータ |
| `pagination` | object | ページネーション情報（一覧取得時） |
| `meta` | object | メタデータ（任意） |
| `error` | object | エラー情報（失敗時） |

---

## 付録

### API仕様の確認方法

#### Swagger UI
```
http://localhost:8000/api/docs/
```

#### ReDoc
```
http://localhost:8000/api/docs/redoc/
```

#### OpenAPI仕様書（YAML）
```
http://localhost:8000/api/openapi.yaml
```

### 関連ドキュメント

- [API使用例ガイド](./api_usage_guide.md) - 実践的な使用例とコードサンプル
- [APIバージョニングガイド](./versioning_guide.md) - バージョン管理の詳細
- [プロジェクトアーキテクチャ](../architecture/project_architecture.md) - システム全体の設計

---

**最終更新**: 2025-01-15
**バージョン**: 1.0.0
