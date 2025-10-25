"""README.mdの改善に関するテストコード.

このテストファイルは、README.mdファイルの内容と関連ファイルの存在を検証します。
"""

import os
from pathlib import Path
import re

import pytest


class TestReadmeImprovement:
    """README.mdの改善に関するテストクラス."""

    @pytest.fixture
    def project_root(self):
        """プロジェクトルートディレクトリのパスを取得."""
        return Path(__file__).parent.parent

    @pytest.fixture
    def readme_content(self, project_root):
        """README.mdファイルの内容を取得."""
        readme_path = project_root / "README.md"
        with open(readme_path, "r", encoding="utf-8") as f:
            return f.read()

    def test_readme_file_exists(self, project_root):
        """README.mdファイルが存在することを確認."""
        readme_path = project_root / "README.md"
        assert readme_path.exists(), "README.md file should exist"

    def test_license_file_exists(self, project_root):
        """LICENSEファイルが存在することを確認."""
        license_path = project_root / "LICENSE"
        assert license_path.exists(), "LICENSE file should exist"

    def test_contributing_file_exists(self, project_root):
        """CONTRIBUTING.mdファイルが存在することを確認."""
        contributing_path = project_root / "CONTRIBUTING.md"
        assert contributing_path.exists(), "CONTRIBUTING.md file should exist"

    def test_readme_has_badges(self, readme_content):
        """README.mdにバッジが含まれていることを確認."""
        # Pythonバージョンバッジ
        python_badge_pattern = r"!\[Python\]\(https://img\.shields\.io/badge/python-3\.8\+-blue\.svg\)"
        assert re.search(
            python_badge_pattern, readme_content
        ), "Python version badge should be present"

        # ライセンスバッジ
        license_badge_pattern = r"!\[License\]\(https://img\.shields\.io/badge/license-MIT-green\.svg\)"
        assert re.search(
            license_badge_pattern, readme_content
        ), "License badge should be present"

    def test_readme_has_table_of_contents(self, readme_content):
        """README.mdに目次が含まれていることを確認."""
        toc_patterns = [r"## 📋 目次", r"- \[.*\]\(#.*\)"]  # 目次のリンク形式

        for pattern in toc_patterns:
            assert re.search(
                pattern, readme_content
            ), f"Table of contents pattern '{pattern}' should be present"

    def test_readme_has_project_overview(self, readme_content):
        """README.mdにプロジェクト概要が含まれていることを確認."""
        overview_patterns = [
            r"## 🎯 プロジェクトの目的",
            r"## 📊 背景",
            r"## 👥 対象ユーザー",
        ]

        for pattern in overview_patterns:
            assert re.search(
                pattern, readme_content
            ), f"Project overview section '{pattern}' should be present"

    def test_readme_has_features_section(self, readme_content):
        """README.mdに機能説明セクションが含まれていることを確認."""
        features_patterns = [
            r"## ✨ 主な機能",
            r"### 📈 多時間軸データ管理",
            r"### 🌐 Yahoo Finance連携",
            r"### 🗄️ PostgreSQL統合",
        ]

        for pattern in features_patterns:
            assert re.search(
                pattern, readme_content
            ), f"Features section '{pattern}' should be present"

    def test_readme_has_quickstart_guide(self, readme_content):
        """README.mdにクイックスタートガイドが含まれていることを確認."""
        quickstart_patterns = [
            r"## 🚀 クイックスタートガイド",
            r"### 📋 前提条件",
            r"### ⚡ ワンコマンドセットアップ",
            r"### 🔧 手動セットアップ",
        ]

        for pattern in quickstart_patterns:
            assert re.search(
                pattern, readme_content
            ), f"Quickstart section '{pattern}' should be present"

    def test_readme_has_troubleshooting_section(self, readme_content):
        """README.mdにトラブルシューティングセクションが含まれていることを確認."""
        troubleshooting_patterns = [
            r"## 🔧 トラブルシューティング",
            r"### よくある問題",
            r"### ログの確認方法",
        ]

        for pattern in troubleshooting_patterns:
            assert re.search(
                pattern, readme_content
            ), f"Troubleshooting section '{pattern}' should be present"

    def test_readme_has_faq_section(self, readme_content):
        """README.mdにFAQセクションが含まれていることを確認."""
        faq_patterns = [
            r"## ❓ よくある質問 \(FAQ\)",
            r"### Q\d+:",  # Q1:, Q2: などの質問形式
            r"\*\*A\d+:\*\*",  # A1:, A2: などの回答形式
        ]

        for pattern in faq_patterns:
            assert re.search(
                pattern, readme_content
            ), f"FAQ section pattern '{pattern}' should be present"

    def test_readme_has_contributing_link(self, readme_content):
        """README.mdにCONTRIBUTING.mdへのリンクが含まれていることを確認."""
        contributing_link_pattern = r"\[CONTRIBUTING\.md\]\(CONTRIBUTING\.md\)"
        assert re.search(
            contributing_link_pattern, readme_content
        ), "Link to CONTRIBUTING.md should be present"

    def test_readme_has_license_section(self, readme_content):
        """README.mdにライセンス情報が含まれていることを確認."""
        license_patterns = [
            r"## 📄 ライセンス",
            r"MIT License",
            r"\[LICENSE\]\(LICENSE\)",
        ]

        for pattern in license_patterns:
            assert re.search(
                pattern, readme_content
            ), f"License section pattern '{pattern}' should be present"

    def test_readme_internal_links(self, readme_content):
        """README.md内の内部リンクが正しい形式であることを確認."""
        # 目次のアンカーリンクを抽出
        anchor_links = re.findall(r"\[.*?\]\(#([^)]+)\)", readme_content)

        # GitHubのアンカー生成ルールを実装
        def github_anchor_from_header(header_text):
            # 絵文字と特殊文字を削除し、日本語文字とアルファベット、数字のみを残す
            import unicodedata

            # 絵文字を削除
            clean_text = "".join(
                c
                for c in header_text
                if unicodedata.category(c) not in ["So", "Sm"]
            )
            # 括弧などの記号を削除
            clean_text = re.sub(
                r"[^\w\s\u3040-\u309F\u30A0-\u30FF\u4E00-\u9FAF]",
                "",
                clean_text,
            )
            # スペースをハイフンに変換し、小文字化
            anchor = re.sub(r"\s+", "-", clean_text.strip()).lower()
            # 連続するハイフンを1つにまとめる
            anchor = re.sub(r"-+", "-", anchor)
            # 先頭と末尾のハイフンを削除
            return anchor.strip("-")

        # 全てのヘッダーを抽出してアンカーマップを作成
        headers = re.findall(
            r"^(#{1,6})\s+(.+)$", readme_content, re.MULTILINE
        )
        header_anchors = {}
        for _level, header_text in headers:
            anchor = github_anchor_from_header(header_text)
            header_anchors[anchor] = header_text.strip()

        # 各アンカーリンクに対応するヘッダーが存在することを確認
        for anchor in anchor_links:
            assert (
                anchor in header_anchors
            ), f"Header for anchor '{anchor}' should exist. Available anchors: {list(header_anchors.keys())}"

    def test_readme_has_update_history(self, readme_content):
        """README.mdに更新履歴が含まれていることを確認."""
        update_history_patterns = [
            r"## 📝 更新履歴",
            r"### \d{4}-\d{2}-\d{2}",  # 日付形式 (YYYY-MM-DD)
        ]

        for pattern in update_history_patterns:
            assert re.search(
                pattern, readme_content
            ), f"Update history pattern '{pattern}' should be present"

    def test_readme_code_blocks_have_language(self, readme_content):
        """README.mdのコードブロックに言語指定があることを確認."""
        # コードブロックを抽出
        code_blocks = re.findall(r"```(\w*)\n", readme_content)

        # 空の言語指定がないことを確認（最低限のコードブロックには言語指定があることを期待）
        bash_blocks = [
            lang
            for lang in code_blocks
            if lang in ["bash", "shell", "cmd", "powershell"]
        ]
        assert (
            len(bash_blocks) > 0
        ), "At least one bash/shell code block should be present"

    def test_readme_has_emoji_consistency(self, readme_content):
        """README.mdで絵文字が一貫して使用されていることを確認."""
        # 主要セクションに絵文字が使用されていることを確認
        emoji_sections = [
            r"## 🎯",  # 目的
            r"## 📊",  # 背景
            r"## ✨",  # 機能
            r"## 🚀",  # クイックスタート
            r"## 🔧",  # トラブルシューティング
            r"## ❓",  # FAQ
            r"## 🤝",  # 貢献
            r"## 📄",  # ライセンス
        ]

        emoji_count = 0
        for pattern in emoji_sections:
            if re.search(pattern, readme_content):
                emoji_count += 1

        assert (
            emoji_count >= 6
        ), f"At least 6 sections should have emojis, found {emoji_count}"


class TestRelatedFiles:
    """関連ファイルの存在と内容をテストするクラス."""

    @pytest.fixture
    def project_root(self):
        """プロジェクトルートディレクトリのパスを取得."""
        return Path(__file__).parent.parent

    def test_license_file_content(self, project_root):
        """LICENSEファイルの内容が適切であることを確認."""
        license_path = project_root / "LICENSE"

        if license_path.exists():
            with open(license_path, "r", encoding="utf-8") as f:
                license_content = f.read()

            # MIT Licenseの基本的な要素が含まれていることを確認
            mit_patterns = [
                r"MIT License",
                r"Permission is hereby granted",
                r'THE SOFTWARE IS PROVIDED "AS IS"',
            ]

            for pattern in mit_patterns:
                assert re.search(
                    pattern, license_content
                ), f"MIT License pattern '{pattern}' should be present"

    def test_contributing_file_content(self, project_root):
        """CONTRIBUTING.mdファイルの内容が適切であることを確認."""
        contributing_path = project_root / "CONTRIBUTING.md"

        if contributing_path.exists():
            with open(contributing_path, "r", encoding="utf-8") as f:
                contributing_content = f.read()

            # 貢献ガイドの基本的な要素が含まれていることを確認
            contributing_patterns = [
                r"# プロジェクトへの貢献ガイド",
                r"## 貢献方法",
                r"## 開発環境のセットアップ",
                r"## 開発フロー",
            ]

            for pattern in contributing_patterns:
                assert re.search(
                    pattern, contributing_content
                ), f"Contributing guide pattern '{pattern}' should be present"

    def test_requirements_file_exists(self, project_root):
        """requirements.txtファイルが存在することを確認."""
        requirements_path = project_root / "requirements.txt"
        assert requirements_path.exists(), "requirements.txt file should exist"

    def test_pyproject_file_exists(self, project_root):
        """pyproject.tomlファイルが存在することを確認."""
        pyproject_path = project_root / "pyproject.toml"
        assert pyproject_path.exists(), "pyproject.toml file should exist"


if __name__ == "__main__":
    # テストを直接実行する場合
    pytest.main([__file__, "-v"])
