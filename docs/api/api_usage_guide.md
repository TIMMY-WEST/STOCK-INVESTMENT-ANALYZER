# API使用例ガイド

このガイドでは、STOCK-INVESTMENT-ANALYZER APIの各エンドポイントの使用方法を、具体的なサンプルコードとともに説明します。

## 目次

1. [認証](#認証)
2. [株価データ取得API](#株価データ取得api)
3. [銘柄一覧取得API](#銘柄一覧取得api)
4. [銘柄詳細取得API](#銘柄詳細取得api)
5. [JPX銘柄マスタ更新API](#jpx銘柄マスタ更新api)
6. [バルクデータAPI](#バルクデータapi)
7. [システム監視API](#システム監視api)
8. [エラーハンドリング](#エラーハンドリング)
9. [レート制限](#レート制限)

## 認証

APIキーが設定されている場合、すべてのリクエストにAPIキーが必要です。

### ヘッダー設定
```
X-API-Key: your_api_key_here
```

## 株価データ取得API

### エンドポイント
```
POST /api/fetch-data
```

### cURLサンプル

#### 基本的な株価データ取得
```bash
curl -X POST "http://localhost:5000/api/fetch-data" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your_api_key_here" \
  -d '{
    "symbol": "7203.T",
    "period": "1mo",
    "interval": "1d"
  }'
```

#### 複数時間軸での取得
```bash
curl -X POST "http://localhost:5000/api/fetch-data" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your_api_key_here" \
  -d '{
    "symbol": "6758.T",
    "period": "3mo",
    "interval": "1wk"
  }'
```

### Pythonクライアントサンプル

#### 基本的な使用例
```python
import requests
import json

def fetch_stock_data(symbol, period="1mo", interval="1d", api_key=None):
    """
    株価データを取得する関数

    Args:
        symbol (str): 銘柄コード（例: "7203.T"）
        period (str): 取得期間（例: "1mo", "3mo", "6mo", "1y"）
        interval (str): データ間隔（例: "1d", "1wk", "1mo"）
        api_key (str): APIキー

    Returns:
        dict: APIレスポンス
    """
    url = "http://localhost:5000/api/fetch-data"

    headers = {
        "Content-Type": "application/json"
    }

    if api_key:
        headers["X-API-Key"] = api_key

    payload = {
        "symbol": symbol,
        "period": period,
        "interval": interval
    }

    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        return response.json()

    except requests.exceptions.RequestException as e:
        print(f"リクエストエラー: {e}")
        return None

# 使用例
if __name__ == "__main__":
    # トヨタ自動車の1ヶ月間の日次データを取得
    result = fetch_stock_data("7203.T", "1mo", "1d", "your_api_key_here")

    if result and result.get("status") == "success":
        data = result.get("data", {})
        print(f"銘柄: {data.get('symbol')}")
        print(f"データ件数: {len(data.get('stock_data', []))}")
        print(f"取得期間: {data.get('period')}")
        print(f"データ間隔: {data.get('interval')}")
    else:
        print("データ取得に失敗しました")
```

#### 複数銘柄の一括取得
```python
import requests
import json
import time

def fetch_multiple_stocks(symbols, period="1mo", interval="1d", api_key=None):
    """
    複数銘柄の株価データを一括取得する関数

    Args:
        symbols (list): 銘柄コードのリスト
        period (str): 取得期間
        interval (str): データ間隔
        api_key (str): APIキー

    Returns:
        dict: 銘柄コードをキーとした結果辞書
    """
    results = {}

    for symbol in symbols:
        print(f"取得中: {symbol}")
        result = fetch_stock_data(symbol, period, interval, api_key)
        results[symbol] = result

        # レート制限を考慮して少し待機
        time.sleep(0.5)

    return results

# 使用例
symbols = ["7203.T", "6758.T", "9984.T"]  # トヨタ、ソニー、ソフトバンク
results = fetch_multiple_stocks(symbols, "1mo", "1d", "your_api_key_here")

for symbol, result in results.items():
    if result and result.get("status") == "success":
        data_count = len(result.get("data", {}).get("stock_data", []))
        print(f"{symbol}: {data_count}件のデータを取得")
    else:
        print(f"{symbol}: 取得失敗")
```

### 成功レスポンス例

#### 単一銘柄のレスポンス
```json
{
  "status": "success",
  "message": "株価データの取得が完了しました",
  "data": {
    "symbol": "7203.T",
    "period": "1mo",
    "interval": "1d",
    "stock_data": [
      {
        "date": "2024-01-15",
        "open": 2500.0,
        "high": 2550.0,
        "low": 2480.0,
        "close": 2530.0,
        "volume": 1500000
      }
    ],
    "total_records": 20,
    "data_source": "yahoo_finance"
  },
  "meta": {
    "timestamp": "2024-01-15T10:30:00Z",
    "response_time_ms": 1250.5
  }
}
```

#### 複数時間軸のレスポンス
```json
{
  "status": "success",
  "message": "株価データの取得が完了しました",
  "data": {
    "symbol": "6758.T",
    "period": "3mo",
    "interval": "1wk",
    "stock_data": [
      {
        "date": "2024-01-15",
        "open": 12000.0,
        "high": 12200.0,
        "low": 11900.0,
        "close": 12100.0,
        "volume": 800000
      }
    ],
    "total_records": 12,
    "data_source": "yahoo_finance"
  },
  "meta": {
    "timestamp": "2024-01-15T10:35:00Z",
    "response_time_ms": 1850.2
  }
}
```

#### エラーレスポンス例
```json
{
  "status": "error",
  "error": {
    "code": "INVALID_SYMBOL",
    "message": "指定された銘柄コードが無効です",
    "details": "銘柄コード '9999.T' は存在しません"
  },
  "meta": {
    "timestamp": "2024-01-15T10:40:00Z",
    "response_time_ms": 50.1
  }
}
```

## 銘柄一覧取得API

### エンドポイント
```
GET /api/stocks
```

### cURLサンプル

#### 全銘柄取得
```bash
curl -X GET "http://localhost:5000/api/stocks" \
  -H "X-API-Key: your_api_key_here"
```

#### ページネーション付き取得
```bash
curl -X GET "http://localhost:5000/api/stocks?page=1&per_page=50" \
  -H "X-API-Key: your_api_key_here"
```

#### 市場別フィルタリング
```bash
curl -X GET "http://localhost:5000/api/stocks?market=Prime" \
  -H "X-API-Key: your_api_key_here"
```

### Pythonクライアントサンプル

```python
import requests

def get_stocks(page=None, per_page=None, market=None, api_key=None):
    """
    銘柄一覧を取得する関数

    Args:
        page (int): ページ番号
        per_page (int): 1ページあたりの件数
        market (str): 市場名でフィルタリング
        api_key (str): APIキー

    Returns:
        dict: APIレスポンス
    """
    url = "http://localhost:5000/api/stocks"

    headers = {}
    if api_key:
        headers["X-API-Key"] = api_key

    params = {}
    if page is not None:
        params["page"] = page
    if per_page is not None:
        params["per_page"] = per_page
    if market:
        params["market"] = market

    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        return response.json()

    except requests.exceptions.RequestException as e:
        print(f"リクエストエラー: {e}")
        return None

def search_stocks_by_sector(sector, api_key=None):
    """
    セクター別に銘柄を検索する関数

    Args:
        sector (str): セクター名
        api_key (str): APIキー

    Returns:
        dict: APIレスポンス
    """
    url = "http://localhost:5000/api/stocks"

    headers = {}
    if api_key:
        headers["X-API-Key"] = api_key

    params = {"sector": sector}

    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        return response.json()

    except requests.exceptions.RequestException as e:
        print(f"リクエストエラー: {e}")
        return None

def get_all_stocks_paginated(api_key=None, page_size=100):
    """
    全銘柄をページネーションで取得する関数

    Args:
        api_key (str): APIキー
        page_size (int): 1ページあたりの件数

    Returns:
        list: 全銘柄のリスト
    """
    all_stocks = []
    page = 1

    while True:
        result = get_stocks(page=page, per_page=page_size, api_key=api_key)

        if not result or result.get("status") != "success":
            break

        stocks = result.get("data", [])
        if not stocks:
            break

        all_stocks.extend(stocks)

        # 最後のページかチェック
        pagination = result.get("pagination", {})
        if page >= pagination.get("total_pages", 0):
            break

        page += 1

    return all_stocks

# 使用例
if __name__ == "__main__":
    # プライム市場の銘柄を50件ずつ取得
    result = get_stocks(page=1, per_page=50, market="Prime", api_key="your_api_key_here")

    if result and result.get("status") == "success":
        stocks = result.get("data", [])
        pagination = result.get("pagination", {})

        print(f"取得件数: {len(stocks)}")
        print(f"総件数: {pagination.get('total')}")
        print(f"現在のページ: {pagination.get('page')}")

        # 最初の5銘柄を表示
        for stock in stocks[:5]:
            print(f"- {stock.get('symbol')}: {stock.get('name')}")

    # セクター検索の例
    tech_stocks = search_stocks_by_sector("輸送用機器", "your_api_key_here")
    if tech_stocks and tech_stocks.get("status") == "success":
        print("\n輸送用機器セクターの銘柄:")
        for stock in tech_stocks.get("data", [])[:3]:
            print(f"  {stock.get('symbol')}: {stock.get('name')}")
```

### 成功レスポンス例
```json
{
  "status": "success",
  "message": "銘柄一覧の取得が完了しました",
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
    "page": 1,
    "per_page": 50,
    "total": 3800,
    "total_pages": 76
  }
}
```

## 銘柄詳細取得API

### エンドポイント
```
GET /api/stocks/{stock_id}
```

### cURLサンプル

```bash
curl -X GET "http://localhost:5000/api/stocks/7203.T" \
  -H "X-API-Key: your_api_key_here"
```

### Pythonクライアントサンプル

```python
import requests

def get_stock_detail(stock_id, api_key=None):
    """
    銘柄詳細情報を取得する関数

    Args:
        stock_id (str): 銘柄ID（例: "7203.T"）
        api_key (str): APIキー

    Returns:
        dict: APIレスポンス
    """
    url = f"http://localhost:5000/api/stocks/{stock_id}"

    headers = {}
    if api_key:
        headers["X-API-Key"] = api_key

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json()

    except requests.exceptions.RequestException as e:
        print(f"リクエストエラー: {e}")
        return None

# 使用例
result = get_stock_detail("7203.T", "your_api_key_here")

if result and result.get("status") == "success":
    stock = result.get("data")
    print(f"銘柄名: {stock.get('name')}")
    print(f"市場: {stock.get('market')}")
    print(f"業種: {stock.get('sector')}")
else:
    print("銘柄詳細の取得に失敗しました")
```

## JPX銘柄マスタ更新API

### エンドポイント
```
POST /api/stock-master/
```

### cURLサンプル

#### 手動更新
```bash
curl -X POST "http://localhost:5000/api/stock-master/" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your_api_key_here" \
  -d '{
    "update_type": "manual"
  }'
```

#### スケジュール更新
```bash
curl -X POST "http://localhost:5000/api/stock-master/" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your_api_key_here" \
  -d '{
    "update_type": "scheduled"
  }'
```

### Pythonクライアントサンプル

```python
import requests

def update_stock_master(update_type="manual", api_key=None):
    """
    JPX銘柄マスタを更新する関数

    Args:
        update_type (str): 更新タイプ（"manual" または "scheduled"）
        api_key (str): APIキー

    Returns:
        dict: APIレスポンス
    """
    url = "http://localhost:5000/api/stock-master/"

    headers = {
        "Content-Type": "application/json"
    }

    if api_key:
        headers["X-API-Key"] = api_key

    payload = {
        "update_type": update_type
    }

    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        return response.json()

    except requests.exceptions.RequestException as e:
        print(f"リクエストエラー: {e}")
        return None

# 使用例
result = update_stock_master("manual", "your_api_key_here")

if result and result.get("status") == "success":
    data = result.get("data")
    print(f"更新完了: {data.get('total_stocks')}銘柄")
    print(f"追加: {data.get('added_stocks')}銘柄")
    print(f"更新: {data.get('updated_stocks')}銘柄")
    print(f"削除: {data.get('removed_stocks')}銘柄")
else:
    print("銘柄マスタの更新に失敗しました")
```

## バルクデータAPI

### エンドポイント
```
POST /api/bulk-data/
```

### cURLサンプル

#### バルクデータジョブの開始
```bash
curl -X POST "http://localhost:5000/api/bulk-data/" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your_api_key_here" \
  -d '{
    "symbols": ["7203.T", "6758.T", "9984.T"],
    "period": "1mo",
    "interval": "1d"
  }'
```

#### ジョブ状態の確認
```bash
curl -X GET "http://localhost:5000/api/bulk-data/job/{job_id}" \
  -H "X-API-Key: your_api_key_here"
```

### Pythonクライアントサンプル

```python
import requests
import time

def start_bulk_job(symbols, period="1mo", interval="1d", api_key=None):
    """
    バルクデータジョブを開始する関数

    Args:
        symbols (list): 銘柄コードのリスト
        period (str): 取得期間
        interval (str): データ間隔
        api_key (str): APIキー

    Returns:
        dict: APIレスポンス
    """
    url = "http://localhost:5000/api/bulk-data/"

    headers = {
        "Content-Type": "application/json"
    }

    if api_key:
        headers["X-API-Key"] = api_key

    payload = {
        "symbols": symbols,
        "period": period,
        "interval": interval
    }

    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        return response.json()

    except requests.exceptions.RequestException as e:
        print(f"リクエストエラー: {e}")
        return None

def check_job_status(job_id, api_key=None):
    """
    ジョブの状態を確認する関数

    Args:
        job_id (str): ジョブID
        api_key (str): APIキー

    Returns:
        dict: APIレスポンス
    """
    url = f"http://localhost:5000/api/bulk-data/job/{job_id}"

    headers = {}
    if api_key:
        headers["X-API-Key"] = api_key

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json()

    except requests.exceptions.RequestException as e:
        print(f"リクエストエラー: {e}")
        return None

def wait_for_job_completion(job_id, api_key=None, timeout=300):
    """
    ジョブの完了を待機する関数

    Args:
        job_id (str): ジョブID
        api_key (str): APIキー
        timeout (int): タイムアウト秒数

    Returns:
        dict: 最終的なジョブ状態
    """
    start_time = time.time()

    while time.time() - start_time < timeout:
        status = check_job_status(job_id, api_key)

        if not status:
            return None

        job_status = status.get("data", {}).get("status")

        if job_status in ["completed", "failed"]:
            return status

        print(f"ジョブ状態: {job_status}")
        time.sleep(5)  # 5秒待機

    print("タイムアウトしました")
    return None

# 使用例
if __name__ == "__main__":
    symbols = ["7203.T", "6758.T", "9984.T"]

    # バルクジョブを開始
    result = start_bulk_job(symbols, "1mo", "1d", "your_api_key_here")

    if result and result.get("status") == "success":
        job_id = result.get("data", {}).get("job_id")
        print(f"ジョブ開始: {job_id}")

        # ジョブの完了を待機
        final_status = wait_for_job_completion(job_id, "your_api_key_here")

        if final_status:
            job_data = final_status.get("data", {})
            if job_data.get("status") == "completed":
                print("ジョブが正常に完了しました")
                print(f"処理件数: {job_data.get('processed_count')}")
            else:
                print("ジョブが失敗しました")
                print(f"エラー: {job_data.get('error_message')}")
    else:
        print("ジョブの開始に失敗しました")
```

### バルクデータAPIレスポンス例

#### ジョブ開始成功レスポンス
```json
{
  "status": "success",
  "data": {
    "job_id": "bulk_job_20240115_001",
    "status": "started",
    "symbols": ["7203.T", "6758.T", "9984.T"],
    "estimated_completion": "2024-01-15T11:35:00Z"
  },
  "meta": {
    "request_id": "req_bulk_start_001",
    "timestamp": "2024-01-15T11:30:00Z",
    "response_time_ms": 120
  }
}
```

#### ジョブ状態確認レスポンス
```json
{
  "status": "success",
  "data": {
    "job_id": "bulk_job_20240115_001",
    "status": "completed",
    "processed_count": 3,
    "success_count": 3,
    "error_count": 0,
    "completion_time": "2024-01-15T11:33:45Z"
  },
  "meta": {
    "request_id": "req_bulk_status_001",
    "timestamp": "2024-01-15T11:34:00Z",
    "response_time_ms": 45
  }
}
```

## システム監視API

### データベース接続テスト

#### エンドポイント
```
GET /api/system/database/connection
```

#### cURLサンプル
```bash
curl -X GET "http://localhost:5000/api/system/database/connection" \
  -H "X-API-Key: your_api_key_here"
```

#### Pythonクライアントサンプル
```python
import requests

def test_database_connection(api_key=None):
    """
    データベース接続をテストする関数

    Args:
        api_key (str): APIキー

    Returns:
        dict: APIレスポンス
    """
    url = "http://localhost:5000/api/system/database/connection"

    headers = {}
    if api_key:
        headers["X-API-Key"] = api_key

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json()

    except requests.exceptions.RequestException as e:
        print(f"リクエストエラー: {e}")
        return None

# 使用例
result = test_database_connection("your_api_key_here")

if result and result.get("status") == "success":
    data = result.get("data")
    meta = result.get("meta")
    print(f"データベース: {data.get('database')}")
    print(f"テーブル存在: {data.get('table_exists')}")
    print(f"接続数: {data.get('connection_count')}")
    print(f"応答時間: {meta.get('response_time_ms')}ms")
else:
    print("データベース接続テストに失敗しました")
```

#### 成功レスポンス例
```json
{
  "status": "success",
  "data": {
    "database": "stock_investment_analyzer",
    "table_exists": true,
    "connection_count": 5,
    "last_updated": "2024-01-15T10:45:00Z"
  },
  "meta": {
    "request_id": "req_db_test_001",
    "timestamp": "2024-01-15T11:15:00Z",
    "response_time_ms": 25
  }
}
```

### 外部API接続テスト

#### エンドポイント
```
GET /api/system/external-api/connection
```

#### cURLサンプル
```bash
curl -X GET "http://localhost:5000/api/system/external-api/connection?symbol=7203.T" \
  -H "X-API-Key: your_api_key_here"
```

#### Pythonクライアントサンプル
```python
import requests

def test_external_api_connection(symbol="7203.T", api_key=None):
    """
    外部API接続をテストする関数

    Args:
        symbol (str): テスト用銘柄コード
        api_key (str): APIキー

    Returns:
        dict: APIレスポンス
    """
    url = "http://localhost:5000/api/system/external-api/connection"

    headers = {}
    if api_key:
        headers["X-API-Key"] = api_key

    params = {"symbol": symbol}

    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        return response.json()

    except requests.exceptions.RequestException as e:
        print(f"リクエストエラー: {e}")
        return None

# 使用例
result = test_external_api_connection("7203.T", "your_api_key_here")

if result and result.get("status") == "success":
    data = result.get("data")
    meta = result.get("meta")
    print(f"テスト銘柄: {data.get('symbol')}")
    print(f"API接続: 正常")
    print(f"応答時間: {meta.get('response_time_ms')}ms")
```

#### 成功レスポンス例
```json
{
  "status": "success",
  "data": {
    "symbol": "7203.T",
    "api_status": "connected",
    "test_data_retrieved": true,
    "last_price": 2530.0
  },
  "meta": {
    "request_id": "req_ext_api_test_001",
    "timestamp": "2024-01-15T11:20:00Z",
    "response_time_ms": 180
  }
}
```

### システム監視の統合例

```python
import requests
import time

def comprehensive_system_check(api_key=None):
    """
    システム全体の健全性をチェックする関数

    Args:
        api_key (str): APIキー

    Returns:
        dict: システム状態の詳細
    """
    results = {
        "database": None,
        "external_api": None,
        "overall_status": "unknown"
    }

    # データベース接続テスト
    db_result = test_database_connection(api_key)
    results["database"] = db_result

    # 外部API接続テスト
    ext_api_result = test_external_api_connection("7203.T", api_key)
    results["external_api"] = ext_api_result

    # 総合判定
    if (db_result and db_result.get("status") == "success" and
        ext_api_result and ext_api_result.get("status") == "success"):
        results["overall_status"] = "healthy"
    else:
        results["overall_status"] = "unhealthy"

    return results

# 使用例
system_status = comprehensive_system_check("your_api_key_here")
print(f"システム状態: {system_status['overall_status']}")
```

## エラーハンドリング

### 一般的なエラーレスポンス形式

```json
{
  "status": "error",
  "error": {
    "code": "ERROR_CODE",
    "message": "エラーメッセージ"
  },
  "details": {
    "timestamp": "2024-01-15T10:30:00Z",
    "request_id": "req_123456789"
  }
}
```

### エラーコード一覧

| エラーコード | HTTPステータス | 説明 |
|-------------|---------------|------|
| `INVALID_SYMBOL` | 400 | 無効な銘柄コード |
| `INVALID_PERIOD` | 400 | 無効な期間指定 |
| `INVALID_INTERVAL` | 400 | 無効な間隔指定 |
| `UNAUTHORIZED` | 401 | 認証エラー |
| `RATE_LIMIT_EXCEEDED` | 429 | レート制限超過 |
| `YAHOO_FINANCE_ERROR` | 502 | Yahoo Finance APIエラー |
| `DATABASE_ERROR` | 500 | データベースエラー |
| `INTERNAL_SERVER_ERROR` | 500 | 内部サーバーエラー |

### Pythonでのエラーハンドリング例

```python
import requests
from requests.exceptions import RequestException

def handle_api_response(response):
    """
    APIレスポンスを処理し、エラーハンドリングを行う関数

    Args:
        response (requests.Response): HTTPレスポンス

    Returns:
        dict or None: 成功時はデータ、失敗時はNone
    """
    try:
        response.raise_for_status()
        data = response.json()

        if data.get("status") == "success":
            return data
        else:
            # APIレベルのエラー
            error = data.get("error", {})
            error_code = error.get("code", "UNKNOWN_ERROR")
            error_message = error.get("message", "不明なエラー")

            print(f"APIエラー [{error_code}]: {error_message}")
            return None

    except requests.exceptions.HTTPError as e:
        # HTTPエラー
        status_code = e.response.status_code

        if status_code == 401:
            print("認証エラー: APIキーを確認してください")
        elif status_code == 429:
            print("レート制限エラー: しばらく待ってから再試行してください")
        elif status_code >= 500:
            print("サーバーエラー: しばらく待ってから再試行してください")
        else:
            print(f"HTTPエラー {status_code}: {e}")

        return None

    except requests.exceptions.RequestException as e:
        # ネットワークエラーなど
        print(f"リクエストエラー: {e}")
        return None

    except ValueError as e:
        # JSON解析エラー
        print(f"レスポンス解析エラー: {e}")
        return None

# 使用例
def fetch_stock_data_with_error_handling(symbol, period="1mo", interval="1d", api_key=None):
    """
    エラーハンドリング付きの株価データ取得関数
    """
    url = "http://localhost:5000/api/fetch-data"

    headers = {
        "Content-Type": "application/json"
    }

    if api_key:
        headers["X-API-Key"] = api_key

    payload = {
        "symbol": symbol,
        "period": period,
        "interval": interval
    }

    try:
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        return handle_api_response(response)

    except requests.exceptions.Timeout:
        print("タイムアウトエラー: リクエストがタイムアウトしました")
        return None

    except requests.exceptions.ConnectionError:
        print("接続エラー: サーバーに接続できません")
        return None

# 使用例
result = fetch_stock_data_with_error_handling("7203.T", "1mo", "1d", "your_api_key_here")

if result:
    print("データ取得成功")
    # データ処理...
else:
    print("データ取得失敗")
```

### リトライ機能付きクライアント

```python
import requests
import time
from functools import wraps

def retry_on_failure(max_retries=3, delay=1, backoff=2):
    """
    失敗時にリトライするデコレータ

    Args:
        max_retries (int): 最大リトライ回数
        delay (float): 初回待機時間（秒）
        backoff (float): 待機時間の倍率
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            current_delay = delay

            for attempt in range(max_retries + 1):
                try:
                    result = func(*args, **kwargs)

                    # 成功時は結果を返す
                    if result:
                        return result

                    # 最後の試行でない場合は待機
                    if attempt < max_retries:
                        print(f"リトライ {attempt + 1}/{max_retries} - {current_delay}秒待機")
                        time.sleep(current_delay)
                        current_delay *= backoff

                except Exception as e:
                    if attempt == max_retries:
                        print(f"最大リトライ回数に達しました: {e}")
                        raise

                    print(f"エラー発生 (試行 {attempt + 1}/{max_retries + 1}): {e}")
                    time.sleep(current_delay)
                    current_delay *= backoff

            return None

        return wrapper
    return decorator

@retry_on_failure(max_retries=3, delay=1, backoff=2)
def fetch_stock_data_with_retry(symbol, period="1mo", interval="1d", api_key=None):
    """
    リトライ機能付きの株価データ取得関数
    """
    return fetch_stock_data_with_error_handling(symbol, period, interval, api_key)

# 使用例
result = fetch_stock_data_with_retry("7203.T", "1mo", "1d", "your_api_key_here")
```

## レート制限

### 制限内容
- デフォルト: 60リクエスト/分
- 環境変数 `RATE_LIMIT_PER_MINUTE` で設定可能
- APIキーまたはIPアドレス単位で制限

### レート制限エラーの処理

```python
import time
import requests

def handle_rate_limit(func, *args, **kwargs):
    """
    レート制限を考慮してAPIを呼び出す関数

    Args:
        func: 呼び出す関数
        *args, **kwargs: 関数の引数

    Returns:
        dict or None: APIレスポンス
    """
    max_retries = 3
    base_delay = 60  # 1分待機

    for attempt in range(max_retries):
        try:
            response = func(*args, **kwargs)
            return response

        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 429:
                if attempt < max_retries - 1:
                    wait_time = base_delay * (attempt + 1)
                    print(f"レート制限に達しました。{wait_time}秒待機します...")
                    time.sleep(wait_time)
                    continue
                else:
                    print("レート制限により最大リトライ回数に達しました")
                    return None
            else:
                raise

    return None

# 使用例
def api_call():
    return requests.post(
        "http://localhost:5000/api/fetch-data",
        headers={"Content-Type": "application/json", "X-API-Key": "your_api_key_here"},
        json={"symbol": "7203.T", "period": "1mo", "interval": "1d"}
    )

result = handle_rate_limit(api_call)
```

## まとめ

このガイドでは、STOCK-INVESTMENT-ANALYZER APIの各エンドポイントの使用方法を、cURLとPythonの両方のサンプルコードで説明しました。

### 重要なポイント
1. **認証**: APIキーが設定されている場合は必須
2. **エラーハンドリング**: 適切なエラー処理とリトライ機能の実装
3. **レート制限**: 1分間に60リクエストまでの制限に注意
4. **タイムアウト**: 長時間のリクエストに対するタイムアウト設定

### 次のステップ
- [API仕様書](./api_specification.md)で詳細な仕様を確認
- [OpenAPI仕様](./openapi.md)でスキーマ定義を確認
- 実際の開発環境でサンプルコードを試行

### サポート
問題が発生した場合は、以下を確認してください：
1. APIキーの設定
2. エンドポイントURLの正確性
3. リクエスト形式の妥当性
4. ネットワーク接続状況
