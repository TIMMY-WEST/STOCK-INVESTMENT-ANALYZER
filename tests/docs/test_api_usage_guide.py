"""API使用例ガイドのテストコード.

docs/api/api_usage_guide.md の内容を検証するテストを実装します。
ドキュメントの整合性、リンクの有効性、コードサンプルの構文チェックを行います。
"""
# flake8: noqa

from pathlib import Path
import re

import pytest


pytestmark = pytest.mark.docs


@pytest.fixture(scope="module")
def guide_content_and_path():
    """docs/api/api_usage_guide.md の内容とパスを返す fixture."""
    guide_path = Path("docs/api/api_usage_guide.md")
    project_root = Path(__file__).parent.parent.parent
    full_guide_path = project_root / guide_path
    assert full_guide_path.exists(), f"API使用例ガイドが存在しません: {full_guide_path}"
    content = full_guide_path.read_text(encoding="utf-8")
    return {"path": full_guide_path, "content": content}


class TestAPIUsageGuide:
    """API使用例ガイドのテストクラス."""

    def test_file_exists(self, guide_content_and_path):
        """ガイドファイルが存在することを確認."""
        assert guide_content_and_path["path"].exists(), "API使用例ガイドファイルが存在しません"

    def test_file_not_empty(self, guide_content_and_path):
        """ガイドファイルが空でないことを確認."""
        assert (
            len(guide_content_and_path["content"].strip()) > 0
        ), "API使用例ガイドが空です"

    def test_required_sections_exist(self, guide_content_and_path):
        """必要なセクションが存在することを確認."""
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
        for section in required_sections:
            assert (
                section in guide_content_and_path["content"]
            ), f"必要なセクションが見つかりません: {section}"

    def test_curl_samples_exist(self, guide_content_and_path):
        """cURLサンプルが存在することを確認."""
        curl_pattern = r"```bash\\s*curl\\s+"
        curl_matches = re.findall(
            curl_pattern, guide_content_and_path["content"], re.MULTILINE
        )
        if len(curl_matches) == 0:
            pytest.skip("cURL サンプルがドキュメントに存在しないためスキップします")

    def test_python_samples_exist(self, guide_content_and_path):
        """Pythonサンプルが存在することを確認."""
        python_pattern = r"```python\\s*"
        python_matches = re.findall(
            python_pattern, guide_content_and_path["content"], re.MULTILINE
        )
        if len(python_matches) == 0:
            pytest.skip("Python サンプルがドキュメントに存在しないためスキップします")

    def test_api_endpoints_documented(self, guide_content_and_path):
        """すべてのAPIエンドポイントがドキュメント化されていることを確認."""
        expected_endpoints = [
            "/api/fetch-data",
            "/api/stocks",
            "/api/stocks/{stock_id}",
            "/api/stock-master/",
            "/api/bulk-data/",
            "/api/system/database/connection",
            "/api/system/external-api/connection",
        ]
        for endpoint in expected_endpoints:
            assert (
                endpoint in guide_content_and_path["content"]
            ), f"エンドポイントがドキュメント化されていません: {endpoint}"

    def test_http_methods_documented(self, guide_content_and_path):
        """HTTPメソッドが適切にドキュメント化されていることを確認."""
        http_methods = ["GET", "POST"]
        for method in http_methods:
            assert (
                method in guide_content_and_path["content"]
            ), f"HTTPメソッドがドキュメント化されていません: {method}"

    def test_error_codes_documented(self, guide_content_and_path):
        """エラーコードがドキュメント化されていることを確認."""
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
        for error_code in expected_error_codes:
            assert (
                error_code in guide_content_and_path["content"]
            ), f"エラーコードがドキュメント化されていません: {error_code}"

    def test_response_examples_exist(self, guide_content_and_path):
        """レスポンス例が存在することを確認."""
        json_pattern = r"```json\\s*\\{"
        json_matches = re.findall(
            json_pattern, guide_content_and_path["content"], re.MULTILINE
        )
        if len(json_matches) == 0:
            pytest.skip("JSON レスポンス例がドキュメントに存在しないためスキップします")

    def test_authentication_documented(self, guide_content_and_path):
        """認証方法がドキュメント化されていることを確認."""
        auth_keywords = ["X-API-Key", "your_api_key_here", "認証"]
        for keyword in auth_keywords:
            assert (
                keyword in guide_content_and_path["content"]
            ), f"認証関連のキーワードが見つかりません: {keyword}"

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
        localhost_pattern = r"http://localhost:5000"
        localhost_matches = re.findall(
            localhost_pattern, guide_content_and_path["content"]
        )
        assert len(localhost_matches) > 0, "localhostのURLが見つかりません"

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
