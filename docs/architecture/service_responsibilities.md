# サービス責任分掌ドキュメント

## 目次

- [1. 概要](#1-概要)
- [2. サービス一覧と責任範囲](#2-サービス一覧と責任範囲)
- [3. 主要メソッドの説明](#3-主要メソッドの説明)
- [4. 重複機能の洗い出し](#4-重複機能の洗い出し)
- [5. 統合候補の提案](#5-統合候補の提案)
- [6. 不要なコードの特定](#6-不要なコードの特定)
- [7. サービス間連携パターン](#7-サービス間連携パターン)

## 1. 概要

本ドキュメントは、`app/services/` 配下の全サービスクラスの責任範囲を明確化し、重複機能や不要コードを特定することで、システムのメンテナンス性と拡張性を向上させることを目的としています。

【サービスモジュール構造（実装済み）】

**実装完了済み（v1.0）:**

システムは機能別にモジュール化されています:

```
app/services/
├── stock_data/      # 株価データ取得・保存
│   ├── fetcher.py          # StockDataFetcher
│   ├── saver.py            # StockDataSaver
│   ├── converter.py        # データ変換
│   ├── validator.py        # データ検証
│   ├── orchestrator.py     # StockDataOrchestrator
│   └── scheduler.py        # StockDataScheduler
├── bulk/            # 一括データ取得
│   └── bulk_service.py     # BulkDataService
├── jpx/             # JPX銘柄マスタ管理
│   └── jpx_stock_service.py # JPXStockService
├── batch/           # バッチ実行管理
│   └── batch_service.py    # BatchService
└── common/          # 共通機能
    └── error_handler.py    # ErrorHandler
```

**ドキュメント更新日:** 2025-01-02
**対象サービス数:** 10
**実装済みモジュール:** stock_data, bulk, jpx, batch, common

## 2. サービス一覧と責任範囲

### 2.1 サービス分類

サービスを以下の4つのカテゴリに分類します:

#### A. データ取得サービス
- **StockDataFetcher** - 外部API（Yahoo Finance）からのデータ取得
- **JPXStockService** - JPX銘柄マスタの管理

#### B. データ保存サービス
- **StockDataSaver** - データベースへのデータ保存

#### C. オーケストレーションサービス
- **StockDataOrchestrator** - 単一銘柄のデータ取得・保存を統括
- **BulkDataService** - 複数銘柄の一括データ取得・保存を統括

#### D. 管理・補助サービス
- **BatchService** - バッチ実行履歴の管理
- **StockDataScheduler** - スケジュール管理
- **ErrorHandler** - エラーハンドリングの統一管理

### 2.2 各サービスの責任範囲

#### 2.2.1 StockDataFetcher（データ取得サービス）

**ファイルパス:** [app/services/stock_data/fetcher.py](app/services/stock_data/fetcher.py)

**責任範囲:**
- Yahoo Finance APIからの株価データ取得
- 銘柄コードのバリデーション
- Yahoo Finance用の銘柄コードフォーマット変換
- 取得データのPython辞書形式への変換
- 最新データ日付の取得

**主要メソッド:**
- `fetch_stock_data(symbol, period, interval)` - 単一銘柄のデータ取得
- `fetch_multiple_timeframes(symbol, timeframes)` - 複数時間軸の一括取得
- `fetch_batch_stock_data(symbols, period, interval)` - 複数銘柄の一括取得
- `convert_to_dict(df_data, symbol)` - DataFrameを辞書形式に変換
- `get_latest_data_date(symbol, interval)` - 最新データ日付の取得

**依存関係:**
- `yfinance` - Yahoo Finance API
- `StructuredLogger` - ロギング

**カスタム例外:**
- `StockDataFetchError` - データ取得時のエラー
---
#### 2.2.2 StockDataSaver（データ保存サービス）

**ファイルパス:** [app/services/stock_data/saver.py](app/services/stock_data/saver.py)

**責任範囲:**
- データベースへの株価データ保存
- 時間軸に応じた適切なテーブルへの振り分け
- 重複データのフィルタリング
- UPSERT操作（INSERT or UPDATE）
- トランザクション管理
- データの最新日付・レコード数の取得

**主要メソッド:**
- `save_stock_data(stock_data, interval)` - 単一銘柄のデータ保存
- `save_multiple_timeframes(symbol, timeframes_data)` - 複数時間軸の一括保存
- `save_batch_stock_data(batch_data, interval)` - 複数銘柄の一括保存
- `_filter_duplicate_data(symbol, data_list, interval, session)` - 重複データフィルタリング
- `get_latest_date(symbol, interval)` - 最新データ日付の取得
- `count_records(symbol, interval, start_date, end_date)` - レコード数カウント

**依存関係:**
- `SQLAlchemy Models` - 各時間軸のモデル
- `TimeframeUtils` - 時間軸に応じたモデル選択
- `StructuredLogger` - ロギング

**カスタム例外:**
- `StockDataSaveError` - データ保存時のエラー
---
#### 2.2.3 StockDataOrchestrator（統括サービス）

**ファイルパス:** [app/services/stock_data/orchestrator.py](app/services/stock_data/orchestrator.py)

**責任範囲:**
- 単一銘柄のデータ取得・保存フローの統括
- 複数時間軸の一括処理
- データ整合性チェック
- システムステータスの取得
- 全時間軸の更新処理

**主要メソッド:**
- `fetch_and_save(symbol, period, interval)` - 単一銘柄・単一時間軸の取得・保存
- `fetch_and_save_multiple_timeframes(symbol, timeframes, period)` - 複数時間軸の一括処理
- `check_data_integrity(symbol, interval, start_date, end_date)` - データ整合性チェック
- `get_status(symbol, intervals)` - ステータス取得
- `update_all_timeframes(symbol)` - 全時間軸の更新

**依存関係:**
- `StockDataFetcher` - データ取得
- `StockDataSaver` - データ保存
- `StructuredLogger` - ロギング

**カスタム例外:**
- `StockDataOrchestrationError` - オーケストレーションエラー

**特徴:**
- Fetcher と Saver を組み合わせた高レベルサービス
- エラーハンドリングとロギングを統合
---
#### 2.2.4 BulkDataService（一括取得サービス）

**ファイルパス:** [app/services/bulk/bulk_service.py](app/services/bulk/bulk_service.py)

**責任範囲:**
- 複数銘柄のデータを並列処理で効率的に取得・保存
- 進捗トラッキングとWebSocket経由での進捗配信
- ETA（残り時間）推定
- バッチ処理とパラレル処理の2つのモード提供
- リトライ機能
- エラーハンドリングと詳細ロギング

**主要メソッド:**
- `fetch_single_stock(symbol, period, interval, batch_id)` - 単一銘柄取得（バッチ管理付き）
- `fetch_multiple_stocks(symbols, period, interval, use_parallel)` - 複数銘柄取得
- `_fetch_multiple_stocks_batch(symbols, period, interval, batch_id)` - バッチモード処理
- `_fetch_multiple_stocks_parallel(symbols, period, interval, batch_id)` - パラレルモード処理
- `fetch_all_stocks_from_list_file(file_path, period, interval)` - リストファイルから一括取得
- `estimate_completion_time(symbols, period, interval)` - 処理時間の推定

**依存関係:**
- `StockDataFetcher` - データ取得
- `StockDataSaver` - データ保存
- `StructuredLogger` - 通常ログ + バッチログ
- `ErrorHandler` - エラー処理
- `concurrent.futures.ThreadPoolExecutor` - 並列処理

**カスタム例外:**
- `BulkDataServiceError` - バルクデータ処理エラー

**内部クラス:**
- `ProgressTracker` - 進捗管理クラス

**特徴:**
- ThreadPoolExecutor で並列処理（最大10並列）
- WebSocket経由で進捗配信
- ETA推定機能
- バッチ実行管理との連携
---
#### 2.2.5 JPXStockService（JPX銘柄サービス）

**ファイルパス:** [app/services/jpx/jpx_stock_service.py](app/services/jpx/jpx_stock_service.py)

**責任範囲:**
- JPX（日本取引所グループ）公式サイトからの銘柄一覧取得
- 銘柄マスタデータの正規化・変換
- 銘柄マスタの更新管理（追加・更新・非アクティブ化）
- 銘柄一覧の取得（フィルタリング、ページネーション対応）

**主要メソッド:**
- `fetch_jpx_stock_list()` - JPX銘柄一覧の取得
- `update_stock_master()` - 銘柄マスタの更新
- `get_stock_list(is_active, market_codes, page, limit)` - 銘柄一覧の取得
- `_normalize_jpx_data(raw_data)` - データの正規化
- `_create_update_record()` - 更新レコードの作成
- `_get_existing_stock_codes()` - 既存銘柄コードの取得
- `_insert_stock(stock, session)` - 銘柄の追加
- `_update_stock(stock, session)` - 銘柄の更新
- `_deactivate_stocks(delisted_codes, session)` - 銘柄の非アクティブ化
- `_complete_update_record(update_id, stats, session)` - 更新レコードの完了

**依存関係:**
- `StockMaster` モデル - 銘柄マスタデータ
- `StructuredLogger` - ロギング
- `selenium` - Webスクレイピング

**カスタム例外:**
- `JPXStockServiceError` - 基本エラー
- `JPXDownloadError` - ダウンロードエラー
- `JPXParseError` - パースエラー

**定数:**
- `JPX_STOCK_LIST_URL` - JPX銘柄一覧のURL
- `REQUEST_TIMEOUT` - リクエストタイムアウト（30秒）

**特徴:**
- JPX公式サイトから銘柄一覧を取得
- 銘柄マスタの完全な更新管理（追加・更新・非アクティブ化）
---
#### 2.2.6 BatchService（バッチ管理サービス）

**ファイルパス:** [app/services/batch/batch_service.py](app/services/batch/batch_service.py)

**責任範囲:**
- バッチ処理の実行履歴管理
- バッチ実行の作成・取得・更新
- バッチ実行詳細の管理
- バッチ一覧の取得（フィルタリング、ページネーション対応）

**主要メソッド:**
- `create_batch(batch_type, total_count, parameters)` - バッチ実行の作成
- `get_batch(batch_id)` - バッチ実行の取得
- `update_batch_progress(batch_id, success_count, failure_count, current_symbol)` - 進捗更新
- `complete_batch(batch_id, status, error_message)` - バッチ実行の完了
- `list_batches(batch_type, status, page, limit)` - バッチ一覧の取得
- `create_batch_detail(batch_id, symbol, interval, status, records_count)` - 詳細レコードの作成
- `update_batch_detail(detail_id, status, records_count, error_message)` - 詳細レコードの更新
- `get_batch_details(batch_id)` - バッチ詳細の取得

**依存関係:**
- `BatchExecution` モデル - バッチ実行管理
- `BatchExecutionDetail` モデル - バッチ実行詳細
- `StructuredLogger` - ロギング

**カスタム例外:**
- `BatchServiceError` - バッチサービスエラー

**特徴:**
- バッチ処理の完全なライフサイクル管理
- 詳細な実行履歴の記録
- フィルタリングとページネーション対応
---
#### 2.2.7 StockDataScheduler（スケジューラ）

**ファイルパス:** [app/services/stock_data/scheduler.py](app/services/stock_data/scheduler.py)

**責任範囲:**
- 定期的なデータ更新のスケジューリング
- ジョブの追加・削除・管理
- ジョブの実行履歴とエラーのロギング

**主要メソッド:**
- `add_daily_update_job(symbols, timeframes, hour, minute, timezone)` - 日次更新ジョブの追加
- `add_intraday_update_job(symbols, timeframes, interval_minutes, timezone)` - イントラデイ更新ジョブの追加
- `add_custom_job(job_id, func, trigger, **trigger_args)` - カスタムジョブの追加
- `remove_job(job_id)` - ジョブの削除
- `start()` - スケジューラの起動
- `shutdown(wait)` - スケジューラの停止
- `get_jobs()` - ジョブ一覧の取得
- `print_jobs()` - ジョブ一覧の表示
- `_update_job(symbols, timeframes)` - 更新ジョブの実行
- `_setup_event_listeners()` - イベントリスナーの設定
- `_job_executed_listener(event)` - ジョブ実行イベント
- `_job_error_listener(event)` - ジョブエラーイベント

**依存関係:**
- `StockDataOrchestrator` - 定期実行する処理
- `APScheduler` - スケジューリング
- `StructuredLogger` - ロギング

**特徴:**
- Cron形式のスケジュール設定
- バックグラウンド実行
- イベントリスナーによるログ記録

**グローバル関数:**
- `get_scheduler()` - シングルトンインスタンスの取得
---
#### 2.2.8 ErrorHandler（エラーハンドリングサービス）

**ファイルパス:** [app/services/common/error_handler.py](app/services/common/error_handler.py)

**責任範囲:**
- エラーの分類（一時的、恒久的、システムエラー）
- エラーハンドリングの統一管理
- リトライロジック（指数バックオフ）
- エラーログの記録と統計管理
- エラーレポートの生成

**主要メソッド:**
- `classify_error(error)` - エラーの分類
- `handle_error(error, context, retry_count)` - エラーハンドリング
- `retry_with_backoff(retry_count)` - バックオフ計算
- `generate_error_report(start_time, end_time)` - エラーレポート生成
- `get_error_statistics()` - エラー統計の取得
- `clear_error_records()` - エラー記録のクリア
- `_handle_temporary_error(error, context, retry_count)` - 一時的エラーの処理
- `_handle_permanent_error(error, context)` - 恒久的エラーの処理
- `_handle_system_error(error, context)` - システムエラーの処理
- `_log_error(error_type, error, context, action)` - エラーログの記録

**依存関係:**
- `StructuredLogger` - ロギング

**カスタム列挙型:**
- `ErrorType` - エラータイプ（TEMPORARY, PERMANENT, SYSTEM）
- `ErrorAction` - エラーアクション（RETRY, SKIP, ABORT）

**カスタムクラス:**
- `ErrorRecord` - エラー記録のデータクラス

**特徴:**
- エラーの詳細な分類と適切なアクション決定
- 指数バックオフによるリトライ
- エラー統計とレポート生成
---
## 3. 主要メソッドの説明

### 3.1 データ取得フロー

#### 単一銘柄・単一時間軸の取得
```
StockDataOrchestrator.fetch_and_save()
  └─> StockDataFetcher.fetch_stock_data()
  └─> StockDataSaver.save_stock_data()
```

#### 単一銘柄・複数時間軸の取得
```
StockDataOrchestrator.fetch_and_save_multiple_timeframes()
  └─> StockDataFetcher.fetch_multiple_timeframes()
  └─> StockDataSaver.save_multiple_timeframes()
```

#### 複数銘柄・単一時間軸の取得（バッチモード）
```
BulkDataService.fetch_multiple_stocks(use_parallel=False)
  └─> BulkDataService._fetch_multiple_stocks_batch()
      └─> StockDataFetcher.fetch_stock_data()
      └─> StockDataSaver.save_stock_data()
      └─> BatchService.update_batch_progress()
```

#### 複数銘柄・単一時間軸の取得（並列モード）
```
BulkDataService.fetch_multiple_stocks(use_parallel=True)
  └─> BulkDataService._fetch_multiple_stocks_parallel()
      └─> ThreadPoolExecutor.map()
          └─> BulkDataService.fetch_single_stock()
              └─> StockDataFetcher.fetch_stock_data()
              └─> StockDataSaver.save_stock_data()
              └─> BatchService.create_batch_detail()
```

### 3.2 エラーハンドリングフロー

```
BulkDataService.fetch_single_stock()
  └─> try-except
      └─> ErrorHandler.classify_error()
      └─> ErrorHandler.handle_error()
          └─> ErrorAction.RETRY → retry_with_backoff()
          └─> ErrorAction.SKIP → 次の処理へ
          └─> ErrorAction.ABORT → 処理中断
```

### 3.3 スケジュール実行フロー

```
StockDataScheduler.add_daily_update_job()
  └─> APScheduler.add_job()
      └─> StockDataScheduler._update_job()
          └─> StockDataOrchestrator.fetch_and_save_multiple_timeframes()
```

## 4. 重複機能の洗い出し

### 4.1 データ取得機能の重複

#### 問題点
`StockDataFetcher` と `BulkDataService` の両方に以下の機能が存在:
- 単一銘柄のデータ取得
- 複数銘柄のデータ取得

**重複箇所:**

1. **StockDataFetcher.fetch_batch_stock_data()**
   - [app/services/stock_data_fetcher.py:213-337](app/services/stock_data_fetcher.py#L213-L337)
   - 複数銘柄のデータを順次取得

2. **BulkDataService.fetch_single_stock()**
   - [app/services/bulk_data_service.py:199-312](app/services/bulk_data_service.py#L199-L312)
   - 単一銘柄のデータ取得（内部で StockDataFetcher を呼び出し）

3. **BulkDataService._fetch_multiple_stocks_batch()**
   - [app/services/bulk_data_service.py:346-531](app/services/bulk_data_service.py#L346-L531)
   - 複数銘柄のデータを順次取得（内部で fetch_single_stock を呼び出し）

**重複の詳細:**
- `StockDataFetcher.fetch_batch_stock_data()` は複数銘柄を順次取得しますが、バッチ管理機能がありません
- `BulkDataService._fetch_multiple_stocks_batch()` は同様の処理を行いますが、バッチ管理、進捗管理、エラーハンドリングが追加されています
- 実質的に `StockDataFetcher.fetch_batch_stock_data()` は使用されておらず、`BulkDataService` が使用されています

### 4.2 データ保存機能の重複

#### 問題点なし
`StockDataSaver` は単一責任原則に従い、データ保存のみを担当しています。重複機能は検出されませんでした。

### 4.3 ロギング機能の重複

#### 問題点
各サービスが独自に `StructuredLogger` のインスタンスを保持しています。

**重複箇所:**
- StockDataFetcher.logger
- StockDataSaver.logger
- StockDataOrchestrator.logger
- BulkDataService.logger
- BulkDataService.batch_logger
- JPXStockService.session (ロガーではなくDBセッション)
- BatchService（ロガーを直接インポート）
- StockDataScheduler.logger
- ErrorHandler.logger

**影響:**
- メモリ使用量の増加（微小）
- ロギング設定の一元管理が困難

**ただし:**
これは設計上の選択であり、各サービスが独立してログを管理することで柔軟性が向上しています。

### 4.4 データベースセッション管理の重複

#### 問題点
データベースセッションの管理方法が統一されていません。

**パターン1: 明示的なセッション管理**
- `JPXStockService` - `self.session` として保持

**パターン2: コンテキストマネージャー使用**
- `StockDataSaver` - `with get_db_session() as session:` を使用
- `BatchService` - `with get_db_session() as session:` を使用

**パターン3: セッションなし（ORM操作なし）**
- `StockDataFetcher` - 外部API呼び出しのみ
- `StockDataOrchestrator` - 他のサービスに委譲
- `BulkDataService` - 他のサービスに委譲
- `StockDataScheduler` - 他のサービスに委譲

**影響:**
- コード一貫性の欠如
- メンテナンス性の低下

**推奨:**
コンテキストマネージャーの使用を統一（現在の主流パターン）

## 5. 統合候補の提案

### 5.1 StockDataFetcher.fetch_batch_stock_data() の廃止

**理由:**
- `BulkDataService` に同等の機能が存在
- `BulkDataService` の方が高機能（バッチ管理、進捗管理、エラーハンドリング）
- 実際の使用例が確認できない

**統合手順:**
1. `StockDataFetcher.fetch_batch_stock_data()` の使用箇所を検索
2. 使用されていない場合、メソッドを削除
3. 使用されている場合、`BulkDataService.fetch_multiple_stocks()` に置き換え

**影響範囲:**
- [app/services/stock_data_fetcher.py:213-337](app/services/stock_data_fetcher.py#L213-L337)

### 5.2 データベースセッション管理の統一

**理由:**
- コード一貫性の向上
- メンテナンス性の向上
- リソースリークの防止

**統合手順:**
1. `JPXStockService` のセッション管理をコンテキストマネージャーに変更
2. 全サービスで `with get_db_session() as session:` パターンを使用

**影響範囲:**
- [app/services/jpx_stock_service.py:45-50](app/services/jpx_stock_service.py#L45-L50)

### 5.3 ロギング設定の一元管理（オプション）

**理由:**
- ロギング設定の一元管理
- メモリ使用量の削減（微小）

**統合手順:**
1. 各サービスのロガーインスタンスを削除
2. グローバルロガーインスタンスを使用
3. または、ロガーファクトリーパターンを導入

**影響範囲:**
- 全サービス

**注意:**
この変更は破壊的であり、各サービスの独立性を損なう可能性があるため、慎重に検討が必要です。

## 6. 不要なコードの特定

### 6.1 未使用メソッド

#### StockDataFetcher.fetch_batch_stock_data()
**ファイルパス:** [app/services/stock_data_fetcher.py:213-337](app/services/stock_data_fetcher.py#L213-L337)

**理由:**
- `BulkDataService` に同等の機能が存在
- 実際の使用例が確認できない

**推奨アクション:**
削除候補。ただし、削除前に全コードベースでの使用箇所を確認が必要。

### 6.2 不要なインポート

**確認方法:**
各サービスファイルのインポート文を確認し、実際に使用されていないライブラリを特定。

**影響:**
- コードの肥大化
- 可読性の低下

**推奨アクション:**
未使用インポートの削除（IDE の自動検出機能を使用）

### 6.3 重複したエラーハンドリングコード

**問題点:**
`BulkDataService` 内で `ErrorHandler` を使用しているが、一部のエラーハンドリングコードが重複しています。

**重複箇所:**
- [app/services/bulk_data_service.py:199-312](app/services/bulk_data_service.py#L199-L312) - fetch_single_stock()
- [app/services/bulk_data_service.py:346-531](app/services/bulk_data_service.py#L346-L531) - _fetch_multiple_stocks_batch()

**推奨アクション:**
エラーハンドリングロジックを `ErrorHandler` に完全に委譲し、重複コードを削除。

### 6.4 不要な変数

**ProgressTracker クラス内:**
[app/services/bulk_data_service.py:134-171](app/services/bulk_data_service.py#L134-L171)

一部のインスタンス変数が使用されていない可能性があります。

**推奨アクション:**
使用されていない変数を削除。

## 7. サービス間連携パターン

### 7.1 依存関係パターン

#### パターン1: 高レベルサービス → 低レベルサービス
```
StockDataOrchestrator
  └─> StockDataFetcher
  └─> StockDataSaver
```

このパターンは適切であり、変更不要。

#### パターン2: 並列サービス間の依存なし
```
BatchService (独立)
JPXStockService (独立)
ErrorHandler (独立)
```

各サービスが独立しており、疎結合を実現。

#### パターン3: スケジューラ → オーケストレータ
```
StockDataScheduler
  └─> StockDataOrchestrator
```

適切な分離であり、変更不要。

### 7.2 推奨される連携パターン

#### データ取得・保存フロー
```
API Layer
  └─> Orchestrator/BulkService (高レベル)
      └─> Fetcher (低レベル)
      └─> Saver (低レベル)
      └─> ErrorHandler (ユーティリティ)
      └─> BatchService (管理)
```

#### 定期実行フロー
```
Scheduler
  └─> Orchestrator
      └─> Fetcher
      └─> Saver
```

## 8. まとめ

### 8.1 サービスの責任範囲の明確性

各サービスは比較的明確な責任範囲を持っていますが、以下の改善点があります:

**良好な点:**
- ✓ 単一責任原則の遵守（ほぼ全サービス）
- ✓ 明確なレイヤー分離
- ✓ 疎結合な設計

**改善点:**
- StockDataFetcher.fetch_batch_stock_data() の削除
- データベースセッション管理の統一
- エラーハンドリングの完全な委譲

### 8.2 重複機能の統合提案サマリー

| 機能               | 統合前                                    | 統合後                       | 優先度 |
| ------------------ | ----------------------------------------- | ---------------------------- | ------ |
| 複数銘柄データ取得 | StockDataFetcher + BulkDataService        | BulkDataService のみ         | 高     |
| DBセッション管理   | 混在（明示的 + コンテキストマネージャー） | コンテキストマネージャー統一 | 中     |
| エラーハンドリング | 一部重複あり                              | ErrorHandler に完全委譲      | 中     |
| ロギング           | 各サービスで独立                          | 現状維持（または一元管理）   | 低     |

### 8.3 不要なコードのサマリー

| コード                   | ファイル              | 行番号   | 推奨アクション | 優先度 |
| ------------------------ | --------------------- | -------- | -------------- | ------ |
| fetch_batch_stock_data() | stock_data_fetcher.py | 213-337  | 削除           | 高     |
| 未使用インポート         | 全サービス            | -        | 削除           | 中     |
| 重複エラーハンドリング   | bulk_data_service.py  | 複数箇所 | 統一           | 中     |
| 不要な変数               | bulk_data_service.py  | 134-171  | 削除           | 低     |

### 8.4 次のステップ

1. **優先度：高**
   - [ ] `StockDataFetcher.fetch_batch_stock_data()` の使用箇所を確認
   - [ ] 使用されていない場合、削除を実施

2. **優先度：中**
   - [ ] データベースセッション管理をコンテキストマネージャーに統一
   - [ ] エラーハンドリングを `ErrorHandler` に完全委譲

3. **優先度：低**
   - [ ] 未使用インポートの削除
   - [ ] 不要な変数の削除

## 関連ドキュメント

- [アーキテクチャ概要](architecture_overview.md) - システム全体のアーキテクチャ
- [コンポーネント依存関係](component_dependency.md) - サービス間の依存関係
- [データフロー](data_flow.md) - データの流れと処理フロー
- [データベース設計](database_design.md) - データベーススキーマ詳細
- [API仕様書](../api/README.md) - API エンドポイント詳細
