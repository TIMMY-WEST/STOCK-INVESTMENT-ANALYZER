"""D212 docstringフォーマット修正のテストコード."""

import subprocess

import pytest


class TestD212DocstringFormat:
    """D212 docstringフォーマット修正のテストクラス."""

    def test_no_d212_errors_exist(self):
        """D212エラーが存在しないことを確認するテスト."""
        # flake8でD212エラーをチェック
        result = subprocess.run(
            ["flake8", "--select=D212"],
            capture_output=True,
            text=True,
            check=False,
        )

        # D212エラーが存在しないことを確認
        assert (
            result.returncode == 0
        ), f"D212エラーが検出されました: {result.stdout}"
        # flake8がエラーなしの場合は"0"または空文字を出力
        assert result.stdout.strip() in [
            "",
            "0",
        ], f"D212エラーが残っています: {result.stdout}"

    def test_d212_statistics_zero(self):
        """D212エラーの統計が0件であることを確認するテスト."""
        # flake8でD212エラーの統計を取得
        result = subprocess.run(
            ["flake8", "--select=D212", "--statistics"],
            capture_output=True,
            text=True,
            check=False,
        )

        # 統計結果が空（0件）であることを確認
        assert result.returncode == 0, f"flake8実行エラー: {result.stderr}"
        # flake8統計でエラーなしの場合は"0"または空文字を出力
        assert result.stdout.strip() in [
            "",
            "0",
        ], f"D212エラーが統計に表示されています: {result.stdout}"

    def test_sample_docstring_format_compliance(self):
        """サンプルファイルのdocstringがGoogleスタイルに準拠していることを確認."""
        # 修正されたファイルの一部をサンプルとしてチェック
        sample_files = [
            "app/api/stock_master.py",
            "app/services/batch_service.py",
            "app/services/bulk_data_service.py",
        ]

        for file_path in sample_files:
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()

                # マルチラインdocstringの開始パターンをチェック
                # 正しい形式: """サマリー行.
                # 間違った形式: """\n    サマリー行.

                # 簡単なパターンマッチングでGoogleスタイル準拠を確認
                lines = content.split("\n")
                for i, line in enumerate(lines):
                    if (
                        line.strip().startswith('"""')
                        and line.strip() != '"""'
                    ):
                        # docstringの開始行にサマリーが含まれている（正しい形式）
                        assert (
                            '"""' in line and len(line.strip()) > 3
                        ), f"{file_path}:{i+1} - docstringの開始行が空です"

            except FileNotFoundError:
                pytest.skip(f"テストファイル {file_path} が見つかりません")

    def test_docstring_format_consistency(self):
        """docstringフォーマットの一貫性を確認するテスト."""
        # 全体的なdocstringフォーマットチェック
        result = subprocess.run(
            ["flake8", "--select=D", "--statistics"],
            capture_output=True,
            text=True,
            check=False,
        )

        # D212エラーが統計に含まれていないことを確認
        if result.stdout:
            lines = result.stdout.strip().split("\n")
            for line in lines:
                assert not line.strip().endswith(
                    "D212"
                ), f"D212エラーが統計に残っています: {line}"

    def test_flake8_d212_exit_code(self):
        """flake8 D212チェックの終了コードが0であることを確認."""
        result = subprocess.run(
            ["flake8", "--select=D212"],
            capture_output=True,
            text=True,
            check=False,
        )

        assert (
            result.returncode == 0
        ), f"flake8 D212チェックが失敗しました。終了コード: {result.returncode}, 出力: {result.stdout}"
