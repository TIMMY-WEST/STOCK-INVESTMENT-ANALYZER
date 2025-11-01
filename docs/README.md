# 株価データ取得システム - 開発者向けドキュメント

## 📋 概要

このプロジェクトは、Yahoo Finance（yfinance）から日本企業の株価データを取得し、PostgreSQLデータベースに格納するWebアプリケーションです。

**設計理念**: 動作優先・シンプル設計・後から拡張

## 📁 ドキュメント構成

ドキュメントはカテゴリー別に整理されています。各カテゴリーは以下の通りです。

### 🚀 機能別統合ドキュメント

主要機能の完全ガイド（API仕様・設計・実装・運用を統合）

| ドキュメント | 説明 | AI優先度 |
|------------|------|---------|
| [全銘柄一括取得システム](bulk-data-fetch.md) | バルクデータ取得の完全ガイド | **高** |
| [JPX全銘柄順次取得システム](jpx-sequential-fetch.md) | JPX8種類時間軸自動取得の完全ガイド | **高** |
| [システム監視・ログ機能](monitoring-guide.md) | 監視・ログ・メトリクス・接続テストの完全ガイド | 中 |

### 🏗️ アーキテクチャ・設計 (`architecture/`)

システム全体の設計方針とアーキテクチャ関連のドキュメント

| ドキュメント | 説明 | AI優先度 |
|------------|------|---------|
| [プロジェクトアーキテクチャ](architecture/project_architecture.md) | プロジェクト全体の構成・技術スタック・ディレクトリ構成 | **高** |
| [データベース設計](architecture/database_design.md) | テーブル設計・SQLAlchemyモデル・インデックス | **高** |
| [フロントエンド設計](architecture/frontend_design.md) | UI/UX設計・HTML/CSS/JavaScript実装 | 中 |

### 🔌 API仕様 (`api/`)

APIエンドポイントとインターフェース仕様

| ドキュメント | 説明 | AI優先度 |
|------------|------|---------|
| [API仕様書](api/api_specification.md) | 全APIエンドポイント・リクエスト/レスポンス形式 | **高** |

### 📖 運用・利用ガイド (`guides/`)

セットアップ、運用、パフォーマンス最適化のガイド

| ドキュメント | 説明 | AI優先度 |
|------------|------|---------|
| [セットアップガイド](guides/setup_guide.md) | 開発環境構築・初回セットアップ | **高** |
| [データベースセットアップ](guides/DATABASE_SETUP.md) | PostgreSQL環境構築・接続設定 | **高** |
| [パフォーマンス最適化ガイド](guides/performance_optimization_guide.md) | パフォーマンス改善手法 | 低 |
| [バックアップ手順](guides/backup_procedures.md) | データバックアップ・リストア | 低 |

### 🔧 開発関連 (`development/`)

開発プロセス、テスト戦略、統合仕様

| ドキュメント | 説明 | AI優先度 |
|------------|------|---------|
| [GitHub運用ワークフロー](development/github_workflow.md) | Issue管理・ブランチ戦略・PR作成 | **高** |
| [テスト戦略](development/testing_strategy.md) | テスト方針・テストケース | 中 |


### 🔄 マイグレーション (`migration/`)

バージョン移行手順

| ドキュメント | 説明 | AI優先度 |
|------------|------|---------|
| [Phase1→Phase2移行](migration/phase1_to_phase2_migration.md) | フェーズ間移行手順 | 中 |

### 📝 実装レポート (`implementation/`)

実装完了時のレポート

| ドキュメント | 説明 |
|------------|------|
| [Issue-79実装レポート](implementation/issue-79-implementation-report.md) | Issue #79実装完了レポート |

### 📋 タスク管理 (`tasks/`)

進行中のタスクとマイルストーン

| ドキュメント | 説明 |
|------------|------|
| [Issues一覧](tasks/issues.md) | 現在のIssue一覧 |
| [Milestones](tasks/milestones.md) | マイルストーン管理 |

### 🗄️ 旧バージョン (`old/`)

過去バージョンのドキュメントアーカイブ

---

## 🤖 AI開発者向けガイド

### タスク別推奨参照順序

#### 🏁 初期セットアップ時
1. [architecture/project_architecture.md](architecture/project_architecture.md) - 全体像把握
2. [guides/setup_guide.md](guides/setup_guide.md) - 環境構築
3. [guides/DATABASE_SETUP.md](guides/DATABASE_SETUP.md) - PostgreSQLセットアップ
4. [development/github_workflow.md](development/github_workflow.md) - 開発フロー確認

#### 🛠️ バックエンド開発時
1. [api/api_specification.md](api/api_specification.md) - APIエンドポイント実装
2. [architecture/database_design.md](architecture/database_design.md) - データベースモデル実装
3. [guides/DATABASE_SETUP.md](guides/DATABASE_SETUP.md) - データベース接続・セットアップ
4. [architecture/project_architecture.md](architecture/project_architecture.md) - 技術スタック確認

#### 🎨 フロントエンド開発時
1. [architecture/frontend_design.md](architecture/frontend_design.md) - UI/UX設計確認
2. [api/api_specification.md](api/api_specification.md) - API連携仕様
3. [architecture/project_architecture.md](architecture/project_architecture.md) - フロントエンド技術確認

#### 🚀 リリース・デプロイ時
1. [development/github_workflow.md](development/github_workflow.md) - CI/CD・デプロイフロー
2. [guides/setup_guide.md](guides/setup_guide.md) - 本番環境セットアップ
3. [guides/DATABASE_SETUP.md](guides/DATABASE_SETUP.md) - 本番環境データベースセットアップ

### 開発優先度別機能マップ

#### 🔴 優先度: 高（MVP必須）
- **API実装**: [api/api_specification.md](api/api_specification.md) の「優先度: 高」セクション
- **DB実装**: [architecture/database_design.md](architecture/database_design.md) の「優先度: 高」セクション
- **UI実装**: [architecture/frontend_design.md](architecture/frontend_design.md) の「優先度: 高」セクション

#### 🟡 優先度: 中（動作確認後）
- **機能改善**: 各仕様書の「優先度: 中」セクション
- **パフォーマンス最適化**: [architecture/database_design.md](architecture/database_design.md) のパフォーマンス考慮事項

#### 🟢 優先度: 低（必要になってから）
- **将来拡張**: 各仕様書の「将来拡張計画」セクション
- **複数時間軸対応**: [api/api_specification.md](api/api_specification.md) の将来拡張計画

## 🔍 よくある参照パターン

### エラー対応時
- **API エラー**: [api/api_specification.md](api/api_specification.md) の「エラーハンドリング」
- **DB エラー**: [architecture/database_design.md](architecture/database_design.md) の「トラブルシューティング」
- **DB接続エラー**: [guides/DATABASE_SETUP.md](guides/DATABASE_SETUP.md) の「トラブルシューティング」
- **環境エラー**: [guides/setup_guide.md](guides/setup_guide.md) の「トラブルシューティング」

### 新機能追加時
1. [architecture/project_architecture.md](architecture/project_architecture.md) - 既存アーキテクチャとの整合性確認
2. [api/api_specification.md](api/api_specification.md) - API設計への影響確認
3. [architecture/database_design.md](architecture/database_design.md) - データ構造への影響確認
4. [architecture/frontend_design.md](architecture/frontend_design.md) - UI/UXへの影響確認

### コードレビュー時
- **API レビュー**: [api/api_specification.md](api/api_specification.md) の「実装例」
- **DB レビュー**: [architecture/database_design.md](architecture/database_design.md) のSQLAlchemyモデル定義
- **フロントエンド レビュー**: [architecture/frontend_design.md](architecture/frontend_design.md) の実装例

## 📌 開発の進め方

### ステップ1: 環境構築
```bash
# 1. セットアップガイドに従って環境構築
参照: guides/setup_guide.md

# 2. PostgreSQLセットアップ
参照: guides/DATABASE_SETUP.md

# 3. 動作確認
参照: guides/setup_guide.md の「動作確認」セクション
```

### ステップ2: MVP実装
```bash
# 1. データベース実装
参照: architecture/database_design.md の「優先度: 高」

# 2. API実装
参照: api/api_specification.md の「優先度: 高」

# 3. フロントエンド実装
参照: architecture/frontend_design.md の「優先度: 高」
```

### ステップ3: 機能拡張
```bash
# 必要に応じて各仕様書の「優先度: 中・低」を参照
```

## 🎯 重要な設計判断基準

### 技術選定時
- [architecture/project_architecture.md](architecture/project_architecture.md) の「技術スタック」に従う
- **避けるもの**: 同ファイルの「避けるもの」セクションを確認

### データ設計時
- [architecture/database_design.md](architecture/database_design.md) の「設計方針」に従う
- **制約**: 同ファイルの「制約」セクションを必ず確認

### API設計時
- [api/api_specification.md](api/api_specification.md) の「開発方針」に従う
- **エラーハンドリング**: 同ファイルの標準に準拠

## 🔄 継続的改善

このドキュメントと各仕様書は、開発進捗に合わせて継続的に更新していきます。

### 更新タイミング
- 新機能実装時
- 技術仕様変更時
- トラブルシューティング追加時
- 開発フロー改善時

---

💡 **ヒント**: 不明な点があれば、まず該当する仕様書を確認し、それでも解決しない場合は新しいIssueを作成してください。

## テストマーカーの標準化（追記）

このプロジェクトでは、テストファイル単位での実行選択を容易にするため、モジュールレベルの pytest マーカー（`pytestmark = pytest.mark.<name>`）を順次導入しています。

主な標準マーカー:

- `unit` — ユニットテスト（`tests/unit/`）
- `integration` — 統合テスト（`tests/integration/`）
- `e2e` — E2Eテスト（`tests/e2e/`）
- `slow` — 長時間実行テスト
- `docs` — ドキュメント関連テスト（`tests/docs/`）

運用上のポイント:

- モジュールレベルマーカーはファイル先頭付近に `import pytest` の後で宣言されています（例: `pytestmark = pytest.mark.docs`）。
- これらのマーカーは `pytest.ini` の `markers` セクションに登録されており、`--strict-markers` を有効にしても収集エラーになりません。
- ファイル単位での実行は `pytest -m docs` のように `-m` オプションで行います。

この変更は Issue #219 によるもので、レビュワーがテストを絞って実行しやすくする目的で行われました。
