import pytest
import sys
import os
import tempfile
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# プロジェクトのルートディレクトリをPythonパスに追加
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# テスト用のデータベース設定
TEST_DATABASE_URL = "sqlite:///:memory:"  # インメモリデータベースを使用

@pytest.fixture(scope="session")
def test_engine():
    """テスト用データベースエンジン"""
    engine = create_engine(TEST_DATABASE_URL, echo=False)
    return engine

@pytest.fixture(scope="session")
def test_session_factory(test_engine):
    """テスト用セッションファクトリ"""
    return sessionmaker(bind=test_engine)

@pytest.fixture
def test_db_session(test_engine, test_session_factory):
    """テスト用データベースセッション"""
    # テーブルを作成
    from models import Base
    Base.metadata.create_all(test_engine)
    
    # セッションを作成
    session = test_session_factory()
    
    try:
        yield session
    finally:
        session.close()
        # テーブルをクリーンアップ
        Base.metadata.drop_all(test_engine)

@pytest.fixture
def app():
    """Flaskアプリケーションのテスト用フィクスチャ"""
    from app import app
    app.config['TESTING'] = True
    app.config['DATABASE_URL'] = TEST_DATABASE_URL
    return app

@pytest.fixture
def client(app):
    """Flaskテストクライアント"""
    return app.test_client()

@pytest.fixture
def mock_yfinance_data():
    """yfinanceのモックデータ"""
    import pandas as pd
    from datetime import datetime, timedelta
    
    # サンプルデータを作成
    dates = pd.date_range(start='2024-01-01', end='2024-01-10', freq='D')
    data = {
        'Open': [100.0, 101.0, 102.0, 103.0, 104.0, 105.0, 106.0, 107.0, 108.0, 109.0],
        'High': [105.0, 106.0, 107.0, 108.0, 109.0, 110.0, 111.0, 112.0, 113.0, 114.0],
        'Low': [95.0, 96.0, 97.0, 98.0, 99.0, 100.0, 101.0, 102.0, 103.0, 104.0],
        'Close': [102.0, 103.0, 104.0, 105.0, 106.0, 107.0, 108.0, 109.0, 110.0, 111.0],
        'Volume': [1000, 1100, 1200, 1300, 1400, 1500, 1600, 1700, 1800, 1900]
    }
    
    return pd.DataFrame(data, index=dates)