# 既存テストドキュメント

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
├── README.md                           # テスト実行ガイド
├── conftest.py                         # pytest設定とフィクスチャ
├── test_app.py                         # メインアプリケーションテスト
├── test_models.py                      # データモデルテスト
├── api/                                # API関連テスト
│   └── test_bulk_api.py               # 一括データ取得APIテスト
├── docs/                               # ドキュメント関連テスト
├── e2e/                                # エンドツーエンドテスト
├── integration/                        # 統合テスト
└── unit/                               # ユニットテスト
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

#### `test_stock_master_api.py`
- **目的：** 株式マスターAPIテスト
- **カバレッジ：** 70%
- **未カバー領域：** 330-387, 399-441, 445行

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

### 4. エラーハンドリングテスト

#### `test_error_handler.py`
- **目的：** エラーハンドリング機能のテスト
- **カバレッジ：** 100%

#### `test_error_handling.py`
- **目的：** アプリケーション全体のエラー処理テスト
- **カバレッジ：** 96%

### 5. フロントエンド関連テスト

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
