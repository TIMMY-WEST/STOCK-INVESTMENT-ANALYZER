"""ドキュメント内部リンク整合性検査テスト.

このモジュールは以下をテストします:
- 内部リンクの整合性検査
- リンク切れの検出
- アンカーリンクの検証
"""

from pathlib import Path
import re

import pytest


pytestmark = pytest.mark.docs


class TestDocsInternalLinks:
    """ドキュメント内部リンクテストクラス."""

    @pytest.fixture
    def project_root(self) -> Path:
        """プロジェクトルートディレクトリのパスを取得."""
        return Path(__file__).parent.parent.parent

    @pytest.fixture
    def docs_dir(self, project_root: Path) -> Path:
        """docsディレクトリのパスを取得."""
        return project_root / "docs"

    @pytest.fixture
    def all_markdown_files(self, docs_dir: Path) -> list[Path]:
        """docsディレクトリ内の全Markdownファイルを取得（old/archiveディレクトリを除外）."""
        exclude_dirs = {"old", "archive"}
        return [
            f
            for f in docs_dir.rglob("*.md")
            if not any(excluded in f.parts for excluded in exclude_dirs)
        ]

    def _extract_markdown_links(self, content: str) -> list[tuple[str, str]]:
        """Markdownコンテンツからリンクを抽出.

        Returns:
            (リンクテキスト, リンク先) のタプルのリスト
        """
        # [text](url) 形式のリンクを抽出
        link_pattern = r"\[([^\]]+)\]\(([^)]+)\)"
        return re.findall(link_pattern, content)

    def _is_external_link(self, link: str) -> bool:
        """外部リンクかどうかを判定."""
        return link.startswith(("http://", "https://", "mailto:"))

    def _resolve_link_path(
        self, current_file: Path, link: str, docs_dir: Path
    ) -> Path:
        """リンクパスを解決して絶対パスを取得."""
        # アンカー部分を除去
        link_without_anchor = link.split("#")[0]

        # 空の場合（アンカーのみのリンク）は現在のファイル
        if not link_without_anchor:
            return current_file

        # 絶対パス（ルートから）
        if link_without_anchor.startswith("/"):
            return docs_dir.parent / link_without_anchor.lstrip("/")

        # 相対パス
        return (current_file.parent / link_without_anchor).resolve()

    def test_no_broken_internal_links(
        self, docs_dir: Path, all_markdown_files: list[Path]
    ) -> None:
        """壊れた内部リンクが存在しないことを確認."""
        # Arrange (準備)
        broken_links = []

        # 除外するディレクトリ
        exclude_dirs = {"old", "archive"}

        # Act (実行)
        for md_file in all_markdown_files:
            # old/とarchive/ディレクトリ内のファイルはスキップ
            if any(excluded in md_file.parts for excluded in exclude_dirs):
                continue

            content = md_file.read_text(encoding="utf-8")
            links = self._extract_markdown_links(content)

            for link_text, link_url in links:
                # 外部リンクはスキップ
                if self._is_external_link(link_url):
                    continue

                # ソースコードファイルへの参照はスキップ
                # (例: app/services/file.py, app/services/file.py#L123)
                if (
                    link_url.endswith((".py", ".js", ".css", ".html"))
                    or "#L" in link_url
                ):
                    continue

                # リンク先のファイルパスを取得
                target_path = self._resolve_link_path(
                    md_file, link_url, docs_dir
                )

                # ファイルが存在するか確認
                if not target_path.exists():
                    relative_source = md_file.relative_to(docs_dir)
                    broken_links.append(
                        f"'{link_url}' in {relative_source} "
                        f"(text: '{link_text}')"
                    )

        # Assert (検証)
        assert not broken_links, "以下の壊れた内部リンクが見つかりました:\n" + "\n".join(
            f"  - {link}" for link in broken_links
        )

    def test_readme_links_are_valid(self, docs_dir: Path) -> None:
        """README.mdからのリンクが全て有効であることを確認."""
        # Arrange (準備)
        readme_path = docs_dir / "README.md"
        if not readme_path.exists():
            pytest.skip("README.md not found")

        # Act (実行)
        content = readme_path.read_text(encoding="utf-8")
        links = self._extract_markdown_links(content)

        broken_links = []
        for link_text, link_url in links:
            # 外部リンクはスキップ
            if self._is_external_link(link_url):
                continue

            # リンク先のファイルパスを取得
            target_path = self._resolve_link_path(
                readme_path, link_url, docs_dir
            )

            # ファイルが存在するか確認
            if not target_path.exists():
                broken_links.append(f"'{link_url}' (text: '{link_text}')")

        # Assert (検証)
        assert not broken_links, "README.mdに以下の壊れたリンクが見つかりました:\n" + "\n".join(
            f"  - {link}" for link in broken_links
        )

    def test_subdirectory_readme_links_are_valid(self, docs_dir: Path) -> None:
        """各サブディレクトリのREADME.mdからのリンクが有効であることを確認."""
        # Arrange (準備)
        readme_files = list(docs_dir.glob("*/README.md"))

        # 除外するディレクトリ
        exclude_dirs = {"old", "archive"}

        # Act (実行)
        all_broken_links = []
        for readme_path in readme_files:
            # old/とarchive/のREADME.mdはスキップ
            if any(excluded in readme_path.parts for excluded in exclude_dirs):
                continue

            content = readme_path.read_text(encoding="utf-8")
            links = self._extract_markdown_links(content)

            for link_text, link_url in links:
                # 外部リンクはスキップ
                if self._is_external_link(link_url):
                    continue

                # ソースコードファイルへの参照はスキップ
                if (
                    link_url.endswith((".py", ".js", ".css", ".html", ".yaml"))
                    or "#L" in link_url
                ):
                    continue

                # リンク先のファイルパスを取得
                target_path = self._resolve_link_path(
                    readme_path, link_url, docs_dir
                )

                # ファイルが存在するか確認
                if not target_path.exists():
                    relative_readme = readme_path.relative_to(docs_dir)
                    all_broken_links.append(
                        f"'{link_url}' in {relative_readme} "
                        f"(text: '{link_text}')"
                    )

        # Assert (検証)
        assert (
            not all_broken_links
        ), "サブディレクトリのREADME.mdに壊れたリンクが見つかりました:\n" + "\n".join(
            f"  - {link}" for link in all_broken_links
        )


class TestDocsAnchorLinks:
    """ドキュメントのアンカーリンクテストクラス."""

    @pytest.fixture
    def project_root(self) -> Path:
        """プロジェクトルートディレクトリのパスを取得."""
        return Path(__file__).parent.parent.parent

    @pytest.fixture
    def docs_dir(self, project_root: Path) -> Path:
        """docsディレクトリのパスを取得."""
        return project_root / "docs"

    @pytest.fixture
    def all_markdown_files(self, docs_dir: Path) -> list[Path]:
        """docsディレクトリ内の全Markdownファイルを取得（old/archiveディレクトリを除外）."""
        exclude_dirs = {"old", "archive"}
        return [
            f
            for f in docs_dir.rglob("*.md")
            if not any(excluded in f.parts for excluded in exclude_dirs)
        ]

    def _extract_headings(self, content: str) -> set[str]:
        """Markdownコンテンツから見出しを抽出してアンカーIDに変換.

        GitHubのMarkdown変換ルールに従う:
        - 小文字化
        - スペースをハイフンに変換
        - 特殊文字を除去
        """
        heading_pattern = r"^#{1,6}\s+(.+)$"
        headings = re.findall(heading_pattern, content, re.MULTILINE)

        anchor_ids = set()
        for heading in headings:
            # GitHubのアンカーID変換ルール
            anchor = heading.lower()
            # 特殊文字を除去、スペースをハイフンに
            anchor = re.sub(r"[^\w\s-]", "", anchor)
            anchor = re.sub(r"\s+", "-", anchor)
            anchor_ids.add(anchor)

        return anchor_ids

    def test_anchor_links_are_valid(
        self, docs_dir: Path, all_markdown_files: list[Path]
    ) -> None:
        """アンカーリンクが有効であることを確認（警告のみ）."""
        # Arrange (準備)
        invalid_anchors = []

        # Act (実行)
        for md_file in all_markdown_files:
            content = md_file.read_text(encoding="utf-8")

            # ファイル内の見出しからアンカーIDを抽出
            valid_anchors = self._extract_headings(content)

            # アンカーリンクを抽出
            anchor_pattern = r"\[([^\]]+)\]\(#([^)]+)\)"
            anchor_links = re.findall(anchor_pattern, content)

            for link_text, anchor in anchor_links:
                if anchor not in valid_anchors:
                    relative_path = md_file.relative_to(docs_dir)
                    invalid_anchors.append(
                        f"'{anchor}' in {relative_path} "
                        f"(text: '{link_text}')"
                    )

        # Assert (検証)
        # 警告のみ（エラーにはしない）
        if invalid_anchors:
            print(
                "\n警告: 以下の無効なアンカーリンクが見つかりました:\n"
                + "\n".join(f"  - {link}" for link in invalid_anchors)
            )


class TestDocsCrossReferences:
    """ドキュメント間の相互参照テストクラス."""

    @pytest.fixture
    def project_root(self) -> Path:
        """プロジェクトルートディレクトリのパスを取得."""
        return Path(__file__).parent.parent.parent

    @pytest.fixture
    def docs_dir(self, project_root: Path) -> Path:
        """docsディレクトリのパスを取得."""
        return project_root / "docs"

    def test_important_docs_referenced_in_main_readme(
        self, docs_dir: Path
    ) -> None:
        """重要なドキュメントがメインREADME.mdで参照されていることを確認."""
        # Arrange (準備)
        readme_path = docs_dir / "README.md"
        if not readme_path.exists():
            pytest.skip("README.md not found")

        # 実際に存在する重要なドキュメント
        important_docs = [
            "guides/setup_guide.md",
            "standards/coding-standards.md",
            "standards/testing-standards.md",
            "standards/git-workflow.md",
            "api/api_reference.md",  # api_specification.md から変更
            "architecture/architecture_overview.md",
        ]

        # Act (実行)
        readme_content = readme_path.read_text(encoding="utf-8")
        missing_references = []

        for doc in important_docs:
            # ファイル名のみでもOK
            doc_name = Path(doc).name
            if doc not in readme_content and doc_name not in readme_content:
                missing_references.append(doc)

        # Assert (検証)
        assert not missing_references, (
            f"以下の重要なドキュメントがREADME.mdで参照されていません: "
            f"{', '.join(missing_references)}"
        )


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
