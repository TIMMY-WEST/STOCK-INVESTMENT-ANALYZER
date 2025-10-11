# 全銘柄一括取得API（Bulk Fetch API）

このドキュメントは、Issue #50 に基づき実装された一括取得APIの仕様をまとめたものです。

## 概要
- 複数銘柄を並列で取得・保存するジョブを開始し、進捗と状態を取得できます。
- 認証はヘッダ `X-API-KEY` に設定したAPIキーで行います（環境変数 `API_KEY` が未設定の場合は認証スキップ）。
- 簡易レート制限（1分あたりのリクエスト数）に対応しています。

## エンドポイント

### POST `/api/bulk/start`
- 説明: 一括取得ジョブを開始します。
- 認証: 必須（`X-API-KEY`）※環境変数 `API_KEY` が設定されている場合のみ
- リクエストボディ:
```json
{
  "symbols": ["7203.T", "6758.T"],
  "interval": "1d",
  "period": "1mo"
}
```
  - `symbols` (必須): 取得する銘柄コードの配列
  - `interval` (オプション): データの間隔（デフォルト: `1d`）
  - `period` (オプション): データの期間

- 成功レスポンス (202 Accepted):
```json
{
  "success": true,
  "job_id": "job-1720000000000",
  "status": "accepted"
}
```

- エラーレスポンス (400 Bad Request):
```json
{
  "success": false,
  "error": "VALIDATION_ERROR",
  "message": "'symbols' は文字列リストで指定してください"
}
```

- エラーレスポンス (401 Unauthorized):
```json
{
  "success": false,
  "error": "UNAUTHORIZED",
  "message": "APIキーが不正です。ヘッダ 'X-API-KEY' を設定してください"
}
```

- エラーレスポンス (429 Too Many Requests):
```json
{
  "success": false,
  "error": "RATE_LIMIT_EXCEEDED",
  "message": "レート制限を超過しました。しばらく待って再試行してください"
}
```

### GET `/api/bulk/status/{job_id}`
- 説明: ジョブの進捗と状態を取得します。
- 認証: 必須（`X-API-KEY`）※環境変数 `API_KEY` が設定されている場合のみ
- URLパラメータ:
  - `job_id`: ジョブID

- 成功レスポンス (200 OK):
```json
{
  "success": true,
  "job": {
    "id": "job-1720000000000",
    "status": "running",
    "progress": {
      "total": 2,
      "processed": 1,
      "successful": 1,
      "failed": 0,
      "progress_percentage": 50.0
    },
    "created_at": 1720000000.0,
    "updated_at": 1720000050.0
  }
}
```

- ジョブステータス値:
  - `running`: 実行中
  - `completed`: 完了
  - `failed`: 失敗
  - `cancel_requested`: キャンセル要求済み

- 完了時の追加フィールド:
```json
{
  "success": true,
  "job": {
    "id": "job-1720000000000",
    "status": "completed",
    "progress": {...},
    "summary": {
      "total_symbols": 2,
      "successful": 2,
      "failed": 0,
      "duration_seconds": 5.2
    },
    "created_at": 1720000000.0,
    "updated_at": 1720000055.0
  }
}
```

- エラーレスポンス (404 Not Found):
```json
{
  "success": false,
  "error": "NOT_FOUND",
  "message": "指定されたジョブが見つかりません"
}
```

### POST `/api/bulk/stop/{job_id}`
- 説明: ジョブのキャンセルを要求します（簡易実装）。
- 認証: 必須（`X-API-KEY`）※環境変数 `API_KEY` が設定されている場合のみ
- URLパラメータ:
  - `job_id`: ジョブID

- 成功レスポンス (200 OK):
```json
{
  "success": true,
  "message": "キャンセルを受け付けました",
  "job": {
    "id": "job-1720000000000",
    "status": "cancel_requested",
    "progress": {...},
    "created_at": 1720000000.0,
    "updated_at": 1720000030.0
  }
}
```

- エラーレスポンス (404 Not Found):
```json
{
  "success": false,
  "error": "NOT_FOUND",
  "message": "指定されたジョブが見つかりません"
}
```

## 認証・レート制限
- `.env` に `API_KEY` を設定してください。
- `.env` に `RATE_LIMIT_PER_MINUTE` を設定することでレート制限を調整できます（デフォルト: 60）。

## 進捗通知（WebSocket）
- 現在の実装は進捗のREST取得に対応しています。
- WebSocketによるリアルタイム通知は `flask_socketio` の導入後に有効化予定です（コードに拡張用の土台あり）。

## 注意事項
- 外部API（Yahoo Finance）への大量アクセスとなるため、運用時はレート制限の設定を慎重に行ってください。
- バックグラウンド処理は簡易なスレッド実行です。大規模運用ではキュー（RQ/Celery等）の採用を検討してください。