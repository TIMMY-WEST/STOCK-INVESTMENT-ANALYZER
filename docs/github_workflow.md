# 株価データ取得・管理システム GitHub運用ルール

## 目次

- [株価データ取得・管理システム GitHub運用ルール](#株価データ取得管理システム-github運用ルール)
  - [目次](#目次)
  - [1. 開発ワークフロー概要（個人+AI開発向け）](#1-開発ワークフロー概要個人ai開発向け)
    - [1.1 基本方針](#11-基本方針)
    - [1.2 開発サイクル概要](#12-開発サイクル概要)
  - [2. Issue管理とタスクトラッキング](#2-issue管理とタスクトラッキング)
    - [2.1 Issue管理の基本方針（小規模開発向け）](#21-issue管理の基本方針小規模開発向け)
      - [Issue作成の基本ルール](#issue作成の基本ルール)
      - [Issue分割の目安](#issue分割の目安)
      - [基本設定項目（シンプル化）](#基本設定項目シンプル化)
      - [Pull Request連携](#pull-request連携)
    - [2.2 実装中の追加課題対応（シンプル化）](#22-実装中の追加課題対応シンプル化)
      - [基本的な対応パターン](#基本的な対応パターン)
      - [判断の目安](#判断の目安)
    - [2.3 プロジェクト管理（シンプル化）](#23-プロジェクト管理シンプル化)
      - [カンバンボード構成](#カンバンボード構成)
      - [日常の進捗管理](#日常の進捗管理)
    - [2.4 段階的開発の仕組み（簡素化）](#24-段階的開発の仕組み簡素化)
      - [機能フラグによる段階的リリース](#機能フラグによる段階的リリース)
      - [シンプルなAPI設計](#シンプルなapi設計)
  - [3. ブランチ戦略（個人開発・小規模開発向け）](#3-ブランチ戦略個人開発小規模開発向け)
    - [3.1 基本方針とブランチ構成](#31-基本方針とブランチ構成)
      - [メインブランチ](#メインブランチ)
      - [作業ブランチ](#作業ブランチ)
    - [3.2 ワークフローパターン](#32-ワークフローパターン)
      - [シンプルワークフロー（推奨）](#シンプルワークフロー推奨)
    - [3.3 ブランチ管理手順](#33-ブランチ管理手順)
      - [ブランチ命名規則](#ブランチ命名規則)
      - [新しい作業の開始](#新しい作業の開始)
    - [3.4 マージ戦略](#34-マージ戦略)
      - [個人開発向けのマージ方式](#個人開発向けのマージ方式)
      - [ブランチ保護ルール](#ブランチ保護ルール)
    - [3.5 ベストプラクティス](#35-ベストプラクティス)
      - [やるべきこと ✅](#やるべきこと-)
      - [避けるべきこと ❌](#避けるべきこと-)
  - [4. CI/CD（GitHub Actions）](#4-cicdgithub-actions)
    - [4.1 基本方針](#41-基本方針)
    - [4.2 基本的なワークフロー構成](#42-基本的なワークフロー構成)
      - [メインワークフロー](#メインワークフロー)
    - [4.3 ブランチ保護との連携](#43-ブランチ保護との連携)
      - [PR作成時の自動チェック](#pr作成時の自動チェック)
      - [mainブランチへのマージ条件](#mainブランチへのマージ条件)
    - [4.4 セキュリティ・品質チェック](#44-セキュリティ品質チェック)
      - [依存関係の脆弱性チェック](#依存関係の脆弱性チェック)
      - [コード品質チェック](#コード品質チェック)
    - [4.5 デプロイメント（必要に応じて）](#45-デプロイメント必要に応じて)
      - [本番デプロイワークフロー（例）](#本番デプロイワークフロー例)
    - [4.6 ワークフロー管理のベストプラクティス](#46-ワークフロー管理のベストプラクティス)
      - [やるべきこと ✅](#やるべきこと--1)
      - [避けるべきこと ❌](#避けるべきこと--1)
    - [4.7 環境変数とシークレット管理](#47-環境変数とシークレット管理)
      - [GitHub Secrets設定例](#github-secrets設定例)
      - [ワークフローでの使用例](#ワークフローでの使用例)
    - [4.8 トラブルシューティング](#48-トラブルシューティング)
      - [よくある問題と対処法](#よくある問題と対処法)
      - [ログの確認方法](#ログの確認方法)
  - [5. まとめ](#5-まとめ)

## 1. 開発ワークフロー概要（個人+AI開発向け）

### 1.1 基本方針

このシステムは**個人開発者とAI（Claude）による小規模開発**を前提としており、シンプルで効率的なワークフローを採用します。

**主な特徴**:
- シンプルなIssue管理とタスクトラッキング
- 柔軟な開発サイクル（必要に応じて1-3日程度の短期サイクル）
- 基本的なPRレビュー（セルフレビュー中心）
- 軽量なCI/CD（必要最小限）

### 1.2 開発サイクル概要
```
┌─ タスク計画 ─┐    ┌─ 実装・レビュー ─┐    ┌─ 統合・デプロイ ─┐
│              │    │                  │    │                  │
│ • Issue作成   │ ── │ • ブランチ作成・実装│ ── │ • PRマージ        │
│ • 優先度設定  │    │ • セルフレビュー   │    │ • テスト実行      │
│ • 作業見積もり│    │ • AI支援活用      │    │ • 必要に応じてデプロイ│
└──────────────┘    └──────────────────┘    └──────────────────┘
```

## 2. Issue管理とタスクトラッキング

### 2.1 Issue管理の基本方針（小規模開発向け）

個人+AI開発では、シンプルで実用的なIssue管理を行います。複雑な細分化や厳密なルールよりも、**実装効率と品質のバランス**を重視します。

#### Issue作成の基本ルール
- **適度なサイズ**: 1-3日で完了できるタスク単位で作成
- **明確な目標**: 何を実装するかが分かりやすい
- **テスト可能**: 完了時に動作確認できる単位

#### Issue分割の目安
```
✅ 適切なIssue例（小規模開発向け）:
- "株価データ取得API実装（基本CRUD一式）"
- "フロントエンド画面作成（一覧・詳細・登録）"
- "データベース設定とマイグレーション"
- "Docker環境構築"
- "エラーハンドリング強化"

⚠️ 必要に応じて分割する例:
- 非常に複雑な機能（500行超えが予想される場合）
- 複数の技術領域にまたがる場合（DB+API+UI）
- 独立してテストしたい場合
```

#### 基本設定項目（シンプル化）
- **Assignees**: 基本的に自分をアサイン
- **Labels**: 必要最小限のラベル
  - 優先度: `priority:high`, `priority:medium`, `priority:low`
  - タスク種別: `feature`, `bugfix`, `enhancement`, `docs`
  - 技術領域: `backend`, `frontend`, `database`, `infrastructure`
- **Milestone**: 必要に応じて設定（例: `v1.0-MVP`）
- **Projects**: シンプルなカンバンボード
- **PRレビュー観点**: Issue作成時に関連するPRレビュー観点を事前記載し、レビューの効率化を図ること
- **仕様書との整合性確認**: 実装内容が既存の仕様書・ドキュメントと乖離していないかを必ず確認すること

#### Pull Request連携
- PRタイトルにIssue番号を含める: `#101: 株価データ取得API実装`
- PRマージ時に `Closes #101` でIssue自動クローズ
- 基本的に1つのPRは1つのIssueに対応

```markdown
## Issue テンプレート例（シンプル版）
### 実装内容
株価データのCRUD API実装

### 完了条件
- [ ] GET /api/stocks (一覧取得)
- [ ] GET /api/stocks/:id (詳細取得)
- [ ] POST /api/stocks (新規作成)
- [ ] PUT /api/stocks/:id (更新)
- [ ] DELETE /api/stocks/:id (削除)
- [ ] 基本的なバリデーション実装
- [ ] エラーハンドリング実装
- [ ] 動作確認完了

### PRレビュー重点観点
- [ ] APIエンドポイントの設計が適切か（RESTful）
- [ ] エラーハンドリングが適切に実装されているか
- [ ] バリデーションが十分か（入力値チェック）
- [ ] セキュリティ面での問題がないか
- [ ] コードの可読性・保守性が保たれているか
- [ ] 既存機能への影響がないか
- [ ] 実装内容が既存の仕様書・ドキュメントと乖離していないか

### テスト方法
- Postman または curl でのAPI動作確認
- 正常系・異常系の基本テストを実行
```

### 2.2 実装中の追加課題対応（シンプル化）

個人+AI開発では、複雑なルールよりも**実用的で柔軟な対応**を重視します。

#### 基本的な対応パターン
```
📝 小さな課題発見
→ 同じPR内で修正、コミットメッセージに説明を記録

🔥 重大な課題発見
→ 新しいIssue作成、必要に応じて別PRで対応

⚡ 緊急バグ発見
→ 即座修正、後でIssue作成して記録
```

#### 判断の目安
- **同じPRで対応**: 30分以内で修正可能な軽微な問題
- **別Issue作成**: 1時間以上かかるまたは別の技術領域の問題

### 2.3 プロジェクト管理（シンプル化）

#### カンバンボード構成
```
📋 Todo → 👷 In Progress → 👀 Review → ✅ Done
```

#### 日常の進捗管理
- **作業開始時**: Issueを "In Progress" に移動
- **レビュー準備完了時**: Issueを "Review" に移動
- **作業完了時**: Issueを "Done" に移動

### 2.4 段階的開発の仕組み（簡素化）

#### 機能フラグによる段階的リリース
```javascript
// config.js - 必要に応じて機能のON/OFF切り替え
const features = {
  multipleSymbols: false,     // 将来拡張
  excelUpload: false,         // 将来拡張
  dataVisualization: false    // 将来拡張
};
```

#### シンプルなAPI設計
```
# MVP版 - 基本機能
/api/stocks (GET, POST, PUT, DELETE)
/api/stocks/:id (GET, PUT, DELETE)

# 拡張版 - 必要に応じて追加
/api/stocks/batch (POST) # 複数銘柄一括処理
/api/stocks/upload (POST) # Excelアップロード
```

## 3. ブランチ戦略（個人開発・小規模開発向け）

### 3.1 基本方針とブランチ構成

個人開発では、シンプルさと効率性を重視したブランチ戦略を採用します。

#### メインブランチ
- **`main`**: 本番環境にデプロイ可能な安定版コード
  - 常にビルド可能でテストが通る状態を維持
  - プロダクション環境との同期

#### 作業ブランチ
各IssueのタスクはIssue番号を含む個別ブランチで作業：

```bash
# 機能開発
feature/issue-101-stock-api
feature/issue-102-frontend-ui

# バグ修正
bugfix/issue-103-api-error
fix/issue-104-validation-bug

# ホットフィックス（緊急修正）
hotfix/issue-105-security-fix

# ドキュメント
docs/issue-106-readme-update
```

### 3.2 ワークフローパターン

#### シンプルワークフロー（推奨）
```
main → feature/issue-xxx → PR Review → main → Release Tag
```

**メリット**:
- 管理が簡単
- 素早い開発サイクル
- PRレビューによる品質確保

### 3.3 ブランチ管理手順

#### ブランチ命名規則
```bash
{接頭辞}/issue-{Issue番号}-{簡潔な説明}

# 良い例
feature/issue-101-stock-api
bugfix/issue-102-db-connection
docs/issue-103-setup-guide
```

#### 新しい作業の開始
```bash
# 1. 最新のmainブランチに同期
git checkout main
git pull origin main

# 2. 新しいブランチを作成
git checkout -b feature/issue-123-stock-api

# 3. リモートブランチを作成
git push -u origin feature/issue-123-stock-api
```

### 3.4 マージ戦略

#### 個人開発向けのマージ方式

**Squash and Merge（推奨）**
```bash
# PRマージ時に複数コミットを1つにまとめる
# ✅ メリット: クリーンな履歴、Issue単位での追跡
# ✅ 小規模開発に最適
```

#### ブランチ保護ルール

**mainブランチの保護設定**
```yaml
# GitHub Settings > Branches > main
Protect this branch: ✅
- Require pull request reviews before merging: ✅
  - Required number of reviewers: 1 (個人開発では自己レビュー可)
- Require status checks to pass before merging: ✅
- Require branches to be up to date before merging: ✅
```

### 3.5 ベストプラクティス

#### やるべきこと ✅
- **定期的なコミット**: 小さな単位で頻繁にコミット
- **意味のあるコミットメッセージ**: 変更内容が分かりやすいメッセージ
- **PRセルフレビュー**: マージ前に自分でコードをレビュー
- **テスト実行**: PR作成前に全テストが通ることを確認

#### 避けるべきこと ❌
- **直接mainへのpush**: 必ずPR経由でマージ
- **長期間のブランチ**: 1週間以上放置されたブランチ
- **巨大なPR**: 500行を超える変更は分割検討
- **コンフリクトの放置**: マージコンフリクトは即座に解決

## 4. CI/CD（GitHub Actions）

### 4.1 基本方針

個人+AI開発では、シンプルで効率的なCI/CDパイプラインを構築します。複雑な設定よりも、**必要最小限の自動化**で品質と効率性を向上させることを重視します。

### 4.2 基本的なワークフロー構成

#### メインワークフロー
```yaml
# .github/workflows/main.yml
name: CI/CD Pipeline

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout code
        uses: actions/checkout@v4
        
      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '18'
          cache: 'npm'
          
      - name: Install dependencies
        run: npm ci
        
      - name: Run linting
        run: npm run lint
        
      - name: Run tests
        run: npm test
        
      - name: Run type checking
        run: npm run type-check
        
  build:
    runs-on: ubuntu-latest
    needs: test
    steps:
      - name: Checkout code
        uses: actions/checkout@v4
        
      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '18'
          cache: 'npm'
          
      - name: Install dependencies
        run: npm ci
        
      - name: Build application
        run: npm run build
        
      - name: Archive build artifacts
        uses: actions/upload-artifact@v4
        with:
          name: build-files
          path: dist/
```

### 4.3 ブランチ保護との連携

#### PR作成時の自動チェック
```yaml
# PRマージ前に必須チェック項目
- ✅ Linting pass
- ✅ Type checking pass  
- ✅ Unit tests pass
- ✅ Build successful
```

#### mainブランチへのマージ条件
- 全てのGitHub Actionsジョブが成功
- PRレビュー完了（セルフレビュー可）
- ブランチが最新状態

### 4.4 セキュリティ・品質チェック

#### 依存関係の脆弱性チェック
```yaml
# .github/workflows/security.yml
name: Security Scan

on:
  schedule:
    - cron: '0 9 * * 1'  # 毎週月曜日 9:00
  pull_request:
    branches: [ main ]

jobs:
  security:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout code
        uses: actions/checkout@v4
        
      - name: Run npm audit
        run: npm audit --audit-level moderate
        
      - name: Dependency Review
        uses: actions/dependency-review-action@v4
        if: github.event_name == 'pull_request'
```

#### コード品質チェック
```yaml
# .github/workflows/code-quality.yml
name: Code Quality

on:
  pull_request:
    branches: [ main ]

jobs:
  quality:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout code
        uses: actions/checkout@v4
        
      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '18'
          cache: 'npm'
          
      - name: Install dependencies
        run: npm ci
        
      - name: Code coverage
        run: npm run test:coverage
        
      - name: Upload coverage to Codecov
        uses: codecov/codecov-action@v4
        with:
          file: ./coverage/lcov.info
```

### 4.5 デプロイメント（必要に応じて）

#### 本番デプロイワークフロー（例）
```yaml
# .github/workflows/deploy.yml
name: Deploy to Production

on:
  push:
    tags:
      - 'v*'  # バージョンタグでトリガー

jobs:
  deploy:
    runs-on: ubuntu-latest
    if: github.ref_type == 'tag'
    
    steps:
      - name: Checkout code
        uses: actions/checkout@v4
        
      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '18'
          cache: 'npm'
          
      - name: Install dependencies
        run: npm ci
        
      - name: Build for production
        run: npm run build:prod
        
      - name: Deploy to server
        run: |
          # デプロイスクリプトの実行
          echo "Deploy to production server"
```

### 4.6 ワークフロー管理のベストプラクティス

#### やるべきこと ✅
- **軽量なCI**: 実行時間を5分以内に抑制
- **早期失敗**: 問題があれば素早く検出して停止
- **キャッシュ活用**: node_modules等の依存関係をキャッシュ
- **並列実行**: 独立したジョブは並列で実行
- **明確な名前**: ワークフローとジョブに分かりやすい名前を付与

#### 避けるべきこと ❌
- **過度な自動化**: 不要な複雑さを避ける
- **長時間実行**: 10分を超えるワークフローは見直し
- **秘密情報の露出**: API キーやパスワードをログに出力
- **無駄なトリガー**: 不要なイベントでのワークフロー実行

### 4.7 環境変数とシークレット管理

#### GitHub Secrets設定例
```
# Repository Settings > Secrets and variables > Actions
DATABASE_URL=postgresql://...
API_KEY=your-api-key
DEPLOY_TOKEN=your-deploy-token
```

#### ワークフローでの使用例
```yaml
env:
  NODE_ENV: production
  DATABASE_URL: ${{ secrets.DATABASE_URL }}
  
steps:
  - name: Run with secrets
    run: npm run migrate
    env:
      API_KEY: ${{ secrets.API_KEY }}
```

### 4.8 トラブルシューティング

#### よくある問題と対処法
```
❌ npm ci が失敗する
→ package-lock.json のコミット確認

❌ テストがタイムアウトする  
→ jest.config.js のtimeout設定を確認

❌ ビルドが失敗する
→ 環境変数の設定を確認

❌ デプロイが失敗する
→ 秘密情報の設定を確認
```

#### ログの確認方法
- GitHub > Actions タブでワークフロー実行状況を確認
- 失敗したジョブの詳細ログを確認
- 必要に応じてdebugログを有効化（`ACTIONS_STEP_DEBUG: true`）

## 5. まとめ

この GitHub ワークフローは個人+AI による小規模開発に最適化されており、以下の特徴があります：

✅ **シンプルな管理**: 複雑な手順を排除し、本質的な開発に集中
✅ **柔軟な対応**: 厳密なルールよりも実用性を重視
✅ **品質確保**: 基本的なレビューとテストで品質維持
✅ **効率性**: 素早い開発サイクルで迅速な機能実装
✅ **拡張性**: 必要に応じてルールを追加・調整可能

**開発の進め方**:
1. 必要な機能をIssueとして作成
2. 適切なサイズに分割（1-3日で完了する単位）
3. ブランチを作成して実装
4. セルフレビューを行いPR作成
5. テスト確認後、mainにマージ
6. 必要に応じてデプロイ

このワークフローにより、小規模開発でも品質を保ちながら効率的な開発が可能になります。