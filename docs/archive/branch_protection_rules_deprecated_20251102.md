---
category: development
ai_context: high
last_updated: 2025-10-22
related_docs:
  - ./git_workflow.md
  - ./github_workflow.md
  - ./testing_strategy.md
deprecated: true
deprecated_date: 2025-11-02
replacement: ../guides/development-workflow.md
---

# ⚠️ このドキュメントは非推奨です

**移行日**: 2025-11-02
**理由**: 内容が統合ワークフローガイドに統合されました
**移行先**: `docs/guides/development-workflow.md` (ブランチ保護設定セクション)

このドキュメントは参照用として保管されていますが、最新情報は上記の移行先を参照してください。

---

# GitHubブランチ保護ルール設定ガイド

## 目次

- [GitHubブランチ保護ルール設定ガイド](#githubブランチ保護ルール設定ガイド)
  - [目次](#目次)
  - [1. 概要](#1-概要)
    - [1.1 目的](#11-目的)
    - [1.2 対象ブランチ](#12-対象ブランチ)
  - [2. ブランチ保護ルール設定内容](#2-ブランチ保護ルール設定内容)
    - [2.1 mainブランチの保護設定](#21-mainブランチの保護設定)
    - [2.2 設定項目の詳細](#22-設定項目の詳細)
  - [3. 設定手順](#3-設定手順)
    - [3.1 GitHub Web UIからの設定](#31-github-web-uiからの設定)
    - [3.2 設定値の確認](#32-設定値の確認)
  - [4. CI/CD要件](#4-cicd要件)
    - [4.1 必須チェック項目](#41-必須チェック項目)
    - [4.2 GitHub Actions ワークフロー](#42-github-actions-ワークフロー)
  - [5. 動作確認方法](#5-動作確認方法)
    - [5.1 直接プッシュの禁止確認](#51-直接プッシュの禁止確認)
    - [5.2 Pull Request必須化の確認](#52-pull-request必須化の確認)
    - [5.3 CI/CD全パス必須の確認](#53-cicd全パス必須の確認)
    - [5.4 コンフリクト解決必須の確認](#54-コンフリクト解決必須の確認)
    - [5.5 再承認設定の確認](#55-再承認設定の確認)
  - [6. 運用上の注意事項](#6-運用上の注意事項)
    - [6.1 緊急時の対応](#61-緊急時の対応)
    - [6.2 設定変更時のルール](#62-設定変更時のルール)
    - [6.3 ベストプラクティス](#63-ベストプラクティス)
  - [7. トラブルシューティング](#7-トラブルシューティング)
    - [7.1 マージできない場合](#71-マージできない場合)
    - [7.2 CI/CDが失敗する場合](#72-cicdが失敗する場合)
  - [8. まとめ](#8-まとめ)

## 1. 概要

### 1.1 目的

このドキュメントは、STOCK-INVESTMENT-ANALYZERプロジェクトのGitHubリポジトリにおけるブランチ保護ルールの設定方法と運用ガイドラインを定義します。

**ブランチ保護の目的:**
- コードの品質保証
- セキュリティリスクの低減
- チーム全体での一貫した開発フロー
- 本番環境への誤ったデプロイ防止

### 1.2 対象ブランチ

| ブランチ  | 保護レベル | 説明                                     |
| --------- | ---------- | ---------------------------------------- |
| `main`    | **最高**   | 本番デプロイ可能な安定版                 |
| `develop` | **中**     | 統合開発ブランチ（将来的に使用する場合） |

現在は **`main`ブランチのみ** を保護対象とします。

## 2. ブランチ保護ルール設定内容

### 2.1 mainブランチの保護設定

以下の設定をGitHub Web UIまたはAPIで適用します：

| 設定項目                                                             | 設定値            | 理由                                           |
| -------------------------------------------------------------------- | ----------------- | ---------------------------------------------- |
| **Require a pull request before merging**                            | ✅ 有効            | 直接プッシュを禁止し、レビュープロセスを必須化 |
| **Require approvals**                                                | ✅ 有効（最低1名） | コードレビューの徹底                           |
| **Dismiss stale pull request approvals when new commits are pushed** | ✅ 有効            | レビュー後の変更に対する再確認                 |
| **Require review from Code Owners**                                  | ❌ 無効            | 現時点では不要（将来的に検討）                 |
| **Require status checks to pass before merging**                     | ✅ 有効            | CI/CDの全チェック通過を必須化                  |
| **Require branches to be up to date before merging**                 | ✅ 有効            | 最新のmainに追従済みであることを保証           |
| **Require conversation resolution before merging**                   | ✅ 有効            | レビューコメントの解決を必須化                 |
| **Require signed commits**                                           | ❌ 無効            | 現時点では不要（GPG署名は任意）                |
| **Require linear history**                                           | ❌ 無効            | Squash and Mergeで対応                         |
| **Include administrators**                                           | ✅ 有効            | 管理者にも同じルールを適用                     |
| **Allow force pushes**                                               | ❌ 無効            | 履歴の改変を禁止                               |
| **Allow deletions**                                                  | ❌ 無効            | mainブランチの削除を禁止                       |

### 2.2 設定項目の詳細

#### Require a pull request before merging

```yaml
説明: mainブランチへの直接プッシュを禁止
効果: 全ての変更がPull Requestを経由する
例外: なし（管理者も含む）
```

**実現される保護:**
- 意図しない直接プッシュの防止
- コードレビューの機会保証
- 変更履歴の明確化

#### Require approvals

```yaml
説明: 最低1名のレビュアー承認が必要
設定値: 1名以上
推奨: 2名以上（チーム規模に応じて）
```

**レビュアーの責務:**
- コードの品質確認
- セキュリティリスクの評価
- 設計の妥当性チェック
- テストカバレッジの確認

#### Dismiss stale pull request approvals when new commits are pushed

```yaml
説明: 新しいコミットがプッシュされたら承認を無効化
効果: レビュー後の変更を再確認
重要性: 高（セキュリティ上重要）
```

**シナリオ例:**
```
1. レビュアーAがPRを承認
2. 開発者が追加のコミットをプッシュ
3. 承認が自動的に無効化される
4. レビュアーAが再度レビュー・承認
```

#### Require status checks to pass before merging

```yaml
説明: CI/CDの全チェック通過を必須化
必須チェック:
  - Linting (Ruff)
  - Type checking (mypy)
  - Unit tests (pytest)
  - Integration tests
  - Build verification
```

**CI/CD失敗時の対応:**
```bash
# ローカルでテスト実行
pytest tests/

# Linterチェック
ruff check .

# 型チェック
mypy .

# 修正後に再プッシュ
git add .
git commit -m "fix: CI/CDエラーの修正"
git push origin feature/xxx
```

#### Require branches to be up to date before merging

```yaml
説明: mainブランチの最新状態に追従必須
効果: コンフリクトの事前解決
手順: マージ前に最新のmainをrebase
```

**更新手順:**
```bash
# 作業ブランチを最新のmainに追従
git fetch origin
git rebase origin/main

# コンフリクトがある場合は解決
# 解決後、強制プッシュ
git push --force-with-lease origin feature/xxx
```

## 3. 設定手順

### 3.1 GitHub Web UIからの設定

#### Step 1: リポジトリ設定にアクセス

```
1. GitHubでリポジトリを開く
   https://github.com/TIMMY-WEST/STOCK-INVESTMENT-ANALYZER

2. [Settings] タブをクリック

3. 左メニューから [Branches] を選択

4. [Branch protection rules] セクションの [Add rule] をクリック
```

#### Step 2: ブランチパターンの指定

```
Branch name pattern: main
```

#### Step 3: 保護ルールの設定

**Protect matching branches** セクションで以下を設定:

```
☑ Require a pull request before merging
  ☑ Require approvals
    Required number of approvals before merging: 1
  ☑ Dismiss stale pull request approvals when new commits are pushed
  ☐ Require review from Code Owners

☑ Require status checks to pass before merging
  ☑ Require branches to be up to date before merging
  Status checks that are required:
    ☑ Lint (Ruff)
    ☑ Type Check (mypy)
    ☑ Unit Tests (pytest)
    ☑ Build

☑ Require conversation resolution before merging

☐ Require signed commits

☐ Require linear history

☑ Include administrators

☐ Allow force pushes

☐ Allow deletions
```

#### Step 4: 設定の保存

```
[Create] または [Save changes] をクリック
```

### 3.2 設定値の確認

設定後、以下のコマンドで確認可能（GitHub CLI使用）:

```bash
# ブランチ保護ルールの確認
gh api repos/TIMMY-WEST/STOCK-INVESTMENT-ANALYZER/branches/main/protection

# またはWeb UIで確認
# Settings > Branches > Branch protection rules
```

## 4. CI/CD要件

### 4.1 必須チェック項目

ブランチ保護ルールで必須とするCI/CDチェック:

| チェック項目          | ツール       | 目的                 | 失敗時の影響   |
| --------------------- | ------------ | -------------------- | -------------- |
| **Linting**           | Ruff         | コードスタイルの統一 | マージブロック |
| **Type Check**        | mypy         | 型安全性の保証       | マージブロック |
| **Unit Tests**        | pytest       | 機能の正常動作確認   | マージブロック |
| **Integration Tests** | pytest       | システム統合確認     | マージブロック |
| **Build**             | Python build | ビルド可能性の確認   | マージブロック |

### 4.2 GitHub Actions ワークフロー

以下のワークフローが必須チェックとして登録されている必要があります:

```yaml
# .github/workflows/ci.yml の例
name: CI

on:
  pull_request:
    branches: [main]
  push:
    branches: [main]

jobs:
  lint:
    name: Lint (Ruff)
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.12'
      - name: Install dependencies
        run: |
          pip install ruff
      - name: Run Ruff
        run: ruff check .

  type-check:
    name: Type Check (mypy)
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.12'
      - name: Install dependencies
        run: |
          pip install mypy
      - name: Run mypy
        run: mypy .

  test:
    name: Unit Tests (pytest)
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.12'
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install pytest pytest-cov
      - name: Run tests
        run: pytest tests/ --cov

  build:
    name: Build
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.12'
      - name: Build package
        run: |
          pip install build
          python -m build
```

## 5. 動作確認方法

### 5.1 直接プッシュの禁止確認

**テスト手順:**

```bash
# mainブランチに直接プッシュを試みる
git checkout main
echo "test" > test.txt
git add test.txt
git commit -m "test: 直接プッシュのテスト"
git push origin main
```

**期待される結果:**

```
remote: error: GH006: Protected branch update failed for refs/heads/main.
remote: error: Changes must be made through a pull request.
To https://github.com/TIMMY-WEST/STOCK-INVESTMENT-ANALYZER.git
 ! [remote rejected] main -> main (protected branch hook declined)
error: failed to push some refs to 'https://github.com/TIMMY-WEST/STOCK-INVESTMENT-ANALYZER.git'
```

✅ **確認完了:** 直接プッシュがブロックされる

### 5.2 Pull Request必須化の確認

**テスト手順:**

```bash
# 1. 新しいブランチを作成
git checkout -b test/branch-protection
echo "test" > test.txt
git add test.txt
git commit -m "test: ブランチ保護のテスト"
git push -u origin test/branch-protection

# 2. GitHub UIでPRを作成

# 3. レビュアーを指定せずにマージを試みる
```

**期待される結果:**

```
GitHub UI上で:
- "Merge pull request" ボタンが無効化
- "This branch requires approval before merging" メッセージが表示
```

✅ **確認完了:** レビュー承認なしではマージ不可

### 5.3 CI/CD全パス必須の確認

**テスト手順:**

```bash
# 意図的にLintエラーを含むコードをプッシュ
echo "def bad_function( ): pass" > bad_code.py
git add bad_code.py
git commit -m "test: CI/CDチェックのテスト"
git push origin test/branch-protection
```

**期待される結果:**

```
GitHub UI上で:
- CI/CDチェックが実行される
- Lintチェックが失敗
- "All checks have failed" メッセージが表示
- マージボタンが無効化または警告表示
```

✅ **確認完了:** CI/CD失敗時はマージ不可

### 5.4 コンフリクト解決必須の確認

**テスト手順:**

```bash
# 1. main にファイルを追加（別のPRで）
# 2. 同じファイルを変更するPRを作成
# 3. 最初のPRをマージ
# 4. 2番目のPRでコンフリクトが発生
```

**期待される結果:**

```
GitHub UI上で:
- "This branch has conflicts that must be resolved" メッセージ
- マージボタンが無効化
- "Resolve conflicts" ボタンが表示
```

✅ **確認完了:** コンフリクト解決後のみマージ可能

### 5.5 再承認設定の確認

**テスト手順:**

```bash
# 1. PRを作成し、レビュアーに承認してもらう
# 2. 承認後、追加のコミットをプッシュ
git add new_changes.py
git commit -m "feat: 追加機能"
git push origin test/branch-protection
```

**期待される結果:**

```
GitHub UI上で:
- 以前の承認が "Stale" (無効) としてマーク
- "Re-request review" ボタンが表示
- 再度承認が必要な状態になる
```

✅ **確認完了:** 新しいコミット後は再承認が必要

## 6. 運用上の注意事項

### 6.1 緊急時の対応

#### 緊急修正が必要な場合

```bash
# 1. ホットフィックスブランチを作成
git checkout main
git pull origin main
git checkout -b hotfix/critical-security-fix

# 2. 迅速に修正
# ... 修正作業 ...

# 3. コミット・プッシュ
git add .
git commit -m "fix(security)!: 重大なセキュリティ脆弱性の修正"
git push -u origin hotfix/critical-security-fix

# 4. PRを作成し、priority:critical ラベルを付与

# 5. 最低限のレビュー（1名）で迅速にマージ
```

**注意:**
- ブランチ保護ルールは緊急時でも適用されます
- 管理者であっても直接プッシュは不可
- 迅速なレビューとマージを行うため、事前にチームに通知

#### 管理者による一時的な保護解除（最終手段）

```yaml
手順:
  1. Settings > Branches > Branch protection rules
  2. 該当ルールの [Edit] をクリック
  3. 必要な設定を一時的に無効化
  4. 緊急作業を実施
  5. 作業完了後、すぐに設定を元に戻す

警告:
  - この手順は最終手段としてのみ使用
  - 必ずチーム全体に通知
  - 実施理由と経緯をドキュメント化
```

### 6.2 設定変更時のルール

ブランチ保護ルールの変更は以下の手順で実施:

```
1. Issue作成
   - 変更理由を明記
   - チームの合意を得る

2. PRでドキュメント更新
   - 本ドキュメント (branch_protection_rules.md) を更新

3. 設定変更の実施
   - GitHub UI で設定を変更

4. 変更内容の周知
   - チームに通知
   - 運用への影響を説明
```

### 6.3 ベストプラクティス

#### PR作成時

```markdown
✅ やるべきこと:
- [ ] CI/CDが全てパスしていることを確認
- [ ] コンフリクトが解決されていることを確認
- [ ] セルフレビューを実施
- [ ] 適切なラベルを付与
- [ ] 関連Issueをリンク

❌ 避けるべきこと:
- CI/CD失敗状態でのレビュー依頼
- コンフリクト未解決でのマージ依頼
- 説明不足のPR
```

#### レビュー時

```markdown
✅ やるべきこと:
- [ ] コードの品質を確認
- [ ] テストカバレッジを確認
- [ ] セキュリティリスクを評価
- [ ] 建設的なフィードバック

❌ 避けるべきこと:
- CI/CD失敗状態での承認
- 不十分な理解での承認
- 形式的なレビュー
```

## 7. トラブルシューティング

### 7.1 マージできない場合

#### 問題: "Required status checks must pass"

```bash
原因: CI/CDチェックが失敗している

解決策:
1. GitHub ActionsのログでエラーChall詳細を確認
2. ローカルで同じチェックを実行
   pytest tests/
   ruff check .
   mypy .
3. エラーを修正
4. コミット・プッシュ
5. CI/CDの再実行を待つ
```

#### 問題: "This branch is out-of-date with the base branch"

```bash
原因: mainブランチが進んでいる

解決策:
git fetch origin
git rebase origin/main
# コンフリクトがあれば解決
git push --force-with-lease origin feature/xxx
```

#### 問題: "Review required"

```bash
原因: レビュー承認がない、または無効化された

解決策:
1. レビュアーに承認を依頼
2. 新しいコミットをプッシュした場合は再承認を依頼
```

### 7.2 CI/CDが失敗する場合

#### Lintエラー

```bash
# ローカルで確認
ruff check .

# 自動修正
ruff check --fix .

# 手動で修正が必要な場合
# エラーメッセージを確認して修正
```

#### 型チェックエラー

```bash
# ローカルで確認
mypy .

# 型ヒントを追加
def fetch_data(symbol: str) -> dict[str, Any]:
    ...
```

#### テストエラー

```bash
# ローカルで確認
pytest tests/ -v

# 失敗したテストを個別に実行
pytest tests/test_specific.py::test_function -v

# カバレッジ確認
pytest tests/ --cov --cov-report=html
```

## 8. まとめ

### 実現される保護

✅ **品質保証**
- コードレビューの徹底
- CI/CDによる自動チェック
- テストカバレッジの維持

✅ **セキュリティ**
- 直接プッシュの禁止
- レビュー後の変更に対する再確認
- 管理者にも同じルールを適用

✅ **安全性**
- 誤った変更の防止
- コンフリクトの事前解決
- 履歴の改変禁止

✅ **透明性**
- 全ての変更がPRを経由
- レビューコメントの記録
- 変更履歴の明確化

### 重要な原則

1. **全員が同じルールに従う** - 管理者も例外なし
2. **CI/CDの全パスが必須** - 品質基準の維持
3. **レビューの徹底** - コードの品質とセキュリティ
4. **コンフリクトは事前に解決** - マージの安全性
5. **緊急時でもプロセス遵守** - ホットフィックスブランチを使用

### 継続的な改善

- 定期的な設定の見直し（四半期ごと）
- チームからのフィードバック収集
- CI/CDチェックの追加・改善
- ドキュメントの更新

---

**関連ドキュメント:**
- [Git運用ワークフロー](./git_workflow.md)
- [GitHub運用ルール](./github_workflow.md)
- [テスト戦略](./testing_strategy.md)
- [コーディング規約](./coding_standards.md)

**参考資料:**
- [GitHub Branch Protection Documentation](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches/about-protected-branches)
- [GitHub Actions Documentation](https://docs.github.com/en/actions)

**バージョン:** 1.0.0
**最終更新:** 2025-10-22
**作成者:** Development Team
**Issue:** #113
