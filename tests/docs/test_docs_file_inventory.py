"""ドキュメントファイルの存在確認とファイル増減検出テスト.

このモジュールは以下をテストします:
- 全ドキュメントファイルの存在確認
- ファイルが追加された場合の検出
- ファイルが削除された場合の検出
"""

from pathlib import Path

import pytest


pytestmark = pytest.mark.docs


class TestDocsFileInventory:
    """ドキュメントファイルのインベントリテストクラス."""

    @pytest.fixture
    def project_root(self) -> Path:
        """プロジェクトルートディレクトリのパスを取得."""
        return Path(__file__).parent.parent.parent

    @pytest.fixture
    def docs_dir(self, project_root: Path) -> Path:
        """docsディレクトリのパスを取得."""
        return project_root / "docs"

    @pytest.fixture
    def expected_files(self) -> set[str]:
        """期待されるドキュメントファイルのセットを取得.

        ファイルが追加された場合、このリストを更新すること。
        """
        return {
            # ルートディレクトリ
            "README.md",
            # api/
            "api/README.md",
            "api/api_reference.md",
            "api/api_usage_guide.md",
            "api/versioning_guide.md",
            # architecture/
            "architecture/README.md",
            "architecture/architecture_overview.md",
            "architecture/component_dependency.md",
            "architecture/database_design.md",
            "architecture/data_flow.md",
            "architecture/frontend_design.md",
            "architecture/service_responsibilities.md",
            # ci-cd/
            "ci-cd/README.md",
            "ci-cd/pipeline-config.md",
            "ci-cd/pre_commit_setup.md",
            # guides/
            "guides/README.md",
            "guides/backup_procedures.md",
            "guides/bulk-data-fetch.md",
            "guides/DATABASE_SETUP.md",
            "guides/development-workflow.md",
            "guides/formatter_linter_guide.md",
            "guides/jpx-sequential-fetch.md",
            "guides/monitoring-guide.md",
            "guides/performance_optimization_guide.md",
            "guides/setup_guide.md",
            "guides/troubleshooting.md",
            # standards/
            "standards/README.md",
            "standards/coding-standards.md",
            "standards/CSS_BEM_METHODOLOGY.md",
            "standards/exception_handling.md",
            "standards/frontend_guide.md",
            "standards/git-workflow.md",
            "standards/testing-standards.md",
            "standards/type_hints_guide.md",
            # tasks/
            "tasks/README.md",
            "tasks/issues.md",
            "tasks/milestones.md",
        }

    def test_all_expected_files_exist(
        self, docs_dir: Path, expected_files: set[str]
    ) -> None:
        """期待される全てのファイルが存在することを確認."""
        # Arrange (準備)
        # フィクスチャで準備済み

        # Act (実行)
        missing_files = []
        for file_path in expected_files:
            full_path = docs_dir / file_path
            if not full_path.exists():
                missing_files.append(file_path)

        # Assert (検証)
        assert not missing_files, (
            f"以下のファイルが見つかりません: " f"{', '.join(sorted(missing_files))}"
        )

    def test_no_unexpected_files_added(
        self, docs_dir: Path, expected_files: set[str]
    ) -> None:
        """予期しないファイルが追加されていないことを確認.

        新しいファイルが追加された場合、expected_filesを更新してください。
        """
        # Arrange (準備)
        exclude_patterns = {
            "__pycache__",
            ".DS_Store",
            "Thumbs.db",
            ".pytest_cache",
        }
        exclude_dirs = {"old", "archive"}

        # Act (実行)
        actual_files = set()
        for md_file in docs_dir.rglob("*.md"):
            # 除外ディレクトリをスキップ
            if any(excluded in md_file.parts for excluded in exclude_dirs):
                continue

            # 除外パターンに一致するファイルをスキップ
            if any(pattern in str(md_file) for pattern in exclude_patterns):
                continue

            relative_path = md_file.relative_to(docs_dir)
            actual_files.add(str(relative_path).replace("\\", "/"))

        unexpected_files = actual_files - expected_files

        # Assert (検証)
        assert not unexpected_files, (
            f"以下の予期しないファイルが追加されています。\n"
            f"expected_filesフィクスチャを更新してください: "
            f"{', '.join(sorted(unexpected_files))}"
        )

    def test_file_count_matches_expectation(
        self, docs_dir: Path, expected_files: set[str]
    ) -> None:
        """ファイル数が期待値と一致することを確認."""
        # Arrange (準備)
        exclude_patterns = {
            "__pycache__",
            ".DS_Store",
            "Thumbs.db",
            ".pytest_cache",
        }
        exclude_dirs = {"old", "archive"}

        # Act (実行)
        actual_count = 0
        for md_file in docs_dir.rglob("*.md"):
            # 除外ディレクトリをスキップ
            if any(excluded in md_file.parts for excluded in exclude_dirs):
                continue

            if any(pattern in str(md_file) for pattern in exclude_patterns):
                continue
            actual_count += 1

        expected_count = len(expected_files)

        # Assert (検証)
        assert actual_count == expected_count, (
            f"ファイル数が一致しません。期待: {expected_count}, "
            f"実際: {actual_count}。\n"
            f"ファイルの追加または削除があった場合、"
            f"expected_filesフィクスチャを更新してください。"
        )


class TestDocsFileNaming:
    """ドキュメントファイルの命名規則テストクラス."""

    @pytest.fixture
    def project_root(self) -> Path:
        """プロジェクトルートディレクトリのパスを取得."""
        return Path(__file__).parent.parent.parent

    @pytest.fixture
    def docs_dir(self, project_root: Path) -> Path:
        """docsディレクトリのパスを取得."""
        return project_root / "docs"

    def test_markdown_files_have_md_extension(self, docs_dir: Path) -> None:
        """Markdownファイルが.md拡張子を持つことを確認."""
        # Arrange (準備)
        exclude_patterns = {"__pycache__", ".pytest_cache"}

        # Act (実行)
        non_md_files = []
        for file_path in docs_dir.rglob("*"):
            if not file_path.is_file():
                continue
            if any(pattern in str(file_path) for pattern in exclude_patterns):
                continue
            if file_path.suffix not in {".md"}:
                relative_path = file_path.relative_to(docs_dir)
                non_md_files.append(str(relative_path))

        # Assert (検証)
        assert not non_md_files, (
            f"以下のファイルが.md拡張子を持っていません: " f"{', '.join(non_md_files)}"
        )

    def test_no_spaces_in_filenames(self, docs_dir: Path) -> None:
        """ファイル名にスペースが含まれていないことを確認."""
        # Arrange (準備)
        # フィクスチャで準備済み

        # Act (実行)
        files_with_spaces = []
        for md_file in docs_dir.rglob("*.md"):
            if " " in md_file.name:
                relative_path = md_file.relative_to(docs_dir)
                files_with_spaces.append(str(relative_path))

        # Assert (検証)
        assert not files_with_spaces, (
            f"以下のファイル名にスペースが含まれています: " f"{', '.join(files_with_spaces)}"
        )


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
