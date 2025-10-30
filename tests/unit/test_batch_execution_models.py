"""バッチ実行関連モデルのテストコード.

Issue #80: バッチ実行情報テーブルの実装。
"""

from datetime import datetime, timezone
import os

# 既存のテストファイルと同じインポート方法を使用
import sys

import pytest
from sqlalchemy import create_engine
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import sessionmaker


sys.path.append(os.path.join(os.path.dirname(__file__), "..", "app"))

from app.models import Base, BatchExecution, BatchExecutionDetail  # noqa: E402


class TestBatchExecutionModel:
    """BatchExecutionモデルのテストクラス."""

    @pytest.fixture
    def sample_batch_execution(self):
        """テスト用のBatchExecutionインスタンスを作成."""
        return BatchExecution(
            batch_type="all_stocks",
            status="running",
            total_stocks=100,
            processed_stocks=50,
            successful_stocks=45,
            failed_stocks=5,
        )

    def test_batch_execution_model_creation_with_valid_data_returns_instance(
        self, sample_batch_execution
    ):
        """BatchExecutionインスタンスの作成テスト."""
        assert sample_batch_execution.batch_type == "all_stocks"
        assert sample_batch_execution.status == "running"
        assert sample_batch_execution.total_stocks == 100
        assert sample_batch_execution.processed_stocks == 50
        assert sample_batch_execution.successful_stocks == 45
        assert sample_batch_execution.failed_stocks == 5

    def test_batch_execution_model_repr_with_valid_instance_returns_string_representation(
        self, sample_batch_execution
    ):
        """BatchExecutionの__repr__メソッドテスト."""
        expected = "<BatchExecution(id=None, batch_type='all_stocks', status='running')>"
        assert repr(sample_batch_execution) == expected

    def test_batch_execution_model_to_dict_with_valid_instance_returns_dictionary(
        self, sample_batch_execution
    ):
        """BatchExecutionのto_dictメソッドテスト."""
        result = sample_batch_execution.to_dict()

        assert result["batch_type"] == "all_stocks"
        assert result["status"] == "running"
        assert result["total_stocks"] == 100
        assert result["processed_stocks"] == 50
        assert result["successful_stocks"] == 45
        assert result["failed_stocks"] == 5
        assert result["id"] is None  # まだDBに保存されていない
        assert result["start_time"] is None  # server_defaultなのでインスタンス作成時はNone
        assert result["end_time"] is None
        assert result["error_message"] is None
        assert result["created_at"] is None

    def test_batch_execution_model_progress_percentage_with_valid_data_returns_correct_percentage(
        self,
    ):
        """進捗率計算のテスト."""
        # 正常ケース
        batch = BatchExecution(
            batch_type="test",
            status="running",
            total_stocks=100,
            processed_stocks=25,
        )
        assert batch.progress_percentage == 25.0

        # 0除算回避テスト
        batch_zero = BatchExecution(
            batch_type="test",
            status="running",
            total_stocks=0,
            processed_stocks=0,
        )
        assert batch_zero.progress_percentage == 0.0

        # 100%完了テスト
        batch_complete = BatchExecution(
            batch_type="test",
            status="completed",
            total_stocks=50,
            processed_stocks=50,
        )
        assert batch_complete.progress_percentage == 100.0

    def test_batch_execution_model_duration_seconds_with_valid_timestamps_returns_correct_duration(
        self,
    ):
        """実行時間計算のテスト."""
        now = datetime.now(timezone.utc)

        # start_timeがNoneの場合
        batch = BatchExecution(
            batch_type="test", status="running", total_stocks=100
        )
        assert batch.duration_seconds is None

        # start_timeのみ設定（実行中）
        batch.start_time = now
        duration = batch.duration_seconds
        assert duration is not None
        assert duration >= 0

        # start_timeとend_timeの両方設定（完了）
        batch.end_time = now
        assert batch.duration_seconds == 0.0


class TestBatchExecutionDetailModel:
    """BatchExecutionDetailモデルのテストクラス."""

    @pytest.fixture
    def sample_batch_execution_detail(self):
        """テスト用のBatchExecutionDetailインスタンスを作成."""
        return BatchExecutionDetail(
            batch_execution_id=1,
            stock_code="7203",
            status="completed",
            records_inserted=100,
        )

    def test_batch_execution_detail_model_creation_with_valid_data_returns_instance(
        self, sample_batch_execution_detail
    ):
        """BatchExecutionDetailインスタンスの作成テスト."""
        assert sample_batch_execution_detail.batch_execution_id == 1
        assert sample_batch_execution_detail.stock_code == "7203"
        assert sample_batch_execution_detail.status == "completed"
        assert sample_batch_execution_detail.records_inserted == 100

    def test_batch_execution_detail_model_repr_with_valid_instance_returns_string_representation(
        self, sample_batch_execution_detail
    ):
        """BatchExecutionDetailの__repr__メソッドテスト."""
        expected = "<BatchExecutionDetail(id=None, batch_execution_id=1, stock_code='7203', status='completed')>"
        assert repr(sample_batch_execution_detail) == expected

    def test_batch_execution_detail_model_to_dict_with_valid_instance_returns_dictionary(
        self, sample_batch_execution_detail
    ):
        """BatchExecutionDetailのto_dictメソッドテスト."""
        result = sample_batch_execution_detail.to_dict()

        assert result["batch_execution_id"] == 1
        assert result["stock_code"] == "7203"
        assert result["status"] == "completed"
        assert result["records_inserted"] == 100
        assert result["id"] is None
        assert result["start_time"] is None
        assert result["end_time"] is None
        assert result["error_message"] is None
        assert result["created_at"] is None

    def test_batch_execution_detail_model_duration_seconds_with_valid_timestamps_returns_correct_duration(
        self,
    ):
        """処理時間計算のテスト."""
        now = datetime.now(timezone.utc)

        # start_timeがNoneの場合
        detail = BatchExecutionDetail(
            batch_execution_id=1, stock_code="7203", status="pending"
        )
        assert detail.duration_seconds is None

        # start_timeのみ設定（処理中）
        detail.start_time = now
        duration = detail.duration_seconds
        assert duration is not None
        assert duration >= 0

        # start_timeとend_timeの両方設定（完了）
        detail.end_time = now
        assert detail.duration_seconds == 0.0


class TestBatchExecutionModelValidation:
    """BatchExecutionモデルのバリデーションテスト."""

    def test_batch_execution_model_validation_with_missing_required_fields_returns_none_values(
        self,
    ):
        """必須フィールドのテスト."""
        # SQLAlchemyモデルでは、インスタンス作成時にTypeErrorは発生しない
        # 代わりに、必須フィールドが設定されていることを確認
        batch = BatchExecution()
        assert batch.batch_type is None  # 必須フィールドが未設定
        assert batch.status is None
        assert batch.total_stocks is None

        # 最小限の必須フィールドでの作成
        batch = BatchExecution(
            batch_type="test", status="running", total_stocks=10
        )
        assert batch.batch_type == "test"
        assert batch.status == "running"
        assert batch.total_stocks == 10

    def test_batch_execution_model_validation_with_valid_data_returns_default_values(
        self,
    ):
        """デフォルト値のテスト."""
        batch = BatchExecution(
            batch_type="test", status="running", total_stocks=100
        )

        # SQLAlchemyのdefaultは、DBに保存時に適用される
        # インスタンス作成時はNoneになる
        assert batch.processed_stocks is None or batch.processed_stocks == 0
        assert batch.successful_stocks is None or batch.successful_stocks == 0
        assert batch.failed_stocks is None or batch.failed_stocks == 0
        assert batch.error_message is None
        assert batch.end_time is None


class TestBatchExecutionDetailModelValidation:
    """BatchExecutionDetailモデルのバリデーションテスト."""

    def test_batch_execution_detail_model_validation_with_missing_required_fields_returns_none_values(
        self,
    ):
        """必須フィールドのテスト."""
        # SQLAlchemyモデルでは、インスタンス作成時にTypeErrorは発生しない
        # 代わりに、必須フィールドが設定されていることを確認
        detail = BatchExecutionDetail()
        assert detail.batch_execution_id is None  # 必須フィールドが未設定
        assert detail.stock_code is None
        assert detail.status is None

        # 最小限の必須フィールドでの作成
        detail = BatchExecutionDetail(
            batch_execution_id=1, stock_code="7203", status="pending"
        )
        assert detail.batch_execution_id == 1
        assert detail.stock_code == "7203"
        assert detail.status == "pending"

    def test_batch_execution_detail_model_validation_with_valid_data_returns_default_values(
        self,
    ):
        """デフォルト値のテスト."""
        detail = BatchExecutionDetail(
            batch_execution_id=1, stock_code="7203", status="pending"
        )

        # SQLAlchemyのdefaultは、DBに保存時に適用される
        # インスタンス作成時はNoneになる
        assert detail.records_inserted is None or detail.records_inserted == 0
        assert detail.start_time is None
        assert detail.end_time is None
        assert detail.error_message is None


class TestBatchExecutionModelIntegration:
    """BatchExecutionモデルの統合テスト（実際のDBを使用）."""

    @pytest.fixture
    def db_session(self):
        """テスト用のデータベースセッション."""
        # インメモリSQLiteを使用
        engine = create_engine("sqlite:///:memory:", echo=False)
        Base.metadata.create_all(engine)

        Session = sessionmaker(bind=engine)
        session = Session()

        yield session

        session.close()

    def test_batch_execution_model_crud_operations_with_valid_data_returns_success(
        self, db_session
    ):
        """BatchExecutionのCRUD操作テスト."""
        # Create
        batch = BatchExecution(
            batch_type="all_stocks", status="running", total_stocks=100
        )
        db_session.add(batch)
        db_session.commit()

        assert batch.id is not None
        assert batch.created_at is not None
        assert batch.start_time is not None

        # Read
        retrieved_batch = (
            db_session.query(BatchExecution).filter_by(id=batch.id).first()
        )
        assert retrieved_batch is not None
        assert retrieved_batch.batch_type == "all_stocks"
        assert retrieved_batch.status == "running"

        # Update
        retrieved_batch.status = "completed"
        retrieved_batch.processed_stocks = 100
        db_session.commit()

        updated_batch = (
            db_session.query(BatchExecution).filter_by(id=batch.id).first()
        )
        assert updated_batch.status == "completed"
        assert updated_batch.processed_stocks == 100

        # Delete
        db_session.delete(updated_batch)
        db_session.commit()

        deleted_batch = (
            db_session.query(BatchExecution).filter_by(id=batch.id).first()
        )
        assert deleted_batch is None

    def test_batch_execution_detail_model_crud_operations_with_valid_data_returns_success(
        self, db_session
    ):
        """BatchExecutionDetailのCRUD操作テスト."""
        # 親レコード作成
        batch = BatchExecution(
            batch_type="test", status="running", total_stocks=1
        )
        db_session.add(batch)
        db_session.commit()

        # Create
        detail = BatchExecutionDetail(
            batch_execution_id=batch.id, stock_code="7203", status="pending"
        )
        db_session.add(detail)
        db_session.commit()

        assert detail.id is not None
        assert detail.created_at is not None

        # Read
        retrieved_detail = (
            db_session.query(BatchExecutionDetail)
            .filter_by(id=detail.id)
            .first()
        )
        assert retrieved_detail is not None
        assert retrieved_detail.stock_code == "7203"
        assert retrieved_detail.status == "pending"

        # Update
        retrieved_detail.status = "completed"
        retrieved_detail.records_inserted = 50
        db_session.commit()

        updated_detail = (
            db_session.query(BatchExecutionDetail)
            .filter_by(id=detail.id)
            .first()
        )
        assert updated_detail.status == "completed"
        assert updated_detail.records_inserted == 50

        # Delete
        db_session.delete(updated_detail)
        db_session.commit()

        deleted_detail = (
            db_session.query(BatchExecutionDetail)
            .filter_by(id=detail.id)
            .first()
        )
        assert deleted_detail is None

    def test_batch_execution_model_foreign_key_relationship_with_valid_data_returns_correct_associations(
        self, db_session
    ):
        """外部キー関係のテスト（SQLiteでは制約チェックが無効なので、論理的なテストのみ）."""
        # 親レコード作成
        batch = BatchExecution(
            batch_type="test", status="running", total_stocks=2
        )
        db_session.add(batch)
        db_session.commit()

        # 子レコード作成
        detail1 = BatchExecutionDetail(
            batch_execution_id=batch.id, stock_code="7203", status="pending"
        )
        detail2 = BatchExecutionDetail(
            batch_execution_id=batch.id, stock_code="6758", status="pending"
        )

        db_session.add_all([detail1, detail2])
        db_session.commit()

        # 関連レコードの確認
        details = (
            db_session.query(BatchExecutionDetail)
            .filter_by(batch_execution_id=batch.id)
            .all()
        )
        assert len(details) == 2
        assert {detail.stock_code for detail in details} == {"7203", "6758"}
