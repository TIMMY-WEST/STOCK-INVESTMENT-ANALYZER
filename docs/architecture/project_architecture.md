---
category: architecture
ai_context: high
last_updated: 2025-10-25
related_docs:
  - ../api/api_specification.md
  - ../architecture/database_design.md
  - ../guides/setup_guide.md
---

# 株価データ取得システム - プロジェクト全体アーキテクチャ

## 目次

- [株価データ取得システム - プロジェクト全体アーキテクチャ](#株価データ取得システム---プロジェクト全体アーキテクチャ)
  - [目次](#目次)
  - [1. プロジェクト概要](#1-プロジェクト概要)
    - [1.1 目的](#11-目的)
    - [1.2 設計理念](#12-設計理念)
  - [2. プロジェクトディレクトリ構成](#2-プロジェクトディレクトリ構成)
    - [2.1 計画中のディレクトリ構成（実装予定）](#21-計画中のディレクトリ構成実装予定)
    - [2.2 各ディレクトリ・ファイルの役割](#22-各ディレクトリファイルの役割)
      - [ドキュメント（docs/）](#ドキュメントdocs)
      - [アプリケーション（app/）](#アプリケーションapp)
      - [設定ファイル](#設定ファイル)
  - [3. 現在のアーキテクチャ（超シンプル構成）](#3-現在のアーキテクチャ超シンプル構成)
    - [3.1 シンプルMVP構成](#31-シンプルmvp構成)
    - [3.2 将来の拡張案（現時点では実装しない）](#32-将来の拡張案現時点では実装しない)
  - [4. 技術スタック](#4-技術スタック)
    - [4.1 シンプル技術スタック（動作優先）](#41-シンプル技術スタック動作優先)
    - [4.2 避けるもの（MVP段階では導入しない）](#42-避けるものmvp段階では導入しない)
  - [5. 超シンプル実装構造（MVP優先）](#5-超シンプル実装構造mvp優先)
    - [5.1 MVP実装方針](#51-mvp実装方針)
    - [5.2 実装の進め方](#52-実装の進め方)
  - [6. 開発ステップ（超シンプル）](#6-開発ステップ超シンプル)
    - [Step 1: 最小動作確認（最優先）](#step-1-最小動作確認最優先)
    - [Step 2: データ保存](#step-2-データ保存)
    - [Step 3: UI改善（動作確認後）](#step-3-ui改善動作確認後)
    - [Step 4: 機能追加（必要になってから）](#step-4-機能追加必要になってから)
  - [7. MVP要件（最小限）](#7-mvp要件最小限)
    - [7.1 必須機能](#71-必須機能)
    - [7.2 非機能要件](#72-非機能要件)
    - [7.3 後回しにする要素](#73-後回しにする要素)
  - [8. 開発方針](#8-開発方針)
  - [まとめ](#まとめ)
    - [🎯 **個人+AI開発での超シンプルアプローチ**](#-個人ai開発での超シンプルアプローチ)
      - [開発の進め方](#開発の進め方)
      - [避けるべき過度な設計](#避けるべき過度な設計)
      - [成功の指標](#成功の指標)

## 1. プロジェクト概要

### 1.1 目的
Yahoo Finance（yfinance）から日本企業の株価データを取得し、PostgreSQLデータベースに格納するWebアプリケーション

### 1.2 設計理念
- **動作優先**: まず動くものを作る
- **シンプル設計**: 複雑さを避け、必要最小限の構成
- **後から拡張**: 必要になってから機能追加・リファクタリング

## 2. プロジェクトディレクトリ構成

### 2.1 バックエンドディレクトリ構成（リファクタリング後）

```
stock-investment-analyzer/
├── app/
│   ├── app.py
│   ├── api/
│   │   ├── bulk_data.py
│   │   ├── stock_master.py
│   │   └── system_monitoring.py
│   ├── models.py
│   ├── services/
│   │   ├── stock_data/
│   │   │   ├── fetcher.py
│   │   │   ├── saver.py
│   │   │   ├── converter.py
│   │   │   ├── validator.py
│   │   │   ├── orchestrator.py
│   │   │   └── scheduler.py
│   │   ├── bulk/
│   │   │   └── bulk_service.py
│   │   ├── jpx/
│   │   │   └── jpx_stock_service.py
│   │   ├── batch/
│   │   │   └── batch_service.py
│   │   └── common/
│   │       └── error_handler.py
│   ├── utils/
│   │   ├── database_utils.py
│   │   ├── structured_logger.py
│   │   └── timeframe_utils.py
│   ├── templates/
│   │   ├── index.html
│   │   └── websocket_test.html
│   └── static/
│       ├── style.css
│       ├── app.js
│       └── jpx_sequential.js
├── docs/
│   ├── architecture/...
│   └── api/...
├── tests/...
└── scripts/...
```

#### 2.1.1 サービスディレクトリ再編成（旧→新）
- `app/services/stock_data_fetcher.py` → `app/services/stock_data/fetcher.py`
- `app/services/stock_data_saver.py` → `app/services/stock_data/saver.py`
- `app/services/stock_data_converter.py` → `app/services/stock_data/converter.py`
- `app/services/stock_data_validator.py` → `app/services/stock_data/validator.py`
- `app/services/stock_data_orchestrator.py` → `app/services/stock_data/orchestrator.py`
- `app/services/stock_data_scheduler.py` → `app/services/stock_data/scheduler.py`
- `app/services/bulk_data_service.py` → `app/services/bulk/bulk_service.py`
- `app/services/jpx_stock_service.py` → `app/services/jpx/jpx_stock_service.py`
- `app/services/batch_service.py` → `app/services/batch/batch_service.py`
- `app/services/error_handler.py` → `app/services/common/error_handler.py`

> フロントエンド（`templates/`, `static/`）の構成は変更不要です。バックエンドのみ機能単位のモジュール化を行います。

### 2.2 各ディレクトリ・ファイルの役割

#### ドキュメント（docs/）
- **api_specification.md**: REST API の仕様とエンドポイント定義
- **database_design.md**: データベーススキーマとテーブル設計
- **frontend_design.md**: フロントエンド設計とUI/UX仕様
- **github_workflow.md**: 開発ワークフローとGit運用方針
- **project_architecture.md**: プロジェクト全体のアーキテクチャ設計
- **README.md**: ドキュメント全体の概要とナビゲーション
- **setup_guide.md**: 開発環境のセットアップ手順
- **tasks/**: タスク・進捗管理ディレクトリ
  - **issues.md**: 発見された課題と問題の管理
  - **milestones.md**: 開発マイルストーンと進捗管理

#### アプリケーション（app/）
- **app.py**: Flaskアプリケーションのメインファイル
- **models.py**: SQLAlchemyを使用したデータベースモデル
- **templates/**: Jinja2テンプレートファイル
- **static/**: CSS、JavaScript、画像などの静的ファイル
- **api/**: API Blueprint群（フロント→バック呼び出し用のルート定義）

#### テスト（tests/）
- **test_app.py**: Flaskアプリケーションの機能テスト
- **test_models.py**: データベースモデルの単体テスト
- **conftest.py**: pytestの設定ファイルとテスト用フィクスチャ

#### 設定ファイル
- **requirements.txt**: Python パッケージの依存関係
- **.env.example**: 環境変数の設定例
- **.gitignore**: バージョン管理から除外するファイル

## 3. 現在のアーキテクチャ（超シンプル構成）

### 3.1 シンプルMVP構成
```
┌─────────────────────────────────────┐
│            Web Browser              │
│        (Alpine.js + Tailwind)      │
└─────────────────────────────────────┘
                  │ HTTP
                  ▼
┌─────────────────────────────────────┐
│             Flask App               │
│           (Port: 8000)              │
│                                     │
│  ┌─── Frontend Serving ───────────┐ │
│  │  • HTML/CSS/JS                 │ │
│  │  • Static Files                │ │
│  └───────────────────────────────── │ │
│                                     │
│  ┌─── API Endpoints ─────────────┐  │
│  │  • /api/fetch-data            │  │
│  │  • /api/stocks                │  │
│  │  • /api/bulk/status/<job_id>   │  │
│  └───────────────────────────────┘  │
│                                     │
│  ┌─── Business Logic ──────────────┐ │
│  │  • Yahoo Finance 連携          │ │
│  │  • データ処理                   │ │
│  │  • プログレス管理               │ │
│  └────────────────────────────────┘ │
└─────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────┐
│            PostgreSQL               │
│           (Port: 5432)              │
└─────────────────────────────────────┘
```

### 3.2 将来の拡張案（現時点では実装しない）
> **注意**: 以下は将来の可能性であり、現時点では実装せず、MVPが完成してから検討する

- マイクロサービス化
- API Gateway導入
- サービス分離
- Docker化

## 4. 技術スタック

### 4.1 シンプル技術スタック（動作優先）
- **言語**: Python 3.12.8
- **フロントエンド**: HTML + 最小限のJavaScript（Alpine.jsは後で検討）
- **バックエンド**: Flask（最小限の機能のみ）
- **データベース**: PostgreSQL + SQLAlchemy（本格的なデータ管理）
- **外部API**: Yahoo Finance (yfinance)
- **Background Tasks**: なし（同期処理で開始、必要になったら追加）

### 4.2 避けるもの（MVP段階では導入しない）
- 複雑なフロントエンドフレームワーク
- マイクロサービス
- Docker
- 複雑な状態管理
- リアルタイム通信

## 5. 超シンプル実装構造（MVP優先）

```
app/
├── app.py               # メインアプリケーション（全てここに集約）
├── models.py            # データベースモデル（1ファイル）
├── templates/
│   └── index.html       # HTMLファイル
└── static/
    └── style.css        # 最小限のCSS
```

### 5.1 MVP実装方針
- **1つのファイルに集約**: `app.py` にルーティング・ビジネスロジック全て
- **最小限のファイル構成**: 複雑なフォルダ構造は避ける
- **後からリファクタリング**: 動いてから整理する

### 5.2 実装の進め方
1. **最小限の動作確認**: データ取得→表示だけ
2. **データベース保存**: PostgreSQLで永続化
3. **UI改善**: 必要に応じて見た目を調整
4. **機能追加**: 動作確認できてから新機能追加

## 6. 開発ステップ（超シンプル）

### Step 1: 最小動作確認（最優先）
- Flask起動
- Yahoo Financeから1つの株価データ取得
- ブラウザに表示

### Step 2: データ保存
- PostgreSQLでデータ保存
- 取得したデータの表示

### Step 3: UI改善（動作確認後）
- HTMLテーブルでデータ表示
- 基本的なスタイル

### Step 4: 機能追加（必要になってから）
- 複数銘柄対応
- 期間指定
- その他の機能

## 7. MVP要件（最小限）

### 7.1 必須機能
- Yahoo Financeからの株価データ取得
- データベースへの保存
- Webブラウザでの表示

### 7.2 非機能要件
- **動作すること**（最重要）
- ローカル環境での実行
- 基本的なエラーハンドリング

### 7.3 後回しにする要素
- セキュリティ（ローカル開発のため）
- 監視・ログ
- パフォーマンス最適化
- Docker化
- テスト（動作確認後に追加）

## 8. 開発方針

- **動作第一**: 完璧でなくても動くものを作る
- **シンプル第一**: 複雑な設計は避ける
- **後から改善**: リファクタリングは動作確認後
- **学習重視**: 新しい技術は必要になってから

---

## まとめ

### 🎯 **個人+AI開発での超シンプルアプローチ**

#### 開発の進め方
1. **最小限で開始**: Flask + PostgreSQL + 基本HTML
2. **動作確認優先**: 複雑な設計より動くもの
3. **段階的改善**: 必要になってから機能追加・リファクタリング

#### 避けるべき過度な設計
- マイクロサービス（現時点では不要）
- 複雑なフロントエンドフレームワーク
- 過度な抽象化・設計パターン
- 完璧なテストカバレッジ

#### 成功の指標
- **3日以内**に基本機能が動作
- **1週間以内**にデータ保存・表示が完成
- コードが理解しやすく修正しやすい状態

このアプローチで、**動作するものを素早く構築**し、**必要に応じて進化**させることができます。
