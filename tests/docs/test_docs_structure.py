"""docsディレクトリの構造に関するテストコード.

このテストファイルは、docsディレクトリの構造とファイルの存在を検証します。
"""

from pathlib import Path

import pytest


pytestmark = pytest.mark.docs


class TestDocsStructure:
    """ドキュメントディレクトリ構造のテストクラス."""

    @pytest.fixture
    def project_root(self) -> Path:
        """プロジェクトルートディレクトリのパスを取得."""
        return Path(__file__).parent.parent.parent

    @pytest.fixture
    def docs_dir(self, project_root: Path) -> Path:
        """docsディレクトリのパスを取得."""
        return project_root / "docs"

    def test_docs_directory_exists(self, docs_dir: Path) -> None:
        """docsディレクトリが存在することを確認."""
        # Arrange (準備)
        # フィクスチャで準備済み

        # Act (実行)
        exists = docs_dir.exists()
        is_dir = docs_dir.is_dir()

        # Assert (検証)
        assert exists, "docs directory should exist"
        assert is_dir, "docs should be a directory"

    def test_required_subdirectories_exist(self, docs_dir: Path) -> None:
        """必須のサブディレクトリが存在することを確認."""
        # Arrange (準備)
        required_subdirs = [
            "api",
            "architecture",
            "guides",
            "standards",
            "ci-cd",
            "tasks",
            "archive",
            "old",
        ]

        # Act (実行)
        # 検証処理で実行

        # Assert (検証)
        for subdir in required_subdirs:
            subdir_path = docs_dir / subdir
            assert (
                subdir_path.exists()
            ), f"Required subdirectory '{subdir}' should exist"
            assert subdir_path.is_dir(), f"'{subdir}' should be a directory"

    def test_main_readme_exists(self, docs_dir: Path) -> None:
        """docs/README.mdが存在することを確認."""
        # Arrange (準備)
        readme_path = docs_dir / "README.md"

        # Act (実行)
        exists = readme_path.exists()
        is_file = readme_path.is_file()

        # Assert (検証)
        assert exists, "docs/README.md should exist"
        assert is_file, "README.md should be a file"

    @pytest.mark.parametrize(
        "subdir",
        [
            "api",
            "architecture",
            "guides",
            "standards",
            "ci-cd",
            "tasks",
            "archive",
        ],
    )
    def test_subdirectory_readme_exists(
        self, docs_dir: Path, subdir: str
    ) -> None:
        """各サブディレクトリにREADME.mdが存在することを確認."""
        # Arrange (準備)
        readme_path = docs_dir / subdir / "README.md"

        # Act (実行)
        exists = readme_path.exists()
        is_file = readme_path.is_file()

        # Assert (検証)
        assert exists, f"README.md should exist in {subdir} directory"
        assert is_file, f"{subdir}/README.md should be a file"

    def test_all_markdown_subdirectories_have_readme(
        self, docs_dir: Path
    ) -> None:
        """Markdownファイルを含む全サブディレクトリにREADME.mdがあることを確認.

        old/ディレクトリは除外（README不要）
        """
        # Arrange (準備)
        exclude_dirs = {"old"}
        missing_readme = []

        # Act (実行)
        for subdir in docs_dir.iterdir():
            if not subdir.is_dir() or subdir.name in exclude_dirs:
                continue

            has_markdown = any(subdir.glob("*.md"))
            if has_markdown:
                readme_path = subdir / "README.md"
                if not readme_path.exists():
                    missing_readme.append(subdir.name)

        # Assert (検証)
        assert not missing_readme, (
            f"以下のサブディレクトリにREADME.mdが存在しません: " f"{', '.join(missing_readme)}"
        )


class TestDocsFileMovementDetection:
    """docsディレクトリ内のファイル移動・修正を検出するテストクラス."""

    @pytest.fixture
    def project_root(self) -> Path:
        """プロジェクトルートディレクトリのパスを取得."""
        return Path(__file__).parent.parent.parent

    @pytest.fixture
    def docs_dir(self, project_root: Path) -> Path:
        """docsディレクトリのパスを取得."""
        return project_root / "docs"

    def test_important_files_not_moved(self, docs_dir: Path) -> None:
        """重要なファイルが移動されていないことを確認."""
        # Arrange (準備)
        important_files = [
            "README.md",
            "api/README.md",
            "api/api_reference.md",
            "api/api_usage_guide.md",
            "architecture/README.md",
            "architecture/architecture_overview.md",
            "architecture/database_design.md",
            "guides/README.md",
            "guides/setup_guide.md",
            "guides/DATABASE_SETUP.md",
            "standards/README.md",
            "standards/coding-standards.md",
            "standards/testing-standards.md",
            "standards/git-workflow.md",
            "ci-cd/README.md",
            "ci-cd/pipeline-config.md",
            "tasks/README.md",
            "archive/README.md",
        ]

        # Act (実行)
        missing_files = []
        for file_path in important_files:
            full_path = docs_dir / file_path
            if not full_path.exists():
                missing_files.append(file_path)

        # Assert (検証)
        assert not missing_files, (
            f"以下の重要なファイルが移動または削除されています: " f"{', '.join(missing_files)}"
        )

    def test_directory_structure_integrity(self, docs_dir: Path) -> None:
        """ディレクトリ構造の整合性を確認."""
        # Arrange (準備)
        expected_structure = {
            "api": [
                "api_reference.md",
                "api_usage_guide.md",
                "versioning_guide.md",
            ],
            "architecture": [
                "architecture_overview.md",
                "database_design.md",
                "data_flow.md",
                "frontend_design.md",
                "service_responsibilities.md",
                "component_dependency.md",
            ],
            "guides": [
                "DATABASE_SETUP.md",
                "setup_guide.md",
                "backup_procedures.md",
                "performance_optimization_guide.md",
                "bulk-data-fetch.md",
                "jpx-sequential-fetch.md",
                "monitoring-guide.md",
                "troubleshooting.md",
                "development-workflow.md",
                "formatter_linter_guide.md",
            ],
            "standards": [
                "coding-standards.md",
                "testing-standards.md",
                "git-workflow.md",
                "exception_handling.md",
                "type_hints_guide.md",
                "frontend_guide.md",
                "CSS_BEM_METHODOLOGY.md",
            ],
            "ci-cd": [
                "pipeline-config.md",
                "pre_commit_setup.md",
            ],
            "tasks": [
                "issues.md",
                "milestones.md",
            ],
        }

        # Act (実行)
        missing_files = []
        for dir_name, expected_files in expected_structure.items():
            dir_path = docs_dir / dir_name
            if not dir_path.exists():
                missing_files.append(f"Directory '{dir_name}' not found")
                continue

            for file_name in expected_files:
                file_path = dir_path / file_name
                if not file_path.exists():
                    missing_files.append(f"{dir_name}/{file_name}")

        # Assert (検証)
        assert not missing_files, (
            f"以下のファイルまたはディレクトリが見つかりません: " f"{', '.join(missing_files)}"
        )


if __name__ == "__main__":
    # テストを直接実行する場合
    pytest.main([__file__, "-v"])
