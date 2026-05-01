from contextlib import asynccontextmanager
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from lib.user import UserRegistrationError, _hash_password, register_user, verify_user
from tables import UserTable


def _make_mock_db(existing_user: UserTable | None = None) -> AsyncMock:
    mock_db = AsyncMock()
    mock_db.add = MagicMock()
    exec_result = MagicMock()
    exec_result.first.return_value = existing_user
    mock_db.exec.return_value = exec_result
    return mock_db


def _patch_session(mock_db: AsyncMock):
    @asynccontextmanager
    async def _mock():
        yield mock_db

    return patch("lib.user.get_database_session", _mock)


class TestRegisterUser:
    @pytest.mark.anyio
    async def test_メールアドレスとパスワードが正常なとき(self):
        mock_db = _make_mock_db(existing_user=None)
        with _patch_session(mock_db):
            user = await register_user("new@example.com", "ValidPass1!")
        assert user.email == "new@example.com", "ユーザ登録できること"
        mock_db.add.assert_called_once()
        mock_db.commit.assert_awaited_once()
        mock_db.refresh.assert_awaited_once()

    @pytest.mark.anyio
    async def test_メールアドレスが不正なとき(self):
        with pytest.raises(UserRegistrationError) as exc:
            await register_user("not-an-email", "ValidPass1!")
        assert exc.value.type == "INVALID_EMAIL_ADDRESS", "エラーになること"

    @pytest.mark.anyio
    async def test_パスワードが不正なとき(self):
        with pytest.raises(UserRegistrationError) as exc:
            await register_user("user@example.com", "short")
        assert exc.value.type == "INVALID_PASSWORD", "エラーになること"

    @pytest.mark.anyio
    async def test_同じメールアドレスのユーザが既に登録されているとき(self):
        existing = UserTable(email="user@example.com", password_hash="hash", name="")
        mock_db = _make_mock_db(existing_user=existing)
        with _patch_session(mock_db):
            with pytest.raises(UserRegistrationError) as exc:
                await register_user("user@example.com", "ValidPass1!")
        assert exc.value.type == "ALREADY_EXISTS", "エラーになること"


class TestVerifyUser:
    @pytest.mark.anyio
    async def test_メールアドレスとパスワードが正しいとき(self):
        existing = UserTable(email="user@example.com", password_hash=_hash_password("ValidPass1!"), name="")
        mock_db = _make_mock_db(existing_user=existing)
        with _patch_session(mock_db):
            result = await verify_user("user@example.com", "ValidPass1!")
        assert result is existing, "認証が通ること"

    @pytest.mark.anyio
    async def test_ユーザが存在しないとき(self):
        mock_db = _make_mock_db(existing_user=None)
        with _patch_session(mock_db):
            result = await verify_user("unknown@example.com", "ValidPass1!")
        assert result is None, "認証が通らないこと"

    @pytest.mark.anyio
    async def test_パスワードが誤っているとき(self):
        existing = UserTable(email="user@example.com", password_hash=_hash_password("CorrectPass1!"), name="")
        mock_db = _make_mock_db(existing_user=existing)
        with _patch_session(mock_db):
            result = await verify_user("user@example.com", "WrongPass1!")
        assert result is None, "認証が通らないこと"
