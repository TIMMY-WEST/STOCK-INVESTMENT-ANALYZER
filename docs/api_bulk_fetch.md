# 全銘柄一括取得API（Bulk Fetch API）

このドキュメントは、Issue #50 に基づき実装された一括取得APIの仕様をまとめたものです。

## 概要
- 複数銘柄を並列で取得・保存するジョブを開始し、進捗と状態を取得できます。
- 認証はヘッダ `X-API-KEY` に設定したAPIキーで行います。
- 簡易レート制限（1分あたりのリクエスト数）に対応しています。

## エンドポイント

### POST `/api/bulk-fetch/start`
- 説明: 一括取得ジョブを開始します。
- 認証: 必須（`X-API-KEY`）
- ボディ例:
```json
{
  "symbols": ["7203.T", "6758.T"],
  "interval": "1d",
  "period": "1mo"
}
```
- レスポンス例:
```json
{
  "success": true,
  "job_id": "job-1720000000000",
  "status": "accepted"
}
```

### GET `/api/bulk-fetch/status/{job_id}`
- 説明: ジョブの進捗と状態を取得します。
- 認証: 必須（`X-API-KEY`）
- レスポンス例:
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
    }
  }
}
```

### POST `/api/bulk-fetch/stop/{job_id}`
- 説明: ジョブのキャンセルを要求します（簡易実装）。
- 認証: 必須（`X-API-KEY`）

## 認証・レート制限
- `.env` に `API_KEY` を設定してください。
- `.env` に `RATE_LIMIT_PER_MINUTE` を設定することでレート制限を調整できます（デフォルト: 60）。

## 進捗通知（WebSocket）
- 現在の実装は進捗のREST取得に対応しています。
- WebSocketによるリアルタイム通知は `flask_socketio` の導入後に有効化予定です（コードに拡張用の土台あり）。

## 注意事項
- 外部API（Yahoo Finance）への大量アクセスとなるため、運用時はレート制限の設定を慎重に行ってください。
- バックグラウンド処理は簡易なスレッド実行です。大規模運用ではキュー（RQ/Celery等）の採用を検討してください。