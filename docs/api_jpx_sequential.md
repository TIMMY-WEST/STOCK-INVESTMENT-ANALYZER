# JPX全銘柄自動取得API仕様書

## 概要

JPX全銘柄の株価データを8種類の時間軸で順次自動取得するAPI機能です。
1つのボタン操作で、以下の8種類のデータ取得を順次実行します。

## 実行される時間軸

1. **1分足、5日間** - `interval=1m, period=5d`
2. **5分足、1ヶ月** - `interval=5m, period=1mo`
3. **15分足、1ヶ月** - `interval=15m, period=1mo`
4. **30分足、1ヶ月** - `interval=30m, period=1mo`
5. **1時間足、2年** - `interval=1h, period=2y`
6. **1日足、最大期間** - `interval=1d, period=max`
7. **週足、最大期間** - `interval=1wk, period=max`
8. **月足、最大期間** - `interval=1mo, period=max`

## エンドポイント

### 1. JPX銘柄一覧取得

JPX銘柄マスタから有効な銘柄コード一覧を取得します。

**エンドポイント:** `GET /api/bulk/jpx-sequential/get-symbols`

**リクエストパラメータ:**
```
- market_category (optional): 市場区分でフィルタ
- limit (optional): 取得件数上限（デフォルト: 5000、最大: 5000）
```

**レスポンス例:**
```json
{
  "success": true,
  "symbols": ["7203.T", "6758.T", "9984.T", ...],
  "total": 100,
  "market_category": null
}
```

**cURLサンプル:**
```bash
# 全銘柄取得（最大5000件）
curl -X GET "http://127.0.0.1:8000/api/bulk/jpx-sequential/get-symbols?limit=5000"

# プライム市場のみ取得
curl -X GET "http://127.0.0.1:8000/api/bulk/jpx-sequential/get-symbols?market_category=プライム&limit=100"
```

### 2. JPX全銘柄順次取得開始

JPX全銘柄の8種類時間軸データを順次取得するジョブを開始します。

**エンドポイント:** `POST /api/bulk/jpx-sequential/start`

**リクエストボディ:**
```json
{
  "symbols": ["7203.T", "6758.T", "9984.T", ...]
}
```

**レスポンス例:**
```json
{
  "success": true,
  "job_id": "jpx-seq-1728901234567",
  "batch_db_id": 123,
  "status": "accepted",
  "total_symbols": 100,
  "intervals": [
    {"interval": "1m", "period": "5d", "name": "1分足、5日間"},
    {"interval": "5m", "period": "1mo", "name": "5分足、1ヶ月"},
    {"interval": "15m", "period": "1mo", "name": "15分足、1ヶ月"},
    {"interval": "30m", "period": "1mo", "name": "30分足、1ヶ月"},
    {"interval": "1h", "period": "2y", "name": "1時間足、2年"},
    {"interval": "1d", "period": "max", "name": "1日足、最大期間"},
    {"interval": "1wk", "period": "max", "name": "週足、最大期間"},
    {"interval": "1mo", "period": "max", "name": "月足、最大期間"}
  ]
}
```

**cURLサンプル:**
```bash
curl -X POST "http://127.0.0.1:8000/api/bulk/jpx-sequential/start" \
  -H "Content-Type: application/json" \
  -d '{
    "symbols": ["7203.T", "6758.T", "9984.T"]
  }'
```

### 3. ジョブステータス取得

実行中のジョブのステータスと進捗を取得します。

**エンドポイント:** `GET /api/bulk/status/{job_id}`

**レスポンス例（実行中）:**
```json
{
  "success": true,
  "job": {
    "id": "jpx-seq-1728901234567",
    "type": "jpx_sequential",
    "status": "running",
    "total_symbols": 100,
    "total_intervals": 8,
    "completed_intervals": 2,
    "current_interval": "15分足、1ヶ月",
    "current_interval_index": 3,
    "interval_results": [
      {
        "interval": "1m",
        "period": "5d",
        "name": "1分足、5日間",
        "success": true,
        "summary": {
          "total_symbols": 100,
          "successful": 95,
          "failed": 5,
          "total_downloaded": 47500,
          "total_saved": 47500,
          "duration_seconds": 125.5
        }
      },
      {
        "interval": "5m",
        "period": "1mo",
        "name": "5分足、1ヶ月",
        "success": true,
        "summary": {
          "total_symbols": 100,
          "successful": 98,
          "failed": 2,
          "total_downloaded": 89600,
          "total_saved": 89600,
          "duration_seconds": 203.2
        }
      }
    ],
    "created_at": 1728901234.567,
    "updated_at": 1728901500.123
  }
}
```

**レスポンス例（完了）:**
```json
{
  "success": true,
  "job": {
    "id": "jpx-seq-1728901234567",
    "type": "jpx_sequential",
    "status": "completed",
    "total_symbols": 100,
    "total_intervals": 8,
    "completed_intervals": 8,
    "summary": {
      "total_intervals": 8,
      "completed_intervals": 8,
      "successful_intervals": 8,
      "failed_intervals": 0,
      "interval_results": [
        {
          "interval": "1m",
          "period": "5d",
          "name": "1分足、5日間",
          "success": true,
          "summary": {
            "total_symbols": 100,
            "successful": 95,
            "failed": 5,
            "total_downloaded": 47500,
            "total_saved": 47500,
            "duration_seconds": 125.5
          }
        },
        ...
      ]
    },
    "created_at": 1728901234.567,
    "updated_at": 1728902500.123
  }
}
```

**cURLサンプル:**
```bash
curl -X GET "http://127.0.0.1:8000/api/bulk/status/jpx-seq-1728901234567"
```

## WebSocket通知

ジョブの進捗はWebSocketでリアルタイムに通知されます。

### イベント: `jpx_interval_complete`

各時間軸の処理が完了した時に送信されます。

**ペイロード例:**
```json
{
  "job_id": "jpx-seq-1728901234567",
  "batch_db_id": 123,
  "interval_index": 3,
  "total_intervals": 8,
  "interval_result": {
    "interval": "15m",
    "period": "1mo",
    "name": "15分足、1ヶ月",
    "success": true,
    "summary": {
      "total_symbols": 100,
      "successful": 97,
      "failed": 3,
      "total_downloaded": 69700,
      "total_saved": 69700,
      "duration_seconds": 180.3
    }
  }
}
```

### イベント: `jpx_complete`

全時間軸の処理が完了した時に送信されます。

**ペイロード例:**
```json
{
  "job_id": "jpx-seq-1728901234567",
  "batch_db_id": 123,
  "summary": {
    "total_intervals": 8,
    "completed_intervals": 8,
    "successful_intervals": 8,
    "failed_intervals": 0,
    "interval_results": [...]
  }
}
```

## 使用例

### Python

```python
import requests
import time

BASE_URL = "http://127.0.0.1:8000"

# 1. JPX銘柄一覧を取得
response = requests.get(f"{BASE_URL}/api/bulk/jpx-sequential/get-symbols?limit=100")
symbols = response.json()["symbols"]

# 2. 順次取得ジョブを開始
response = requests.post(
    f"{BASE_URL}/api/bulk/jpx-sequential/start",
    json={"symbols": symbols}
)
job_id = response.json()["job_id"]

# 3. ジョブの進捗を監視
while True:
    response = requests.get(f"{BASE_URL}/api/bulk/status/{job_id}")
    job = response.json()["job"]

    if job["status"] == "completed":
        print("完了!")
        print(f"成功した時間軸: {job['summary']['successful_intervals']}/8")
        break
    elif job["status"] == "failed":
        print(f"エラー: {job['error']}")
        break

    print(f"進捗: {job['completed_intervals']}/8 - {job.get('current_interval', '')}")
    time.sleep(10)
```

### JavaScript (fetch API)

```javascript
const BASE_URL = "http://127.0.0.1:8000";

async function runJpxSequentialFetch() {
  // 1. JPX銘柄一覧を取得
  const symbolsResponse = await fetch(
    `${BASE_URL}/api/bulk/jpx-sequential/get-symbols?limit=100`
  );
  const { symbols } = await symbolsResponse.json();

  // 2. 順次取得ジョブを開始
  const startResponse = await fetch(
    `${BASE_URL}/api/bulk/jpx-sequential/start`,
    {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ symbols })
    }
  );
  const { job_id } = await startResponse.json();

  // 3. ジョブの進捗を監視
  const checkInterval = setInterval(async () => {
    const statusResponse = await fetch(
      `${BASE_URL}/api/bulk/status/${job_id}`
    );
    const { job } = await statusResponse.json();

    if (job.status === "completed") {
      console.log("完了!");
      console.log(
        `成功した時間軸: ${job.summary.successful_intervals}/8`
      );
      clearInterval(checkInterval);
    } else if (job.status === "failed") {
      console.error(`エラー: ${job.error}`);
      clearInterval(checkInterval);
    } else {
      console.log(
        `進捗: ${job.completed_intervals}/8 - ${job.current_interval || ""}`
      );
    }
  }, 10000);
}

runJpxSequentialFetch();
```

## エラーハンドリング

### エラーレスポンス形式

```json
{
  "success": false,
  "error": "ERROR_CODE",
  "message": "エラーメッセージの詳細"
}
```

### 主なエラーコード

| エラーコード | HTTPステータス | 説明 |
|-------------|---------------|------|
| VALIDATION_ERROR | 400 | リクエストパラメータが不正 |
| REQUEST_TOO_LARGE | 413 | 銘柄数が上限（5000件）を超過 |
| NOT_FOUND | 404 | 指定されたジョブが見つからない |
| SERVICE_ERROR | 500 | サービスエラー |
| INTERNAL_ERROR | 500 | 内部エラー |

## パフォーマンス

### 処理時間の目安

- **銘柄数:** 100銘柄
- **時間軸:** 8種類
- **推定処理時間:** 約20〜30分（ネットワーク速度、サーバー負荷に依存）

### 並列処理

- 各時間軸内ではバッチ処理（100銘柄ずつ並列取得）
- 時間軸間は順次実行（1分足 → 5分足 → ... → 月足）

## 注意事項

1. **レート制限:** Yahoo Finance APIのレート制限に注意してください
2. **データ量:** 全銘柄×8時間軸のデータ量は非常に大きくなります
3. **処理時間:** 数千銘柄の場合、完了まで数時間かかることがあります
4. **エラー処理:** 一部の時間軸で失敗しても、他の時間軸の処理は継続されます

## 関連ドキュメント

- [バッチ処理API仕様書](./api_bulk_fetch.md)
- [銘柄マスタAPI仕様書](./api_stock_master.md)
