# APIエンドポイント整理ドキュメント

## ドキュメント概要

本ドキュメントは、株価データ取得システムの全APIエンドポイントを整理し、RESTful原則との整合性を評価するものです。

**作成日**: 2025-10-22
**対象バージョン**: v1.0.0
**ベースURL**: `http://localhost:8000`

---

## フロント→バック呼び出し規約

- フロントエンドはHTTP(S)で`/api/*`配下のエンドポイントのみを呼び出します。
- エンドポイントは`app/api/*`に定義されたBlueprintが提供します。
- フロントエンドから`app/services/*`やデータベースへ直接アクセスしません（禁止）。
- WebSocketは進捗通知などの双方向通信に限定し、APIの代替にはしません。

## Blueprint配置規約

- 物理配置: `app/api/<module>.py` にBlueprintを定義します。
- Blueprint名: `<module>_api`（例: `system_api`, `bulk_api`）。
- URLプレフィックス: `/api/<module>/` を基本とし、株価データ管理は `/api/stocks` を使用します。
- ルーティング責務: ルートはサービス層（`app/services/*`）を呼び出し、HTTPリクエスト/レスポンスの整形のみを担います。

## 目次

1. [APIエンドポイント一覧](#apiエンドポイント一覧)
2. [エンドポイント詳細](#エンドポイント詳細)
3. [RESTful原則との整合性チェック](#restful原則との整合性チェック)
4. [非推奨・削除予定エンドポイント](#非推奨削除予定エンドポイント)
5. [推奨される改善事項](#推奨される改善事項)
6. [サービスモジュール対応表](#サービスモジュール対応表)

---

## APIエンドポイント一覧

### 1. メインルート

| メソッド | パス | 用途 | Blueprint |
|---------|------|------|-----------|
| GET | `/` | フロントエンドのインデックスページ | メイン |
| GET | `/websocket-test` | WebSocket進捗配信テストページ | メイン |

### 2. 株価データ管理API（メインアプリ）

| メソッド | パス | 用途 | RESTful準拠 |
|---------|------|------|------------|

| POST | `/api/fetch-data` | Yahoo Financeから株価データ取得・保存 | ⚠️ 部分的 |
| POST | `/api/stocks` | 株価データを作成 | ✅ 準拠 |
| GET | `/api/stocks` | 株価データを取得（クエリパラメータ対応） | ✅ 準拠 |
| GET | `/api/stocks/<int:stock_id>` | 特定IDの株価データを取得 | ✅ 準拠 |
| PUT | `/api/stocks/<int:stock_id>` | 株価データを更新 | ✅ 準拠 |
| DELETE | `/api/stocks/<int:stock_id>` | 株価データを削除 | ✅ 準拠 |
| POST | `/api/stocks/test-data` | テスト用サンプルデータ作成 | ⚠️ 部分的 |

### 3. 一括データ取得API（Blueprint: bulk_api）

**プレフィックス**: `/api/bulk/`

| メソッド | パス | 用途 | RESTful準拠 |
|---------|------|------|------------|
| POST | `/api/bulk/start` | 一括取得ジョブを開始 | ✅ 準拠 |
| GET | `/api/bulk/status/<job_id>` | ジョブステータスを取得 | ✅ 準拠 |
| POST | `/api/bulk/stop/<job_id>` | ジョブをキャンセル | ⚠️ 部分的 |
| GET | `/api/bulk/jpx-sequential/get-symbols` | JPX銘柄コード一覧を取得 | ⚠️ 部分的 |
| POST | `/api/bulk/jpx-sequential/start` | JPX全銘柄順次取得を開始 | ✅ 準拠 |

### 4. JPX銘柄マスタ管理API（Blueprint: stock_master_api）

**プレフィックス**: `/api/stock-master/`

| メソッド | パス | 用途 | RESTful準拠 |
|---------|------|------|------------|
| POST | `/api/stock-master/update` | JPX銘柄マスタを更新 | ⚠️ 部分的 |
| GET | `/api/stock-master/list` | JPX銘柄マスタ一覧を取得 | ✅ 準拠 |
| GET | `/api/stock-master/status` | 銘柄マスタ状態を取得 | ✅ 準拠 |

### 5. システム監視API（Blueprint: system_api）

**プレフィックス**: `/api/system/`

| メソッド | パス | 用途 | RESTful準拠 |
|---------|------|------|------------|
| POST | `/api/system/db-connection-test` | データベース接続テスト | ⚠️ 部分的 |
| POST | `/api/system/api-connection-test` | Yahoo Finance API接続テスト | ⚠️ 部分的 |
| GET | `/api/system/health-check` | 統合ヘルスチェック | ✅ 準拠 |

---

## エンドポイント詳細

### 株価データ管理API

#### `POST /api/fetch-data`

**用途**: Yahoo Financeから株価データを取得し、データベースに保存

**リクエスト**:
```json
{
  "symbol": "7203.T",
  "period": "1mo",
  "interval": "1d"
}
```

**パラメータ**:
- `symbol` (string, 必須): 銘柄コード
- `period` (string, オプション): 取得期間（デフォルト: "1mo"）
- `interval` (string, オプション): 時間軸（デフォルト: "1d"）

**対応時間軸**: 1m, 2m, 5m, 15m, 30m, 60m, 90m, 1h, 1d, 5d, 1wk, 1mo, 3mo

**レスポンス（成功）**:
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
      "start": "2025-09-22",
      "end": "2025-10-22"
    },
    "table_name": "stocks_1d"
  }
}
```

**エラーコード**:
- `INVALID_INTERVAL`: 無効な足種別
- `INVALID_SYMBOL`: 無効な銘柄コード
- `DATA_FETCH_ERROR`: データ取得失敗
- `EXTERNAL_API_ERROR`: Yahoo Finance API エラー

---

#### `GET /api/stocks`

**用途**: 保存済み株価データを取得（ページネーション対応）

**クエリパラメータ**:
- `symbol` (string, オプション): 銘柄コードでフィルタ
- `interval` (string, オプション): 時間軸（デフォルト: "1d"）
- `limit` (integer, オプション): 取得件数（デフォルト: 100）
- `offset` (integer, オプション): オフセット（デフォルト: 0）
- `start_date` (string, オプション): 開始日（YYYY-MM-DD）
- `end_date` (string, オプション): 終了日（YYYY-MM-DD）

**レスポンス（成功）**:
```json
{
  "success": true,
  "data": [
    {
      "id": 1,
      "symbol": "7203.T",
      "date": "2025-10-22",
      "open": 2500.0,
      "high": 2550.0,
      "low": 2480.0,
      "close": 2530.0,
      "volume": 1500000
    }
  ],
  "metadata": {
    "interval": "1d",
    "table_name": "stocks_1d"
  },
  "pagination": {
    "total": 100,
    "limit": 100,
    "offset": 0,
    "has_next": false
  }
}
```

---

#### `POST /api/stocks`, `GET /api/stocks/<int:stock_id>`, `PUT /api/stocks/<int:stock_id>`, `DELETE /api/stocks/<int:stock_id>`

**用途**: RESTful CRUD操作

これらのエンドポイントは標準的なRESTful設計に準拠しており、株価データの基本的なCRUD操作を提供します。

---

### 一括データ取得API

#### `POST /api/bulk/start`

**用途**: 複数銘柄の一括取得ジョブを開始

**認証**: X-API-KEY ヘッダー（環境変数で設定されている場合のみ必須）

**リクエスト**:
```json
{
  "symbols": ["7203.T", "6758.T", "9984.T"],
  "interval": "1d",
  "period": "1mo"
}
```

**レスポンス（成功）**:
```json
{
  "success": true,
  "job_id": "job-1729594800000",
  "batch_db_id": 123,
  "status": "accepted"
}
```

**制限**:
- 1回のリクエストで最大5000銘柄まで
- レート制限あり（デフォルト: 60回/分）

---

#### `GET /api/bulk/status/<job_id>`

**用途**: ジョブの進捗状況を取得

**レスポンス（成功）**:
```json
{
  "success": true,
  "job": {
    "id": "job-1729594800000",
    "status": "running",
    "progress": {
      "total": 100,
      "processed": 50,
      "successful": 45,
      "failed": 5,
      "progress_percentage": 50.0
    },
    "created_at": 1729594800.0,
    "updated_at": 1729594850.0
  }
}
```

**ステータス値**:
- `running`: 実行中
- `completed`: 完了
- `failed`: 失敗
- `cancel_requested`: キャンセル要求済み

---

#### `POST /api/bulk/jpx-sequential/start`

**用途**: JPX全銘柄の8種類の時間軸を順次取得

**時間軸定義**:
1. 1分足（5日間）
2. 5分足（1ヶ月）
3. 15分足（1ヶ月）
4. 30分足（1ヶ月）
5. 1時間足（2年）
6. 1日足（最大期間）
7. 週足（最大期間）
8. 月足（最大期間）

**リクエスト**:
```json
{
  "symbols": ["7203.T", "6758.T", ...]
}
```

**レスポンス（成功）**:
```json
{
  "success": true,
  "job_id": "jpx-seq-1729594800000",
  "batch_db_id": 124,
  "status": "accepted",
  "total_symbols": 3800,
  "intervals": [...]
}
```

---

### JPX銘柄マスタ管理API

#### `POST /api/stock-master/update`

**用途**: JPXから最新の銘柄一覧を取得してデータベースを更新

**認証**: X-API-KEY ヘッダー（環境変数で設定されている場合のみ必須）

**リクエスト**:
```json
{
  "update_type": "manual"
}
```

**レスポンス（成功）**:
```json
{
  "status": "success",
  "message": "銘柄マスタの更新が完了しました",
  "data": {
    "update_type": "manual",
    "total_stocks": 3800,
    "added_stocks": 50,
    "updated_stocks": 3700,
    "removed_stocks": 10,
    "status": "success"
  }
}
```

---

#### `GET /api/stock-master/list`

**用途**: データベースに保存されている銘柄マスタ一覧を取得

**クエリパラメータ**:
- `is_active` (string, オプション): 有効フラグ（true/false/all、デフォルト: true）
- `market_category` (string, オプション): 市場区分でフィルタ
- `limit` (integer, オプション): 取得件数上限（1-1000、デフォルト: 100）
- `offset` (integer, オプション): オフセット（デフォルト: 0）

---

#### `GET /api/stock-master/status`

**用途**: 銘柄マスタの現在の状態と最新の更新履歴を取得

**レスポンス（成功）**:
```json
{
  "status": "success",
  "message": "銘柄マスタ状態を取得しました",
  "data": {
    "total_stocks": 3800,
    "active_stocks": 3790,
    "inactive_stocks": 10,
    "last_update": {...}
  }
}
```

---

### システム監視API

#### `POST /api/system/db-connection-test`

**用途**: データベース接続テスト

**レスポンス（成功）**:
```json
{
  "success": true,
  "message": "データベース接続正常",
  "responseTime": 45.23,
  "details": {
    "host": "localhost",
    "database": "stock_analyzer",
    "tableExists": true,
    "connectionCount": 3
  },
  "timestamp": "2025-10-22T10:00:00Z"
}
```

---

#### `POST /api/system/api-connection-test`

**用途**: Yahoo Finance API接続テスト

**リクエスト**:
```json
{
  "symbol": "7203.T"
}
```

**レスポンス（成功）**:
```json
{
  "success": true,
  "message": "Yahoo Finance API接続正常",
  "responseTime": 1234.56,
  "details": {
    "symbol": "7203.T",
    "dataAvailable": true,
    "dataPoints": 5
  },
  "timestamp": "2025-10-22T10:00:00Z"
}
```

---

#### `GET /api/system/health-check`

**用途**: データベースとYahoo Finance APIの両方の状態を統合チェック

**レスポンス（成功）**:
```json
{
  "status": "healthy",
  "timestamp": "2025-10-22T10:00:00Z",
  "services": {
    "database": {
      "status": "healthy",
      "message": "接続正常"
    },
    "yahoo_finance_api": {
      "status": "healthy",
      "message": "API接続正常"
    }
  }
}
```

**ステータス値**:
- `healthy`: すべて正常
- `degraded`: 一部警告あり
- `error`: エラーあり

---

## RESTful原則との整合性チェック

### ✅ RESTful原則に準拠しているエンドポイント

以下のエンドポイントは標準的なRESTful設計に準拠しています：

1. **株価データCRUD操作**
   - `POST /api/stocks` - リソース作成
   - `GET /api/stocks` - コレクション取得
   - `GET /api/stocks/<id>` - 個別リソース取得
   - `PUT /api/stocks/<id>` - リソース更新
   - `DELETE /api/stocks/<id>` - リソース削除

2. **一括処理ジョブ管理**
   - `POST /api/bulk/start` - ジョブ作成
   - `GET /api/bulk/status/<job_id>` - ジョブ状態取得
   - `POST /api/bulk/jpx-sequential/start` - 順次処理ジョブ作成

3. **銘柄マスタ照会**
   - `GET /api/stock-master/list` - リスト取得
   - `GET /api/stock-master/status` - ステータス取得

4. **システム監視**
   - `GET /api/system/health-check` - ヘルスチェック

---

### ⚠️ RESTful原則に部分的に準拠しているエンドポイント

以下のエンドポイントは機能的には問題ないものの、RESTful設計の観点から改善の余地があります：

#### 1. `POST /api/fetch-data`

**問題点**:
- データ取得と保存の2つの操作を同時に実行
- RESTfulでは、データ取得はGET、リソース作成はPOSTとして分離すべき

**推奨改善案**:
```
GET /api/external/stock-data?symbol=7203.T&period=1mo&interval=1d  # データ取得
POST /api/stocks  # 保存
```

または

```
POST /api/stocks/import  # インポート操作として明示
```

**現状維持の理由**:
- シンプルな操作フローを維持
- 既存のフロントエンドとの互換性

---

#### 2. `POST /api/bulk/stop/<job_id>`

**問題点**:
- キャンセル操作は状態変更なので、RESTfulではPATCHまたはPUTが適切

**推奨改善案**:
```
PATCH /api/bulk/jobs/<job_id>
{
  "status": "cancelled"
}
```

または

```
DELETE /api/bulk/jobs/<job_id>  # ジョブ削除
```

---

#### 3. `POST /api/stock-master/update`

**問題点**:
- 更新操作だが、リソースを新規作成しているわけではない
- RESTfulではPATCHまたはPUTが適切

**推奨改善案**:
```
PATCH /api/stock-master
{
  "update_type": "manual"
}
```

または

```
POST /api/stock-master/sync  # 同期操作として明示
```

---

#### 4. `GET /api/bulk/jpx-sequential/get-symbols`

**問題点**:
- GETメソッドなのにアクション名 "get-symbols" が冗長
- RESTfulではリソース名を使用すべき

**推奨改善案**:
```
GET /api/bulk/jpx-sequential/symbols
```

または

```
GET /api/stock-master/symbols?source=jpx&format=yfinance
```

---

#### 5. `POST /api/system/db-connection-test` および `POST /api/system/api-connection-test`

**問題点**:
- テスト操作は副作用がないため、GETが適切
- ただし、実行トリガーの意味合いでPOSTも許容範囲

**推奨改善案**:
```
GET /api/system/connections/database/test
GET /api/system/connections/api/test
```

---

#### 6. `POST /api/stocks/test-data`

**問題点**:
- テストデータ作成は開発・デバッグ用途
- 本番環境では無効化すべき

**推奨改善案**:
- 環境変数でエンドポイントの有効/無効を制御
- または開発環境専用のプレフィックスを使用（例: `/api/dev/test-data`）

---

### ❌ RESTful原則に準拠していないエンドポイント

現時点では、重大な違反はありません。上記の部分的準拠エンドポイントの改善で十分です。

---

## 非推奨・削除予定エンドポイント

### 現時点で非推奨のエンドポイント

該当なし

### 将来的に削除予定のエンドポイント

#### 1. `/api/test-connection`

**理由**:
- `/api/system/db-connection-test` および `/api/system/health-check` で代替可能
- 機能が重複している

**削除予定バージョン**: v2.0.0

**移行手順**:
```
旧: GET /api/test-connection
新: GET /api/system/health-check
新: POST /api/system/db-connection-test
```

---

#### 2. `/api/stocks/test-data`

**理由**:
- 開発・デバッグ専用機能
- 本番環境では不要

**削除予定バージョン**: v2.0.0

**代替案**:
- マイグレーションスクリプトでテストデータを投入
- または開発環境専用のエンドポイントとして `/api/dev/test-data` に移動

---

## 推奨される改善事項

### 1. RESTful設計の統一

**優先度**: 中

**内容**:
- 部分的準拠エンドポイントを完全準拠に改善
- HTTPメソッドの適切な使用（GET: 取得、POST: 作成、PUT/PATCH: 更新、DELETE: 削除）
- アクション名ではなくリソース名を使用

**実装時期**: v1.1.0

---

### 2. APIバージョニング

**優先度**: 中

**内容**:
- APIのバージョン管理を導入
- 例: `/api/v1/stocks`, `/api/v2/stocks`

**メリット**:
- 後方互換性を維持しながら新機能を追加可能
- エンドポイントの段階的な移行が可能

**実装時期**: v2.0.0

---

### 3. 認証・認可の統一

**優先度**: 高

**内容**:
- 現在は環境変数によるオプショナル認証
- 本番環境では必須にすべき

**推奨実装**:
- JWT認証
- APIキーによるレート制限
- ロールベースアクセス制御（RBAC）

**実装時期**: v1.2.0

---

### 4. エラーレスポンスの統一

**優先度**: 中

**内容**:
- 現在は概ね統一されているが、一部のエラーハンドリングが異なる
- RFC 7807（Problem Details for HTTP APIs）の採用を検討

**実装時期**: v1.1.0

---

### 5. ページネーションの統一

**優先度**: 低

**内容**:
- 現在は `limit` と `offset` を使用
- カーソルベースページネーションの導入を検討（大量データに対応）

**実装時期**: v2.0.0以降

---

### 6. ドキュメント自動生成

**優先度**: 中

**内容**:
- OpenAPI（Swagger）仕様の導入
- APIドキュメントの自動生成

**メリット**:
- APIの一覧性向上
- クライアントコード生成が可能
- API変更の追跡が容易

**実装時期**: v1.2.0

---

## サービスモジュール対応表

### 株価データ管理API
- `POST /api/fetch-data` → `app/services/stock_data/orchestrator.py`（内部で `fetcher.py` / `saver.py` を使用）
- `GET /api/stocks` → モデル経由のデータ参照（時間軸判定に `stock_data/timeframe_utils` を利用）
- `POST /api/stocks` / `PUT /api/stocks/<id>` / `DELETE /api/stocks/<id>` → `app/services/stock_data/saver.py`（UPSERT/削除）

### 一括データ取得API（bulk_api）
- `POST /api/bulk/start` → `app/services/bulk/bulk_service.py`
- `GET /api/bulk/status/<job_id>` → `app/services/bulk/bulk_service.py`
- `POST /api/bulk/stop/<job_id>` → `app/services/bulk/bulk_service.py`
- `GET /api/bulk/jpx-sequential/get-symbols` → `app/services/jpx/jpx_stock_service.py`
- `POST /api/bulk/jpx-sequential/start` → `app/services/bulk/bulk_service.py`（銘柄取得は `jpx/jpx_stock_service.py` 連携）

### JPX銘柄マスタ（stock_master_api）
- `POST /api/stock-master/update` → `app/services/jpx/jpx_stock_service.py`
- `GET /api/stock-master/list` → モデル参照（マスタ管理は `jpx/jpx_stock_service.py`）
- `GET /api/stock-master/status` → `app/services/jpx/jpx_stock_service.py`

### システム監視（system_api）
- `POST /api/system/db-connection-test` → DB接続確認（共通例外処理は `common/error_handler.py`）
- `POST /api/system/api-connection-test` → Yahoo Finance接続確認（同上）
- `GET /api/system/health-check` → アプリ全体の統合チェック（同上）

## まとめ

### 現状の評価

**全体的な評価**: ⭐⭐⭐⭐☆（4/5）

**良い点**:
- 株価データCRUD操作は完全にRESTful準拠
- エンドポイントの命名が直感的で理解しやすい
- エラーハンドリングが適切に実装されている
- 認証がオプショナルで開発環境に優しい

**改善が必要な点**:
- 一部のエンドポイントでHTTPメソッドの使い方が非標準的
- アクション名を含むエンドポイントが一部存在
- APIバージョニングが未実装
- 本番環境向けの認証・認可が不十分

---

### 今後のロードマップ

#### v1.1.0（短期）
- 部分的準拠エンドポイントの改善
- エラーレスポンスの完全統一
- 非推奨エンドポイントの警告追加

#### v1.2.0（中期）
- 認証・認可の強化
- OpenAPI仕様の導入
- APIドキュメント自動生成

#### v2.0.0（長期）
- APIバージョニング導入
- 非推奨エンドポイントの削除
- カーソルベースページネーション
- 完全なRESTful準拠

---

## 参考資料

- [RESTful API Design Best Practices](https://restfulapi.net/)
- [RFC 7807: Problem Details for HTTP APIs](https://tools.ietf.org/html/rfc7807)
- [OpenAPI Specification](https://swagger.io/specification/)
- [既存API仕様書](../api/api_specification.md)
- [プロジェクトアーキテクチャ](./project_architecture.md)
