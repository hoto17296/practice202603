from __future__ import annotations

import uuid
from datetime import datetime
from typing import NotRequired, TypedDict

from sqlalchemy import func
from sqlmodel import Field, SQLModel
from utils import Fields


# ------------------------------------------------------------
# BaseTable
# ------------------------------------------------------------
class BaseTable(SQLModel):
    id: uuid.UUID = Fields.uuid(primary_key=True)


# ------------------------------------------------------------
# Mixins
# ------------------------------------------------------------
class TimestampMixin(SQLModel):
    created_at: datetime = Field(
        nullable=False,
        index=True,
        # Mixin で sa_column=Column(...) と書くと同一オブジェクトが共有されてしまうため sa_column_kwargs を使う
        sa_column_kwargs={"server_default": func.now()},
    )
    updated_at: datetime = Field(
        nullable=False,
        index=True,
        # Mixin で sa_column=Column(...) と書くと同一オブジェクトが共有されてしまうため sa_column_kwargs を使う
        sa_column_kwargs={"server_default": func.now(), "onupdate": func.now()},
    )


# ------------------------------------------------------------
# JSON Types
# ------------------------------------------------------------
class UserMeta(TypedDict):
    tags: NotRequired[list[str]]


# ------------------------------------------------------------
# Tables
# ------------------------------------------------------------
class UserTable(TimestampMixin, BaseTable, table=True):
    __tablename__ = "user"  # type: ignore

    email: str = Fields.text(unique=True, index=True)
    name: str = Fields.text()
    password_hash: str = Fields.text()
    meta: UserMeta = Fields.jsonb()

    # Relationships
    articles: list[ArticleTable] = Fields.relationship_has_many(back_populates="author")
    comments: list[CommentTable] = Fields.relationship_has_many(back_populates="author")


class ArticleTable(TimestampMixin, BaseTable, table=True):
    __tablename__ = "article"  # type: ignore

    author_id: uuid.UUID = Fields.foreign_key(column="user.id", index=True)
    title: str = Fields.text()
    body: str = Fields.text()
    published_at: datetime | None = Field(default=None, index=True)

    # Relationships
    author: UserTable | None = Fields.relationship_has_one(back_populates="articles")
    comments: list[CommentTable] = Fields.relationship_has_many(
        back_populates="article"
    )


class CommentTable(TimestampMixin, BaseTable, table=True):
    __tablename__ = "comment"  # type: ignore

    article_id: uuid.UUID = Fields.foreign_key(column="article.id", index=True)
    author_id: uuid.UUID = Fields.foreign_key(column="user.id", index=True)
    body: str = Fields.text()

    # Relationships
    article: ArticleTable | None = Fields.relationship_has_one(
        back_populates="comments"
    )
    author: UserTable | None = Fields.relationship_has_one(back_populates="comments")
