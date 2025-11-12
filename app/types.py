"""Project shared type definitions.

プロジェクト全体で使用する共通型定義を格納するモジュール。

注意:
- ソース内コメントは日本語で記載すること。
"""

from __future__ import annotations

from enum import Enum
from typing import Literal, Optional, TypedDict


# Interval は yfinance スタイルの時間軸を表すリテラル型。
# プロジェクト内では '1m', '5m', '15m', '30m', '1h', '1d', '1wk', '1mo' を使用します。
Interval = Literal["1m", "5m", "15m", "30m", "1h", "1d", "1wk", "1mo"]


class ProcessStatus(str, Enum):
    """Represents the execution status of a process.

    バッチやプロセスの実行状態を表す列挙型。
    """

    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"


class BatchStatus(str, Enum):
    """Represents high-level batch processing status.

    バッチ処理の高レベルステータスを表す列挙型。
    """

    CREATED = "created"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"


class PaginationParams(TypedDict, total=False):
    """TypedDict for pagination parameters.

    ページネーションに使用するパラメータの型定義。

    - page: 1始まりのページ番号
    - per_page: 1ページあたりの件数
    - sort: ソートキー（オプション）
    """

    page: int
    per_page: int
    sort: Optional[str]


__all__ = ["Interval", "ProcessStatus", "BatchStatus", "PaginationParams"]
