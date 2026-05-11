import uuid
from contextlib import asynccontextmanager
from datetime import UTC, datetime
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi import HTTPException
from httpx import ASGITransport, AsyncClient

from app import app
from lib.session import AuthSession, get_session
from tables import ArticleTable


@asynccontextmanager
async def get_client():
    async with AsyncClient(transport=ASGITransport(app), base_url="http://test") as client:
        yield client


MOCK_USER_ID = uuid.uuid4()
MOCK_SESSION: AuthSession = {"user": {"id": str(MOCK_USER_ID), "email": "test@example.com", "name": "Test User"}}


def _make_article(**kwargs) -> ArticleTable:
    return ArticleTable(
        **{
            "author_id": MOCK_USER_ID,
            "title": "Test Title",
            "body": "Test Body",
            "published_at": datetime(2026, 1, 1, tzinfo=UTC),
            **kwargs,
        }
    )


@asynccontextmanager
async def _mock_db(**kwargs):
    """
    キーワード引数でモック DB の振る舞いを設定する。
      articles: list_articles の db.exec().all() の戻り値
      article:  get_article / delete_article の db.exec().first() および
                db.get() の戻り値（None = 未存在）
    """
    db = AsyncMock()
    db.add = MagicMock()  # add() は同期呼び出し
    exec_result = MagicMock()
    if "articles" in kwargs:
        exec_result.all.return_value = kwargs["articles"]
    if "article" in kwargs:
        exec_result.first.return_value = kwargs["article"]
        db.get.return_value = kwargs["article"]
    db.exec.return_value = exec_result
    yield db


async def _raise_401():
    raise HTTPException(status_code=401)


class TestGetArticles:
    @pytest.mark.anyio
    async def test_未認証のとき(self):
        app.dependency_overrides[get_session] = _raise_401
        try:
            async with get_client() as client:
                response = await client.get("/api/articles/")
        finally:
            app.dependency_overrides.pop(get_session, None)
        assert response.status_code == 401, "Unauthorized エラーになること"

    @pytest.mark.anyio
    async def test_正常なとき(self):
        articles = [_make_article(title="Article 1"), _make_article(title="Article 2")]

        app.dependency_overrides[get_session] = lambda: MOCK_SESSION
        try:
            with patch("views.articles.get_database_session", lambda: _mock_db(articles=articles)):
                async with get_client() as client:
                    response = await client.get("/api/articles/")
        finally:
            app.dependency_overrides.pop(get_session, None)
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        assert [a["title"] for a in data] == ["Article 1", "Article 2"]

    @pytest.mark.anyio
    async def test_published_at_が_null_の記事は返らないこと(self):
        published = _make_article(title="Published")
        unpublished = _make_article(title="Unpublished", published_at=None)

        app.dependency_overrides[get_session] = lambda: MOCK_SESSION
        try:
            with patch("views.articles.get_database_session", lambda: _mock_db(articles=[published, unpublished])):
                async with get_client() as client:
                    response = await client.get("/api/articles/")
        finally:
            app.dependency_overrides.pop(get_session, None)
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["title"] == "Published"

    @pytest.mark.anyio
    async def test_記事がないとき(self):
        app.dependency_overrides[get_session] = lambda: MOCK_SESSION
        try:
            with patch("views.articles.get_database_session", lambda: _mock_db(articles=[])):
                async with get_client() as client:
                    response = await client.get("/api/articles/")
        finally:
            app.dependency_overrides.pop(get_session, None)
        assert response.status_code == 200
        assert response.json() == []


class TestGetArticle:
    @pytest.mark.anyio
    async def test_未認証のとき(self):
        app.dependency_overrides[get_session] = _raise_401
        try:
            async with get_client() as client:
                response = await client.get(f"/api/articles/{uuid.uuid4()}")
        finally:
            app.dependency_overrides.pop(get_session, None)
        assert response.status_code == 401, "Unauthorized エラーになること"

    @pytest.mark.anyio
    async def test_記事が存在するとき(self):
        article = _make_article()

        app.dependency_overrides[get_session] = lambda: MOCK_SESSION
        try:
            with patch("views.articles.get_database_session", lambda: _mock_db(article=article)):
                async with get_client() as client:
                    response = await client.get(f"/api/articles/{article.id}")
        finally:
            app.dependency_overrides.pop(get_session, None)
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == article.title
        assert data["body"] == article.body

    @pytest.mark.anyio
    async def test_記事が存在しないとき(self):
        app.dependency_overrides[get_session] = lambda: MOCK_SESSION
        try:
            with patch("views.articles.get_database_session", lambda: _mock_db(article=None)):
                async with get_client() as client:
                    response = await client.get(f"/api/articles/{uuid.uuid4()}")
        finally:
            app.dependency_overrides.pop(get_session, None)
        assert response.status_code == 404, "Not Found エラーになること"


class TestPostArticle:
    @pytest.mark.anyio
    async def test_未認証のとき(self):
        app.dependency_overrides[get_session] = _raise_401
        try:
            async with get_client() as client:
                response = await client.post("/api/articles/", json={"title": "Title", "body": "Body"})
        finally:
            app.dependency_overrides.pop(get_session, None)
        assert response.status_code == 401, "Unauthorized エラーになること"

    @pytest.mark.anyio
    async def test_正常なとき(self):
        app.dependency_overrides[get_session] = lambda: MOCK_SESSION
        try:
            with patch("views.articles.get_database_session", lambda: _mock_db()):
                async with get_client() as client:
                    response = await client.post("/api/articles/", json={"title": "Title", "body": "Body"})
        finally:
            app.dependency_overrides.pop(get_session, None)
        assert response.status_code == 201

    @pytest.mark.anyio
    async def test_タイトルが空のとき(self):
        app.dependency_overrides[get_session] = lambda: MOCK_SESSION
        try:
            async with get_client() as client:
                response = await client.post("/api/articles/", json={"title": "  ", "body": "Body"})
        finally:
            app.dependency_overrides.pop(get_session, None)
        assert response.status_code == 400
        assert response.json()["detail"] == "TITLE_IS_REQUIRED"

    @pytest.mark.anyio
    async def test_本文が空のとき(self):
        app.dependency_overrides[get_session] = lambda: MOCK_SESSION
        try:
            async with get_client() as client:
                response = await client.post("/api/articles/", json={"title": "Title", "body": "  "})
        finally:
            app.dependency_overrides.pop(get_session, None)
        assert response.status_code == 400
        assert response.json()["detail"] == "BODY_IS_REQUIRED"


class TestPatchArticle:
    @pytest.mark.anyio
    async def test_未認証のとき(self):
        app.dependency_overrides[get_session] = _raise_401
        try:
            async with get_client() as client:
                response = await client.patch(f"/api/articles/{uuid.uuid4()}", json={"title": "Title", "body": "Body"})
        finally:
            app.dependency_overrides.pop(get_session, None)
        assert response.status_code == 401, "Unauthorized エラーになること"

    @pytest.mark.anyio
    async def test_正常なとき(self):
        article = _make_article()

        app.dependency_overrides[get_session] = lambda: MOCK_SESSION
        try:
            with patch("views.articles.get_database_session", lambda: _mock_db(article=article)):
                async with get_client() as client:
                    response = await client.patch(
                        f"/api/articles/{article.id}",
                        json={"title": "Updated Title", "body": "Updated Body"},
                    )
        finally:
            app.dependency_overrides.pop(get_session, None)
        assert response.status_code == 204

    @pytest.mark.anyio
    async def test_記事が存在しないとき(self):
        app.dependency_overrides[get_session] = lambda: MOCK_SESSION
        try:
            with patch("views.articles.get_database_session", lambda: _mock_db(article=None)):
                async with get_client() as client:
                    response = await client.patch(
                        f"/api/articles/{uuid.uuid4()}",
                        json={"title": "Title", "body": "Body"},
                    )
        finally:
            app.dependency_overrides.pop(get_session, None)
        assert response.status_code == 404, "Not Found エラーになること"

    @pytest.mark.anyio
    async def test_投稿者以外が編集しようとしたとき(self):
        article = _make_article(author_id=uuid.uuid4())

        app.dependency_overrides[get_session] = lambda: MOCK_SESSION
        try:
            with patch("views.articles.get_database_session", lambda: _mock_db(article=article)):
                async with get_client() as client:
                    response = await client.patch(
                        f"/api/articles/{article.id}",
                        json={"title": "Title", "body": "Body"},
                    )
        finally:
            app.dependency_overrides.pop(get_session, None)
        assert response.status_code == 403, "Forbidden エラーになること"

    @pytest.mark.anyio
    async def test_タイトルが空のとき(self):
        app.dependency_overrides[get_session] = lambda: MOCK_SESSION
        try:
            async with get_client() as client:
                response = await client.patch(f"/api/articles/{uuid.uuid4()}", json={"title": "  ", "body": "Body"})
        finally:
            app.dependency_overrides.pop(get_session, None)
        assert response.status_code == 400
        assert response.json()["detail"] == "TITLE_IS_REQUIRED"

    @pytest.mark.anyio
    async def test_本文が空のとき(self):
        app.dependency_overrides[get_session] = lambda: MOCK_SESSION
        try:
            async with get_client() as client:
                response = await client.patch(f"/api/articles/{uuid.uuid4()}", json={"title": "Title", "body": "  "})
        finally:
            app.dependency_overrides.pop(get_session, None)
        assert response.status_code == 400
        assert response.json()["detail"] == "BODY_IS_REQUIRED"


class TestDeleteArticle:
    @pytest.mark.anyio
    async def test_未認証のとき(self):
        app.dependency_overrides[get_session] = _raise_401
        try:
            async with get_client() as client:
                response = await client.delete(f"/api/articles/{uuid.uuid4()}")
        finally:
            app.dependency_overrides.pop(get_session, None)
        assert response.status_code == 401, "Unauthorized エラーになること"

    @pytest.mark.anyio
    async def test_正常なとき(self):
        article = _make_article()

        app.dependency_overrides[get_session] = lambda: MOCK_SESSION
        try:
            with patch("views.articles.get_database_session", lambda: _mock_db(article=article)):
                async with get_client() as client:
                    response = await client.delete(f"/api/articles/{article.id}")
        finally:
            app.dependency_overrides.pop(get_session, None)
        assert response.status_code == 204, "No Content が返ること"

    @pytest.mark.anyio
    async def test_記事が存在しないとき(self):
        app.dependency_overrides[get_session] = lambda: MOCK_SESSION
        try:
            with patch("views.articles.get_database_session", lambda: _mock_db(article=None)):
                async with get_client() as client:
                    response = await client.delete(f"/api/articles/{uuid.uuid4()}")
        finally:
            app.dependency_overrides.pop(get_session, None)
        assert response.status_code == 404, "Not Found エラーになること"

    @pytest.mark.anyio
    async def test_投稿者以外が削除しようとしたとき(self):
        article = _make_article(author_id=uuid.uuid4())

        app.dependency_overrides[get_session] = lambda: MOCK_SESSION
        try:
            with patch("views.articles.get_database_session", lambda: _mock_db(article=article)):
                async with get_client() as client:
                    response = await client.delete(f"/api/articles/{article.id}")
        finally:
            app.dependency_overrides.pop(get_session, None)
        assert response.status_code == 403, "Forbidden エラーになること"
