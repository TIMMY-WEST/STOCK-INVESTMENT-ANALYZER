"""StockDailyモデルのCRUD操作."""

from datetime import date
from typing import Any, Dict, List, Optional

from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session

from app.models.errors import DatabaseError, StockDataError
from app.models.stock_data import StockDaily


class StockDailyCRUD:
    """StockDailyモデルのCRUD操作クラス.

    日足株価データに対する作成、読み取り、更新、削除操作を提供します。
    """

    @staticmethod
    def create(session: Session, **kwargs) -> StockDaily:
        """新しい株価データを作成.

        Args:
            session: データベースセッション
            **kwargs: 株価データの属性

        Returns:
            StockDaily: 作成された株価データ

        Raises:
            StockDataError: データが既に存在する場合
            DatabaseError: データベースエラーが発生した場合
        """
        try:
            stock_data = StockDaily(**kwargs)
            session.add(stock_data)
            session.flush()
            return stock_data
        except IntegrityError as e:
            if "uk_stocks_daily_symbol_date" in str(e):
                raise StockDataError(
                    f"銘柄 {kwargs.get('symbol')} の日付 "
                    f"{kwargs.get('date')} のデータは既に存在します"
                )
            raise DatabaseError(f"データベース制約違反: {str(e)}")
        except SQLAlchemyError as e:
            raise DatabaseError(f"データベースエラー: {str(e)}")

    @staticmethod
    def get_by_id(session: Session, stock_id: int) -> Optional[StockDaily]:
        """IDで株価データを取得.

        Args:
            session: データベースセッション
            stock_id: 株価データのID

        Returns:
            Optional[StockDaily]: 見つかった株価データ、存在しない場合はNone

        Raises:
            DatabaseError: データベースエラーが発生した場合
        """
        try:
            return (
                session.query(StockDaily)
                .filter(StockDaily.id == stock_id)
                .first()
            )
        except SQLAlchemyError as e:
            raise DatabaseError(f"データベースエラー: {str(e)}")

    @staticmethod
    def get_by_symbol_and_date(
        session: Session, symbol: str, date: date
    ) -> Optional[StockDaily]:
        """銘柄コードと日付で株価データを取得.

        Args:
            session: データベースセッション
            symbol: 銘柄コード
            date: 日付

        Returns:
            Optional[StockDaily]: 見つかった株価データ、存在しない場合はNone

        Raises:
            DatabaseError: データベースエラーが発生した場合
        """
        try:
            return (
                session.query(StockDaily)
                .filter(StockDaily.symbol == symbol, StockDaily.date == date)
                .first()
            )
        except SQLAlchemyError as e:
            raise DatabaseError(f"データベースエラー: {str(e)}")

    @staticmethod
    def get_by_symbol(
        session: Session,
        symbol: str,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
    ) -> List[StockDaily]:
        """銘柄コードで株価データを取得(日付降順).

        Args:
            session: データベースセッション
            symbol: 銘柄コード
            limit: 取得件数の上限
            offset: 取得開始位置のオフセット
            start_date: 開始日付(この日付以降)
            end_date: 終了日付(この日付以前)

        Returns:
            List[StockDaily]: 株価データのリスト

        Raises:
            DatabaseError: データベースエラーが発生した場合
        """
        try:
            query = session.query(StockDaily).filter(
                StockDaily.symbol == symbol
            )

            if start_date:
                query = query.filter(StockDaily.date >= start_date)
            if end_date:
                query = query.filter(StockDaily.date <= end_date)

            query = query.order_by(StockDaily.date.desc())

            if offset:
                query = query.offset(offset)
            if limit:
                query = query.limit(limit)

            return query.all()
        except SQLAlchemyError as e:
            raise DatabaseError(f"データベースエラー: {str(e)}")

    @staticmethod
    def get_with_filters(
        session: Session,
        symbol: Optional[str] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
    ) -> List[StockDaily]:
        """フィルタ条件に基づく株価データを取得(日付降順).

        Args:
            session: データベースセッション
            symbol: 銘柄コード(指定時のみフィルタ)
            limit: 取得件数の上限
            offset: 取得開始位置のオフセット
            start_date: 開始日付(この日付以降)
            end_date: 終了日付(この日付以前)

        Returns:
            List[StockDaily]: 株価データのリスト

        Raises:
            DatabaseError: データベースエラーが発生した場合
        """
        try:
            query = session.query(StockDaily)

            if symbol:
                query = query.filter(StockDaily.symbol == symbol)
            if start_date:
                query = query.filter(StockDaily.date >= start_date)
            if end_date:
                query = query.filter(StockDaily.date <= end_date)

            query = query.order_by(StockDaily.date.desc(), StockDaily.symbol)

            if offset:
                query = query.offset(offset)
            if limit:
                query = query.limit(limit)

            return query.all()
        except SQLAlchemyError as e:
            raise DatabaseError(f"データベースエラー: {str(e)}")

    @staticmethod
    def get_all(
        session: Session,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
    ) -> List[StockDaily]:
        """全ての株価データを取得(日付降順).

        Args:
            session: データベースセッション
            limit: 取得件数の上限
            offset: 取得開始位置のオフセット

        Returns:
            List[StockDaily]: 株価データのリスト

        Raises:
            DatabaseError: データベースエラーが発生した場合
        """
        try:
            query = session.query(StockDaily).order_by(
                StockDaily.date.desc(), StockDaily.symbol
            )

            if offset:
                query = query.offset(offset)
            if limit:
                query = query.limit(limit)

            return query.all()
        except SQLAlchemyError as e:
            raise DatabaseError(f"データベースエラー: {str(e)}")

    @staticmethod
    def update(
        session: Session, stock_id: int, **kwargs
    ) -> Optional[StockDaily]:
        """株価データを更新.

        Args:
            session: データベースセッション
            stock_id: 更新対象の株価データID
            **kwargs: 更新するフィールドと値

        Returns:
            Optional[StockDaily]: 更新された株価データ(見つからない場合はNone)

        Raises:
            StockDataError: 銘柄コードと日付の組み合わせが重複した場合
            DatabaseError: データベースエラーが発生した場合
        """
        try:
            stock_data = (
                session.query(StockDaily)
                .filter(StockDaily.id == stock_id)
                .first()
            )
            if not stock_data:
                return None

            for key, value in kwargs.items():
                if hasattr(stock_data, key):
                    setattr(stock_data, key, value)

            # updated_atはonupdateで自動更新されるため、明示的な設定は不要
            session.flush()
            return stock_data
        except IntegrityError as e:
            if "uk_stocks_daily_symbol_date" in str(e):
                raise StockDataError("銘柄コードと日付の組み合わせが既に存在します")
            raise DatabaseError(f"データベース制約違反: {str(e)}")
        except SQLAlchemyError as e:
            raise DatabaseError(f"データベースエラー: {str(e)}")

    @staticmethod
    def delete(session: Session, stock_id: int) -> bool:
        """株価データを削除.

        Args:
            session: データベースセッション
            stock_id: 削除対象の株価データID

        Returns:
            bool: 削除が成功した場合True、対象が見つからない場合False

        Raises:
            DatabaseError: データベースエラーが発生した場合
        """
        try:
            stock_data = (
                session.query(StockDaily)
                .filter(StockDaily.id == stock_id)
                .first()
            )
            if not stock_data:
                return False

            session.delete(stock_data)
            session.flush()
            return True
        except SQLAlchemyError as e:
            raise DatabaseError(f"データベースエラー: {str(e)}")

    @staticmethod
    def bulk_create(
        session: Session, stock_data_list: List[Dict[str, Any]]
    ) -> List[StockDaily]:
        """複数の株価データを一括作成.

        Args:
            session: データベースセッション
            stock_data_list: 作成する株価データのリスト

        Returns:
            List[StockDaily]: 作成された株価データのリスト

        Raises:
            StockDataError: 重複データが検出された場合
            DatabaseError: データベースエラーが発生した場合
        """
        try:
            stock_objects = []
            for data in stock_data_list:
                stock_data = StockDaily(**data)
                stock_objects.append(stock_data)

            session.add_all(stock_objects)
            session.flush()
            return stock_objects
        except IntegrityError as e:
            if "uk_stocks_daily_symbol_date" in str(e):
                raise StockDataError("一括作成中に重複データが検出されました")
            raise DatabaseError(f"データベース制約違反: {str(e)}")
        except SQLAlchemyError as e:
            raise DatabaseError(f"データベースエラー: {str(e)}")

    @staticmethod
    def count_by_symbol(session: Session, symbol: str) -> int:
        """銘柄のデータ件数を取得.

        Args:
            session: データベースセッション
            symbol: 銘柄コード

        Returns:
            int: 指定銘柄のデータ件数

        Raises:
            DatabaseError: データベースエラーが発生した場合
        """
        try:
            return (
                session.query(StockDaily)
                .filter(StockDaily.symbol == symbol)
                .count()
            )
        except SQLAlchemyError as e:
            raise DatabaseError(f"データベースエラー: {str(e)}")

    @staticmethod
    def get_latest_date_by_symbol(
        session: Session, symbol: str
    ) -> Optional[date]:
        """銘柄の最新データ日付を取得.

        Args:
            session: データベースセッション
            symbol: 銘柄コード

        Returns:
            Optional[date]: 最新データの日付(データがない場合はNone)

        Raises:
            DatabaseError: データベースエラーが発生した場合
        """
        try:
            result = (
                session.query(StockDaily.date)
                .filter(StockDaily.symbol == symbol)
                .order_by(StockDaily.date.desc())
                .first()
            )
            return result[0] if result else None
        except SQLAlchemyError as e:
            raise DatabaseError(f"データベースエラー: {str(e)}")

    @staticmethod
    def count_all(session: Session) -> int:
        """全ての株価データ件数を取得.

        Args:
            session: データベースセッション

        Returns:
            int: 全ての株価データの件数

        Raises:
            DatabaseError: データベースエラーが発生した場合
        """
        try:
            return session.query(StockDaily).count()
        except SQLAlchemyError as e:
            raise DatabaseError(f"データベースエラー: {str(e)}")

    @staticmethod
    def count_with_filters(
        session: Session,
        symbol: Optional[str] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
    ) -> int:
        """フィルタ条件に基づく株価データ件数を取得.

        Args:
            session: データベースセッション
            symbol: 銘柄コード(指定時のみフィルタ)
            start_date: 開始日付(この日付以降)
            end_date: 終了日付(この日付以前)

        Returns:
            int: フィルタ条件に一致するデータの件数

        Raises:
            DatabaseError: データベースエラーが発生した場合
        """
        try:
            query = session.query(StockDaily)

            if symbol:
                query = query.filter(StockDaily.symbol == symbol)
            if start_date:
                query = query.filter(StockDaily.date >= start_date)
            if end_date:
                query = query.filter(StockDaily.date <= end_date)

            return query.count()
        except SQLAlchemyError as e:
            raise DatabaseError(f"データベースエラー: {str(e)}")


__all__ = ["StockDailyCRUD"]
