"""Import tests for app.types to ensure module can be imported and symbols exist."""

from app import types


def test_interval_literal_exists() -> None:
    # Interval は typing.Literal なので存在することを確認する
    assert hasattr(types, "Interval")


def test_enums_have_expected_members() -> None:
    # ProcessStatus と BatchStatus に代表的メンバーがあることを確認する
    assert types.ProcessStatus.PENDING.value == "pending"
    assert types.ProcessStatus.RUNNING.value == "running"
    assert types.BatchStatus.QUEUED.value == "queued"


def test_pagination_typedict_keys() -> None:
    # TypedDictは実行時に型情報が失われるが、クラス名は存在する
    assert hasattr(types, "PaginationParams")
