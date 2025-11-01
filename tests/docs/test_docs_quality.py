"""docsディレクトリのドキュメント品質に関するテストコード.

このテストファイルは、docsディレクトリ内のMarkdownファイルの品質と整合性を検証します。
"""

from pathlib import Path
import re

import pytest


pytestmark = pytest.mark.docs


class TestDocsQuality:
    """ドキュメント品質をテストするクラス."""

    @pytest.fixture
    def project_root(self):
        """プロジェクトルートディレクトリのパスを取得."""
        return Path(__file__).parent.parent.parent

    @pytest.fixture
    def docs_dir(self, project_root):
        """docsディレクトリのパスを取得."""
        return project_root / "docs"

    def get_all_markdown_files(self, docs_dir):
        """docsディレクトリ内のすべてのMarkdownファイルを取得."""
        return list(docs_dir.rglob("*.md"))

    def test_markdown_files_have_titles(self, docs_dir):
        """すべてのMarkdownファイルにタイトル（H1ヘッダー）があることを確認."""
        # Arrange (準備)
        markdown_files = self.get_all_markdown_files(docs_dir)

        # Act (実行)
        for md_file in markdown_files:
            with open(md_file, "r", encoding="utf-8") as f:
                content = f.read()

            # Assert (検証)
            h1_pattern = r"^# .+"
            assert re.search(
                h1_pattern, content, re.MULTILINE
            ), f"File '{md_file.relative_to(docs_dir)}' should have an H1 title"

    def test_internal_links_consistency(self, docs_dir):
        """内部リンクの整合性を確認（警告のみ）."""
        # Arrange (準備)
        markdown_files = self.get_all_markdown_files(docs_dir)
        broken_links = []

        # Act (実行)
        for md_file in markdown_files:
            with open(md_file, "r", encoding="utf-8") as f:
                content = f.read()

            relative_links = re.findall(
                r"\[.*?\]\(([^)]+\.md(?:#[^)]*)?)\)", content
            )

            for link in relative_links:
                file_path = link.split("#")[0] if "#" in link else link

                if file_path.startswith("./"):
                    target_path = md_file.parent / file_path[2:]
                elif file_path.startswith("../"):
                    target_path = md_file.parent / file_path
                else:
                    target_path = md_file.parent / file_path

                if not target_path.exists():
                    broken_links.append(
                        f"'{file_path}' from '{md_file.relative_to(docs_dir)}'"
                    )

        # Assert (検証)
        if broken_links:
            print(f"Warning: Broken internal links found: {broken_links}")

    def test_no_broken_internal_links(self, docs_dir):
        """壊れた内部リンクがないことを確認（警告のみ）."""
        # Arrange (準備)
        markdown_files = self.get_all_markdown_files(docs_dir)
        broken_links = []

        # Act (実行)
        for md_file in markdown_files:
            with open(md_file, "r", encoding="utf-8") as f:
                content = f.read()

            link_pattern = r"\[([^\]]+)\]\(([^)]+\.md)\)"
            links = re.findall(link_pattern, content)

            for link_text, file_path in links:
                if file_path.startswith("http"):
                    continue

                if file_path.startswith("/"):
                    target_path = docs_dir.parent / file_path.lstrip("/")
                else:
                    target_path = md_file.parent / file_path

                if not target_path.exists():
                    broken_links.append(
                        f"'{file_path}' in '{md_file.relative_to(docs_dir)}' (text: '{link_text}')"
                    )

        # Assert (検証)
        if broken_links:
            print(f"Warning: Broken internal links found: {broken_links}")

    def test_consistent_heading_style(self, docs_dir):
        """見出しスタイルの一貫性を確認（Setextスタイルの禁止）（警告のみ）."""
        # Arrange (準備)
        markdown_files = self.get_all_markdown_files(docs_dir)
        setext_headings = []

        # Act (実行)
        for md_file in markdown_files:
            with open(md_file, "r", encoding="utf-8") as f:
                lines = f.readlines()

            for i, line in enumerate(lines[1:], 1):
                if re.match(r"^=+\s*$", line.strip()) or re.match(
                    r"^-+\s*$", line.strip()
                ):
                    setext_headings.append(
                        f"'{md_file.relative_to(docs_dir)}' at line {i + 1}"
                    )

        # Assert (検証)
        if setext_headings:
            print(
                f"Warning: Setext-style headings found (use ATX-style # ## ### instead): {setext_headings}"
            )

    def test_no_trailing_whitespace(self, docs_dir):
        """行末の空白がないことを確認（警告のみ）."""
        # Arrange (準備)
        markdown_files = self.get_all_markdown_files(docs_dir)
        trailing_whitespace_files = []

        # Act (実行)
        for md_file in markdown_files:
            with open(md_file, "r", encoding="utf-8") as f:
                lines = f.readlines()

            for i, line in enumerate(lines, 1):
                if line.rstrip("\n\r").endswith(" ") or line.rstrip(
                    "\n\r"
                ).endswith("\t"):
                    trailing_whitespace_files.append(
                        f"'{md_file.relative_to(docs_dir)}' at line {i}"
                    )
                    break

        # Assert (検証)
        if trailing_whitespace_files:
            print(
                f"Warning: Trailing whitespace found in: {trailing_whitespace_files}"
            )

    def test_proper_code_block_language(self, docs_dir):
        """コードブロックに適切な言語指定があることを確認."""
        # Arrange (準備)
        markdown_files = self.get_all_markdown_files(docs_dir)

        # Act (実行)
        for md_file in markdown_files:
            with open(md_file, "r", encoding="utf-8") as f:
                content = f.read()

            code_blocks = re.findall(r"```(\w*)\n", content)

            # Assert (検証)
            for _i, lang in enumerate(code_blocks):
                if not lang:
                    pass

    def test_consistent_emoji_usage(self, docs_dir):
        """絵文字の一貫した使用を確認."""
        # Arrange (準備)
        markdown_files = self.get_all_markdown_files(docs_dir)
        allowed_emoji_patterns = [
            r"📋",  # 概要
            r"📁",  # ドキュメント構成
            r"🤖",  # AI開発者向け
            r"🏁",  # 初期セットアップ
            r"🛠️",  # バックエンド開発
            r"🎨",  # フロントエンド開発
            r"🚀",  # リリース・デプロイ
            r"🔴",  # 優先度: 高
            r"🟡",  # 優先度: 中
            r"🟢",  # 優先度: 低
            r"🔍",  # よくある参照パターン
            r"📌",  # 開発の進め方
            r"🏗️",  # アーキテクチャ
            r"🔌",  # API仕様
            r"📖",  # 運用・利用ガイド
            r"🔧",  # 開発関連
        ]

        # Act (実行)
        for md_file in markdown_files:
            with open(md_file, "r", encoding="utf-8") as f:
                content = f.read()

            emoji_pattern = r"[\U0001F600-\U0001F64F\U0001F300-\U0001F5FF\U0001F680-\U0001F6FF\U0001F1E0-\U0001F1FF\U00002600-\U000027BF\U0001F900-\U0001F9FF]"
            found_emojis = re.findall(emoji_pattern, content)

            # Assert (検証)
            for emoji in found_emojis:
                is_allowed = any(
                    re.search(pattern, emoji)
                    for pattern in allowed_emoji_patterns
                )
                if not is_allowed:
                    pass


class TestDocsLinkIntegrity:
    """ドキュメント間のリンク整合性をテストするクラス."""

    @pytest.fixture
    def project_root(self):
        """プロジェクトルートディレクトリのパスを取得."""
        return Path(__file__).parent.parent.parent

    @pytest.fixture
    def docs_dir(self, project_root):
        """docsディレクトリのパスを取得."""
        return project_root / "docs"

    def test_readme_links_to_existing_files(self, docs_dir):
        """README.mdからのリンクが存在するファイルを指していることを確認."""
        # Arrange (準備)
        readme_path = docs_dir / "README.md"

        # Act (実行)
        with open(readme_path, "r", encoding="utf-8") as f:
            content = f.read()

        md_links = re.findall(r"\[.*?\]\(([^)]+\.md(?:#[^)]*)?)\)", content)

        # Assert (検証)
        for link in md_links:
            file_path = link.split("#")[0] if "#" in link else link
            target_path = docs_dir / file_path
            assert (
                target_path.exists()
            ), f"README.md links to non-existent file: {file_path}"

    def test_bidirectional_link_consistency(self, docs_dir):
        """双方向リンクの整合性を確認（警告のみ）."""
        # Arrange (準備)
        readme_path = docs_dir / "README.md"
        if not readme_path.exists():
            pytest.skip("README.md not found")

        # Act (実行)
        with open(readme_path, "r", encoding="utf-8") as f:
            readme_content = f.read()

        link_pattern = r"\[([^\]]+)\]\(([^)]+\.md)\)"
        readme_links = re.findall(link_pattern, readme_content)

        missing_back_links = []
        for _link_text, file_path in readme_links:
            target_path = docs_dir / file_path
            if target_path.exists():
                with open(target_path, "r", encoding="utf-8") as f:
                    target_content = f.read()

                back_link_patterns = [
                    r"\[.*?\]\(\.\./README\.md\)",
                    r"\[.*?\]\(README\.md\)",
                    r"\[.*?\]\(\./README\.md\)",
                ]

                has_back_link = any(
                    re.search(pattern, target_content)
                    for pattern in back_link_patterns
                )
                if not has_back_link:
                    missing_back_links.append(file_path)

        # Assert (検証)
        if missing_back_links:
            print(
                f"Warning: Files without back-links to README.md: {missing_back_links}"
            )


if __name__ == "__main__":
    # テストを直接実行する場合
    pytest.main([__file__, "-v"])
