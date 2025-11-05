"""ドキュメント絵文字使用検証テスト.

このモジュールは以下をテストします:
- 絵文字の使用が許容リスト内に収まっているか
- 不許可の絵文字が使用されていないか（警告）
"""

from pathlib import Path
import re

import pytest


pytestmark = pytest.mark.docs


class TestDocsEmojiUsage:
    """ドキュメント絵文字使用テストクラス."""

    @pytest.fixture
    def project_root(self) -> Path:
        """プロジェクトルートディレクトリのパスを取得."""
        return Path(__file__).parent.parent.parent

    @pytest.fixture
    def docs_dir(self, project_root: Path) -> Path:
        """docsディレクトリのパスを取得."""
        return project_root / "docs"

    @pytest.fixture
    def all_markdown_files(self, docs_dir: Path) -> list[Path]:
        """docsディレクトリ内の全Markdownファイルを取得（old/archiveディレクトリを除外）."""
        exclude_dirs = {"old", "archive"}
        return [
            f
            for f in docs_dir.rglob("*.md")
            if not any(excluded in f.parts for excluded in exclude_dirs)
        ]

    @pytest.fixture
    def allowed_emojis(self) -> set[str]:
        """許可された絵文字のセット.

        プロジェクトで使用を許可する絵文字をここに定義します。
        """
        return {
            # ドキュメント構造
            "📋",  # 概要・目次
            "📁",  # ドキュメント構成・ファイル
            "📚",  # ライブラリ・資料
            "📖",  # ドキュメント・読み物
            "📝",  # 変更履歴・ノート
            # 開発フロー
            "🚀",  # リリース・デプロイ・クイックスタート
            "🏁",  # 初期セットアップ・スタート
            "🔧",  # 開発・設定・ツール
            "🛠️",  # バックエンド開発・メンテナンス
            "🎨",  # フロントエンド開発・デザイン
            "🤖",  # AI開発者向け・自動化
            # 優先度・状態
            "🔴",  # 優先度: 高・重要
            "🟡",  # 優先度: 中・注意
            "🟢",  # 優先度: 低・OK
            "✅",  # 完了・成功
            "❌",  # エラー・失敗
            "⚠️",  # 警告
            # 情報・ナビゲーション
            "🔍",  # 検索・参照パターン
            "📌",  # ピン留め・重要ポイント
            "🆘",  # ヘルプ・困った時
            "🎯",  # ターゲット・目標
            # アーキテクチャ・技術
            "🏗️",  # アーキテクチャ・構造
            "🔌",  # API・プラグイン
            "💾",  # データベース・ストレージ
            "📊",  # データ・グラフ
            "🔗",  # リンク・連携
            # その他
            "✨",  # 新機能・改善
            "🐛",  # バグ
            "⚡",  # パフォーマンス
            "♻️",  # リファクタリング
            "🔒",  # セキュリティ
        }

    def _extract_emojis(self, text: str) -> list[str]:
        """テキストから絵文字を抽出.

        Returns:
            絵文字のリスト
        """
        # 絵文字の範囲を定義
        emoji_pattern = (
            r"[\U0001F600-\U0001F64F"  # 顔文字
            r"\U0001F300-\U0001F5FF"  # 記号・絵文字
            r"\U0001F680-\U0001F6FF"  # 交通・地図記号
            r"\U0001F1E0-\U0001F1FF"  # 国旗
            r"\U00002600-\U000027BF"  # その他の記号
            r"\U0001F900-\U0001F9FF"  # 補助絵文字
            r"\U0001FA70-\U0001FAFF"  # 拡張絵文字
            r"\U00002300-\U000023FF"  # 技術記号
            r"\U0001F200-\U0001F2FF"  # 囲み文字
            r"\U0001F700-\U0001F77F"  # 錬金術記号
            r"]"
        )
        return re.findall(emoji_pattern, text)

    def test_only_allowed_emojis_used(
        self,
        docs_dir: Path,
        all_markdown_files: list[Path],
        allowed_emojis: set[str],
    ) -> None:
        """許可された絵文字のみが使用されていることを確認（警告のみ）."""
        # Arrange (準備)
        files_with_disallowed_emojis = []

        # Act (実行)
        for md_file in all_markdown_files:
            content = md_file.read_text(encoding="utf-8")
            emojis = self._extract_emojis(content)

            disallowed = [
                emoji for emoji in emojis if emoji not in allowed_emojis
            ]

            if disallowed:
                relative_path = md_file.relative_to(docs_dir)
                unique_disallowed = set(disallowed)
                files_with_disallowed_emojis.append(
                    f"{relative_path}: {', '.join(unique_disallowed)}"
                )

        # Assert (検証)
        # 警告のみ（エラーにはしない）
        if files_with_disallowed_emojis:
            print(
                "\n警告: 以下のファイルで許可されていない絵文字が使用されています:\n"
                + "\n".join(
                    f"  - {file}" for file in files_with_disallowed_emojis
                )
            )

    def test_emoji_consistency_in_headings(
        self, docs_dir: Path, all_markdown_files: list[Path]
    ) -> None:
        """見出しでの絵文字使用の一貫性を確認（警告のみ）."""
        # Arrange (準備)
        inconsistent_files = []

        # Act (実行)
        for md_file in all_markdown_files:
            content = md_file.read_text(encoding="utf-8")

            # H1-H3の見出しを抽出
            heading_pattern = r"^(#{1,3})\s+(.+)$"
            headings = re.findall(heading_pattern, content, re.MULTILINE)

            # 絵文字で始まる見出しと、そうでない見出しをカウント
            with_emoji = 0
            without_emoji = 0

            for level, heading_text in headings:
                emojis = self._extract_emojis(heading_text)
                if emojis:
                    with_emoji += 1
                else:
                    without_emoji += 1

            # 両方が混在している場合は一貫性なし
            if with_emoji > 0 and without_emoji > 0:
                relative_path = md_file.relative_to(docs_dir)
                inconsistent_files.append(
                    f"{relative_path} "
                    f"(絵文字あり: {with_emoji}, なし: {without_emoji})"
                )

        # Assert (検証)
        # 警告のみ（エラーにはしない）
        if inconsistent_files:
            print(
                "\n警告: 以下のファイルで見出しの絵文字使用に一貫性がありません:\n"
                + "\n".join(f"  - {file}" for file in inconsistent_files)
            )

    def test_no_excessive_emoji_usage(
        self, docs_dir: Path, all_markdown_files: list[Path]
    ) -> None:
        """絵文字の過度な使用がないことを確認（警告のみ）.

        1つのファイルで絵文字が20個以上使用されている場合に警告。
        """
        # Arrange (準備)
        excessive_emoji_files = []
        max_emoji_count = 20

        # Act (実行)
        for md_file in all_markdown_files:
            content = md_file.read_text(encoding="utf-8")
            emojis = self._extract_emojis(content)

            if len(emojis) > max_emoji_count:
                relative_path = md_file.relative_to(docs_dir)
                excessive_emoji_files.append(
                    f"{relative_path} ({len(emojis)} emojis)"
                )

        # Assert (検証)
        # 警告のみ（エラーにはしない）
        if excessive_emoji_files:
            print(
                f"\n警告: 以下のファイルで絵文字が過度に使用されています "
                f"({max_emoji_count}個超):\n"
                + "\n".join(f"  - {file}" for file in excessive_emoji_files)
            )


class TestDocsEmojiDocumentation:
    """絵文字使用に関するドキュメントテストクラス."""

    @pytest.fixture
    def project_root(self) -> Path:
        """プロジェクトルートディレクトリのパスを取得."""
        return Path(__file__).parent.parent.parent

    @pytest.fixture
    def docs_dir(self, project_root: Path) -> Path:
        """docsディレクトリのパスを取得."""
        return project_root / "docs"

    def test_emoji_guidelines_exist(self, docs_dir: Path) -> None:
        """絵文字使用ガイドラインの存在確認（警告のみ）."""
        # Arrange (準備)
        possible_locations = [
            docs_dir / "README.md",
            docs_dir / "standards" / "coding-standards.md",
            docs_dir / "guides" / "development-workflow.md",
        ]

        # Act (実行)
        has_guidelines = False
        for doc_path in possible_locations:
            if doc_path.exists():
                content = doc_path.read_text(encoding="utf-8")
                # "絵文字" または "emoji" が含まれているか
                if "絵文字" in content or "emoji" in content.lower():
                    has_guidelines = True
                    break

        # Assert (検証)
        # 警告のみ（エラーにはしない）
        if not has_guidelines:
            print(
                "\n警告: 絵文字使用に関するガイドラインが見つかりません。"
                "ドキュメントに絵文字使用のガイドラインを追加することを推奨します。"
            )


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
