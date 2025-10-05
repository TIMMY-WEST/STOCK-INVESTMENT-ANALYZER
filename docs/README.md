# 株価データ取得システム - 開発者向けドキュメント

## 📋 概要

このプロジェクトは、Yahoo Finance（yfinance）から日本企業の株価データを取得し、PostgreSQLデータベースに格納するWebアプリケーションです。

**設計理念**: 動作優先・シンプル設計・後から拡張

## 🗂️ 仕様書一覧と利用場面

開発時に参照する仕様書とその利用場面を以下に示します。

### 🏗️ プロジェクト全体設計

| 仕様書 | ファイル | 参照場面 |
|-------|---------|----------|
| **プロジェクトアーキテクチャ** | [`project_architecture.md`](./project_architecture.md) | プロジェクト全体の構成理解・技術スタック選定・ディレクトリ構成確認 |
| **環境構築・セットアップ** | [`setup_guide.md`](./setup_guide.md) | 開発環境構築・初回セットアップ・トラブルシューティング |

### 🔧 技術実装

| 仕様書 | ファイル | 参照場面 |
|-------|---------|----------|
| **API仕様書** | [`api_specification.md`](./api_specification.md) | API エンドポイント実装・リクエスト/レスポンス形式確認・エラーハンドリング実装 |
| **データベース設計** | [`database_design.md`](./database_design.md) | テーブル設計・SQLAlchemyモデル実装・インデックス作成・データマイグレーション |
| **データベースセットアップ** | [`DATABASE_SETUP.md`](./DATABASE_SETUP.md) | PostgreSQL環境構築・データベース接続設定・初期セットアップ・トラブルシューティング |
| **フロントエンド設計** | [`frontend_design.md`](./frontend_design.md) | UI/UXデザイン・HTML/CSS/JavaScript実装・レスポンシブ対応 |

### 🚀 開発プロセス

| 仕様書 | ファイル | 参照場面 |
|-------|---------|----------|
| **GitHub運用ワークフロー** | [`github_workflow.md`](./github_workflow.md) | Issue管理・ブランチ戦略・PR作成・CI/CD設定 |
| **バルクデータサービス利用ガイド** | [`bulk_data_service_guide.md`](./bulk_data_service_guide.md) | 複数銘柄の一括取得・進捗トラッキング・運用ガイド |

## 🤖 AI開発者向けガイド

### タスク別推奨参照順序

#### 🏁 初期セットアップ時
1. [`project_architecture.md`](./project_architecture.md) - 全体像把握
2. [`setup_guide.md`](./setup_guide.md) - 環境構築
3. [`DATABASE_SETUP.md`](./DATABASE_SETUP.md) - PostgreSQLセットアップ
4. [`github_workflow.md`](./github_workflow.md) - 開発フロー確認

#### 🛠️ バックエンド開発時
1. [`api_specification.md`](./api_specification.md) - APIエンドポイント実装
2. [`database_design.md`](./database_design.md) - データベースモデル実装
3. [`DATABASE_SETUP.md`](./DATABASE_SETUP.md) - データベース接続・セットアップ
4. [`project_architecture.md`](./project_architecture.md) - 技術スタック確認

#### 🎨 フロントエンド開発時
1. [`frontend_design.md`](./frontend_design.md) - UI/UX設計確認
2. [`api_specification.md`](./api_specification.md) - API連携仕様
3. [`project_architecture.md`](./project_architecture.md) - フロントエンド技術確認

#### 🚀 リリース・デプロイ時
1. [`github_workflow.md`](./github_workflow.md) - CI/CD・デプロイフロー
2. [`setup_guide.md`](./setup_guide.md) - 本番環境セットアップ
3. [`DATABASE_SETUP.md`](./DATABASE_SETUP.md) - 本番環境データベースセットアップ

### 開発優先度別機能マップ

#### 🔴 優先度: 高（MVP必須）
- **API実装**: [`api_specification.md`](./api_specification.md) の「優先度: 高」セクション
- **DB実装**: [`database_design.md`](./database_design.md) の「優先度: 高」セクション  
- **UI実装**: [`frontend_design.md`](./frontend_design.md) の「優先度: 高」セクション

#### 🟡 優先度: 中（動作確認後）
- **機能改善**: 各仕様書の「優先度: 中」セクション
- **パフォーマンス最適化**: [`database_design.md`](./database_design.md) のパフォーマンス考慮事項

#### 🟢 優先度: 低（必要になってから）
- **将来拡張**: 各仕様書の「将来拡張計画」セクション
- **複数時間軸対応**: [`api_specification.md`](./api_specification.md) の将来拡張計画

## 🔍 よくある参照パターン

### エラー対応時
- **API エラー**: [`api_specification.md`](./api_specification.md) の「エラーハンドリング」
- **DB エラー**: [`database_design.md`](./database_design.md) の「トラブルシューティング」
- **DB接続エラー**: [`DATABASE_SETUP.md`](./DATABASE_SETUP.md) の「トラブルシューティング」
- **環境エラー**: [`setup_guide.md`](./setup_guide.md) の「トラブルシューティング」

### 新機能追加時
1. [`project_architecture.md`](./project_architecture.md) - 既存アーキテクチャとの整合性確認
2. [`api_specification.md`](./api_specification.md) - API設計への影響確認
3. [`database_design.md`](./database_design.md) - データ構造への影響確認
4. [`frontend_design.md`](./frontend_design.md) - UI/UXへの影響確認

### コードレビュー時
- **API レビュー**: [`api_specification.md`](./api_specification.md) の「実装例」
- **DB レビュー**: [`database_design.md`](./database_design.md) のSQLAlchemyモデル定義
- **フロントエンド レビュー**: [`frontend_design.md`](./frontend_design.md) の実装例

## 📌 開発の進め方

### ステップ1: 環境構築
```bash
# 1. セットアップガイドに従って環境構築
参照: setup_guide.md

# 2. PostgreSQLセットアップ
参照: DATABASE_SETUP.md

# 3. 動作確認
参照: setup_guide.md の「動作確認」セクション
```

### ステップ2: MVP実装
```bash
# 1. データベース実装
参照: database_design.md の「優先度: 高」

# 2. API実装  
参照: api_specification.md の「優先度: 高」

# 3. フロントエンド実装
参照: frontend_design.md の「優先度: 高」
```

### ステップ3: 機能拡張
```bash
# 必要に応じて各仕様書の「優先度: 中・低」を参照
```

## 🎯 重要な設計判断基準

### 技術選定時
- [`project_architecture.md`](./project_architecture.md) の「技術スタック」に従う
- **避けるもの**: 同ファイルの「避けるもの」セクションを確認

### データ設計時
- [`database_design.md`](./database_design.md) の「設計方針」に従う
- **制約**: 同ファイルの「制約」セクションを必ず確認

### API設計時
- [`api_specification.md`](./api_specification.md) の「開発方針」に従う
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
