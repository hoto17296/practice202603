import uuid
from typing import TypedDict, cast

import jwt
from fastapi import HTTPException, Request, Response
from sqlmodel import select

from database import get_database_session
from settings import settings
from tables import UserTable

JWT_SIGN_ALGORITHM = "HS256"


class JwtPayload(TypedDict):
    id: str


class AuthSessionUser(TypedDict):
    id: str
    email: str
    name: str


class AuthSession(TypedDict):
    user: AuthSessionUser


async def get_session(request: Request) -> AuthSession:
    token = request.cookies.get(settings.session_key)
    if token is None:
        raise HTTPException(status_code=401)
    try:
        payload = cast(JwtPayload, jwt.decode(token, settings.jwt_private_key, JWT_SIGN_ALGORITHM))
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401)
    async with get_database_session() as db:
        stmt = select(UserTable).where(UserTable.id == uuid.UUID(payload["id"]))
        user = (await db.exec(stmt)).first()
    if user is None:
        raise HTTPException(status_code=401)
    return {
        "user": {
            "id": str(user.id),
            "email": user.email,
            "name": user.name,
        }
    }


def set_session(response: Response, user: UserTable):
    payload: JwtPayload = {"id": str(user.id)}
    token = jwt.encode(dict(payload), settings.jwt_private_key, JWT_SIGN_ALGORITHM)
    response.set_cookie(settings.session_key, token, secure=True, httponly=True)


def clear_session(response: Response):
    response.delete_cookie(settings.session_key)
