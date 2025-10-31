"""StockDataConverterのテスト."""

from datetime import date, datetime

import pandas as pd
import pytest

from app.services.stock_data.converter import (
    StockDataConversionError,
    StockDataConverter,
)


class TestStockDataConverter:
    """StockDataConverterのテスト."""

    @pytest.fixture
    def converter(self):
        """コンバーターインスタンス."""
        return StockDataConverter()

    @pytest.fixture
    def sample_dataframe(self):
        """サンプルDataFrame.

        Note: conftest.py にも sample_dataframe がありますが、
        このテストでは複数行のデータが必要なため、専用フィクスチャを使用します。
        """
        return pd.DataFrame(
            {
                "Open": [100.0, 103.0],
                "High": [105.0, 108.0],
                "Low": [99.0, 102.0],
                "Close": [103.0, 106.0],
                "Volume": [1000000, 1100000],
            },
            index=pd.date_range("2024-01-01", periods=2),
        )

    def test_converter_convert_to_dict_with_sample_dataframe_returns_list(
        self, converter, sample_dataframe
    ):
        """DataFrameから辞書リストへの変換テスト."""
        # Arrange (準備)
        # converterとsample_dataframeフィクスチャを使用

        # Act (実行)
        result = converter.convert_to_dict(sample_dataframe, "1d")

        # Assert (検証)
        assert isinstance(result, list)
        assert len(result) == 2
        first_record = result[0]
        assert "open" in first_record
        assert "high" in first_record
        assert "low" in first_record
        assert "close" in first_record
        assert "volume" in first_record
        assert "date" in first_record

    def test_converter_convert_to_dict_with_empty_dataframe_returns_empty_list(
        self, converter
    ):
        """空のDataFrameの変換テスト."""
        # Arrange (準備)
        empty_df = pd.DataFrame()

        # Act (実行)
        result = converter.convert_to_dict(empty_df, "1d")

        # Assert (検証)
        assert isinstance(result, list)
        assert len(result) == 0

    def test_converter_extract_price_data_with_sample_dataframe_returns_dict(
        self, converter, sample_dataframe
    ):
        """価格データ抽出のテスト."""
        # Arrange (準備)
        # converterとsample_dataframeフィクスチャを使用

        # Act (実行)
        result = converter.extract_price_data(sample_dataframe)

        # Assert (検証)
        assert isinstance(result, dict)
        assert "latest_close" in result
        assert "latest_date" in result
        assert "record_count" in result
        assert "date_range" in result
        assert result["record_count"] == 2

    def test_converter_extract_price_data_with_single_row_returns_correct_values(
        self, converter
    ):
        """単一行のDataFrameでの価格データ抽出テスト."""
        # Arrange (準備)
        single_df = pd.DataFrame(
            {
                "Open": [100.0],
                "High": [105.0],
                "Low": [99.0],
                "Close": [103.0],
                "Volume": [1000000],
            },
            index=pd.date_range("2024-01-01", periods=1),
        )

        # Act (実行)
        result = converter.extract_price_data(single_df)

        # Assert (検証)
        assert result["latest_close"] == 103.0
        assert result["record_count"] == 1
        assert "latest_date" in result

    def test_converter_get_latest_data_date_with_sample_dataframe_returns_datetime(
        self, converter, sample_dataframe
    ):
        """最新データ日時取得のテスト."""
        # Arrange (準備)
        # converterとsample_dataframeフィクスチャを使用

        # Act (実行)
        result = converter.get_latest_data_date(sample_dataframe)

        # Assert (検証)
        assert isinstance(result, datetime)
        assert result.date() == date(2024, 1, 2)

    def test_converter_get_latest_data_date_with_empty_dataframe_raises_error(
        self, converter
    ):
        """空のDataFrameでの最新データ日時取得テスト."""
        # Arrange (準備)
        empty_df = pd.DataFrame()

        # Act & Assert (実行と検証)
        with pytest.raises(StockDataConversionError):
            converter.get_latest_data_date(empty_df)

    def test_converter_split_multi_symbol_result_with_multi_index_returns_dict(
        self, converter
    ):
        """複数銘柄データの分割テスト."""
        # Arrange (準備)
        symbols = ["AAPL", "GOOGL"]
        columns = pd.MultiIndex.from_product([["Open", "Close"], symbols])
        data = [[100, 150, 200, 250], [101, 151, 201, 251]]
        multi_df = pd.DataFrame(data, columns=columns)

        # Act (実行)
        result = converter.split_multi_symbol_result(multi_df, symbols)

        # Assert (検証)
        assert len(result) == 2
        assert "AAPL" in result
        assert "GOOGL" in result
        assert isinstance(result["AAPL"], pd.DataFrame)
        assert isinstance(result["GOOGL"], pd.DataFrame)

    def test_converter_format_summary_data_with_results_returns_formatted_dict(
        self, converter
    ):
        """サマリーデータフォーマットのテスト."""
        # Arrange (準備)
        results = {
            "success": True,
            "record_count": 100,
            "latest_date": datetime(2024, 1, 1),
            "error": None,
        }

        # Act (実行)
        summary = converter.format_summary_data(results, "7203.T", "1d")

        # Assert (検証)
        assert summary["success"] is True
        assert summary["record_count"] == 100
        assert summary["symbol"] == "7203.T"
        assert summary["interval"] == "1d"
        assert "timestamp" in summary

    def test_converter_create_record_from_row_with_series_returns_record_dict(
        self, converter
    ):
        """行からレコード作成のテスト."""
        # Arrange (準備)
        row = pd.Series(
            {
                "Open": 100.0,
                "High": 110.0,
                "Low": 95.0,
                "Close": 105.0,
                "Volume": 1000,
            },
            name=datetime(2024, 1, 1),
        )

        # Act (実行)
        record = converter._create_record_from_row(
            datetime(2024, 1, 1), row, "1d"
        )

        # Assert (検証)
        assert record["open"] == 100.0
        assert record["high"] == 110.0
        assert record["low"] == 95.0
        assert record["close"] == 105.0
        assert record["volume"] == 1000
        assert record["date"] == date(2024, 1, 1)
