"""StockDataValidatorのテスト."""

import pandas as pd
import pytest

from services.stock_data.validator import (
    StockDataValidationError,
    StockDataValidator,
)


class TestStockDataValidator:
    """StockDataValidatorのテスト."""

    @pytest.fixture
    def validator(self):
        """バリデーターインスタンス."""
        return StockDataValidator()

    def test_is_valid_stock_code_valid(self, validator):
        """有効な銘柄コードのテスト."""
        assert validator.is_valid_stock_code("7203.T") is True
        assert validator.is_valid_stock_code("AAPL") is True
        assert validator.is_valid_stock_code("1234.T") is True

    def test_is_valid_stock_code_invalid(self, validator):
        """無効な銘柄コードのテスト."""
        assert validator.is_valid_stock_code("") is False
        assert validator.is_valid_stock_code(None) is False
        assert (
            validator.is_valid_stock_code("123A") is False
        )  # 数字+A形式は無効
        assert validator.is_valid_stock_code("!@#$") is False  # 特殊文字は無効

    def test_format_symbol_for_yahoo(self, validator):
        """Yahoo Finance用銘柄コードフォーマットのテスト."""
        assert validator.format_symbol_for_yahoo("7203") == "7203.T"
        assert validator.format_symbol_for_yahoo("7203.T") == "7203.T"
        assert validator.format_symbol_for_yahoo("AAPL") == "AAPL"

    def test_is_valid_price_data_valid(self, validator):
        """有効な価格データのテスト."""
        df = pd.DataFrame(
            {
                "Open": [100.0],
                "High": [105.0],
                "Low": [99.0],
                "Close": [103.0],
                "Volume": [1000000],
            },
            index=pd.date_range("2024-01-01", periods=1),
        )

        assert validator.is_valid_price_data(df) is True

    def test_is_valid_price_data_invalid(self, validator):
        """無効な価格データのテスト."""
        # 空のDataFrame
        assert validator.is_valid_price_data(pd.DataFrame()) is False

        # 必要な列が不足
        df_missing_cols = pd.DataFrame({"Open": [100.0], "High": [105.0]})
        assert validator.is_valid_price_data(df_missing_cols) is False

    def test_validate_and_filter_symbols(self, validator):
        """銘柄コードのバリデーションとフィルタリングのテスト."""
        symbols = [
            "7203.T",
            "AAPL",
            "123A",
            "",
            "1234.T",
        ]  # "123A"は無効（数字+A形式）
        valid_symbols, invalid_symbols = validator.validate_and_filter_symbols(
            symbols
        )

        assert len(valid_symbols) == 3
        assert "7203.T" in valid_symbols
        assert "AAPL" in valid_symbols
        assert "1234.T" in valid_symbols
        assert len(invalid_symbols) == 2
        assert "123A" in invalid_symbols
        assert "" in invalid_symbols

    def test_validate_dataframe_structure_valid(self, validator):
        """有効なDataFrame構造のテスト."""
        df = pd.DataFrame(
            {
                "Open": [100.0],
                "High": [105.0],
                "Low": [99.0],
                "Close": [103.0],
                "Volume": [1000000],
            },
            index=pd.date_range("2024-01-01", periods=1),
        )

        # 例外が発生しないことを確認
        validator.validate_dataframe_structure(df, "7203.T")

    def test_validate_dataframe_structure_invalid(self, validator):
        """無効なDataFrame構造のテスト."""
        from services.stock_data.validator import StockDataValidationError

        # 空のDataFrame
        with pytest.raises(
            StockDataValidationError, match="データが取得できませんでした"
        ):
            validator.validate_dataframe_structure(pd.DataFrame(), "7203.T")

        # 必要な列が不足
        df_missing_cols = pd.DataFrame({"Open": [100.0], "High": [105.0]})
        with pytest.raises(
            StockDataValidationError, match="無効な価格データです"
        ):
            validator.validate_dataframe_structure(df_missing_cols, "7203.T")
