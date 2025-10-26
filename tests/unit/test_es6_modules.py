"""ES6モジュール化の動作確認テスト.

このテストは、ES6モジュール化が正しく実装されているかを確認します。
- app.jsからのエクスポート/インポートが正常に動作するか
- script.jsでのモジュール使用が正常に動作するか
- jpx_sequential.jsでのモジュール使用が正常に動作するか
"""

import os
from pathlib import Path
import re

import pytest


class TestES6Modules:
    """ES6モジュール化のテストクラス."""

    @pytest.fixture
    def static_dir(self):
        """staticディレクトリのパスを取得."""
        return Path(__file__).parent.parent.parent / "app" / "static"

    @pytest.fixture
    def templates_dir(self):
        """templatesディレクトリのパスを取得."""
        return Path(__file__).parent.parent.parent / "app" / "templates"

    def test_app_js_exports(self, static_dir):
        """app.jsが正しくエクスポートしているかテスト."""
        app_js_path = static_dir / "app.js"
        assert app_js_path.exists(), "app.jsファイルが存在しません"

        with open(app_js_path, "r", encoding="utf-8") as f:
            content = f.read()

        # AppStateクラスのエクスポートを確認
        assert (
            "export class AppState" in content
        ), "AppStateクラスがエクスポートされていません"

        # Utilsクラスのエクスポートを確認
        assert (
            "export class Utils" in content
        ), "Utilsクラスがエクスポートされていません"

        # UIComponentsクラスのエクスポートを確認
        assert (
            "export class UIComponents" in content
        ), "UIComponentsクラスがエクスポートされていません"

    def test_script_js_imports(self, static_dir):
        """script.jsが正しくインポートしているかテスト."""
        script_js_path = static_dir / "script.js"
        assert script_js_path.exists(), "script.jsファイルが存在しません"

        with open(script_js_path, "r", encoding="utf-8") as f:
            content = f.read()

        # app.jsからのインポートを確認
        import_pattern = r"import\s+\{[^}]*appStateManager[^}]*\}\s+from\s+['\"]\.\/app\.js['\"]"
        assert re.search(
            import_pattern, content
        ), "appStateManagerのインポートが見つかりません"

        # 新しいシステムのappState使用を確認
        assert (
            "const appState = appStateManager;" in content
        ), "appStateManagerの使用が確認できません"

        # AppStateの直接定義がないことを確認（重複定義の回避）
        assert (
            "const AppState = {" not in content
        ), "AppStateの重複定義が存在します"

    def test_jpx_sequential_js_imports(self, static_dir):
        """jpx_sequential.jsが正しくインポートしているかテスト."""
        jpx_js_path = static_dir / "jpx_sequential.js"
        assert jpx_js_path.exists(), "jpx_sequential.jsファイルが存在しません"

        with open(jpx_js_path, "r", encoding="utf-8") as f:
            content = f.read()

        # app.jsからのインポートを確認
        import_pattern = r"import\s+\{[^}]*Utils[^}]*,\s*UIComponents[^}]*\}\s+from\s+['\"]\.\/app\.js['\"]"
        assert re.search(
            import_pattern, content
        ), "Utils, UIComponentsのインポートが見つかりません"

    def test_index_html_module_scripts(self, templates_dir):
        """index.htmlでscriptタグにtype="module"が設定されているかテスト."""
        index_html_path = templates_dir / "index.html"
        assert index_html_path.exists(), "index.htmlファイルが存在しません"

        with open(index_html_path, "r", encoding="utf-8") as f:
            content = f.read()

        # app.jsのモジュール読み込みを確認
        app_js_pattern = r'<script\s+type="module"\s+src="[^"]*app\.js[^"]*">'
        assert re.search(
            app_js_pattern, content
        ), "app.jsがモジュールとして読み込まれていません"

        # script.jsのモジュール読み込みを確認
        script_js_pattern = (
            r'<script\s+type="module"\s+src="[^"]*script\.js[^"]*">'
        )
        assert re.search(
            script_js_pattern, content
        ), "script.jsがモジュールとして読み込まれていません"

        # jpx_sequential.jsのモジュール読み込みを確認
        jpx_js_pattern = (
            r'<script\s+type="module"\s+src="[^"]*jpx_sequential\.js[^"]*">'
        )
        assert re.search(
            jpx_js_pattern, content
        ), "jpx_sequential.jsがモジュールとして読み込まれていません"

    def test_no_duplicate_appstate_definitions(self, static_dir):
        """AppStateの重複定義がないことを確認."""
        script_js_path = static_dir / "script.js"

        with open(script_js_path, "r", encoding="utf-8") as f:
            content = f.read()

        # AppStateの定義パターンを検索
        appstate_definitions = re.findall(
            r"(const|let|var)\s+AppState\s*=", content
        )

        # AppStateの定義は1つまで（appStateインスタンスの作成のみ）
        assert (
            len(appstate_definitions) <= 1
        ), f"AppStateの定義が複数見つかりました: {appstate_definitions}"

    def test_appstate_usage_consistency(self, static_dir):
        """AppStateの使用が一貫しているかテスト（AppState.xxx → appState.xxx）."""
        script_js_path = static_dir / "script.js"

        with open(script_js_path, "r", encoding="utf-8") as f:
            content = f.read()

        # AppState.xxxの使用を検索（appState.xxxではない）
        incorrect_usage = re.findall(
            r"AppState\.[a-zA-Z_][a-zA-Z0-9_]*", content
        )

        # AppState.xxxの使用がないことを確認
        assert (
            len(incorrect_usage) == 0
        ), f"AppState.xxxの使用が見つかりました（appState.xxxに変更してください）: {incorrect_usage}"

    def test_es6_module_syntax_validity(self, static_dir):
        """ES6モジュール構文の妥当性をテスト."""
        files_to_check = ["app.js", "script.js", "jpx_sequential.js"]

        for filename in files_to_check:
            file_path = static_dir / filename
            assert file_path.exists(), f"{filename}ファイルが存在しません"

            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            # 基本的なES6構文チェック
            if filename == "app.js":
                # exportが存在することを確認
                assert (
                    "export" in content
                ), f"{filename}にexport文が見つかりません"
            else:
                # importが存在することを確認
                assert (
                    "import" in content
                ), f"{filename}にimport文が見つかりません"
