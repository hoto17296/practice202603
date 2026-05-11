import uuid
from datetime import UTC, datetime
from typing import Literal

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import selectinload
from sqlmodel import col, select

from database import get_database_session
from lib.session import AuthSession, get_session
from lib.utils import sanitize_string
from models import HTTPExceptionBody, UnixTimestamp
from tables import ArticleTable

router = APIRouter()


class ArticleSummary(BaseModel):
    id: uuid.UUID
    author_id: uuid.UUID
    author_name: str
    title: str
    published_at: UnixTimestamp


@router.get("/")
async def list_articles(_: AuthSession = Depends(get_session)) -> list[ArticleSummary]:
    """記事一覧を返すエンドポイント"""
    async with get_database_session() as db:
        stmt = (
            select(ArticleTable)
            .options(selectinload(ArticleTable.author))  # type: ignore[arg-type]
            .where(col(ArticleTable.published_at).isnot(None))
            .order_by(col(ArticleTable.published_at).desc())
        )
        articles = (await db.exec(stmt)).all()
    return [
        ArticleSummary(
            id=a.id,
            author_id=a.author_id,
            author_name=a.author.name if a.author else "",
            title=a.title,
            published_at=a.published_at,
        )
        for a in articles
        if a.published_at is not None
    ]


class ArticleDetail(BaseModel):
    id: uuid.UUID
    author_id: uuid.UUID
    author_name: str
    title: str
    body: str
    published_at: UnixTimestamp | None
    created_at: UnixTimestamp | None
    updated_at: UnixTimestamp | None


@router.get("/{article_id}")
async def get_article(
    article_id: uuid.UUID,
    _: AuthSession = Depends(get_session),
) -> ArticleDetail:
    """指定された ID の記事の詳細を返すエンドポイント"""
    async with get_database_session() as db:
        stmt = (
            select(ArticleTable)
            .options(selectinload(ArticleTable.author))  # type: ignore[arg-type]
            .where(ArticleTable.id == article_id)
        )
        article = (await db.exec(stmt)).first()
    if article is None:
        raise HTTPException(status_code=404)
    return ArticleDetail(
        id=article.id,
        author_id=article.author_id,
        author_name=article.author.name if article.author else "",
        title=article.title,
        body=article.body,
        published_at=article.published_at,
        created_at=article.created_at,
        updated_at=article.updated_at,
    )


class PostArticleRequestBody(BaseModel):
    title: str
    body: str


@router.post(
    "/",
    status_code=201,
    responses={
        400: {
            "model": HTTPExceptionBody[
                Literal[
                    "TITLE_IS_REQUIRED",
                    "BODY_IS_REQUIRED",
                ]
            ]
        }
    },
)
async def post_article(
    req: PostArticleRequestBody,
    session: AuthSession = Depends(get_session),
) -> None:
    """新しい記事を作成するエンドポイント"""
    title = sanitize_string(req.title, remove_newlines=True).strip()
    body = sanitize_string(req.body).strip()
    if not title:
        raise HTTPException(status_code=400, detail="TITLE_IS_REQUIRED")
    if not body:
        raise HTTPException(status_code=400, detail="BODY_IS_REQUIRED")

    async with get_database_session() as db:
        article = ArticleTable(
            author_id=uuid.UUID(session["user"]["id"]),
            title=title,
            body=body,
            published_at=datetime.now(UTC),
        )
        db.add(article)
        await db.commit()


class PatchArticleRequestBody(BaseModel):
    title: str
    body: str


@router.patch(
    "/{article_id}",
    status_code=204,
    responses={
        400: {
            "model": HTTPExceptionBody[
                Literal[
                    "TITLE_IS_REQUIRED",
                    "BODY_IS_REQUIRED",
                ]
            ]
        },
    },
)
async def patch_article(
    article_id: uuid.UUID,
    req: PatchArticleRequestBody,
    session: AuthSession = Depends(get_session),
) -> None:
    """指定された ID の記事を変更するエンドポイント"""
    title = sanitize_string(req.title, remove_newlines=True).strip()
    body = sanitize_string(req.body).strip()
    if not title:
        raise HTTPException(status_code=400, detail="TITLE_IS_REQUIRED")
    if not body:
        raise HTTPException(status_code=400, detail="BODY_IS_REQUIRED")

    async with get_database_session() as db:
        stmt = (
            select(ArticleTable)
            .options(selectinload(ArticleTable.author))  # type: ignore[arg-type]
            .where(ArticleTable.id == article_id)
        )
        article = (await db.exec(stmt)).first()
        if article is None:
            raise HTTPException(status_code=404)
        if str(article.author_id) != session["user"]["id"]:
            raise HTTPException(status_code=403)
        article.title = title
        article.body = body
        await db.commit()


@router.delete("/{article_id}", status_code=204)
async def delete_article(
    article_id: uuid.UUID,
    session: AuthSession = Depends(get_session),
) -> None:
    """指定された ID の記事を削除するエンドポイント"""
    async with get_database_session() as db:
        article = await db.get(ArticleTable, article_id)
        if article is None:
            raise HTTPException(status_code=404)
        if str(article.author_id) != session["user"]["id"]:
            raise HTTPException(status_code=403)
        await db.delete(article)
        await db.commit()
