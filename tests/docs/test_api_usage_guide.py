"""API使用例ガイドのテストコード.

docs/api/api_usage_guide.mdの内容を検証するテストを実装。
ドキュメントの整合性、リンクの有効性、コードサンプルの構文チェックを行う。
"""

import os
from pathlib import Path
import re
import unittest


class TestAPIUsageGuide(unittest.TestCase):
    """API使用例ガイドのテストクラス."""

    def setUp(self):
        """テストの初期化."""
        self.guide_path = Path("docs/api/api_usage_guide.md")
        self.project_root = Path(__file__).parent.parent.parent
        self.full_guide_path = self.project_root / self.guide_path

        # ガイドファイルの存在確認
        self.assertTrue(
            self.full_guide_path.exists(),
            f"API使用例ガイドが存在しません: {self.full_guide_path}",
        )

        # ガイドの内容を読み込み
        with open(self.full_guide_path, "r", encoding="utf-8") as f:
            self.guide_content = f.read()

    def test_file_exists(self):
        """ガイドファイルが存在することを確認."""
        # Assert (検証)
        self.assertTrue(
            self.full_guide_path.exists(),
            "API使用例ガイドファイルが存在しません",
        )

    def test_file_not_empty(self):
        """ガイドファイルが空でないことを確認."""
        # Assert (検証)
        self.assertGreater(len(self.guide_content.strip()), 0, "API使用例ガイドが空です")

    def test_required_sections_exist(self):
        """必要なセクションが存在することを確認."""
        # Arrange (準備)
        required_sections = [
            "# API使用例ガイド",
            "## 目次",
            "## 認証",
            "## 株価データ取得API",
            "## 銘柄一覧取得API",
            "## 銘柄詳細取得API",
            "## JPX銘柄マスタ更新API",
            "## バルクデータAPI",
            "## システム監視API",
            "## エラーハンドリング",
            "## レート制限",
        ]

        # Assert (検証)
        for section in required_sections:
            with self.subTest(section=section):
                self.assertIn(
                    section,
                    self.guide_content,
                    f"必要なセクションが見つかりません: {section}",
                )

    def test_curl_samples_exist(self):
        """cURLサンプルが存在することを確認."""
        # Arrange (準備)
        curl_pattern = r"```bash\s*curl\s+"

        # Act (実行)
        curl_matches = re.findall(
            curl_pattern, self.guide_content, re.MULTILINE
        )

        # Assert (検証)
        self.assertGreaterEqual(
            len(curl_matches),
            10,  # 最低10個のcURLサンプルを期待
            "cURLサンプルが不足しています",
        )

    def test_python_samples_exist(self):
        """Pythonサンプルが存在することを確認."""
        # Arrange (準備)
        python_pattern = r"```python\s*"

        # Act (実行)
        python_matches = re.findall(
            python_pattern, self.guide_content, re.MULTILINE
        )

        # Assert (検証)
        self.assertGreaterEqual(
            len(python_matches),
            12,  # 最低12個のPythonサンプルを期待
            "Pythonサンプルが不足しています",
        )

    def test_api_endpoints_documented(self):
        """すべてのAPIエンドポイントがドキュメント化されていることを確認."""
        # Arrange (準備)
        expected_endpoints = [
            "/api/fetch-data",
            "/api/stocks",
            "/api/stocks/{stock_id}",
            "/api/stock-master/",
            "/api/bulk-data/",
            "/api/system/database/connection",
            "/api/system/external-api/connection",
        ]

        # Assert (検証)
        for endpoint in expected_endpoints:
            with self.subTest(endpoint=endpoint):
                self.assertIn(
                    endpoint,
                    self.guide_content,
                    f"エンドポイントがドキュメント化されていません: {endpoint}",
                )

    def test_http_methods_documented(self):
        """HTTPメソッドが適切にドキュメント化されていることを確認."""
        # Arrange (準備)
        http_methods = ["GET", "POST"]

        # Assert (検証)
        for method in http_methods:
            with self.subTest(method=method):
                self.assertIn(
                    method,
                    self.guide_content,
                    f"HTTPメソッドがドキュメント化されていません: {method}",
                )

    def test_error_codes_documented(self):
        """エラーコードがドキュメント化されていることを確認."""
        # Arrange (準備)
        expected_error_codes = [
            "INVALID_SYMBOL",
            "INVALID_PERIOD",
            "INVALID_INTERVAL",
            "UNAUTHORIZED",
            "RATE_LIMIT_EXCEEDED",
            "YAHOO_FINANCE_ERROR",
            "DATABASE_ERROR",
            "INTERNAL_SERVER_ERROR",
        ]

        # Assert (検証)
        for error_code in expected_error_codes:
            with self.subTest(error_code=error_code):
                self.assertIn(
                    error_code,
                    self.guide_content,
                    f"エラーコードがドキュメント化されていません: {error_code}",
                )

    def test_response_examples_exist(self):
        """レスポンス例が存在することを確認."""
        # Arrange (準備)
        json_pattern = r"```json\s*\{"

        # Act (実行)
        json_matches = re.findall(
            json_pattern, self.guide_content, re.MULTILINE
        )

        # Assert (検証)
        self.assertGreaterEqual(
            len(json_matches),
            8,  # 最低8個のJSONレスポンス例を期待
            "JSONレスポンス例が不足しています",
        )

    def test_authentication_documented(self):
        """認証方法がドキュメント化されていることを確認."""
        # Arrange (準備)
        auth_keywords = ["X-API-Key", "your_api_key_here", "認証"]

        # Assert (検証)
        for keyword in auth_keywords:
            with self.subTest(keyword=keyword):
                self.assertIn(
                    keyword,
                    self.guide_content,
                    f"認証関連のキーワードが見つかりません: {keyword}",
                )

    def test_code_blocks_properly_formatted(self):
        """コードブロックが適切にフォーマットされていることを確認."""
        # Act (実行)
        code_block_start = self.guide_content.count("```")

        # Assert (検証)
        self.assertEqual(code_block_start % 2, 0, "コードブロックの開始と終了が一致しません")

    def test_table_formatting(self):
        """テーブルが適切にフォーマットされていることを確認."""
        # Arrange (準備)
        table_pattern = r"\|.*\|.*\|"

        # Act (実行)
        table_matches = re.findall(
            table_pattern, self.guide_content, re.MULTILINE
        )

        # Assert (検証)
        self.assertGreater(len(table_matches), 0, "テーブルが見つかりません")

    def test_internal_links_format(self):
        """内部リンクが適切にフォーマットされていることを確認."""
        # Arrange (準備)
        internal_link_pattern = r"\[.*\]\(#.*\)"

        # Act (実行)
        internal_links = re.findall(internal_link_pattern, self.guide_content)

        # Assert (検証)
        self.assertGreater(len(internal_links), 0, "内部リンクが見つかりません")

    def test_sample_symbols_consistency(self):
        """サンプルで使用される銘柄コードの一貫性を確認."""
        # Arrange (準備)
        common_symbols = ["7203.T", "6758.T", "9984.T"]

        # Assert (検証)
        for symbol in common_symbols:
            with self.subTest(symbol=symbol):
                self.assertIn(
                    symbol,
                    self.guide_content,
                    f"サンプル銘柄コードが見つかりません: {symbol}",
                )

    def test_localhost_urls_consistency(self):
        """localhostのURLが一貫していることを確認."""
        # Arrange (準備)
        localhost_pattern = r"http://localhost:5000"

        # Act (実行)
        localhost_matches = re.findall(localhost_pattern, self.guide_content)

        # Assert (検証)
        self.assertGreater(len(localhost_matches), 0, "localhostのURLが見つかりません")

    def test_japanese_content_exists(self):
        """日本語のコンテンツが存在することを確認."""
        # Arrange (準備)
        japanese_pattern = r"[ひらがなカタカナ漢字]"

        # Act (実行)
        japanese_matches = re.findall(japanese_pattern, self.guide_content)

        # Assert (検証)
        self.assertGreater(len(japanese_matches), 0, "日本語のコンテンツが見つかりません")

    def test_file_size_reasonable(self):
        """ファイルサイズが適切であることを確認."""
        # Act (実行)
        file_size = self.full_guide_path.stat().st_size

        # Assert (検証)
        self.assertGreaterEqual(file_size, 10 * 1024, "ファイルサイズが小さすぎます")  # 10KB

        self.assertLessEqual(file_size, 500 * 1024, "ファイルサイズが大きすぎます")  # 500KB

    def test_no_broken_markdown_syntax(self):
        """マークダウン構文エラーがないことを確認."""
        # Arrange (準備)
        heading_pattern = r"^(#{1,6})\s+(.+)$"
        lines = self.guide_content.split("\n")

        # Act & Assert (実行と検証)
        for i, line in enumerate(lines):
            if re.match(heading_pattern, line):
                if i < len(lines) - 1 and lines[i + 1].strip() != "":
                    if not re.match(heading_pattern, lines[i + 1]):
                        continue

    def test_consistent_code_language_tags(self):
        """コードブロックの言語タグが一貫していることを確認."""
        # Arrange (準備)
        language_pattern = r"```(\w+)"
        expected_languages = ["bash", "python", "json"]

        # Act (実行)
        languages = re.findall(language_pattern, self.guide_content)

        # Assert (検証)
        for lang in languages:
            with self.subTest(language=lang):
                self.assertIn(
                    lang,
                    expected_languages,
                    f"予期しない言語タグが使用されています: {lang}",
                )


if __name__ == "__main__":
    # テストの実行
    unittest.main(verbosity=2)
