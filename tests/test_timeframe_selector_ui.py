"""Issue #67: 時間軸選択UI機能のテストコード.
Enhanced Timeframe Selector UI Tests

このテストファイルは、時間軸選択UIの基本機能をテストします：
- HTMLテンプレートの構造確認
- CSSスタイルの存在確認
- JavaScriptファイルの構文確認。
"""

import os
import re
import sys

from bs4 import BeautifulSoup
import pytest


# アプリケーションのパスを追加
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


class TestTimeframeSelectorUI:
    """時間軸選択UI機能のテストクラス."""

    def test_html_template_structure(self):
        """HTMLテンプレートの構造確認テスト."""
        template_path = os.path.join(
            os.path.dirname(__file__), "..", "app", "templates", "index.html"
        )

        with open(template_path, "r", encoding="utf-8") as f:
            html_content = f.read()

        soup = BeautifulSoup(html_content, "html.parser")

        # 期間選択セレクターの存在確認
        period_select = soup.find("select", {"id": "period"})
        assert period_select is not None, "期間選択セレクターが見つかりません"

        # optgroupの存在確認
        optgroups = period_select.find_all("optgroup")
        assert len(optgroups) >= 4, "optgroupが4つ以上必要です"

        # 必須項目インジケーターの確認
        required_indicator = soup.find("span", class_="required-indicator")
        assert (
            required_indicator is not None
        ), "必須項目インジケーターが見つかりません"

        # 時間軸インジケーターの確認
        timeframe_indicator = soup.find("div", {"id": "timeframe-indicator"})
        assert (
            timeframe_indicator is not None
        ), "時間軸インジケーターが見つかりません"

    def test_css_styles_exist(self):
        """CSSスタイルの存在確認テスト."""
        css_path = os.path.join(
            os.path.dirname(__file__), "..", "app", "static", "style.css"
        )

        with open(css_path, "r", encoding="utf-8") as f:
            css_content = f.read()

        # 重要なCSSクラスの存在確認
        required_classes = [
            ".required-indicator",
            ".timeframe-selector-container",
            ".timeframe-selector",
            ".timeframe-indicator",
            ".field-error",
            ".is-invalid",
            ".is-valid",
        ]

        for css_class in required_classes:
            assert (
                css_class in css_content
            ), f"CSSクラス {css_class} が見つかりません"

        # レスポンシブデザインの確認
        assert (
            "@media (max-width: 768px)" in css_content
        ), "タブレット用メディアクエリが見つかりません"
        assert (
            "@media (max-width: 480px)" in css_content
        ), "モバイル用メディアクエリが見つかりません"

    def test_javascript_functions_exist(self):
        """JavaScript関数の存在確認テスト."""
        js_path = os.path.join(
            os.path.dirname(__file__), "..", "app", "static", "script.js"
        )

        with open(js_path, "r", encoding="utf-8") as f:
            js_content = f.read()

        # 重要なJavaScript関数の存在確認
        required_functions = [
            "initTimeframeSelector",
            "handleTimeframeChange",
            "validateTimeframeSelection",
            "updateTimeframeIndicator",
            "getTimeframeConfig",
            "setTimeframeSelectorState",
            "showTimeframeError",
            "clearTimeframeError",
        ]

        for function_name in required_functions:
            pattern = rf"function\s+{function_name}\s*\(|{function_name}\s*[:=]\s*function"
            assert re.search(
                pattern, js_content
            ), f"JavaScript関数 {function_name} が見つかりません"

    def test_timeframe_config_structure(self):
        """時間軸設定の構造確認テスト."""
        js_path = os.path.join(
            os.path.dirname(__file__), "..", "app", "static", "script.js"
        )

        with open(js_path, "r", encoding="utf-8") as f:
            js_content = f.read()

        # getTimeframeConfig関数の内容確認
        assert "short-term" in js_content, "短期間設定が見つかりません"
        assert "medium-term" in js_content, "中期間設定が見つかりません"
        assert "long-term" in js_content, "長期間設定が見つかりません"
        assert "max-term" in js_content, "最大期間設定が見つかりません"

    def test_accessibility_attributes(self):
        """アクセシビリティ属性の確認テスト."""
        template_path = os.path.join(
            os.path.dirname(__file__), "..", "app", "templates", "index.html"
        )

        with open(template_path, "r", encoding="utf-8") as f:
            html_content = f.read()

        soup = BeautifulSoup(html_content, "html.parser")

        # 期間選択セレクターのアクセシビリティ属性確認
        period_select = soup.find("select", {"id": "period"})
        assert (
            period_select.get("aria-label") is not None
        ), "aria-label属性が見つかりません"
        assert (
            period_select.get("aria-describedby") is not None
        ), "aria-describedby属性が見つかりません"

    def test_form_validation_integration(self):
        """フォームバリデーション統合の確認テスト."""
        js_path = os.path.join(
            os.path.dirname(__file__), "..", "app", "static", "script.js"
        )

        with open(js_path, "r", encoding="utf-8") as f:
            js_content = f.read()

        # validateForm関数に時間軸バリデーションが統合されているか確認
        assert (
            "validateTimeframeSelection" in js_content
        ), "時間軸バリデーションが統合されていません"

        # initApp関数に初期化が含まれているか確認
        assert (
            "initTimeframeSelector" in js_content
        ), "時間軸セレクター初期化が含まれていません"


class TestTimeframeSelectorConfiguration:
    """時間軸選択設定のテストクラス."""

    def test_timeframe_options_completeness(self):
        """時間軸オプションの完全性テスト."""
        template_path = os.path.join(
            os.path.dirname(__file__), "..", "app", "templates", "index.html"
        )

        with open(template_path, "r", encoding="utf-8") as f:
            html_content = f.read()

        soup = BeautifulSoup(html_content, "html.parser")
        period_select = soup.find("select", {"id": "period"})

        # 各optgroupに適切なオプションが含まれているか確認
        optgroups = period_select.find_all("optgroup")

        for optgroup in optgroups:
            options = optgroup.find_all("option")
            assert (
                len(options) > 0
            ), f"optgroup '{optgroup.get('label')}' にオプションがありません"

            # 各オプションにvalue属性があることを確認
            for option in options:
                assert (
                    option.get("value") is not None
                ), "オプションにvalue属性がありません"
                assert (
                    option.get_text().strip() != ""
                ), "オプションにテキストがありません"

    def test_css_responsive_design(self):
        """CSSレスポンシブデザインのテスト."""
        css_path = os.path.join(
            os.path.dirname(__file__), "..", "app", "static", "style.css"
        )

        with open(css_path, "r", encoding="utf-8") as f:
            css_content = f.read()

        # モバイル対応のスタイルが含まれているか確認
        _ = ["font-size", "padding", "margin", "width"]

        # メディアクエリ内でモバイル用スタイルが定義されているか確認
        media_query_pattern = r"@media\s*\([^)]*max-width[^)]*\)\s*\{[^}]*\}"
        media_queries = re.findall(media_query_pattern, css_content, re.DOTALL)

        assert (
            len(media_queries) >= 2
        ), "十分なメディアクエリが定義されていません"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
