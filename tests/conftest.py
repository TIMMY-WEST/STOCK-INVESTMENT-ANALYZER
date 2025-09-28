import pytest
import sys
import os

# プロジェクトのルートディレクトリをPythonパスに追加
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

@pytest.fixture
def app():
    """Flaskアプリケーションのテスト用フィクスチャ"""
    from app import app
    app.config['TESTING'] = True
    return app

@pytest.fixture
def client(app):
    """Flaskテストクライアント"""
    return app.test_client()