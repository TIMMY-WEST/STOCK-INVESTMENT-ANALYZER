"""Tests for BatchService using an in-memory SQLite database.

These tests exercise create/get/update/complete/list and detail methods
of `BatchService` without touching the production DB by using a
temporary in-memory SQLAlchemy engine and session.

日本語のdocstring（テスト内コメントは日本語）
"""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.models import Base, BatchExecution, BatchExecutionDetail
from app.services.batch.batch_service import BatchService, BatchServiceError


# このテストはDB（インメモリSQLite）を使用するため統合テスト扱いとする
pytestmark = pytest.mark.integration


@pytest.fixture
def in_memory_session():
    """インメモリSQLiteセッションを作成して返す."""
    engine = create_engine("sqlite:///:memory:")
    # テーブルを作成
    Base.metadata.create_all(bind=engine)
    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


def test_create_and_get_batch(in_memory_session):
    """BatchServiceの作成と取得が正しく動作することを検証する.

    Arrange: インメモリセッションを準備
    Act: バッチを作成して取得する
    Assert: 作成したバッチと取得結果の主要フィールドが一致する
    """
    # Arrange
    session = in_memory_session

    # Act: create
    res = BatchService.create_batch(
        batch_type="all_stocks", total_stocks=10, session=session
    )

    # Assert: basic fields
    assert res is not None
    assert res["batch_type"] == "all_stocks"
    assert res["status"] == "running"
    assert res["total_stocks"] == 10

    batch_id = res["id"]

    # Act: get
    got = BatchService.get_batch(batch_id=batch_id, session=session)

    # Assert: fetched equals created (at least key fields)
    assert got is not None
    assert got["id"] == batch_id
    assert got["total_stocks"] == 10


def test_update_progress_and_complete(in_memory_session):
    """バッチの進捗更新と完了処理が期待通りに動作することを検証する.

    Arrange: バッチを作成
    Act: 進捗を更新してバッチを完了させる
    Assert: 更新された進捗と完了ステータスが反映される
    """
    session = in_memory_session

    # create a batch first
    created = BatchService.create_batch(
        batch_type="partial", total_stocks=5, session=session
    )
    batch_id = created["id"]

    # update progress
    updated = BatchService.update_batch_progress(
        batch_id=batch_id,
        processed_stocks=3,
        successful_stocks=2,
        failed_stocks=1,
        session=session,
    )

    assert updated is not None
    assert updated["processed_stocks"] == 3
    assert updated["successful_stocks"] == 2
    assert updated["failed_stocks"] == 1

    # complete the batch
    completed = BatchService.complete_batch(
        batch_id=batch_id, status="completed", session=session
    )
    assert completed is not None
    assert completed["status"] == "completed"
    assert completed["end_time"] is not None


def test_list_and_details(in_memory_session):
    """バッチの一覧取得、ステータスフィルタ、詳細（detail）の作成・更新・取得を検証する.

    Arrange: 複数のバッチを作成
    Act: 一覧取得・フィルタリング・detail作成・更新・取得を行う
    Assert: 期待する結果が返ること
    """
    session = in_memory_session

    # create multiple batches with different statuses
    b1 = BatchService.create_batch(
        batch_type="a", total_stocks=1, session=session
    )
    b2 = BatchService.create_batch(
        batch_type="b", total_stocks=2, session=session
    )
    BatchService.complete_batch(
        batch_id=b2["id"],
        status="failed",
        error_message="err",
        session=session,
    )

    # list all
    all_batches = BatchService.list_batches(
        limit=10, offset=0, session=session
    )
    assert isinstance(all_batches, list)
    assert len(all_batches) >= 2

    # list by status filter
    failed_batches = BatchService.list_batches(
        limit=10, offset=0, status="failed", session=session
    )
    assert all(isinstance(b, dict) for b in failed_batches)
    assert any(b.get("status") == "failed" for b in failed_batches)

    # create batch detail
    detail = BatchService.create_batch_detail(
        batch_execution_id=b1["id"],
        stock_code="7203",
        status="pending",
        session=session,
    )
    assert detail is not None
    assert detail["stock_code"] == "7203"

    # update detail
    updated_detail = BatchService.update_batch_detail(
        detail_id=detail["id"],
        status="completed",
        records_inserted=10,
        session=session,
    )
    assert updated_detail is not None
    assert updated_detail["status"] == "completed"
    assert updated_detail["records_inserted"] == 10

    # get batch details
    details = BatchService.get_batch_details(
        batch_execution_id=b1["id"], session=session
    )
    assert isinstance(details, list)
    assert any(d["stock_code"] == "7203" for d in details)


def test_get_nonexistent_returns_none(in_memory_session):
    """存在しないバッチIDで取得した場合にNoneが返ることを検証する."""
    session = in_memory_session
    assert BatchService.get_batch(batch_id=9999, session=session) is None
