import re
from hashlib import pbkdf2_hmac
from typing import Literal

from sqlmodel import select

from database import get_database_session
from settings import settings
from tables import UserTable

type UserRegistrationErrorType = Literal["INVALID_EMAIL_ADDRESS", "INVALID_PASSWORD", "ALREADY_EXISTS"]


class UserRegistrationError(Exception):
    type: UserRegistrationErrorType

    def __init__(self, type: UserRegistrationErrorType):
        super().__init__()
        self.type = type


def _hash_password(password: str) -> str:
    return pbkdf2_hmac(
        hash_name="sha256",
        password=password.encode(),
        salt=settings.password_pepper.encode(),
        iterations=100000,
    ).hex()


VALIDATION_PATTERNS = {
    "email": re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", re.ASCII),
    "password": re.compile(r"^[\w\d.!@*_-]{8,}$", re.ASCII),
}


async def register_user(email: str, password: str) -> UserTable:
    # validation
    if not re.match(VALIDATION_PATTERNS["email"], email):
        raise UserRegistrationError("INVALID_EMAIL_ADDRESS")
    if not re.match(VALIDATION_PATTERNS["password"], password):
        raise UserRegistrationError("INVALID_PASSWORD")

    async with get_database_session() as db:
        # check duplicates
        stmt = select(UserTable).where(UserTable.email == email)
        if (await db.exec(stmt)).first():
            raise UserRegistrationError("ALREADY_EXISTS")

        # create user
        user = UserTable(
            email=email,
            password_hash=_hash_password(password),
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)

    return user


async def verify_user(email: str, password: str) -> UserTable | None:
    async with get_database_session() as db:
        stmt = select(UserTable).where(UserTable.email == email)
        user = (await db.exec(stmt)).first()
    if user is None or _hash_password(password) != user.password_hash:
        return None
    return user
