---
category: api
ai_context: high
last_updated: 2025-10-18
related_docs:
  - ../architecture/database_design.md
  - ../architecture/project_architecture.md
  - ../bulk-data-fetch.md
---

# API仕様書

## 概要

株価データ取得システムのAPIエンドポイント仕様書です。
プロジェクトの設計理念（**動作優先・シンプル設計・後から拡張**）に基づき、最小限の機能から開始し、必要に応じて拡張していく方針です。

## 目次

- [API仕様書](#api仕様書)
  - [概要](#概要)
  - [目次](#目次)
  - [基本情報](#基本情報)
  - [APIエンドポイント一覧](#apiエンドポイント一覧)
    - [1. 株価データ取得API](#1-株価データ取得api)
      - [`POST /api/fetch-data`](#post-apifetch-data)
    - [2. 株価データ取得API](#2-株価データ取得api)
      - [`GET /api/stocks`](#get-apistocks)
    - [3. プログレス取得API](#3-プログレス取得api)
      - [`GET /api/progress`](#get-apiprogress)
  - [エラーハンドリング](#エラーハンドリング)
    - [エラーコード一覧](#エラーコード一覧)
    - [共通エラーレスポンス形式](#共通エラーレスポンス形式)
  - [データモデル](#データモデル)
    - [StockData（日足データ）](#stockdata日足データ)
  - [実装優先度](#実装優先度)
    - [優先度: 高（MVP必須）](#優先度-高mvp必須)
    - [優先度: 中（動作確認後）](#優先度-中動作確認後)
    - [優先度: 低（必要になってから）](#優先度-低必要になってから)
  - [技術的制約・考慮事項](#技術的制約考慮事項)
    - [MVP段階での制約](#mvp段階での制約)
    - [Yahoo Finance API制約](#yahoo-finance-api制約)
    - [開発方針](#開発方針)
  - [将来拡張計画（複数時間軸対応）](#将来拡張計画複数時間軸対応)
    - [拡張予定のエンドポイント](#拡張予定のエンドポイント)
      - [分足データAPI（将来拡張）](#分足データapi将来拡張)
      - [週足・月足データAPI（将来拡張）](#週足月足データapi将来拡張)
    - [拡張時のパラメータ](#拡張時のパラメータ)
      - [分足データ取得](#分足データ取得)
      - [時間軸指定パラメータ](#時間軸指定パラメータ)
    - [拡張時の設計方針](#拡張時の設計方針)
  - [実装例（参考）](#実装例参考)
    - [Flask実装例](#flask実装例)

## 基本情報

- **ベースURL**: `http://localhost:8000`
- **Content-Type**: `application/json`
- **認証**: なし（MVP段階）

## APIエンドポイント一覧

### 1. 株価データ取得API

#### `POST /api/fetch-data`

Yahoo Financeから株価データを取得し、データベースに保存します。

**リクエスト**

```json
{
  "symbol": "7203.T",
  "period": "1mo",
  "interval": "1d"
}
```

**リクエスト例（複数時間軸対応）**

```json
// 日足データ取得（従来通り）
{
  "symbol": "7203.T",
  "period": "1y",
  "interval": "1d"
}

// 5分足データ取得（マイルストーン1新機能）
{
  "symbol": "7203.T",
  "period": "1d",
  "interval": "5m"
}

// 最大期間での日足データ取得（マイルストーン1新機能）
{
  "symbol": "7203.T",
  "period": "max",
  "interval": "1d"
}

// 1時間足データ取得（マイルストーン1新機能）
{
  "symbol": "7203.T",
  "period": "1mo",
  "interval": "1h"
}
```

**パラメータ**

| フィールド | 型     | 必須 | 説明                                                         | デフォルト |
| ---------- | ------ | ---- | ------------------------------------------------------------ | ---------- |
| `symbol`   | string | ✓    | 銘柄コード（例：7203.T = トヨタ）                            | -          |
| `period`   | string | -    | 取得期間（1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, **max**） | "1mo"      |
| `interval` | string | -    | 時間軸（1m, 5m, 15m, 30m, 1h, 1d, 1wk, 1mo）               | "1d"       |

**成功レスポンス (200)**

```json
{
  "success": true,
  "message": "データを正常に取得しました",
  "data": {
    "symbol": "7203.T",
    "interval": "1d",
    "period": "1mo",
    "records_count": 30,
    "date_range": {
      "start": "2024-08-09",
      "end": "2024-09-09"
    },
    "table_name": "stocks_1d"
  }
}
```

**レスポンス例（複数時間軸対応）**

```json
// 5分足データ取得レスポンス
{
  "success": true,
  "message": "5分足データを正常に取得しました",
  "data": {
    "symbol": "7203.T",
    "interval": "5m",
    "period": "1d",
    "records_count": 78,
    "date_range": {
      "start": "2024-09-09T09:00:00+09:00",
      "end": "2024-09-09T15:00:00+09:00"
    },
    "table_name": "stocks_5m"
  }
}

// max期間での日足データ取得レスポンス
{
  "success": true,
  "message": "最大期間の日足データを正常に取得しました",
  "data": {
    "symbol": "7203.T",
    "interval": "1d",
    "period": "max",
    "records_count": 2850,
    "date_range": {
      "start": "2010-01-04",
      "end": "2024-09-09"
    },
    "table_name": "stocks_1d"
  }
}
```

**エラーレスポンス**

```json
{
  "success": false,
  "error": "INVALID_SYMBOL",
  "message": "指定された銘柄コードが見つかりません",
  "details": {
    "symbol": "INVALID.T"
  }
}
```

### 2. 株価データ取得API

#### `GET /api/stocks`

保存済みの株価データを取得します。

**クエリパラメータ**

| パラメータ   | 型      | 必須 | 説明                               | デフォルト |
| ------------ | ------- | ---- | ---------------------------------- | ---------- |
| `symbol`     | string  | -    | 銘柄コード（指定時はその銘柄のみ） | -          |
| `interval`   | string  | -    | 時間軸（1m, 5m, 15m, 30m, 1h, 1d, 1wk, 1mo） | "1d"       |
| `limit`      | integer | -    | 取得件数制限                       | 100        |
| `offset`     | integer | -    | オフセット                         | 0          |
| `start_date` | string  | -    | 開始日（YYYY-MM-DD形式）           | -          |
| `end_date`   | string  | -    | 終了日（YYYY-MM-DD形式）           | -          |
| `start_datetime` | string  | -    | 開始日時（分足・時間足のみ、ISO8601形式） | -          |
| `end_datetime`   | string  | -    | 終了日時（分足・時間足のみ、ISO8601形式） | -          |

**リクエスト例**

```
// 日足データ取得（従来通り）
GET /api/stocks?symbol=7203.T&interval=1d&limit=30
GET /api/stocks?interval=1d&limit=10&offset=20
GET /api/stocks?interval=1d&start_date=2024-08-01&end_date=2024-08-31
GET /api/stocks?symbol=7203.T&interval=1d&start_date=2024-08-01&end_date=2024-08-31&limit=50

// 分足・時間足データ取得（マイルストーン1新機能）
GET /api/stocks?symbol=7203.T&interval=5m&limit=100
GET /api/stocks?symbol=7203.T&interval=1h&start_datetime=2024-09-09T09:00:00+09:00&end_datetime=2024-09-09T15:00:00+09:00
GET /api/stocks?symbol=7203.T&interval=15m&limit=50

// 週足・月足データ取得（マイルストーン1新機能）
GET /api/stocks?symbol=7203.T&interval=1wk&limit=52
GET /api/stocks?symbol=7203.T&interval=1mo&start_date=2024-01-01&end_date=2024-12-31
```

**成功レスポンス (200)**

```json
{
  "success": true,
  "data": [
    {
      "id": 1,
      "symbol": "7203.T",
      "date": "2024-09-09",
      "open": 2500.0,
      "high": 2550.0,
      "low": 2480.0,
      "close": 2530.0,
      "volume": 1500000,
      "created_at": "2024-09-09T10:00:00Z"
    }
  ],
  "metadata": {
    "interval": "1d",
    "table_name": "stocks_1d"
  },
  "pagination": {
    "total": 100,
    "limit": 30,
    "offset": 0,
    "has_next": true
  }
}
```

**レスポンス例（複数時間軸対応）**

```json
// 5分足データレスポンス
{
  "success": true,
  "data": [
    {
      "id": 1,
      "symbol": "7203.T",
      "datetime": "2024-09-09T09:00:00+09:00",
      "open": 2500.0,
      "high": 2505.0,
      "low": 2498.0,
      "close": 2503.0,
      "volume": 50000,
      "created_at": "2024-09-09T09:05:00+09:00"
    },
    {
      "id": 2,
      "symbol": "7203.T",
      "datetime": "2024-09-09T09:05:00+09:00",
      "open": 2503.0,
      "high": 2510.0,
      "low": 2500.0,
      "close": 2508.0,
      "volume": 45000,
      "created_at": "2024-09-09T09:10:00+09:00"
    }
  ],
  "metadata": {
    "interval": "5m",
    "table_name": "stocks_5m"
  },
  "pagination": {
    "total": 78,
    "limit": 100,
    "offset": 0,
    "has_next": false
  }
}

// 1時間足データレスポンス
{
  "success": true,
  "data": [
    {
      "id": 1,
      "symbol": "7203.T",
      "datetime": "2024-09-09T09:00:00+09:00",
      "open": 2500.0,
      "high": 2535.0,
      "low": 2495.0,
      "close": 2520.0,
      "volume": 300000,
      "created_at": "2024-09-09T10:00:00+09:00"
    }
  ],
  "metadata": {
    "interval": "1h",
    "table_name": "stocks_1h"
  },
  "pagination": {
    "total": 6,
    "limit": 100,
    "offset": 0,
    "has_next": false
  }
}
```

### 3. プログレス取得API

#### `GET /api/progress`

データ取得処理の進行状況を取得します（将来の拡張用）。

**成功レスポンス (200)**

```json
{
  "success": true,
  "data": {
    "status": "idle",
    "current_symbol": null,
    "progress_percentage": 0,
    "message": "待機中"
  }
}
```

**ステータス値**

| ステータス   | 説明         |
| ------------ | ------------ |
| `idle`       | 待機中       |
| `fetching`   | データ取得中 |
| `processing` | データ処理中 |
| `completed`  | 完了         |
| `error`      | エラー       |

## エラーハンドリング

### エラーコード一覧

| コード               | HTTPステータス | 説明                     |
| -------------------- | -------------- | ------------------------ |
| `INVALID_SYMBOL`     | 400            | 不正な銘柄コード         |
| `INVALID_PERIOD`     | 400            | 不正な期間指定           |
| `INVALID_INTERVAL`   | 400            | 不正な時間軸指定         |
| `INVALID_DATETIME_RANGE` | 400        | 不正な日時範囲指定       |
| `MAX_PERIOD_TIMEOUT` | 408            | max期間取得タイムアウト  |
| `DATA_NOT_FOUND`     | 404            | データが見つからない     |
| `EXTERNAL_API_ERROR` | 502            | Yahoo Finance API エラー |
| `DATABASE_ERROR`     | 500            | データベースエラー       |
| `INTERNAL_ERROR`     | 500            | 内部サーバーエラー       |

### 共通エラーレスポンス形式

```json
{
  "success": false,
  "error": "ERROR_CODE",
  "message": "エラーの詳細説明",
  "details": {}
}
```

## データモデル

### StockData（時間軸共通構造）

#### 日足・週足・月足データ

| フィールド   | 型       | 説明           |
| ------------ | -------- | -------------- |
| `id`         | integer  | 主キー         |
| `symbol`     | string   | 銘柄コード     |
| `date`       | date     | 取引日         |
| `open`       | float    | 始値           |
| `high`       | float    | 高値           |
| `low`        | float    | 安値           |
| `close`      | float    | 終値           |
| `volume`     | integer  | 出来高         |
| `created_at` | datetime | データ作成日時 |
| `updated_at` | datetime | データ更新日時 |

**対応テーブル**: `stocks_1d`, `stocks_1wk`, `stocks_1mo`

#### 分足・時間足データ

| フィールド   | 型       | 説明           |
| ------------ | -------- | -------------- |
| `id`         | integer  | 主キー         |
| `symbol`     | string   | 銘柄コード     |
| `datetime`   | datetime | 取引日時       |
| `open`       | float    | 始値           |
| `high`       | float    | 高値           |
| `low`        | float    | 安値           |
| `close`      | float    | 終値           |
| `volume`     | integer  | 出来高         |
| `created_at` | datetime | データ作成日時 |
| `updated_at` | datetime | データ更新日時 |

**対応テーブル**: `stocks_1m`, `stocks_5m`, `stocks_15m`, `stocks_30m`, `stocks_1h`

### 時間軸とテーブル対応表

| interval | テーブル名   | データ型 | 主キー時間フィールド |
| -------- | ------------ | -------- | -------------------- |
| 1m       | stocks_1m    | 分足     | datetime             |
| 5m       | stocks_5m    | 分足     | datetime             |
| 15m      | stocks_15m   | 分足     | datetime             |
| 30m      | stocks_30m   | 分足     | datetime             |
| 1h       | stocks_1h    | 時間足   | datetime             |
| 1d       | stocks_1d    | 日足     | date                 |
| 1wk      | stocks_1wk   | 週足     | date                 |
| 1mo      | stocks_1mo   | 月足     | date                 |

**注記**: マイルストーン1で全時間軸対応完了。

## 実装優先度

### 優先度: 高（マイルストーン1必須）

- ✅ `POST /api/fetch-data` - 複数時間軸対応株価データ取得
  - ✅ interval パラメータ追加（1m, 5m, 15m, 30m, 1h, 1d, 1wk, 1mo）
  - ✅ period=max オプション追加
- ✅ `GET /api/stocks` - 複数時間軸対応データ表示
  - ✅ interval パラメータ追加
  - ✅ start_datetime/end_datetime パラメータ追加
- ✅ 複数時間軸エラーハンドリング
  - ✅ INVALID_INTERVAL エラーコード
  - ✅ MAX_PERIOD_TIMEOUT エラーコード

### 優先度: 中（動作確認後）

- `GET /api/progress` - プログレス表示（特にmax期間取得時）
- ページネーション機能の最適化
- より詳細なエラーハンドリング
- パフォーマンス監視機能

### 優先度: 低（必要になってから）

- 認証・認可
- レート制限
- キャッシュ機能
- バッチ処理API（マイルストーン2で実装予定）

## 技術的制約・考慮事項

### MVP段階での制約

- **セキュリティ**: 認証なし（ローカル開発のみ）
- **パフォーマンス**: 最適化は後回し
- **エラーハンドリング**: 基本的なもののみ
- **ログ**: 最小限

### Yahoo Finance API制約

- レート制限あり（具体的な制限は要調査）
- 日本株式は銘柄コード末尾に「.T」が必要
- 利用可能な期間に制限がある場合あり

### 開発方針

1. **動作優先**: まず基本機能を実装
2. **シンプル実装**: 複雑な設計は避ける
3. **段階的改善**: 動作確認後に機能拡張

## マイルストーン1実装完了：複数時間軸対応

### ✅ 実装完了した機能

#### 統一エンドポイント
```
POST /api/fetch-data  - 全時間軸対応
GET /api/stocks       - 全時間軸対応
```

#### 対応時間軸一覧
| interval | 説明     | 対象テーブル | 実装状況 |
| -------- | -------- | ------------ | -------- |
| `1m`     | 1分足    | stocks_1m    | ✅ 完了  |
| `5m`     | 5分足    | stocks_5m    | ✅ 完了  |
| `15m`    | 15分足   | stocks_15m   | ✅ 完了  |
| `30m`    | 30分足   | stocks_30m   | ✅ 完了  |
| `1h`     | 1時間足  | stocks_1h    | ✅ 完了  |
| `1d`     | 日足     | stocks_1d    | ✅ 完了  |
| `1wk`    | 週足     | stocks_1wk   | ✅ 完了  |
| `1mo`    | 月足     | stocks_1mo   | ✅ 完了  |

#### 対応期間一覧
| period | 説明           | 実装状況 |
| ------ | -------------- | -------- |
| `1d`   | 過去1日        | ✅ 完了  |
| `5d`   | 過去5日        | ✅ 完了  |
| `1mo`  | 過去1ヶ月      | ✅ 完了  |
| `3mo`  | 過去3ヶ月      | ✅ 完了  |
| `6mo`  | 過去6ヶ月      | ✅ 完了  |
| `1y`   | 過去1年        | ✅ 完了  |
| `2y`   | 過去2年        | ✅ 完了  |
| `5y`   | 過去5年        | ✅ 完了  |
| `10y`  | 過去10年       | ✅ 完了  |
| `ytd`  | 年初来         | ✅ 完了  |
| `max`  | 全利用可能期間 | ✅ 完了  |

### 将来拡張計画（マイルストーン2以降）

#### バッチ処理API（マイルストーン2）
```
POST /api/batch/fetch-all-symbols  - 全銘柄一括取得
GET /api/batch/progress            - バッチ処理進捗
```

#### システム監視API（マイルストーン3）
```
GET /api/system/status             - システム状態確認
POST /api/system/connection-test   - 接続テスト実行
```

---

## 実装例（参考）

### Flask実装例

```python
from flask import Flask, request, jsonify
import yfinance as yf
from datetime import datetime

app = Flask(__name__)

@app.route('/api/fetch-data', methods=['POST'])
def fetch_data():
    data = request.get_json()
    symbol = data.get('symbol')
    period = data.get('period', '1mo')

    try:
        # Yahoo Financeからデータ取得
        ticker = yf.Ticker(symbol)
        hist = ticker.history(period=period)

        # データベースに保存（実装必要）
        # save_to_database(symbol, hist)

        return jsonify({
            "success": True,
            "message": "データを正常に取得しました",
            "data": {
                "symbol": symbol,
                "records_count": len(hist),
                "date_range": {
                    "start": hist.index[0].strftime('%Y-%m-%d'),
                    "end": hist.index[-1].strftime('%Y-%m-%d')
                }
            }
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": "EXTERNAL_API_ERROR",
            "message": f"データ取得に失敗しました: {str(e)}"
        }), 502

@app.route('/api/stocks', methods=['GET'])
def get_stocks():
    # データベースからデータ取得（実装必要）
    # stocks = get_stocks_from_database()

    return jsonify({
        "success": True,
        "data": [],  # 実装後にデータを返す
        "pagination": {
            "total": 0,
            "limit": 100,
            "offset": 0,
            "has_next": False
        }
    })

if __name__ == '__main__':
    app.run(debug=True, port=8000)
```

この仕様書は、プロジェクトの進行に合わせて段階的に更新・拡張していくものとします。
