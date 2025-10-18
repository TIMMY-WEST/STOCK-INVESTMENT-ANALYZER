---
category: monitoring
ai_context: low
last_updated: 2025-10-18
related_docs:
  - ../architecture/system_monitoring_design.md
  - ../architecture/batch_processing_design.md
---

# バッチ処理監視・ログ機能ガイド

## 概要

Phase 2で実装されたバッチ処理の監視・ログ機能について説明します。

## 構造化ログ

### ログフォーマット

バッチ処理のログはJSON形式で出力されます。

```json
{
  "timestamp": "2024-01-15T10:30:00Z",
  "batch_id": "batch_20240115_103000",
  "worker_id": 1,
  "stock_code": "7203",
  "action": "data_fetch",
  "status": "success",
  "duration_ms": 1500,
  "records_count": 50,
  "error_message": null,
  "retry_count": 0
}
```

### ログレベル

- **INFO**: 正常な処理の記録
- **WARNING**: リトライが発生した場合
- **ERROR**: エラーが発生した場合

### アクション種別

- `data_fetch`: データ取得
- `data_save`: データ保存
- `error_occurred`: エラー発生

### ステータス

- `success`: 成功
- `failed`: 失敗
- `retry`: リトライ中

## ログローテーション

ログファイルは自動的にローテーションされます。

### 設定

- **最大ファイルサイズ**: 10MB
- **バックアップファイル数**: 10個
- **ログディレクトリ**: `logs/`
- **ログファイル名**: `batch_bulk.log`

### ローテーション動作

1. `batch_bulk.log` が 10MB に達すると、`batch_bulk.log.1` にリネーム
2. 古いログは `.2`, `.3` ... と順次リネーム
3. 最大10個のバックアップファイルを保持
4. 11個目以降は自動削除

## メトリクス収集

### 進捗情報

バッチ処理の進捗情報には以下のメトリクスが含まれます:

```python
{
    'total': 100,              # 総銘柄数
    'processed': 50,           # 処理済み銘柄数
    'successful': 45,          # 成功数
    'failed': 5,               # 失敗数
    'progress_percentage': 50.0,  # 進捗率
    'elapsed_time': 120.5,     # 経過時間（秒）
    'stocks_per_second': 0.41, # 処理速度（銘柄/秒）
    'estimated_completion': '2024-01-15T14:30:00',  # ETA

    # Phase 2メトリクス
    'throughput': {
        'stocks_per_minute': 24.6,    # 分あたり処理銘柄数
        'records_per_minute': 1230.0  # 分あたり処理レコード数
    },
    'performance': {
        'success_rate': 90.0,              # 成功率 (%)
        'avg_processing_time_ms': 2400.0,  # 平均処理時間（ミリ秒）
        'total_records_fetched': 2250,     # 総取得レコード数
        'total_records_saved': 2150        # 総保存レコード数
    }
}
```

### パフォーマンス監視

#### スループット

- **stocks_per_minute**: 1分あたりに処理できる銘柄数
- **records_per_minute**: 1分あたりに保存できるレコード数

#### 成功率

- **success_rate**: 処理成功率（%）
- 計算式: `(成功数 / 処理済み数) × 100`

#### 平均処理時間

- **avg_processing_time_ms**: 銘柄あたりの平均処理時間（ミリ秒）
- データ取得から保存までの時間を含む

## 完了予定時刻（ETA）

### 計算方法

ETAは以下の方法で計算されます:

1. **経過時間の計算**: 開始時刻から現在までの経過時間
2. **処理速度の計算**: `処理済み数 / 経過時間`
3. **残り時間の推定**: `残り数 / 処理速度`
4. **ETAの算出**: `現在時刻 + 残り時間`

### 精度向上のポイント

- 処理が進むほど精度が向上します
- 最初の数件ではETAが大きくぶれる可能性があります
- 10件以上処理した後のETAが比較的正確です

## 使用例

### Pythonでの使用

```python
from services.bulk_data_service import BulkDataService
from utils.structured_logger import setup_structured_logging

# 構造化ログ設定
setup_structured_logging(
    log_dir='logs',
    log_level=logging.INFO
)

# バッチサービス初期化（batch_idを指定）
service = BulkDataService(
    max_workers=10,
    batch_id='batch-001'
)

# バッチ処理実行
result = service.fetch_multiple_stocks(
    symbols=['7203.T', '6758.T'],
    interval='1d',
    period='1mo'
)

# メトリクス確認
print(f"成功率: {result['performance']['success_rate']}%")
print(f"平均処理時間: {result['performance']['avg_processing_time_ms']}ms")
print(f"スループット: {result['throughput']['stocks_per_minute']}銘柄/分")
```

### ログファイルの確認

```bash
# 最新ログの確認
tail -f logs/batch_bulk.log

# JSON形式で整形して表示
tail -n 10 logs/batch_bulk.log | jq .

# 特定の銘柄のログを抽出
grep "7203" logs/batch_bulk.log | jq .

# エラーのみ抽出
grep '"status":"failed"' logs/batch_bulk.log | jq .
```

## トラブルシューティング

### ログが出力されない

1. `logs/` ディレクトリが存在するか確認
2. 書き込み権限があるか確認
3. `setup_structured_logging()` が呼ばれているか確認

### メトリクスが正しく表示されない

1. `tracker.update()` に必要なパラメータが渡されているか確認
2. `duration_ms`, `records_fetched`, `records_saved` が正しく設定されているか確認

### ETAが表示されない

1. 処理が開始されているか確認
2. `stocks_per_second` が0より大きいか確認（処理が進んでいない場合はETAは計算されません）

## 参考

- [仕様書](../docs/api_bulk_fetch.md) - Phase 2の詳細仕様
- [テストコード](../tests/test_structured_logger.py) - 構造化ログのテスト
- [メトリクステスト](../tests/test_progress_metrics.py) - メトリクス収集のテスト
