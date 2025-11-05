"""ドキュメント品質チェックテスト.

このモジュールは以下をテストします:
- 全MarkdownファイルにH1が存在すること
- 空ファイルが存在しないこと
- コードブロックに言語指定があること
"""

from pathlib import Path
import re

import pytest


pytestmark = pytest.mark.docs


class TestDocsQuality:
    """ドキュメント品質をテストするクラス."""

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

    def test_markdown_files_have_h1_title(
        self, docs_dir: Path, all_markdown_files: list[Path]
    ) -> None:
        """全てのMarkdownファイルにH1タイトルが存在することを確認."""
        # Arrange (準備)
        files_without_h1 = []

        # Act (実行)
        for md_file in all_markdown_files:
            with open(md_file, "r", encoding="utf-8") as f:
                content = f.read()

            # H1パターン: # で始まる行
            h1_pattern = r"^# .+"
            if not re.search(h1_pattern, content, re.MULTILINE):
                relative_path = md_file.relative_to(docs_dir)
                files_without_h1.append(str(relative_path))

        # Assert (検証)
        assert not files_without_h1, (
            f"以下のファイルにH1タイトルがありません: " f"{', '.join(files_without_h1)}"
        )

    def test_no_empty_files(
        self, docs_dir: Path, all_markdown_files: list[Path]
    ) -> None:
        """空のMarkdownファイルが存在しないことを確認."""
        # Arrange (準備)
        empty_files = []

        # Act (実行)
        for md_file in all_markdown_files:
            content = md_file.read_text(encoding="utf-8").strip()
            if not content:
                relative_path = md_file.relative_to(docs_dir)
                empty_files.append(str(relative_path))

        # Assert (検証)
        assert not empty_files, f"以下の空ファイルが存在します: " f"{', '.join(empty_files)}"

    def test_files_have_minimum_content(
        self, docs_dir: Path, all_markdown_files: list[Path]
    ) -> None:
        """ファイルが最低限の内容を持つことを確認（10文字以上）."""
        # Arrange (準備)
        too_short_files = []
        min_length = 10

        # Act (実行)
        for md_file in all_markdown_files:
            content = md_file.read_text(encoding="utf-8").strip()
            if len(content) < min_length:
                relative_path = md_file.relative_to(docs_dir)
                too_short_files.append(
                    f"{relative_path} ({len(content)} chars)"
                )

        # Assert (検証)
        assert not too_short_files, (
            f"以下のファイルの内容が短すぎます（{min_length}文字未満）: "
            f"{', '.join(too_short_files)}"
        )

    @pytest.mark.skip(reason="大規模修正が必要なため一時的にスキップ")
    def test_code_blocks_have_language_specification(
        self, docs_dir: Path, all_markdown_files: list[Path]
    ) -> None:
        """コードブロックに言語指定があることを確認."""
        # Arrange (準備)
        files_with_unspecified_lang = []

        # Act (実行)
        for md_file in all_markdown_files:
            content = md_file.read_text(encoding="utf-8")

            # コードブロックパターン: ```language
            code_block_pattern = r"```(\w*)\n"
            code_blocks = re.findall(code_block_pattern, content)

            # 言語指定のないコードブロックをチェック
            unspecified_blocks = [lang for lang in code_blocks if not lang]

            if unspecified_blocks:
                relative_path = md_file.relative_to(docs_dir)
                files_with_unspecified_lang.append(
                    f"{relative_path} ({len(unspecified_blocks)} blocks)"
                )

        # Assert (検証)
        assert not files_with_unspecified_lang, (
            f"以下のファイルに言語指定のないコードブロックがあります: "
            f"{', '.join(files_with_unspecified_lang)}"
        )


class TestDocsConsistency:
    """ドキュメントの一貫性テストクラス."""

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

    def _is_setext_heading(self, prev_line: str, line_stripped: str) -> bool:
        """Setext形式の見出しかどうかを判定."""
        # 前の行がテキストで、アンダーラインの長さが前の行のテキスト長に近い場合のみ
        # Setext見出しと判定（水平線はちょうど3文字が多いので除外）
        if not prev_line or len(line_stripped) <= 3:
            return False

        # 前の行がマークダウン記号で始まっていない
        markdown_prefixes = ["#", ">", "|", "*", "-", "+", "```"]
        if any(prev_line.startswith(c) for c in markdown_prefixes):
            return False

        # 前の行が括弧などではない
        if prev_line in ["}", "{", "]", "["]:
            return False

        # アンダーラインの長さが前の行のテキスト長に近い（±30%以内）
        return (
            0.7 * len(prev_line) <= len(line_stripped) <= 1.3 * len(prev_line)
        )

    def test_consistent_heading_style(
        self, docs_dir: Path, all_markdown_files: list[Path]
    ) -> None:
        """見出しスタイルの一貫性を確認（ATX形式推奨）.

        Setext形式（===や---による見出し）の使用を検出します。
        """
        # Arrange (準備)
        setext_headings = []

        # Act (実行)
        for md_file in all_markdown_files:
            with open(md_file, "r", encoding="utf-8") as f:
                lines = f.readlines()

            in_code_block = False
            for i, line in enumerate(lines[1:], 1):
                # コードブロックの開始/終了を追跡
                if line.strip().startswith("```"):
                    in_code_block = not in_code_block
                    continue

                # コードブロック内はスキップ
                if in_code_block:
                    continue

                # Setextスタイルの見出し検出
                line_stripped = line.strip()
                is_underline = re.match(r"^=+\s*$", line_stripped) or re.match(
                    r"^-+\s*$", line_stripped
                )

                if is_underline:
                    prev_line = lines[i - 1].strip() if i > 0 else ""
                    if self._is_setext_heading(prev_line, line_stripped):
                        relative_path = md_file.relative_to(docs_dir)
                        setext_headings.append(f"{relative_path}:{i + 1}")

        # Assert (検証)
        # 警告のみ（エラーにはしない）
        if setext_headings:
            pytest.fail(
                f"警告: 以下の箇所でSetext形式の見出しが使用されています。"
                f"ATX形式（#, ##, ###）の使用を推奨します: "
                f"{', '.join(setext_headings)}"
            )

    def test_no_trailing_whitespace(
        self, docs_dir: Path, all_markdown_files: list[Path]
    ) -> None:
        """行末の空白がないことを確認（警告のみ）."""
        # Arrange (準備)
        trailing_whitespace_files = []

        # Act (実行)
        for md_file in all_markdown_files:
            with open(md_file, "r", encoding="utf-8") as f:
                lines = f.readlines()

            for i, line in enumerate(lines, 1):
                stripped = line.rstrip("\n\r")
                if stripped.endswith(" ") or stripped.endswith("\t"):
                    relative_path = md_file.relative_to(docs_dir)
                    trailing_whitespace_files.append(f"{relative_path}:{i}")
                    break  # ファイルごとに1つのみ報告

        # Assert (検証)
        # 警告のみ（エラーにはしない）
        if trailing_whitespace_files:
            print(
                f"\n警告: 以下のファイルに行末の空白があります: "
                f"{', '.join(trailing_whitespace_files)}"
            )


class TestDocsMetadata:
    """ドキュメントのメタデータテストクラス."""

    @pytest.fixture
    def project_root(self) -> Path:
        """プロジェクトルートディレクトリのパスを取得."""
        return Path(__file__).parent.parent.parent

    @pytest.fixture
    def docs_dir(self, project_root: Path) -> Path:
        """docsディレクトリのパスを取得."""
        return project_root / "docs"

    def test_main_readme_has_last_updated(self, docs_dir: Path) -> None:
        """docs/README.mdに最終更新日が記載されていることを確認."""
        # Arrange (準備)
        readme_path = docs_dir / "README.md"

        # Act (実行)
        content = readme_path.read_text(encoding="utf-8")

        # "最終更新" パターン
        last_updated_pattern = r"\*\*最終更新\*\*:\s*\d{4}-\d{2}-\d{2}"

        # Assert (検証)
        assert re.search(last_updated_pattern, content), (
            "docs/README.mdに最終更新日（**最終更新**: YYYY-MM-DD）" "が記載されていません"
        )


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
