from contextlib import asynccontextmanager
from os import getenv

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine

DATABASE_URL = getenv("DATABASE_URL")
assert DATABASE_URL

engine = create_async_engine(DATABASE_URL)


@asynccontextmanager
async def get_database_session():
    async with AsyncSession(engine) as session:
        yield session
