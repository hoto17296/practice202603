import re
from hashlib import pbkdf2_hmac
from typing import Literal

from sqlmodel import select

from database import get_database_session
from lib.utils import sanitize_string
from settings import settings
from tables import UserTable

type UserRegistrationErrorType = Literal[
    "INVALID_EMAIL_ADDRESS",
    "INVALID_PASSWORD",
    "NAME_IS_REQUIRED",
    "ALREADY_EXISTS",
]


class UserRegistrationError(Exception):
    type: UserRegistrationErrorType

    def __init__(self, type: UserRegistrationErrorType):
        super().__init__()
        self.type = type


def hash_password(password: str) -> str:
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


async def register_user(email: str, password: str, name: str) -> UserTable:
    # validation
    if not re.match(VALIDATION_PATTERNS["email"], email):
        raise UserRegistrationError("INVALID_EMAIL_ADDRESS")
    if not re.match(VALIDATION_PATTERNS["password"], password):
        raise UserRegistrationError("INVALID_PASSWORD")
    name = sanitize_string(name, remove_newlines=True).strip()
    if len(name) == 0:
        raise UserRegistrationError("NAME_IS_REQUIRED")

    async with get_database_session() as db:
        # check duplicates
        stmt = select(UserTable).where(UserTable.email == email)
        if (await db.exec(stmt)).first():
            raise UserRegistrationError("ALREADY_EXISTS")

        # create user
        user = UserTable(email=email, password_hash=hash_password(password), name=name)
        db.add(user)
        await db.commit()
        await db.refresh(user)

    return user


async def verify_user(email: str, password: str) -> UserTable | None:
    async with get_database_session() as db:
        stmt = select(UserTable).where(UserTable.email == email)
        user = (await db.exec(stmt)).first()
    if user is None or hash_password(password) != user.password_hash:
        return None
    return user
