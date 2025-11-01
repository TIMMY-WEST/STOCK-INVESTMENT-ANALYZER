"""株価データバリデーションサービス.

このモジュールは株価データの検証機能を提供します。
"""

import logging
import re
from typing import List

import pandas as pd

from app.utils.timeframe_utils import validate_interval


logger = logging.getLogger(__name__)


class StockDataValidationError(Exception):
    """データ検証エラー."""

    pass


class StockDataValidator:
    """株価データ検証クラス."""

    def __init__(self):
        """初期化."""
        self.logger = logger

    def is_valid_stock_code(self, symbol: str) -> bool:
        """有効な銘柄コードかチェック.

        Args:
            symbol: 銘柄コード

        Returns:
            有効な場合True。
        """
        if not symbol or not isinstance(symbol, str):
            return False

        # .T サフィックスを除去
        code = symbol.replace(".T", "")

        # 日本株で無効なパターンを除外
        # 英字と数字が混在する場合は除外（純粋なアルファベットは許可）
        if re.search(r"[A-Za-z]", code) and not code.isalpha():
            # ただし、米国株の特殊形式（例: BRK.A）は許可
            if "." not in code:
                self.logger.debug(f"無効な銘柄コード（英数字混在パターン）: {symbol}")
                return False

        # 有効なパターンをチェック
        # 数字のみ（4桁）が日本株の標準形式
        if code.isdigit() and len(code) == 4:
            return True

        # 複雑な米国株形式（例: BRK.A, BRK.B）
        if "." in code and len(code) > 4:
            return True

        # 純粋なアルファベットのみ、または特定の形式
        if code.replace(".", "").replace("-", "").isalpha() and len(code) >= 1:
            return True

        return False

    def format_symbol_for_yahoo(self, symbol: str) -> str:
        """Yahoo Finance用の銘柄コードフォーマット.

        Args:
            symbol: 銘柄コード

        Returns:
            Yahoo Finance用にフォーマットされた銘柄コード。
        """
        if not symbol:
            return symbol

        # 既に.Tサフィックスがある場合はそのまま
        if symbol.endswith(".T"):
            return symbol

        # 4桁の数字の場合は.Tを追加（日本株）
        if symbol.isdigit() and len(symbol) == 4:
            return f"{symbol}.T"

        return symbol

    def is_valid_price_data(self, df: pd.DataFrame) -> bool:
        """価格データの妥当性をチェック.

        Args:
            df: 価格データのDataFrame

        Returns:
            妥当な場合True。
        """
        if df.empty:
            return False

        required_columns = ["Open", "High", "Low", "Close", "Volume"]
        if not all(col in df.columns for col in required_columns):
            return False

        # 価格データが数値であることを確認
        price_columns = ["Open", "High", "Low", "Close"]
        for col in price_columns:
            if not pd.api.types.is_numeric_dtype(df[col]):
                return False

        # 負の価格がないことを確認
        for col in price_columns:
            if (df[col] < 0).any():
                return False

        # High >= Low の関係を確認
        if (df["High"] < df["Low"]).any():
            return False

        return True

    def validate_and_filter_symbols(
        self, symbols: List[str]
    ) -> tuple[List[str], List[str]]:
        """銘柄コードのバリデーションとフィルタリング.

        Args:
            symbols: 銘柄コードのリスト

        Returns:
            (有効な銘柄コードのリスト, 無効な銘柄コードのリスト)
        """
        valid_symbols = []
        invalid_symbols = []

        for symbol in symbols:
            if self.is_valid_stock_code(symbol):
                formatted_symbol = self.format_symbol_for_yahoo(symbol)
                valid_symbols.append(formatted_symbol)
            else:
                invalid_symbols.append(symbol)

        return valid_symbols, invalid_symbols

    def validate_symbol_input(self, symbol: str) -> str:
        """銘柄コード入力の検証とフォーマット.

        Args:
            symbol: 銘柄コード

        Returns:
            フォーマットされた銘柄コード

        Raises:
            StockDataValidationError: 無効な銘柄コードの場合
        """
        if not symbol:
            raise StockDataValidationError(f"無効な銘柄コード: {symbol}")

        if not self.is_valid_stock_code(symbol):
            raise StockDataValidationError(f"無効な銘柄コード: {symbol}")

        return self.format_symbol_for_yahoo(symbol)

    def validate_dataframe_structure(
        self, df: pd.DataFrame, symbol: str
    ) -> None:
        """DataFrameの構造を検証.

        Args:
            df: 検証対象のDataFrame
            symbol: 銘柄コード

        Raises:
            StockDataValidationError: データが無効な場合
        """
        if df.empty:
            raise StockDataValidationError(f"データが取得できませんでした: {symbol}")

        if not self.is_valid_price_data(df):
            raise StockDataValidationError(f"無効な価格データです: {symbol}")

        self.logger.debug(f"データ検証完了: {symbol} - {len(df)}件")

    def validate_interval(self, interval: str) -> bool:
        """時間間隔の妥当性をチェック.

        Args:
            interval: 時間間隔

        Returns:
            妥当な場合True。
        """
        return validate_interval(interval)
