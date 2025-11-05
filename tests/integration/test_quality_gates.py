"""品質ゲート設定のテスト.

品質ゲートの設定が正しく機能しているかを検証するテスト。
"""

from pathlib import Path
import subprocess

import pytest


pytestmark = pytest.mark.integration


class TestQualityGateConfiguration:
    """品質ゲート設定のテスト."""

    def test_pyproject_toml_coverage_threshold_configured(self):
        """pyproject.tomlにカバレッジ閾値が設定されている."""
        # Arrange
        pyproject_path = Path("pyproject.toml")

        # Act
        content = pyproject_path.read_text(encoding="utf-8")

        # Assert
        assert (
            "--cov-fail-under=70" in content
        ), "pyproject.tomlにカバレッジ閾値70%が設定されていません"

    def test_flake8_complexity_threshold_configured(self):
        """.flake8ファイルに複雑度閾値が設定されている."""
        # Arrange
        flake8_path = Path(".flake8")

        # Act
        content = flake8_path.read_text(encoding="utf-8")

        # Assert
        assert "max-complexity" in content, ".flake8に複雑度設定がありません"
        assert "max-complexity = 10" in content, ".flake8に複雑度閾値10が設定されていません"

    def test_precommit_has_quality_gates(self):
        """pre-commit設定に品質ゲートが設定されている."""
        # Arrange
        precommit_path = Path(".pre-commit-config.yaml")

        # Act
        content = precommit_path.read_text(encoding="utf-8")

        # Assert
        # 複雑度チェック
        assert "complexity-check" in content, "pre-commit設定に複雑度チェックが設定されていません"
        assert (
            "--max-complexity=10" in content or "max-complexity" in content
        ), "pre-commit設定に複雑度閾値が設定されていません"

        # Lintチェック
        assert "flake8" in content, "pre-commit設定にFlake8チェックが設定されていません"

        # 型チェック
        assert "mypy" in content, "pre-commit設定に型チェックが設定されていません"

    def test_quality_gates_documentation_exists(self):
        """品質ゲート設定ドキュメントがgit_workflow.mdに存在する."""
        # Arrange
        doc_path = Path("docs/standards/git-workflow.md")

        # Act & Assert
        assert doc_path.exists(), "git-workflow.mdが存在しません"

        content = doc_path.read_text(encoding="utf-8")
        assert "CI/CD" in content, "git-workflow.mdにCI/CD関連セクションがありません"

    def test_documentation_contains_required_sections(self):
        """git-workflow.mdに開発ワークフローの必要なセクションが含まれている."""
        # Arrange
        doc_path = Path("docs/standards/git-workflow.md")
        content = doc_path.read_text(encoding="utf-8")

        # Act & Assert
        required_sections = [
            "## 1. 開発ワークフロー概要",
            "## 2. Issue管理とタスクトラッキング",
            "## 3. ブランチ戦略",
            "## 4. CI/CD",
            "## 5. まとめ",
        ]

        for section in required_sections:
            assert section in content, f"ドキュメントに必須セクション '{section}' が含まれていません"


class TestQualityGateExecution:
    """品質ゲート実行のテスト."""

    def test_flake8_complexity_check_executable(self):
        """flake8複雑度チェックが実行可能."""
        # Arrange & Act
        result = subprocess.run(
            ["flake8", "app/", "--select=C901", "--exit-zero"],
            capture_output=True,
            text=True,
        )

        # Assert
        assert result.returncode == 0, "flake8複雑度チェックの実行に失敗しました"

    def test_flake8_style_check_executable(self):
        """flake8スタイルチェックが実行可能."""
        # Arrange & Act
        result = subprocess.run(
            ["flake8", "app/", "--exit-zero"],
            capture_output=True,
            text=True,
        )

        # Assert
        assert result.returncode == 0, "flake8スタイルチェックの実行に失敗しました"

    def test_mypy_type_check_executable(self):
        """mypy型チェックが実行可能."""
        # Arrange & Act
        result = subprocess.run(
            ["mypy", "app/", "--exclude", "tests/"],
            capture_output=True,
            text=True,
        )

        # Assert
        # mypyは警告でも0以外を返すことがあるので、実行可能かのみチェック
        assert result.returncode in [0, 1], "mypy型チェックの実行に失敗しました"


class TestDependencies:
    """依存関係のテスト."""

    def test_dev_requirements_has_quality_tools(self):
        """requirements-dev.txtに品質ツールが含まれている."""
        # Arrange
        req_path = Path("requirements-dev.txt")
        content = req_path.read_text(encoding="utf-8")

        # Act & Assert
        required_tools = [
            "flake8",
            "mypy",
            "pytest-cov",
            "black",
            "isort",
        ]

        for tool in required_tools:
            assert tool in content, f"requirements-dev.txtに{tool}が含まれていません"

    def test_mccabe_package_available(self):
        """mccabeパッケージが利用可能."""
        # Arrange
        req_path = Path("requirements-dev.txt")
        content = req_path.read_text(encoding="utf-8")

        # Act & Assert
        assert "mccabe" in content, "requirements-dev.txtにmccabeが含まれていません"


class TestPreCommitHookScript:
    """pre-commitフックスクリプトのテスト."""

    def test_hook_script_exists(self):
        """run_check_with_status.pyが存在する."""
        # Arrange
        script_path = Path("scripts/hooks/run_check_with_status.py")

        # Act & Assert
        assert script_path.exists(), "run_check_with_status.pyが存在しません"

    def test_hook_script_supports_complexity_check(self):
        """フックスクリプトが複雑度チェックをサポートしている."""
        # Arrange
        script_path = Path("scripts/hooks/run_check_with_status.py")
        content = script_path.read_text(encoding="utf-8")

        # Act & Assert
        assert (
            "complexity" in content
        ), "run_check_with_status.pyに複雑度チェックが含まれていません"
        assert "run_complexity" in content, "run_complexity関数が定義されていません"


class TestCoverageConfiguration:
    """カバレッジ設定のテスト."""

    def test_coverage_threshold_in_pyproject(self):
        """pyproject.tomlにカバレッジ閾値が設定されている."""
        # Arrange
        pyproject_path = Path("pyproject.toml")
        content = pyproject_path.read_text(encoding="utf-8")

        # Act & Assert
        assert (
            "--cov-fail-under=70" in content
        ), "pyproject.tomlにカバレッジ閾値70%が設定されていません"

    def test_coverage_in_github_actions(self):
        """Coverage check is configured in GitHub Actions workflow."""
        # Arrange
        workflow_path = Path(".github/workflows/quality.yml")
        content = workflow_path.read_text(encoding="utf-8")

        # Act & Assert
        assert "--cov=app" in content, "GitHub Actionsにカバレッジ測定対象が設定されていません"
        assert (
            "--cov-fail-under=70" in content
        ), "GitHub Actionsにカバレッジ閾値70%が設定されていません"
        assert (
            "--cov-report=xml" in content or "--cov-report=term" in content
        ), "GitHub Actionsにカバレッジレポート形式が設定されていません"
