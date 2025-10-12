"""構造化ログ出力モジュール

Phase 2要件: バッチ処理の詳細なログ出力とメトリクス収集機能
仕様書: docs/api_bulk_fetch.md (772-787行目)
"""

import json
import logging
import logging.handlers
from datetime import datetime
from typing import Any, Dict, Optional
from pathlib import Path


class StructuredFormatter(logging.Formatter):
    """JSON形式の構造化ログフォーマッター"""

    def format(self, record: logging.LogRecord) -> str:
        """ログレコードをJSON形式にフォーマット"""
        log_data = {
            "timestamp": datetime.fromtimestamp(record.created).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }

        # 追加のフィールドがあれば含める
        if hasattr(record, 'batch_id'):
            log_data['batch_id'] = record.batch_id
        if hasattr(record, 'worker_id'):
            log_data['worker_id'] = record.worker_id
        if hasattr(record, 'stock_code'):
            log_data['stock_code'] = record.stock_code
        if hasattr(record, 'action'):
            log_data['action'] = record.action
        if hasattr(record, 'status'):
            log_data['status'] = record.status
        if hasattr(record, 'duration_ms'):
            log_data['duration_ms'] = record.duration_ms
        if hasattr(record, 'records_count'):
            log_data['records_count'] = record.records_count
        if hasattr(record, 'error_message'):
            log_data['error_message'] = record.error_message
        if hasattr(record, 'retry_count'):
            log_data['retry_count'] = record.retry_count

        return json.dumps(log_data, ensure_ascii=False)


class BatchLoggerAdapter(logging.LoggerAdapter):
    """バッチ処理用ログアダプター

    構造化ログ出力用の追加情報を管理します。
    """

    def process(self, msg: str, kwargs: Dict[str, Any]) -> tuple:
        """ログメッセージに追加情報を付与"""
        extra = kwargs.get('extra', {})

        # コンテキスト情報をマージ
        if self.extra:
            extra.update(self.extra)

        kwargs['extra'] = extra
        return msg, kwargs

    def log_batch_action(
        self,
        action: str,
        stock_code: Optional[str] = None,
        status: str = 'success',
        duration_ms: Optional[int] = None,
        records_count: Optional[int] = None,
        error_message: Optional[str] = None,
        retry_count: int = 0,
        **kwargs
    ):
        """バッチ処理のアクションをログ出力

        Args:
            action: アクション種別 (data_fetch, data_save, error_occurred等)
            stock_code: 銘柄コード
            status: ステータス (success, failed, retry)
            duration_ms: 処理時間（ミリ秒）
            records_count: レコード数
            error_message: エラーメッセージ
            retry_count: リトライ回数
            **kwargs: 追加のログ情報
        """
        extra = {
            'action': action,
            'status': status,
            'retry_count': retry_count
        }

        if stock_code:
            extra['stock_code'] = stock_code
        if duration_ms is not None:
            extra['duration_ms'] = duration_ms
        if records_count is not None:
            extra['records_count'] = records_count
        if error_message:
            extra['error_message'] = error_message

        # 追加のフィールドを含める
        extra.update(kwargs)

        # ステータスに応じたログレベルを選択
        if status == 'failed':
            self.error(f"[{action}] {stock_code or 'N/A'}: {error_message or 'Unknown error'}", extra=extra)
        elif status == 'retry':
            self.warning(f"[{action}] {stock_code or 'N/A'}: Retry {retry_count}", extra=extra)
        else:
            self.info(f"[{action}] {stock_code or 'N/A'}: Success", extra=extra)


def setup_structured_logging(
    log_dir: str = 'logs',
    log_level: int = logging.INFO,
    max_bytes: int = 10 * 1024 * 1024,  # 10MB
    backup_count: int = 10,
    enable_console: bool = True,
    enable_file: bool = True
) -> logging.Logger:
    """構造化ログ設定

    Args:
        log_dir: ログディレクトリ
        log_level: ログレベル
        max_bytes: ログファイルの最大サイズ（バイト）
        backup_count: バックアップファイル数
        enable_console: コンソール出力を有効化
        enable_file: ファイル出力を有効化

    Returns:
        設定済みのロガー
    """
    # ログディレクトリの作成
    log_path = Path(log_dir)
    log_path.mkdir(exist_ok=True)

    # ルートロガーの取得
    logger = logging.getLogger('bulk_batch')
    logger.setLevel(log_level)
    logger.handlers.clear()  # 既存のハンドラをクリア

    formatter = StructuredFormatter()

    # ファイルハンドラ（ローテーション付き）
    if enable_file:
        file_handler = logging.handlers.RotatingFileHandler(
            filename=log_path / 'batch_bulk.log',
            maxBytes=max_bytes,
            backupCount=backup_count,
            encoding='utf-8'
        )
        file_handler.setLevel(log_level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    # コンソールハンドラ
    if enable_console:
        console_handler = logging.StreamHandler()
        console_handler.setLevel(log_level)
        # コンソールは人間が読みやすい形式
        console_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        console_handler.setFormatter(console_formatter)
        logger.addHandler(console_handler)

    return logger


def get_batch_logger(
    batch_id: Optional[str] = None,
    worker_id: Optional[int] = None
) -> BatchLoggerAdapter:
    """バッチ処理用ロガーを取得

    Args:
        batch_id: バッチID
        worker_id: ワーカーID

    Returns:
        バッチロガーアダプター
    """
    logger = logging.getLogger('bulk_batch')

    extra = {}
    if batch_id:
        extra['batch_id'] = batch_id
    if worker_id is not None:
        extra['worker_id'] = worker_id

    return BatchLoggerAdapter(logger, extra)
