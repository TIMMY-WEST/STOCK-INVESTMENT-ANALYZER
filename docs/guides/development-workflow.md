# 開発ワークフロー

## 📋 目次

- [概要](#概要)
- [開発サイクル](#開発サイクル)
- [Issue管理](#issue管理)
- [ブランチ戦略](#ブランチ戦略)
- [コミットとPR](#コミットとpr)
- [レビュープロセス](#レビュープロセス)
- [テストとCI/CD](#テストとcicd)
- [デプロイ](#デプロイ)

---

## 概要

**最終更新**: 2025-11-02
**文書バージョン**: v2.0.0
**AI優先度**: 高

本ドキュメントは、Issue作成から実装、レビュー、デプロイまでの開発フロー全体を説明します。

### 開発サイクル概要

```
1. Issue作成 → 2. ブランチ作成 → 3. 実装 → 4. PR作成
    ↓                                            ↓
8. デプロイ ← 7. マージ ← 6. レビュー ← 5. テスト実行
```

---

## 開発サイクル

### 1. タスクの特定とIssue作成

**手順**:
1. 実装する機能やバグを特定
2. GitHubでIssueを作成
3. 適切なラベル、マイルストーン、優先度を設定

**Issueテンプレート例**:
```markdown
## 実装内容
株価データのCRUD API実装

## 完了条件
- [ ] GET /api/stocks (一覧取得)
- [ ] POST /api/stocks (新規作成)
- [ ] PUT /api/stocks/:id (更新)
- [ ] DELETE /api/stocks/:id (削除)
- [ ] 基本的なバリデーション実装
- [ ] エラーハンドリング実装
- [ ] 動作確認完了

## テスト方法
- Postman または curl でのAPI動作確認
```

### 2. ブランチ作成と実装

**ブランチ命名規則**:
```bash
{接頭辞}/issue-{Issue番号}-{簡潔な説明}

例:
feature/issue-101-stock-api
bugfix/issue-102-db-connection
docs/issue-103-readme-update
```

**作業開始**:
```bash
# 1. 最新のmainブランチに同期
git checkout main
git pull origin main

# 2. 新しいブランチを作成
git checkout -b feature/issue-123-stock-api

# 3. リモートブランチを作成
git push -u origin feature/issue-123-stock-api
```

### 3. コミット

**コミットメッセージ規約**:
```
<type>: <subject>

<body>

Refs: #<Issue番号>
```

**Type一覧**:
- `feat`: 新機能
- `fix`: バグ修正
- `docs`: ドキュメント変更
- `style`: コードフォーマット
- `refactor`: リファクタリング
- `test`: テスト追加・修正
- `chore`: ビルド・ツール関連

**例**:
```bash
git commit -m "feat: 株価データ取得APIエンドポイント実装

- GET /api/stocks エンドポイント追加
- バリデーション実装
- エラーハンドリング追加

Refs: #101"
```

### 4. Pull Request作成

**PRタイトル**:
```
#<Issue番号>: <変更内容>

例:
#101: 株価データ取得API実装
```

**PR説明テンプレート**:
```markdown
## 関連Issue
Closes #101

## 変更内容
- GET /api/stocks エンドポイント実装
- バリデーション追加
- エラーハンドリング実装

## テスト
- [ ] ユニットテスト追加
- [ ] 統合テスト追加
- [ ] 手動テスト完了

## レビューポイント
- APIエンドポイントの設計
- エラーハンドリングの適切性
- セキュリティ面の確認
```

### 5. テスト実行

**PR作成前の必須チェック**:
```bash
# 全テスト実行
pytest

# カバレッジ確認
pytest --cov=app --cov-fail-under=70

# Linter実行
flake8 app/
black app/ --check
mypy app/
```

### 6. コードレビュー

**セルフレビュー**:
1. PRの差分を自分で確認
2. 不要なコメントやデバッグコードを削除
3. テストが全て通過していることを確認

**レビュー観点**:
- [ ] コーディング規約に準拠しているか
- [ ] テストが適切に追加されているか
- [ ] ドキュメントが更新されているか
- [ ] セキュリティ上の問題がないか
- [ ] パフォーマンスに影響がないか

### 7. マージ

**マージ方式**: Squash and Merge（推奨）
- 複数コミットを1つにまとめる
- クリーンな履歴を維持

```bash
# GitHubでのマージ後、ローカルを同期
git checkout main
git pull origin main

# 作業ブランチを削除
git branch -d feature/issue-123-stock-api
```

### 8. デプロイ

本番環境へのデプロイは、mainブランチへのマージ後に自動または手動で実行します。

詳細は [CI/CDパイプライン設定](../ci-cd/pipeline-config.md) を参照。

---

## Issue管理

### Issueのライフサイクル

```
📋 Todo → 👷 In Progress → 👀 Review → ✅ Done
```

### ラベル分類

**優先度**:
- `priority:high` - 緊急対応が必要
- `priority:medium` - 通常の優先度
- `priority:low` - 時間があるときに対応

**タスク種別**:
- `feature` - 新機能
- `bugfix` - バグ修正
- `enhancement` - 既存機能の改善
- `docs` - ドキュメント

**技術領域**:
- `backend` - バックエンド
- `frontend` - フロントエンド
- `database` - データベース
- `infrastructure` - インフラ

---

## ブランチ戦略

### メインブランチ

- **`main`**: 本番環境にデプロイ可能な安定版コード
  - 常にビルド可能でテストが通る状態を維持
  - プロダクション環境との同期

### 作業ブランチ

各Issueのタスクは個別ブランチで作業:

```bash
# 機能開発
feature/issue-101-stock-api

# バグ修正
bugfix/issue-103-api-error
fix/issue-104-validation-bug

# ホットフィックス（緊急修正）
hotfix/issue-105-security-fix

# ドキュメント
docs/issue-106-readme-update
```

### ブランチ保護ルール

**mainブランチの保護設定**:
- ✅ Require pull request reviews before merging
- ✅ Require status checks to pass before merging
- ✅ Require branches to be up to date before merging
- ❌ 直接pushは禁止

---

## コミットとPR

### コミットのベストプラクティス

**やるべきこと** ✅:
- 小さな単位で頻繁にコミット
- 意味のあるコミットメッセージ
- 1コミット = 1つの論理的変更

**避けるべきこと** ❌:
- 巨大なコミット（500行以上の変更）
- 曖昧なメッセージ（例: "fix", "update"）
- 無関係な変更を含むコミット

### PRのサイズ

- **理想**: 200〜300行以内
- **最大**: 500行以内
- **500行超**: 分割を検討

---

## レビュープロセス

### レビュアーの責任

1. **コードの品質確認**: コーディング規約、ベストプラクティス
2. **テストの妥当性**: テストが適切に追加されているか
3. **セキュリティチェック**: 脆弱性がないか
4. **パフォーマンス確認**: パフォーマンスに悪影響がないか

### レビューコメントの書き方

**良いコメント例**:
```
この実装では、データベース接続がリーク する可能性があります。
with文を使用してセッションを管理することを推奨します。

例:
with SessionLocal() as session:
    # 処理
```

**避けるべきコメント**:
```
これは良くない。
```

---

## テストとCI/CD

### ローカルでのテスト実行

```bash
# 全テスト実行
pytest

# カバレッジ付き実行
pytest --cov=app --cov-report=html

# 特定レベルのテスト実行
pytest -m unit
pytest -m integration
pytest -m "not e2e"
```

### CI/CDパイプライン

**PR作成時**:
1. ユニットテスト実行
2. 統合テスト実行
3. カバレッジ測定（最低70%）
4. Linterチェック

**mainブランチマージ時**:
1. 全テスト実行（E2E含む）
2. カバレッジレポート保存
3. 自動デプロイ（設定による）

詳細は [CI/CDパイプライン設定](../ci-cd/pipeline-config.md) を参照。

---

## デプロイ

### デプロイフロー

```
mainブランチマージ → CI/CD自動実行 → テスト成功 → デプロイ
```

### デプロイ前のチェックリスト

- [ ] 全テストが通過している
- [ ] カバレッジが70%以上
- [ ] Linterエラーがない
- [ ] ドキュメントが更新されている
- [ ] データベースマイグレーションが適用されている

---

## まとめ

この開発ワークフローは、小規模開発に最適化されています:

✅ **シンプルな管理**: 複雑な手順を排除
✅ **柔軟な対応**: 実用性を重視
✅ **品質確保**: 基本的なレビューとテストで品質維持
✅ **効率性**: 素早い開発サイクル

---

## 関連ドキュメント

- [テスト規約](../standards/testing-standards.md) - テストの作成方法
- [コーディング規約](../standards/coding-standards.md) - コーディング規約
- [Git/GitHub運用ルール](../standards/git-workflow.md) - Git詳細ルール
- [CI/CDパイプライン設定](../ci-cd/pipeline-config.md) - CI/CD詳細

---

**最終更新**: 2025-11-02
**文書バージョン**: v2.0.0
