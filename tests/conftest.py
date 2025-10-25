"""共通テストフィクスチャ.

このファイルはpytestによって自動的に読み込まれ、
全てのテストで利用可能な共通フィクスチャを提供します。

テストレベル別のディレクトリ構造:
- tests/unit/: ユニットテスト（外部依存なし）
- tests/integration/: 統合テスト（DB/API連携）
- tests/e2e/: E2Eテスト（ブラウザ操作）

既存のテストは現在の場所に保持され、リファクタリングの安全網として機能します。
"""

import os
import sys

import pytest


# プロジェクトのルートディレクトリをPythonパスに追加
sys.path.insert(
    0, os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
)
# appディレクトリもPythonパスに追加
sys.path.insert(
    0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "app"))
)


@pytest.fixture
def app():
    """Flaskアプリケーションのテスト用フィクスチャ."""
    from app import app

    app.config["TESTING"] = True
    return app


@pytest.fixture
def client(app):
    """Flaskテストクライアント."""
    return app.test_client()


# ===== 共通フィクスチャエリア =====
# 今後、テストレベル共通で使用するフィクスチャをここに追加します
# 例: モックDB、テストデータ、共通セットアップ等
