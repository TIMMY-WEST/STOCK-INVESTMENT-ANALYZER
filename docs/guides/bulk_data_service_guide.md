---
category: guide
ai_context: medium
last_updated: 2025-10-18
related_docs:
  - ../api/api_bulk_fetch.md
  - ../architecture/batch_processing_design.md
---

# バルクデータサービス利用ガイド

このガイドでは、`services.bulk_data_service` に実装されたバルクデータ取得機能の使い方、運用時の注意点、よくある質問をまとめます。PR #73 の機能に対応しています。

## 概要・目的
- 複数銘柄の株価データを並列で効率的に取得し、保存するためのサービスです。
- 進捗トラッキングや完了時間の推定、リストファイルからの一括処理に対応しています。

## 主なクラスと機能

### BulkDataService
- 役割: データ取得・保存のオーケストレーション（並列処理・進捗通知・サマリー集計）
- 主要パラメータ
  - `max_workers: int` 並列ワーカー数（デフォルト: `10`）
  - `retry_count: int` リトライ回数（デフォルト: `3`）

#### 公開メソッド
- `fetch_multiple_stocks(symbols: List[str], interval: str = '1d', period: Optional[str] = None, progress_callback: Optional[Callable[[Dict[str, Any]], None]] = None) -> Dict[str, Any]`
  - 概要: 複数銘柄を並列で取得・保存し、サマリーを返します
  - 引数
    - `symbols`: 銘柄コードのリスト（例: `['7203.T', '6758.T']`）
    - `interval`: 時間軸（例: `'1d'`, `'1h'`, `'1wk'`）
    - `period`: 取得期間（例: `'1y'`, `'5y'`）。未指定の場合はFetcher側のデフォルト
    - `progress_callback`: 進捗更新時に呼ばれるコールバック (`Dict[str, Any]` を受け取る)
  - 戻り値: サマリー `Dict`
    - `total`, `processed`, `successful`, `failed`, `progress_percentage`, `elapsed_time`, `stocks_per_second`, `estimated_completion`, `error_details(最大100件)`, `results(各銘柄の詳細)`

- `fetch_all_stocks_from_list_file(file_path: str, interval: str = '1d', period: Optional[str] = None, progress_callback: Optional[Callable[[Dict[str, Any]], None]] = None) -> Dict[str, Any]`
  - 概要: テキストファイルから銘柄リストを読み込み、一括処理を実行します
  - 引数
    - `file_path`: 1行1銘柄のテキストファイルパス（UTF-8）
    - その他は `fetch_multiple_stocks` と同様
  - 例外: ファイル不存在や読み込みエラー時に `BulkDataServiceError` を送出

- `estimate_completion_time(symbol_count: int, interval: str = '1d') -> Dict[str, Any]`
  - 概要: サンプル実行時間から総処理時間を推定します（並列数考慮）
  - 引数
    - `symbol_count`: 処理予定の銘柄数
    - `interval`: 時間軸（サンプル実行に使用）
  - 戻り値: 推定 `Dict`（`symbol_count`, `sample_time_per_stock`, `estimated_total_seconds`, `estimated_total_minutes`, `max_workers`）。エラー時は `error` を含みます

### ProgressTracker
- 役割: 進捗の集計と推定（速度・ETA）
- 主なメソッド
  - `update(symbol: str, success: bool, error_message: Optional[str] = None)`
  - `get_progress() -> Dict[str, Any]`
  - `get_summary() -> Dict[str, Any]`

## 使用方法

### インポートと初期化
```python
from services.bulk_data_service import BulkDataService

service = BulkDataService(max_workers=4, retry_count=2)
```

### 複数銘柄の並列取得
```python
symbols = ['7203.T', '6758.T', '9984.T']

# 進捗コールバック（任意）
progress_events = []
def on_progress(p):
    # p は Dict（processed, total, progress_percentage, stocks_per_second, estimated_completion 等）
    progress_events.append(p)

summary = service.fetch_multiple_stocks(
    symbols=symbols,
    interval='1d',
    period=None,
    progress_callback=on_progress
)

print(summary['successful'], summary['failed'])
for r in summary['results']:
    print(r['symbol'], r.get('success'), r.get('records_saved'), r.get('error'))
```

### ファイルから銘柄を読み込んで取得
```python
# list.txt（UTF-8, 1行1銘柄）
# 例:
# 7203.T
# 6758.T
# 9984.T

summary = service.fetch_all_stocks_from_list_file(
    file_path='list.txt',
    interval='1d',
    period=None,
    progress_callback=None
)
print(summary['total'], summary['successful'], summary['failed'])
```

### 完了時間の推定
```python
est = service.estimate_completion_time(symbol_count=500, interval='1d')
print(est)
```

## 運用ガイド

- 並列数（`max_workers`）
  - 通常はマシンのCPUコア数〜その2倍程度を目安に調整
  - APIレートやネットワーク帯域に応じて増減。失敗が増える場合は縮小

- リトライ（`retry_count`）
  - 一時的なネットワークエラーやAPI応答エラーに備えて設定
  - 連続失敗時は原因調査（レート制限、シンボルミス、DB障害など）

- ログ確認
  - 10件ごとの進捗ログに加え、失敗時のエラー詳細が `error_details` に最大100件保持されます
  - アプリ側のロガー設定・保存先（コンソール/ファイル）を適切に構成してください

- 進捗コールバック
  - UIや監視に進捗を反映したい場合に利用。重い処理は避け、例外は内部で捕捉・ログ化されます

## 制限事項と注意点

- APIレート制限
  - 外部API（例: yfinance）に依存するため、レート制限や一時的な失敗が発生します。並列数・リトライで緩和可能ですが、過負荷を避けてください

- シンボル形式
  - 日本株は一般に `XXXX.T` 形式（例: トヨタ `7203.T`）。取得元仕様に従ってください

- データ品質
  - 欠損や分割等のイベントによりデータが不整合になる可能性があります。保存前の検証・保存後の監視を推奨します

- 依存関係
  - ランタイム依存は `requirements.txt` を参照してください

## よくある質問（FAQ）

**Q. 何銘柄まで一度に処理できますか？**
- ハードウェア性能とAPI制約に依存します。大規模処理はバッチ分割と進捗通知の活用を推奨します。

**Q. 進捗をWeb UIで表示したいです。**
- `progress_callback` を使ってUIへ送る仕組み（WebSocket等）を追加してください。コールバック内の例外はサービス側でログ化されます。

**Q. 保存前のデータ整形を挟めますか？**
- `StockDataFetcher.convert_to_dict` の出力をカスタマイズする、または `fetch_single_stock` 前後にフックを設ける拡張で対応可能です。

## 既存サービスとの連携

- `StockDataFetcher`
  - Yahoo Finance等からデータ取得、`pandas.DataFrame` を取得、辞書リストへ変換

- `StockDataSaver`
  - 変換済みデータをDBへ保存（保存件数やスキップ件数を返却）

これらは `BulkDataService` 内部から利用されます。詳細は各サービスの実装を参照してください。

---

更新履歴
- 初版（PR #73）: ガイド追加
