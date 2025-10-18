---
category: feature
ai_context: high
last_updated: 2025-10-18
related_docs:
  - api/api_specification.md
  - architecture/database_design.md
---

# JPX全銘柄8種類順次自動取得システム完全ガイド

## 📋 目次

- [システム概要](#システム概要)
- [機能の特徴](#機能の特徴)
- [使い方](#使い方)
- [API仕様](#api仕様)
- [WebSocket通知](#websocket通知)
- [JPX連携仕様](#jpx連携仕様)
- [システム設計](#システム設計)
- [運用ガイド](#運用ガイド)
- [トラブルシューティング](#トラブルシューティング)

---

## システム概要

JPX（日本取引所グループ）に上場している全銘柄の株価データを、**8種類の時間軸で順次自動的に取得**する強力な機能です。

**たった1つのボタンをクリックするだけで、すべての作業が自動で完了します。**

### 取得される8種類の時間軸

| 番号 | 時間軸 | 取得期間 | 用途 | interval | period |
|------|--------|----------|------|----------|--------|
| 1 | 1分足 | 5日間 | デイトレード、超短期分析 | 1m | 5d |
| 2 | 5分足 | 1ヶ月 | 短期トレード | 5m | 1mo |
| 3 | 15分足 | 1ヶ月 | スイングトレード準備 | 15m | 1mo |
| 4 | 30分足 | 1ヶ月 | 中短期分析 | 30m | 1mo |
| 5 | 1時間足 | 2年 | スイングトレード | 1h | 2y |
| 6 | 1日足 | 最大期間 | 中長期投資 | 1d | max |
| 7 | 週足 | 最大期間 | 長期投資 | 1wk | max |
| 8 | 月足 | 最大期間 | 超長期投資 | 1mo | max |

---

## 機能の特徴

### 🚀 ワンクリック操作

1つのボタンで8種類すべての時間軸データを自動取得：
- ボタン1つで処理開始
- 銘柄一覧の取得から各時間軸のデータ取得まで、すべて自動
- 進捗状況をリアルタイムで確認可能

### ✅ 各時間軸の実行結果を可視化

- 各時間軸ごとの成功/失敗銘柄数
- ダウンロードしたデータ件数
- データベースに保存した件数
- 処理時間
- エラーが発生した場合の詳細情報

### 📊 並列処理とバッチ処理

- 各時間軸内ではバッチ処理（100銘柄ずつ並列取得）
- 時間軸間は順次実行（1分足 → 5分足 → ... → 月足）

---

## 使い方

### ステップ1: Webアプリケーションにアクセス

1. サーバーを起動:
```bash
python app/app.py
```

2. ブラウザで以下のURLにアクセス:
```
http://127.0.0.1:8000
```

### ステップ2: 設定を選択

「🚀 JPX全銘柄8種類順次自動取得」セクションで、以下の設定を選択します：

#### 取得銘柄数

|  選択肢  |  説明  |  推奨用途  |
|----------|--------|------------|
| 10銘柄（テスト用） | 動作確認用 | 初めて使う場合のテスト |
| 50銘柄 | 小規模取得 | 特定の銘柄グループ |
| 100銘柄 | 中規模取得（デフォルト） | バランスの良い選択 |
| 500銘柄 | 大規模取得 | 広範囲の分析 |
| 1000銘柄 | 超大規模取得 | 包括的な分析 |
| 5000銘柄（全銘柄） | 完全取得 | すべての上場銘柄 |

#### 市場区分（オプション）

| 選択肢 | 説明 |
|--------|------|
| 全市場 | すべての市場の銘柄を取得 |
| プライム市場のみ | 東証プライム市場の銘柄のみ |
| スタンダード市場のみ | 東証スタンダード市場の銘柄のみ |
| グロース市場のみ | 東証グロース市場の銘柄のみ |

### ステップ3: 取得開始

**「🚀 8種類データ順次自動取得 開始」ボタンをクリック**

これだけで、以下の処理がすべて自動で実行されます：

1. JPX銘柄マスタから銘柄一覧を取得
2. 1分足データの取得（全銘柄）
3. 5分足データの取得（全銘柄）
4. 15分足データの取得（全銘柄）
5. 30分足データの取得（全銘柄）
6. 1時間足データの取得（全銘柄）
7. 1日足データの取得（全銘柄）
8. 週足データの取得（全銘柄）
9. 月足データの取得（全銘柄）

### ステップ4: 進捗確認

実行中は以下の情報がリアルタイムで表示されます：

#### 処理状況
- **対象銘柄数**: 取得する銘柄の総数
- **完了時間軸**: 完了した時間軸数 / 総時間軸数（8）
- **現在の時間軸**: 現在処理中の時間軸

#### 各時間軸の実行結果

各時間軸の処理が完了すると、以下の情報が表示されます：

```
✅ 1. 1分足、5日間
   成功: 95 / 100 銘柄
   失敗: 5 銘柄
   ダウンロード: 47,500 件
   保存: 47,500 件
   処理時間: 125.5秒
```

### ステップ5: 結果確認

全時間軸の処理が完了すると、最終結果サマリーが表示されます：

```
✅ 全時間軸のデータ取得が完了しました！

総時間軸数: 8
完了: 8
成功: 8
失敗: 0
```

---

## API仕様

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
      "interval_results": [...]
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

### エラーハンドリング

**エラーレスポンス形式:**
```json
{
  "success": false,
  "error": "ERROR_CODE",
  "message": "エラーメッセージの詳細"
}
```

**主なエラーコード:**

| エラーコード | HTTPステータス | 説明 |
|-------------|---------------|------|
| VALIDATION_ERROR | 400 | リクエストパラメータが不正 |
| REQUEST_TOO_LARGE | 413 | 銘柄数が上限（5000件）を超過 |
| NOT_FOUND | 404 | 指定されたジョブが見つからない |
| SERVICE_ERROR | 500 | サービスエラー |
| INTERNAL_ERROR | 500 | 内部エラー |

---

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

---

## JPX連携仕様

### JPXデータソース

JPX（日本取引所グループ）から最新の上場銘柄情報を自動取得し、システムの銘柄マスタを常に最新状態に保ちます。

#### JPX銘柄一覧ファイル情報
- **ファイル名**: `data_j.xls`
- **URL**: `https://www.jpx.co.jp/markets/statistics-equities/misc/tvdivq0000001vg2-att/data_j.xls`
- **更新頻度**: 月末基準（直近月末の東証上場銘柄一覧）
- **ファイル形式**: Microsoft Excel (.xls)
- **文字エンコード**: Shift_JIS
- **総銘柄数**: 約4,410銘柄（2025年8月29日基準）

#### 市場区分の種類
- **プライム（内国株式）**: 1,618銘柄
- **スタンダード（内国株式）**: 1,571銘柄
- **グロース（内国株式）**: 606銘柄
- **ETF・ETN**: 397銘柄
- **PRO Market**: 148銘柄
- **REIT等**: 63銘柄

### データ保存先

取得したデータは以下のテーブルに保存されます：

- `stocks_1m`: 1分足データ
- `stocks_5m`: 5分足データ
- `stocks_15m`: 15分足データ
- `stocks_30m`: 30分足データ
- `stocks_1h`: 1時間足データ
- `stocks_1d`: 日足データ
- `stocks_1wk`: 週足データ
- `stocks_1mo`: 月足データ

### バッチ実行履歴

Phase 2が有効な場合、実行履歴は `batch_executions` テーブルに保存されます。

---

## システム設計

### アーキテクチャ図

```
[JPX公式サイト]
       ↓ (HTTPSダウンロード)
[JPXデータ取得モジュール]
       ↓
[Excelファイル解析モジュール]
       ↓
[データ検証モジュール]
       ↓
[銘柄マスタ更新モジュール]
       ↓
[順次取得ジョブマネージャー]
       ↓
[BulkDataService (並列処理)]
       ↓
[PostgreSQLデータベース]
```

### コンポーネント構成

```
jpx_integration/
├── downloader.py         # JPXデータダウンロード
├── parser.py            # Excelファイル解析
├── validator.py         # データ検証
├── master_updater.py    # 銘柄マスタ更新
├── sequential_runner.py # 順次取得実行
└── config.py           # JPX連携設定

services/
├── bulk_data_service.py # バルクデータ取得サービス
└── jpx_sequential_service.py # JPX順次取得サービス
```

### 処理フロー

1. **銘柄一覧取得**: JPX銘柄マスタから対象銘柄を取得
2. **ジョブ作成**: 8種類の時間軸処理ジョブを作成
3. **順次実行**: 各時間軸を順番に処理
   - 1分足（5日間）
   - 5分足（1ヶ月）
   - 15分足（1ヶ月）
   - 30分足（1ヶ月）
   - 1時間足（2年）
   - 1日足（最大期間）
   - 週足（最大期間）
   - 月足（最大期間）
4. **進捗通知**: WebSocketで各時間軸完了を通知
5. **結果集計**: 全時間軸の結果をサマリー

---

## 運用ガイド

### 処理時間の目安

| 銘柄数 | 推定処理時間 |
|--------|--------------|
| 10銘柄 | 約2〜3分 |
| 50銘柄 | 約10〜15分 |
| 100銘柄 | 約20〜30分 |
| 500銘柄 | 約2〜3時間 |
| 1000銘柄 | 約4〜6時間 |
| 5000銘柄 | 約100分（1時間40分） |

**注意**: 処理時間はネットワーク速度、サーバー負荷、Yahoo Finance APIのレート制限により変動します。

### パフォーマンス最適化

- **並列処理**: 各時間軸内ではバッチ処理（100銘柄ずつ並列取得）
- **時間軸間は順次実行**: 1分足 → 5分足 → ... → 月足
- **リトライ機能**: 失敗した銘柄は自動リトライ

### 注意事項

1. **レート制限**: Yahoo Finance APIのレート制限に注意してください
2. **データ量**: 全銘柄×8時間軸のデータ量は非常に大きくなります
3. **処理時間**: 数千銘柄の場合、完了まで数時間かかることがあります
4. **エラー処理**: 一部の時間軸で失敗しても、他の時間軸の処理は継続されます

### よくある質問

**Q1: 処理を途中で停止できますか？**

A: はい、「⏸️ 停止」ボタンをクリックすることで、処理を停止できます。ただし、現在処理中の銘柄が完了するまで若干の時間がかかる場合があります。

**Q2: 一部の時間軸でエラーが発生した場合はどうなりますか？**

A: 一部の時間軸でエラーが発生しても、残りの時間軸の処理は継続されます。各時間軸の結果は個別に表示され、どの時間軸が成功/失敗したかを確認できます。

**Q3: 既に取得済みのデータはどうなりますか？**

A: 既存のデータは上書きされます（重複排除機能により、同じ日時のデータは更新されます）。

**Q4: 処理中にブラウザを閉じても大丈夫ですか？**

A: 処理はサーバー側で実行されているため、ブラウザを閉じても処理は継続されます。ただし、進捗の確認ができなくなります。

**Q5: 銘柄マスタが古い場合はどうすれば良いですか？**

A: 「JPX全銘柄自動取得（単一時間軸）」セクションの「JPX銘柄リスト取得 & 全銘柄データ取得開始」ボタンを先に実行して、銘柄マスタを最新化してください。

---

## トラブルシューティング

### エラー: 「銘柄一覧の取得に失敗しました」

**原因**:
- JPX銘柄マスタが空、または設定された市場区分に該当する銘柄がない

**対処法**:
1. 「JPX全銘柄自動取得（単一時間軸）」セクションで銘柄マスタを更新
2. 市場区分の設定を「全市場」に変更

### エラー: 「ジョブの開始に失敗しました」

**原因**:
- サーバーエラー
- データベース接続エラー

**対処法**:
1. サーバーのログを確認
2. データベース接続をテスト（「システム状態」セクションの「接続テスト実行」）
3. サーバーを再起動

### 一部の銘柄でデータ取得が失敗する

**原因**:
- 銘柄コードが無効
- Yahoo Finance APIでデータが提供されていない
- レート制限

**対処法**:
- これは正常な動作です
- 失敗した銘柄は「失敗」としてカウントされ、処理は継続されます
- 失敗銘柄が多い場合は、時間をおいて再試行

### エラーが多発する場合の対処法

以下を確認してください：
- インターネット接続が安定しているか
- Yahoo Finance APIが正常に動作しているか
- サーバーのログを確認（`logs/` ディレクトリ）
- 銘柄数を減らして再試行

---

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

---

## まとめ

この機能を使えば、**たった1回のボタンクリック**で、JPX全銘柄の包括的な株価データを自動取得できます。

各時間軸の実行結果がリアルタイムで可視化されるため、処理の進捗と結果を簡単に確認できます。

ぜひこの強力な機能を活用して、効率的なデータ収集を実現してください！
