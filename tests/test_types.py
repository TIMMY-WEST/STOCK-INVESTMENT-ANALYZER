"""tests for app.types module.

基本的な import と列挙値の検証を行う。
"""

from app import types


def test_process_status_enum_values():
    # Enum メンバーが期待通りの値を持っていることを確認する。
    assert types.ProcessStatus.PENDING.value == "pending"
    assert types.ProcessStatus.RUNNING.value == "running"
    assert types.ProcessStatus.SUCCESS.value == "success"
    assert types.ProcessStatus.FAILED.value == "failed"


def test_batch_status_enum_values():
    assert types.BatchStatus.CREATED.value == "created"
    assert types.BatchStatus.IN_PROGRESS.value == "in_progress"
    assert types.BatchStatus.COMPLETED.value == "completed"
    assert types.BatchStatus.FAILED.value == "failed"


def test_pagination_params_typed_dict_usage():
    # TypedDict はランタイムでは dict として振る舞うので、シンプルな使用例で検証する。
    params: types.PaginationParams = {
        "page": 1,
        "per_page": 50,
        "sort": "date",
    }
    assert params["page"] == 1
    assert params["per_page"] == 50
    assert params["sort"] == "date"
