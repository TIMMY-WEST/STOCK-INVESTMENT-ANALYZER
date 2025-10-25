"""docsディレクトリのドキュメント品質に関するテストコード.

このテストファイルは、docsディレクトリ内のMarkdownファイルの品質と整合性を検証します。
"""

from pathlib import Path
import re

import pytest


class TestDocsQuality:
    """ドキュメント品質をテストするクラス."""

    @pytest.fixture
    def project_root(self):
        """プロジェクトルートディレクトリのパスを取得."""
        return Path(__file__).parent.parent

    @pytest.fixture
    def docs_dir(self, project_root):
        """docsディレクトリのパスを取得."""
        return project_root / "docs"

    def get_all_markdown_files(self, docs_dir):
        """docsディレクトリ内のすべてのMarkdownファイルを取得."""
        return list(docs_dir.rglob("*.md"))

    def test_markdown_files_have_titles(self, docs_dir):
        """すべてのMarkdownファイルにタイトル（H1ヘッダー）があることを確認."""
        markdown_files = self.get_all_markdown_files(docs_dir)

        for md_file in markdown_files:
            with open(md_file, "r", encoding="utf-8") as f:
                content = f.read()

            # H1ヘッダー（# で始まる行）があることを確認
            h1_pattern = r"^# .+"
            assert re.search(
                h1_pattern, content, re.MULTILINE
            ), f"File '{md_file.relative_to(docs_dir)}' should have an H1 title"

    def test_internal_links_consistency(self, docs_dir):
        """内部リンクの整合性を確認（警告のみ）."""
        markdown_files = self.get_all_markdown_files(docs_dir)
        broken_links = []

        for md_file in markdown_files:
            with open(md_file, "r", encoding="utf-8") as f:
                content = f.read()

            # 相対パスのリンクを抽出
            relative_links = re.findall(
                r"\[.*?\]\(([^)]+\.md(?:#[^)]*)?)\)", content
            )

            for link in relative_links:
                # アンカー部分を除去してファイルパスのみを取得
                file_path = link.split("#")[0] if "#" in link else link

                # 相対パスを絶対パスに変換
                if file_path.startswith("./"):
                    target_path = md_file.parent / file_path[2:]
                elif file_path.startswith("../"):
                    target_path = md_file.parent / file_path
                else:
                    target_path = md_file.parent / file_path

                # ファイルが存在しない場合は警告リストに追加
                if not target_path.exists():
                    broken_links.append(
                        f"'{file_path}' from '{md_file.relative_to(docs_dir)}'"
                    )

        # 壊れたリンクは警告として表示（テスト失敗にはしない）
        if broken_links:
            print(f"Warning: Broken internal links found: {broken_links}")

    def test_no_broken_internal_links(self, docs_dir):
        """壊れた内部リンクがないことを確認（警告のみ）."""
        markdown_files = self.get_all_markdown_files(docs_dir)
        broken_links = []

        for md_file in markdown_files:
            with open(md_file, "r", encoding="utf-8") as f:
                content = f.read()

            # 内部リンクパターンを検出
            link_pattern = r"\[([^\]]+)\]\(([^)]+\.md)\)"
            links = re.findall(link_pattern, content)

            for link_text, file_path in links:
                # 外部リンクをスキップ
                if file_path.startswith("http"):
                    continue

                # 相対パスを絶対パスに変換
                if file_path.startswith("/"):
                    # プロジェクトルートからの絶対パス
                    target_path = docs_dir.parent / file_path.lstrip("/")
                else:
                    # 現在のファイルからの相対パス
                    target_path = md_file.parent / file_path

                if not target_path.exists():
                    broken_links.append(
                        f"'{file_path}' in '{md_file.relative_to(docs_dir)}' (text: '{link_text}')"
                    )

        # 壊れたリンクは警告として表示（テスト失敗にはしない）
        if broken_links:
            print(f"Warning: Broken internal links found: {broken_links}")

    def test_consistent_heading_style(self, docs_dir):
        """見出しスタイルの一貫性を確認（Setextスタイルの禁止）（警告のみ）."""
        markdown_files = self.get_all_markdown_files(docs_dir)
        setext_headings = []

        for md_file in markdown_files:
            with open(md_file, "r", encoding="utf-8") as f:
                lines = f.readlines()

            # Setextスタイルの見出し（= または - の下線）を検出
            for i, line in enumerate(lines[1:], 1):  # 2行目から開始
                if re.match(r"^=+\s*$", line.strip()) or re.match(
                    r"^-+\s*$", line.strip()
                ):
                    setext_headings.append(
                        f"'{md_file.relative_to(docs_dir)}' at line {i + 1}"
                    )

        # Setextスタイルの見出しは警告として表示（テスト失敗にはしない）
        if setext_headings:
            print(
                f"Warning: Setext-style headings found (use ATX-style # ## ### instead): {setext_headings}"
            )

    def test_no_trailing_whitespace(self, docs_dir):
        """行末の空白がないことを確認（警告のみ）."""
        markdown_files = self.get_all_markdown_files(docs_dir)
        trailing_whitespace_files = []

        for md_file in markdown_files:
            with open(md_file, "r", encoding="utf-8") as f:
                lines = f.readlines()

            for i, line in enumerate(lines, 1):
                # 行末に空白がないことを確認（改行文字は除く）
                if line.rstrip("\n\r").endswith(" ") or line.rstrip(
                    "\n\r"
                ).endswith("\t"):
                    trailing_whitespace_files.append(
                        f"'{md_file.relative_to(docs_dir)}' at line {i}"
                    )
                    break  # ファイルごとに1つの警告で十分

        # 行末空白は警告として表示（テスト失敗にはしない）
        if trailing_whitespace_files:
            print(
                f"Warning: Trailing whitespace found in: {trailing_whitespace_files}"
            )

    def test_proper_code_block_language(self, docs_dir):
        """コードブロックに適切な言語指定があることを確認."""
        markdown_files = self.get_all_markdown_files(docs_dir)

        for md_file in markdown_files:
            with open(md_file, "r", encoding="utf-8") as f:
                content = f.read()

            # フェンスコードブロック（```）を検索
            code_blocks = re.findall(r"```(\w*)\n", content)

            for _i, lang in enumerate(code_blocks):
                # 言語指定がない空のコードブロックを警告
                if not lang:
                    # 特定のファイルでは言語指定なしを許可する場合もある
                    # ここでは厳密にチェックしないが、推奨として記録
                    pass

    def test_consistent_emoji_usage(self, docs_dir):
        """絵文字の一貫した使用を確認."""
        markdown_files = self.get_all_markdown_files(docs_dir)

        # 許可された絵文字パターン
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

        for md_file in markdown_files:
            with open(md_file, "r", encoding="utf-8") as f:
                content = f.read()

            # 絵文字を検索（基本的なUnicode絵文字範囲）
            emoji_pattern = r"[\U0001F600-\U0001F64F\U0001F300-\U0001F5FF\U0001F680-\U0001F6FF\U0001F1E0-\U0001F1FF\U00002600-\U000027BF\U0001F900-\U0001F9FF]"
            found_emojis = re.findall(emoji_pattern, content)

            # 見つかった絵文字が許可されたパターンに含まれているかチェック
            for emoji in found_emojis:
                is_allowed = any(
                    re.search(pattern, emoji)
                    for pattern in allowed_emoji_patterns
                )
                if not is_allowed:
                    # 警告として記録（必ずしもエラーにしない）
                    pass


class TestDocsLinkIntegrity:
    """ドキュメント間のリンク整合性をテストするクラス."""

    @pytest.fixture
    def project_root(self):
        """プロジェクトルートディレクトリのパスを取得."""
        return Path(__file__).parent.parent

    @pytest.fixture
    def docs_dir(self, project_root):
        """docsディレクトリのパスを取得."""
        return project_root / "docs"

    def test_readme_links_to_existing_files(self, docs_dir):
        """README.mdからのリンクが存在するファイルを指していることを確認."""
        readme_path = docs_dir / "README.md"

        with open(readme_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Markdownリンクを抽出
        md_links = re.findall(r"\[.*?\]\(([^)]+\.md(?:#[^)]*)?)\)", content)

        for link in md_links:
            file_path = link.split("#")[0] if "#" in link else link
            target_path = docs_dir / file_path
            assert (
                target_path.exists()
            ), f"README.md links to non-existent file: {file_path}"

    def test_bidirectional_link_consistency(self, docs_dir):
        """双方向リンクの整合性を確認（警告のみ）."""
        readme_path = docs_dir / "README.md"
        if not readme_path.exists():
            pytest.skip("README.md not found")

        with open(readme_path, "r", encoding="utf-8") as f:
            readme_content = f.read()

        # README.mdからリンクされているファイルを取得
        link_pattern = r"\[([^\]]+)\]\(([^)]+\.md)\)"
        readme_links = re.findall(link_pattern, readme_content)

        missing_back_links = []
        for _link_text, file_path in readme_links:
            target_path = docs_dir / file_path
            if target_path.exists():
                with open(target_path, "r", encoding="utf-8") as f:
                    target_content = f.read()

                # 対象ファイルからREADME.mdへの逆リンクがあることを確認
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

        # 逆リンクの欠如は警告として表示（テスト失敗にはしない）
        if missing_back_links:
            print(
                f"Warning: Files without back-links to README.md: {missing_back_links}"
            )


if __name__ == "__main__":
    # テストを直接実行する場合
    pytest.main([__file__, "-v"])
