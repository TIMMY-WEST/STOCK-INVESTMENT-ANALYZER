"""構造化ログのテスト

Phase 2要件: 構造化ログ出力とメトリクス収集のテスト
"""

import json
import logging
import pytest
from pathlib import Path
from utils.structured_logger import (
    StructuredFormatter,
    BatchLoggerAdapter,
    setup_structured_logging,
    get_batch_logger
)


class TestStructuredFormatter:
    """構造化ログフォーマッターのテスト"""

    def test_basic_format(self):
        """基本的なフォーマットのテスト"""
        formatter = StructuredFormatter()
        record = logging.LogRecord(
            name='test',
            level=logging.INFO,
            pathname='test.py',
            lineno=1,
            msg='Test message',
            args=(),
            exc_info=None
        )

        result = formatter.format(record)
        data = json.loads(result)

        assert 'timestamp' in data
        assert data['level'] == 'INFO'
        assert data['logger'] == 'test'
        assert data['message'] == 'Test message'

    def test_batch_fields(self):
        """バッチフィールドのテスト"""
        formatter = StructuredFormatter()
        record = logging.LogRecord(
            name='test',
            level=logging.INFO,
            pathname='test.py',
            lineno=1,
            msg='Batch operation',
            args=(),
            exc_info=None
        )
        record.batch_id = 'batch-123'
        record.worker_id = 1
        record.stock_code = '7203.T'
        record.action = 'data_fetch'
        record.status = 'success'
        record.duration_ms = 1500
        record.records_count = 50

        result = formatter.format(record)
        data = json.loads(result)

        assert data['batch_id'] == 'batch-123'
        assert data['worker_id'] == 1
        assert data['stock_code'] == '7203.T'
        assert data['action'] == 'data_fetch'
        assert data['status'] == 'success'
        assert data['duration_ms'] == 1500
        assert data['records_count'] == 50


class TestBatchLoggerAdapter:
    """バッチロガーアダプターのテスト"""

    def test_log_batch_action_success(self, caplog):
        """成功時のバッチアクションログのテスト"""
        logger = logging.getLogger('test_batch')
        logger.setLevel(logging.INFO)

        adapter = BatchLoggerAdapter(logger, {'batch_id': 'test-batch'})

        with caplog.at_level(logging.INFO):
            adapter.log_batch_action(
                action='data_fetch',
                stock_code='7203.T',
                status='success',
                duration_ms=1000,
                records_count=50
            )

        assert len(caplog.records) == 1
        assert 'data_fetch' in caplog.text
        assert '7203.T' in caplog.text

    def test_log_batch_action_failed(self, caplog):
        """失敗時のバッチアクションログのテスト"""
        logger = logging.getLogger('test_batch_failed')
        logger.setLevel(logging.ERROR)

        adapter = BatchLoggerAdapter(logger, {'batch_id': 'test-batch'})

        with caplog.at_level(logging.ERROR):
            adapter.log_batch_action(
                action='data_fetch',
                stock_code='9999.T',
                status='failed',
                error_message='Connection timeout'
            )

        assert len(caplog.records) == 1
        assert 'failed' in caplog.text or 'Connection timeout' in caplog.text

    def test_log_batch_action_retry(self, caplog):
        """リトライ時のバッチアクションログのテスト"""
        logger = logging.getLogger('test_batch_retry')
        logger.setLevel(logging.WARNING)

        adapter = BatchLoggerAdapter(logger, {'batch_id': 'test-batch'})

        with caplog.at_level(logging.WARNING):
            adapter.log_batch_action(
                action='data_fetch',
                stock_code='7203.T',
                status='retry',
                retry_count=1
            )

        assert len(caplog.records) == 1
        assert 'retry' in caplog.text.lower() or 'Retry' in caplog.text


class TestLoggingSetup:
    """ログ設定のテスト"""

    def test_setup_logging(self, tmp_path):
        """ログ設定のテスト"""
        log_dir = tmp_path / 'logs'

        logger = setup_structured_logging(
            log_dir=str(log_dir),
            log_level=logging.INFO,
            enable_console=False,
            enable_file=True
        )

        assert logger is not None
        assert logger.level == logging.INFO
        assert log_dir.exists()

        # ログファイルが作成されることを確認
        logger.info('Test log message')
        log_file = log_dir / 'batch_bulk.log'
        assert log_file.exists()

    def test_get_batch_logger(self):
        """バッチロガー取得のテスト"""
        adapter = get_batch_logger(batch_id='test-123', worker_id=1)

        assert isinstance(adapter, BatchLoggerAdapter)
        assert adapter.extra['batch_id'] == 'test-123'
        assert adapter.extra['worker_id'] == 1
