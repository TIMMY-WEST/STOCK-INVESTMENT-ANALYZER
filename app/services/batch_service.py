"""バッチ管理サービス (Phase 2).

Phase 1のインメモリ管理からPhase 2のデータベース永続化への移行。
バッチ実行情報をデータベースに保存し、永続的に管理します。

参照仕様書: docs/api_bulk_fetch.md (Phase 2)。
"""

from datetime import datetime
import logging
from typing import Any, Dict, List, Optional

from sqlalchemy.orm import Session

from models import BatchExecution, BatchExecutionDetail, get_db_session


logger = logging.getLogger(__name__)


class BatchServiceError(Exception):
    """バッチサービスエラー."""

    pass


class BatchService:
    """バッチ実行情報を管理するサービスクラス（Phase 2: データベース永続化対応）."""

    @staticmethod
    def create_batch(
        batch_type: str, total_stocks: int, session: Optional[Session] = None
    ) -> Dict[str, Any]:
        """
        新しいバッチ実行レコードを作成.

        Args:
            batch_type: バッチタイプ ('all_stocks', 'partial', etc.)
            total_stocks: 総銘柄数
            session: SQLAlchemyセッション（省略時は自動生成）

        Returns:
            作成されたバッチ情報の辞書

        Raises:
            BatchServiceError: バッチ作成エラー。
        """
        try:
            if session:
                # セッションが提供されている場合はそれを使用
                batch = BatchExecution(
                    batch_type=batch_type,
                    status="running",
                    total_stocks=total_stocks,
                    processed_stocks=0,
                    successful_stocks=0,
                    failed_stocks=0,
                )
                session.add(batch)
                session.flush()
                return batch.to_dict()
            else:
                # セッションが提供されていない場合は新規作成
                with get_db_session() as db_session:
                    batch = BatchExecution(
                        batch_type=batch_type,
                        status="running",
                        total_stocks=total_stocks,
                        processed_stocks=0,
                        successful_stocks=0,
                        failed_stocks=0,
                    )
                    db_session.add(batch)
                    db_session.flush()
                    batch_dict = batch.to_dict()

                return batch_dict

        except Exception as e:
            logger.error(f"バッチ作成エラー: {e}")
            raise BatchServiceError(f"バッチ作成に失敗しました: {e}") from e

    @staticmethod
    def get_batch(
        batch_id: int, session: Optional[Session] = None
    ) -> Optional[Dict[str, Any]]:
        """
        バッチ実行情報を取得.

        Args:
            batch_id: バッチID
            session: SQLAlchemyセッション（省略時は自動生成）

        Returns:
            バッチ情報の辞書、見つからない場合はNone

        Raises:
            BatchServiceError: バッチ取得エラー。
        """
        try:
            if session:
                batch = (
                    session.query(BatchExecution)
                    .filter(BatchExecution.id == batch_id)
                    .first()
                )
                return batch.to_dict() if batch else None
            else:
                with get_db_session() as db_session:
                    batch = (
                        db_session.query(BatchExecution)
                        .filter(BatchExecution.id == batch_id)
                        .first()
                    )
                    return batch.to_dict() if batch else None

        except Exception as e:
            logger.error(f"バッチ取得エラー (batch_id={batch_id}): {e}")
            raise BatchServiceError(
                f"バッチ情報の取得に失敗しました: {e}"
            ) from e

    @staticmethod
    def update_batch_progress(
        batch_id: int,
        processed_stocks: int,
        successful_stocks: int,
        failed_stocks: int,
        session: Optional[Session] = None,
    ) -> Optional[Dict[str, Any]]:
        """
        バッチの進捗を更新.

        Args:
            batch_id: バッチID
            processed_stocks: 処理済み銘柄数
            successful_stocks: 成功銘柄数
            failed_stocks: 失敗銘柄数
            session: SQLAlchemyセッション（省略時は自動生成）

        Returns:
            更新されたバッチ情報の辞書、見つからない場合はNone

        Raises:
            BatchServiceError: 進捗更新エラー。
        """
        try:
            if session:
                batch = (
                    session.query(BatchExecution)
                    .filter(BatchExecution.id == batch_id)
                    .first()
                )
                if not batch:
                    return None

                batch.processed_stocks = processed_stocks
                batch.successful_stocks = successful_stocks
                batch.failed_stocks = failed_stocks
                session.flush()
                return batch.to_dict()
            else:
                with get_db_session() as db_session:
                    batch = (
                        db_session.query(BatchExecution)
                        .filter(BatchExecution.id == batch_id)
                        .first()
                    )
                    if not batch:
                        return None

                    batch.processed_stocks = processed_stocks
                    batch.successful_stocks = successful_stocks
                    batch.failed_stocks = failed_stocks
                    db_session.flush()
                    batch_dict = batch.to_dict()

                return batch_dict

        except Exception as e:
            logger.error(f"バッチ進捗更新エラー (batch_id={batch_id}): {e}")
            raise BatchServiceError(
                f"バッチ進捗の更新に失敗しました: {e}"
            ) from e

    @staticmethod
    def complete_batch(
        batch_id: int,
        status: str = "completed",
        error_message: Optional[str] = None,
        session: Optional[Session] = None,
    ) -> Optional[Dict[str, Any]]:
        """
        バッチを完了状態にする.

        Args:
            batch_id: バッチID
            status: 完了ステータス ('completed', 'failed', 'paused')
            error_message: エラーメッセージ（失敗時）
            session: SQLAlchemyセッション（省略時は自動生成）

        Returns:
            更新されたバッチ情報の辞書、見つからない場合はNone

        Raises:
            BatchServiceError: バッチ完了エラー。
        """
        try:
            if session:
                batch = (
                    session.query(BatchExecution)
                    .filter(BatchExecution.id == batch_id)
                    .first()
                )
                if not batch:
                    return None

                batch.status = status
                batch.end_time = datetime.now()
                if error_message:
                    batch.error_message = error_message
                session.flush()
                return batch.to_dict()
            else:
                with get_db_session() as db_session:
                    batch = (
                        db_session.query(BatchExecution)
                        .filter(BatchExecution.id == batch_id)
                        .first()
                    )
                    if not batch:
                        return None

                    batch.status = status
                    batch.end_time = datetime.now()
                    if error_message:
                        batch.error_message = error_message
                    db_session.flush()
                    batch_dict = batch.to_dict()

                return batch_dict

        except Exception as e:
            logger.error(f"バッチ完了エラー (batch_id={batch_id}): {e}")
            raise BatchServiceError(
                f"バッチの完了処理に失敗しました: {e}"
            ) from e

    @staticmethod
    def list_batches(
        limit: int = 100,
        offset: int = 0,
        status: Optional[str] = None,
        session: Optional[Session] = None,
    ) -> List[Dict[str, Any]]:
        """
        バッチ実行情報一覧を取得.

        Args:
            limit: 取得件数上限
            offset: オフセット
            status: ステータスでフィルタ（省略時は全て）
            session: SQLAlchemyセッション（省略時は自動生成）

        Returns:
            バッチ情報の辞書のリスト

        Raises:
            BatchServiceError: バッチ一覧取得エラー。
        """
        try:
            if session:
                query = session.query(BatchExecution)
                if status:
                    query = query.filter(BatchExecution.status == status)
                query = query.order_by(BatchExecution.start_time.desc())
                query = query.offset(offset).limit(limit)
                batches = query.all()
                return [batch.to_dict() for batch in batches]
            else:
                with get_db_session() as db_session:
                    query = db_session.query(BatchExecution)
                    if status:
                        query = query.filter(BatchExecution.status == status)
                    query = query.order_by(BatchExecution.start_time.desc())
                    query = query.offset(offset).limit(limit)
                    batches = query.all()
                    return [batch.to_dict() for batch in batches]

        except Exception as e:
            logger.error(f"バッチ一覧取得エラー: {e}")
            raise BatchServiceError(
                f"バッチ一覧の取得に失敗しました: {e}"
            ) from e

    @staticmethod
    def create_batch_detail(
        batch_execution_id: int,
        stock_code: str,
        status: str = "pending",
        session: Optional[Session] = None,
    ) -> Dict[str, Any]:
        """
        バッチ実行詳細レコードを作成.

        Args:
            batch_execution_id: バッチ実行ID
            stock_code: 銘柄コード
            status: ステータス ('pending', 'processing', 'completed', 'failed')
            session: SQLAlchemyセッション（省略時は自動生成）

        Returns:
            作成されたバッチ詳細情報の辞書

        Raises:
            BatchServiceError: バッチ詳細作成エラー。
        """
        try:
            if session:
                detail = BatchExecutionDetail(
                    batch_execution_id=batch_execution_id,
                    stock_code=stock_code,
                    status=status,
                )
                session.add(detail)
                session.flush()
                return detail.to_dict()
            else:
                with get_db_session() as db_session:
                    detail = BatchExecutionDetail(
                        batch_execution_id=batch_execution_id,
                        stock_code=stock_code,
                        status=status,
                    )
                    db_session.add(detail)
                    db_session.flush()
                    detail_dict = detail.to_dict()

                return detail_dict

        except Exception as e:
            logger.error(
                f"バッチ詳細作成エラー (batch_id={batch_execution_id}, stock_code={stock_code}): {e}"
            )
            raise BatchServiceError(
                f"バッチ詳細の作成に失敗しました: {e}"
            ) from e

    @staticmethod
    def update_batch_detail(
        detail_id: int,
        status: str,
        records_inserted: int = 0,
        error_message: Optional[str] = None,
        session: Optional[Session] = None,
    ) -> Optional[Dict[str, Any]]:
        """
        バッチ実行詳細を更新.

        Args:
            detail_id: バッチ詳細ID
            status: ステータス
            records_inserted: 挿入されたレコード数
            error_message: エラーメッセージ（失敗時）
            session: SQLAlchemyセッション（省略時は自動生成）

        Returns:
            更新されたバッチ詳細情報の辞書、見つからない場合はNone

        Raises:
            BatchServiceError: バッチ詳細更新エラー。
        """
        try:
            if session:
                detail = (
                    session.query(BatchExecutionDetail)
                    .filter(BatchExecutionDetail.id == detail_id)
                    .first()
                )
                if not detail:
                    return None

                detail.status = status
                detail.records_inserted = records_inserted
                detail.end_time = datetime.now()
                if error_message:
                    detail.error_message = error_message
                session.flush()
                return detail.to_dict()
            else:
                with get_db_session() as db_session:
                    detail = (
                        db_session.query(BatchExecutionDetail)
                        .filter(BatchExecutionDetail.id == detail_id)
                        .first()
                    )
                    if not detail:
                        return None

                    detail.status = status
                    detail.records_inserted = records_inserted
                    detail.end_time = datetime.now()
                    if error_message:
                        detail.error_message = error_message
                    db_session.flush()
                    detail_dict = detail.to_dict()

                return detail_dict

        except Exception as e:
            logger.error(f"バッチ詳細更新エラー (detail_id={detail_id}): {e}")
            raise BatchServiceError(
                f"バッチ詳細の更新に失敗しました: {e}"
            ) from e

    @staticmethod
    def get_batch_details(
        batch_execution_id: int, session: Optional[Session] = None
    ) -> List[Dict[str, Any]]:
        """
        バッチ実行詳細一覧を取得.

        Args:
            batch_execution_id: バッチ実行ID
            session: SQLAlchemyセッション（省略時は自動生成）

        Returns:
            バッチ詳細情報の辞書のリスト

        Raises:
            BatchServiceError: バッチ詳細一覧取得エラー。
        """
        try:
            if session:
                details = (
                    session.query(BatchExecutionDetail)
                    .filter(
                        BatchExecutionDetail.batch_execution_id
                        == batch_execution_id
                    )
                    .all()
                )
                return [detail.to_dict() for detail in details]
            else:
                with get_db_session() as db_session:
                    details = (
                        db_session.query(BatchExecutionDetail)
                        .filter(
                            BatchExecutionDetail.batch_execution_id
                            == batch_execution_id
                        )
                        .all()
                    )
                    return [detail.to_dict() for detail in details]

        except Exception as e:
            logger.error(
                f"バッチ詳細一覧取得エラー (batch_id={batch_execution_id}): {e}"
            )
            raise BatchServiceError(
                f"バッチ詳細一覧の取得に失敗しました: {e}"
            ) from e
