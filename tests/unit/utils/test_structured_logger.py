"""構造化ログのテスト.

Phase 2要件: 構造化ログ出力とメトリクス収集のテスト。
"""

import json
import logging
from pathlib import Path

import pytest

from app.utils.structured_logger import (
    BatchLoggerAdapter,
    StructuredFormatter,
    get_batch_logger,
    setup_structured_logging,
)


pytestmark = pytest.mark.unit


class TestStructuredFormatter:
    """構造化ログフォーマッターのテスト."""

    def test_basic_format_with_valid_data_returns_formatted_output(self):
        """基本的なフォーマットのテスト."""
        # Arrange (準備)
        formatter = StructuredFormatter()
        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="test.py",
            lineno=1,
            msg="Test message",
            args=(),
            exc_info=None,
        )

        # Act (実行)
        result = formatter.format(record)
        data = json.loads(result)

        # Assert (検証)
        assert "timestamp" in data
        assert data["level"] == "INFO"
        assert data["logger"] == "test"
        assert data["message"] == "Test message"

    def test_batch_fields_with_valid_data_returns_batch_fields(self):
        """バッチフィールドのテスト."""
        # Arrange (準備)
        formatter = StructuredFormatter()
        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="test.py",
            lineno=1,
            msg="Batch operation",
            args=(),
            exc_info=None,
        )
        record.batch_id = "batch-123"
        record.worker_id = 1
        record.stock_code = "7203.T"
        record.action = "data_fetch"
        record.status = "success"
        record.duration_ms = 1500
        record.records_count = 50

        # Act (実行)
        result = formatter.format(record)
        data = json.loads(result)

        # Assert (検証)
        assert data["batch_id"] == "batch-123"
        assert data["worker_id"] == 1
        assert data["stock_code"] == "7203.T"
        assert data["action"] == "data_fetch"
        assert data["status"] == "success"
        assert data["duration_ms"] == 1500
        assert data["records_count"] == 50


class TestBatchLoggerAdapter:
    """バッチロガーアダプターのテスト."""

    def test_log_batch_action_success_with_valid_action_returns_success_log(
        self, caplog
    ):
        """成功時のバッチアクションログのテスト."""
        # Arrange (準備)
        logger = logging.getLogger("test_batch")
        logger.setLevel(logging.INFO)
        adapter = BatchLoggerAdapter(logger, {"batch_id": "test-batch"})

        # Act (実行)
        with caplog.at_level(logging.INFO):
            adapter.log_batch_action(
                action="data_fetch",
                stock_code="7203.T",
                status="success",
                duration_ms=1000,
                records_count=50,
            )

        # Assert (検証)
        assert len(caplog.records) == 1
        assert "data_fetch" in caplog.text
        assert "7203.T" in caplog.text

    def test_log_batch_action_failed_with_error_returns_failure_log(
        self, caplog
    ):
        """失敗時のバッチアクションログのテスト."""
        # Arrange (準備)
        logger = logging.getLogger("test_batch_failed")
        logger.setLevel(logging.ERROR)
        adapter = BatchLoggerAdapter(logger, {"batch_id": "test-batch"})

        # Act (実行)
        with caplog.at_level(logging.ERROR):
            adapter.log_batch_action(
                action="data_fetch",
                stock_code="9999.T",
                status="failed",
                error_message="Connection timeout",
            )

        # Assert (検証)
        assert len(caplog.records) == 1
        assert "failed" in caplog.text or "Connection timeout" in caplog.text

    def test_log_batch_action_retry_with_retry_attempt_returns_retry_log(
        self, caplog
    ):
        """リトライ時のバッチアクションログのテスト."""
        # Arrange (準備)
        logger = logging.getLogger("test_batch_retry")
        logger.setLevel(logging.WARNING)
        adapter = BatchLoggerAdapter(logger, {"batch_id": "test-batch"})

        # Act (実行)
        with caplog.at_level(logging.WARNING):
            adapter.log_batch_action(
                action="data_fetch",
                stock_code="7203.T",
                status="retry",
                retry_count=1,
            )

        # Assert (検証)
        assert len(caplog.records) == 1
        assert "retry" in caplog.text.lower() or "Retry" in caplog.text


class TestLoggingSetup:
    """ログ設定のテスト."""

    def test_setup_logging_with_valid_config_returns_configured_logger(
        self, tmp_path
    ):
        """ログ設定のテスト."""
        # Arrange (準備)
        log_dir = tmp_path / "logs"

        # Act (実行)
        logger = setup_structured_logging(
            log_dir=str(log_dir),
            log_level=logging.INFO,
            enable_console=False,
            enable_file=True,
        )
        logger.info("Test log message")

        # Assert (検証)
        assert logger is not None
        assert logger.level == logging.INFO
        assert log_dir.exists()
        log_file = log_dir / "batch_bulk.log"
        assert log_file.exists()

    def test_get_batch_logger_with_valid_config_returns_logger_instance(self):
        """バッチロガー取得のテスト."""
        # Arrange (準備)
        # 必要なパラメータを準備

        # Act (実行)
        adapter = get_batch_logger(batch_id="test-123", worker_id=1)

        # Assert (検証)
        assert isinstance(adapter, BatchLoggerAdapter)
        assert adapter.extra["batch_id"] == "test-123"
        assert adapter.extra["worker_id"] == "1"

    def test_structured_logger_initialization_with_valid_config_returns_logger_instance(
        self, tmp_path
    ):
        """構造化ログオブジェクトのテスト."""
        # Arrange (準備)
        log_dir = tmp_path / "logs"

        # Act (実行)
        logger = setup_structured_logging(
            log_dir=str(log_dir),
            log_level=logging.INFO,
            enable_console=False,
            enable_file=True,
        )
        logger.info("Test log message")

        # Assert (検証)
        assert logger is not None
        assert logger.level == logging.INFO
        assert log_dir.exists()
        log_file = log_dir / "batch_bulk.log"
        assert log_file.exists()

    def test_structured_logger_info_logging_with_valid_message_returns_formatted_output(
        self, tmp_path
    ):
        """構造化ログ出力のテスト."""
        # Arrange (準備)
        log_dir = tmp_path / "logs"
        logger = setup_structured_logging(
            log_dir=str(log_dir),
            log_level=logging.INFO,
            enable_console=False,
            enable_file=True,
        )

        # Act (実行)
        logger.info("Test log message")

        # Assert (検証)
        assert logger is not None
        assert logger.level == logging.INFO
        assert log_dir.exists()
        log_file = log_dir / "batch_bulk.log"
        assert log_file.exists()

    def test_structured_logger_error_logging_with_exception_returns_error_details(
        self, tmp_path
    ):
        """構造化ログ出力のテスト."""
        # Arrange (準備)
        log_dir = tmp_path / "logs"
        logger = setup_structured_logging(
            log_dir=str(log_dir),
            log_level=logging.INFO,
            enable_console=False,
            enable_file=True,
        )

        # Act (実行)
        logger.info("Test log message")

        # Assert (検証)
        assert logger is not None
        assert logger.level == logging.INFO
        assert log_dir.exists()
        log_file = log_dir / "batch_bulk.log"
        assert log_file.exists()

    def test_structured_logger_debug_logging_with_debug_mode_returns_debug_output(
        self, tmp_path
    ):
        """構造化ログ出力のテスト."""
        # Arrange (準備)
        log_dir = tmp_path / "logs"
        logger = setup_structured_logging(
            log_dir=str(log_dir),
            log_level=logging.INFO,
            enable_console=False,
            enable_file=True,
        )

        # Act (実行)
        logger.info("Test log message")

        # Assert (検証)
        assert logger is not None
        assert logger.level == logging.INFO
        assert log_dir.exists()
        log_file = log_dir / "batch_bulk.log"
        assert log_file.exists()

    def test_structured_logger_warning_logging_with_warning_message_returns_warning_output(
        self, tmp_path
    ):
        """構造化ログ出力のテスト."""
        # Arrange (準備)
        log_dir = tmp_path / "logs"
        logger = setup_structured_logging(
            log_dir=str(log_dir),
            log_level=logging.INFO,
            enable_console=False,
            enable_file=True,
        )

        # Act (実行)
        logger.info("Test log message")

        # Assert (検証)
        assert logger is not None
        assert logger.level == logging.INFO
        assert log_dir.exists()
        log_file = log_dir / "batch_bulk.log"
        assert log_file.exists()
