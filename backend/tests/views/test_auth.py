from contextlib import asynccontextmanager
from unittest.mock import AsyncMock, patch

import pytest
from fastapi import HTTPException
from httpx import ASGITransport, AsyncClient

from app import app
from lib.session import AuthSession, get_session
from lib.user import UserRegistrationError
from tables import UserTable


@asynccontextmanager
async def get_client():
    async with AsyncClient(transport=ASGITransport(app), base_url="http://test") as client:
        yield client


def _make_user(**kwargs) -> UserTable:
    return UserTable(**{"email": "user@example.com", "password_hash": "hash", "name": "", **kwargs})


class TestPostSignup:
    @pytest.mark.anyio
    async def test_正常なとき(self):
        user = _make_user()
        with patch("views.auth.register_user", AsyncMock(return_value=user)):
            async with get_client() as client:
                response = await client.post(
                    "/api/auth/signup", json={"email": "user@example.com", "password": "ValidPass1!", "name": "Test User"}
                )
        assert response.status_code == 200, "登録できること"
        assert "session" in response.cookies, "セッションクッキーがセットされること"

    @pytest.mark.anyio
    async def test_メールアドレスが不正なとき(self):
        with patch("views.auth.register_user", AsyncMock(side_effect=UserRegistrationError("INVALID_EMAIL_ADDRESS"))):
            async with get_client() as client:
                response = await client.post("/api/auth/signup", json={"email": "invalid", "password": "ValidPass1!", "name": "Test User"})
        assert response.status_code == 400, "Bad Request エラーになること"
        assert response.json()["detail"] == "INVALID_EMAIL_ADDRESS"

    @pytest.mark.anyio
    async def test_パスワードが不正なとき(self):
        with patch("views.auth.register_user", AsyncMock(side_effect=UserRegistrationError("INVALID_PASSWORD"))):
            async with get_client() as client:
                response = await client.post(
                    "/api/auth/signup", json={"email": "user@example.com", "password": "short", "name": "Test User"}
                )
        assert response.status_code == 400, "Bad Request エラーになること"
        assert response.json()["detail"] == "INVALID_PASSWORD"

    @pytest.mark.anyio
    async def test_同じメールアドレスのユーザが既に登録されているとき(self):
        with patch("views.auth.register_user", AsyncMock(side_effect=UserRegistrationError("ALREADY_EXISTS"))):
            async with get_client() as client:
                response = await client.post(
                    "/api/auth/signup", json={"email": "user@example.com", "password": "ValidPass1!", "name": "Test User"}
                )
        assert response.status_code == 409, "Conflict エラーになること"
        assert response.json()["detail"] == "ALREADY_EXISTS"


class TestPostSignin:
    @pytest.mark.anyio
    async def test_正常なとき(self):
        user = _make_user()
        with patch("views.auth.verify_user", AsyncMock(return_value=user)):
            async with get_client() as client:
                response = await client.post(
                    "/api/auth/signin", json={"email": "user@example.com", "password": "ValidPass1!"}
                )
        assert response.status_code == 200, "サインインできること"
        assert "session" in response.cookies, "セッションクッキーがセットされること"

    @pytest.mark.anyio
    async def test_認証情報が誤っているとき(self):
        with patch("views.auth.verify_user", AsyncMock(return_value=None)):
            async with get_client() as client:
                response = await client.post(
                    "/api/auth/signin", json={"email": "user@example.com", "password": "WrongPass1!"}
                )
        assert response.status_code == 400, "Bad Request エラーになること"


class TestPostSignout:
    @pytest.mark.anyio
    async def test_正常なとき(self):
        async with get_client() as client:
            response = await client.post("/api/auth/signout")
        assert response.status_code == 200, "サインアウトできること"


class TestGetSession:
    @pytest.mark.anyio
    async def test_セッションが有効なとき(self):
        user = _make_user()
        mock_session: AuthSession = {"user": {"id": str(user.id), "email": user.email, "name": user.name}}
        app.dependency_overrides[get_session] = lambda: mock_session
        try:
            async with get_client() as client:
                response = await client.get("/api/auth/session")
        finally:
            app.dependency_overrides.pop(get_session, None)
        assert response.status_code == 200, "セッション情報を取得できること"

    @pytest.mark.anyio
    async def test_セッションがないとき(self):
        async def _raise_401():
            raise HTTPException(status_code=401)

        app.dependency_overrides[get_session] = _raise_401
        try:
            async with get_client() as client:
                response = await client.get("/api/auth/session")
        finally:
            app.dependency_overrides.pop(get_session, None)
        assert response.status_code == 401, "Unauthorized エラーになること"
