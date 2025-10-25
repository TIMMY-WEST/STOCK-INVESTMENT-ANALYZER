"""docs/README.mdの内容に関するテストコード.

このテストファイルは、docs/README.mdファイルの内容と構造を検証します。
"""

from pathlib import Path
import re

import pytest


class TestDocsReadmeContent:
    """docs/README.mdの内容と構造をテストするクラス."""

    @pytest.fixture
    def project_root(self):
        """プロジェクトルートディレクトリのパスを取得."""
        return Path(__file__).parent.parent

    @pytest.fixture
    def docs_dir(self, project_root):
        """docsディレクトリのパスを取得."""
        return project_root / "docs"

    @pytest.fixture
    def docs_readme_content(self, docs_dir):
        """docs/README.mdファイルの内容を取得."""
        readme_path = docs_dir / "README.md"
        with open(readme_path, "r", encoding="utf-8") as f:
            return f.read()

    def test_docs_readme_file_exists(self, docs_dir):
        """docs/README.mdファイルが存在することを確認."""
        readme_path = docs_dir / "README.md"
        assert readme_path.exists(), "docs/README.md file should exist"

    def test_docs_readme_has_title(self, docs_readme_content):
        """docs/README.mdにタイトルが含まれていることを確認."""
        title_pattern = r"# 株価データ取得システム - 開発者向けドキュメント"
        assert re.search(
            title_pattern, docs_readme_content
        ), "Document title should be present"

    def test_docs_readme_has_overview(self, docs_readme_content):
        """docs/README.mdに概要セクションが含まれていることを確認."""
        overview_patterns = [
            r"## 📋 概要",
            r"Yahoo Finance（yfinance）",
            r"PostgreSQL",
            r"設計理念",
        ]

        for pattern in overview_patterns:
            assert re.search(
                pattern, docs_readme_content
            ), f"Overview section pattern '{pattern}' should be present"

    def test_docs_readme_has_document_structure(self, docs_readme_content):
        """docs/README.mdにドキュメント構成セクションが含まれていることを確認."""
        structure_patterns = [
            r"## 📁 ドキュメント構成",
            r"### 🚀 機能別統合ドキュメント",
            r"### 🏗️ アーキテクチャ・設計",
            r"### 🔌 API仕様",
            r"### 📖 運用・利用ガイド",
            r"### 🔧 開発関連",
        ]

        for pattern in structure_patterns:
            assert re.search(
                pattern, docs_readme_content
            ), f"Document structure pattern '{pattern}' should be present"

    def test_docs_readme_has_ai_developer_guide(self, docs_readme_content):
        """docs/README.mdにAI開発者向けガイドが含まれていることを確認."""
        ai_guide_patterns = [
            r"## 🤖 AI開発者向けガイド",
            r"### タスク別推奨参照順序",
            r"#### 🏁 初期セットアップ時",
            r"#### 🛠️ バックエンド開発時",
            r"#### 🎨 フロントエンド開発時",
            r"#### 🚀 リリース・デプロイ時",
        ]

        for pattern in ai_guide_patterns:
            assert re.search(
                pattern, docs_readme_content
            ), f"AI developer guide pattern '{pattern}' should be present"

    def test_docs_readme_has_priority_mapping(self, docs_readme_content):
        """docs/README.mdに開発優先度別機能マップが含まれていることを確認."""
        priority_patterns = [
            r"### 開発優先度別機能マップ",
            r"#### 🔴 優先度: 高（MVP必須）",
            r"#### 🟡 優先度: 中（動作確認後）",
            r"#### 🟢 優先度: 低（必要になってから）",
        ]

        for pattern in priority_patterns:
            assert re.search(
                pattern, docs_readme_content
            ), f"Priority mapping pattern '{pattern}' should be present"

    def test_docs_readme_has_reference_patterns(self, docs_readme_content):
        """docs/README.mdによくある参照パターンが含まれていることを確認."""
        reference_patterns = [
            r"## 🔍 よくある参照パターン",
            r"### エラー対応時",
            r"### 新機能追加時",
            r"### コードレビュー時",
        ]

        for pattern in reference_patterns:
            assert re.search(
                pattern, docs_readme_content
            ), f"Reference pattern '{pattern}' should be present"

    def test_docs_readme_has_development_steps(self, docs_readme_content):
        """docs/README.mdに開発の進め方が含まれていることを確認."""
        development_patterns = [
            r"## 📌 開発の進め方",
            r"### ステップ1: 環境構築",
            r"### ステップ2: MVP実装",
            r"### ステップ3: 機能拡張",
        ]

        for pattern in development_patterns:
            assert re.search(
                pattern, docs_readme_content
            ), f"Development steps pattern '{pattern}' should be present"

    def test_docs_readme_internal_links(self, docs_readme_content):
        """docs/README.md内の内部リンクが正しい形式であることを確認."""
        # 相対パスのリンクを抽出（.mdファイルへのリンク）
        md_links = re.findall(r"\[.*?\]\(([^)]+\.md)\)", docs_readme_content)

        # 各リンクに対応するファイルが存在することを確認
        docs_dir = Path(__file__).parent.parent / "docs"
        for link in md_links:
            # リンクがアンカー付きの場合、ファイル部分のみを取得
            file_path = link.split("#")[0] if "#" in link else link
            full_path = docs_dir / file_path
            assert (
                full_path.exists()
            ), f"Linked file '{file_path}' should exist at {full_path}"

    def test_ai_priority_consistency(self, docs_readme_content):
        """AI優先度の表記が一貫していることを確認."""
        # AI優先度の表記パターンを確認
        priority_patterns = [
            r"\| \*\*高\*\* \|",  # **高**
            r"\| 中 \|",  # 中
            r"\| 低 \|",  # 低
        ]

        priority_counts = {}
        for pattern in priority_patterns:
            matches = re.findall(pattern, docs_readme_content)
            priority_name = (
                pattern.split("*")[-1].split(" ")[0]
                if "*" in pattern
                else pattern.split("|")[1].strip()
            )
            priority_counts[priority_name] = len(matches)

        # 各優先度が最低1つは存在することを確認
        for priority, count in priority_counts.items():
            assert (
                count > 0
            ), f"Priority '{priority}' should appear at least once in the document"


if __name__ == "__main__":
    # テストを直接実行する場合
    pytest.main([__file__, "-v"])
