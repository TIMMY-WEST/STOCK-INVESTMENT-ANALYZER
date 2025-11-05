"""テスト共通の fixtures を置く conftest です.

このファイルには、ドキュメント読み込み用の fixture を配置して
複数のテストファイルで共有できるようにします.
"""

import os
from pathlib import Path
import sys

import pytest


@pytest.fixture(scope="session")
def guide_content_and_path():
    """docs/api/api_usage_guide.md の内容とパスを返す fixture."""
    guide_path = Path("docs/api/api_usage_guide.md")
    project_root = Path(__file__).parent.parent
    full_guide_path = project_root / guide_path
    assert full_guide_path.exists(), f"API使用例ガイドが存在しません: {full_guide_path}"
    content = full_guide_path.read_text(encoding="utf-8")
    return {"path": full_guide_path, "content": content}


# プロジェクトのルートディレクトリをPythonパスに追加
sys.path.insert(
    0, os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
)


@pytest.fixture
def app():
    """Flaskアプリケーションのテスト用フィクスチャ."""
    from app.app import app

    app.config["TESTING"] = True
    return app


@pytest.fixture
def client(app):
    """Flaskテストクライアント."""
    return app.test_client()


# ===== 共通フィクスチャエリア =====
# 今後、テストレベル共通で使用するフィクスチャをここに追加します
# 例: モックDB、テストデータ、共通セットアップ等


# ===== 環境設定フィクスチャ =====
@pytest.fixture
def setup_test_env(monkeypatch):
    """テスト環境変数のセットアップ.

    API_KEYやRATE_LIMIT等の環境変数を設定します。
    各テストで必要に応じてこのフィクスチャを使用できます。

    Args:
        monkeypatch: pytestのmonkeypatchフィクスチャ

    Example:
        def test_with_env(setup_test_env):
            # 環境変数が設定された状態でテスト
            pass
    """
    monkeypatch.setenv("API_KEY", "test-key")
    monkeypatch.setenv("RATE_LIMIT_PER_MINUTE", "10")


# ===== データベース関連フィクスチャ =====
@pytest.fixture
def mock_db_session(mocker):
    """テスト用のモックデータベースセッション.

    外部DBに依存しない軽量なモックセッションを提供します。
    単体テストでの使用を推奨します。

    Returns:
        Mock: モックされたSQLAlchemyセッション

    Example:
        def test_example(mock_db_session):
            # モックセッションを使用してテスト
            result = some_function(mock_db_session)
            assert result is not None
    """
    session = mocker.Mock()
    session.commit = mocker.Mock()
    session.rollback = mocker.Mock()
    session.close = mocker.Mock()
    session.query = mocker.Mock()
    session.add = mocker.Mock()
    return session


@pytest.fixture
def test_db_session(mocker):
    """テスト用データベースセッションのコンテキストマネージャー.

    実際のDBコネクションをモック化し、安全なテスト環境を提供します。
    統合テストでの使用を推奨します。

    Yields:
        Mock: get_db_session()のモック

    Example:
        def test_with_db(test_db_session):
            with test_db_session as session:
                # セッションを使用した処理
                pass
    """
    mock_session = mocker.Mock()
    mock_session.commit = mocker.Mock()
    mock_session.rollback = mocker.Mock()
    mock_session.close = mocker.Mock()

    # コンテキストマネージャーとして動作するモック
    mock_context = mocker.MagicMock()
    mock_context.__enter__ = mocker.Mock(return_value=mock_session)
    mock_context.__exit__ = mocker.Mock(return_value=False)

    return mock_context


# ===== テストデータファクトリー =====
@pytest.fixture
def sample_stock_data():
    """サンプル株価データを提供.

    基本的な株価データの辞書を返します。
    テストケースで必要に応じてカスタマイズ可能です。

    Returns:
        dict: サンプル株価データ

    Example:
        def test_stock_data(sample_stock_data):
            assert sample_stock_data["symbol"] == "7203.T"
            # 必要に応じて値を変更
            sample_stock_data["price"] = 2000.0
    """
    return {
        "symbol": "7203.T",
        "name": "Toyota Motor Corporation",
        "open": 1000.0,
        "high": 1050.0,
        "low": 990.0,
        "close": 1020.0,
        "volume": 1000000,
        "date": "2025-01-01",
    }


@pytest.fixture
def sample_stock_list():
    """複数銘柄のサンプルデータリストを提供.

    バルク処理のテストで使用する複数銘柄のリストです。

    Returns:
        list[dict]: 複数銘柄のサンプルデータ

    Example:
        def test_bulk_process(sample_stock_list):
            assert len(sample_stock_list) == 3
            for stock in sample_stock_list:
                process_stock(stock)
    """
    return [
        {
            "symbol": "7203.T",
            "name": "Toyota Motor Corporation",
            "close": 1000.0,
        },
        {
            "symbol": "6758.T",
            "name": "Sony Group Corporation",
            "close": 12000.0,
        },
        {
            "symbol": "9984.T",
            "name": "SoftBank Group Corp.",
            "close": 5000.0,
        },
    ]


@pytest.fixture
def sample_dataframe(sample_stock_data):
    """サンプル株価データのDataFrameを提供.

    pandas DataFrameとしての株価データを返します。
    yfinanceのhistory()メソッドの戻り値を模倣します。

    Args:
        sample_stock_data: サンプル株価データフィクスチャ

    Returns:
        pandas.DataFrame: 株価データのDataFrame

    Example:
        def test_dataframe_processing(sample_dataframe):
            assert not sample_dataframe.empty
            assert "Close" in sample_dataframe.columns
    """
    from datetime import datetime

    import pandas as pd

    data = {
        "Open": [sample_stock_data["open"]],
        "High": [sample_stock_data["high"]],
        "Low": [sample_stock_data["low"]],
        "Close": [sample_stock_data["close"]],
        "Volume": [sample_stock_data["volume"]],
    }
    index = pd.DatetimeIndex(
        [datetime.fromisoformat(sample_stock_data["date"])]
    )

    return pd.DataFrame(data, index=index)


# ===== モックヘルパー =====
@pytest.fixture
def mock_yfinance_ticker(mocker, sample_dataframe):
    """Yahoo Finance APIのTickerクラスをモック化.

    yfinance.Tickerの動作をモック化し、外部API呼び出しなしでテスト可能にします。

    Args:
        mocker: pytest-mockのmockerフィクスチャ
        sample_dataframe: サンプルDataFrameフィクスチャ

    Returns:
        Mock: モック化されたTickerインスタンス

    Example:
        def test_fetch_stock_data(mock_yfinance_ticker):
            # yfinance.Ticker()が自動的にモックを返す
            data = fetch_stock_data("7203.T")
            assert data is not None
    """
    mock_ticker = mocker.patch("yfinance.Ticker")
    mock_instance = mocker.Mock()

    # history()メソッドのモック
    mock_instance.history.return_value = sample_dataframe

    # info属性のモック（銘柄情報）
    mock_instance.info = {
        "symbol": "7203.T",
        "longName": "Toyota Motor Corporation",
        "currency": "JPY",
        "exchange": "JPX",
    }

    mock_ticker.return_value = mock_instance

    return mock_ticker


@pytest.fixture
def mock_yfinance_download(mocker, sample_dataframe):
    """Yahoo Finance APIのdownload関数をモック化.

    yfinance.download()の動作をモック化します。
    複数銘柄の一括取得をテストする際に使用します。

    Args:
        mocker: pytest-mockのmockerフィクスチャ
        sample_dataframe: サンプルDataFrameフィクスチャ

    Returns:
        Mock: モック化されたdownload関数

    Example:
        def test_bulk_download(mock_yfinance_download):
            data = yfinance.download(["7203.T", "6758.T"])
            assert not data.empty
    """
    mock_download = mocker.patch("yfinance.download")
    mock_download.return_value = sample_dataframe

    return mock_download
