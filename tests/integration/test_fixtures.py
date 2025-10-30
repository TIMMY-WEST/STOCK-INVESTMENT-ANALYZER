"""共通フィクスチャの動作確認テスト.

このモジュールは、conftest.pyで定義された共通フィクスチャが
正しく動作することを検証します。
"""

import pandas as pd
import pytest


class TestDatabaseFixtures:
    """データベース関連フィクスチャのテスト."""

    def test_mock_db_session_basic(self, mock_db_session):
        """mock_db_sessionの基本動作を確認."""
        assert mock_db_session is not None
        assert hasattr(mock_db_session, "commit")
        assert hasattr(mock_db_session, "rollback")
        assert hasattr(mock_db_session, "close")
        assert hasattr(mock_db_session, "query")
        assert hasattr(mock_db_session, "add")

    def test_mock_db_session_commit(self, mock_db_session):
        """mock_db_sessionのcommitメソッドが呼び出せることを確認."""
        mock_db_session.commit()
        mock_db_session.commit.assert_called()

    def test_mock_db_session_rollback(self, mock_db_session):
        """mock_db_sessionのrollbackメソッドが呼び出せることを確認."""
        mock_db_session.rollback()
        mock_db_session.rollback.assert_called()

    def test_test_db_session_context(self, test_db_session):
        """test_db_sessionがコンテキストマネージャーとして動作することを確認."""
        assert test_db_session is not None

        # コンテキストマネージャーとして使用
        with test_db_session as session:
            assert session is not None
            assert hasattr(session, "commit")
            assert hasattr(session, "rollback")
            assert hasattr(session, "close")


class TestDataFixtures:
    """テストデータフィクスチャのテスト."""

    def test_sample_stock_data_structure(self, sample_stock_data):
        """sample_stock_dataの構造を確認."""
        assert isinstance(sample_stock_data, dict)
        assert "symbol" in sample_stock_data
        assert "name" in sample_stock_data
        assert "open" in sample_stock_data
        assert "high" in sample_stock_data
        assert "low" in sample_stock_data
        assert "close" in sample_stock_data
        assert "volume" in sample_stock_data
        assert "date" in sample_stock_data

    def test_sample_stock_data_values(self, sample_stock_data):
        """sample_stock_dataの値を確認."""
        assert sample_stock_data["symbol"] == "7203.T"
        assert sample_stock_data["name"] == "Toyota Motor Corporation"
        assert sample_stock_data["open"] == 1000.0
        assert sample_stock_data["high"] == 1050.0
        assert sample_stock_data["low"] == 990.0
        assert sample_stock_data["close"] == 1020.0
        assert sample_stock_data["volume"] == 1000000
        assert sample_stock_data["date"] == "2025-01-01"

    def test_sample_stock_data_mutable(self, sample_stock_data):
        """sample_stock_dataが変更可能であることを確認."""
        original_close = sample_stock_data["close"]
        sample_stock_data["close"] = 2000.0
        assert sample_stock_data["close"] == 2000.0
        assert sample_stock_data["close"] != original_close

    def test_sample_stock_list_structure(self, sample_stock_list):
        """sample_stock_listの構造を確認."""
        assert isinstance(sample_stock_list, list)
        assert len(sample_stock_list) == 3

        for stock in sample_stock_list:
            assert isinstance(stock, dict)
            assert "symbol" in stock
            assert "name" in stock
            assert "close" in stock

    def test_sample_stock_list_values(self, sample_stock_list):
        """sample_stock_listの値を確認."""
        symbols = [stock["symbol"] for stock in sample_stock_list]
        assert "7203.T" in symbols
        assert "6758.T" in symbols
        assert "9984.T" in symbols

    def test_sample_dataframe_structure(self, sample_dataframe):
        """sample_dataframeの構造を確認."""
        assert isinstance(sample_dataframe, pd.DataFrame)
        assert not sample_dataframe.empty
        assert len(sample_dataframe) == 1

        # カラムの存在確認
        expected_columns = ["Open", "High", "Low", "Close", "Volume"]
        for col in expected_columns:
            assert col in sample_dataframe.columns

    def test_sample_dataframe_values(self, sample_dataframe):
        """sample_dataframeの値を確認."""
        assert sample_dataframe["Open"].iloc[0] == 1000.0
        assert sample_dataframe["High"].iloc[0] == 1050.0
        assert sample_dataframe["Low"].iloc[0] == 990.0
        assert sample_dataframe["Close"].iloc[0] == 1020.0
        assert sample_dataframe["Volume"].iloc[0] == 1000000

    def test_sample_dataframe_index(self, sample_dataframe):
        """sample_dataframeのインデックスを確認."""
        assert isinstance(sample_dataframe.index, pd.DatetimeIndex)
        assert len(sample_dataframe.index) == 1


class TestMockHelpers:
    """モックヘルパーフィクスチャのテスト."""

    def test_mock_yfinance_ticker_exists(self, mock_yfinance_ticker):
        """mock_yfinance_tickerが存在することを確認."""
        assert mock_yfinance_ticker is not None

    def test_mock_yfinance_ticker_history(
        self, mock_yfinance_ticker, sample_dataframe
    ):
        """mock_yfinance_tickerのhistoryメソッドを確認."""
        import yfinance as yf

        ticker = yf.Ticker("7203.T")
        data = ticker.history(period="1d")

        assert not data.empty
        assert "Close" in data.columns
        # DataFrameの内容がsample_dataframeと一致することを確認
        pd.testing.assert_frame_equal(data, sample_dataframe)

    def test_mock_yfinance_ticker_info(self, mock_yfinance_ticker):
        """mock_yfinance_tickerのinfo属性を確認."""
        import yfinance as yf

        ticker = yf.Ticker("7203.T")
        info = ticker.info

        assert isinstance(info, dict)
        assert info["symbol"] == "7203.T"
        assert info["longName"] == "Toyota Motor Corporation"
        assert info["currency"] == "JPY"
        assert info["exchange"] == "JPX"

    def test_mock_yfinance_download_exists(self, mock_yfinance_download):
        """mock_yfinance_downloadが存在することを確認."""
        assert mock_yfinance_download is not None

    def test_mock_yfinance_download_call(
        self, mock_yfinance_download, sample_dataframe
    ):
        """mock_yfinance_downloadが呼び出せることを確認."""
        import yfinance as yf

        data = yf.download(["7203.T", "6758.T"], period="1d")

        assert not data.empty
        # DataFrameの内容がsample_dataframeと一致することを確認
        pd.testing.assert_frame_equal(data, sample_dataframe)
        mock_yfinance_download.assert_called_once()


class TestFlaskFixtures:
    """Flask関連フィクスチャのテスト."""

    def test_fixtures_app_fixture_exists_with_flask_app_returns_valid_instance(
        self, app
    ):
        """appフィクスチャが存在することを確認."""
        assert app is not None

    def test_fixtures_app_testing_mode_with_flask_app_returns_testing_enabled(
        self, app
    ):
        """appがテストモードであることを確認."""
        assert app.config["TESTING"] is True

    def test_client_fixture_exists(self, client):
        """clientフィクスチャが存在することを確認."""
        assert client is not None

    def test_client_can_make_request(self, client):
        """clientでリクエストが送信できることを確認."""
        # ルートパスにアクセス（存在しなくても404が返る）
        response = client.get("/")
        # レスポンスが返ってくることを確認（404でもOK）
        assert response is not None
        assert response.status_code in [200, 404]


class TestFixtureIntegration:
    """フィクスチャ間の統合テスト."""

    def test_sample_dataframe_uses_sample_stock_data(
        self, sample_stock_data, sample_dataframe
    ):
        """sample_dataframeがsample_stock_dataを使用していることを確認."""
        # sample_dataframeの値がsample_stock_dataと一致することを確認
        assert sample_dataframe["Open"].iloc[0] == sample_stock_data["open"]
        assert sample_dataframe["High"].iloc[0] == sample_stock_data["high"]
        assert sample_dataframe["Low"].iloc[0] == sample_stock_data["low"]
        assert sample_dataframe["Close"].iloc[0] == sample_stock_data["close"]
        assert (
            sample_dataframe["Volume"].iloc[0] == sample_stock_data["volume"]
        )

    def test_mock_yfinance_ticker_uses_sample_dataframe(
        self, mock_yfinance_ticker, sample_dataframe
    ):
        """mock_yfinance_tickerがsample_dataframeを使用していることを確認."""
        import yfinance as yf

        ticker = yf.Ticker("7203.T")
        data = ticker.history(period="1d")

        # 返されるDataFrameがsample_dataframeと一致することを確認
        pd.testing.assert_frame_equal(data, sample_dataframe)

    def test_multiple_fixtures_together(
        self,
        mock_db_session,
        sample_stock_data,
        sample_dataframe,
        mock_yfinance_ticker,
    ):
        """複数のフィクスチャを同時に使用できることを確認."""
        # すべてのフィクスチャが正常に使用できることを確認
        assert mock_db_session is not None
        assert sample_stock_data is not None
        assert sample_dataframe is not None
        assert mock_yfinance_ticker is not None

        # それぞれが期待通りに動作することを確認
        assert sample_stock_data["symbol"] == "7203.T"
        assert not sample_dataframe.empty
        mock_db_session.commit()
        mock_db_session.commit.assert_called()
