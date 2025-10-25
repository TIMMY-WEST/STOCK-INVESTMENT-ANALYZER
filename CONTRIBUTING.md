# コントリビューションガイド

STOCK-INVESTMENT-ANALYZERプロジェクトへの貢献にご興味をお持ちいただき、ありがとうございます！このガイドでは、プロジェクトに効果的に貢献するための手順とガイドラインを説明します。

## 📋 目次

- [貢献の種類](#貢献の種類)
- [開発環境のセットアップ](#開発環境のセットアップ)
- [開発ワークフロー](#開発ワークフロー)
- [コーディング規約](#コーディング規約)
- [テストガイドライン](#テストガイドライン)
- [Pull Requestガイドライン](#pull-requestガイドライン)
- [Issue報告ガイドライン](#issue報告ガイドライン)
- [コミュニティガイドライン](#コミュニティガイドライン)

## 貢献の種類

### 1. バグ報告
- バグの発見と詳細な報告
- 再現手順の提供
- 環境情報の共有

### 2. 機能要望
- 新機能のアイデア提案
- 既存機能の改善提案
- ユーザビリティの向上提案

### 3. コード貢献
- バグ修正
- 新機能の実装
- パフォーマンス改善
- リファクタリング

### 4. ドキュメント改善
- README.mdの改善
- API仕様書の更新
- コメントの追加・改善
- 使用例の追加

### 5. テスト追加
- ユニットテストの追加
- 統合テストの追加
- テストカバレッジの向上

## 🛠️ 開発環境のセットアップ

### 前提条件
- Python 3.8以上
- PostgreSQL 12以上
- Git

## 開発環境のセットアップ

### セットアップ手順

1. **リポジトリのフォーク**
   ```bash
   # GitHubでリポジトリをフォーク後
   git clone https://github.com/YOUR_USERNAME/STOCK-INVESTMENT-ANALYZER.git
   cd STOCK-INVESTMENT-ANALYZER
   ```

2. **上流リポジトリの追加**
   ```bash
   git remote add upstream https://github.com/TIMMY-WEST/STOCK-INVESTMENT-ANALYZER.git
   ```

3. **開発環境の構築**
   ```bash
   # 自動セットアップ（推奨）
   make setup  # Linux/macOS
   scripts\setup\dev_setup.bat  # Windows
   ```

4. **開発用依存関係のインストール**
   ```bash
   pip install -r requirements-dev.txt
   ```

## 開発ワークフロー

### ブランチ戦略

プロジェクトでは以下のブランチ命名規則を使用します：

```
{type}/{identifier}-{description}
```

**Type:**
- `feature/` - 新機能
- `fix/` - バグ修正
- `refactor/` - リファクタリング
- `docs/` - ドキュメント更新
- `test/` - テスト追加
- `chore/` - その他の作業

**例:**
- `feature/issue-123-add-real-time-data`
- `fix/issue-456-database-connection-error`
- `docs/update-api-documentation`

### 開発手順

1. **最新のmainブランチを取得**
   ```bash
   git checkout main
   git pull upstream main
   ```

2. **機能ブランチを作成**
   ```bash
   git checkout -b feature/issue-123-your-feature-name
   ```

3. **開発とテスト**
   ```bash
   # 開発作業
   # テスト実行
   make test

   # コードフォーマット
   make format

   # リンター実行
   make lint
   ```

4. **コミット**
   ```bash
   git add .
   git commit -m "feat(api): 新機能の実装"
   ```

5. **プッシュとPull Request**
   ```bash
   git push origin feature/issue-123-your-feature-name
   # GitHubでPull Requestを作成
   ```

## 📝 コーディング規約

### Python コーディングスタイル

- **PEP 8** に準拠
- **Black** を使用したコードフォーマット
- **isort** を使用したインポート整理

```bash
# フォーマット実行
make format

# または個別実行
black .
isort .
```

### コメントとドキュメント

```python
def fetch_stock_data(symbol: str, period: str = "1d") -> Dict[str, Any]:
    """
    指定された銘柄の株価データを取得する

    Args:
        symbol (str): 銘柄コード（例: "7203.T"）
        period (str): 取得期間（デフォルト: "1d"）

    Returns:
        Dict[str, Any]: 株価データ辞書

    Raises:
        ValueError: 無効な銘柄コードの場合
        ConnectionError: API接続エラーの場合
    """
    # 実装内容...
```

### 命名規則

- **関数・変数**: snake_case
- **クラス**: PascalCase
- **定数**: UPPER_SNAKE_CASE
- **プライベート**: 先頭にアンダースコア

```python
# 良い例
class StockDataFetcher:
    MAX_RETRY_COUNT = 3

    def __init__(self):
        self._api_client = None

    def fetch_daily_data(self, symbol: str) -> dict:
        pass
```

## 🧪 テストガイドライン

### テスト実行

```bash
# 全テスト実行
make test

# カバレッジ付きテスト
make test-cov

# 特定のテストファイル
pytest tests/test_stock_fetcher.py

# 特定のテスト関数
pytest tests/test_stock_fetcher.py::test_fetch_valid_symbol
```

### テスト作成ガイドライン

1. **テストファイル命名**: `test_*.py`
2. **テスト関数命名**: `test_*`
3. **AAA パターン**: Arrange, Act, Assert

```python
def test_fetch_stock_data_success():
    # Arrange
    fetcher = StockDataFetcher()
    symbol = "7203.T"

    # Act
    result = fetcher.fetch_stock_data(symbol)

    # Assert
    assert result is not None
    assert "symbol" in result
    assert result["symbol"] == symbol
```

### テストカバレッジ

- **最低カバレッジ**: 80%以上
- **新機能**: 90%以上のカバレッジを目標

## 📋 Pull Requestガイドライン

### PR作成前のチェックリスト

- [ ] 最新のmainブランチからブランチを作成
- [ ] 全テストが通過
- [ ] コードフォーマットが適用済み
- [ ] リンターエラーがない
- [ ] 適切なコミットメッセージ
- [ ] 関連Issueがリンク済み

### PRテンプレート

Pull Requestを作成する際は、以下の情報を含めてください：

```markdown
## 概要
このPRの目的と変更内容を簡潔に説明

## 変更内容
- [ ] 新機能の追加
- [ ] バグ修正
- [ ] リファクタリング
- [ ] ドキュメント更新
- [ ] テスト追加

## 関連Issue
Closes #123

## テスト
- [ ] 新しいテストを追加
- [ ] 既存のテストが全て通過
- [ ] 手動テストを実施

## スクリーンショット（UI変更の場合）
変更前後のスクリーンショットを添付

## 追加情報
レビュアーが知っておくべき追加情報
```

### レビュープロセス

1. **自動チェック**: CI/CDによる自動テスト
2. **コードレビュー**: メンテナーによるレビュー
3. **修正対応**: 指摘事項への対応
4. **マージ**: 承認後のマージ

## 🐛 Issue報告ガイドライン

### バグ報告

バグを発見した場合は、以下の情報を含めて報告してください：

```markdown
## バグの概要
バグの簡潔な説明

## 再現手順
1. 手順1
2. 手順2
3. 手順3

## 期待される動作
正常に動作した場合の期待される結果

## 実際の動作
実際に発生した問題

## 環境情報
- OS: Windows 10 / macOS Big Sur / Ubuntu 20.04
- Python: 3.9.0
- PostgreSQL: 13.0
- ブラウザ: Chrome 95.0

## 追加情報
- エラーログ
- スクリーンショット
- その他の関連情報
```

### 機能要望

新機能の要望は以下の形式で報告してください：

```markdown
## 機能の概要
提案する機能の簡潔な説明

## 背景・動機
なぜこの機能が必要なのか

## 提案する解決策
具体的な実装案や動作イメージ

## 代替案
他に考えられる解決方法

## 追加情報
- 参考資料
- モックアップ
- 類似機能の例
```

## 🌟 コミュニティガイドライン

### 行動規範

1. **尊重**: 全ての参加者を尊重する
2. **建設的**: 建設的なフィードバックを提供する
3. **協力的**: チームワークを重視する
4. **学習志向**: 学習と成長を促進する

### コミュニケーション

- **日本語**: 主要なコミュニケーション言語
- **英語**: 国際的な貢献者との交流
- **丁寧語**: 敬意を持った言葉遣い

### 質問とサポート

- **GitHub Issues**: バグ報告・機能要望
- **GitHub Discussions**: 一般的な質問・議論
- **Wiki**: 詳細な技術情報

## 🎯 貢献のヒント

### 初心者向け

1. **Good First Issue**: 初心者向けのラベルが付いたIssueから始める
2. **ドキュメント**: ドキュメントの改善から始める
3. **テスト**: 既存機能のテスト追加から始める

### 効果的な貢献

1. **小さなPR**: 大きな変更は小さなPRに分割
2. **明確な説明**: 変更の理由と方法を明確に説明
3. **継続的な改善**: 段階的な改善を心がける

## 📞 サポート

質問や不明な点がある場合は、以下の方法でお気軽にお問い合わせください：

- **GitHub Issues**: [新しいIssueを作成](https://github.com/TIMMY-WEST/STOCK-INVESTMENT-ANALYZER/issues/new)
- **GitHub Discussions**: [ディスカッションに参加](https://github.com/TIMMY-WEST/STOCK-INVESTMENT-ANALYZER/discussions)

---

**ご協力いただき、ありがとうございます！** 🙏

あなたの貢献により、STOCK-INVESTMENT-ANALYZERはより良いプロジェクトになります。
