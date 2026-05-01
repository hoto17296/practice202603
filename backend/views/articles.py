import uuid
from datetime import UTC, datetime
from typing import Literal

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import selectinload
from sqlmodel import col, select

from database import get_database_session
from lib.session import AuthSession, get_session
from models import HTTPExceptionBody
from tables import ArticleTable

router = APIRouter()

type PostArticleErrorType = Literal["TITLE_IS_REQUIRED", "BODY_IS_REQUIRED"]


class ArticleSummary(BaseModel):
    id: uuid.UUID
    author_id: uuid.UUID
    author_name: str
    title: str
    published_at: datetime


class ArticleDetail(BaseModel):
    id: uuid.UUID
    author_id: uuid.UUID
    author_name: str
    title: str
    body: str
    published_at: datetime | None
    created_at: datetime | None
    updated_at: datetime | None


class PostArticleRequestBody(BaseModel):
    title: str
    body: str


@router.get("/")
async def list_articles(_: AuthSession = Depends(get_session)) -> list[ArticleSummary]:
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


@router.get("/{article_id}")
async def get_article(
    article_id: uuid.UUID,
    _: AuthSession = Depends(get_session),
) -> ArticleDetail:
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


@router.post(
    "/",
    responses={400: {"model": HTTPExceptionBody[PostArticleErrorType]}},
)
async def post_article(
    req: PostArticleRequestBody,
    session: AuthSession = Depends(get_session),
) -> ArticleTable:
    title = req.title.strip()
    body = req.body.strip()
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
        await db.refresh(article)

    return article
