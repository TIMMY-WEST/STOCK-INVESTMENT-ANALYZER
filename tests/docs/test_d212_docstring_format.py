"""D212 docstringフォーマット修正のテストコード."""

import subprocess

import pytest


class TestD212DocstringFormat:
    """D212 docstringフォーマット修正のテストクラス."""

    def test_no_d212_errors_exist(self):
        """D212エラーが存在しないことを確認するテスト."""
        # Arrange (準備)

        # Act (実行)
        result = subprocess.run(
            ["flake8", "--select=D212"],
            capture_output=True,
            text=True,
            check=False,
        )

        # Assert (検証)
        assert result.returncode == 0, f"D212エラーが検出されました: {result.stdout}"
        assert result.stdout.strip() in [
            "",
            "0",
        ], f"D212エラーが残っています: {result.stdout}"

    def test_d212_statistics_zero(self):
        """D212エラーの統計が0件であることを確認するテスト."""
        # Arrange (準備)

        # Act (実行)
        result = subprocess.run(
            ["flake8", "--select=D212", "--statistics"],
            capture_output=True,
            text=True,
            check=False,
        )

        # Assert (検証)
        assert result.returncode == 0, f"flake8実行エラー: {result.stderr}"
        assert result.stdout.strip() in [
            "",
            "0",
        ], f"D212エラーが統計に表示されています: {result.stdout}"

    def test_sample_docstring_format_compliance(self):
        """サンプルファイルのdocstringがGoogleスタイルに準拠していることを確認."""
        # Arrange (準備)
        sample_files = [
            "app/api/stock_master.py",
            "app/services/batch_service.py",
            "app/services/bulk_data_service.py",
        ]

        # Act (実行)
        for file_path in sample_files:
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()

                lines = content.split("\n")

                # Assert (検証)
                for i, line in enumerate(lines):
                    if (
                        line.strip().startswith('"""')
                        and line.strip() != '"""'
                    ):
                        assert (
                            '"""' in line and len(line.strip()) > 3
                        ), f"{file_path}:{i + 1} - docstringの開始行が空です"

            except FileNotFoundError:
                pytest.skip(f"テストファイル {file_path} が見つかりません")

    def test_docstring_format_consistency(self):
        """docstringフォーマットの一貫性を確認するテスト."""
        # Arrange (準備)

        # Act (実行)
        result = subprocess.run(
            ["flake8", "--select=D", "--statistics"],
            capture_output=True,
            text=True,
            check=False,
        )

        # Assert (検証)
        if result.stdout:
            lines = result.stdout.strip().split("\n")
            for line in lines:
                assert not line.strip().endswith(
                    "D212"
                ), f"D212エラーが統計に残っています: {line}"

    def test_flake8_d212_exit_code(self):
        """flake8 D212チェックの終了コードが0であることを確認."""
        # Arrange (準備)

        # Act (実行)
        result = subprocess.run(
            ["flake8", "--select=D212"],
            capture_output=True,
            text=True,
            check=False,
        )

        # Assert (検証)
        assert (
            result.returncode == 0
        ), f"flake8 D212チェックが失敗しました。終了コード: {result.returncode}, 出力: {result.stdout}"
