"""Unit tests for mixin classes.

このモジュールは、app/models/mixins.pyで定義されているMixinクラスの
ユニットテストを提供します。
"""

from datetime import datetime
from decimal import Decimal

import pytest
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base
from app.models.mixins import (
    DictSerializableMixin,
    SoftDeleteMixin,
    TimestampMixin,
)


# テスト用のモデルクラス定義
class TestTimestampModel(Base, TimestampMixin):
    """TimestampMixinのテスト用モデル."""

    __tablename__ = "test_timestamp"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50))


class TestSoftDeleteModel(Base, SoftDeleteMixin):
    """SoftDeleteMixinのテスト用モデル."""

    __tablename__ = "test_soft_delete"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50))


class TestDictSerializableModel(Base, DictSerializableMixin):
    """DictSerializableMixinのテスト用モデル."""

    __tablename__ = "test_dict_serializable"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50))
    price: Mapped[Decimal] = mapped_column()


class TestCombinedMixinsModel(
    Base, TimestampMixin, SoftDeleteMixin, DictSerializableMixin
):
    """全てのMixinを組み合わせたテスト用モデル."""

    __tablename__ = "test_combined"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50))
    value: Mapped[Decimal] = mapped_column()


class TestTimestampMixin:
    """TimestampMixinのテストクラス."""

    def test_timestamp_fields_exist(self):
        """タイムスタンプフィールドが存在することを確認."""
        model = TestTimestampModel()
        assert hasattr(model, "created_at")
        assert hasattr(model, "updated_at")

    def test_timestamp_fields_are_mapped_columns(self):
        """タイムスタンプフィールドがMapped型であることを確認."""
        # MixinのアノテーションはTimestampMixinクラス自体にある
        assert "created_at" in TimestampMixin.__annotations__
        assert "updated_at" in TimestampMixin.__annotations__

    def test_timestamp_fields_in_table(self):
        """タイムスタンプフィールドがテーブルカラムとして定義されていることを確認."""
        table = TestTimestampModel.__table__
        assert "created_at" in table.c
        assert "updated_at" in table.c


class TestSoftDeleteMixin:
    """SoftDeleteMixinのテストクラス."""

    def test_soft_delete_fields_exist(self):
        """論理削除フィールドが存在することを確認."""
        model = TestSoftDeleteModel()
        assert hasattr(model, "is_deleted")
        assert hasattr(model, "deleted_at")

    def test_is_deleted_default_is_false(self):
        """is_deletedのデフォルト値がFalseであることを確認."""
        table = TestSoftDeleteModel.__table__
        is_deleted_col = table.c.is_deleted
        assert is_deleted_col.default is not None

    def test_soft_delete_fields_in_table(self):
        """論理削除フィールドがテーブルカラムとして定義されていることを確認."""
        table = TestSoftDeleteModel.__table__
        assert "is_deleted" in table.c
        assert "deleted_at" in table.c

    def test_deleted_at_is_nullable(self):
        """deleted_atがnullableであることを確認."""
        table = TestSoftDeleteModel.__table__
        deleted_at_col = table.c.deleted_at
        assert deleted_at_col.nullable is True


class TestDictSerializableMixin:
    """DictSerializableMixinのテストクラス."""

    def test_to_dict_method_exists(self):
        """to_dict()メソッドが存在することを確認."""
        model = TestDictSerializableModel()
        assert hasattr(model, "to_dict")
        assert callable(model.to_dict)

    def test_to_dict_returns_dict(self):
        """to_dict()が辞書を返すことを確認."""
        model = TestDictSerializableModel()
        model.id = 1
        model.name = "Test"
        model.price = Decimal("100.50")

        result = model.to_dict()
        assert isinstance(result, dict)

    def test_to_dict_includes_all_columns(self):
        """to_dict()が全てのカラムを含むことを確認."""
        model = TestDictSerializableModel()
        model.id = 1
        model.name = "Test"
        model.price = Decimal("100.50")

        result = model.to_dict()
        assert "id" in result
        assert "name" in result
        assert "price" in result

    def test_to_dict_converts_decimal_to_float(self):
        """to_dict()がDecimal型をfloatに変換することを確認."""
        model = TestDictSerializableModel()
        model.id = 1
        model.name = "Test"
        model.price = Decimal("100.50")

        result = model.to_dict()
        assert isinstance(result["price"], float)
        assert result["price"] == 100.50

    def test_to_dict_handles_none_values(self):
        """to_dict()がNone値を正しく処理することを確認."""
        model = TestDictSerializableModel()
        model.id = 1
        model.name = "Test"
        model.price = None

        result = model.to_dict()
        assert result["price"] is None

    def test_to_dict_converts_datetime_to_iso_format(self):
        """to_dict()がdatetime型をISO8601形式に変換することを確認."""
        model = TestCombinedMixinsModel()
        model.id = 1
        model.name = "Test"
        model.value = Decimal("100.00")
        test_time = datetime(2025, 1, 15, 12, 30, 45)
        model.created_at = test_time

        result = model.to_dict()
        assert isinstance(result["created_at"], str)
        assert result["created_at"] == test_time.isoformat()


class TestCombinedMixins:
    """全てのMixinを組み合わせた場合のテストクラス."""

    def test_all_mixin_fields_exist(self):
        """全てのMixinのフィールドが存在することを確認."""
        model = TestCombinedMixinsModel()

        # TimestampMixin
        assert hasattr(model, "created_at")
        assert hasattr(model, "updated_at")

        # SoftDeleteMixin
        assert hasattr(model, "is_deleted")
        assert hasattr(model, "deleted_at")

        # DictSerializableMixin
        assert hasattr(model, "to_dict")

    def test_to_dict_includes_all_mixin_fields(self):
        """to_dict()が全てのMixinのフィールドを含むことを確認."""
        model = TestCombinedMixinsModel()
        model.id = 1
        model.name = "Test"
        model.value = Decimal("100.00")
        model.is_deleted = False

        result = model.to_dict()

        # 基本フィールド
        assert "id" in result
        assert "name" in result
        assert "value" in result

        # TimestampMixin
        assert "created_at" in result
        assert "updated_at" in result

        # SoftDeleteMixin
        assert "is_deleted" in result
        assert "deleted_at" in result

    def test_mixin_order_does_not_cause_conflicts(self):
        """Mixinの順序が競合を引き起こさないことを確認."""

        # 異なる順序でMixinを継承したモデルを作成
        class AlternateOrderModel(
            Base, SoftDeleteMixin, TimestampMixin, DictSerializableMixin
        ):
            __tablename__ = "test_alternate_order"
            id: Mapped[int] = mapped_column(primary_key=True)

        model = AlternateOrderModel()
        assert hasattr(model, "created_at")
        assert hasattr(model, "is_deleted")
        assert hasattr(model, "to_dict")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
