"""データベースリセットスクリプトのテストモジュール.

このモジュールは reset_db.sh および reset_db.bat スクリプトが
正しく動作することを検証します。
"""

import os
from pathlib import Path
import platform

from dotenv import load_dotenv
import psycopg2
import pytest


# プロジェクトルートディレクトリを取得
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent

# .envファイルを読み込み
load_dotenv(PROJECT_ROOT / ".env")

# データベース接続情報
DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "port": os.getenv("DB_PORT", "5432"),
    "database": os.getenv("DB_NAME", "stock_data_system"),
    "user": os.getenv("DB_USER", "stock_user"),
    "password": os.getenv("DB_PASSWORD", "stock_password"),
}


def get_db_connection():
    """データベース接続を取得."""
    return psycopg2.connect(**DB_CONFIG)


def check_database_exists(dbname: str) -> bool:
    """データベースが存在するか確認."""
    try:
        # postgresデータベースに接続して確認
        conn = psycopg2.connect(
            host=DB_CONFIG["host"],
            port=DB_CONFIG["port"],
            database="postgres",
            user=DB_CONFIG["user"],
            password=DB_CONFIG["password"],
        )
        conn.autocommit = True
        cursor = conn.cursor()

        cursor.execute(
            "SELECT 1 FROM pg_database WHERE datname = %s", (dbname,)
        )
        exists = cursor.fetchone() is not None

        cursor.close()
        conn.close()
        return exists
    except Exception as e:
        print(f"Error checking database existence: {e}")
        return False


def count_tables() -> int:
    """データベース内のテーブル数をカウント."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT COUNT(*)
            FROM information_schema.tables
            WHERE table_schema = 'public'
            AND table_type = 'BASE TABLE'
        """
        )

        count = cursor.fetchone()[0]

        cursor.close()
        conn.close()
        return count
    except Exception as e:
        print(f"Error counting tables: {e}")
        return 0


def count_sample_data() -> int:
    """サンプルデータのレコード数をカウント."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT COUNT(*) FROM stocks_1d")
        count = cursor.fetchone()[0]

        cursor.close()
        conn.close()
        return count
    except Exception as e:
        print(f"Error counting sample data: {e}")
        return 0


@pytest.mark.skipif(
    platform.system() == "Windows", reason="This test is for Linux/Mac only"
)
class TestResetDbShell:
    """reset_db.sh スクリプトのテスト（Linux/Mac用）."""

    def test_script_exists(self):
        """スクリプトファイルが存在することを確認."""
        # Arrange (準備)
        script_path = PROJECT_ROOT / "scripts" / "setup" / "reset_db.sh"

        # Act (実行)
        exists = script_path.exists()

        # Assert (検証)
        assert exists, "reset_db.sh script not found"

    def test_script_is_executable(self):
        """スクリプトが実行可能であることを確認."""
        # Arrange (準備)
        script_path = PROJECT_ROOT / "scripts" / "setup" / "reset_db.sh"

        # Act (実行)
        is_executable = os.access(script_path, os.X_OK)

        # Assert (検証)
        assert is_executable, "reset_db.sh is not executable"

    @pytest.mark.slow
    def test_script_runs_successfully(self):
        """スクリプトが正常に実行されることを確認.

        注意: このテストは実際にデータベースをリセットするため、
        テスト環境でのみ実行してください。
        """
        # Arrange (準備)
        # Act (実行)
        # Assert (検証)
        pytest.skip("Skipping actual database reset in automated tests")


@pytest.mark.skipif(
    platform.system() != "Windows", reason="This test is for Windows only"
)
class TestResetDbBatch:
    """reset_db.bat スクリプトのテスト（Windows用）."""

    def test_script_exists(self):
        """スクリプトファイルが存在することを確認."""
        # Arrange (準備)
        script_path = PROJECT_ROOT / "scripts" / "setup" / "reset_db.bat"

        # Act (実行)
        exists = script_path.exists()

        # Assert (検証)
        assert exists, "reset_db.bat script not found"

    @pytest.mark.slow
    def test_script_runs_successfully(self):
        """スクリプトが正常に実行されることを確認.

        注意: このテストは実際にデータベースをリセットするため、
        テスト環境でのみ実行してください。
        """
        # Arrange (準備)
        # Act (実行)
        # Assert (検証)
        pytest.skip("Skipping actual database reset in automated tests")


class TestDatabaseStructure:
    """データベース構造のテスト."""

    def test_database_exists(self):
        """データベースが存在することを確認."""
        # Arrange (準備)
        dbname = DB_CONFIG["database"]

        # Act (実行)
        exists = check_database_exists(dbname)

        # Assert (検証)
        assert exists, f"Database {dbname} does not exist"

    def test_tables_created(self):
        """必要なテーブルが作成されていることを確認."""
        # Arrange (準備)
        expected_min_tables = 12

        # Act (実行)
        table_count = count_tables()

        # Assert (検証)
        assert (
            table_count >= expected_min_tables
        ), f"Expected at least {expected_min_tables} tables, found {table_count}"

    def test_required_tables_exist(self):
        """主要テーブルが存在することを確認."""
        # Arrange (準備)
        required_tables = [
            "stocks_1m",
            "stocks_5m",
            "stocks_15m",
            "stocks_30m",
            "stocks_1h",
            "stocks_1d",
            "stocks_1wk",
            "stocks_1mo",
            "stock_master",
            "stock_master_updates",
            "batch_executions",
            "batch_execution_details",
        ]
        conn = get_db_connection()
        cursor = conn.cursor()

        # Act (実行)
        # Assert (検証)
        for table_name in required_tables:
            cursor.execute(
                """
                SELECT EXISTS (
                    SELECT FROM information_schema.tables
                    WHERE table_schema = 'public'
                    AND table_name = %s
                )
            """,
                (table_name,),
            )
            exists = cursor.fetchone()[0]
            assert exists, f"Table {table_name} does not exist"

        cursor.close()
        conn.close()

    def test_sample_data_inserted(self):
        """サンプルデータが投入されていることを確認."""
        # Arrange (準備)
        # Act (実行)
        sample_count = count_sample_data()

        # Assert (検証)
        assert sample_count > 0, "No sample data found in stocks_1d table"


class TestDatabaseConnection:
    """データベース接続のテスト."""

    def test_connection_successful(self):
        """データベースに接続できることを確認."""
        # Arrange (準備)
        # Act (実行)
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT 1")
            result = cursor.fetchone()

            # Assert (検証)
            assert result[0] == 1, "Connection test query failed"
            cursor.close()
            conn.close()
        except Exception as e:
            pytest.fail(f"Database connection failed: {e}")

    def test_user_has_permissions(self):
        """ユーザーに必要な権限があることを確認."""
        # Arrange (準備)
        conn = get_db_connection()
        cursor = conn.cursor()

        # Act (実行)
        # Assert (検証)
        try:
            cursor.execute(
                "CREATE TABLE IF NOT EXISTS test_permissions (id SERIAL PRIMARY KEY)"
            )
            cursor.execute("DROP TABLE test_permissions")
            conn.commit()
        except Exception as e:
            pytest.fail(f"User does not have sufficient permissions: {e}")
        finally:
            cursor.close()
            conn.close()


@pytest.mark.integration
class TestResetScriptIntegration:
    """リセットスクリプトの統合テスト."""

    @pytest.mark.slow
    @pytest.mark.skipif(
        os.getenv("CI") == "true", reason="Skip destructive test in CI"
    )
    def test_full_reset_workflow(self):
        """完全なリセットワークフローのテスト.

        注意: このテストは実際にデータベースをリセットするため、
        開発環境でのみ実行してください。
        """
        # Arrange (準備)
        flask_env = os.getenv("FLASK_ENV")

        # Act (実行)
        # Assert (検証)
        if flask_env == "production":
            pytest.skip("Skipping destructive test in production")

        pytest.skip("Manual test only - requires user confirmation")


if __name__ == "__main__":
    # テストを直接実行
    pytest.main([__file__, "-v"])
