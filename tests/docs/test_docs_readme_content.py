"""docs/README.mdの内容に関するテストコード.

このテストファイルは、docs/README.mdファイルの内容と構造を検証します。
新しいドキュメント構造（2025-11-02再編成）に対応しています。
"""

from pathlib import Path
import re

import pytest


pytestmark = pytest.mark.docs


class TestDocsReadmeContent:
    """docs/README.mdの内容と構造をテストするクラス."""

    @pytest.fixture
    def project_root(self) -> Path:
        """プロジェクトルートディレクトリのパスを取得."""
        return Path(__file__).parent.parent.parent

    @pytest.fixture
    def docs_dir(self, project_root: Path) -> Path:
        """docsディレクトリのパスを取得."""
        return project_root / "docs"

    @pytest.fixture
    def docs_readme_content(self, docs_dir: Path) -> str:
        """docs/README.mdファイルの内容を取得."""
        readme_path = docs_dir / "README.md"
        return readme_path.read_text(encoding="utf-8")

    def test_docs_readme_file_exists(self, docs_dir: Path) -> None:
        """docs/README.mdファイルが存在することを確認."""
        # Arrange (準備)
        readme_path = docs_dir / "README.md"

        # Act (実行)
        exists = readme_path.exists()

        # Assert (検証)
        assert exists, "docs/README.md file should exist"

    def test_docs_readme_has_title(self, docs_readme_content: str) -> None:
        """docs/README.mdにタイトルが含まれていることを確認."""
        # Arrange (準備)
        # 新しいタイトル「ドキュメントインデックス」
        title_pattern = r"# ドキュメントインデックス"

        # Act (実行)
        result = re.search(title_pattern, docs_readme_content)

        # Assert (検証)
        assert result, "Document title 'ドキュメントインデックス' should be present"

    def test_docs_readme_has_overview(self, docs_readme_content: str) -> None:
        """docs/README.mdに概要セクションが含まれていることを確認."""
        # Arrange (準備)
        overview_patterns = [
            r"## 📚 概要",
            r"STOCK-INVESTMENT-ANALYZER",
            r"\*\*最終更新\*\*:",
            r"\*\*プロジェクト\*\*:",
        ]

        # Act (実行)
        # 検証で実行

        # Assert (検証)
        for pattern in overview_patterns:
            assert re.search(
                pattern, docs_readme_content
            ), f"Overview section pattern '{pattern}' should be present"

    def test_docs_readme_has_quick_reference(
        self, docs_readme_content: str
    ) -> None:
        """docs/README.mdに困ったときのクイックリファレンスがあることを確認."""
        # Arrange (準備)
        quick_ref_patterns = [
            r"## 🆘 困ったときのクイックリファレンス",
            r"### 🔧 開発中に困ったとき",
            r"### 🐛 エラーが発生したとき",
            r"### 📋 作業フローで困ったとき",
        ]

        # Act (実行)
        # 検証で実行

        # Assert (検証)
        for pattern in quick_ref_patterns:
            assert re.search(
                pattern, docs_readme_content
            ), f"Quick reference pattern '{pattern}' should be present"

    def test_docs_readme_has_new_structure_section(
        self, docs_readme_content: str
    ) -> None:
        """docs/README.mdに新しいドキュメント構造セクションがあることを確認."""
        # Arrange (準備)
        structure_patterns = [
            r"新しいドキュメント構造（2025-11-02再編成）",
            r"guides/ - 実践的なガイド",
            r"standards/ - 規約・基準",
            r"ci-cd/ - CI/CD詳細設定",
        ]

        # Act (実行)
        # 検証で実行

        # Assert (検証)
        for pattern in structure_patterns:
            assert re.search(
                pattern, docs_readme_content
            ), f"Structure pattern '{pattern}' should be present"

    def test_docs_readme_has_ai_developer_guide(
        self, docs_readme_content: str
    ) -> None:
        """docs/README.mdにAI開発者向けガイドが含まれていることを確認."""
        # Arrange (準備)
        ai_guide_patterns = [
            r"## 🤖 AI開発者向けガイド",
            r"### タスク別推奨参照順序",
            r"#### 🏁 初期セットアップ時",
            r"#### 🛠️ バックエンド開発時",
        ]

        # Act (実行)
        # 検証で実行

        # Assert (検証)
        for pattern in ai_guide_patterns:
            assert re.search(
                pattern, docs_readme_content
            ), f"AI guide pattern '{pattern}' should be present"

    def test_docs_readme_internal_links(
        self, docs_dir: Path, docs_readme_content: str
    ) -> None:
        """docs/README.md内のリンクが有効なファイルを指していることを確認."""
        # Arrange (準備)
        # [text](path) 形式のリンクを抽出
        link_pattern = r"\[([^\]]+)\]\(([^)]+\.md)\)"
        links = re.findall(link_pattern, docs_readme_content)

        # Act (実行)
        broken_links = []
        for link_text, file_path in links:
            # 外部リンクはスキップ
            if file_path.startswith(("http://", "https://")):
                continue

            # 絶対パスの場合
            if file_path.startswith("/"):
                target_path = docs_dir.parent / file_path.lstrip("/")
            else:
                target_path = docs_dir / file_path

            if not target_path.exists():
                broken_links.append(f"'{file_path}' (text: '{link_text}')")

        # Assert (検証)
        assert not broken_links, f"以下のリンクが壊れています: {', '.join(broken_links)}"

    def test_docs_readme_has_important_sections(
        self, docs_readme_content: str
    ) -> None:
        """docs/README.mdに重要なセクションが全て含まれていることを確認."""
        # Arrange (準備)
        important_sections = [
            r"クイックスタート",
            r"新しいドキュメント構造",
            r"従来のドキュメント構造",
            r"2025-11-02の主な変更点",
            r"ドキュメント管理ルール",
            r"AI開発者向けガイド",
            r"よくある参照パターン",
            r"変更履歴",
            r"外部リソース",
        ]

        # Act (実行)
        missing_sections = []
        for section in important_sections:
            if not re.search(section, docs_readme_content):
                missing_sections.append(section)

        # Assert (検証)
        assert not missing_sections, (
            f"以下の重要なセクションが見つかりません: " f"{', '.join(missing_sections)}"
        )


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
