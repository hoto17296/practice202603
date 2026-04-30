from contextlib import asynccontextmanager
from os import getenv

from sqlalchemy.ext.asyncio import create_async_engine
from sqlmodel.ext.asyncio.session import AsyncSession

DATABASE_URL = getenv("DATABASE_URL")
assert DATABASE_URL

# PostgreSQL に接続するドライバとして psycopg (v3) を使用する場合は接続文字列のスキームで明示する必要がある
# ※ SQLAlchemy 2.1 以降は PostgreSQL 接続時のデフォルトドライバが psycopg (v3) になるため、この対応は不要になる
# 参考: https://docs.sqlalchemy.org/en/21/changelog/migration_21.html#postgresql
DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+psycopg://")

engine = create_async_engine(DATABASE_URL)


@asynccontextmanager
async def get_database_session():
    async with AsyncSession(engine) as session:
        yield session
