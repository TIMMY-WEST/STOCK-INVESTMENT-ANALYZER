"""README.mdの改善に関するテストコード.

このテストファイルは、README.mdファイルの内容と関連ファイルの存在を検証します。
"""

import os
from pathlib import Path
import re

import pytest


pytestmark = pytest.mark.docs


class TestReadmeImprovement:
    """README.mdの改善に関するテストクラス."""

    @pytest.fixture
    def project_root(self):
        """プロジェクトルートディレクトリのパスを取得."""
        return Path(__file__).parent.parent.parent

    @pytest.fixture
    def readme_content(self, project_root):
        """README.mdファイルの内容を取得."""
        readme_path = project_root / "README.md"
        with open(readme_path, "r", encoding="utf-8") as f:
            return f.read()

    def test_readme_file_exists(self, project_root):
        """README.mdファイルが存在することを確認."""
        # Arrange (準備)
        readme_path = project_root / "README.md"

        # Act (実行)
        exists = readme_path.exists()

        # Assert (検証)
        assert exists, "README.md file should exist"

    def test_license_file_exists(self, project_root):
        """LICENSEファイルが存在することを確認."""
        # Arrange (準備)
        license_path = project_root / "LICENSE"

        # Act (実行)
        exists = license_path.exists()

        # Assert (検証)
        assert exists, "LICENSE file should exist"

    def test_contributing_file_exists(self, project_root):
        """CONTRIBUTING.mdファイルが存在することを確認."""
        # Arrange (準備)
        contributing_path = (
            project_root / "docs" / "guides" / "contributing.md"
        )

        # Act (実行)
        exists = contributing_path.exists()

        # Assert (検証)
        assert exists, "CONTRIBUTING.md file should exist"

    def test_readme_has_badges(self, readme_content):
        """README.mdにバッジが含まれていることを確認."""
        # Arrange (準備)
        python_badge_pattern = r"!\[Python\]\(https://img\.shields\.io/badge/python-3\.8\+-blue\.svg\)"
        license_badge_pattern = r"!\[License\]\(https://img\.shields\.io/badge/license-MIT-green\.svg\)"

        # Act (実行)
        python_badge_result = re.search(python_badge_pattern, readme_content)
        license_badge_result = re.search(license_badge_pattern, readme_content)

        # Assert (検証)
        assert python_badge_result, "Python version badge should be present"
        assert license_badge_result, "License badge should be present"

    def test_readme_has_table_of_contents(self, readme_content):
        """README.mdに目次が含まれていることを確認."""
        # Arrange (準備)
        toc_patterns = [r"## 📋 目次", r"- \[.*\]\(#.*\)"]

        # Act (実行)
        # Execute

        # Assert (検証)
        for pattern in toc_patterns:
            assert re.search(
                pattern, readme_content
            ), f"Table of contents pattern '{pattern}' should be present"

    def test_readme_has_project_overview(self, readme_content):
        """README.mdにプロジェクト概要が含まれていることを確認."""
        # Arrange (準備)
        overview_patterns = [
            r"## 🎯 プロジェクトの目的",
            r"## 📊 背景",
            r"## 👥 対象ユーザー",
        ]

        # Act (実行)
        # Execute

        # Assert (検証)
        for pattern in overview_patterns:
            assert re.search(
                pattern, readme_content
            ), f"Project overview section '{pattern}' should be present"

    def test_readme_has_features_section(self, readme_content):
        """README.mdに機能説明セクションが含まれていることを確認."""
        # Arrange (準備)
        features_patterns = [
            r"## ✨ 主な機能",
            r"### 📈 多時間軸データ管理",
            r"### 🌐 Yahoo Finance連携",
            r"### 🗄️ PostgreSQL統合",
        ]

        # Act (実行)
        # Execute

        # Assert (検証)
        for pattern in features_patterns:
            assert re.search(
                pattern, readme_content
            ), f"Features section '{pattern}' should be present"

    def test_readme_has_quickstart_guide(self, readme_content):
        """README.mdにクイックスタートガイドが含まれていることを確認."""
        # Arrange (準備)
        quickstart_patterns = [
            r"## 🚀 クイックスタートガイド",
            r"### 📋 前提条件",
            r"### ⚡ ワンコマンドセットアップ",
            r"### 🔧 手動セットアップ",
        ]

        # Act (実行)
        # Execute

        # Assert (検証)
        for pattern in quickstart_patterns:
            assert re.search(
                pattern, readme_content
            ), f"Quickstart section '{pattern}' should be present"

    def test_readme_has_troubleshooting_section(self, readme_content):
        """README.mdにトラブルシューティングセクションが含まれていることを確認."""
        # Arrange (準備)
        troubleshooting_patterns = [
            r"## 🔧 トラブルシューティング",
            r"### よくある問題",
            r"### ログの確認方法",
        ]

        # Act (実行)
        # Execute

        # Assert (検証)
        for pattern in troubleshooting_patterns:
            assert re.search(
                pattern, readme_content
            ), f"Troubleshooting section '{pattern}' should be present"

    def test_readme_has_faq_section(self, readme_content):
        """README.mdにFAQセクションが含まれていることを確認."""
        # Arrange (準備)
        faq_patterns = [
            r"## ❓ よくある質問 \(FAQ\)",
            r"### Q\d+:",
            r"\*\*A\d+:\*\*",
        ]

        # Act (実行)
        # Execute

        # Assert (検証)
        for pattern in faq_patterns:
            assert re.search(
                pattern, readme_content
            ), f"FAQ section pattern '{pattern}' should be present"

    def test_readme_has_contributing_link(self, readme_content):
        """README.mdにCONTRIBUTING.mdへのリンクが含まれていることを確認."""
        # Arrange (準備)
        contributing_link_pattern = (
            r"\[CONTRIBUTING\.md\]\(docs/guides/contributing\.md\)"
        )

        # Act (実行)
        result = re.search(contributing_link_pattern, readme_content)

        # Assert (検証)
        assert result, "Link to CONTRIBUTING.md should be present"

    def test_readme_has_license_section(self, readme_content):
        """README.mdにライセンス情報が含まれていることを確認."""
        # Arrange (準備)
        license_patterns = [
            r"## 📄 ライセンス",
            r"MIT License",
            r"\[LICENSE\]\(LICENSE\)",
        ]

        # Act (実行)
        # Execute

        # Assert (検証)
        for pattern in license_patterns:
            assert re.search(
                pattern, readme_content
            ), f"License section pattern '{pattern}' should be present"

    def test_readme_internal_links(self, readme_content):
        """README.md内の内部リンクが正しい形式であることを確認."""
        # Arrange (準備)
        anchor_links = re.findall(r"\[.*?\]\(#([^)]+)\)", readme_content)

        def github_anchor_from_header(header_text):
            import unicodedata

            clean_text = "".join(
                c
                for c in header_text
                if unicodedata.category(c) not in ["So", "Sm"]
            )
            clean_text = re.sub(
                r"[^\w\s\u3040-\u309F\u30A0-\u30FF\u4E00-\u9FAF]",
                "",
                clean_text,
            )
            anchor = re.sub(r"\s+", "-", clean_text.strip()).lower()
            anchor = re.sub(r"-+", "-", anchor)
            return anchor.strip("-")

        # Act (実行)
        headers = re.findall(
            r"^(#{1,6})\s+(.+)$", readme_content, re.MULTILINE
        )
        header_anchors = {}
        for _level, header_text in headers:
            anchor = github_anchor_from_header(header_text)
            header_anchors[anchor] = header_text.strip()

        # Assert (検証)
        for anchor in anchor_links:
            assert (
                anchor in header_anchors
            ), f"Header for anchor '{anchor}' should exist. Available anchors: {list(header_anchors.keys())}"

    def test_readme_has_update_history(self, readme_content):
        """README.mdに更新履歴が含まれていることを確認."""
        # Arrange (準備)
        update_history_patterns = [
            r"## 📝 更新履歴",
            r"### \d{4}-\d{2}-\d{2}",
        ]

        # Act (実行)
        # Execute

        # Assert (検証)
        for pattern in update_history_patterns:
            assert re.search(
                pattern, readme_content
            ), f"Update history pattern '{pattern}' should be present"

    def test_readme_code_blocks_have_language(self, readme_content):
        """README.mdのコードブロックに言語指定があることを確認."""
        # Arrange (準備)
        # Setup

        # Act (実行)
        code_blocks = re.findall(r"```(\w*)\n", readme_content)
        bash_blocks = [
            lang
            for lang in code_blocks
            if lang in ["bash", "shell", "cmd", "powershell"]
        ]

        # Assert (検証)
        assert (
            len(bash_blocks) > 0
        ), "At least one bash/shell code block should be present"

    def test_readme_has_emoji_consistency(self, readme_content):
        """README.mdで絵文字が一貫して使用されていることを確認."""
        # Arrange (準備)
        emoji_sections = [
            r"## 🎯",
            r"## 📊",
            r"## ✨",
            r"## 🚀",
            r"## 🔧",
            r"## ❓",
            r"## 🤝",
            r"## 📄",
        ]

        # Act (実行)
        emoji_count = 0
        for pattern in emoji_sections:
            if re.search(pattern, readme_content):
                emoji_count += 1

        # Assert (検証)
        assert (
            emoji_count >= 6
        ), f"At least 6 sections should have emojis, found {emoji_count}"


class TestRelatedFiles:
    """関連ファイルの存在と内容をテストするクラス."""

    @pytest.fixture
    def project_root(self):
        """プロジェクトルートディレクトリのパスを取得."""
        return Path(__file__).parent.parent.parent

    def test_license_file_content(self, project_root):
        """LICENSEファイルの内容が適切であることを確認."""
        # Arrange (準備)
        license_path = project_root / "LICENSE"
        mit_patterns = [
            r"MIT License",
            r"Permission is hereby granted",
            r'THE SOFTWARE IS PROVIDED "AS IS"',
        ]

        # Act (実行)
        if not license_path.exists():
            return

        with open(license_path, "r", encoding="utf-8") as f:
            license_content = f.read()

        # Assert (検証)
        for pattern in mit_patterns:
            assert re.search(
                pattern, license_content
            ), f"MIT License pattern '{pattern}' should be present"

    def test_contributing_file_content(self, project_root):
        """CONTRIBUTING.mdファイルの内容が適切であることを確認."""
        # Arrange (準備)
        contributing_path = (
            project_root / "docs" / "guides" / "contributing.md"
        )
        contributing_patterns = [
            r"# プロジェクトへの貢献ガイド",
            r"## 貢献方法",
            r"## 開発環境のセットアップ",
            r"## 開発フロー",
        ]

        # Act (実行)
        if not contributing_path.exists():
            return

        with open(contributing_path, "r", encoding="utf-8") as f:
            contributing_content = f.read()

        # Assert (検証)
        for pattern in contributing_patterns:
            assert re.search(
                pattern, contributing_content
            ), f"Contributing guide pattern '{pattern}' should be present"

    def test_requirements_file_exists(self, project_root):
        """requirements.txtファイルが存在することを確認."""
        # Arrange (準備)
        requirements_path = project_root / "requirements.txt"

        # Act (実行)
        exists = requirements_path.exists()

        # Assert (検証)
        assert exists, "requirements.txt file should exist"

    def test_pyproject_file_exists(self, project_root):
        """pyproject.tomlファイルが存在することを確認."""
        # Arrange (準備)
        pyproject_path = project_root / "pyproject.toml"

        # Act (実行)
        exists = pyproject_path.exists()

        # Assert (検証)
        assert exists, "pyproject.toml file should exist"


if __name__ == "__main__":
    # テストを直接実行する場合
    pytest.main([__file__, "-v"])
