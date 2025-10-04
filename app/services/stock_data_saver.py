"""株価データ保存サービス

各時間軸の株価データをデータベースに保存します。
"""

from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
import logging
from datetime import datetime, date

from app.models import get_db_session, StockDataBase
from app.utils.timeframe_utils import (
    get_model_for_interval,
    validate_interval,
    get_display_name,
    is_intraday_interval
)

logger = logging.getLogger(__name__)


class StockDataSaveError(Exception):
    """データ保存エラー"""
    pass


class StockDataSaver:
    """株価データ保存クラス"""

    def __init__(self):
        """初期化"""
        self.logger = logger

    def save_stock_data(
        self,
        symbol: str,
        interval: str,
        data_list: List[Dict[str, Any]],
        session: Optional[Session] = None
    ) -> Dict[str, Any]:
        """
        株価データを保存

        Args:
            symbol: 銘柄コード
            interval: 時間軸
            data_list: 保存するデータのリスト
            session: SQLAlchemyセッション（Noneの場合は新規作成）

        Returns:
            保存結果の統計情報

        Raises:
            StockDataSaveError: データ保存失敗時
        """
        # 時間軸の検証
        if not validate_interval(interval):
            raise ValueError(f"サポートされていない時間軸: {interval}")

        # モデルクラスの取得
        model_class = get_model_for_interval(interval)

        # セッション管理
        if session:
            return self._save_with_session(
                session, symbol, interval, model_class, data_list
            )
        else:
            with get_db_session() as session:
                return self._save_with_session(
                    session, symbol, interval, model_class, data_list
                )

    def _save_with_session(
        self,
        session: Session,
        symbol: str,
        interval: str,
        model_class: type,
        data_list: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        セッションを使用してデータを保存（内部メソッド）

        Args:
            session: SQLAlchemyセッション
            symbol: 銘柄コード
            interval: 時間軸
            model_class: データベースモデルクラス
            data_list: 保存するデータのリスト

        Returns:
            保存結果の統計情報
        """
        saved_count = 0
        skipped_count = 0
        error_count = 0

        self.logger.info(
            f"データ保存開始: {symbol} (時間軸: {get_display_name(interval)}, "
            f"件数: {len(data_list)})"
        )

        for data in data_list:
            try:
                # データに銘柄コードを追加
                data_with_symbol = {**data, 'symbol': symbol}

                # レコードを作成
                record = model_class(**data_with_symbol)
                session.add(record)
                session.flush()

                saved_count += 1

            except IntegrityError as e:
                # ユニーク制約違反（重複データ）
                session.rollback()
                skipped_count += 1
                self.logger.debug(
                    f"重複データをスキップ: {symbol} "
                    f"({data.get('date') or data.get('datetime')})"
                )

            except SQLAlchemyError as e:
                session.rollback()
                error_count += 1
                self.logger.error(
                    f"データ保存エラー: {symbol} "
                    f"({data.get('date') or data.get('datetime')}): {e}"
                )

        # コミット
        try:
            session.commit()
        except SQLAlchemyError as e:
            session.rollback()
            raise StockDataSaveError(
                f"データ保存のコミットに失敗: {symbol} "
                f"(時間軸: {get_display_name(interval)}): {e}"
            )

        result = {
            'symbol': symbol,
            'interval': interval,
            'total': len(data_list),
            'saved': saved_count,
            'skipped': skipped_count,
            'errors': error_count
        }

        self.logger.info(
            f"データ保存完了: {symbol} (時間軸: {get_display_name(interval)}) - "
            f"保存: {saved_count}, スキップ: {skipped_count}, エラー: {error_count}"
        )

        return result

    def save_multiple_timeframes(
        self,
        symbol: str,
        data_dict: Dict[str, List[Dict[str, Any]]]
    ) -> Dict[str, Dict[str, Any]]:
        """
        複数時間軸のデータを一度に保存

        Args:
            symbol: 銘柄コード
            data_dict: {interval: data_list} の辞書

        Returns:
            {interval: 保存結果} の辞書

        Raises:
            StockDataSaveError: データ保存失敗時
        """
        results = {}

        with get_db_session() as session:
            for interval, data_list in data_dict.items():
                try:
                    result = self.save_stock_data(
                        symbol=symbol,
                        interval=interval,
                        data_list=data_list,
                        session=session
                    )
                    results[interval] = result

                except Exception as e:
                    self.logger.error(
                        f"時間軸 {interval} のデータ保存エラー: {e}"
                    )
                    results[interval] = {
                        'symbol': symbol,
                        'interval': interval,
                        'error': str(e)
                    }

        return results

    def get_latest_date(
        self,
        symbol: str,
        interval: str,
        session: Optional[Session] = None
    ) -> Optional[datetime | date]:
        """
        データベース内の最新データ日時を取得

        Args:
            symbol: 銘柄コード
            interval: 時間軸
            session: SQLAlchemyセッション（Noneの場合は新規作成）

        Returns:
            最新データの日時、データがない場合はNone
        """
        # 時間軸の検証
        if not validate_interval(interval):
            raise ValueError(f"サポートされていない時間軸: {interval}")

        # モデルクラスの取得
        model_class = get_model_for_interval(interval)
        is_intraday = is_intraday_interval(interval)

        # 最新日時の取得
        def _get_latest(sess: Session):
            if is_intraday:
                # 分足・時間足: datetime
                result = sess.query(model_class.datetime).filter(
                    model_class.symbol == symbol
                ).order_by(model_class.datetime.desc()).first()
            else:
                # 日足・週足・月足: date
                result = sess.query(model_class.date).filter(
                    model_class.symbol == symbol
                ).order_by(model_class.date.desc()).first()

            return result[0] if result else None

        if session:
            return _get_latest(session)
        else:
            with get_db_session() as session:
                return _get_latest(session)

    def count_records(
        self,
        symbol: str,
        interval: str,
        session: Optional[Session] = None
    ) -> int:
        """
        データベース内のレコード数を取得

        Args:
            symbol: 銘柄コード
            interval: 時間軸
            session: SQLAlchemyセッション（Noneの場合は新規作成）

        Returns:
            レコード数
        """
        # 時間軸の検証
        if not validate_interval(interval):
            raise ValueError(f"サポートされていない時間軸: {interval}")

        # モデルクラスの取得
        model_class = get_model_for_interval(interval)

        # レコード数の取得
        def _count(sess: Session):
            return sess.query(model_class).filter(
                model_class.symbol == symbol
            ).count()

        if session:
            return _count(session)
        else:
            with get_db_session() as session:
                return _count(session)
