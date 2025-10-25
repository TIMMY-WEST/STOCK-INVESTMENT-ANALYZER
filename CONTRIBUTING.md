# プロジェクトへの貢献ガイド

STOCK-INVESTMENT-ANALYZERプロジェクトに興味を持っていただきありがとうございます。このドキュメントは、プロジェクトへの貢献方法を包括的に説明します。

## 目次

- [プロジェクトへの貢献ガイド](#プロジェクトへの貢献ガイド)
  - [目次](#目次)
  - [貢献方法](#貢献方法)
  - [開発フロー](#開発フロー)
  - [Issue作成ガイド](#issue作成ガイド)
  - [Pull Request（PR）作成ガイド](#pull-requestpr作成ガイド)
  - [コードレビュー基準](#コードレビュー基準)
  - [コーディング規約](#コーディング規約)
  - [テストガイドライン](#テストガイドライン)
  - [ドキュメント更新](#ドキュメント更新)
  - [行動規範（Code of Conduct）](#行動規範code-of-conduct)
  - [コミュニティガイドライン](#コミュニティガイドライン)
  - [開発環境のセットアップ](#開発環境のセットアップ)
  - [関連ドキュメント](#関連ドキュメント)
  - [ライセンス](#ライセンス)

---

## 貢献方法

STOCK-INVESTMENT-ANALYZERへの貢献を検討していただき、ありがとうございます。

### 歓迎する貢献の種類

私たちは、あらゆる形での貢献を歓迎しています：

- **コード貢献**
  - 新機能の実装
  - バグ修正
  - パフォーマンス改善
  - リファクタリング
  - テストの追加・改善

- **ドキュメント貢献**
  - README、ガイドの改善
  - コード内のコメント追加
  - APIドキュメントの作成
  - チュートリアルの作成

- **Issue報告**
  - バグ報告
  - 機能要望
  - ドキュメントの改善提案
  - 質問

- **レビュー**
  - コードレビュー
  - ドキュメントレビュー
  - Issue・PRへのコメント

### 初めての方へ

初めて貢献する方には、以下のラベルがついたIssueがおすすめです：

- `good first issue`: 初心者向けの簡単なタスク
- `help wanted`: コミュニティからの協力を歓迎しているタスク
- `documentation`: ドキュメント関連のタスク

まずは[README.md](README.md)と[開発環境セットアップガイド](#開発環境のセットアップ)を読んで、プロジェクトの概要と環境構築方法を理解してください。

---

## 開発フロー

このプロジェクトでは、**GitHub Flow**を採用しています。基本的な開発サイクルは以下の通りです：

```
1. Issue作成/確認
   ↓
2. ブランチ作成
   ↓
3. 実装・テスト
   ↓
4. コミット（Conventional Commits規約）
   ↓
5. プッシュ
   ↓
6. Pull Request作成
   ↓
7. コードレビュー
   ↓
8. 修正対応（必要に応じて）
   ↓
9. マージ
```

### ブランチ戦略

- **mainブランチ**: 本番環境にデプロイ可能な安定版コード
- **作業ブランチ**: 各Issue/タスクごとに作成するブランチ

```bash
# 最新のmainブランチを取得
git checkout main
git pull origin main

# 新しいブランチを作成
git checkout -b feature/issue-123-stock-api

# リモートブランチを作成
git push -u origin feature/issue-123-stock-api
```

### ブランチ命名規則

ブランチ名は以下の形式に従ってください：

```
{type}/{identifier}-{description}
```

**例**：
- `feature/issue-123-stock-api`
- `fix/issue-124-pagination-bug`
- `docs/update-readme`

### コミットメッセージ規約（Conventional Commits）

コミットメッセージは**Conventional Commits**規約に従ってください。

**基本フォーマット**：
```
<type>(<scope>): <subject>
```

**例**：
- `feat(api): 株価データ取得APIを追加`
- `fix(database): データベース接続エラーを修正`
- `docs(readme): セットアップ手順を更新`

詳細は[Git Workflow](docs/development/git_workflow.md)を参照してください。

---

## Issue作成ガイド

### Issue作成前の確認事項

1. **既存のIssueを確認**: 同じ内容のIssueが既に存在しないか検索
2. **ドキュメントを確認**: README.mdや関連する仕様書を確認
3. **再現可能性の確認**（バグの場合）: 最新のmainブランチで再現するか確認

### Issueテンプレートの使用

Issueを作成する際は、適切なテンプレートを使用してください：

- **[Feature Request](.github/ISSUE_TEMPLATE/feature_request.md)**: 新機能の提案
- **[Bug Report](.github/ISSUE_TEMPLATE/bug_report.md)**: バグ報告
- **[Question](.github/ISSUE_TEMPLATE/question.md)**: 質問
- **[Refactoring](.github/ISSUE_TEMPLATE/refactoring.md)**: リファクタリング提案

### ラベルの使い方

適切なラベルを付けることで、Issueの管理がしやすくなります：

- **優先度**: `priority:high`, `priority:medium`, `priority:low`
- **タスク種別**: `feature`, `bug`, `enhancement`, `documentation`
- **技術領域**: `backend`, `frontend`, `database`, `infrastructure`

---

## Pull Request（PR）作成ガイド

### PR作成前のセルフチェック

PRを作成する前に、以下の項目を確認してください：

#### コード品質
- [ ] Issue要件を満たしている
- [ ] コーディング規約に準拠している（PEP 8）
- [ ] 適切な型ヒントを追加している
- [ ] Docstringを記述している（Google スタイル）
- [ ] Lintエラーがない（Flake8, Pylint）
- [ ] Black, isortでフォーマット済み

#### テスト
- [ ] テストが実装され、全て通過している
- [ ] 既存のテストがすべて通過している

#### Git運用
- [ ] Conventional Commits規約に準拠している
- [ ] ブランチ命名規則に従っている
- [ ] 最新のmainブランチに追従している

### PRの説明の書き方

PRテンプレート（[.github/PULL_REQUEST_TEMPLATE.md](.github/PULL_REQUEST_TEMPLATE.md)）に従って、以下の情報を記載してください：

1. **概要**: 変更の目的と背景
2. **変更内容**: 主な変更点をリストアップ
3. **関連Issue**: `Closes #123`の形式で記載
4. **テスト方法**: 動作確認の手順
5. **レビュー観点**: レビュアーに特に注目してほしい点

---

## コードレビュー基準

### レビュー時の観点

レビュアーは以下の観点でコードをレビューします：

- **機能性**: Issue要件を満たしているか
- **コード品質**: コーディング規約に準拠しているか、可読性が高いか
- **セキュリティ**: セキュリティ上の問題がないか
- **パフォーマンス**: パフォーマンスに悪影響がないか
- **テスト**: テストが十分か
- **ドキュメント**: コメントやDocstringが適切か

### コメントの書き方

レビューコメントは、建設的で丁寧な表現を心がけてください。

**良いコメント例**：
```
この部分、エッジケース（値が0の場合）の処理を追加してはどうでしょうか？
```

---

## コーディング規約

本プロジェクトでは、**PEP 8**（Pythonの公式スタイルガイド）に準拠しています。

### 基本ルール

- **インデント**: スペース4つ
- **行の最大長**: 79文字
- **文字コード**: UTF-8
- **改行コード**: LF（Unix形式）

### 命名規則

```python
# クラス名: PascalCase
class StockDataFetcher:
    pass

# 関数名・変数名: snake_case
def fetch_stock_data(symbol: str) -> dict:
    user_count = 10
    return {}

# 定数: UPPER_CASE
MAX_RETRY_COUNT = 3
```

### コード品質チェックツール

以下のツールを使用して、コード品質を保ちます：

```bash
# Black（コードフォーマッター）
black app/ tests/

# isort（import文の整理）
isort app/ tests/

# Flake8（Linter）
flake8 app/ tests/

# Mypy（型チェック）
mypy app/
```

詳細は[Coding Standards](docs/development/coding_standards.md)を参照してください。

---

## テストガイドライン

### テストの種類

1. **単体テスト（Unit Test）**: 個々の関数・メソッドのテスト
2. **統合テスト（Integration Test）**: 複数のコンポーネント間の連携テスト
3. **E2Eテスト（End-to-End Test）**: APIエンドポイントのテスト

### テストの実行方法

```bash
# すべてのテストを実行
pytest

# 特定のテストファイルを実行
pytest tests/test_stock_data_fetcher.py

# カバレッジレポート付きで実行
pytest --cov=app --cov-report=html
```

### テストカバレッジ

- **目標**: 80%以上のカバレッジを維持
- 新しいコードには必ずテストを追加

詳細は[Testing Guide](docs/development/testing_guide.md)を参照してください。

---

## ドキュメント更新

以下のドキュメントを適切に更新してください：

1. **README.md**: プロジェクトの概要、セットアップ手順
2. **API仕様書**: APIエンドポイントの説明
3. **開発者向けドキュメント**: コーディング規約、Git運用ワークフロー
4. **アーキテクチャドキュメント**: システム構成、データベーススキーマ

---

## 行動規範（Code of Conduct）

### 私たちの約束

私たちは、全ての人にとって、ハラスメントフリーで包括的なコミュニティを作ることを約束します。

### 推奨される行動

- 歓迎的で包括的な言葉を使う
- 異なる視点や経験を尊重する
- 建設的な批判を受け入れる

### 禁止される行動

- 性的な言葉や画像の使用
- 荒らし行為、侮辱的・軽蔑的なコメント
- ハラスメント

### 違反時の対応

行動規範に違反する行動を目撃した場合は、プロジェクトメンテナーに報告してください。

---

## コミュニティガイドライン

### コミュニケーション方法

- **GitHub Issues**: バグ報告、機能要望、質問
- **Pull Request**: コードレビュー、実装の議論

### 質問の仕方

良い質問をすることで、迅速な回答が得られます：

1. **既存のIssueを検索**: 同じ質問が既にないか確認
2. **明確なタイトル**: 何について質問しているかが一目で分かる
3. **詳細な説明**: 環境情報、再現手順、エラーメッセージ
4. **コード例**: マークダウンのコードブロックを使用

---

## 開発環境のセットアップ

詳細な開発環境のセットアップ手順は、[README.md](README.md#クイックスタートガイド)を参照してください。

### クイックセットアップ

```bash
# リポジトリのクローン
git clone https://github.com/TIMMY-WEST/STOCK-INVESTMENT-ANALYZER.git
cd STOCK-INVESTMENT-ANALYZER

# 自動セットアップ（推奨）
# Linux/macOS
make setup
# Windows
scripts\setup\dev_setup.bat
```

---

## 関連ドキュメント

- **[README.md](README.md)**: プロジェクト概要とセットアップ
- **[GitHub Workflow](docs/development/github_workflow.md)**: 個人開発向けワークフロー
- **[Git Workflow](docs/development/git_workflow.md)**: 共同開発向けワークフロー
- **[Coding Standards](docs/development/coding_standards.md)**: コーディング規約
- **[Testing Guide](docs/development/testing_guide.md)**: テストガイドライン

---

## ライセンス

このプロジェクトに貢献することで、あなたの貢献がMITライセンスの下でライセンスされることに同意したものとみなされます。

---

**ご質問やご提案がありましたら、お気軽にIssueを作成してください。皆様の貢献をお待ちしています！**
