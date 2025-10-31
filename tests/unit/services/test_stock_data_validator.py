"""StockDataValidatorのテスト."""

import pandas as pd
import pytest

from app.services.stock_data.validator import (
    StockDataValidationError,
    StockDataValidator,
)


class TestStockDataValidator:
    """StockDataValidatorのテスト."""

    @pytest.fixture
    def validator(self):
        """バリデーターインスタンス."""
        return StockDataValidator()

    def test_stock_data_validator_validate_symbol_with_valid_symbol_returns_true(
        self, validator
    ):
        """有効な銘柄コードのテスト."""
        # Arrange (準備)
        # validatorはfixtureで準備済み

        # Act (実行)
        result_1 = validator.is_valid_stock_code("7203.T")
        result_2 = validator.is_valid_stock_code("AAPL")
        result_3 = validator.is_valid_stock_code("1234.T")

        # Assert (検証)
        assert result_1 is True
        assert result_2 is True
        assert result_3 is True

    def test_stock_data_validator_validate_symbol_with_invalid_symbol_returns_false(
        self, validator
    ):
        """無効な銘柄コードのテスト."""
        # Arrange (準備)
        # validatorはfixtureで準備済み

        # Act (実行)
        result_empty = validator.is_valid_stock_code("")
        result_none = validator.is_valid_stock_code(None)
        result_123a = validator.is_valid_stock_code("123A")
        result_special = validator.is_valid_stock_code("!@#$")

        # Assert (検証)
        assert result_empty is False
        assert result_none is False
        assert result_123a is False
        assert result_special is False

    def test_format_symbol_for_yahoo(self, validator):
        """Yahoo Finance用銘柄コードフォーマットのテスト."""
        # Arrange (準備)
        # validatorはfixtureで準備済み

        # Act (実行)
        result_1 = validator.format_symbol_for_yahoo("7203")
        result_2 = validator.format_symbol_for_yahoo("7203.T")
        result_3 = validator.format_symbol_for_yahoo("AAPL")

        # Assert (検証)
        assert result_1 == "7203.T"
        assert result_2 == "7203.T"
        assert result_3 == "AAPL"

    def test_is_valid_price_data_valid(self, validator):
        """有効な価格データのテスト."""
        # Arrange (準備)
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

        # Act (実行)
        result = validator.is_valid_price_data(df)

        # Assert (検証)
        assert result is True

    def test_is_valid_price_data_invalid(self, validator):
        """無効な価格データのテスト."""
        # Arrange (準備)
        df_empty = pd.DataFrame()
        df_missing_cols = pd.DataFrame({"Open": [100.0], "High": [105.0]})

        # Act (実行)
        result_empty = validator.is_valid_price_data(df_empty)
        result_missing = validator.is_valid_price_data(df_missing_cols)

        # Assert (検証)
        assert result_empty is False
        assert result_missing is False

    def test_validate_and_filter_symbols(self, validator):
        """銘柄コードのバリデーションとフィルタリングのテスト."""
        # Arrange (準備)
        symbols = [
            "7203.T",
            "AAPL",
            "123A",
            "",
            "1234.T",
        ]

        # Act (実行)
        valid_symbols, invalid_symbols = validator.validate_and_filter_symbols(
            symbols
        )

        # Assert (検証)
        assert len(valid_symbols) == 3
        assert "7203.T" in valid_symbols
        assert "AAPL" in valid_symbols
        assert "1234.T" in valid_symbols
        assert len(invalid_symbols) == 2
        assert "123A" in invalid_symbols
        assert "" in invalid_symbols

    def test_validate_dataframe_structure_valid(self, validator):
        """有効なDataFrame構造のテスト."""
        # Arrange (準備)
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

        # Act (実行)
        # 例外が発生しないことを確認
        validator.validate_dataframe_structure(df, "7203.T")

        # Assert (検証)
        # 例外が発生しなければ成功

    def test_validate_dataframe_structure_invalid(self, validator):
        """無効なDataFrame構造のテスト."""
        # Arrange (準備)
        from app.services.stock_data.validator import StockDataValidationError

        df_empty = pd.DataFrame()
        df_missing_cols = pd.DataFrame({"Open": [100.0], "High": [105.0]})

        # Act & Assert (実行と検証)
        # 空のDataFrame
        with pytest.raises(StockDataValidationError, match="データが取得できませんでした"):
            validator.validate_dataframe_structure(df_empty, "7203.T")

        # 必要な列が不足
        with pytest.raises(StockDataValidationError, match="無効な価格データです"):
            validator.validate_dataframe_structure(df_missing_cols, "7203.T")

    def test_stock_data_validator_validate_data_with_valid_data_returns_validation_success(
        self, validator
    ):
        """有効なデータのバリデーションテスト."""
        # Arrange (準備)
        df = pd.DataFrame(
            {
                "Open": [100.0],
                "High": [105.0],
                "Low": [99.0],
                "Close": [103.0],
                "Volume": [1000000],
            },
            index=pd.date_range("2023-01-01", periods=1),
        )

        # Act (実行)
        result = validator.is_valid_price_data(df)

        # Assert (検証)
        assert result is True

    def test_stock_data_validator_validate_data_with_invalid_data_returns_validation_error(
        self, validator
    ):
        """無効なデータのバリデーションテスト."""
        # Arrange (準備)
        df = pd.DataFrame(
            {
                "Open": [100.0],
                "High": [105.0],
                "Low": [99.0],
                "Close": [103.0],
                # Volume列が不足
            },
            index=pd.date_range("2023-01-01", periods=1),
        )

        # Act (実行)
        result = validator.is_valid_price_data(df)

        # Assert (検証)
        assert result is False
