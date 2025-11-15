"""データベース操作に関するエラークラス定義."""


class DatabaseError(Exception):
    """データベース操作エラーの基底クラス."""

    pass


class StockDataError(DatabaseError):
    """株価データ関連エラー."""

    pass
