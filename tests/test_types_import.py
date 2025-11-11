"""Import tests for app.types to ensure module can be imported and symbols exist."""

from app import types


def test_interval_literal_exists() -> None:
    # Interval は typing.Literal なので存在することを確認する
    assert hasattr(types, "Interval")


def test_processstatus_members() -> None:
    # ProcessStatus の代表的メンバーを個別に検証する
    assert types.ProcessStatus.PENDING.value == "pending"
    assert types.ProcessStatus.RUNNING.value == "running"
    assert types.ProcessStatus.SUCCESS.value == "success"
    assert types.ProcessStatus.FAILED.value == "failed"


def test_batchstatus_members() -> None:
    # BatchStatus の代表的メンバーを個別に検証する
    assert types.BatchStatus.QUEUED.value == "queued"
    assert types.BatchStatus.PROCESSING.value == "processing"
    assert types.BatchStatus.COMPLETED.value == "completed"
    assert types.BatchStatus.FAILED.value == "failed"


def test_pagination_typedict_keys() -> None:
    # TypedDictは実行時に型情報が失われるが、クラス名は存在する
    assert hasattr(types, "PaginationParams")
