---
category: monitoring
ai_context: medium
last_updated: 2025-10-19
related_docs:
  - architecture/database_design.md
  - bulk-data-fetch.md
  - jpx-sequential-fetch.md
implementation_status: ✅ 実装完了
---

# システム監視・ログ機能完全ガイド

## 📋 目次

- [概要](#概要)
- [構造化ログ](#構造化ログ)
- [メトリクス収集](#メトリクス収集)
- [システム監視機能](#システム監視機能)
- [使用例](#使用例)
- [トラブルシューティング](#トラブルシューティング)
- [運用考慮事項](#運用考慮事項)

## 概要

株価データ取得システムのバッチ処理監視・ログ機能、およびシステム状態の可視化と接続テスト機能について説明します。

### 主要機能

- **構造化ログ**: JSON形式での詳細なバッチ処理ログ
- **メトリクス収集**: パフォーマンス指標のリアルタイム計測
- **システム状態監視**: データベース・API接続の可視化 ✅ **実装完了**
- **接続テスト**: ワンクリックでの接続確認機能 ✅ **実装完了**

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

### ログローテーション

ログファイルは自動的にローテーションされます。

#### 設定

- **最大ファイルサイズ**: 10MB
- **バックアップファイル数**: 10個
- **ログディレクトリ**: `logs/`
- **ログファイル名**: `batch_bulk.log`

#### ローテーション動作

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

### 完了予定時刻（ETA）

#### 計算方法

ETAは以下の方法で計算されます:

1. **経過時間の計算**: 開始時刻から現在までの経過時間
2. **処理速度の計算**: `処理済み数 / 経過時間`
3. **残り時間の推定**: `残り数 / 処理速度`
4. **ETAの算出**: `現在時刻 + 残り時間`

#### 精度向上のポイント

- 処理が進むほど精度が向上します
- 最初の数件ではETAが大きくぶれる可能性があります
- 10件以上処理した後のETAが比較的正確です

## システム監視機能

### 設計理念

- **リアルタイム可視化**: システム状態を即座に把握可能
- **シンプルな操作**: ワンクリックでの接続テスト実行
- **直感的な表示**: 色分けによる状態の視覚的理解
- **運用効率化**: 問題の早期発見と対応支援

### 監視対象

| 監視項目 | 重要度 | 説明 |
|----------|--------|------|
| **データベース接続** | 高 | PostgreSQL接続状態 |
| **Yahoo Finance API** | 高 | 外部API接続状態 |
| **システム稼働状況** | 中 | 全体的なシステム健全性 |
| **メモリ使用量** | 低 | アプリケーションリソース監視（将来実装） |
| **ディスク容量** | 低 | ストレージ監視（将来実装） |

### 状態レベル定義

```javascript
const StatusLevel = {
  HEALTHY: {
    level: 'healthy',
    color: '#10b981',
    backgroundColor: '#dcfce7',
    label: '正常',
    icon: '✅'
  },
  WARNING: {
    level: 'warning',
    color: '#f59e0b',
    backgroundColor: '#fef3c7',
    label: '警告',
    icon: '⚠️'
  },
  ERROR: {
    level: 'error',
    color: '#ef4444',
    backgroundColor: '#fee2e2',
    label: 'エラー',
    icon: '❌'
  },
  UNKNOWN: {
    level: 'unknown',
    color: '#6b7280',
    backgroundColor: '#f3f4f6',
    label: '確認中',
    icon: '❓'
  }
};
```

### 接続テスト機能

#### データベーステスト項目

- **接続確認**: PostgreSQL接続の成功/失敗
- **応答時間**: 接続確立までの時間
- **接続数**: 現在のアクティブ接続数
- **テーブル存在確認**: `stocks_1d`テーブルの存在確認

#### APIテスト項目

- **外部API接続**: Yahoo Finance APIへのアクセス確認
- **データ取得**: サンプル銘柄（7203.T）のデータ取得
- **応答時間**: API応答時間の測定
- **データ形式**: 返却データの形式確認

### API仕様

#### データベース接続テスト

```http
POST /api/system/db-connection-test
Content-Type: application/json
```

**レスポンス例:**
```json
{
  "success": true,
  "message": "データベース接続正常",
  "responseTime": 45.23,
  "details": {
    "host": "localhost",
    "database": "stock_db",
    "tableExists": true,
    "connectionCount": 3
  },
  "timestamp": "2024-01-15T10:30:00Z"
}
```

#### API接続テスト

```http
POST /api/system/api-connection-test
Content-Type: application/json

{
  "symbol": "7203.T"
}
```

**レスポンス例:**
```json
{
  "success": true,
  "message": "Yahoo Finance API接続正常",
  "responseTime": 1250.45,
  "details": {
    "symbol": "7203.T",
    "dataPoints": 20,
    "lastUpdate": "2024-01-15",
    "companyName": "Toyota Motor Corporation"
  },
  "timestamp": "2024-01-15T10:30:00Z"
}
```

#### 統合ヘルスチェック

```http
GET /api/system/health-check
```

**レスポンス例:**
```json
{
  "overall": "healthy",
  "timestamp": "2024-01-15T10:30:00Z",
  "services": {
    "database": {
      "status": "healthy",
      "message": "接続正常"
    },
    "api": {
      "status": "healthy",
      "message": "API接続正常"
    }
  }
}
```

### リアルタイム監視

#### 自動監視機能

```javascript
const AutoMonitor = {
  interval: 300000, // 5分間隔
  isRunning: false,

  start: function() {
    if (this.isRunning) return;

    this.isRunning = true;
    this.intervalId = setInterval(() => {
      this.runHealthCheck();
    }, this.interval);

    // 初回実行
    this.runHealthCheck();
  },

  stop: function() {
    if (this.intervalId) {
      clearInterval(this.intervalId);
      this.intervalId = null;
    }
    this.isRunning = false;
  }
};
```

## 使用例

### Pythonでの構造化ログ使用

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

### WebUI統合

#### システム状態セクション

WebUIの「システム状態」セクションには、「システム状態の確認」ボタンがあり、ワンクリックで以下の3つのテストを順次実行します：

1. **データベース接続テスト** (`POST /api/system/db-connection-test`)
2. **Yahoo Finance API接続テスト** (`POST /api/system/api-connection-test`)
3. **統合ヘルスチェック** (`GET /api/system/health-check`)

#### 実装例

```javascript
// SystemStatusManager - WebUIシステム監視マネージャー
const SystemStatusManager = {
  init: () => {
    const checkBtn = document.getElementById('system-check-btn');
    if (checkBtn) {
      checkBtn.addEventListener('click', SystemStatusManager.runSystemCheck);
    }
  },

  runSystemCheck: async () => {
    const btn = document.getElementById('system-check-btn');
    const resultsContainer = document.getElementById('monitoring-results');

    try {
      btn.disabled = true;
      btn.textContent = 'チェック実行中...';
      resultsContainer.style.display = 'block';

      // 3つのテストを順次実行
      await SystemStatusManager.runDatabaseTest();
      await SystemStatusManager.runApiTest();
      await SystemStatusManager.runHealthCheck();

    } finally {
      btn.disabled = false;
      btn.textContent = 'システム状態の確認';
    }
  },

  runDatabaseTest: async () => {
    const response = await fetch('/api/system/db-connection-test', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' }
    });
    const data = await response.json();
    // 結果を表示
  },

  runApiTest: async () => {
    const response = await fetch('/api/system/api-connection-test', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' }
    });
    const data = await response.json();
    // 結果を表示
  },

  runHealthCheck: async () => {
    const response = await fetch('/api/system/health-check');
    const data = await response.json();
    // 総合ステータスを表示
  }
};

// ページ読み込み時に初期化
document.addEventListener('DOMContentLoaded', function() {
  window.systemMonitor = new SystemMonitor();
});
```

## トラブルシューティング

### ログが出力されない

**原因:**
- `logs/` ディレクトリが存在しない
- 書き込み権限がない
- `setup_structured_logging()` が呼ばれていない

**解決方法:**
1. `logs/` ディレクトリの存在確認と作成
2. ディレクトリの書き込み権限確認
3. ロガー初期化コードの確認

### メトリクスが正しく表示されない

**原因:**
- `tracker.update()` に必要なパラメータが渡されていない
- `duration_ms`, `records_fetched`, `records_saved` が正しく設定されていない

**解決方法:**
1. メトリクス更新コードのパラメータ確認
2. 計測タイミングの見直し
3. ログ出力での値確認

### ETAが表示されない

**原因:**
- 処理が開始されていない
- `stocks_per_second` が0（処理が進んでいない）

**解決方法:**
1. バッチ処理の開始確認
2. 処理速度の計算ロジック確認
3. 十分な件数（10件以上）の処理完了待機

### 接続テストが失敗する

**データベース接続エラーの場合:**
- PostgreSQL サーバーの起動確認
- 接続情報（ホスト、ポート、認証情報）の確認
- ネットワーク接続の確認

**API接続エラーの場合:**
- インターネット接続の確認
- Yahoo Finance API のステータス確認
- プロキシ設定の確認

### システム状態表示が更新されない

**原因:**
- JavaScript エラーの発生
- ネットワークエラー
- API レスポンスの遅延

**解決方法:**
1. ブラウザの開発者ツールでエラー確認
2. ネットワークタブでAPI通信確認
3. 手動更新ボタンの再実行

## 運用考慮事項

### 監視間隔

- **自動監視**: 5分間隔（設定可能）
- **手動更新**: ユーザー操作によるリアルタイム確認
- **初期読み込み**: ページアクセス時の即座確認

### アラート設定（将来実装予定）

- **エラー状態継続時**: 3回連続エラーでアラート
- **応答時間劣化**: 平均応答時間の2倍を超えた場合
- **サービス復旧**: エラー状態からの復旧通知

### ログ管理（将来実装予定）

- **接続テスト履歴**: 過去24時間の接続テスト結果
- **エラーログ**: 詳細なエラー情報の記録
- **パフォーマンスログ**: 応答時間の推移記録

### テスト項目

#### 接続テスト
- [ ] PostgreSQL接続確認
- [ ] 接続応答時間測定
- [ ] テーブル存在確認（stocks_1d）
- [ ] アクティブ接続数取得
- [ ] Yahoo Finance API接続確認
- [ ] テスト銘柄（7203.T）データ取得
- [ ] API応答時間測定

#### UI動作テスト
- [ ] システム状態の正確な表示
- [ ] ステータスインジケータの色分け
- [ ] 手動更新ボタンの動作
- [ ] 自動監視機能の開始/停止
- [ ] 詳細情報の表示/非表示切り替え

#### レスポンシブテスト
- [ ] モバイル表示での適切なレイアウト
- [ ] タブレット表示での操作性確認
- [ ] デスクトップ表示での情報表示

## 参考

- [一括データ取得ガイド](bulk-data-fetch.md) - バッチ処理の詳細仕様
- [JPX全銘柄取得ガイド](jpx-sequential-fetch.md) - JPX統合システムの監視
- [データベース設計書](architecture/database_design.md) - DB接続の詳細
