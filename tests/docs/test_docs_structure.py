"""docsディレクトリの構造に関するテストコード.

このテストファイルは、docsディレクトリの構造とファイルの存在を検証します。
"""

from pathlib import Path

import pytest


pytestmark = pytest.mark.unit


class TestDocsStructure:
    """docsディレクトリの構造をテストするクラス."""

    @pytest.fixture
    def project_root(self):
        """プロジェクトルートディレクトリのパスを取得."""
        return Path(__file__).parent.parent.parent

    @pytest.fixture
    def docs_dir(self, project_root):
        """docsディレクトリのパスを取得."""
        return project_root / "docs"

    def test_docs_directory_exists(self, docs_dir):
        """docsディレクトリが存在することを確認."""
        # Arrange (準備)
        # Setup

        # Act (実行)
        exists = docs_dir.exists()
        is_dir = docs_dir.is_dir()

        # Assert (検証)
        assert exists, "docs directory should exist"
        assert is_dir, "docs should be a directory"

    def test_required_subdirectories_exist(self, docs_dir):
        """必須のサブディレクトリが存在することを確認."""
        # Arrange (準備)
        required_subdirs = [
            "api",
            "architecture",
            "guides",
            "development",
            "tasks",
            "migration",
            "implementation",
            "old",
        ]

        # Act (実行)
        # Execute

        # Assert (検証)
        for subdir in required_subdirs:
            subdir_path = docs_dir / subdir
            assert (
                subdir_path.exists()
            ), f"Required subdirectory '{subdir}' should exist"
            assert subdir_path.is_dir(), f"'{subdir}' should be a directory"

    def test_api_directory_structure(self, docs_dir):
        """apiディレクトリの必須ファイルが存在することを確認."""
        # Arrange (準備)
        api_dir = docs_dir / "api"
        required_files = [
            "api_specification.md",
        ]

        # Act (実行)
        # Execute

        # Assert (検証)
        for file_name in required_files:
            file_path = api_dir / file_name
            assert (
                file_path.exists()
            ), f"API file '{file_name}' should exist in api directory"

    def test_architecture_directory_structure(self, docs_dir):
        """architectureディレクトリの必須ファイルが存在することを確認."""
        # Arrange (準備)
        arch_dir = docs_dir / "architecture"
        required_files = [
            "system_overview.md",
            "database_design.md",
            "project_architecture.md",
            "data_flow.md",
        ]

        # Act (実行)
        # Execute

        # Assert (検証)
        for file_name in required_files:
            file_path = arch_dir / file_name
            assert (
                file_path.exists()
            ), f"Architecture file '{file_name}' should exist in architecture directory"

    def test_guides_directory_structure(self, docs_dir):
        """guidesディレクトリの必須ファイルが存在することを確認."""
        # Arrange (準備)
        guides_dir = docs_dir / "guides"
        required_files = [
            "DATABASE_SETUP.md",
            "setup_guide.md",
            "backup_procedures.md",
            "performance_optimization_guide.md",
        ]

        # Act (実行)
        # Execute

        # Assert (検証)
        for file_name in required_files:
            file_path = guides_dir / file_name
            assert (
                file_path.exists()
            ), f"Guide file '{file_name}' should exist in guides directory"

    def test_development_directory_structure(self, docs_dir):
        """developmentディレクトリの必須ファイルが存在することを確認."""
        # Arrange (準備)
        dev_dir = docs_dir / "development"
        required_files = [
            "testing_strategy.md",
            "testing_guide.md",
            "git_workflow.md",
            "coding_standards.md",
        ]

        # Act (実行)
        # Execute

        # Assert (検証)
        for file_name in required_files:
            file_path = dev_dir / file_name
            assert (
                file_path.exists()
            ), f"Development file '{file_name}' should exist in development directory"

    def test_integration_documents_exist(self, docs_dir):
        """機能別統合ドキュメントが存在することを確認."""
        # Arrange (準備)
        integration_files = [
            "bulk-data-fetch.md",
            "jpx-sequential-fetch.md",
            "monitoring-guide.md",
        ]

        # Act (実行)
        # Execute

        # Assert (検証)
        for file_name in integration_files:
            file_path = docs_dir / file_name
            assert (
                file_path.exists()
            ), f"Integration document '{file_name}' should exist in docs directory"

    def test_readme_mentioned_files_exist(self, docs_dir):
        """README.mdで言及されているファイルが実際に存在することを確認（警告のみ）."""
        # Arrange (準備)
        readme_path = docs_dir / "README.md"
        if not readme_path.exists():
            pytest.skip("README.md not found")

        # Act (実行)
        with open(readme_path, "r", encoding="utf-8") as f:
            readme_content = f.read()

        import re

        link_pattern = r"\[([^\]]+)\]\(([^)]+\.md)\)"
        mentioned_files = re.findall(link_pattern, readme_content)

        missing_files = []
        for link_text, file_path in mentioned_files:
            if not file_path.startswith("/"):
                full_path = docs_dir / file_path
            else:
                full_path = docs_dir.parent / file_path.lstrip("/")

            if not full_path.exists():
                missing_files.append(f"{file_path} (link text: '{link_text}')")

        # Assert (検証)
        if missing_files:
            print(
                f"Warning: Files mentioned in README.md do not exist: {missing_files}"
            )

    def test_no_orphaned_files(self, docs_dir):
        """README.mdで言及されていない孤立したファイルがないことを確認（警告のみ）."""
        # Arrange (準備)
        readme_path = docs_dir / "README.md"
        if not readme_path.exists():
            pytest.skip("README.md not found")

        # Act (実行)
        with open(readme_path, "r", encoding="utf-8") as f:
            readme_content = f.read()

        all_md_files = []
        for md_file in docs_dir.rglob("*.md"):
            if md_file.name != "README.md":
                relative_path = md_file.relative_to(docs_dir)
                all_md_files.append(str(relative_path))

        orphaned_files = []
        for file_path in all_md_files:
            file_name = Path(file_path).stem
            if (
                file_name not in readme_content
                and file_path not in readme_content
            ):
                orphaned_files.append(file_path)

        # Assert (検証)
        if orphaned_files:
            print(
                f"Warning: Orphaned files found (not mentioned in README.md): {orphaned_files}"
            )

    def test_all_subdirectories_have_readme(self, docs_dir):
        """すべてのサブディレクトリにREADME.mdが存在することを確認（存在する場合のみ）."""
        # Arrange (準備)
        subdirectories = [
            "api",
            "architecture",
            "guides",
            "development",
            "tasks",
            "migration",
            "implementation",
            "old",
        ]

        # Act (実行)
        # Execute

        # Assert (検証)
        for subdir_name in subdirectories:
            subdir_path = docs_dir / subdir_name
            if subdir_path.exists():
                readme_path = subdir_path / "README.md"
                if not readme_path.exists():
                    print(
                        f"Warning: README.md does not exist in {subdir_name} directory"
                    )

    def test_markdown_files_only(self, docs_dir):
        """docsディレクトリ内にMarkdownファイル以外の不適切なファイルがないことを確認."""
        # Arrange (準備)
        allowed_extensions = {".md"}

        def check_directory(directory):
            """ディレクトリ内のファイル拡張子をチェック."""
            for item in directory.iterdir():
                if item.is_file():
                    assert (
                        item.suffix in allowed_extensions
                    ), f"Non-markdown file found: {item}"
                elif item.is_dir():
                    check_directory(item)

        # Act (実行)
        # Execute

        # Assert (検証)
        check_directory(docs_dir)


class TestDocsFileMovementDetection:
    """docsディレクトリ内のファイル移動・修正を検出するテストクラス."""

    @pytest.fixture
    def project_root(self):
        """プロジェクトルートディレクトリのパスを取得."""
        return Path(__file__).parent.parent.parent

    @pytest.fixture
    def docs_dir(self, project_root):
        """docsディレクトリのパスを取得."""
        return project_root / "docs"

    def test_important_files_not_moved(self, docs_dir):
        """重要なファイルが移動されていないことを確認."""
        # Arrange (準備)
        important_files = [
            "README.md",
            "api/api_specification.md",
            "architecture/system_overview.md",
            "guides/DATABASE_SETUP.md",
            "development/testing_strategy.md",
        ]

        # Act (実行)
        # Execute

        # Assert (検証)
        for file_path in important_files:
            full_path = docs_dir / file_path
            assert (
                full_path.exists()
            ), f"Important file '{file_path}' should not be moved from its expected location"

    def test_directory_structure_integrity(self, docs_dir):
        """ディレクトリ構造の整合性を確認."""
        # Arrange (準備)
        expected_structure = {
            "api": ["api_specification.md"],
            "architecture": [
                "system_overview.md",
                "database_design.md",
                "project_architecture.md",
                "data_flow.md",
            ],
            "guides": [
                "DATABASE_SETUP.md",
                "setup_guide.md",
                "backup_procedures.md",
                "performance_optimization_guide.md",
            ],
            "development": [
                "testing_strategy.md",
                "testing_guide.md",
                "git_workflow.md",
                "coding_standards.md",
            ],
        }

        # Act (実行)
        # Execute

        # Assert (検証)
        for dir_name, expected_files in expected_structure.items():
            dir_path = docs_dir / dir_name
            assert dir_path.exists(), f"Directory '{dir_name}' should exist"

            for file_name in expected_files:
                file_path = dir_path / file_name
                assert (
                    file_path.exists()
                ), f"File '{file_name}' should exist in '{dir_name}' directory"


if __name__ == "__main__":
    # テストを直接実行する場合
    pytest.main([__file__, "-v"])
