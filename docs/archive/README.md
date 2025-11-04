# アーカイブドキュメント

このディレクトリには、統合または廃止されたドキュメントが保管されています。

## 📅 アーカイブ日: 2025年11月2日

### ドキュメント構造再編成

以下のドキュメントは重複を排除し、統合されました:

#### テスト関連ドキュメント → `../standards/testing-standards.md` (v3.0.0)
- ❌ `testing_guide_deprecated_20251102.md`
- ❌ `testing_strategy_deprecated_20251102.md`
- ❌ `test_coverage_report_deprecated_20251102.md`
- ❌ `api_integration_testing_guide_deprecated_20251102.md`
- ❌ `existing_tests_deprecated_20251102.md`
- ❌ `test_refactoring_plan_deprecated_20251102.md`

#### CI/CD関連ドキュメント → `../ci-cd/pipeline-config.md` (v2.0.0)
- ❌ `pipeline_overview_deprecated_20251102.md`
- ❌ `ci-cd_troubleshooting_deprecated_20251102.md`

#### 開発ワークフロー関連ドキュメント → `../guides/development-workflow.md` (v2.0.0)
- ❌ `coding_standards_deprecated_20251102.md`
- ❌ `github_workflow_deprecated_20251102.md`
- ❌ `git_workflow_deprecated_20251102.md`
- ❌ `branch_protection_rules_deprecated_20251102.md`
- ❌ `code_review_guide_deprecated_20251102.md`

#### その他
- 📋 `test_removal_log_20251102.md` (履歴記録として保存)

## 🔍 統合ドキュメント一覧

### 標準仕様 (`standards/`)
- [テスト標準仕様書](../standards/testing-standards.md) - テスト戦略・ベストプラクティス・カバレッジ目標
- [コーディング規約](../standards/coding-standards.md) - Pythonコーディング標準
- [Git運用ワークフロー](../standards/git-workflow.md) - ブランチ戦略・PR作成

### 運用ガイド (`guides/`)
- [開発ワークフロー](../guides/development-workflow.md) - Issue→Deploy全工程
- [トラブルシューティング](../guides/troubleshooting.md) - 問題解決・FAQ

### CI/CD (`ci-cd/`)
- [パイプライン設定ガイド](../ci-cd/pipeline-config.md) - GitHub Actions・Pre-commit設定

## ⚠️ 注意事項

このディレクトリのドキュメントは**非推奨**です。各ファイルの先頭に代替ドキュメントへのリンクが記載されています。

新しい開発では、必ず統合された最新ドキュメントを参照してください。
---
**このアーカイブに関する質問は、GitHubのIssueで受け付けています。**
