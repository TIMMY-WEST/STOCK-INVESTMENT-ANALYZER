---
category: migration
ai_context: medium
last_updated: 2025-10-18
related_docs:
  - ../bulk-data-fetch.md
---

# Phase 1 から Phase 2 への移行ガイド

## 概要

このドキュメントは、全銘柄一括取得システムのPhase 1（MVP実装）からPhase 2（高度なバッチ処理エンジン）への移行について説明します。

## 実装内容

### Phase 1 (既存)
- **ジョブ管理**: インメモリ管理（JOBS辞書）
- **永続性**: アプリケーション再起動時にジョブ情報が失われる
- **API**: `/api/bulk/start`, `/api/bulk/status/<job_id>`, `/api/bulk/stop/<job_id>`
- **識別子**: job_id (例: "job-1720000000000")

### Phase 2 (新規)
- **ジョブ管理**: データベース永続化（batch_executions テーブル）
- **永続性**: アプリケーション再起動後もバッチ情報が保持される
- **API**: 既存APIと互換性を保ちながら、batch_db_idも返却
- **識別子**: batch_db_id (例: 1, 2, 3...)

## 主要な変更点

### 1. データベーステーブルの追加

**batch_executions テーブル**
```sql
CREATE TABLE batch_executions (
    id SERIAL PRIMARY KEY,
    batch_type VARCHAR(50) NOT NULL,
    status VARCHAR(20) NOT NULL,
    total_stocks INTEGER NOT NULL,
    processed_stocks INTEGER DEFAULT 0,
    successful_stocks INTEGER DEFAULT 0,
    failed_stocks INTEGER DEFAULT 0,
    start_time TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    end_time TIMESTAMP WITH TIME ZONE,
    error_message TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
```

**batch_execution_details テーブル**
```sql
CREATE TABLE batch_execution_details (
    id SERIAL PRIMARY KEY,
    batch_execution_id INTEGER NOT NULL,
    stock_code VARCHAR(10) NOT NULL,
    status VARCHAR(20) NOT NULL,
    start_time TIMESTAMP WITH TIME ZONE,
    end_time TIMESTAMP WITH TIME ZONE,
    error_message TEXT,
    records_inserted INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
```

### 2. 新規サービスクラス

**BatchService クラス** (`app/services/batch_service.py`)
- バッチ実行情報のCRUD操作を提供
- データベースとのやり取りを抽象化

主要メソッド:
- `create_batch()`: 新規バッチ作成
- `get_batch()`: バッチ情報取得
- `update_batch_progress()`: 進捗更新
- `complete_batch()`: バッチ完了
- `create_batch_detail()`: バッチ詳細作成
- `update_batch_detail()`: バッチ詳細更新

### 3. APIエンドポイントの拡張

**POST `/api/bulk/start`**

Phase 1のレスポンス:
```json
{
  "success": true,
  "job_id": "job-1720000000000",
  "status": "accepted"
}
```

Phase 2のレスポンス（下位互換性を保持）:
```json
{
  "success": true,
  "job_id": "job-1720000000000",
  "batch_db_id": 1,
  "status": "accepted"
}
```

**GET `/api/bulk/status/<job_id>`**

Phase 1とPhase 2の両方に対応:
- `job_id`が "job-" で始まる場合: Phase 1のインメモリ管理から取得
- `job_id`が数値の場合: Phase 2のデータベースから取得

## 移行手順

### ステップ1: データベースマイグレーション実行

```bash
python migrations/create_batch_execution_tables.py upgrade
```

### ステップ2: 環境変数設定（オプション）

Phase 2機能を無効化したい場合:
```bash
# .env ファイルに追加
ENABLE_PHASE2=false
```

デフォルトでは有効です（`ENABLE_PHASE2=true`）。

### ステップ3: アプリケーション再起動

```bash
# アプリケーションを再起動
python app/app.py
```

## 動作確認

### Phase 1互換性テスト

既存のクライアントコードが引き続き動作することを確認:

```bash
# ジョブ開始
curl -X POST http://localhost:8000/api/bulk/start \
  -H "Content-Type: application/json" \
  -H "X-API-KEY: your-api-key" \
  -d '{"symbols": ["7203.T", "6758.T"], "interval": "1d"}'

# レスポンス例
# {
#   "success": true,
#   "job_id": "job-1720000000000",
#   "batch_db_id": 1,  # Phase 2では追加
#   "status": "accepted"
# }

# ジョブステータス確認（Phase 1形式）
curl http://localhost:8000/api/bulk/status/job-1720000000000 \
  -H "X-API-KEY: your-api-key"

# ジョブステータス確認（Phase 2形式）
curl http://localhost:8000/api/bulk/status/1 \
  -H "X-API-KEY: your-api-key"
```

### Phase 2データベース確認

PostgreSQLでバッチ実行情報を確認:

```sql
-- バッチ実行情報一覧
SELECT * FROM batch_executions ORDER BY start_time DESC LIMIT 10;

-- バッチ実行詳細（特定のバッチ）
SELECT * FROM batch_execution_details WHERE batch_execution_id = 1;
```

## 下位互換性

Phase 2実装では、既存のPhase 1クライアントコードとの完全な下位互換性を保持しています:

1. **Phase 1のjob_idは引き続き使用可能**: "job-XXXX" 形式のIDでステータス取得可能
2. **Phase 1のレスポンス形式を維持**: 既存のクライアントは変更不要
3. **Phase 2の追加情報はオプション**: batch_db_idは追加情報として返却されるが、無視しても動作に影響なし

## トラブルシューティング

### Phase 2機能が動作しない

**原因**: データベーステーブルが作成されていない

**対処**:
```bash
python migrations/create_batch_execution_tables.py upgrade
```

### バッチ情報がデータベースに保存されない

**原因**: `ENABLE_PHASE2`環境変数がfalseに設定されている

**対処**:
```bash
# .envファイルを確認
cat .env | grep ENABLE_PHASE2

# 必要に応じて修正
echo "ENABLE_PHASE2=true" >> .env
```

### アプリケーション起動時のエラー

**原因**: BatchServiceのインポートエラー

**対処**:
```bash
# app/services/batch_service.py が存在することを確認
ls -la app/services/batch_service.py

# Pythonパスを確認
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
```

## 今後の拡張予定

Phase 2実装後、以下の機能追加が予定されています:

### Phase 2.1: 高度なバッチ管理
- バッチ一時停止/再開機能
- バッチキャンセル機能の強化
- バッチ実行履歴の検索・フィルタリング

### Phase 2.2: 監視・通知機能
- バッチ実行メトリクスの収集・可視化
- 異常検知とアラート機能
- 完了/エラー時のSlack/メール通知

### Phase 3: スケーラビリティ
- 分散処理対応
- キュー（RQ/Celery）導入
- ロードバランシング

## 参考資料

- [全銘柄一括取得システム仕様書](./api_bulk_fetch.md)
- [データベース設計](./database_design.md)
- [Issue #85: Phase 1からPhase 2への移行実装](https://github.com/TIMMY-WEST/STOCK-INVESTMENT-ANALYZER/issues/85)

## まとめ

Phase 1からPhase 2への移行により、以下のメリットが得られます:

✅ **永続化**: アプリケーション再起動後もバッチ情報が保持される
✅ **下位互換性**: 既存のクライアントコードは変更不要
✅ **拡張性**: 今後の機能追加がしやすい設計
✅ **監視性**: データベースクエリでバッチ実行履歴を分析可能

移行は段階的に行われ、Phase 1とPhase 2が共存する形で実装されているため、リスクを最小限に抑えながら新機能を導入できます。
