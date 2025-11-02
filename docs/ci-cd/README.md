# CI/CD パイプライン

株価投資分析システムの継続的インテグレーション/デプロイメント（CI/CD）に関するドキュメント集です。

## 📚 ドキュメント一覧

### パイプライン設定

#### [CI/CDパイプライン設定ガイド](./pipeline-config.md) ⚙️
**対象**: 開発者全員、DevOps担当

GitHub ActionsとPre-commitフックの完全な設定ガイドです。

**含まれる内容:**
- GitHub Actions ワークフロー全体像
- Pre-commit フック設定
  - Black（コードフォーマット）
  - isort（インポート整理）
  - flake8（コード品質チェック）
- CI パイプラインの段階別実行内容
- トラブルシューティング
- 設定ファイルの詳細解説

**こんな時に使用:**
- CI/CDパイプラインを理解したい時
- Pre-commitフックをセットアップする時
- GitHub Actionsのエラーを解決したい時
- パイプライン設定を変更したい時

---

#### [Pre-commitセットアップガイド](./pre_commit_setup.md) 🪝
**対象**: 開発者全員

Pre-commitフックの詳細なセットアップと使用方法です。

**含まれる内容:**
- Pre-commitフックの詳細設定
- 各ツールのカスタマイズ方法
- トラブルシューティング
- 実践的な使用例
- ベストプラクティス

**こんな時に使用:**
- Pre-commitフックを初めてセットアップする時
- Pre-commit設定をカスタマイズしたい時
- Pre-commitエラーを解決する時
- フックの動作を詳しく理解したい時

---

## 🗺️ CI/CDパイプラインの全体像

### Pre-commit フック（ローカル実行）

コミット前に自動実行されます:

```
コミット実行
  ↓
1. Black（コードフォーマット）
  ↓
2. isort（インポート整理）
  ↓
3. flake8（Linter）
  ↓
コミット成功 or 修正が必要
```

### GitHub Actions（リモート実行）

PRやプッシュ時に自動実行されます:

```
PR作成/プッシュ
  ↓
1. Lint & Format Check
   - Black チェック
   - isort チェック
   - flake8 実行
  ↓
2. Type Check
   - mypy 実行
  ↓
3. Tests
   - pytest 実行
   - カバレッジ測定（70%以上）
  ↓
全てパス → マージ可能
```

---

## 🎯 開発フロー別利用ガイド

### 初回セットアップ

```bash
# Pre-commitフックのインストール
pip install pre-commit
pre-commit install

# 全ファイルに対して実行（初回のみ）
pre-commit run --all-files
```

詳細: [パイプライン設定ガイド](./pipeline-config.md) の「Pre-commit設定」

### コミット前の確認

Pre-commitフックが自動実行されますが、手動で確認も可能:

```bash
# フォーマット確認
black . --check
isort . --check-only

# Linter実行
flake8 .
```

エラーがある場合は自動修正:

```bash
# 自動修正
black .
isort .
```

### PR作成前の確認

ローカルで全チェックを実行:

```bash
# すべてのチェックを一度に実行
black . && isort . && flake8 . && mypy app && pytest --cov=app --cov-report=term-missing
```

### CI/CDエラーの対応

GitHub ActionsでCIが失敗した場合:

1. **[パイプライン設定ガイド](./pipeline-config.md)** のトラブルシューティングセクションを確認
2. エラーログから該当するエラーを特定
3. ローカルで同じコマンドを実行して再現
4. 修正してコミット＆プッシュ

---

## 🔗 関連ドキュメント

### 開発標準
- [テスト標準仕様書](../standards/testing-standards.md) - テスト戦略とカバレッジ
- [コーディング規約](../standards/coding-standards.md) - コーディングスタイル
- [Git運用ワークフロー](../standards/git-workflow.md) - ブランチ戦略とコミット規約

### ガイド
- [開発ワークフロー](../guides/development-workflow.md) - Issue→Deploy全工程
- [トラブルシューティング](../guides/troubleshooting.md) - 問題解決ガイド
- [セットアップガイド](../guides/setup_guide.md) - 開発環境構築

---

## 🚀 クイックスタート

### Pre-commitフックのセットアップ（5分）

```bash
# 1. pre-commitのインストール
pip install pre-commit

# 2. Git hookとして登録
pre-commit install

# 3. 動作確認
pre-commit run --all-files
```

これで、以降のコミット時に自動的にコード品質チェックが実行されます！

### CI/CD設定ファイルの場所

- **GitHub Actions**: `.github/workflows/ci.yml`
- **Pre-commit設定**: `.pre-commit-config.yaml`
- **pytest設定**: `pytest.ini`
- **flake8設定**: `.flake8` または `setup.cfg`
- **mypy設定**: `mypy.ini` または `setup.cfg`

---

## 📊 品質基準

### コード品質
- **Black**: 行長79文字以内、PEP 8準拠
- **isort**: インポートが正しく整理されている
- **flake8**: エラーゼロ

### 型チェック
- **mypy**: 主要な関数に型ヒント付与

### テスト
- **pytest**: 全テスト成功
- **カバレッジ**: 70%以上（現在69%）

すべての基準をクリアしないとPRはマージできません。

---

## 📝 ドキュメント更新履歴

### 2025-11-02
- ✅ CI/CDパイプライン設定ガイドを統合作成（v2.0.0）
  - `pipeline_overview.md` と `troubleshooting.md` を統合
- ✅ 新しいディレクトリ構造（ci-cd/）を導入
- ✅ ナビゲーションREADMEを追加

### 過去の更新
- 2025-10-24: パイプライン概要の初版作成

---

## ❓ よくある質問

### Q: Pre-commitフックは必須ですか？

**A:** 強く推奨します。ローカルでコード品質を担保することで、CI/CDパイプラインでのエラーを防ぎ、開発効率が向上します。

### Q: Pre-commitフックをスキップできますか？

**A:** 緊急時のみ `git commit --no-verify` でスキップ可能ですが、その後必ずフォーマットを修正してください。通常はスキップしないでください。

### Q: GitHub Actionsでエラーが出ました

**A:** [パイプライン設定ガイド](./pipeline-config.md) の「トラブルシューティング」セクションを確認してください。主なエラーとその解決方法が記載されています。

### Q: カバレッジが70%未満でもマージできますか？

**A:** 原則としてマージできません。既存のカバレッジを下げないように、新機能には必ずテストを追加してください。詳細は [テスト標準仕様書](../standards/testing-standards.md) を参照してください。

### Q: CIの実行時間が長いです

**A:** 将来的にキャッシュやマトリックス実行を導入して高速化を予定しています。現在の実行時間は約5-10分です。

---

## 🔧 CI/CD改善提案

現在検討中の改善項目:

- [ ] Dependabot導入（依存パッケージの自動更新）
- [ ] キャッシュ戦略の最適化
- [ ] マトリックス実行（複数Pythonバージョンのテスト）
- [ ] デプロイ自動化
- [ ] ステージング環境へのCD

改善提案は、GitHubのIssueで受け付けています。

---

## 🐛 問題が発生した場合

1. **[パイプライン設定ガイド](./pipeline-config.md)** のトラブルシューティングセクションを確認
2. **エラーログ**から該当するエラーを特定
3. **ローカルで再現**して原因を特定
4. それでも解決しない場合は **GitHubのIssue** で質問

---

## 📬 フィードバック

CI/CD設定の改善提案やバグ報告は、GitHubのIssueまたはPull Requestでお願いします。

---

**最終更新**: 2025-11-02
