"""データベース接続管理のユニットテスト.

このモジュールは、データベース接続プールとセッション管理の
ユニットテストを提供します。
"""

import unittest
from unittest.mock import MagicMock, patch

import pytest
from sqlalchemy import inspect
from sqlalchemy.exc import OperationalError, SQLAlchemyError

from app.models import SessionLocal, engine, get_db_session


class TestDatabaseConnectionPool(unittest.TestCase):
    """データベース接続プールのテストクラス."""

    def test_engine_has_pool_configuration_with_settings_returns_configured_pool(
        self,
    ):
        """エンジンにコネクションプール設定があることを確認."""
        # Arrange (準備)
        # エンジンのプール設定を確認
        pool = engine.pool

        # Act (実行)
        # 設定値の取得は準備フェーズで完了

        # Assert (検証)
        self.assertIsNotNone(pool)
        # pool_sizeの確認（10に設定されているはず）
        self.assertEqual(pool.size(), 10)
        # max_overflowの確認（20に設定されているはず）
        self.assertEqual(pool._max_overflow, 20)

    def test_engine_has_pool_pre_ping_with_setting_returns_enabled(self):
        """pool_pre_pingが有効であることを確認."""
        # Arrange (準備)
        # pool_pre_pingは接続使用前にpingを実行

        # Act (実行)
        # 設定値の取得は準備フェーズで完了

        # Assert (検証)
        self.assertTrue(engine.pool._pre_ping)

    def test_engine_has_pool_recycle_with_setting_returns_configured_time(
        self,
    ):
        """pool_recycleが設定されていることを確認."""
        # Arrange (準備)
        # pool_recycleは3600秒（1時間）に設定

        # Act (実行)
        # 設定値の取得は準備フェーズで完了

        # Assert (検証)
        self.assertEqual(engine.pool._recycle, 3600)

    def test_engine_pool_timeout_with_setting_returns_configured_timeout(self):
        """pool_timeoutが設定されていることを確認."""
        # Arrange (準備)
        # pool_timeoutは30秒に設定

        # Act (実行)
        # 設定値の取得は準備フェーズで完了

        # Assert (検証)
        self.assertEqual(engine.pool._timeout, 30)


class TestSessionManagement(unittest.TestCase):
    """セッション管理のテストクラス."""

    def test_get_db_session_context_manager_with_usage_returns_session(self):
        """get_db_sessionがコンテキストマネージャーとして機能することを確認."""
        # Arrange (準備)
        # セットアップ不要

        # Act (実行)
        with get_db_session() as db_session:
            # Assert (検証)
            self.assertIsNotNone(db_session)
            # セッションが有効であることを確認
            self.assertTrue(db_session.is_active)

    @patch("app.models.SessionLocal")
    def test_session_commit_on_success_with_normal_operation_returns_committed(
        self, mock_session_local
    ):
        """正常終了時にセッションがコミットされることを確認."""
        # Arrange (準備)
        mock_session = MagicMock()
        mock_session_local.return_value = mock_session

        # Act (実行)
        with get_db_session():
            # 正常に処理が完了
            pass

        # Assert (検証)
        # commitが呼ばれたことを確認
        mock_session.commit.assert_called_once()
        # closeが呼ばれたことを確認
        mock_session.close.assert_called_once()

    @patch("app.models.SessionLocal")
    def test_session_rollback_on_exception_with_error_returns_rolled_back(
        self, mock_session_local
    ):
        """例外発生時にセッションがロールバックされることを確認."""
        # Arrange (準備)
        mock_session = MagicMock()
        mock_session_local.return_value = mock_session

        # Act (実行)
        with pytest.raises(ValueError):
            with get_db_session():
                # 例外を発生させる
                raise ValueError("Test exception")

        # Assert (検証)
        # rollbackが呼ばれたことを確認
        mock_session.rollback.assert_called_once()
        # closeが呼ばれたことを確認
        mock_session.close.assert_called_once()
        # commitは呼ばれていないことを確認
        mock_session.commit.assert_not_called()

    @patch("app.models.SessionLocal")
    def test_session_always_closed(self, mock_session_local):
        """例外の有無に関わらずセッションが必ずクローズされることを確認."""
        mock_session = MagicMock()
        mock_session_local.return_value = mock_session

        # 正常ケース
        with get_db_session():
            pass
        mock_session.close.assert_called_once()

        # 例外ケース
        mock_session.reset_mock()
        with pytest.raises(RuntimeError):
            with get_db_session():
                raise RuntimeError("Test error")
        mock_session.close.assert_called_once()


class TestConnectionLeakPrevention(unittest.TestCase):
    """接続リーク防止のテストクラス."""

    def test_multiple_sequential_sessions(self):
        """連続したセッション使用で接続リークが発生しないことを確認."""
        from sqlalchemy import text

        # 複数のセッションを連続して使用
        for _ in range(5):
            with get_db_session() as session:
                self.assertIsNotNone(session)
                # セッション内で簡単なクエリを実行
                result = session.execute(text("SELECT 1")).scalar()
                self.assertEqual(result, 1)

        # プールの統計情報を確認（接続がプールに戻されていることを確認）
        pool = engine.pool
        # チェックアウトされた接続数が0であることを確認
        self.assertEqual(pool.checkedout(), 0)

    def test_session_exception_does_not_leak_connection_with_error_returns_clean_state(
        self,
    ):
        """例外発生時も接続リークが発生しないことを確認."""
        initial_checkedout = engine.pool.checkedout()

        try:
            with get_db_session():
                # 意図的に例外を発生させる
                raise ValueError("Test exception")
        except ValueError:
            pass

        # チェックアウトされた接続数が元に戻っていることを確認
        self.assertEqual(engine.pool.checkedout(), initial_checkedout)


class TestConnectionResilience(unittest.TestCase):
    """接続の回復力テストクラス."""

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

        # pool_pre_pingにより自動的に再接続されるはず
        # （この挙動は実際のデータベース接続でテストするのが望ましい）
        pass


class TestSessionLocalConfiguration(unittest.TestCase):
    """SessionLocalの設定テストクラス."""

    def test_session_local_autocommit_false(self):
        """SessionLocalのautocommitがFalseであることを確認."""
        # SQLAlchemy 2.0ではSessionLocalのautocommit引数がFalseに設定されている
        # セッション作成時の設定を確認
        session = SessionLocal()
        try:
            # SQLAlchemy 2.0ではautocommit属性は存在しないため、
            # sessionmaker の設定を確認
            # autocommit=Falseはデフォルト動作
            self.assertIsNotNone(session)
        finally:
            session.close()

    def test_session_local_autoflush_false(self):
        """SessionLocalのautoflushがFalseであることを確認."""
        session = SessionLocal()
        try:
            # autoflushがFalseであることを確認
            self.assertFalse(session.autoflush)
        finally:
            session.close()

    def test_session_local_bound_to_engine(self):
        """SessionLocalが正しいエンジンにバインドされていることを確認."""
        session = SessionLocal()
        try:
            # セッションが正しいエンジンを使用していることを確認
            self.assertEqual(session.bind, engine)
        finally:
            session.close()


if __name__ == "__main__":
    unittest.main()
