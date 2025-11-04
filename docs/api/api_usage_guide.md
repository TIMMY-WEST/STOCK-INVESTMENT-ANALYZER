# API使用例ガイド

STOCK-INVESTMENT-ANALYZER APIの実践的な使用例とコードサンプル集です。

## 目次

- [クイックスタート](#クイックスタート)
- [株価データ取得の基本](#株価データ取得の基本)
- [複数銘柄の一括取得](#複数銘柄の一括取得)
- [データの検索とフィルタリング](#データの検索とフィルタリング)
- [エラーハンドリング](#エラーハンドリング)
- [実践的なユースケース](#実践的なユースケース)
- [パフォーマンス最適化](#パフォーマンス最適化)
---
## クイックスタート

### 前提条件

- APIサーバーが `http://localhost:8000` で起動していること
- 必要に応じて認証情報（将来実装予定）

### 最小限の例

#### cURL

```bash
# 株価データを取得して保存
curl -X POST "http://localhost:8000/api/stocks/data" \
  -H "Content-Type: application/json" \
  -d '{
    "symbol": "7203.T",
    "period": "1mo",
    "interval": "1d"
  }'

# 保存されたデータを取得
curl -X GET "http://localhost:8000/api/stocks?symbol=7203.T&limit=10"
```

#### Python

```python
import requests

BASE_URL = "http://localhost:8000"

# 株価データを取得して保存
response = requests.post(
    f"{BASE_URL}/api/stocks/data",
    json={
        "symbol": "7203.T",
        "period": "1mo",
        "interval": "1d"
    }
)

print(response.json())
```

#### JavaScript

```javascript
const BASE_URL = 'http://localhost:8000';

// 株価データを取得して保存
fetch(`${BASE_URL}/api/stocks/data`, {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    symbol: '7203.T',
    period: '1mo',
    interval: '1d'
  })
})
  .then(response => response.json())
  .then(data => console.log(data));
```
---
## 株価データ取得の基本

### 1. 日足データの取得

最も一般的な使用例です。

#### Python実装例

```python
import requests
from datetime import datetime, timedelta

class StockDataClient:
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url

    def fetch_daily_data(self, symbol, period="1mo"):
        """日足データを取得"""
        url = f"{self.base_url}/api/stocks/data"
        payload = {
            "symbol": symbol,
            "period": period,
            "interval": "1d"
        }

        response = requests.post(url, json=payload)
        response.raise_for_status()
        return response.json()

    def get_latest_data(self, symbol, limit=30):
        """最新の日足データを取得"""
        url = f"{self.base_url}/api/stocks"
        params = {
            "symbol": symbol,
            "interval": "1d",
            "limit": limit,
            "offset": 0
        }

        response = requests.get(url, params=params)
        response.raise_for_status()
        return response.json()

# 使用例
client = StockDataClient()

# トヨタ自動車の1ヶ月分のデータを取得
result = client.fetch_daily_data("7203.T", "1mo")
print(f"取得件数: {result['data']['records_count']}")
print(f"保存件数: {result['data']['saved_records']}")

# 最新30件のデータを取得
latest_data = client.get_latest_data("7203.T", 30)
print(f"データ件数: {len(latest_data['data'])}")
```

### 2. 分足データの取得

短期取引や詳細分析に使用します。

```python
def fetch_intraday_data(symbol, interval="5m", period="1d"):
    """分足データを取得"""
    url = "http://localhost:8000/api/stocks/data"
    payload = {
        "symbol": symbol,
        "period": period,
        "interval": interval
    }

    response = requests.post(url, json=payload)
    return response.json()

# 5分足データを取得
intraday = fetch_intraday_data("7203.T", interval="5m", period="1d")

# 取得したデータの確認
if intraday["success"]:
    print(f"5分足データ: {intraday['data']['records_count']}件")
    print(f"期間: {intraday['data']['date_range']}")
```

### 3. 週足・月足データの取得

長期分析に使用します。

```python
def fetch_weekly_data(symbol, period="1y"):
    """週足データを取得"""
    url = "http://localhost:8000/api/stocks/data"
    payload = {
        "symbol": symbol,
        "period": period,
        "interval": "1wk"
    }

    response = requests.post(url, json=payload)
    return response.json()

def fetch_monthly_data(symbol, period="5y"):
    """月足データを取得"""
    url = "http://localhost:8000/api/stocks/data"
    payload = {
        "symbol": symbol,
        "period": period,
        "interval": "1mo"
    }

    response = requests.post(url, json=payload)
    return response.json()

# 週足データ取得
weekly = fetch_weekly_data("7203.T", "1y")
print(f"週足データ: {weekly['data']['records_count']}件")

# 月足データ取得
monthly = fetch_monthly_data("7203.T", "5y")
print(f"月足データ: {monthly['data']['records_count']}件")
```
---
## 複数銘柄の一括取得

### 1. 逐次的な取得（シンプル）

```python
import time

def fetch_multiple_stocks_sequential(symbols, period="1mo", interval="1d"):
    """複数銘柄を順次取得"""
    results = {}

    for symbol in symbols:
        print(f"取得中: {symbol}")

        try:
            response = requests.post(
                "http://localhost:8000/api/stocks/data",
                json={
                    "symbol": symbol,
                    "period": period,
                    "interval": interval
                }
            )
            results[symbol] = response.json()

            # レート制限を考慮して待機
            time.sleep(1)

        except Exception as e:
            print(f"エラー ({symbol}): {e}")
            results[symbol] = {"error": str(e)}

    return results

# 使用例
symbols = ["7203.T", "6758.T", "9984.T"]  # トヨタ、ソニー、ソフトバンク
results = fetch_multiple_stocks_sequential(symbols, "1mo", "1d")

# 結果の確認
for symbol, result in results.items():
    if result.get("success"):
        count = result["data"]["records_count"]
        print(f"{symbol}: {count}件取得成功")
    else:
        print(f"{symbol}: 取得失敗")
```

### 2. バルクAPIを使用した一括取得（推奨）

```python
def start_bulk_job(symbols, period="1mo", interval="1d"):
    """バルクジョブを開始"""
    url = "http://localhost:8000/api/v1/bulk-data/jobs"
    payload = {
        "symbols": symbols,
        "period": period,
        "interval": interval
    }

    response = requests.post(url, json=payload)
    return response.json()

def check_job_status(job_id):
    """ジョブのステータスを確認"""
    url = f"http://localhost:8000/api/v1/bulk-data/jobs/{job_id}"
    response = requests.get(url)
    return response.json()

def wait_for_job_completion(job_id, timeout=300, interval=5):
    """ジョブの完了を待機"""
    import time

    start_time = time.time()

    while time.time() - start_time < timeout:
        status = check_job_status(job_id)

        if not status.get("success"):
            return None

        job_status = status["data"]["status"]
        progress = status["data"].get("progress_percentage", 0)

        print(f"進捗: {progress:.1f}% - {job_status}")

        if job_status == "completed":
            return status
        elif job_status == "failed":
            return status

        time.sleep(interval)

    print("タイムアウトしました")
    return None

# 使用例
symbols = ["7203.T", "6758.T", "9984.T", "8306.T", "9433.T"]

# ジョブ開始
job = start_bulk_job(symbols, "1mo", "1d")

if job.get("success"):
    job_id = job["data"]["job_id"]
    print(f"ジョブID: {job_id}")

    # 完了を待機
    result = wait_for_job_completion(job_id)

    if result and result["data"]["status"] == "completed":
        print("全ての銘柄のデータ取得が完了しました")
        print(f"処理済み: {result['data']['processed_symbols']}")
    else:
        print("ジョブが失敗しました")
```
---
## データの検索とフィルタリング

### 1. 日付範囲指定での検索

```python
def get_stocks_by_date_range(symbol, start_date, end_date, interval="1d"):
    """日付範囲でデータを取得"""
    url = "http://localhost:8000/api/stocks"
    params = {
        "symbol": symbol,
        "interval": interval,
        "start_date": start_date,
        "end_date": end_date,
        "limit": 1000
    }

    response = requests.get(url, params=params)
    return response.json()

# 使用例：2024年1月のデータを取得
data = get_stocks_by_date_range(
    symbol="7203.T",
    start_date="2024-01-01",
    end_date="2024-01-31",
    interval="1d"
)

print(f"取得件数: {len(data['data'])}")
```

### 2. ページネーションを使った大量データ取得

```python
def get_all_stocks_paginated(symbol, interval="1d", page_size=100):
    """ページネーションで全データを取得"""
    all_data = []
    offset = 0

    while True:
        url = "http://localhost:8000/api/stocks"
        params = {
            "symbol": symbol,
            "interval": interval,
            "limit": page_size,
            "offset": offset
        }

        response = requests.get(url, params=params)
        result = response.json()

        if not result.get("success"):
            break

        data = result["data"]
        if not data:
            break

        all_data.extend(data)

        # 次のページがあるか確認
        pagination = result.get("pagination", {})
        if not pagination.get("has_next", False):
            break

        offset += page_size
        print(f"取得済み: {len(all_data)}件")

    return all_data

# 使用例
all_data = get_all_stocks_paginated("7203.T", "1d", 100)
print(f"総取得件数: {len(all_data)}")
```

### 3. 複数時間軸のデータを統合

```python
def get_multi_timeframe_data(symbol):
    """複数の時間軸でデータを取得"""
    timeframes = {
        "daily": "1d",
        "weekly": "1wk",
        "monthly": "1mo"
    }

    results = {}

    for name, interval in timeframes.items():
        url = "http://localhost:8000/api/stocks"
        params = {
            "symbol": symbol,
            "interval": interval,
            "limit": 100
        }

        response = requests.get(url, params=params)
        results[name] = response.json()

    return results

# 使用例
multi_data = get_multi_timeframe_data("7203.T")

for timeframe, data in multi_data.items():
    if data.get("success"):
        count = len(data["data"])
        print(f"{timeframe}: {count}件")
```
---
## エラーハンドリング

### 1. 基本的なエラーハンドリング

```python
def fetch_with_error_handling(symbol, period="1mo", interval="1d"):
    """エラーハンドリング付きデータ取得"""
    try:
        response = requests.post(
            "http://localhost:8000/api/stocks/data",
            json={
                "symbol": symbol,
                "period": period,
                "interval": interval
            },
            timeout=30
        )

        # HTTPステータスコードをチェック
        response.raise_for_status()

        result = response.json()

        # APIレベルのエラーチェック
        if not result.get("success"):
            error = result.get("error", {})
            error_code = error.get("code", "UNKNOWN")
            error_message = error.get("message", "不明なエラー")

            print(f"APIエラー [{error_code}]: {error_message}")
            return None

        return result

    except requests.exceptions.ConnectionError:
        print("接続エラー: サーバーに接続できません")
        return None

    except requests.exceptions.Timeout:
        print("タイムアウトエラー: リクエストがタイムアウトしました")
        return None

    except requests.exceptions.HTTPError as e:
        status_code = e.response.status_code

        if status_code == 400:
            print("リクエストエラー: パラメータを確認してください")
        elif status_code == 500:
            print("サーバーエラー: しばらく待ってから再試行してください")
        else:
            print(f"HTTPエラー {status_code}: {e}")

        return None

    except Exception as e:
        print(f"予期しないエラー: {e}")
        return None

# 使用例
result = fetch_with_error_handling("7203.T", "1mo", "1d")

if result:
    print("データ取得成功")
else:
    print("データ取得失敗")
```

### 2. リトライ機能付きクライアント

```python
from functools import wraps
import time

def retry_on_failure(max_retries=3, delay=1, backoff=2):
    """リトライデコレータ"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            current_delay = delay

            for attempt in range(max_retries):
                try:
                    result = func(*args, **kwargs)

                    if result:
                        return result

                    if attempt < max_retries - 1:
                        print(f"リトライ {attempt + 1}/{max_retries} ({current_delay}秒後)")
                        time.sleep(current_delay)
                        current_delay *= backoff

                except Exception as e:
                    if attempt == max_retries - 1:
                        print(f"最大リトライ回数に達しました: {e}")
                        raise

                    print(f"エラー発生 (試行 {attempt + 1}): {e}")
                    time.sleep(current_delay)
                    current_delay *= backoff

            return None

        return wrapper
    return decorator

@retry_on_failure(max_retries=3, delay=2, backoff=2)
def fetch_with_retry(symbol, period="1mo", interval="1d"):
    """リトライ機能付きデータ取得"""
    return fetch_with_error_handling(symbol, period, interval)

# 使用例
result = fetch_with_retry("7203.T", "1mo", "1d")
```
---
## 実践的なユースケース

### 1. 日次データ更新スクリプト

```python
import schedule
import time
from datetime import datetime

class DailyUpdater:
    def __init__(self, symbols):
        self.symbols = symbols
        self.base_url = "http://localhost:8000"

    def update_all_symbols(self):
        """全銘柄のデータを更新"""
        print(f"[{datetime.now()}] データ更新開始")

        for symbol in self.symbols:
            try:
                response = requests.post(
                    f"{self.base_url}/api/stocks/data",
                    json={
                        "symbol": symbol,
                        "period": "5d",
                        "interval": "1d"
                    }
                )

                result = response.json()

                if result.get("success"):
                    saved = result["data"]["saved_records"]
                    print(f"  {symbol}: {saved}件保存")
                else:
                    print(f"  {symbol}: エラー")

                time.sleep(1)  # レート制限対策

            except Exception as e:
                print(f"  {symbol}: 例外 - {e}")

        print(f"[{datetime.now()}] データ更新完了")

    def run_scheduled(self):
        """スケジュール実行"""
        # 平日の16:00に実行（東証の取引終了後）
        schedule.every().monday.at("16:00").do(self.update_all_symbols)
        schedule.every().tuesday.at("16:00").do(self.update_all_symbols)
        schedule.every().wednesday.at("16:00").do(self.update_all_symbols)
        schedule.every().thursday.at("16:00").do(self.update_all_symbols)
        schedule.every().friday.at("16:00").do(self.update_all_symbols)

        print("スケジューラー起動")

        while True:
            schedule.run_pending()
            time.sleep(60)

# 使用例
watchlist = ["7203.T", "6758.T", "9984.T", "8306.T"]
updater = DailyUpdater(watchlist)

# 即座に実行
updater.update_all_symbols()

# スケジュール実行（本番環境）
# updater.run_scheduled()
```

### 2. テクニカル分析との連携

```python
import pandas as pd

def get_stock_dataframe(symbol, interval="1d", limit=200):
    """株価データをDataFrameで取得"""
    url = "http://localhost:8000/api/stocks"
    params = {
        "symbol": symbol,
        "interval": interval,
        "limit": limit
    }

    response = requests.get(url, params=params)
    result = response.json()

    if not result.get("success"):
        return None

    # DataFrameに変換
    df = pd.DataFrame(result["data"])

    # 日付を datetime 型に変換
    if "date" in df.columns:
        df["date"] = pd.to_datetime(df["date"])
        df.set_index("date", inplace=True)
    elif "datetime" in df.columns:
        df["datetime"] = pd.to_datetime(df["datetime"])
        df.set_index("datetime", inplace=True)

    # 降順から昇順に並び替え
    df.sort_index(inplace=True)

    return df

def calculate_indicators(df):
    """テクニカル指標を計算"""
    # 移動平均
    df["SMA_5"] = df["close"].rolling(window=5).mean()
    df["SMA_25"] = df["close"].rolling(window=25).mean()
    df["SMA_75"] = df["close"].rolling(window=75).mean()

    # ボリンジャーバンド
    df["BB_middle"] = df["close"].rolling(window=20).mean()
    bb_std = df["close"].rolling(window=20).std()
    df["BB_upper"] = df["BB_middle"] + (bb_std * 2)
    df["BB_lower"] = df["BB_middle"] - (bb_std * 2)

    return df

# 使用例
df = get_stock_dataframe("7203.T", "1d", 200)

if df is not None:
    df = calculate_indicators(df)

    # 最新のデータを表示
    print(df[["close", "SMA_5", "SMA_25", "SMA_75"]].tail())

    # ゴールデンクロスの検出
    df["golden_cross"] = (df["SMA_5"] > df["SMA_25"]) & (df["SMA_5"].shift(1) <= df["SMA_25"].shift(1))
    golden_crosses = df[df["golden_cross"]]

    print(f"\nゴールデンクロス発生日: {len(golden_crosses)}回")
```
---
## パフォーマンス最適化

### 1. 並列処理による高速化

```python
from concurrent.futures import ThreadPoolExecutor, as_completed

def fetch_single_symbol(symbol, period="1mo", interval="1d"):
    """単一銘柄のデータを取得"""
    try:
        response = requests.post(
            "http://localhost:8000/api/stocks/data",
            json={
                "symbol": symbol,
                "period": period,
                "interval": interval
            },
            timeout=30
        )
        return symbol, response.json()
    except Exception as e:
        return symbol, {"error": str(e)}

def fetch_multiple_parallel(symbols, period="1mo", interval="1d", max_workers=5):
    """並列処理で複数銘柄を取得"""
    results = {}

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # 全ての銘柄に対してタスクを投入
        futures = {
            executor.submit(fetch_single_symbol, symbol, period, interval): symbol
            for symbol in symbols
        }

        # 完了したタスクから順次処理
        for future in as_completed(futures):
            symbol, result = future.result()
            results[symbol] = result

            if result.get("success"):
                print(f"✓ {symbol}: 取得完了")
            else:
                print(f"✗ {symbol}: 取得失敗")

    return results

# 使用例
symbols = ["7203.T", "6758.T", "9984.T", "8306.T", "9433.T",
           "8035.T", "6501.T", "6861.T", "6902.T", "7974.T"]

# 並列処理で高速取得
results = fetch_multiple_parallel(symbols, "1mo", "1d", max_workers=5)

# 成功した銘柄数を集計
success_count = sum(1 for r in results.values() if r.get("success"))
print(f"\n成功: {success_count}/{len(symbols)}")
```

### 2. キャッシュの活用

```python
from datetime import datetime, timedelta
import json
import os

class CachedStockClient:
    def __init__(self, cache_dir="cache", cache_ttl=3600):
        self.cache_dir = cache_dir
        self.cache_ttl = cache_ttl

        # キャッシュディレクトリの作成
        os.makedirs(cache_dir, exist_ok=True)

    def _get_cache_path(self, symbol, interval):
        """キャッシュファイルのパスを生成"""
        filename = f"{symbol}_{interval}.json"
        return os.path.join(self.cache_dir, filename)

    def _is_cache_valid(self, cache_path):
        """キャッシュが有効か確認"""
        if not os.path.exists(cache_path):
            return False

        # ファイルの更新時刻をチェック
        mtime = os.path.getmtime(cache_path)
        age = time.time() - mtime

        return age < self.cache_ttl

    def get_stocks(self, symbol, interval="1d", limit=100, use_cache=True):
        """キャッシュを使用してデータを取得"""
        cache_path = self._get_cache_path(symbol, interval)

        # キャッシュの確認
        if use_cache and self._is_cache_valid(cache_path):
            print(f"キャッシュから取得: {symbol}")
            with open(cache_path, "r", encoding="utf-8") as f:
                return json.load(f)

        # APIからデータを取得
        print(f"APIから取得: {symbol}")
        url = "http://localhost:8000/api/stocks"
        params = {
            "symbol": symbol,
            "interval": interval,
            "limit": limit
        }

        response = requests.get(url, params=params)
        result = response.json()

        # キャッシュに保存
        if result.get("success"):
            with open(cache_path, "w", encoding="utf-8") as f:
                json.dump(result, f, ensure_ascii=False, indent=2)

        return result

# 使用例
client = CachedStockClient(cache_ttl=3600)  # 1時間キャッシュ

# 初回はAPIから取得
data1 = client.get_stocks("7203.T", "1d", 100)

# 2回目はキャッシュから取得（高速）
data2 = client.get_stocks("7203.T", "1d", 100)
```
---
## まとめ

このガイドでは、STOCK-INVESTMENT-ANALYZER APIの実践的な使用方法を紹介しました。

### 重要なポイント

1. **エラーハンドリング**: 常に適切なエラー処理を実装する
2. **レート制限**: 連続リクエスト時は適切な待機時間を設ける
3. **バルクAPI**: 大量データ取得時はバルクAPIを活用する
4. **キャッシュ**: 頻繁にアクセスするデータはキャッシュを活用する
5. **並列処理**: パフォーマンスが必要な場合は並列処理を検討する

### 次のステップ

- [APIリファレンス](./api_reference.md) - 全エンドポイントの詳細仕様
- [APIバージョニングガイド](./versioning_guide.md) - バージョン管理の詳細
- [アーキテクチャ概要](../architecture/architecture_overview.md) - システム設計の理解

### トラブルシューティング

問題が発生した場合：
1. エンドポイントURLが正しいか確認
2. リクエストパラメータの形式が正しいか確認
3. サーバーが起動しているか確認（`http://localhost:8000`）
4. エラーメッセージの内容を確認
---
**最終更新**: 2025-01-15
**バージョン**: 1.0.0
