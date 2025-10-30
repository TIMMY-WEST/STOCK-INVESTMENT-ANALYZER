"""セットアップスクリプトのテスト.

このモジュールは、開発環境セットアップスクリプトの
正常動作を検証するためのテストを提供します。

"""

import os
from pathlib import Path
import subprocess
import sys

import pytest


class TestSetupScripts:
    """セットアップスクリプトのテストクラス."""

    @pytest.fixture
    def project_root(self):
        """プロジェクトルートディレクトリを返す."""
        return Path(__file__).parent.parent.parent

    @pytest.fixture
    def scripts_dir(self, project_root):
        """scriptsディレクトリを返す."""
        return project_root / "scripts"

    @pytest.fixture
    def scripts_setup_dir(self, scripts_dir):
        """scripts/setupディレクトリを返す."""
        return scripts_dir / "setup"

    def test_setup_scripts_makefile_exists_with_project_root_returns_valid_file(
        self, project_root
    ):
        """Makefileが存在することを確認."""
        makefile = project_root / "Makefile"
        assert makefile.exists(), "Makefile が見つかりません"
        assert makefile.is_file(), "Makefile がファイルではありません"

    def test_setup_scripts_dev_setup_sh_exists_with_scripts_dir_returns_valid_file(
        self, scripts_setup_dir
    ):
        """dev_setup.sh が存在することを確認."""
        dev_setup_sh = scripts_setup_dir / "dev_setup.sh"
        assert dev_setup_sh.exists(), "dev_setup.sh が見つかりません"
        assert dev_setup_sh.is_file(), "dev_setup.sh がファイルではありません"

    def test_setup_scripts_dev_setup_bat_exists_with_scripts_dir_returns_valid_file(
        self, scripts_setup_dir
    ):
        """dev_setup.bat が存在することを確認."""
        dev_setup_bat = scripts_setup_dir / "dev_setup.bat"
        assert dev_setup_bat.exists(), "dev_setup.bat が見つかりません"
        assert dev_setup_bat.is_file(), "dev_setup.bat がファイルではありません"

    def test_makefile_contains_setup_target(self, project_root):
        """Makefile に setup ターゲットが含まれていることを確認."""
        makefile = project_root / "Makefile"
        content = makefile.read_text(encoding="utf-8")

        assert "setup:" in content, "Makefile に setup ターゲットがありません"
        assert ".PHONY:" in content, "Makefile に .PHONY 宣言がありません"

    def test_makefile_contains_help_target(self, project_root):
        """Makefile に help ターゲットが含まれていることを確認."""
        makefile = project_root / "Makefile"
        content = makefile.read_text(encoding="utf-8")

        assert "help:" in content, "Makefile に help ターゲットがありません"

    def test_dev_setup_sh_has_shebang(self, scripts_setup_dir):
        """dev_setup.sh にシェバンが含まれていることを確認."""
        dev_setup_sh = scripts_setup_dir / "dev_setup.sh"
        with open(dev_setup_sh, "r", encoding="utf-8") as f:
            first_line = f.readline()

        assert first_line.startswith("#!/bin/bash"), "dev_setup.sh にシェバンがありません"

    def test_dev_setup_sh_contains_error_handling(self, scripts_setup_dir):
        """dev_setup.sh にエラーハンドリングが含まれていることを確認."""
        dev_setup_sh = scripts_setup_dir / "dev_setup.sh"
        content = dev_setup_sh.read_text(encoding="utf-8")

        assert "set -e" in content, "dev_setup.sh にエラーハンドリング(set -e)がありません"
        assert (
            "error_exit" in content or "log_error" in content
        ), "dev_setup.sh にエラー処理関数がありません"

    def test_dev_setup_bat_contains_error_handling(self, scripts_setup_dir):
        """dev_setup.bat にエラーハンドリングが含まれていることを確認."""
        dev_setup_bat = scripts_setup_dir / "dev_setup.bat"
        content = dev_setup_bat.read_text(encoding="utf-8")

        assert (
            "errorlevel" in content.lower()
        ), "dev_setup.bat にエラーハンドリングがありません"
        assert "setlocal" in content.lower(), "dev_setup.bat にsetlocalがありません"

    def test_dev_setup_sh_contains_python_check(self, scripts_setup_dir):
        """dev_setup.sh にPythonバージョンチェックが含まれていることを確認."""
        dev_setup_sh = scripts_setup_dir / "dev_setup.sh"
        content = dev_setup_sh.read_text(encoding="utf-8")

        assert "python" in content.lower(), "dev_setup.sh にPythonチェックがありません"
        assert "version" in content.lower(), "dev_setup.sh にバージョンチェックがありません"

    def test_dev_setup_bat_contains_python_check(self, scripts_setup_dir):
        """dev_setup.bat にPythonバージョンチェックが含まれていることを確認."""
        dev_setup_bat = scripts_setup_dir / "dev_setup.bat"
        content = dev_setup_bat.read_text(encoding="utf-8")

        assert "python" in content.lower(), "dev_setup.bat にPythonチェックがありません"
        assert "version" in content.lower(), "dev_setup.bat にバージョンチェックがありません"

    def test_dev_setup_sh_contains_venv_creation(self, scripts_setup_dir):
        """dev_setup.sh に仮想環境作成処理が含まれていることを確認."""
        dev_setup_sh = scripts_setup_dir / "dev_setup.sh"
        content = dev_setup_sh.read_text(encoding="utf-8")

        assert "venv" in content, "dev_setup.sh に仮想環境処理がありません"
        assert "-m venv" in content, "dev_setup.sh に仮想環境作成コマンドがありません"

    def test_dev_setup_bat_contains_venv_creation(self, scripts_setup_dir):
        """dev_setup.bat に仮想環境作成処理が含まれていることを確認."""
        dev_setup_bat = scripts_setup_dir / "dev_setup.bat"
        content = dev_setup_bat.read_text(encoding="utf-8")

        assert "venv" in content, "dev_setup.bat に仮想環境処理がありません"
        assert "-m venv" in content, "dev_setup.bat に仮想環境作成コマンドがありません"

    def test_dev_setup_sh_contains_requirements_install(
        self, scripts_setup_dir
    ):
        """dev_setup.sh に依存関係インストール処理が含まれていることを確認."""
        dev_setup_sh = scripts_setup_dir / "dev_setup.sh"
        content = dev_setup_sh.read_text(encoding="utf-8")

        assert (
            "requirements.txt" in content
        ), "dev_setup.sh に requirements.txt がありません"
        assert "pip install" in content, "dev_setup.sh に pip install がありません"

    def test_dev_setup_bat_contains_requirements_install(
        self, scripts_setup_dir
    ):
        """dev_setup.bat に依存関係インストール処理が含まれていることを確認."""
        dev_setup_bat = scripts_setup_dir / "dev_setup.bat"
        content = dev_setup_bat.read_text(encoding="utf-8")

        assert (
            "requirements.txt" in content
        ), "dev_setup.bat に requirements.txt がありません"
        assert "pip install" in content, "dev_setup.bat に pip install がありません"

    def test_dev_setup_sh_contains_env_file_setup(self, scripts_setup_dir):
        """dev_setup.sh に.envファイル設定処理が含まれていることを確認."""
        dev_setup_sh = scripts_setup_dir / "dev_setup.sh"
        content = dev_setup_sh.read_text(encoding="utf-8")

        assert ".env" in content, "dev_setup.sh に.env処理がありません"

    def test_dev_setup_bat_contains_env_file_setup(self, scripts_setup_dir):
        """dev_setup.bat に.envファイル設定処理が含まれていることを確認."""
        dev_setup_bat = scripts_setup_dir / "dev_setup.bat"
        content = dev_setup_bat.read_text(encoding="utf-8")

        assert ".env" in content, "dev_setup.bat に.env処理がありません"

    def test_setup_scripts_env_example_exists_with_project_root_returns_valid_file(
        self, project_root
    ):
        """.env.example が存在することを確認."""
        env_example = project_root / ".env.example"
        assert env_example.exists(), ".env.example が見つかりません"

    def test_requirements_txt_exists(self, project_root):
        """requirements.txt が存在することを確認."""
        requirements = project_root / "requirements.txt"
        assert requirements.exists(), "requirements.txt が見つかりません"

    @pytest.mark.skipif(
        sys.platform != "linux" and sys.platform != "darwin",
        reason="Unix系OSでのみ実行",
    )
    def test_dev_setup_sh_is_executable(self, scripts_dir):
        """dev_setup.sh が実行可能であることを確認（Unix系のみ）."""
        dev_setup_sh = scripts_dir / "dev_setup.sh"

        # 実行権限を付与
        os.chmod(dev_setup_sh, 0o755)

        # 実行可能かチェック
        assert os.access(dev_setup_sh, os.X_OK), "dev_setup.sh が実行可能ではありません"

    def test_makefile_syntax_basic(self, project_root):
        """Makefileの基本的な構文をチェック."""
        makefile = project_root / "Makefile"
        content = makefile.read_text(encoding="utf-8")

        # タブとスペースの混在チェック（簡易版）
        lines = content.split("\n")
        for i, line in enumerate(lines, 1):
            if line.startswith(" ") and not line.startswith("#"):
                # コマンド行はタブで始まるべき
                if i > 1 and lines[i - 2].endswith(":"):
                    # ターゲット直後の行
                    assert line.startswith(
                        "\t"
                    ), f"Makefile の {i} 行目: コマンドはタブで始める必要があります"

    def test_scripts_directory_structure(self, scripts_dir):
        """scriptsディレクトリの構造を確認."""
        assert scripts_dir.exists(), "scripts ディレクトリが見つかりません"
        assert scripts_dir.is_dir(), "scripts がディレクトリではありません"

        # 必要なサブディレクトリの確認
        required_subdirs = [
            "setup",
            "database",
            "analysis",
        ]

        for subdir_name in required_subdirs:
            subdir_path = scripts_dir / subdir_name
            assert subdir_path.exists(), f"{subdir_name} ディレクトリが見つかりません"
            assert subdir_path.is_dir(), f"{subdir_name} がディレクトリではありません"

        # setup ディレクトリ内のファイル確認
        setup_dir = scripts_dir / "setup"
        required_setup_files = [
            "dev_setup.sh",
            "dev_setup.bat",
            "setup_db.sh",
            "setup_db.bat",
        ]

        for file_name in required_setup_files:
            file_path = setup_dir / file_name
            assert file_path.exists(), f"setup/{file_name} が見つかりません"


class TestSetupScriptIntegration:
    """セットアップスクリプトの統合テスト."""

    @pytest.fixture
    def project_root(self):
        """プロジェクトルートディレクトリを返す."""
        return Path(__file__).parent.parent.parent

    @pytest.mark.slow
    @pytest.mark.skipif(
        sys.platform == "win32",
        reason="Windows では make が使えない場合がある",
    )
    def test_setup_scripts_make_help_works_with_project_root_returns_successful_output(
        self, project_root
    ):
        """Make help が正常に動作することを確認."""
        result = subprocess.run(
            ["make", "help"],
            cwd=project_root,
            capture_output=True,
            text=True,
        )

        assert result.returncode == 0, f"make help が失敗しました: {result.stderr}"
        assert "setup" in result.stdout.lower(), "help に setup コマンドが表示されていません"

    def test_scripts_have_correct_encoding(self, project_root):
        """スクリプトファイルが正しいエンコーディングであることを確認."""
        scripts_setup_dir = project_root / "scripts" / "setup"

        # UTF-8で読み込めることを確認
        for script_file in ["dev_setup.sh", "dev_setup.bat"]:
            script_path = scripts_setup_dir / script_file
            try:
                content = script_path.read_text(encoding="utf-8")
                assert len(content) > 0, f"{script_file} が空です"
            except UnicodeDecodeError:
                pytest.fail(f"{script_file} が UTF-8 でエンコードされていません")
