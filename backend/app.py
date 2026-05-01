from fastapi import FastAPI
from sqlmodel import select

from database import get_database_session
from settings import settings
from tables import UserTable

app = FastAPI(
    debug=settings.debug,
    openapi_url="/api/openapi.json" if settings.debug else None,
)


@app.get("/api/healthcheck")
async def healthcheck():
    return "ok"


@app.get("/api/users")
async def get_users():
    async with get_database_session() as db:
        stmt = select(UserTable)
        user = (await db.exec(stmt)).first()
    if user:
        return "ok"
    return "ng"
