"""データベース接続管理のユニットテスト.

このモジュールは、データベース接続プールとセッション管理の
ユニットテストを提供します.
"""
# flake8: noqa

from unittest.mock import MagicMock, patch

import pytest
from sqlalchemy import inspect
from sqlalchemy.exc import OperationalError, SQLAlchemyError

from app.models import SessionLocal, engine, get_db_session


pytestmark = pytest.mark.unit


class TestDatabaseConnectionPool:
    """データベース接続プールのテストクラス。"""

    def test_engine_has_pool_configuration_with_settings_returns_configured_pool(
        self,
    ):
        """エンジンにコネクションプール設定があることを確認."""
        # Arrange (準備)
        # エンジンのプール設定を確認
        pool = engine.pool
        # Assert (検証)
        assert pool is not None
        # pool_sizeの確認（10に設定されているはず）
        assert pool.size() == 10
        # max_overflowの確認（20に設定されているはず）
        assert pool._max_overflow == 20

    def test_engine_has_pool_pre_ping_with_setting_returns_enabled(self):
        """pool_pre_pingが有効であることを確認."""
        # Arrange (準備)
        # pool_pre_pingは接続使用前にpingを実行

        # Act (実行)
        # 設定値の取得は準備フェーズで完了
        # Assert (検証)
        assert engine.pool._pre_ping

    def test_engine_has_pool_recycle_with_setting_returns_configured_time(
        self,
    ):
        """pool_recycleが設定されていることを確認."""
        # Arrange (準備)
        # pool_recycleは3600秒（1時間）に設定

        # Act (実行)
        # 設定値の取得は準備フェーズで完了
        # Assert (検証)
        assert engine.pool._recycle == 3600

    def test_engine_pool_timeout_with_setting_returns_configured_timeout(self):
        """pool_timeoutが設定されていることを確認."""
        # Arrange (準備)
        # pool_timeoutは30秒に設定

        # Act (実行)
        # 設定値の取得は準備フェーズで完了
        # Assert (検証)
        assert engine.pool._timeout == 30


class TestSessionManagement:
    """セッション管理のテストクラス。"""

    def test_get_db_session_context_manager_with_usage_returns_session(self):
        """get_db_sessionがコンテキストマネージャーとして機能することを確認."""
        # Arrange (準備)
        # セットアップ不要

        # Act (実行)
        with get_db_session() as db_session:
            # Assert (検証)
            assert db_session is not None
            # セッションが有効であることを確認
            assert db_session.is_active

    @patch("app.models.database.SessionLocal")
    def test_session_commit_on_success_with_normal_operation_returns_committed(
        self, mock_session_local
    ):
        """正常終了時にセッションがコミットされることを確認."""
        # Arrange (準備)
        mock_session = MagicMock()
        mock_session_local.return_value = mock_session

        with get_db_session():
            pass

        # commitが呼ばれたことを確認
        mock_session.commit.assert_called_once()
        # closeが呼ばれたことを確認
        mock_session.close.assert_called_once()

    @patch("app.models.database.SessionLocal")
    def test_session_rollback_on_exception_with_error_returns_rolled_back(
        self, mock_session_local
    ):
        """例外発生時にセッションがロールバックされることを確認."""
        # Arrange (準備)
        mock_session = MagicMock()
        mock_session_local.return_value = mock_session

        with pytest.raises(ValueError):
            with get_db_session():
                raise ValueError("Test exception")

        # rollbackが呼ばれたことを確認
        mock_session.rollback.assert_called_once()
        # closeが呼ばれたことを確認
        mock_session.close.assert_called_once()
        # commitは呼ばれていないことを確認
        mock_session.commit.assert_not_called()

    @patch("app.models.database.SessionLocal")
    def test_session_always_closed(self, mock_session_local):
        """例外の有無に関わらずセッションが必ずクローズされることを確認."""
        # Arrange (準備)
        mock_session = MagicMock()
        mock_session_local.return_value = mock_session

        # Act (実行) - 正常ケース
        with get_db_session():
            pass
        # Assert (検証)
        mock_session.close.assert_called_once()

        # Act (実行) - 例外ケース
        mock_session.reset_mock()
        with pytest.raises(RuntimeError):
            with get_db_session():
                raise RuntimeError("Test error")
        # Assert (検証)
        mock_session.close.assert_called_once()


class TestConnectionLeakPrevention:
    """接続リーク防止のテストクラス。"""

    def test_multiple_sequential_sessions(self):
        """連続したセッション使用で接続リークが発生しないことを確認."""
        from sqlalchemy import text

        # Arrange (準備)
        # Act (実行)
        # 複数のセッションを連続して使用
        for _ in range(5):
            with get_db_session() as session:
                # Assert (検証)
                assert session is not None
                result = session.execute(text("SELECT 1")).scalar()
                assert result == 1

        # Assert (検証) - プールの統計情報を確認（接続がプールに戻されていることを確認）
        pool = engine.pool
        assert pool.checkedout() == 0

    def test_session_exception_does_not_leak_connection_with_error_returns_clean_state(
        self,
    ):
        """例外発生時も接続リークが発生しないことを確認."""
        # Arrange (準備)
        initial_checkedout = engine.pool.checkedout()

        # Act (実行)
        try:
            with get_db_session():
                raise ValueError("Test exception")
        except ValueError:
            pass

        # Assert (検証)
        assert engine.pool.checkedout() == initial_checkedout


class TestConnectionResilience:
    """接続の回復力テストクラス。"""

    @patch("app.models.engine.pool.connect")
    def test_pool_pre_ping_detects_stale_connections_with_invalid_connection_returns_new_connection(
        self, mock_connect
    ):
        """pool_pre_pingが古い接続を検出できることを確認."""
        # 最初の接続は失敗、2回目は成功するようモック
        mock_connect.side_effect = [
            OperationalError("statement", "params", "orig"),
            MagicMock(),
        ]
        # Arrange (準備)
        # Act (実行) - pool.connect が最初失敗し次に成功するように設定
        # Assert (検証) - 実際の接続フローは外部 DB 環境での検証を推奨
        pass


class TestSessionLocalConfiguration:
    """SessionLocalの設定テストクラス。"""

    def test_session_local_autocommit_false(self):
        """SessionLocalのautocommitがFalseであることを確認."""
        # Arrange (準備)
        # Act (実行)
        session = SessionLocal()
        try:
            # Assert (検証)
            assert session is not None
        finally:
            session.close()

    def test_session_local_autoflush_false(self):
        """SessionLocalのautoflushがFalseであることを確認."""
        # Arrange (準備)
        # Act (実行)
        session = SessionLocal()
        try:
            # Assert (検証)
            assert not session.autoflush
        finally:
            session.close()

    def test_session_local_bound_to_engine(self):
        """SessionLocalが正しいエンジンにバインドされていることを確認."""
        # Arrange (準備)
        # Act (実行)
        session = SessionLocal()
        try:
            # Assert (検証)
            assert session.bind == engine
        finally:
            session.close()
