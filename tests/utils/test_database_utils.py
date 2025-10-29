"""database_utilsモジュールのテスト."""

from unittest.mock import MagicMock, patch

import pytest

from app.utils.database_utils import execute_with_session, to_dict_if_exists


class TestExecuteWithSession:
    """execute_with_session関数のテスト."""

    def test_with_provided_session_with_valid_session_returns_success(self):
        """セッションが提供された場合のテスト."""
        # Arrange
        mock_session = MagicMock()
        expected_result = {"id": 1, "name": "test"}

        def operation(s):
            return expected_result

        # Act
        result = execute_with_session(operation, mock_session)

        # Assert
        assert result == expected_result

    @patch("app.utils.database_utils.get_db_session")
    def test_without_provided_session_with_no_session_returns_success(
        self, mock_get_db_session
    ):
        """セッションが提供されない場合のテスト."""
        # Arrange
        mock_session = MagicMock()
        mock_get_db_session.return_value.__enter__.return_value = mock_session
        expected_result = {"id": 2, "name": "test2"}

        def operation(s):
            return expected_result

        # Act
        result = execute_with_session(operation, None)

        # Assert
        assert result == expected_result
        mock_get_db_session.assert_called_once()

    def test_operation_with_database_modification_with_valid_data_returns_success(
        self,
    ):
        """データベース変更を伴う操作のテスト."""
        # Arrange
        mock_session = MagicMock()

        def operation(s):
            s.add({"test": "data"})
            s.flush()
            return True

        # Act
        result = execute_with_session(operation, mock_session)

        # Assert
        assert result is True
        mock_session.add.assert_called_once()
        mock_session.flush.assert_called_once()


class TestToDictIfExists:
    """to_dict_if_exists関数のテスト."""

    def test_with_existing_object_with_valid_object_returns_dict(self):
        """オブジェクトが存在する場合のテスト."""
        # Arrange
        mock_obj = MagicMock()
        expected_dict = {"id": 1, "name": "test"}
        mock_obj.to_dict.return_value = expected_dict

        # Act
        result = to_dict_if_exists(mock_obj)

        # Assert
        assert result == expected_dict
        mock_obj.to_dict.assert_called_once()

    def test_with_none_object_with_none_input_returns_none(self):
        """オブジェクトがNoneの場合のテスト."""
        # Act
        result = to_dict_if_exists(None)

        # Assert
        assert result is None

    def test_with_object_without_to_dict_method_with_invalid_object_returns_none(
        self,
    ):
        """to_dictメソッドを持たないオブジェクトのテスト."""
        # Arrange
        obj = object()

        # Act & Assert
        with pytest.raises(AttributeError):
            to_dict_if_exists(obj)
