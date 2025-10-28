# Stock Investment Analyzer API – OpenAPI 3.0.3

概要
- このドキュメントは `docs/api/openapi.yaml` をもとに、人が読みやすいMarkdown形式で要点をまとめたものです。
- バージョン: `1.0.0`
- APIバージョニング: 既定は `v1`（`/api/v1/...`）。一部非バージョンの互換エンドポイントあり。

サーバー
- `http://localhost:8000`（開発）
- `http://127.0.0.1:8000`（ローカル）

タグ
- `stock-data` 株価データ関連
- `bulk-data` バルクデータ処理
- `stock-master` 銘柄マスター管理
- `system` システム監視・ヘルスチェック

エンドポイント概要

stock-data
- `POST /api/stocks/data` 株価データの取得・保存（`symbol`, `period`, `interval` を指定）。
- `GET /api/stocks` 株価データの一覧取得（ページネーション、フィルタ、ソート対応）。
- `POST /api/stocks` 株価データの新規作成。
- `GET /api/stocks/{stock_id}` 特定データ取得。
- `PUT /api/stocks/{stock_id}` 特定データ更新。
- `DELETE /api/stocks/{stock_id}` 特定データ削除。
- `POST /api/stocks/test` テストデータの作成（開発・検証用）。

bulk-data（v1）
- `POST /api/v1/bulk-data/jobs` バルク取得ジョブ開始。
- `GET /api/v1/bulk-data/jobs/{job_id}` ジョブステータス確認。
- `POST /api/v1/bulk-data/jobs/{job_id}/stop` 実行中ジョブの停止。

stock-master（v1）
- `POST /api/v1/stock-master` 銘柄マスターの更新。
- `GET /api/v1/stock-master/stocks` 銘柄マスター一覧取得（ページネーション対応）。

system（v1）
- `GET /api/v1/system/database/connection` データベース接続テスト。
- `GET /api/v1/system/external-api/connection` 外部API接続テスト。
- `GET /api/v1/system/health-check` システムヘルスチェック。

非バージョン（互換）
- `GET /api/system/health-check` ヘルスチェック（互換用）。
- `GET /api/system/database/connection` DB接続テスト（互換用）。
- `GET /api/system/external-api/connection` 外部API接続テスト（互換用）。

主要スキーマ（抜粋）
- `FetchDataRequest` 入力: `symbol`（必須）, `period`, `interval`。
- `FetchDataResponse` 出力: 取得・保存結果、件数、期間、テーブル名等。
- `StockData` 株価データの標準レコード。
- `StockDataCreate` / `StockDataUpdate` 作成・更新用の入力。
- `PaginatedStockDataResponse` 一覧取得のページネーション付き応答。
- `JobResponse` / `JobStatusResponse` バルクジョブ開始・進捗の応答。
- `StockMasterListResponse` 銘柄マスター一覧の応答。
- `ConnectionTestResponse` 接続テスト結果。
- `HealthCheckResponse` ヘルスチェック結果（全体状態・各コンポーネント）。

共通レスポンス
- `SuccessResponse` 成功時の標準形式（`status=success`, `message`）。
- `ErrorResponse` 失敗時の標準形式（`status=error`, `message`, `error{code,message,details}`）。
- 事前定義: `BadRequest`, `NotFound`, `InternalServerError`, `BadGateway`。

セキュリティ
- `ApiKeyAuth` ヘッダー `X-API-Key`（将来拡張用）。

備考
- 詳細なフィールド定義と例は `docs/api/openapi.yaml` を参照してください。
- Swagger UI（`/api/docs/`）と ReDoc（`/api/docs/redoc/`）で仕様の可視化が可能です。
