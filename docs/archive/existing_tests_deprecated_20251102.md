# ⚠️ 非推奨: このドキュメントは統合されました

**このドキュメントは 2025年11月2日 に非推奨となりました。**

代わりに以下の統合ドキュメントを参照してください:
- **[テスト標準仕様書 (v3.0.0)](../standards/testing-standards.md)** ← 現在のテスト状況と戦略

最新のテスト実行結果は統合ドキュメントの「現在のカバレッジ状況」セクションに記載されています。

---

# 既存テストドキュメント (ARCHIVED)

## 概要

このドキュメントは、STOCK-INVESTMENT-ANALYZERプロジェクトの既存テストスイートの詳細な分析と記録を提供します。

## テスト実行結果サマリー

### 最新実行結果（2025-10-25）
- **総テスト数：** 377件
- **成功：** 353件 (93.7%)
- **スキップ：** 24件 (6.4%)
- **失敗：** 0件
- **警告：** 2件
- **実行時間：** 118秒（約2分）

### テストカバレッジ
- **総合カバレッジ：** 81%
- **総行数：** 6,428行
- **未カバー行数：** 1,201行

## テストディレクトリ構造

```
tests/
├── api/
│   ├── test_app.py
│   ├── test_bulk_api.py
│   ├── test_restful_endpoints.py
│   ├── test_stock_master_api.py
│   ├── test_swagger_api.py
│   └── test_system_monitoring_api.py
├── unit/
│   ├── test_data_fetcher.py
│   ├── test_stock_analyzer.py
│   └── test_timeframe_selector_ui.py
├── integration/
│   ├── test_api_versioning.py
│   ├── test_bulk_data_api_integration.py
│   ├── test_fixtures.py
│   ├── test_reset_db.py
│   ├── test_setup_scripts.py
│   ├── test_state_integration.html
│   ├── test_stock_data_api_integration.py
│   ├── test_stock_master_system_api_integration.py
│   ├── test_stocks_daily_removal.py
│   └── test_swagger_integration.py
├── conftest.py
├── pytest.ini
└── test_error_handler.py
```

## 主要テストファイル詳細

### 1. アプリケーション基盤テスト

#### `test_app.py`
- **目的：** メインアプリケーションの基本機能テスト
- **主要テストケース：**
  - `test_index_route` - ルートエンドポイントのテスト
  - `test_fetch_data_api_structure` - データ取得APIの構造テスト
  - `test_fetch_data_api_max_period_structure` - 最大期間データ取得テスト
  - `test_fetch_data_api_max_period_parameter_validation` - パラメータ検証テスト

#### `test_models.py`
- **目的：** データベースモデルの検証
- **カバレッジ：** 100%

### 2. API関連テスト

#### `api/test_bulk_api.py`
- **目的：** 一括データ取得APIの機能テスト
- **主要テストケース：**
  - `test_rate_limit_exceeded` - レート制限テスト
  - `test_status_not_found` - 404エラーハンドリング
  - `test_status_running_after_start` - 実行状態管理テスト
- **カバレッジ：** 100%

#### `api/test_stock_master_api.py`
- **目的：** JPX銘柄マスタAPIのテスト
- **主要テストケース：**
  - `test_update_stock_master_success` - 銘柄マスタ更新成功テスト
  - `test_update_stock_master_scheduled` - スケジュール実行テスト
- **カバレッジ：** 70%
- **未カバー領域：** 330-387, 399-441, 445行

#### `api/test_system_monitoring_api.py`
- **目的：** システム監視APIのテスト
- **主要テストケース：**
  - `test_db_connection_success` - データベース接続成功テスト
  - `test_db_connection_failure` - データベース接続失敗テスト
  - `test_api_connection_success` - Yahoo Finance API接続テスト

#### `api/test_swagger_api.py`
- **目的：** Swagger UIとOpenAPI仕様書の提供機能テスト
- **主要テストケース：**
  - `test_swagger_ui_page` - Swagger UIページ表示テスト
  - `test_openapi_json_endpoint` - OpenAPI JSON仕様書テスト
  - `test_openapi_yaml_endpoint` - OpenAPI YAML仕様書テスト
  - `test_redoc_page` - ReDoc表示テスト
  - `test_docs_health_endpoint` - ドキュメントヘルスチェック

#### `api/test_app.py`
- **目的：** メインアプリケーションAPIの基本機能テスト
- **主要テストケース：**
  - `test_index_route_with_get_request_returns_success_response` - トップページテスト
  - `test_fetch_data_api_with_basic_request_returns_valid_structure` - 基本API構造テスト
  - `test_fetch_data_api_with_max_period_returns_valid_structure` - 最大期間データ取得テスト
  - `test_fetch_data_api_with_max_period_parameter_passes_validation` - パラメータ検証テスト

#### `api/test_restful_endpoints.py`
- **目的：** RESTful APIエンドポイントのテスト
- **主要テストケース：**
  - `test_get_stocks_endpoint_returns_valid_response` - 株式一覧取得テスト
  - `test_post_stocks_endpoint_creates_new_stock` - 新規株式作成テスト
  - `test_put_stocks_endpoint_updates_existing_stock` - 株式情報更新テスト
  - `test_delete_stocks_endpoint_removes_stock` - 株式削除テスト

### 3. サービス層テスト

#### `test_bulk_data_service.py`
- **目的：** 一括データサービスのテスト
- **カバレッジ：** 97%
- **未カバー領域：** 114-115, 120-121行

#### `test_stock_data_services.py`
- **目的：** 株価データサービステスト
- **カバレッジ：** 100%

#### `test_jpx_stock_service.py`
- **目的：** JPX株式サービステスト
- **カバレッジ：** 99%

### 4. ユニットテスト

#### `unit/test_data_fetcher.py`
- **目的：** データ取得機能のユニットテスト
- **カバレッジ：** 85%
- **未カバー領域：** 45-52, 78-85行

#### `unit/test_stock_analyzer.py`
- **目的：** 株式分析機能のユニットテスト
- **カバレッジ：** 90%

#### `unit/test_timeframe_selector_ui.py`
- **目的：** 時間軸選択UIコンポーネントのユニットテスト
- **主要テストケース：**
  - `test_html_template_structure_with_valid_template_returns_valid_structure` - HTMLテンプレート構造確認
  - `test_css_styles_exist_with_valid_css_returns_required_styles` - CSSスタイル存在確認
  - `test_javascript_functions_exist_with_valid_js_returns_required_functions` - JavaScript関数存在確認
- **テスト対象：** HTML構造、CSSスタイル、JavaScript構文の基本機能

### 5. エラーハンドリングテスト

#### `test_error_handler.py`
- **目的：** エラーハンドリング機能のテスト
- **カバレッジ：** 96%

### 6. 統合・E2Eテスト

#### `integration/test_api_versioning.py`
- **目的：** APIバージョニング機能の統合テスト
- **主要テストケース：**
  - `test_backward_compatibility_bulk_api` - バルクAPI後方互換性テスト
  - `test_backward_compatibility_stock_master_api` - 株式マスターAPI後方互換性テスト
  - `test_backward_compatibility_system_api` - システムAPI後方互換性テスト
  - `test_version_parsing_in_request` - リクエスト内バージョン解析テスト
  - `test_default_version_for_non_versioned_request` - 非バージョン指定リクエストのデフォルト処理テスト

#### `integration/test_fixtures.py`
- **目的：** テストフィクスチャの統合テスト
- **主要テストケース：**
  - `test_mock_db_session_basic` - モックデータベースセッション基本テスト
  - `test_test_db_session_context` - テストデータベースセッションコンテキストテスト
  - `test_sample_stock_data_structure` - サンプル株式データ構造テスト
  - `test_sample_dataframe_structure` - サンプルデータフレーム構造テスト
- **テスト対象：** `conftest.py`で定義された共通フィクスチャの動作検証

#### `integration/test_stock_data_api_integration.py`
- **目的：** 株価データAPI統合テスト
- **主要テストケース：**
  - `test_fetch_stock_data_with_valid_symbol_returns_success_response` - 有効銘柄コードでの株価データ取得テスト
  - `test_fetch_stock_data_with_invalid_symbol_raises_exception` - 無効銘柄コードでの例外発生テスト
  - `test_fetch_stock_data_with_network_error_raises_exception` - ネットワークエラー時の例外発生テスト
- **テスト対象：** `StockDataFetcher`クラスの基本機能とエラーハンドリング

#### `integration/test_bulk_data_api_integration.py`
- **目的：** バルクデータ処理API統合テスト
- **主要テストケース：**
  - `test_create_bulk_job_success` - バルクジョブ作成成功テスト
  - `test_create_bulk_job_missing_params` - 必須パラメータ不足テスト
  - `test_create_bulk_job_unauthorized` - 認証エラーテスト
  - `test_create_bulk_job_invalid_api_key` - 無効APIキーテスト
- **テスト対象：** バルクデータ処理関連APIエンドポイント

#### `integration/test_swagger_integration.py`
- **目的：** Swagger UIとOpenAPI仕様書の統合テスト
- **主要テストケース：**
  - `test_swagger_ui_integration_with_main_app` - メインアプリケーションとのSwagger UI統合テスト
  - `test_openapi_spec_reflects_actual_endpoints` - OpenAPI仕様書の実際エンドポイント反映テスト
  - `test_openapi_spec_server_urls_dynamic_setting` - OpenAPI仕様書サーバーURL動的設定テスト
  - `test_swagger_ui_with_different_environments` - 異なる環境でのSwagger UI動作テスト

#### `integration/test_state_integration.html`
- **目的：** 状態管理システムの統合テスト用HTMLファイル
- **テスト要素：**
  - ページネーション機能
  - ソート機能
  - データ状態更新ボタンと表示領域
  - テスト結果表示用要素

#### その他の統合テストファイル
- `test_reset_db.py` - データベースリセット機能テスト
- `test_setup_scripts.py` - セットアップスクリプトテスト
- `test_stock_master_system_api_integration.py` - 株式マスターシステムAPI統合テスト
- `test_stocks_daily_removal.py` - 日次株式データ削除機能テスト

### 7. フロントエンド関連テスト

#### `test_frontend_e2e.py`
- **目的：** フロントエンドのE2Eテスト
- **カバレッジ：** 84%

#### `test_frontend_error_display.py`
- **目的：** フロントエンドエラー表示テスト
- **カバレッジ：** 100%

### 6. ドキュメント品質テスト

#### `test_docs_quality.py`
- **目的：** ドキュメントの品質検証
- **カバレッジ：** 97%

#### `test_docs_structure.py`
- **目的：** ドキュメント構造の検証
- **カバレッジ：** 95%

#### `test_docs_readme_content.py`
- **目的：** READMEコンテンツの検証
- **カバレッジ：** 98%

## カバレッジ詳細分析

### 高カバレッジ（90%以上）
- `app/utils/structured_logger.py` - 100%
- `app/services/error_handler.py` - 93%
- `app/api/system_monitoring.py` - 91%
- `tests/` 配下の多数のテストファイル - 90%以上

### 中カバレッジ（70-89%）
- `app/services/bulk_data_service.py` - 88%
- `app/services/jpx_stock_service.py` - 85%
- `app/models.py` - 76%
- `app/services/stock_data_fetcher.py` - 74%
- `app/app.py` - 73%
- `app/api/stock_master.py` - 72%
- `app/services/stock_data_saver.py` - 72%

### 低カバレッジ（70%未満）
- `app/services/stock_data_orchestrator.py` - 55%
- `app/api/bulk_data.py` - 49%
- `app/services/batch_service.py` - 32%
- `app/services/stock_data_scheduler.py` - 0%

## テストフィクスチャ

### 利用可能なフィクスチャ（conftest.py）
- `app` - Flaskアプリケーションインスタンス
- `client` - テストクライアント
- `mock_db_session` - モックデータベースセッション
- `test_db_session` - テスト用データベースセッション
- `sample_stock_data` - サンプル株価データ
- `sample_stock_list` - サンプル株式リスト
- `sample_dataframe` - サンプルDataFrame
- `mock_yfinance_ticker` - Yahoo Finance Tickerモック
- `mock_yfinance_download` - Yahoo Finance downloadモック

## テスト実行方法

### 全テスト実行
```bash
pytest tests/ -v
```

### カバレッジ付き実行
```bash
pytest tests/ --cov=. --cov-report=term-missing --cov-report=html
```

### 特定レベルのテスト実行
```bash
# ユニットテスト
pytest tests/unit/ -v

# 統合テスト
pytest tests/integration/ -v

# E2Eテスト
pytest tests/e2e/ -v
```

### マーカー別実行
```bash
# 高速テストのみ
pytest -m "not slow" -v

# 外部依存なしテスト
pytest -m "not external" -v
```

## モジュールレベルマーカーについて

このリポジトリでは、テストファイル単位でのマーカー指定（モジュールレベルの `pytestmark`）を順次導入しています。
これにより同一ファイル内の全テストをまとめて選択・除外できます。主に次のマーカーを標準化しています:

- `unit` — ユニットテスト
- `integration` — 統合テスト
- `e2e` — E2Eテスト
- `slow` — 実行時間の長いテスト
- `docs` — ドキュメント品質チェック用テスト（`tests/docs/`）

注意: 新しく追加した `docs` マーカーなどは `pytest.ini` の `markers` セクションに登録済みです。
そのため `--strict-markers` を有効にしていても収集エラーになりません。

例: docs テストのみを実行する

```bash
pytest -m docs
```

## 改善が必要な領域

### 1. カバレッジ向上が必要
- `app/services/stock_data_scheduler.py` (0%)
- `app/services/batch_service.py` (32%)
- `app/api/bulk_data.py` (49%)

### 2. テスト安定性
- Yahoo Finance APIに依存するテストの安定化
- 外部依存を持つテストのモック化強化

### 3. パフォーマンステスト
- 大量データ処理のパフォーマンステスト追加
- メモリ使用量テストの追加

## 警告とエラー

### 現在の警告
1. **FutureWarning:** `YF.download()` の `auto_adjust` デフォルト値変更
   - 影響ファイル: `app/services/stock_data_fetcher.py:264`
   - 対応: yfinanceライブラリの新しいデフォルト値に対応

### 一般的なテスト実行時の注意点
- USBデバイス関連のエラーメッセージは無視可能
- TensorFlow Liteのメッセージは無視可能
- データベース初期化エラーは環境設定を確認

## 継続的改善

### 推奨事項
1. **定期的なカバレッジ監視**
   - 新機能追加時のカバレッジ維持
   - 月次カバレッジレポートの作成

2. **テストデータ管理**
   - テストデータの定期更新
   - モックデータの充実

3. **CI/CD統合**
   - GitHub Actionsでの自動テスト実行
   - プルリクエスト時のカバレッジチェック

## 参考資料

- [pytest公式ドキュメント](https://docs.pytest.org/)
- [pytest-cov](https://pytest-cov.readthedocs.io/)
- [プロジェクトのテスト実行ガイド](../tests/README.md)

---

**最終更新日:** 2025-10-25
**作成者:** Issue #162対応
**次回更新予定:** 新機能追加時またはテスト構造変更時
