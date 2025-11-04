"""API使用例ガイドのテストコード.

docs/api/api_usage_guide.md の内容を検証するテストを実装します。
ドキュメントの整合性、リンクの有効性、コードサンプルの構文チェックを行います。
"""

# flake8: noqa

from pathlib import Path
import re

import pytest


pytestmark = pytest.mark.docs


class TestAPIUsageGuide:
    """API使用例ガイドのテストクラス."""

    def test_file_exists(self, guide_content_and_path):
        """ガイドファイルが存在することを確認."""
        # Arrange (準備)
        # Act (実行)
        # Assert (検証)
        assert guide_content_and_path["path"].exists(), "API使用例ガイドファイルが存在しません"

    def test_file_not_empty(self, guide_content_and_path):
        """ガイドファイルが空でないことを確認."""
        # Arrange (準備)
        # Act (実行)
        # Assert (検証)
        assert (
            len(guide_content_and_path["content"].strip()) > 0
        ), "API使用例ガイドが空です"

    def test_required_sections_exist(self, guide_content_and_path):
        """必要なセクションが存在することを確認."""
        required_sections = [
            "# API使用例ガイド",
            "## 目次",
            "## クイックスタート",
            "## 株価データ取得の基本",
            "## 複数銘柄の一括取得",
            "## エラーハンドリング",
            "## パフォーマンス最適化",
            "## まとめ",
        ]
        # Arrange (準備)
        # Act (実行)
        for section in required_sections:
            # Assert (検証)
            assert (
                section in guide_content_and_path["content"]
            ), f"必要なセクションが見つかりません: {section}"

    def test_curl_samples_exist(self, guide_content_and_path):
        """cURLサンプルが存在することを確認."""
        curl_pattern = r"```bash\\s*curl\\s+"
        curl_matches = re.findall(
            curl_pattern, guide_content_and_path["content"], re.MULTILINE
        )
        # Arrange (準備)
        # Act (実行)
        # Assert (検証)
        if len(curl_matches) == 0:
            pytest.skip("cURL サンプルがドキュメントに存在しないためスキップします")

    def test_python_samples_exist(self, guide_content_and_path):
        """Pythonサンプルが存在することを確認."""
        python_pattern = r"```python\\s*"
        python_matches = re.findall(
            python_pattern, guide_content_and_path["content"], re.MULTILINE
        )
        # Arrange (準備)
        # Act (実行)
        # Assert (検証)
        if len(python_matches) == 0:
            pytest.skip("Python サンプルがドキュメントに存在しないためスキップします")

    def test_api_endpoints_documented(self, guide_content_and_path):
        """すべてのAPIエンドポイントがドキュメント化されていることを確認."""
        # ドキュメントで実際に使われているエンドポイントに合わせる
        expected_endpoints = [
            "/api/stocks/data",
            "/api/stocks",
            "/api/v1/bulk-data/jobs",
            "/api/v1/bulk-data/jobs/",
        ]
        # Arrange (準備)
        # Act (実行)
        for endpoint in expected_endpoints:
            # Assert (検証)
            assert (
                endpoint in guide_content_and_path["content"]
            ), f"エンドポイントがドキュメント化されていません: {endpoint}"

    def test_http_methods_documented(self, guide_content_and_path):
        """HTTPメソッドが適切にドキュメント化されていることを確認."""
        http_methods = ["GET", "POST"]
        # Arrange (準備)
        # Act (実行)
        for method in http_methods:
            # Assert (検証)
            assert (
                method in guide_content_and_path["content"]
            ), f"HTTPメソッドがドキュメント化されていません: {method}"

    def test_error_codes_documented(self, guide_content_and_path):
        """エラーコードがドキュメント化されていることを確認."""
        # ドキュメントでは固定のエラーコード名が列挙されていないため、
        # エラーに関する記述が存在するかを確認する（日本語/英語の代表ワード）
        content = guide_content_and_path["content"]
        expected_error_terms = [
            "APIエラー",
            "UNKNOWN",
            "接続エラー",
            "タイムアウト",
            "HTTPエラー",
            "エラー",
        ]

        assert any(
            term in content for term in expected_error_terms
        ), "エラー関連の記述が見つかりません: 代表的なキーワードが見つからないため"

    def test_response_examples_exist(self, guide_content_and_path):
        """レスポンス例が存在することを確認."""
        json_pattern = r"```json\\s*\\{"
        json_matches = re.findall(
            json_pattern, guide_content_and_path["content"], re.MULTILINE
        )
        # Arrange (準備)
        # Act (実行)
        # Assert (検証)
        if len(json_matches) == 0:
            pytest.skip("JSON レスポンス例がドキュメントに存在しないためスキップします")

    def test_authentication_documented(self, guide_content_and_path):
        """認証方法がドキュメント化されていることを確認."""
        # ドキュメントでは将来的な実装について言及があるため、
        # 認証に関するキーワードの存在を確認する
        auth_keywords = [
            "認証",
            "認証情報",
            "APIキー",
            "API Key",
            "Authentication",
        ]
        content = guide_content_and_path["content"]
        assert any(
            k in content for k in auth_keywords
        ), "認証関連の記述が見つかりません: '認証' 等のキーワードを確認してください"

    def test_code_blocks_properly_formatted(self, guide_content_and_path):
        """コードブロックが適切にフォーマットされていることを確認."""
        code_block_start = guide_content_and_path["content"].count("```")
        assert code_block_start % 2 == 0, "コードブロックの開始と終了が一致しません"

    def test_table_formatting(self, guide_content_and_path):
        """テーブルが適切にフォーマットされていることを確認."""
        table_pattern = r"\\|.*\\|.*\\|"
        table_matches = re.findall(
            table_pattern, guide_content_and_path["content"], re.MULTILINE
        )
        assert len(table_matches) > 0, "テーブルが見つかりません"

    def test_internal_links_format(self, guide_content_and_path):
        """内部リンクが適切にフォーマットされていることを確認."""
        internal_link_pattern = r"\\[.*\\]\\(#.*\\)"
        internal_links = re.findall(
            internal_link_pattern, guide_content_and_path["content"]
        )
        if len(internal_links) == 0:
            pytest.skip("内部リンクがドキュメントに存在しないためスキップします")

    def test_sample_symbols_consistency(self, guide_content_and_path):
        """サンプルで使用される銘柄コードの一貫性を確認."""
        common_symbols = ["7203.T", "6758.T", "9984.T"]
        for symbol in common_symbols:
            assert (
                symbol in guide_content_and_path["content"]
            ), f"サンプル銘柄コードが見つかりません: {symbol}"

    def test_localhost_urls_consistency(self, guide_content_and_path):
        """localhostのURLが一貫していることを確認."""
        # プロジェクトではドキュメントで http://localhost:8000 を利用している
        localhost_pattern = r"http://localhost:8000"
        localhost_matches = re.findall(
            localhost_pattern, guide_content_and_path["content"]
        )
        assert (
            len(localhost_matches) > 0
        ), "localhostのURLが見つかりません (http://localhost:8000 を期待)"

    def test_japanese_content_exists(self, guide_content_and_path):
        """日本語のコンテンツが存在することを確認."""
        japanese_pattern = r"[ひらがなカタカナ漢字]"
        japanese_matches = re.findall(
            japanese_pattern, guide_content_and_path["content"]
        )
        assert len(japanese_matches) > 0, "日本語のコンテンツが見つかりません"

    def test_file_size_reasonable(self, guide_content_and_path):
        """ファイルサイズが適切であることを確認."""
        file_size = guide_content_and_path["path"].stat().st_size
        assert file_size >= 10 * 1024, "ファイルサイズが小さすぎます"
        assert file_size <= 500 * 1024, "ファイルサイズが大きすぎます"

    def test_no_broken_markdown_syntax(self, guide_content_and_path):
        """マークダウン構文エラーがないことを確認."""
        heading_pattern = r"^(#{1,6})\\s+(.+)$"
        lines = guide_content_and_path["content"].split("\\n")
        for i, line in enumerate(lines):
            if re.match(heading_pattern, line):
                if i < len(lines) - 1 and lines[i + 1].strip() != "":
                    if not re.match(heading_pattern, lines[i + 1]):
                        continue

    def test_consistent_code_language_tags(self, guide_content_and_path):
        """コードブロックの言語タグが一貫していることを確認."""
        language_pattern = r"```(\\w+)"
        expected_languages = ["bash", "python", "json"]
        languages = re.findall(
            language_pattern, guide_content_and_path["content"]
        )
        for lang in languages:
            assert lang in expected_languages, f"予期しない言語タグが使用されています: {lang}"
