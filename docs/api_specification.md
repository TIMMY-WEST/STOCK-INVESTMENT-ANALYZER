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
  "period": "1mo"
}
```

**パラメータ**

| フィールド | 型     | 必須 | 説明                                                         | デフォルト |
| ---------- | ------ | ---- | ------------------------------------------------------------ | ---------- |
| `symbol`   | string | ✓    | 銘柄コード（例：7203.T = トヨタ）                            | -          |
| `period`   | string | -    | 取得期間（1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max） | "1mo"      |

**成功レスポンス (200)**

```json
{
  "success": true,
  "message": "データを正常に取得しました",
  "data": {
    "symbol": "7203.T",
    "records_count": 30,
    "date_range": {
      "start": "2024-08-09",
      "end": "2024-09-09"
    }
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
| `limit`      | integer | -    | 取得件数制限                       | 100        |
| `offset`     | integer | -    | オフセット                         | 0          |
| `start_date` | string  | -    | 開始日（YYYY-MM-DD形式）           | -          |
| `end_date`   | string  | -    | 終了日（YYYY-MM-DD形式）           | -          |

**リクエスト例**

```
GET /api/stocks?symbol=7203.T&limit=30
GET /api/stocks?limit=10&offset=20
GET /api/stocks?start_date=2024-08-01&end_date=2024-08-31
GET /api/stocks?symbol=7203.T&start_date=2024-08-01&end_date=2024-08-31&limit=50
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
  "pagination": {
    "total": 100,
    "limit": 30,
    "offset": 0,
    "has_next": true
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

### StockData（日足データ）

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

**対応テーブル**: `stocks_daily`

**注記**: MVPでは日足データのみ対応。将来的に分足・週足・月足データに拡張予定。

## 実装優先度

### 優先度: 高（MVP必須）

- ✅ `POST /api/fetch-data` - 基本的な株価データ取得
- ✅ `GET /api/stocks` - 保存済みデータの表示
- ✅ 基本的なエラーハンドリング

### 優先度: 中（動作確認後）

- `GET /api/progress` - プログレス表示
- ページネーション機能
- より詳細なエラーハンドリング

### 優先度: 低（必要になってから）

- 認証・認可
- レート制限
- キャッシュ機能
- バッチ処理API
- **複数時間軸対応**（分足・週足・月足データ）

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

## 将来拡張計画（複数時間軸対応）

### 拡張予定のエンドポイント

#### 分足データAPI（将来拡張）
```
POST /api/fetch-data/minute
GET /api/stocks/minute
```

#### 週足・月足データAPI（将来拡張）
```
POST /api/fetch-data/weekly
POST /api/fetch-data/monthly
GET /api/stocks/weekly
GET /api/stocks/monthly
```

### 拡張時のパラメータ

#### 分足データ取得
```json
{
  "symbol": "7203.T",
  "period": "1d",
  "interval": "5m"
}
```

#### 時間軸指定パラメータ
| interval                 | 説明   | 対象API             |
| ------------------------ | ------ | ------------------- |
| `1m`, `5m`, `15m`, `30m` | 分足   | /api/stocks/minute  |
| `1h`                     | 時間足 | /api/stocks/hourly  |
| `1d`                     | 日足   | /api/stocks/daily   |
| `1wk`                    | 週足   | /api/stocks/weekly  |
| `1mo`                    | 月足   | /api/stocks/monthly |

### 拡張時の設計方針

- **段階的実装**: 需要の高い時間軸から順次追加
- **API統一**: 基本構造は現在の設計を踏襲
- **データ分離**: 時間軸ごとに独立したテーブル・エンドポイント

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