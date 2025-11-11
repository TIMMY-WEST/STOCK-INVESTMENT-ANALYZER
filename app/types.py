"""共通型定義モジュール."""

from __future__ import annotations

from enum import Enum
from typing import Literal, Optional, TypedDict


# Interval はデータ取得や集計でよく使われる時間間隔の列挙（Literal 型）
Interval = Literal[
    "1m",
    "5m",
    "15m",
    "30m",
    "60m",
    "1h",
    "1d",
    "1wk",
    "1mo",
]


class ProcessStatus(Enum):
    """バッチやジョブなどの処理状態を表す列挙型.

    値は文字列化してログやDBに格納できるようにしておく。
    """

    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"


class BatchStatus(Enum):
    """バッチ処理全体のステータスを示す列挙型."""

    QUEUED = "queued"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class PaginationParams(TypedDict, total=False):
    """ページネーションで一般的に使うパラメータの型定義.

    total=False としてオプショナルなキーを許容する。
    """

    page: int  # 現在のページ番号（1始まりを想定）
    per_page: int  # 1ページあたりの件数
    sort_by: Optional[str]
    order: Optional[Literal["asc", "desc"]]


__all__ = ["Interval", "ProcessStatus", "BatchStatus", "PaginationParams"]
