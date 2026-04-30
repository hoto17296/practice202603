import uuid

from sqlalchemy import Column, Text
from sqlalchemy.dialects import postgresql as pg
from sqlmodel import Field, Relationship


class Fields:
    """よく使うフィールド型のショートハンド集"""

    @staticmethod
    def uuid(*, primary_key: bool = False, nullable: bool = False, index: bool = False):
        """UUID 型フィールドを作成する"""
        return Field(
            default_factory=uuid.uuid4,
            primary_key=primary_key,
            nullable=nullable,
            index=index,
        )

    @staticmethod
    def text(*, unique: bool = False, nullable: bool = False, index: bool = False):
        """
        SQLAlchemy は str 型フィールドを PostgreSQL 側の VARCHAR 型として作成しようとするが、
        PostgreSQL では TEXT 型を使用するほうが一般的であるため、TEXT 型で作成できるようにする
        """
        return Field(
            sa_column=Column(
                Text,
                unique=unique,
                nullable=nullable,
                index=index,
            )
        )

    @staticmethod
    def jsonb(*, nullable: bool = False):
        """JSONB 型フィールドを作成する"""
        return Field(
            default_factory=dict,
            sa_column=Column(
                pg.JSONB,
                nullable=nullable,
                server_default=None if nullable else "{}",
            ),
        )

    @staticmethod
    def foreign_key(*, column: str, nullable: bool = False, index: bool = False):
        """外部キーフィールド (UUID) を作成する"""
        return Field(
            foreign_key=column,
            nullable=nullable,
            index=index,
        )

    @staticmethod
    def relationship_has_one(*, back_populates: str):
        return Relationship(back_populates=back_populates)

    @staticmethod
    def relationship_has_many(*, back_populates: str, cascade_delete: bool = True):
        sa_relationship_kwargs = {}

        if cascade_delete:
            # all → ORM が親を削除するとき、子も ORM が削除する
            # delete-orphan → ORM 上で親子関係が切り離されたとき、子を削除する
            sa_relationship_kwargs["cascade"] = "all, delete-orphan"
        else:
            # cascade を指定しなかった場合のデフォルト値は "save-update, merge" で、
            # ORM が親を削除するときに子に削除は伝搬しないものの、ORM は子の外部キーを NULL に更新しようとするため、
            # 子の外部キーが nullable = True である場合はエラーとなる
            pass

        return Relationship(
            back_populates=back_populates,
            sa_relationship_kwargs=sa_relationship_kwargs,
        )
