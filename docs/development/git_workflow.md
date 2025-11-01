---
category: development
ai_context: high
last_updated: 2025-10-22
related_docs:
  - ./github_workflow.md
  - ../guides/setup_guide.md
  - ../architecture/project_architecture.md
---

# Git運用ワークフロー

## 目次

- [Git運用ワークフロー](#git運用ワークフロー)
  - [目次](#目次)
  - [1. 概要](#1-概要)
    - [1.1 目的](#11-目的)
    - [1.2 対象読者](#12-対象読者)
    - [1.3 github\_workflow.md との違い](#13-github_workflowmd-との違い)
  - [2. ワークフローモデルの選定](#2-ワークフローモデルの選定)
    - [2.1 GitHub Flowの採用](#21-github-flowの採用)
    - [2.2 採用理由](#22-採用理由)
    - [2.3 基本フロー](#23-基本フロー)
  - [3. ブランチ戦略](#3-ブランチ戦略)
    - [3.1 ブランチ構成](#31-ブランチ構成)
    - [3.2 ブランチ命名規則](#32-ブランチ命名規則)
    - [3.3 ブランチのライフサイクル管理](#33-ブランチのライフサイクル管理)
  - [4. Conventional Commits規約](#4-conventional-commits規約)
    - [4.1 基本フォーマット](#41-基本フォーマット)
    - [4.2 Type（種別）の定義](#42-type種別の定義)
    - [4.3 Scope（スコープ）の定義](#43-scopeスコープの定義)
    - [4.4 コミットメッセージの書き方ガイド](#44-コミットメッセージの書き方ガイド)
    - [4.5 破壊的変更（BREAKING CHANGE）](#45-破壊的変更breaking-change)
  - [5. マージ戦略](#5-マージ戦略)
    - [5.1 マージ方式の選定](#51-マージ方式の選定)
    - [5.2 マージ前の確認事項](#52-マージ前の確認事項)
    - [5.3 マージ後の処理](#53-マージ後の処理)
  - [6. 品質ゲート設定](#6-品質ゲート設定)
    - [6.1 概要](#61-概要)
    - [6.2 品質基準](#62-品質基準)
    - [6.3 pre-commitフックによる品質チェック](#63-pre-commitフックによる品質チェック)
    - [6.4 品質ゲート失敗時の対応](#64-品質ゲート失敗時の対応)
  - [7. コンフリクト解決ルール](#7-コンフリクト解決ルール)
    - [7.1 コンフリクト発生時の基本対応](#71-コンフリクト発生時の基本対応)
    - [7.2 コンフリクト解決の手順](#72-コンフリクト解決の手順)
    - [7.3 コンフリクト解決のベストプラクティス](#73-コンフリクト解決のベストプラクティス)
    - [7.4 コンフリクト解決後の検証](#74-コンフリクト解決後の検証)
  - [8. 実践ワークフロー](#8-実践ワークフロー)
    - [8.1 新機能開発の流れ](#81-新機能開発の流れ)
    - [8.2 バグ修正の流れ](#82-バグ修正の流れ)
    - [8.3 緊急修正（ホットフィックス）の流れ](#83-緊急修正ホットフィックスの流れ)
  - [9. ベストプラクティス](#9-ベストプラクティス)
    - [9.1 やるべきこと ✅](#91-やるべきこと-)
    - [9.2 避けるべきこと ❌](#92-避けるべきこと-)
  - [10. トラブルシューティング](#10-トラブルシューティング)
    - [10.1 よくある問題と対処法](#101-よくある問題と対処法)
    - [10.2 緊急時の対応](#102-緊急時の対応)
  - [11. まとめ](#11-まとめ)

## 1. 概要

### 1.1 目的

本ドキュメントは、STOCK-INVESTMENT-ANALYZERプロジェクトにおける共同開発を円滑に進めるためのGit運用ワークフローを定義します。

### 1.2 対象読者

- プロジェクトの開発メンバー全員
- コードレビュアー
- リポジトリ管理者

### 1.3 github_workflow.md との違い

| 項目 | github_workflow.md | git_workflow.md（本ドキュメント） |
|------|-------------------|--------------------------------|
| **対象** | 個人+AI開発 | 共同開発 |
| **重点** | シンプルさ、効率性 | 一貫性、コミュニケーション |
| **詳細度** | 基本的なルール | 詳細なルールと規約 |
| **Conventional Commits** | 言及のみ | 詳細な仕様 |
| **コンフリクト解決** | 簡単な言及 | 詳細な手順とルール |

## 2. ワークフローモデルの選定

### 2.1 GitHub Flowの採用

本プロジェクトでは**GitHub Flow**を採用します。

```
┌─────────────────────────────────────────────────────────┐
│                      GitHub Flow                         │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  main ─────────────────────●───────────────────●────▶  │
│                           ╱                   ╱         │
│                          ╱  PR Review        ╱          │
│  feature/xxx ───────────●                   ╱           │
│                                            ╱            │
│  bugfix/yyy ───────────────────────────────●            │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

### 2.2 採用理由

| メリット | 説明 |
|---------|------|
| **シンプル** | mainブランチを中心とした直感的な構造 |
| **継続的デリバリー** | いつでもデプロイ可能な状態を維持 |
| **Pull Request中心** | コードレビューと議論の場を提供 |
| **小規模チーム向き** | 少人数での開発に最適 |
| **CI/CD連携** | GitHub Actionsとの親和性が高い |

### 2.3 基本フロー

```bash
# 1. 最新のmainブランチを取得
git checkout main
git pull origin main

# 2. 作業ブランチを作成
git checkout -b feature/MS1-add-architecture-docs

# 3. 作業を実施（コミットを繰り返す）
git add .
git commit -m "feat(docs): アーキテクチャドキュメントの初版作成"

# 4. リモートにプッシュ
git push -u origin feature/MS1-add-architecture-docs

# 5. Pull Requestを作成

# 6. レビューとマージ

# 7. ローカルブランチの削除
git checkout main
git pull origin main
git branch -d feature/MS1-add-architecture-docs
```

## 3. ブランチ戦略

### 3.1 ブランチ構成

| ブランチタイプ | 目的 | ライフサイクル |
|--------------|------|--------------|
| **main** | 本番デプロイ可能な安定版 | 永続 |
| **feature/** | 新機能開発 | 一時的 |
| **fix/** | バグ修正 | 一時的 |
| **refactor/** | リファクタリング | 一時的 |
| **docs/** | ドキュメント更新 | 一時的 |
| **test/** | テスト追加 | 一時的 |

### 3.2 ブランチ命名規則

#### 基本フォーマット

```
{type}/{identifier}-{description}
```

#### Type（種別）

| Type | 用途 | 例 |
|------|------|-----|
| `feature` | 新機能開発 | `feature/MS1-add-architecture-docs` |
| `fix` | バグ修正 | `fix/issue-123-pagination-bug` |
| `refactor` | リファクタリング | `refactor/service-layer-cleanup` |
| `docs` | ドキュメント | `docs/update-api-documentation` |
| `test` | テスト追加 | `test/add-unit-tests-for-fetcher` |
| `chore` | ビルド・設定 | `chore/update-dependencies` |
| `perf` | パフォーマンス改善 | `perf/optimize-database-queries` |

#### Identifier（識別子）

マイルストーン番号またはIssue番号を使用します：

```bash
# マイルストーン番号を使用（推奨）
feature/MS1-add-architecture-docs
feature/MS2-implement-bulk-fetch

# Issue番号を使用
fix/issue-123-pagination-bug
docs/issue-456-update-readme
```

#### Description（説明）

- **小文字**とハイフンを使用
- **簡潔**で分かりやすい英語表現
- **動詞**から始める（add, update, fix, remove など）

#### 良い例 ✅

```bash
feature/MS1-add-architecture-docs
fix/issue-123-pagination-bug
refactor/service-layer-cleanup
docs/update-api-documentation
test/add-unit-tests-for-fetcher
```

#### 悪い例 ❌

```bash
feature/new_feature        # 説明が不明確
fix/Bug123                 # 大文字、識別子が不明確
update-docs                # typeが欠落
feature/MS1_Add_Docs       # アンダースコア、大文字使用
```

### 3.3 ブランチのライフサイクル管理

#### 作成タイミング

```bash
# 作業開始前に必ずmainを最新化
git checkout main
git pull origin main

# 新しいブランチを作成
git checkout -b feature/MS1-add-architecture-docs
```

#### 作業中の管理

```bash
# 定期的にコミット（1日1回以上推奨）
git add .
git commit -m "feat(docs): アーキテクチャ概要を追加"

# 定期的にプッシュ（1日1回以上推奨）
git push origin feature/MS1-add-architecture-docs

# 長期ブランチの場合、定期的にmainを取り込む
git checkout feature/MS1-add-architecture-docs
git fetch origin
git rebase origin/main
```

#### 削除タイミング

```bash
# PRマージ後、すぐにローカルブランチを削除
git checkout main
git pull origin main
git branch -d feature/MS1-add-architecture-docs

# リモートブランチは自動削除設定を推奨
# （GitHub Settings > General > Automatically delete head branches）
```

#### ブランチの有効期限

| 状態 | 有効期限 | 対応 |
|------|---------|------|
| **作業中** | 2週間以内 | 長期化する場合は分割検討 |
| **PR作成後** | 1週間以内 | レビュー促進またはクローズ |
| **マージ後** | 即座に削除 | ローカル・リモート両方 |

## 4. Conventional Commits規約

### 4.1 基本フォーマット

```
<type>(<scope>): <subject>

<body>

<footer>
```

#### 実例

```
feat(api): 株価データ一括取得APIの実装

- JPX全銘柄の取得エンドポイントを追加
- バッチ処理による効率的なデータ取得
- エラーハンドリングとリトライ機能

Closes #123
```

### 4.2 Type（種別）の定義

| Type | 説明 | 例 | セマンティックバージョニング |
|------|------|-----|---------------------------|
| `feat` | 新機能追加 | 新しいAPI、UI機能 | MINOR (0.x.0) |
| `fix` | バグ修正 | 既存機能の不具合修正 | PATCH (0.0.x) |
| `refactor` | リファクタリング | 動作変更なしのコード改善 | - |
| `docs` | ドキュメント | README、仕様書の更新 | - |
| `test` | テスト | テストコード追加・修正 | - |
| `chore` | ビルド・設定 | 依存関係更新、設定変更 | - |
| `style` | コードスタイル | フォーマット、セミコロン | - |
| `perf` | パフォーマンス | 速度・メモリ使用量改善 | PATCH (0.0.x) |
| `ci` | CI/CD | GitHub Actions等の設定 | - |
| `revert` | 取り消し | 以前のコミットを取り消し | - |

### 4.3 Scope（スコープ）の定義

プロジェクトの主要コンポーネントを示します：

| Scope | 説明 | 例 |
|-------|------|-----|
| `api` | バックエンドAPI | `feat(api): 株価取得エンドポイント追加` |
| `frontend` | フロントエンド | `fix(frontend): ページネーションのバグ修正` |
| `database` | データベース | `refactor(database): インデックス最適化` |
| `docs` | ドキュメント | `docs(docs): セットアップガイド更新` |
| `test` | テスト | `test(test): APIテストケース追加` |
| `infra` | インフラ | `chore(infra): Docker設定更新` |
| `ci` | CI/CD | `ci(ci): GitHub Actionsワークフロー追加` |
| `config` | 設定 | `chore(config): 環境変数設定追加` |

### 4.4 コミットメッセージの書き方ガイド

#### Subject（件名）

```bash
# ✅ 良い例
feat(api): 株価データ一括取得APIの実装
fix(frontend): ページネーション時の表示バグ修正
refactor(database): クエリ最適化による高速化
docs(readme): セットアップ手順の更新

# ❌ 悪い例
update code              # type/scopeが不明確
Fix Bug                  # 具体性に欠ける
feat: いろいろ修正        # 日本語は避ける（bodyで使用可）
```

#### 件名のルール

1. **50文字以内**に収める
2. **命令形**で記述（"追加する" ではなく "追加"）
3. **小文字**で始める（typeの後）
4. **ピリオド不要**
5. **具体的**な内容

#### Body（本文）

```bash
# ✅ 良い例
feat(api): 株価データ一括取得APIの実装

JPX上場全銘柄のデータを効率的に取得するためのAPIを実装。
以下の機能を含む：

- GET /api/stocks/bulk エンドポイント
- ページネーション対応（limit/offset）
- エラーハンドリングとリトライ機能
- レート制限の実装

パフォーマンステスト済み（1000件/秒）
```

#### 本文のルール

1. **件名と1行空ける**
2. **72文字で改行**
3. **What（何を）** と **Why（なぜ）** を記述
4. **箇条書き**を活用
5. **日本語可**（チーム内で統一）

#### Footer（フッター）

```bash
# Issue参照
Closes #123
Fixes #456
Refs #789

# 破壊的変更
BREAKING CHANGE: APIエンドポイントのURLを変更

# 複数の参照
Closes #123, #456
Reviewed-by: @username
```

### 4.5 破壊的変更（BREAKING CHANGE）

既存の機能に影響を与える変更の場合：

```bash
feat(api)!: APIレスポンス形式の変更

BREAKING CHANGE: APIレスポンスの形式を変更しました。

変更前:
{
  "data": {...}
}

変更後:
{
  "success": true,
  "data": {...},
  "metadata": {...}
}

マイグレーションガイド: docs/migration/v2.0.0.md

Closes #789
```

#### ポイント

- `!` をtypeの後に付ける: `feat(api)!:`
- フッターに `BREAKING CHANGE:` を記載
- マイグレーション手順を明記

## 5. マージ戦略

### 5.1 マージ方式の選定

本プロジェクトでは**Squash and Merge**を標準とします。

#### Squash and Merge（推奨）

```bash
# 複数のコミットを1つにまとめてマージ
# メリット: クリーンな履歴、Issue単位での追跡
# 使用ケース: ほとんどの機能開発・バグ修正
```

**実行例:**

```bash
# GitHub UI上で "Squash and merge" を選択

# マージコミットメッセージ例:
feat(api): 株価データ一括取得APIの実装 (#123)

- JPX全銘柄の取得エンドポイントを追加
- バッチ処理による効率的なデータ取得
- エラーハンドリングとリトライ機能

Closes #123
```

#### Rebase and Merge（条件付き）

```bash
# 各コミットを保持したままマージ
# メリット: 詳細な履歴保存
# 使用ケース: 複数の論理的変更を含む大規模PR
```

**使用条件:**

- 各コミットが**意味のある単位**である
- コミットメッセージが**Conventional Commits**に準拠
- レビュアーが**履歴保存の必要性**を認めた場合

#### Merge Commit（非推奨）

```bash
# マージコミットを作成
# デメリット: 履歴が複雑化
# 使用ケース: 基本的に使用しない
```

### 5.2 マージ前の確認事項

#### 必須チェック項目

- [ ] **全てのCI/CDチェックがパス**
  - Linting
  - Type checking
  - Unit tests
  - Integration tests
  - Build
- [ ] **コードレビュー承認済み**（最低1名）
- [ ] **コンフリクトが解決済み**
- [ ] **ブランチが最新のmainに追従**
- [ ] **PRの説明が十分**
- [ ] **関連Issueがリンク済み**

#### 推奨チェック項目

- [ ] **ドキュメント更新済み**（必要な場合）
- [ ] **破壊的変更の確認**（該当する場合）
- [ ] **パフォーマンス影響の検証**（該当する場合）
- [ ] **セキュリティリスクの評価**（該当する場合）

### 5.3 マージ後の処理

```bash
# 1. ローカルのmainブランチを更新
git checkout main
git pull origin main

# 2. マージ済みブランチを削除
git branch -d feature/MS1-add-architecture-docs

# 3. リモートブランチの削除確認
# （GitHub設定で自動削除推奨）
git fetch --prune

# 4. 関連Issueのクローズ確認
# （PRマージ時にCloses #XXXで自動クローズ）
```

## 6. 品質ゲート設定

### 6.1 概要

コードベースの品質を維持し、リグレッションを防止するために、以下の品質ゲートを導入しています。

### 6.2 品質基準

#### 6.2.1 コードカバレッジ

**閾値**: 70%

- 測定対象: `app/`
- pyproject.tomlで設定: `--cov-fail-under=70`
- GitHub Actionsで自動チェック（PRマージ前）

#### 6.2.2 複雑度チェック (McCabe)

**閾値**: 10

- .flake8で設定: `max-complexity = 10`
- 循環的複雑度が10を超える関数はリファクタリング必須

#### 6.2.3 コードスタイル (Flake8)

- 最大行長: 79文字
- PEP 8準拠

#### 6.2.4 型チェック (mypy)

- 段階的な厳格化を実施中
- 警告は許容、エラーのみ失敗

### 6.3 pre-commitフックによる品質チェック

#### 設定されている品質ゲート

コミット前に以下のチェックが自動実行されます:

1. **Blackフォーマット**: コードの自動整形
2. **isort**: インポート文の整理
3. **Flake8 linting**: コードスタイルチェック
4. **複雑度チェック**: McCabe複雑度（閾値10）
5. **mypy**: 型チェック

#### セットアップ

```bash
# pre-commitのインストール
pip install pre-commit

# フックの有効化
pre-commit install

# 手動実行
pre-commit run --all-files
```

#### pre-commitフックの動作

コミット時に自動的に以下のチェックが順次実行されます:

1. **自動修正可能なチェック** (Black, isort)
   - 問題があれば自動修正
   - 修正後は再度コミットが必要

2. **静的チェック** (Flake8, 複雑度, mypy)
   - 問題があればエラー表示
   - 手動で修正が必要

すべてのチェックが通過するまで、コミットは完了しません。

### 6.4 GitHub Actionsによる品質チェック

PRマージ前に以下のチェックが自動実行されます:

1. **テスト実行**: E2Eテスト以外の全テスト
2. **カバレッジチェック**: テストカバレッジ（閾値70%）
   - カバレッジが70%未満の場合、CIが失敗
   - カバレッジレポートはアーティファクトとして保存

### 6.5 品質ゲート失敗時の対応

#### カバレッジ不足

```bash
# カバレッジレポートで未カバー箇所を確認
pytest --cov=app --cov-report=term-missing

# 不足している箇所のテストを追加
# tests/unit/ または tests/integration/ にテストを作成
```

#### 複雑度超過

```bash
# 複雑な関数を特定
flake8 app/ --select=C901 --statistics

# リファクタリング戦略
# - 関数を小さく分割
# - 早期リターンを活用
# - ガード節を使用
# - 複雑な条件式を変数に抽出
```

#### スタイル違反

```bash
# 自動整形ツールを実行
black app/ --line-length 79
isort app/

# 手動修正が必要な箇所を確認
flake8 app/ --statistics
```

#### 型エラー

```bash
# 型エラーの詳細を確認
mypy app/ --show-error-codes

# 型ヒントを追加または修正
```

## 7. コンフリクト解決ルール

### 7.1 コンフリクト発生時の基本対応

```bash
# コンフリクトが発生した場合の優先順位

1. コミュニケーション優先
   → チームメンバーと相談

2. 最新のmainを取り込む
   → git rebase origin/main

3. 慎重に解決
   → 両方のコードの意図を理解

4. テスト実施
   → 解決後は必ずテスト
```

### 7.2 コンフリクト解決の手順

#### Step 1: 現状確認

```bash
# 最新のmainブランチを取得
git fetch origin

# コンフリクト状況を確認
git status
```

#### Step 2: Rebaseでコンフリクト解決

```bash
# 作業ブランチでrebase実行
git checkout feature/MS1-add-architecture-docs
git rebase origin/main

# コンフリクトが発生した場合
# → エディタでコンフリクトマーカーを確認
```

#### Step 3: コンフリクトマーカーの理解

```python
<<<<<<< HEAD (現在のブランチ)
# 自分の変更
def fetch_stock_data(symbol, limit=100):
    return api.get_stocks(symbol, limit)
=======
# mainブランチの変更
def fetch_stock_data(symbol, interval="1d"):
    return api.get_stocks(symbol, interval)
>>>>>>> origin/main
```

#### Step 4: 適切な解決方法の選択

| パターン | 対応 | 例 |
|---------|------|-----|
| **自分の変更を採用** | HEAD側を残す | 新機能が優先される場合 |
| **mainの変更を採用** | origin/main側を残す | バグ修正が優先される場合 |
| **両方をマージ** | 両方の変更を統合 | 競合しない独立した変更 |
| **新しい実装** | 完全に書き直す | 両方とも不適切な場合 |

#### Step 5: 解決後の確認

```bash
# コンフリクト解決後、ファイルをステージング
git add <解決したファイル>

# rebaseを続行
git rebase --continue

# 解決を中止したい場合
git rebase --abort

# 強制プッシュ（rebase後は必要）
git push --force-with-lease origin feature/MS1-add-architecture-docs
```

### 7.3 コンフリクト解決のベストプラクティス

#### やるべきこと ✅

1. **相談する**
   ```bash
   # コンフリクトの原因が不明な場合
   # → 元の変更者に相談
   # → チームで議論
   ```

2. **両方のコードを理解する**
   ```bash
   # 自分の変更の意図
   # 相手の変更の意図
   # → 両方を活かせる解決策を探す
   ```

3. **テストを実行する**
   ```bash
   # コンフリクト解決後は必ずテスト
   npm test
   npm run lint
   npm run type-check
   ```

4. **コミットメッセージに記録**
   ```bash
   git commit -m "fix(api): mainとのコンフリクトを解決

   - fetch_stock_data関数のシグネチャを統一
   - limit と interval の両方をサポート
   - 既存の動作を維持しつつ新機能を追加"
   ```

#### 避けるべきこと ❌

1. **無理やり自分の変更を押し通す**
   - 相手の変更意図を無視しない

2. **コンフリクトマーカーを残す**
   - `<<<<<<<`, `=======`, `>>>>>>>` を削除し忘れない

3. **テストせずにプッシュ**
   - 解決後は必ずテスト実行

4. **git push --force の使用**
   - `git push --force-with-lease` を使用（安全）

### 7.4 コンフリクト解決後の検証

```bash
# 1. ローカルテストの実行
npm test
npm run lint
npm run type-check

# 2. 手動での動作確認
npm run dev
# → 実際に機能が動作するか確認

# 3. CIでの確認
git push --force-with-lease origin feature/MS1-add-architecture-docs
# → GitHub ActionsのCI結果を確認

# 4. レビュアーへの通知
# PRコメントでコンフリクト解決について説明
```

## 8. 実践ワークフロー

### 8.1 新機能開発の流れ

```bash
# === Step 1: Issue作成 ===
# GitHub上でIssueを作成
# - タイトル、説明、ラベル、マイルストーンを設定

# === Step 2: ブランチ作成 ===
git checkout main
git pull origin main
git checkout -b feature/MS1-add-architecture-docs

# === Step 3: 開発作業 ===
# コードを書く

# === Step 4: コミット ===
git add .
git commit -m "feat(docs): アーキテクチャドキュメントの初版作成

- システム全体の構成図を追加
- 各コンポーネントの責務を明確化
- データフロー図を作成

Refs #123"

# === Step 5: プッシュ ===
git push -u origin feature/MS1-add-architecture-docs

# === Step 6: Pull Request作成 ===
# GitHub上でPRを作成
# - タイトル: "feat(docs): アーキテクチャドキュメントの追加 (#123)"
# - 説明: Issueの内容を参照
# - レビュアー指定

# === Step 7: レビュー対応 ===
# レビューコメントに対応
git add .
git commit -m "fix(docs): レビュー指摘事項の修正"
git push origin feature/MS1-add-architecture-docs

# === Step 8: マージ ===
# GitHub上で "Squash and merge"

# === Step 9: ブランチ削除 ===
git checkout main
git pull origin main
git branch -d feature/MS1-add-architecture-docs
```

### 8.2 バグ修正の流れ

```bash
# === Step 1: Issue作成 ===
# バグ報告のIssueを作成
# - 再現手順、期待動作、実際の動作を記載

# === Step 2: ブランチ作成 ===
git checkout main
git pull origin main
git checkout -b fix/issue-123-pagination-bug

# === Step 3: バグ修正 ===
# バグを修正

# === Step 4: テスト追加 ===
# バグの再発を防ぐためのテストを追加

# === Step 5: コミット ===
git add .
git commit -m "fix(frontend): ページネーション時の表示バグ修正

問題:
- ページ遷移時に前のページのデータが残る
- 次ページのデータが重複表示される

修正内容:
- ページ遷移前にデータをクリア
- 新しいデータの取得待機処理を追加

テスト:
- ページネーション動作のテストケース追加
- エッジケースのテストも追加

Fixes #123"

# === Step 6: PR作成・マージ ===
# 新機能開発と同様の流れ
```

### 8.3 緊急修正（ホットフィックス）の流れ

```bash
# === 緊急性の高いバグの場合 ===

# Step 1: 即座にブランチ作成
git checkout main
git pull origin main
git checkout -b hotfix/issue-999-critical-security-fix

# Step 2: 迅速に修正
# 必要最小限の変更

# Step 3: コミット
git add .
git commit -m "fix(security)!: 重大なセキュリティ脆弱性の修正

SECURITY: SQL Injection の脆弱性を修正

影響範囲:
- /api/stocks/:id エンドポイント
- ユーザー入力の検証が不十分

修正内容:
- パラメータバリデーションの強化
- プリペアドステートメントの使用

Fixes #999"

# Step 4: 即座にPR作成
git push -u origin hotfix/issue-999-critical-security-fix

# Step 5: 優先レビュー・マージ
# priority:critical ラベルを付与
# レビュアーに緊急性を通知
```

## 9. ベストプラクティス

### 9.1 やるべきこと ✅

#### コミット

- [ ] **小さく頻繁にコミット** - 論理的な単位で分割
- [ ] **意味のあるメッセージ** - Conventional Commits準拠
- [ ] **関連ファイルをまとめる** - 1つの変更は1つのコミット

#### ブランチ

- [ ] **命名規則を守る** - `{type}/{identifier}-{description}`
- [ ] **定期的にmainを取り込む** - rebaseで最新状態を維持
- [ ] **作業完了後すぐ削除** - ブランチの肥大化を防ぐ

#### Pull Request

- [ ] **レビュー可能なサイズ** - 500行以内推奨
- [ ] **明確な説明** - 何を、なぜ、どのように変更したか
- [ ] **セルフレビュー実施** - PR作成前に自分でコードを確認

#### コミュニケーション

- [ ] **コンフリクトは相談** - 独断で解決しない
- [ ] **レビューコメントに対応** - 建設的な議論
- [ ] **進捗を共有** - 長期ブランチは定期報告

### 9.2 避けるべきこと ❌

#### コミット

- ❌ **巨大なコミット** - 複数の変更を1つにまとめない
- ❌ **意味不明なメッセージ** - "update", "fix" だけは避ける
- ❌ **動作しないコード** - コミット前に必ずテスト

#### ブランチ

- ❌ **直接mainにpush** - 必ずPR経由
- ❌ **長期間のブランチ放置** - 2週間以上は要注意
- ❌ **不適切な命名** - ランダムな名前、意味不明な略語

#### Pull Request

- ❌ **巨大なPR** - 1000行を超える変更
- ❌ **説明不足** - タイトルだけで説明なし
- ❌ **テスト未実施** - CIが失敗している状態でマージ依頼

#### Git操作

- ❌ **git push --force** - `--force-with-lease` を使用
- ❌ **履歴の改変** - 公開済みコミットのrebase
- ❌ **コンフリクトマーカー残し** - マージ後の確認不足

## 10. トラブルシューティング

### 10.1 よくある問題と対処法

#### 問題1: 間違ったブランチにコミットした

```bash
# 解決策: cherry-pickで正しいブランチに移動
git checkout 正しいブランチ
git cherry-pick コミットハッシュ

# 間違ったブランチから削除
git checkout 間違ったブランチ
git reset --hard HEAD~1
```

#### 問題2: コミットメッセージを間違えた

```bash
# 最新のコミットメッセージを修正
git commit --amend -m "正しいメッセージ"

# プッシュ済みの場合（慎重に）
git push --force-with-lease origin ブランチ名
```

#### 問題3: 誤ってmainブランチに直接push

```bash
# 1. 直前のコミットを取り消し
git revert HEAD

# 2. 新しいブランチを作成して正しい手順で対応
git checkout -b fix/revert-accidental-push
git push origin fix/revert-accidental-push

# 3. PRを作成してマージ
```

#### 問題4: コンフリクトが解決できない

```bash
# rebaseを中止
git rebase --abort

# チームメンバーに相談
# または、mergeコミットで対応（最終手段）
git merge origin/main
```

#### 問題5: 誤ってブランチを削除した

```bash
# reflogからブランチを復元
git reflog
git checkout -b 復元するブランチ名 復元するコミットハッシュ
```

### 10.2 緊急時の対応

#### 本番環境に問題を起こした場合

```bash
# 1. 即座にrevert
git revert 問題のあるコミットハッシュ
git push origin main

# 2. ホットフィックスブランチで修正
git checkout -b hotfix/emergency-fix
# 修正作業
git commit -m "fix: 緊急修正"
git push origin hotfix/emergency-fix

# 3. 優先レビュー・マージ
# priority:critical ラベルで対応
```

#### レポジトリが破損した場合

```bash
# 1. 新しいクローンを作成
cd ..
git clone <リポジトリURL> new-clone
cd new-clone

# 2. 作業中の変更を退避していた場合
# 元のリポジトリから変更をコピー
cp -r ../old-repo/変更ファイル ./

# 3. 新しいブランチで作業再開
git checkout -b 作業ブランチ
```

## 11. まとめ

このGit運用ワークフローにより、以下が実現されます：

### 実現される価値

✅ **一貫性** - チーム全体で統一されたワークフロー
✅ **透明性** - 変更履歴が明確で追跡可能
✅ **品質** - コードレビューとCI/CDによる品質保証
✅ **効率性** - 明確なルールによる迅速な開発
✅ **安全性** - ブランチ保護とコンフリクト解決ルール

### 重要な原則

1. **GitHub Flowを基本とする** - シンプルで効率的
2. **Conventional Commitsを遵守** - 一貫したコミットメッセージ
3. **Pull Requestを必須とする** - コードレビューの徹底
4. **コンフリクトは相談して解決** - チームワーク重視
5. **定期的にmainに追従** - コンフリクトの最小化

### 継続的な改善

このワークフローは固定されたものではなく、チームの成長と共に進化させていきます：

- 定期的なレビュー（四半期ごと）
- チームからのフィードバック収集
- 新しいツール・手法の導入検討
- ドキュメントの継続的な更新

---

**関連ドキュメント:**
- [GitHub運用ルール](./github_workflow.md) - 個人+AI開発向けの簡易版
- [コーディング規約](./coding_standards.md)
- [テスト戦略](./testing_strategy.md)
- [セットアップガイド](../guides/setup_guide.md)

**バージョン:** 1.0.0
**最終更新:** 2025-10-22
**作成者:** Development Team
